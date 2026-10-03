"""Read-only release checks and bounded geometry/physics regressions."""
import fitz,json,re,subprocess,math,hashlib,argparse
from pathlib import Path
import build_review_ch27_ch28 as r
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
  w=warnings(p.with_suffix('.log'));old=r.book.BOOK/f'build/revision-ch25-ch26-20260922/{key}/{key}.log'
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
 for n,num in [(27,14),(28,10)]:
  s=(r.book.GENERATED/f'chapters/ch{n}.tex').read_text();ex=s.count(r'\begin{origexamplebox}');sol=s.count(r'\begin{xesolution}')
  assert ex==sol==num;counts[n]={'examples':ex,'solutions':sol}
  labels=re.findall(r'\\label\{([^}]+)\}',s);assert len(labels)==len(set(labels))
 (r.BASE/'release-checks.json').write_text(json.dumps({'protected_chapters':30,'counts':counts,'pdfs':result},ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2))
def regression():
 result={}
 names={27:'几何光学：光线、反射和折射',28:'成像与光学仪器'}
 for key in ('volume5','main'):
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
 tests={}
 # Direct Euclidean lengths, vertex limit and near-axis ball lens extremum.
 for R in (.3,1,4):
  for v in (.4,2,7):
   for phi in (0,.1,.3):
    x=R-R*math.cos(phi);y=R*math.sin(phi)
    assert math.isclose((v-x)**2+y*y,(v-R)**2+R*R+2*R*(v-R)*math.cos(phi),abs_tol=1e-12)
 for n in (1.01,1.5,2,2.8,10):
  R=1;x0=R/(n-1)
  def distance(x):return 2*(n-1)*(R+x)**2/((n-2)*R+2*(n-1)*x)
  assert math.isclose(distance(x0),2*n*R/(n-1))
  for x in (x0*.95,x0*1.05):assert distance(x)>=distance(x0)
 tests['sphere_exact_lengths_and_ball_lens_minimum']=True
 # Original lakeshore geometry: independently sample both landing coordinates.
 for alpha in (.12,.4,.9,1.5,2.3):
  beta=alpha/2;k=2*math.sin(beta)
  for h,c in ((.3,3),(.8,2.8),(2,1)):
   ell=math.hypot(h,c)
   t=0 if k>=c/ell else c-k*h/math.sqrt(1-k*k)
   def total(p,q):
    crossing=math.sqrt(max(0,p*p+q*q-2*p*q*math.cos(alpha)))
    return math.hypot(c-p,h)+math.hypot(c-q,h)+2*crossing
   answer=2*ell if t==0 else 2*(h*math.sqrt(1-k*k)+k*c)
   assert abs(total(t,t)-answer)<1e-10
   for j in range(61):
    for m in range(61):assert total(c*2*j/60,c*2*m/60)>=answer-1e-10
 tests['lakeshore_two_variable_time_minimum']=True
 # Signed-angle prism bounds, including A below the critical angle.
 for n in (1.1,1.5,2.4):
  rc=math.asin(1/n)
  for a in (.1*rc,.8*rc,1.2*rc,1.95*rc):
   f=lambda r:math.asin(max(-1,min(1,n*math.sin(r))))
   low=2*f(a/2)-a;high=math.pi/2+f(a-rc)-a
   for j in range(1001):
    angle=a-rc+(2*rc-a)*j/1000;delta=f(angle)+f(a-angle)-a
    assert low-1e-7<=delta<=high+1e-7
 tests['signed_prism_complete_interval']=True
 # Aplanatic point: actual outward ray vs backward virtual conjugate.
 for n in (1.2,1.5,2.1):
  for phi in (-1,-.3,.1,.8):
   p=(math.cos(phi),math.sin(phi));c=(-1/n,0);q=(-n,0)
   a=math.hypot(p[0]-c[0],p[1]);b=math.hypot(p[0]-q[0],p[1])
   assert abs(b-n*a)<1e-12
   di=((p[0]-c[0])/a,p[1]/a);do=((p[0]-q[0])/b,p[1]/b)
   cr=lambda u,v:u[0]*v[1]-u[1]*v[0]
   assert abs(n*cr(di,p)-cr(do,p))<1e-12
   assert sum(di[j]*p[j] for j in (0,1))>0 and sum(do[j]*p[j] for j in (0,1))>0
 tests['aplanatic_outward_snell_and_virtual_image']=True
 # Fresnel coefficients use the declared polarization bases.
 for n1,n2 in ((1,1.5),(1.5,1),(1,2.2)):
  for theta in (.01,.1,.3,.5):
   ti=math.cos(theta);tt=math.sqrt(1-(n1/n2*math.sin(theta))**2)
   for rr,tr in (((n1*ti-n2*tt)/(n1*ti+n2*tt),2*n1*ti/(n1*ti+n2*tt)),
                 ((n2*ti-n1*tt)/(n2*ti+n1*tt),2*n1*ti/(n2*ti+n1*tt))):
    assert abs(rr*rr+n2*tt/(n1*ti)*tr*tr-1)<1e-12
 tests['fresnel_energy_conservation']=True
 # Circle mapping preserves circularity at the stated conjugate position.
 f=1;R=.2;a=f+math.sqrt(f*f+R*R)
 pts=[]
 for j in range(72):
  t=2*math.pi*j/72;x=a+R*math.cos(t);y=R*math.sin(t)
  pts.append((f*x/(x-f),-f*y/(x-f)))
 cx=(max(x for x,y in pts)+min(x for x,y in pts))/2
 radii=[math.hypot(x-cx,y) for x,y in pts]
 assert max(radii)-min(radii)<1e-12
 tests['circle_imaging_special_orientation']=True
 for g in (.2,1,3):
  for yy,aa in ((.01,.002),(.02,-.003)):
   y=lambda x:yy*math.cos(g*x)+aa/g*math.sin(g*x)
   assert abs(y(0)-yy)<1e-12 and abs(y(math.pi/(2*g))-aa/g)<1e-12
 tests['grin_initial_conditions_and_parallel_beam_focus']=True
 geom=json.loads((r.BASE/'geometry-checks.json').read_text())
 assert len(geom)==27 and all(abs(x['residual'])<x['tolerance'] for x in geom)
 tests['computed_diagram_geometry_27_assertions']=True
 (r.BASE/'physics-checks.json').write_text(json.dumps(tests,indent=2))
 print('Optics physics checks passed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--regression',action='store_true');a=p.parse_args()
 if a.regression:regression()
 else:physics();checks()
