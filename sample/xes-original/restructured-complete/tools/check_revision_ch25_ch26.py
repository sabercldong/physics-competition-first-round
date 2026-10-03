"""Read-only release checks and bounded geometry/physics regressions."""
import fitz,json,re,subprocess,math,hashlib,argparse
from pathlib import Path
import build_review_ch25_ch26 as r
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
  w=warnings(p.with_suffix('.log'));old=r.book.BOOK/f'build/revision-ch23-ch24-20260922/{key}/{key}.log'
  inherited=[s for s in w if old.exists() and s in warnings(old)] if key=='main' else []
  q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
  fonts=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True)
  assert fonts.returncode==0 and len(fonts.stdout.splitlines())>2
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
 for n,num in [(25,8),(26,5)]:
  s=(r.book.GENERATED/f'chapters/ch{n}.tex').read_text();ex=s.count(r'\begin{origexamplebox}');sol=s.count(r'\begin{xesolution}')
  assert ex==sol==num;counts[n]={'examples':ex,'solutions':sol}
  labels=re.findall(r'\\label\{([^}]+)\}',s);assert len(labels)==len(set(labels))
 (r.BASE/'release-checks.json').write_text(json.dumps({'protected_chapters':30,'counts':counts,'pdfs':result},ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2))
def regression():
 result={}
 names={25:'交流电、相量与RLC电路',26:'电磁场、电磁波与超导体'}
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
 assert cross((1,0,0),(0,1,0))==(0,0,1)
 for R,L,C in [(20,.2,50e-6),(.1,2,3),(50,2,3)]:
  D=math.sqrt(R*R+4*L/C);w1=(D-R)/(2*L);w2=(D+R)/(2*L)
  assert math.isclose(w2-w1,R/L) and math.isclose(w1*w2,1/(L*C),rel_tol=1e-10)
 for x in ((math.sqrt(65)-1)/8,(math.sqrt(65)+1)/8):
  assert abs(1/(1+16*(x-1/x)**2)-.5)<1e-12
 for a in range(0,360):
  t=math.radians(a);n=(math.cos(t),math.sin(t),0);E=cross(n,cross(n,(0,1,0)))
  assert abs(sum(n[i]*E[i] for i in range(3)))<1e-12
  assert abs(sum(x*x for x in E)-math.cos(t)**2)<1e-12
 for n in [.2,1,1.5,10,1e5]:
  reflect=(1-n)/(1+n);transmit=2/(1+n)
  assert abs(reflect*reflect+n*transmit*transmit-1)<1e-12
 # Fluxoid energy crossing and opposite persistent currents.
 for n in [-2,0,3]:
  f=n+.5;assert (n-f)**2==(n+1-f)**2 and n-f==-(n+1-f)
 # Diamagnetic cylinder streamlines: positive levels cannot cross.
 for c in [.12,.35,.7,1.1,1.55]:
  for j in range(121):
   y=-2.4+4.8*j/120;lo=math.sqrt(max(0,1.15**2-y*y));hi=4
   for k in range(50):
    x=(lo+hi)/2
    if x*(1-1.15**2/(x*x+y*y))<c:lo=x
    else:hi=x
   x=(lo+hi)/2
   assert x*x+y*y>1.15**2 and abs(x*(1-1.15**2/(x*x+y*y))-c)<1e-10
 (r.BASE/'physics-checks.json').write_text(json.dumps({'half_power_roots':True,'wave_handedness_and_phase':True,'radiation_transverse_and_sin_squared':True,'interface_energy_conservation':True,'fluxoid_crossing':True,'meissner_streamlines':True},indent=2))
 print('Geometry and physics checks passed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--regression',action='store_true');a=p.parse_args()
 if a.regression:regression()
 else:physics();checks()
