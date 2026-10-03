"""Retention, model, PDF and render evidence for the thermal expansion."""
import argparse, json, math, re, subprocess, hashlib
from collections import Counter
from scipy.integrate import quad
from PIL import Image, ImageDraw
import fitz
import enrich_thermal_20260927 as m

def save(name, data):
    (m.BASE/name).write_text(json.dumps(data, ensure_ascii=False, indent=2))

def physics():
    checks = {}
    L1,L2,Y1,Y2,A,a1,a2,dT = 1.,2.,2e11,1e11,1e-4,1e-5,3e-5,80.
    F = -A*dT*(a1*L1+a2*L2)/(L1/Y1+L2/Y2)
    dl1,dl2 = a1*L1*dT+F*L1/(A*Y1), a2*L2*dT+F*L2/(A*Y2)
    assert F < 0 and abs(dl1+dl2)<1e-14 and abs(dl1)>1e-7
    assert math.isclose(dl1,L1*L2*(a1*Y1-a2*Y2)/(L1*Y2+L2*Y1)*dT)
    checks['composite_rod'] = {'force':F, 'delta_lengths':[dl1,dl2], 'junction_not_fixed':True}
    assert math.isclose(2/(1/4+1/28),7.)
    checks['mixture'] = {'mole_fraction_He':7/8, 'mean_molar_mass_g_mol':7.}
    Rh,Rc,Th,Tc = 3.,2.,400.,300.
    Ti=(Rc*Th+Rh*Tc)/(Rh+Rc)
    assert math.isclose((Th-Ti)/Rh,(Ti-Tc)/Rc)
    checks['conduction'] = {'interface_temperature':Ti, 'heat_rate':(Th-Tc)/(Rh+Rc)}
    C,e,s,A,T0,P = 20.,.8,5.67e-8,.1,300.,2.
    Te=(T0**4+P/(e*s*A))**.25
    tau=C/(4*e*s*A*Te**3)
    slope=(-e*s*A*((Te+.01)**4-(Te-.01)**4))/(.02*C)
    assert math.isclose(P,e*s*A*(Te**4-T0**4),rel_tol=1e-12)
    assert math.isclose(slope,-1/tau,rel_tol=1e-7)
    checks['radiation'] = {'equilibrium_K':Te,'linear_time_s':tau}
    W=quad(lambda V:1/V**2,1,2)[0];dU=1.5*(.5-1);Q=-.25
    assert math.isclose(W,.5) and math.isclose(dU,Q-W)
    checks['polytropic'] = {'W_over_RT1':W,'dU_over_RT1':dU,'Q_over_RT1':Q}
    checks['two_paths_entropy'] = {'gas_each_over_nR':math.log(2),'generation_reversible':0,'generation_free_over_nR':math.log(2)}
    for C1,C2,Th,Tc in [(1.,1.,400.,300.),(2.,5.,700.,270.),(5.,2.,300.,300.)]:
        Tstar=Tc*(Th/Tc)**(C1/(C1+C2))
        assert abs(C1*math.log(Tstar/Th)+C2*math.log(Tstar/Tc))<1e-12
        work=C1*Th+C2*Tc-(C1+C2)*Tstar
        assert work >= -1e-12 and Tstar <= (C1*Th+C2*Tc)/(C1+C2)+1e-12
    checks['finite_source_work'] = 'entropy equality and nonnegative work: three heat-capacity/temperature pairs'
    for T1 in [100.,250.,299.99]:
        T0=300.;C=2.
        W=quad(lambda T:C*(T0/T-1),T1,T0)[0]
        expected=C*(T0*math.log(T0/T1)-(T0-T1))
        assert math.isclose(W,expected,rel_tol=2e-7)
        assert abs(C*math.log(T1/T0)+(W+C*(T0-T1))/T0)<1e-12
    checks['refrigeration'] = 'integration, energy and entropy balances: three final temperatures'
    phi,pa,ps=.6,3.,2.;crit=1/phi
    assert math.isclose(crit*(pa+phi*ps),crit*pa+ps)
    for r in [1.,crit,3.,10.]:
        vapor=min(r*phi,1)*ps/r
        liquid=max(0.,ps*(phi-1/r))
        assert math.isclose(vapor+liquid,phi*ps) and liquid>=0
    checks['condensation'] = 'piecewise pressure continuous; gas+liquid amount conserved'
    T2=1/(1/360+8.314*math.log(2)/40000)
    assert abs(T2-342)<1 and T2<360
    checks['boiling'] = {'T2_K':T2}
    N=20;q=.2
    probabilities=[math.comb(N,n)*q**n*(1-q)**(N-n) for n in range(N+1)]
    mean=sum(n*p for n,p in enumerate(probabilities))
    variance=sum((n-mean)**2*p for n,p in enumerate(probabilities))
    assert math.isclose(sum(probabilities),1.) and math.isclose(mean,N/5) and math.isclose(variance,4*N/25)
    checks['binomial'] = {'N':N, 'mean':mean, 'variance':variance}
    boltz=math.exp(-math.log(3))
    assert math.isclose(3*boltz/(1+3*boltz),.5)
    checks['degeneracy'] = {'equal_population_kT_over_epsilon':1/math.log(3),'high_temperature_excited_fraction':.75}
    a=.7
    vz2=quad(lambda v:v**3*math.exp(-a*v*v),0,math.inf)[0]/quad(lambda v:v*math.exp(-a*v*v),0,math.inf)[0]
    assert math.isclose(vz2,1/a)
    # N0=T0=k=1, U=3/2 N^(4/3); derivative must equal 2 T.
    for N in [.1,.5,1.]:
        h=1e-6
        deriv=(1.5*(N+h)**(4/3)-1.5*(N-h)**(4/3))/(2*h)
        assert math.isclose(deriv,2*N**(1/3),rel_tol=1e-8)
    checks['effusion'] = {'weighted_vz2':vz2, 'analytic_vz2':1/a, 'energy_balance':'PASS'}
    save('physics-checks.json',checks)

def retain():
    rows={};registry=[]
    for n in range(14,19):
        key=f'ch{n}';old=(m.ARCHIVE/f'source/generated/chapters/{key}.tex').read_text();new=(m.BASE/f'staged/{key}-body.tex').read_text()
        # Every pre-existing nonempty source line remains, including prose and drawing commands.
        missing=Counter(x.strip() for x in old.splitlines() if x.strip())-Counter(x.strip() for x in new.splitlines() if x.strip())
        assert not missing,(key,missing)
        oldlabels=set(re.findall(r'\\label\{([^}]+)\}',old))
        labels=re.findall(r'\\label\{([^}]+)\}',new)
        assert len(labels)==len(set(labels)) and oldlabels<=set(labels)
        refs=re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}',new)
        assert all(ref in labels for ref in refs if ref.startswith(key+':'))
        for label in set(labels)-oldlabels:
            registry.append({'target_id':label,'source':'locally authored bridge example using existing chapter models','role':'teaching bridge','status':'added','chapter':n})
        rows[key]={'all_existing_nonempty_source_lines_retained':True,'labels':len(labels),'new_examples':len(set(labels)-oldlabels),
                   'figures_unchanged':re.findall(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',old,re.S)==re.findall(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',new,re.S)}
        assert rows[key]['figures_unchanged']
    assert len(registry)==13
    save('prose-and-label-retention.json',rows);save('bridge-example-registry.json',registry)

def render(key):
    folder=m.BASE/'visual'/key;folder.mkdir(parents=True,exist_ok=True)
    d=fitz.open(m.BASE/key/f'{key}.pdf')
    for i,p in enumerate(d):p.get_pixmap(dpi=150).save(folder/f'p{i+1:03}.png')
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
        errors=[x for x in log.splitlines() if any(s in x for s in ['Overfull','Missing character','undefined','multiply defined'])]
        q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
        fonts=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True)
        d=fitz.open(p);toc=d.get_toc()
        assert all(0<x[2]<=len(d) for x in toc)
        rows[key]={'sha256':m.sha(p),'pages':len(d),'errors':errors,'qpdf_returncode':q.returncode,'bookmarks':len(toc),
            'min_page_text':min(len(x.get_text()) for x in d),'font_report':fonts.stdout,
            'underfull_warnings':[x for x in log.splitlines() if 'Underfull' in x]}
        if key.startswith('ch'):
            old=fitz.open(m.ARCHIVE/'pdf'/m.names()[key])
            def image_hashes(doc):
                result=set()
                for xref in {v[0] for page in doc for v in page.get_images(full=True)}:
                    pix=fitz.Pixmap(doc,xref)
                    result.add((pix.width,pix.height,pix.n,hashlib.sha256(pix.samples).hexdigest()))
                return result
            a,b=image_hashes(old),image_hashes(d)
            assert a==b,(key,'embedded image assets differ')
            rows[key]['old_raster_assets_preserved']=len(a)
    save('structure.json',rows)
    print(json.dumps({k:{j:v for j,v in x.items() if j!='font_report'} for k,x in rows.items()},ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render');p.add_argument('--structure',action='store_true');a=p.parse_args()
    physics();retain()
    if a.render:render(a.render)
    if a.structure:structure()
