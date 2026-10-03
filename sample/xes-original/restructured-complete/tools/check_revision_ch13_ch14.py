"""Checks for the scoped revision; numerical tests do not replace visual review."""
import argparse, hashlib, json, math, re, subprocess
from pathlib import Path
import fitz
import numpy as np
import build_review_ch13_ch14 as revision

BOOK=revision.book.BOOK
BASE=revision.BASE
ARCHIVE=revision.ARCHIVE
TITLES={f'ch{n}':revision.book.CHAPTERS[n]['title'] for n in (13,14)}
COUNTS={'ch13':(14,17),'ch14':(11,27)}
LEDGER=BOOK/'audit/source-review/ch13-ch14-revision-ledger-20260912.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def body(p): return re.sub(r'\s+','',p.get_text(clip=fitz.Rect(42,51,552,780)))
def raster(p): return p.get_pixmap(matrix=fitz.Matrix(1,1),clip=fitz.Rect(42,51,552,780),alpha=False).samples
def span(doc,title):
 rows=[r for r in doc.get_toc() if r[0]==1]
 idx=next(i for i,r in enumerate(rows) if r[1]==title)
 return rows[idx][2]-1, rows[idx+1][2]-1 if idx+1<len(rows) else len(doc)

def geometry():
 checks={}
 for name,R,levels in [('sphere',1.2,[.35,.75,1.2,1.75]),('cylinder',2.2,[.25,.65,1.1,1.65])]:
  text=(BOOK/f'assets/ch13/{name}-paths.tex').read_text()
  rows=re.findall(r'coordinates \{([^}]+)\}',text)
  upper=rows[::2] if name=='sphere' else rows
  ys=[];errors=[]
  for row,b in zip(upper,levels):
   xy=np.array([(float(x),float(y)) for x,y in re.findall(r'\(([-.\d]+),([-.\d]+)\)',row)])
   x,y=xy.T;rr=np.hypot(x,y)
   assert len(x)==181 and np.all(rr>R)
   psi=y*y*(1-R**3/rr**3) if name=='sphere' else y*(1-R*R/rr**2)
   errors.append(float(max(abs(psi-(b*b if name=='sphere' else b)))))
   ys.append(y)
  gap=float(min(np.diff(np.array(ys),axis=0).ravel()))
  assert max(errors)<4e-6 and gap>0
  checks[name]={'rounded_coordinate_residual':max(errors),'minimum_ordered_gap':gap,
                'path_sha256':sha(BOOK/f'assets/ch13/{name}-paths.tex')}
 t=np.linspace(-2,2,91);tangent=np.array([np.ones_like(t),np.zeros_like(t),.2*t]).T
 normal=np.array([-.2*t,np.zeros_like(t),np.ones_like(t)]).T
 assert np.max(abs((tangent*normal).sum(axis=1)))<1e-14
 h=np.linspace(0,4,41);r=.5/(1+1.2*h)**.25
 assert max(abs(r*r*np.sqrt(1+1.2*h)-.25))<1e-14
 checks['streamtube_normal_and_falling_jet_continuity']=True
 assert abs(.85**2*.35-.5**2*1.0115)<1e-14
 assert abs(.2/.85-.117647/.5)<1e-6
 checks['bernoulli_equal_volumes_and_projection']=True
 checks['coupled_Hg']=[]
 for gamma in (1.4,1.):
  xs=np.sort(np.roots([.32*.60,-(1+gamma)*(.32+.60),1+2*gamma]))
  omega=np.sqrt(9.8*xs)
  residual=[np.linalg.det([[9.8*(1+gamma)-w*w*.32,9.8*gamma],
                         [9.8*gamma,9.8*(1+gamma)-w*w*.60]]) for w in omega]
  assert max(abs(np.array(residual)))<1e-10
  checks['coupled_Hg'].append({'gamma':gamma,'omega':omega.tolist(),'f_Hz':(omega/(2*math.pi)).tolist()})
 R1,R2,w0,rho=.85,2.2,1.3,1.1;C=w0*R1**2/(R2**2-R1**2)
 omega=lambda r:C*(R2**2/r**2-1)
 pressure=lambda r:rho*C*C*((r*r-R1*R1)/2-2*R2**2*np.log(r/R1)-R2**4/2*(1/r**2-1/R1**2))
 rr=np.linspace(R1,R2,101);eps=1e-5
 dp=(pressure(rr+eps)-pressure(rr-eps))/(2*eps)
 error=float(max(abs(dp-rho*(rr*omega(rr))**2/rr)))
 assert abs(omega(R1)-w0)<1e-13 and abs(omega(R2))<1e-13 and error<1e-7
 checks['couette_radial_pressure_derivative_error']=error
 angle=math.radians(31.080962195493385)
 v1=np.array([-math.sin(angle),-math.cos(angle)])
 v2=np.array([math.cos(angle),-math.sin(angle)])
 assert abs(v1@v2)<1e-14
 Q,A,L,mh,g=3e-4,2e-4,.4,.1,10
 mw=1000*A*2*L;u=Q/A
 # The combined center is L(v1*3+v2)/4; torque balance gives cos(theta)-3sin(theta).
 assert abs((mh+mw)*g*L/4*(math.cos(angle)-3*math.sin(angle))+1000*Q*u*L)<1e-12
 checks['hose']={'water_mass_kg':mw,'angle_deg':math.degrees(angle),'orthogonal':True}
 phi=np.linspace(.001,math.pi-.001,501)
 y=(1+np.cos(phi))/2;xp=(1+np.cos(phi))/2;yp=-np.sin(phi)/2
 sintheta=xp/np.hypot(xp,yp)
 assert max(abs(sintheta/np.sqrt(y)-1))<1e-9
 checks['shore_Snell_invariant']=True
 theta=np.linspace(0,math.pi,10001)
 assert abs(float(np.trapz(np.sin(theta)**3,theta))-4/3)<1e-8
 checks['hangar_upward_force_coefficient']=8/3
 # Finite-aperture formula differentiates to area divided by outlet flow.
 a,R,H=.16,2.4,3.4;b=(R-a)/H
 primitive=lambda h:2*np.sqrt(h)+4*b/(3*a)*h**1.5+2*b*b/(5*a*a)*h**2.5
 hh=np.linspace(H/2,H,101)
 assert max(abs((primitive(hh+eps)-primitive(hh-eps))/(2*eps)-(a+b*hh)**2/(a*a*np.sqrt(hh))))<1e-7
 checks['finite_funnel_integral']=True
 roots=[]
 for E in (-.8,-.5):
  q=np.array([(1+math.sqrt(1+E))**(-1/6),(1-math.sqrt(1+E))**(-1/6)])
  assert max(abs(q**-12-2*q**-6-E))<1e-13
  roots.append({'E_over_epsilon':E,'turning_points':q.tolist()})
 checks['potential_turning_points']=roots
 incoming=np.array([3,1.5]);reflected=np.array([-3,1.5]);normal=np.array([1.,0.])
 assert np.all(incoming-2*(incoming@normal)*normal==reflected)
 checks['elastic_reflection_speed_and_tangential_component']=True
 assert abs(-(-1512)/(2*72**2)-7/48)<1e-14
 checks['LJ_classical_statistical_alpha_in_kB_over_epsilon']=7/48
 checks['Torricelli_final_cmHg']=72+2*8/10
 checks['heated_piston_Ts_K']=[297/.9,297*1.1/.9,297*1.1**2/.9]
 checks['sand_initial_and_final_T_K']=[120/(1.8-1.5)-100,1.8*300]
 assert np.allclose(checks['heated_piston_Ts_K'],[330,363,399.3])
 assert np.allclose(checks['sand_initial_and_final_T_K'],[300,540])
 xmax=(100-76)/2
 checks['Hg_spill']={'remaining_cm':xmax,'Tmax_K':(76+xmax)*(100-xmax)/16}
 assert checks['Hg_spill']['Tmax_K']==484
 # U tube: F(0)>0, F -> -infinity; F'<0 throughout (0,L).
 for tr in (1.01,1.5,10):
  x=np.linspace(0,.999,1000);fp=-tr/(1+x)**2-1/(1-x)**2-2
  assert np.all(fp<0) and tr-1>0
 checks['sealed_U_positive_shift_unique_root']=True
 # L tube test all three positions of the final-stage parabola vertex.
 lcases=[]
 for a,b,c,d,b0 in [(2,1,2.5,2,.2),(.5,1,2.5,2,4),(.5,1,2.5,2,12)]:
  x=np.linspace(0,c+d,200001)
  heights=np.where(x<=c-b,0,np.where(x<=c,x+b-c,np.where(x<=c+d-b,b,c+d-x)))
  ratio=(b0+heights)*(a+x)/(b0*a)
  vertex=(b0+c+d-a)/2;chosen=min(c+d,max(c+d-b,vertex))
  exact=(b0+c+d-chosen)*(a+chosen)/(b0*a)
  assert abs(exact-max(ratio))<2e-4
  lcases.append({'vertex':vertex,'clipped':chosen,'Tmax_over_T0':exact})
 checks['L_tube_three_maximum_cases']=lcases
 checks['generated_source_sha256']={ch:sha(BOOK/f'generated/chapters/{ch}.tex') for ch in TITLES}
 save(BASE/'geometry-checks.json',checks)
 print('Independent numeric and geometric checks passed.')

def check():
 result={'scope':'Chapters 13/14 revised; other content is only a compilation regression.','pdfs':{}}
 ledger=json.loads(LEDGER.read_text())
 expected={'kinematics':set(range(78,82)),'notes':set(range(123,129)),
           'exercises':set(range(53,57)),'thermal':set(range(5,18))}
 for key,pages in expected.items():
  assert {r['physical_page'] for r in ledger['pages'] if r['source']==key}==pages
  assert sha(Path(ledger['sources'][key]['path']))==ledger['sources'][key]['sha256']
 text=''.join((BOOK/f'generated/chapters/{ch}.tex').read_text() for ch in TITLES)
 labels=re.findall(r'\\label\{([^}]+)\}',text);assert len(labels)==len(set(labels))
 objects=ledger['pages']+ledger['source_figures']+ledger['source_exercises']
 assert len({r['id'] for r in objects})==len(objects)
 for row in objects:
  assert row['status'] in ('mapped','merged')
  assert all(t in labels for t in row.get('targets',[row.get('target')])),row
 assert all(t in labels for t in ledger['preserved_bridge_examples'])
 assert (len(ledger['pages']),len(ledger['source_figures']),len(ledger['source_exercises']))==(27,23,22)
 result['source_ledger']={'sha256':sha(LEDGER),'teaching_pages':27,'source_figure_groups':23,'source_exercises':22,
 'preserved_bridge_examples':3,'unresolved_recorded_targets':0,
 'granularity':'Source-page teaching topics, individual questions and figure groups, not literal word counts.'}
 docs={}
 for key in revision.OLD_NAMES:
  p=BASE/key/f'{key}.pdf';d=fitz.open(p);docs[key]=d
  row={'sha256':sha(p),'pages':len(d),'bookmarks':len(d.get_toc())}
  for name,args in [('qpdf',['qpdf','--check',str(p)]),('fonts',['pdffonts',str(p)])]:
   q=subprocess.run(args,capture_output=True,text=True);(BASE/key/f'{name}-check.txt').write_text(q.stdout+q.stderr)
   assert q.returncode==0,(key,name,q.stderr)
   if name=='fonts':
    fontrows=q.stdout.splitlines()[2:]
    assert fontrows and all(re.search(r'\byes\s+yes\s+yes\s+\d+\s+\d+\s*$',s) for s in fontrows),q.stdout
    row['embedded_fonts_with_unicode']=len(fontrows)
  log=(BASE/key/f'{key}.log').read_text(errors='replace')
  warnings=[s for s in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined|multiply defined',s)]
  allowed=[r'Underfull \hbox (badness 1152) in paragraph at lines 311--313',
           r'Underfull \hbox (badness 1253) in paragraph at lines 26--26'] if key=='main' else []
  assert warnings==allowed,(key,warnings)
  row['inherited_unrelated_spacing_warnings']=warnings
  for n in (1,2):
   verify=(BASE/key/f'verify-pass-{n}.txt').read_text(errors='replace')
   assert 'Output written' in verify and 'Fatal error' not in verify,(key,n)
  assert d.get_toc() and all(1<=r[2]<=len(d) for r in d.get_toc())
  assert '\ufffd' not in ''.join(pg.get_text() for pg in d)
  if key in TITLES:
   t=(BOOK/f'generated/chapters/{key}.tex').read_text();n,figs=COUNTS[key]
   assert t==revision.chapter_text(int(key[2:]))[0],'Maintenance source changed'
   assert sha(BOOK/f'generated/chapters/{key}.tex')==ledger['generated_sha256'][key]
   assert t.count(r'\begin{origexamplebox}')==t.count(r'\begin{xesolution}')==n
   fl=[l for l in re.findall(r'\\label\{([^}]+)\}',t) if ':fig:' in l]
   assert t.count(r'\figcap')==len(fl)==figs,(key,len(fl),t.count(r'\figcap'))
   assert all((r'\ref{'+l+'}') in t for l in fl)
   assert not re.search(r'fill\s*=\s*[Ww]hite|原扫描|重绘|OCR|标校|学习目标|本节小结',t)
   assert not any(ord(c)<32 and c not in '\n\t' for c in t)
   starts=[]
   for i,pg in enumerate(d):
    tx=pg.get_text()
    for m in re.finditer(r'(?m)^例\s*'+key[2:]+r'\.(\d+)\s+',tx):
     remaining=tx[m.end():];nextq=re.search(r'(?m)^例\s*'+key[2:]+r'\.\d+\s+',remaining)
     if nextq:remaining=remaining[:nextq.start()]
     starts.append({'example':int(m[1]),'page':i+1,'solution_same_page':'解答' in remaining})
   assert sorted(x['example'] for x in starts)==list(range(1,n+1)),starts
   assert all(x['solution_same_page'] for x in starts),(key,starts)
   row.update(source_sha256=sha(BOOK/f'generated/chapters/{key}.tex'),examples=n,figures=figs,
              figure_labels=fl,question_solution_adjacency=starts)
  else:
   toc=(BASE/key/f'{key}.toc').read_text()
   cp=[(int(ch),pg) for pg,ch in re.findall(r'\\contentsline \{chapter\}.*\{(\d+)\}\{chapter\.(\d+)\}',toc)]
   wanted=list(range(5,14)) if key=='volume2' else list(range(14,19)) if key=='volume3' else list(range(1,33))
   selected=[(ch,pg) for ch,pg in cp if ch in wanted][:len(wanted)]
   assert [c for c,p in selected]==wanted,(key,selected)
   top=[r for r in d.get_toc() if r[0]==1]
   for (_,printed),entry in zip(selected,top):assert printed==d[entry[2]-1].get_label()
   row['directory_pages_verified']=len(selected)
  result['pdfs'][key]=row
 for ch,title in TITLES.items():
  independent=docs[ch];expected=[body(p) for p in independent][1:]
  for key in (('volume2','main') if ch=='ch13' else ('volume3','main')):
   start,end=span(docs[key],title);actual=[body(docs[key][i]) for i in range(start,end)]
   assert actual==expected,(ch,key,len(actual),len(expected),[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b])
   diffs=[i+1 for i in range(end-start) if raster(independent[i+1])!=raster(docs[key][start+i])]
   result['pdfs'][key][ch+'_physical_pages']=[start+1,end]
   result['pdfs'][key][ch+'_raster_difference_body_pages']=diffs
   assert not diffs,(key,ch,diffs)
 old=fitz.open(ARCHIVE/'pdf/高中物理竞赛一轮讲义.pdf')
 def retained(d):
  excluded=set()
  for title in TITLES.values():
   a,b=span(d,title);excluded.update(range(a,b))
  first=next(r[2] for r in d.get_toc() if r[0]==1)-1
  return [i for i in range(first,len(d)) if i not in excluded]
 op,npages=retained(old),retained(docs['main']);assert len(op)==len(npages)
 td=[];pd=[]
 for i,j in zip(op,npages):
  if body(old[i])!=body(docs['main'][j]):td.append([i+1,j+1])
  if raster(old[i])!=raster(docs['main'][j]):pd.append([i+1,j+1])
 result.update(unchanged_main_pages_compared=len(op),unchanged_body_text_differences=td,unchanged_body_raster_differences=pd)
 assert not td and not pd,(td[:10],pd[:10])
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 assert all(sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
 assert all(sha(Path(p))==h for p,h in baseline['old_formal'].items()),'Formal PDFs changed before release'
 result['other_generated_chapters_unchanged']=30
 result['recorded_frozen_source_xelatex_passes_per_pdf']=2
 save(BASE/'release-checks.json',result)
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--geometry',action='store_true');p.add_argument('--release',action='store_true');a=p.parse_args()
 if a.geometry:geometry()
 if a.release:check()
