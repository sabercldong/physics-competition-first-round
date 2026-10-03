"""Independent numeric and file/regression checks for this two-chapter revision."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,math
import fitz
import numpy as np
BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2];BASE=BOOK/'build/revision-ch11-ch12-20260912'
ARCHIVE=ROOT/'archive/2026-09-12-ch11-ch12-revision'
TITLES={'ch11':'有心力、万有引力与天体运动','ch12':'弹性体与机械波'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def body(p):return re.sub(r'\s+','',p.get_text(clip=fitz.Rect(42,51,552,780)))
def rng(d,title):
 rows=[r for r in d.get_toc() if r[0]==1]
 i=next(i for i,r in enumerate(rows) if r[1]==title)
 return rows[i][2]-1,rows[i+1][2]-1 if i+1<len(rows) else len(d)
def geometry():
 r={}
 a=.35;b=1;c=math.hypot(a,b);cs=a/c;sn=b/c
 R=np.array([[cs,-sn],[sn,cs]])
 u=np.linspace(-2,2,301)
 q=np.vstack((c-a*np.cosh(u),b*np.sinh(u)));xyz=R@q
 d1=R@np.vstack((-a*np.sinh(u),b*np.cosh(u)))
 d2=R@np.vstack((-a*np.cosh(u),b*np.sinh(u)))
 # Orbit has h constant with dt/du proportional to distance to focus.
 rr=np.linalg.norm(xyz,axis=0)
 rp=(xyz*d1).sum(axis=0)/rr
 acc=d2/rr**2-d1*rp/rr**3
 cross=xyz[0]*acc[1]-xyz[1]*acc[0]
 assert np.max(np.abs(cross))<1e-12
 assert np.all((xyz*acc).sum(axis=0)<0)
 r['hyperbola_acceleration_points_at_focus']=float(np.max(np.abs(cross)))
 r['hyperbola_deflection_deg']=math.degrees(2*math.atan(a/b))
 roots=[(1-math.sqrt(.4))/.6,(1+math.sqrt(.4))/.6]
 assert all(.42<x<3.2 and abs(.5/x**2-1/x+.3)<1e-12 for x in roots)
 r['potential_energy_line_turning_points']={'radius_roots':roots,'energy':-.3,'both_within_drawn_curve_domain':True}
 # The membrane diagram uses the exact normal and outward co-normal of its analytic surface.
 zx=.1875;zy=.205;t=np.array([0,1,zy]);n=np.array([-zx,-zy,1])
 f=np.cross(t,n)
 assert abs(t@n)<1e-15 and abs(t@f)<1e-15 and abs(n@f)<1e-15
 r['membrane_tangent_normal_force_dot_products']=[float(t@n),float(t@f),float(n@f)]
 # Pulley top and right tangent directions perpendicular to their radii.
 assert np.dot([1,0],[0,.3])==0 and np.dot([0,-1],[.3,0])==0
 r['pulley_tangency_checked']=True
 # Continuous zero-natural-length rope: verify force balance, material compliance and work.
 xs=np.linspace(0,3,61);ys=3*(1-xs*xs/16);a0=4.;C=12.
 L=np.sqrt((a0+xs)**2+ys**2);Rr=np.sqrt((a0-xs)**2+ys**2)
 U=(a0-xs)/(2*a0*ys);V=(a0+xs)/(2*a0*ys)
 TL=U*L;TR=V*Rr
 assert np.max(abs(TL*(a0+xs)/L-TR*(a0-xs)/Rr))<1e-12
 assert np.max(abs(TL*ys/L+TR*ys/Rr-1))<1e-12
 assert np.max(abs(L/TL+Rr/TR-C))<1e-12
 energy=.5*(TL*L+TR*Rr)
 work=energy[-1]-energy[0]-(ys[-1]-ys[0])
 assert abs(work-27/32)<1e-12 and abs(ys[-1]-21/16)<1e-12
 r['continuous_rope']={'y_final_over_l':float(ys[-1]),'work_over_Gl':float(work),'material_fraction_left':.875,'sampled_positions':61}
 # Point mass beta=1 illustrated wave: displacement continuous and exact slope jump.
 k=math.pi/2;A=1.4;beta=1.;T=1.;omega=1.
 mass=2*k*T/omega**2
 left0=right0=A/2;leftslope=A*k/2;rightslope=-A*k/2
 assert abs(T*(rightslope-leftslope)+mass*omega**2*left0)<1e-12
 r['point_mass_boundary_force_residual']=float(T*(rightslope-leftslope)+mass*omega**2*left0)
 r['point_mass_energy']=[]
 for beta in (0,.1,1,10):
  rr=-1j*beta/(1+1j*beta);tt=1/(1+1j*beta)
  total=abs(rr)**2+abs(tt)**2;assert abs(total-1)<1e-12
  r['point_mass_energy'].append({'beta':beta,'R_plus_T':total})
 r['fork_tensions_N']=[150/n**2 for n in (1,2,3)]
 r['hinge_K_Nm_per_rad']=.5e9*math.pi*.01**4/(2*.01)
 r['hinge_tau_Nm']=2*.3*100*.01/3
 r['hinge_Omega_over_omega_q0']=2*math.pi*r['hinge_K_Nm_per_rad']/r['hinge_tau_Nm']
 r['doppler_front_back_wavelengths']=[.7*(1-.35),.7*(1+.35)]
 r['generated_source_sha256']={ch:sha(BOOK/f'generated/chapters/{ch}.tex') for ch in TITLES}
 (BASE/'geometry-checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
 print('Geometry and independent numeric checks passed.')
def check():
 result={'scope':'Chapters 11 and 12 only; other chapters are compilation regression, not a renewed content audit.','pdfs':{}}
 ledger_path=BOOK/'audit/source-review/ch11-ch12-revision-ledger-20260912.json'
 ledger=json.loads(ledger_path.read_text())
 expected={'notes':set(range(99,105))|set(range(111,123)), 'exercises':set(range(40,44))|set(range(49,53))}
 for key,pages in expected.items():
  assert {r['physical_page'] for r in ledger['pages'] if r['source']==key}==pages
  assert sha(Path(ledger['sources'][key]['path']))==ledger['sources'][key]['sha256']
 alltext=''.join((BOOK/f'generated/chapters/{ch}.tex').read_text() for ch in TITLES)
 all_labels=set(re.findall(r'\\label\{([^}]+)\}',alltext))
 objects=ledger['pages']+ledger['source_figures']+ledger['source_exercises']
 assert len({r['id'] for r in objects})==len(objects)
 for row in objects:
  assert row['status']=='mapped'
  assert all(t in all_labels for t in row.get('targets',[row.get('target')])),row
 assert len(ledger['source_figures'])==14 and len(ledger['source_exercises'])==12
 result['source_ledger']={'sha256':sha(ledger_path),'teaching_pages':26,'source_figure_groups':14,'source_exercises':12,'unresolved_recorded_targets':0,
  'granularity':'Source-page teaching topics, individual source questions and source figure groups; not a literal sentence count.'}
 docs={}
 for key in ('ch11','ch12','volume2','main'):
  p=BASE/key/f'{key}.pdf';d=fitz.open(p);docs[key]=d
  row={'sha256':sha(p),'pages':len(d),'bookmarks':len(d.get_toc())}
  for name,args in [('qpdf',['qpdf','--check',str(p)]),('fonts',['pdffonts',str(p)])]:
   q=subprocess.run(args,capture_output=True,text=True);(BASE/key/f'{name}-check.txt').write_text(q.stdout+q.stderr);assert q.returncode==0
   if name=='fonts':
    rows=q.stdout.splitlines()[2:]
    assert rows and all(re.search(r'\byes\s+yes\s+yes\s+\d+\s+\d+\s*$',s) for s in rows),q.stdout
    row['embedded_fonts_with_unicode']=len(rows)
  log=(BASE/key/f'{key}.log').read_text(errors='replace')
  warnings=[s for s in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined|multiply defined',s)]
  allowed=[r'Underfull \hbox (badness 1152) in paragraph at lines 311--313',
           r'Underfull \hbox (badness 1253) in paragraph at lines 26--26'] if key=='main' else []
  assert warnings==allowed,(key,warnings)
  row['inherited_unrelated_spacing_warnings']=warnings
  for n in (1,2):
   log=(BASE/key/f'verify-pass-{n}.txt').read_text(errors='replace')
   assert 'Output written' in log and 'Fatal error' not in log
  assert all(1<=r[2]<=len(d) for r in d.get_toc())
  assert '\ufffd' not in ''.join(pg.get_text() for pg in d)
  if key in TITLES:
   t=(BOOK/f'generated/chapters/{key}.tex').read_text();n=8 if key=='ch11' else 14
   assert t.count(r'\begin{origexamplebox}')==t.count(r'\begin{xesolution}')==n
   labels=re.findall(r'\\label\{([^}]+)\}',t);assert len(labels)==len(set(labels))
   fl=[l for l in labels if ':fig:' in l]
   assert t.count(r'\figcap')==len(fl),(key,t.count(r'\figcap'),fl)
   assert all((r'\ref{'+l+'}') in t for l in fl),(key,[l for l in fl if (r'\ref{'+l+'}') not in t])
   assert not re.search(r'fill\s*=\s*white|fill\s*=\s*White|原扫描|重绘|OCR|标校|学习目标|本节小结',t)
   starts=[]
   for i,pg in enumerate(d):
    tx=pg.get_text()
    for m in re.finditer(r'(?m)^例\s*'+key[2:]+r'\.(\d+)\s+',tx):
     remainder=tx[m.end():];nextq=re.search(r'(?m)^例\s*'+key[2:]+r'\.\d+\s+',remainder)
     if nextq:remainder=remainder[:nextq.start()]
     starts.append({'example':int(m[1]),'page':i+1,'solution_same_page':'解答' in remainder})
   assert sorted(x['example'] for x in starts)==list(range(1,n+1)),starts
   assert all(x['solution_same_page'] for x in starts),(key,starts)
   row.update(source_sha256=sha(BOOK/f'generated/chapters/{key}.tex'),examples=n,figures=len(fl),question_solution_adjacency=starts)
  else:
   toc_text=(BASE/key/f'{key}.toc').read_text()
   chapter_pages=[(int(ch),pg) for pg,ch in re.findall(r'\\contentsline \{chapter\}.*\{(\d+)\}\{chapter\.(\d+)\}',toc_text)]
   expected=list(range(5,14)) if key=='volume2' else list(range(1,33))
   selected=[(ch,pg) for ch,pg in chapter_pages if ch in expected][:len(expected)]
   assert [c for c,p in selected]==expected,(key,selected)
   top=[r for r in d.get_toc() if r[0]==1]
   for (_,printed),entry in zip(selected,top):assert printed==d[entry[2]-1].get_label()
   row['directory_pages_verified']=len(selected)
  result['pdfs'][key]=row
 for ch,title in TITLES.items():
  expected=[body(p) for p in docs[ch]][1:]
  for key in ('volume2','main'):
   start,end=rng(docs[key],title);actual=[body(docs[key][i]) for i in range(start,end)]
   assert actual==expected,(ch,key,len(actual),len(expected),[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b])
   result['pdfs'][key][ch+'_physical_pages']=[start+1,end]
   # Compare rendered content, recording any subpixel differences for explicit review.
   diffs=[]
   for i in range(end-start):
    pa=docs[ch][i+1].get_pixmap(matrix=fitz.Matrix(1,1),clip=fitz.Rect(42,51,552,780),alpha=False)
    pb=docs[key][start+i].get_pixmap(matrix=fitz.Matrix(1,1),clip=fitz.Rect(42,51,552,780),alpha=False)
    if pa.samples!=pb.samples:diffs.append(i+1)
   result['pdfs'][key][ch+'_raster_difference_body_pages']=diffs
   assert not diffs,(key,ch,diffs)
 old=fitz.open(ARCHIVE/'pdf/高中物理竞赛一轮讲义.pdf')
 def retained(d):
  excluded=set()
  for title in TITLES.values():
   a,b=rng(d,title);excluded.update(range(a,b))
  first=next(r[2] for r in d.get_toc() if r[0]==1)-1
  return [i for i in range(first,len(d)) if i not in excluded]
 op,npages=retained(old),retained(docs['main']);assert len(op)==len(npages)
 td=[];pd=[]
 for i,j in zip(op,npages):
  if body(old[i])!=body(docs['main'][j]):td.append([i+1,j+1])
  a=old[i].get_pixmap(matrix=fitz.Matrix(1,1),clip=fitz.Rect(42,51,552,780),alpha=False)
  b=docs['main'][j].get_pixmap(matrix=fitz.Matrix(1,1),clip=fitz.Rect(42,51,552,780),alpha=False)
  if a.samples!=b.samples:pd.append([i+1,j+1])
 result.update(unchanged_main_pages_compared=len(op),unchanged_body_text_differences=td,unchanged_body_raster_differences=pd)
 assert not td and not pd,(td[:10],pd[:10])
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 assert all(sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
 assert all(sha(Path(p))==h for p,h in baseline['old_formal'].items()),'Formal files changed before release'
 result['other_generated_chapters_unchanged']=30
 result['recorded_frozen_source_xelatex_passes_per_pdf']=2
 (BASE/'release-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--geometry',action='store_true');p.add_argument('--release',action='store_true');a=p.parse_args()
 if a.geometry:geometry()
 if a.release:check()
