"""Model checks and retention evidence for mechanics teaching expansion."""
import json, math, re, subprocess
from collections import Counter
from pathlib import Path
from scipy.integrate import quad
import fitz
from PIL import Image, ImageDraw
import enrich_mechanics_20260927 as m

def physics():
    checks={}
    rho1,rho2,h1,h2,b,g=800.,1000.,.2,.4,.3,9.8
    f=quad(lambda x:b*g*(rho1*h1+rho2*x),0,h2)[0]
    moment=quad(lambda x:x*b*g*(rho1*h1+rho2*x),0,h2)[0]
    expected=b*g*(rho1*h1*h2+rho2*h2*h2/2)
    xc=(rho1*h1*h2*h2/2+rho2*h2**3/3)/(rho1*h1*h2+rho2*h2*h2/2)
    assert math.isclose(f,expected) and math.isclose(moment/f,xc) and h2/2<xc<2*h2/3
    checks['layered_pressure']={'force':f,'depth_below_interface':xc}
    r0,r1,mu=3.,.7,2.
    integral=quad(lambda r:1/math.sqrt(2*mu*(1/r-1/r0)),r1,r0)[0]
    u=math.acos(math.sqrt(r1/r0));analytic=math.sqrt(r0**3/(2*mu))*(u+math.sin(u)*math.cos(u))
    assert math.isclose(integral,analytic,rel_tol=1e-9)
    checks['radial_time']={'quadrature':integral,'formula':analytic}
    for r2 in [1.001,2.,10.]:
        r1=1.;mu=1.;a=(r1+r2)/2
        vp=math.sqrt(2*mu*r2/(r1*(r1+r2)));va=math.sqrt(2*mu*r1/(r2*(r1+r2)))
        assert vp>math.sqrt(mu/r1) and va<math.sqrt(mu/r2)
        assert math.isclose(r1*vp,r2*va) and math.isclose(vp*vp/2-mu/r1,-mu/(2*a))
    checks['transfer_energy_angular_momentum']='PASS at 3 radius ratios'
    # E(A)-E(A cos u) substitution removes endpoint singularity in period integral.
    eps=.01
    period=4*quad(lambda u:1/math.sqrt(1+eps/2*(1+math.cos(u)**2)),0,math.pi/2)[0]
    omega=2*math.pi/period;first=1+3*eps/8
    assert abs(omega-first)<eps*eps
    checks['duffing_frequency']={'quadrature':omega,'first_order':first}
    level=10*math.log10((2.5e-5+1e-5)/1e-12)
    assert abs(level-75.44068)<1e-5
    checks['sound_level']=level
    assert math.isclose(2*.34*500,340.) and math.isclose(.68/4-.160,.01)
    checks['pipe_resonance']={'sound_speed':340,'end_correction':.01}
    # F(x)=exp(-x^2): a separated half-amplitude traveling pulse has half the initial energy.
    fp=lambda x:-2*x*math.exp(-x*x)
    e0=quad(lambda x:.5*fp(x)**2,-10,10)[0]
    ep=quad(lambda x:.25*fp(x)**2,-10,10)[0]
    assert math.isclose(ep*2,e0)
    checks['pulse_energy']={'initial':e0,'each_pulse':ep}
    (m.BASE/'physics-checks.json').write_text(json.dumps(checks,indent=2))

def blocks(s,env):return re.findall(r'\\begin\{'+env+r'\}(.*?)\\end\{'+env+r'\}',s,re.S)
def retain():
    report={}
    for n in range(5,14):
        key=f'ch{n:02}';old=(m.ARCHIVE/f'source/generated/chapters/{key}.tex').read_text();new=(m.BASE/f'staged/{key}-body.tex').read_text()
        row={}
        for env in ['origexamplebox','xesolution','tikzpicture']:
            # Compare complete existing objects, allowing only already-installed layout directives.
            normalize=lambda s:re.sub(r'\\Needspace\{[^{}]+\}|\\nopagebreak\[[^]]+\]','',s)
            a=Counter(normalize(x) for x in blocks(old,env));b=Counter(normalize(x) for x in blocks(new,env))
            missing=a-b
            assert not missing,(key,env,[x[:120] for x in missing])
            row[env]={'old':sum(a.values()),'new':sum(b.values()),'missing':0}
        report[key]=row
    (m.BASE/'object-retention.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

def render(key):
    folder=m.BASE/'visual'/key;folder.mkdir(parents=True,exist_ok=True)
    d=fitz.open(m.BASE/key/f'{key}.pdf')
    for i,p in enumerate(d):p.get_pixmap(dpi=130).save(folder/f'p{i+1:03}.png')
    for a in range(0,len(d),8):
        sheet=Image.new('RGB',(1600,1180),'#dddddd');draw=ImageDraw.Draw(sheet)
        for j in range(min(8,len(d)-a)):
            im=Image.open(folder/f'p{a+j+1:03}.png');im.thumbnail((390,550));x=j%4*400;y=j//4*590
            sheet.paste(im,(x,y+25));draw.text((x+5,y+5),f'{key} p{a+j+1}',fill='black')
        sheet.save(folder/f'overview-{a+1:03}.jpg',quality=90)

def structure():
    rows={}
    for key in m.names():
        p=m.BASE/key/f'{key}.pdf'
        if not p.exists():continue
        log=p.with_suffix('.log').read_text(errors='replace')
        errors=[line for line in log.splitlines() if any(s in line for s in ['Overfull','Missing character','undefined','multiply defined'])]
        q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
        fonts=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True)
        d=fitz.open(p)
        rows[key]={'sha256':m.sha(p),'pages':len(d),'errors':errors,'qpdf_returncode':q.returncode,'bookmarks':len(d.get_toc()),'min_page_text':min(len(x.get_text()) for x in d),'font_report':fonts.stdout}
    (m.BASE/'structure.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print(json.dumps({k:{j:v for j,v in x.items() if j!='font_report'} for k,x in rows.items()},ensure_ascii=False,indent=2))
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--render');p.add_argument('--structure',action='store_true');a=p.parse_args()
    physics();retain()
    if a.render:render(a.render)
    if a.structure:structure()
