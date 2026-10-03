"""Independent physics tests and hash-bound scoped release regression."""
import argparse,json,math,re,subprocess
from pathlib import Path
import fitz
import numpy as np
import build_review_ch15_ch16 as revision
from check_revision_ch13_ch14 import body,raster,span
BOOK=revision.book.BOOK;BASE=revision.BASE;ARCHIVE=revision.ARCHIVE;sha=revision.sha
TITLES={f'ch{n}':revision.book.CHAPTERS[n]['title'] for n in (15,16)}
COUNTS={'ch15':(11,24),'ch16':(5,11)}
LEDGER=BOOK/'audit/source-review/ch15-ch16-revision-ledger-20260915.json'
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2))

def geometry():
 c={};g=5/3
 for key,v1,v2,kh in [('ch15_carnot',.8,2,3.2),('ch16_carnot',1,2.4,4)]:
  v=np.array([v1,v2,1.5*v2,1.5*v1]);kc=kh/1.5**(g-1)
  p=np.array([kh/v[0],kh/v[1],kc/v[2],kc/v[3]])
  assert abs(p[0]*v[0]-p[1]*v[1])<1e-12 and abs(p[2]*v[2]-p[3]*v[3])<1e-12
  assert abs(p[1]*v[1]**g-p[2]*v[2]**g)<1e-12
  assert abs(p[3]*v[3]**g-p[0]*v[0]**g)<1e-12
  work=(kh-kc)*math.log(v2/v1);qh=kh*math.log(v2/v1)
  assert work>0 and abs(work/qh-(1-kc/kh))<1e-12
  c[key]={'states_VP':list(map(list,zip(v.tolist(),p.tolist()))),'eta':work/qh}
 for key,vmin,vmax in [('ch15_otto',1.,3.),('ch16_otto',1.2,3.)]:
  k=1.4;T=np.array([1.8*(vmin/vmax)**k*vmax,1.8*vmin,4*vmin,4*(vmin/vmax)**k*vmax])
  eta=1-(T[3]-T[0])/(T[2]-T[1])
  assert abs(eta-(1-(vmin/vmax)**(k-1)))<1e-12
  c[key]={'eta':eta,'constant_volume_heat':True}
 ratio=3**(1/1.4);v=np.array([.7*ratio,.7,1.5,1.5*ratio]);p=np.array([1.,3.,3.,1.]);T=p*v
 eta=1-(T[3]-T[0])/(T[2]-T[1]);assert abs(eta-(1-3**(-.4/1.4)))<1e-12
 c['brayton']={'isobars_exactly_horizontal':True,'adiabatic_temperature_ratios':[T[1]/T[0],T[2]/T[3]],'eta':eta}
 # Analytic curve used for both stroke and shade; derivative fixes tangent sign.
 x=np.linspace(1,4.5,4001);work=np.trapz(4/x,x)
 assert abs(work-4*math.log(4.5))<1e-6
 c['piston_work_area_quadrature_error']=abs(work-4*math.log(4.5))
 for alpha in (1.5,2.5,3.5):
  z0=(alpha+1)/(2*alpha+1);C=lambda z:alpha+(1-z)/(1-2*z)
  assert abs(C(z0))<1e-12 and C((.5+z0)/2)<0 and C((1+z0)/2)>0 and C(.25)>0
 c['variable_heat_capacity_zero_and_sign_branches']=True
 c['lift_rod_lengths']=[.85-.18,.85-.18]
 c['work_rod_lengths']=[1.25-.18,1.25-.18]
 c['piston_half_widths_equal_cylinder_half_widths']=[.85,1.,.62]
 lengths=[]
 for deg in (90,270,0,90,270):
  t=math.radians(deg);crank=np.array([.4*math.sin(t),-2+.4*math.cos(t)])
  pin=np.array([0,crank[1]+math.sqrt(1.5**2-crank[0]**2)])
  lengths.append(float(np.linalg.norm(pin-crank)))
 assert np.allclose(lengths,1.5,atol=1e-14)
 c['engine_connecting_rods']=lengths
 # Meniscus x=.5cos(t), y=1.6+.5sin(t), pi<=t<=2pi.
 t=np.linspace(math.pi,2*math.pi,501);xx=.5*np.cos(t);yy=1.6+.5*np.sin(t)
 assert abs(xx[0]+.5)<1e-14 and abs(xx[-1]-.5)<1e-14 and min(yy)<yy[0]
 assert abs(-.5*math.sin(math.pi))<1e-14
 c['capillary']={'concave_and_vertical_contact_tangent':True,'radius_for_10m':2*.073/(1000*9.8*10)}
 for k in (1.,1.4):
  R=.02;sigma=.025;p0=1e5;pr=p0+4*sigma/R
  F=lambda r:4*math.pi*r*r*(pr*(R/r)**(3*k)-p0)-16*math.pi*sigma*r
  eps=R*1e-6;deriv=(F(R+eps)-F(R-eps))/(2*eps);exact=4*math.pi*(4*sigma-3*k*R*pr)
  assert abs((deriv-exact)/exact)<1e-8 and exact<0 and abs(F(R))<1e-10
 c['bubble_isothermal_and_adiabatic_restoring_forces']=True
 assert abs(-9/8+15/8-math.log(4)-(.75-math.log(4)))<1e-14
 c['abc_cycle_first_law_Q_equals_W']=.75-math.log(4)
 for z in (.01,.3,.9):
  tf=(1-z)**(.4/1.4);assert 0<tf<1
 c['lift_pressure_positive_and_cooling']=True
 for outer,inner,core in [(1.7,1.19,.43),(2.1,.68,.23)]:
  mid=(outer+inner)/2;cell=(outer-inner)*.38
  assert 0<core<inner<outer and mid-cell>inner and mid+cell<outer
 c['stellar_convective_cells_inside_envelope']=True
 # For every intermediate X the positive Y,Z roots conserve energy and entropy.
 X=np.linspace(300,399.999,1000);disc=(700-X)**2-36e6/X
 Y=((700-X)+np.sqrt(disc))/2;Z=((700-X)-np.sqrt(disc))/2
 assert np.all(X>=Y-1e-10) and np.all(Y>Z)
 assert max(abs(X+Y+Z-700))<1e-10 and max(abs(X*Y*Z-9e6))<1e-7
 assert 400*150**2==300**2*100
 c['three_body_energy_entropy_path_and_upper_bound']={'maximum_K':400,'other_K':[150,150]}
 # Nondegenerate surface model: sigma=5-T^2, S=2AT.
 A=np.array([.8,1.4,2.8,1.6]);temp=np.array([2.,2.,1.,1.]);S=2*A*temp
 assert S[1]==S[2] and S[0]==S[3]
 qh=temp[0]*(S[1]-S[0]);qc=temp[2]*(S[2]-S[3]);assert abs(1-qc/qh-.5)<1e-14
 c['surface_cycle']={'isentropes_AT_constant':True,'area_work_out_positive':qh-qc,'eta':1-qc/qh}
 c['microstate_count']={'N4_Nleft1':math.comb(4,1),'N4_Nleft2':math.comb(4,2),'log_Omega_ratio_40J_310K':40/310/1.380649e-23}
 c['generated_source_sha256']={ch:sha(BOOK/f'generated/chapters/{ch}.tex') for ch in TITLES}
 save(BASE/'geometry-checks.json',c);print('Physical model and geometric checks passed.')

def check():
 result={'scope':'15、16章修订，其他章节仅合订回归','pdfs':{}}
 ledger=json.loads(LEDGER.read_text());assert sha(Path(ledger['source']['path']))==ledger['source']['sha256']
 assert {r['physical_page'] for r in ledger['pages']}==set(range(19,41))
 texts={ch:(BOOK/f'generated/chapters/{ch}.tex').read_text() for ch in TITLES}
 text=''.join(texts.values());labels=re.findall(r'\\label\{([^}]+)\}',text);assert len(labels)==len(set(labels))
 objects=ledger['pages']+ledger['source_questions']+ledger['source_figures']
 assert len({r['id'] for r in objects})==len(objects)
 for r in objects:
  assert r['status']=='mapped'
  assert all(t in labels for t in r.get('targets',[r.get('target')])),r
  if r.get('target_heading'):assert r['target_heading'] in texts[f"ch{r['chapter']}"]
 assert (len(ledger['pages']),len(ledger['source_questions']),len(ledger['source_figures']))==(22,16,17)
 result['source_ledger']={'sha256':sha(LEDGER),'teaching_pages':22,'source_exercises':16,'source_figure_groups':17,
  'unresolved_recorded_targets':0,'granularity':'源页教学主题、逐题及逐组子图；非逐字词计数'}
 docs={}
 for key in revision.OLD_NAMES:
  p=BASE/key/f'{key}.pdf';d=fitz.open(p);docs[key]=d
  row={'sha256':sha(p),'pages':len(d),'bookmarks':len(d.get_toc())}
  for name,args in [('qpdf',['qpdf','--check',str(p)]),('fonts',['pdffonts',str(p)])]:
   q=subprocess.run(args,capture_output=True,text=True);(BASE/key/f'{name}-check.txt').write_text(q.stdout+q.stderr)
   assert q.returncode==0,(key,name,q.stderr)
   if name=='fonts':
    lines=q.stdout.splitlines()[2:];assert lines and all(re.search(r'\byes\s+yes\s+yes\s+\d+\s+\d+\s*$',s) for s in lines),q.stdout
    row['embedded_fonts_with_unicode']=len(lines)
  log=(BASE/key/f'{key}.log').read_text(errors='replace')
  warnings=[s for s in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined|multiply defined',s)]
  allowed=[r'Underfull \hbox (badness 1152) in paragraph at lines 311--313',r'Underfull \hbox (badness 1253) in paragraph at lines 26--26'] if key=='main' else []
  assert warnings==allowed,(key,warnings);row['inherited_unrelated_spacing_warnings']=warnings
  for n in (1,2):
   verify=(BASE/key/f'verify-pass-{n}.txt').read_text(errors='replace')
   assert 'Output written' in verify and 'Fatal error' not in verify
  assert d.get_toc() and all(1<=r[2]<=len(d) for r in d.get_toc())
  assert '\ufffd' not in ''.join(pg.get_text() for pg in d)
  if key in TITLES:
   t=texts[key];n,figs=COUNTS[key]
   assert t==revision.chapter_text(int(key[2:]))[0]
   assert sha(BOOK/f'generated/chapters/{key}.tex')==ledger['generated_sha256'][key]
   assert t.count(r'\begin{origexamplebox}')==t.count(r'\begin{xesolution}')==n
   fl=[x for x in re.findall(r'\\label\{([^}]+)\}',t) if ':fig:' in x]
   assert len(fl)==figs and all(r'\ref{'+x+'}' in t for x in fl)
   assert not re.search(r'原扫描|重绘|OCR|标校|学习目标|本节小结',t)
   assert not any(ord(c)<32 and c not in '\n\t' for c in t)
   starts=[]
   for i,pg in enumerate(d):
    tx=pg.get_text()
    for m in re.finditer(r'(?m)^例\s*'+key[2:]+r'\.(\d+)\s+',tx):
     remaining=tx[m.end():];nextq=re.search(r'(?m)^例\s*'+key[2:]+r'\.\d+\s+',remaining)
     if nextq:remaining=remaining[:nextq.start()]
     starts.append({'example':int(m[1]),'page':i+1,'solution_same_page':'解答' in remaining})
   assert sorted(x['example'] for x in starts)==list(range(1,n+1)) and all(x['solution_same_page'] for x in starts),starts
   row.update(source_sha256=sha(BOOK/f'generated/chapters/{key}.tex'),examples=n,figures=figs,figure_labels=fl,question_solution_adjacency=starts)
  else:
   toc=(BASE/key/f'{key}.toc').read_text();cp=[(int(ch),pg) for pg,ch in re.findall(r'\\contentsline \{chapter\}.*\{(\d+)\}\{chapter\.(\d+)\}',toc)]
   wanted=list(range(14,19)) if key=='volume3' else list(range(1,33));selected=[(ch,pg) for ch,pg in cp if ch in wanted][:len(wanted)]
   assert [c for c,p in selected]==wanted,(key,selected)
   top=[r for r in d.get_toc() if r[0]==1]
   for (_,printed),entry in zip(selected,top):assert printed==d[entry[2]-1].get_label()
   row['directory_pages_verified']=len(selected)
  result['pdfs'][key]=row
 for ch,title in TITLES.items():
  independent=docs[ch];expected=[body(p) for p in independent][1:]
  for key in ('volume3','main'):
   a,b=span(docs[key],title);actual=[body(docs[key][i]) for i in range(a,b)]
   assert actual==expected,(ch,key,len(actual),len(expected))
   diffs=[i+1 for i in range(b-a) if raster(independent[i+1])!=raster(docs[key][a+i])]
   result['pdfs'][key][ch+'_physical_pages']=[a+1,b];result['pdfs'][key][ch+'_raster_difference_body_pages']=diffs
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
 result['other_generated_chapters_unchanged']=30;result['recorded_frozen_source_xelatex_passes_per_pdf']=2
 save(BASE/'release-checks.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--geometry',action='store_true');p.add_argument('--release',action='store_true');a=p.parse_args()
 if a.geometry:geometry()
 if a.release:check()
