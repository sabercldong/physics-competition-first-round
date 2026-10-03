"""Read-only release checks and bounded geometry/physics regressions."""
import fitz,json,re,subprocess,math,hashlib,argparse
from pathlib import Path
import build_review_ch23_ch24 as r
sha=r.common.sha
def warnings(p):
 return [s for s in p.read_text(errors='replace').splitlines() if re.search(r'Overfull|Underfull|Missing character|undefined|multiply defined|LaTeX Warning',s)]
def body(p):
 return re.sub(r'\s+','',p.get_text(clip=fitz.Rect(0,64,p.rect.width,p.rect.height-45)))
def checks():
 result={}
 for key in r.OLD_NAMES:
  p=r.BASE/key/f'{key}.pdf';d=fitz.open(p);out=r.BASE/key/'review';out.mkdir(exist_ok=True)
  frozen=json.loads((p.parent/'frozen-build.json').read_text());assert frozen['pdf_sha256']==sha(p)
  assert all(sha(Path(x))==h for x,h in frozen['source_hashes'].items())
  w=warnings(p.with_suffix('.log'));old=r.book.BOOK/f'build/revision-ch21-ch22-20260920/{key}/{key}.log'
  inherited=[s for s in w if old.exists() and s in warnings(old)] if key=='main' else []
  q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
  fonts=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True)
  (out/'qpdf.txt').write_text(q.stdout+q.stderr);(out/'fonts.txt').write_text(fonts.stdout)
  txt='\n'.join(pg.get_text() for pg in d);(out/'text.txt').write_text(txt)
  result[key]={'sha256':sha(p),'pages':len(d),'warnings':w,'inherited_out_of_scope_warnings':inherited,
   'new_warnings':[s for s in w if s not in inherited],'qpdf':q.returncode,
   'all_fonts_embedded':all(re.search(r'\s+yes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',s) for s in fonts.stdout.splitlines()[2:]),
   'toc_entries':len(d.get_toc()),'bookmark_destinations_valid':all(1<=x[2]<=len(d) for x in d.get_toc()),
   'replacement_chars':txt.count('\ufffd'),'copies_text':len(txt)}
  for i in range(min(4,len(d))):d[i].get_pixmap(dpi=100,alpha=False).save(out/f'front-{i+1:02}.png')
 baseline=json.loads((r.ARCHIVE/'manifest.json').read_text())
 assert all(sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
 counts={}
 for n,num in [(23,9),(24,21)]:
  s=(r.book.GENERATED/f'chapters/ch{n}.tex').read_text();ex=s.count(r'\begin{origexamplebox}');sol=s.count(r'\begin{xesolution}')
  assert ex==sol==num;counts[n]={'examples':ex,'solutions':sol}
  labels=re.findall(r'\\label\{([^}]+)\}',s);assert len(labels)==len(set(labels))
 (r.BASE/'release-checks.json').write_text(json.dumps({'protected_chapters':30,'counts':counts,'pdfs':result},ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2))
def regression():
 result={}
 names={23:'磁场、安培力与安培定律',24:'电磁感应'}
 for key in ('volume4','main'):
  p=r.BASE/key/f'{key}.pdf';new=fitz.open(p);old=fitz.open(r.ARCHIVE/'pdf'/r.OLD_NAMES[key])
  nt=[x for x in new.get_toc() if x[0]==1];ot=[x for x in old.get_toc() if x[0]==1]
  assert [x[1] for x in nt]==[x[1] for x in ot]
  records=[]
  for i,(a,b) in enumerate(zip(ot,nt)):
   os=a[2]-1;ns=b[2]-1;oe=ot[i+1][2]-1 if i+1<len(ot) else len(old);ne=nt[i+1][2]-1 if i+1<len(nt) else len(new)
   if a[1] in names.values():
    n=next(n for n,t in names.items() if t==a[1]);ref=fitz.open(r.BASE/f'ch{n}'/f'ch{n}.pdf')
    dif=[j+2 for j in range(len(ref)-1) if body(ref[j+1])!=body(new[ns+j])]
    assert ne-ns==len(ref)-1 and not dif,(key,n,dif)
    for j in [ns,ne-1]:new[j].get_pixmap(dpi=140,alpha=False).save(r.BASE/key/'review'/f'boundary-{j+1}.png')
    records.append({'title':a[1],'status':'matches_independent_chapter','new_start':ns+1,'pages':ne-ns});continue
   assert oe-os==ne-ns,(a,b,oe-os,ne-ns)
   dif=[]
   for j in range(oe-os):
    clip=fitz.Rect(0,64,old[os+j].rect.width,old[os+j].rect.height-45)
    if old[os+j].get_pixmap(dpi=90,clip=clip,alpha=False).samples!=new[ns+j].get_pixmap(dpi=90,clip=clip,alpha=False).samples:dif.append(j+1)
   records.append({'title':a[1],'old_start':os+1,'new_start':ns+1,'pages':ne-ns,'pixel_differences':dif})
  result[key]={'pdf_sha256':sha(p),'records':records}
  (r.BASE/f'{key}-pixel-regression.json').write_text(json.dumps(result[key],ensure_ascii=False,indent=2))
  print(key,'pixel difference pages',sum(len(x.get('pixel_differences',[])) for x in records),flush=True)
 (r.BASE/'combined-regression.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
def physics():
 cross=lambda a,b:(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
 r12=(-4,-2,0);l1=(0,1,0);l2=(1,0,0)
 f1=cross(l1,cross(l2,r12));f2=cross(l2,cross(l1,tuple(-x for x in r12)))
 assert f1==(-2,0,0) and f2==(0,4,0)
 assert cross((0,-1,0),(0,0,-1))==(1,0,0)
 assert cross((1,0,0),(3.5,1.6,0))[2]>0
 assert abs(1*1.2+(-1.2)*1)<1e-12 # loop side dot normal
 for h in (1.2,1.25):assert abs(math.sqrt(2.5**2-h**2)**2+h*h-2.5**2)<1e-12
 # Ck^2 is mechanical effective mass; check impulse and finite heat limit.
 m,C,k,v0=2.,3.,.7,4.;vf=m*v0/(m+C*k*k);q=C*k*vf
 heat=.5*m*v0*v0-.5*m*vf*vf-q*q/(2*C)
 assert abs(m*(vf-v0)+k*q)<1e-12
 assert abs(heat-m*C*k*k*v0*v0/(2*(m+C*k*k)))<1e-12
 # Analytic midpoint convergence for integral (1+z^2)^-3 = 3pi/8.
 N=100000;dz=100/N;integ=sum((1+(-50+(i+.5)*dz)**2)**-3 for i in range(N))*dz
 assert abs(integ-3*math.pi/8)<2e-9
 # RLC repeated-root solution satisfies L I''+R I'+I/C=0 and L I'(0)=E-U.
 L,C,R,E,U=2.,.5,4.,5.,1.;alpha=R/(2*L);amp=(E-U)/L
 for t in (0,.3,2.):
  I=amp*t*math.exp(-alpha*t);dI=amp*(1-alpha*t)*math.exp(-alpha*t);ddI=amp*(alpha*alpha*t-2*alpha)*math.exp(-alpha*t)
  assert abs(L*ddI+R*dI+I/C)<1e-12
 assert abs(L*amp-(E-U))<1e-12
 (r.BASE/'physics-checks.json').write_text(json.dumps({'current_elements_forces':[f1,f2],'rod_force_positive_x':True,'biot_savart_out_of_page':True,'chord_intersections':True,'capacitor_heat':heat,'lens_integral_error':abs(integ-3*math.pi/8),'rlc_critical_residual_pass':True},indent=2))
 print('Geometry and physics spot checks passed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--regression',action='store_true');a=p.parse_args()
 if a.regression:regression()
 else:physics();checks()
