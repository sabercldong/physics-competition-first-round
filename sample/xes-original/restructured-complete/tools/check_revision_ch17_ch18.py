"""Numerical checks and scoped PDF release regression (never publishes)."""
import json,re,math,subprocess,hashlib,argparse
from pathlib import Path
import fitz,numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
import build_review_ch17_ch18 as r
from check_revision_ch13_ch14 import body,raster,span
BOOK=r.book.BOOK;BASE=r.BASE
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def geometry():
 d={};p=lambda v:7.2/(3*v-1)-3/v**2
 a,m,b=.603401903,1.090526633,2.348842376;pt=.646998352
 s1=quad(lambda v:pt-p(v),a,m)[0];s2=quad(lambda v:p(v)-pt,m,b)[0]
 assert abs(s1-s2)<1e-8 and max(abs(p(v)-pt) for v in (a,m,b))<1e-8
 d['maxwell']={'S1':s1,'S2':s2,'relative_difference':abs(s1-s2)/s1,'intersection_max_residual':max(abs(p(v)-pt) for v in (a,m,b))}
 assert -24/(3-1)**2+6==0 and 144/(3-1)**3-18==0
 d['critical_first_second_derivatives']=[0,0]
 # PABQ lies above the coexistence curve on its whole domain; BQ is at T>Tc.
 assert 1.5>(.2+.2*1**2) and 4.6>(.2+.2*4**2) and 5>4
 d['critical_bypass_no_crossing']=True
 d['mixed_gas_states']=[(.5,5),(1,3),(2,2),(4,1)]
 for x,y in d['mixed_gas_states']:assert abs(y-(1+2/x if x<=2 else 4/x))<1e-12
 water=json.loads((BASE/'water-data.json').read_text());tab=np.genfromtxt(BOOK/'assets/ch17/saturation.dat',names=True)
 for temp,col in [(water['lift_C'],'total'),(120,'ps')]:
  assert abs(np.interp(temp,tab['t'],tab[col])-water['p120_kPa'])<1e-4
 d['water']=water
 td=278.474927;actual=.6*(td/288)**3.5;sat=math.exp(44000/8.314*(1/288-1/td))
 assert abs(actual-sat)<1e-8;d['cloud_intersection']={'T':td,'residual':abs(actual-sat),'z_m':(288-td)/.0097}
 d['speed_distribution_integrals']=[quad(lambda x:4/math.sqrt(math.pi)*a**1.5*x*x*math.exp(-a*x*x),0,np.inf)[0] for a in [1,.5]]
 assert max(abs(x-1) for x in d['speed_distribution_integrals'])<1e-10
 f=lambda x:math.exp(-x*x/2)/math.sqrt(2*math.pi)
 d['energy_gaussian']={'integral':quad(f,-np.inf,np.inf)[0],'variance':quad(lambda x:x*x*f(x),-np.inf,np.inf)[0],'marked_interval':[-1,1]}
 assert abs(d['energy_gaussian']['variance']-1)<1e-10
 d['geometric_probability_sum']=sum(.4*.6**n for n in range(200));assert abs(d['geometric_probability_sum']-1)<1e-12
 t=(BOOK/'chapters/new/ch18-statistical.tex').read_text()
 mix=t.split(r'\subsection{理想气体混合熵}')[1].split(r'\figcap')[0]
 groups=re.findall(r'\\foreach \\p in \{([^\n]+)\}',mix)
 counts=[len(re.findall(r'\([^()]+\)',g)) for g in groups];assert counts==[5,5,5,5];d['mixing_counts']=counts
 d['source_sha256']={f'ch{n}':sha(BOOK/f'generated/chapters/ch{n}.tex') for n in [17,18]}
 (BASE/'geometry-checks.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));print('Numerical checks passed')
def release():
 result={'pdfs':{},'scope':'17–18章修订；其他章只作构建回归'};docs={}
 for key in r.OLD_NAMES:
  p=BASE/key/f'{key}.pdf';d=fitz.open(p);docs[key]=d
  row={'pages':len(d),'sha256':sha(p),'bookmarks':len(d.get_toc())}
  for name,args in [('qpdf',['qpdf','--check',str(p)]),('fonts',['pdffonts',str(p)])]:
   q=subprocess.run(args,capture_output=True,text=True);(BASE/key/f'{name}-check.txt').write_text(q.stdout+q.stderr);assert q.returncode==0,(key,name,q.stderr)
   if name=='fonts':assert all(re.search(r'\byes\s+yes\s+yes\s+\d+\s+\d+\s*$',s) for s in q.stdout.splitlines()[2:]),q.stdout
  log=(BASE/key/f'{key}.log').read_text(errors='replace')
  ws=[s for s in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined|multiply defined',s)]
  allowed=[r'Underfull \hbox (badness 1152) in paragraph at lines 311--313',r'Underfull \hbox (badness 1253) in paragraph at lines 26--26'] if key=='main' else []
  assert ws==allowed,(key,ws);row['inherited_unrelated_spacing_warnings']=ws
  frozen=json.loads((BASE/key/'frozen-build.json').read_text());assert frozen['pdf_sha256']==sha(p) and frozen['passes']>=2
  assert all(sha(Path(x))==h for x,h in frozen['source_hashes'].items())
  assert all(1<=x[2]<=len(d) for x in d.get_toc())
  text=''.join(p.get_text() for p in d);assert '\ufffd' not in text
  if key in ['ch17','ch18']:
   src=(BOOK/f'generated/chapters/{key}.tex').read_text();expected=6 if key=='ch17' else 7
   assert src.count(r'\begin{origexamplebox}')==src.count(r'\begin{xesolution}')==expected
   labels=re.findall(r'\\label\{([^}]+)\}',src);assert len(labels)==len(set(labels))
   figs=[x for x in labels if ':fig:' in x or ':ref:fig-' in x]
   assert len(figs)==(11 if key=='ch17' else 5)
   assert all(r'\ref{'+x+'}' in src for x in figs)
   assert not re.search(r'@@BILINGUAL|原扫描|重绘|OCR|标校|学习目标|本节小结',text)
   starts=[]
   for i,p in enumerate(d):
    tx=p.get_text()
    for m in re.finditer(r'(?m)^例\s*'+key[2:]+r'\.(\d+)\s+',tx):
     remaining=tx[m.end():];nextq=re.search(r'(?m)^例\s*'+key[2:]+r'\.\d+\s+',remaining)
     if nextq:remaining=remaining[:nextq.start()]
     starts.append({'number':int(m[1]),'page':i+1,'answer_starts_same_page':'解答' in remaining})
   assert len(starts)==expected and all(x['answer_starts_same_page'] for x in starts),starts
   row.update(examples=expected,figures=len(figs),source_sha256=sha(BOOK/f'generated/chapters/{key}.tex'),question_adjacency=starts)
  else:
   toc=(BASE/key/f'{key}.toc').read_text();cp=[(int(ch),pg) for pg,ch in re.findall(r'\\contentsline \{chapter\}.*\{(\d+)\}\{chapter\.(\d+)\}',toc)]
   wanted=list(range(14,19)) if key=='volume3' else list(range(1,33));selected=[(c,p) for c,p in cp if c in wanted][:len(wanted)]
   assert [c for c,p in selected]==wanted
   for (_,printed),entry in zip(selected,[x for x in d.get_toc() if x[0]==1]):assert printed==d[entry[2]-1].get_label()
   row['directory_pages_checked']=len(selected)
  result['pdfs'][key]=row
 for ch in ['ch17','ch18']:
  title=r.book.CHAPTERS[int(ch[2:])]['title'];ind=docs[ch]
  for key in ['main','volume3']:
   a,b=span(docs[key],title);assert b-a==len(ind)-1
   diffs=[j+1 for j in range(b-a) if body(ind[j+1])!=body(docs[key][a+j]) or raster(ind[j+1])!=raster(docs[key][a+j])]
   assert not diffs,(ch,key,diffs);result['pdfs'][key][ch+'_pages']=[a+1,b]
 old=fitz.open(r.ARCHIVE/'pdf/高中物理竞赛一轮讲义.pdf')
 def retained(d):
  excluded=set()
  for n in [17,18]:
   a,b=span(d,r.book.CHAPTERS[n]['title']);excluded.update(range(a,b))
  first=next(x[2]-1 for x in d.get_toc() if x[0]==1)
  return [i for i in range(first,len(d)) if i not in excluded]
 op,npages=retained(old),retained(docs['main']);assert len(op)==len(npages)
 diffs=[]
 for i,j in zip(op,npages):
  if body(old[i])!=body(docs['main'][j]) or raster(old[i])!=raster(docs['main'][j]):diffs.append([i+1,j+1])
 assert not diffs,diffs[:20]
 result['other_main_body_pages_identical']=len(op)
 archive=json.loads((r.ARCHIVE/'manifest.json').read_text())
 assert all(sha(Path(p))==h for p,h in archive['protected_generated_chapters'].items())
 assert all(sha(Path(p))==h for p,h in archive['old_formal'].items())
 result['protected_chapters']=30
 (BASE/'release-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--geometry',action='store_true');p.add_argument('--release',action='store_true');a=p.parse_args()
 if a.geometry:geometry()
 if a.release:release()
