"""Scoped release checks. Numerical and file checks do not replace visual review."""
import json,re,subprocess,hashlib
from pathlib import Path
import fitz
import build_review_ch19_ch20 as r
from check_revision_ch13_ch14 import body,raster,span
BASE=r.BASE;BOOK=r.book.BOOK
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def release():
 result={'scope':'第19—20章修订；其他章仅作合订回归','pdfs':{}};docs={}
 for key in r.OLD_NAMES:
  p=BASE/key/f'{key}.pdf';d=fitz.open(p);docs[key]=d
  row={'pages':len(d),'sha256':sha(p),'bookmarks':len(d.get_toc())}
  for name,args in [('qpdf',['qpdf','--check',str(p)]),('fonts',['pdffonts',str(p)])]:
   q=subprocess.run(args,capture_output=True,text=True);(BASE/key/f'{name}-check.txt').write_text(q.stdout+q.stderr)
   assert q.returncode==0,(key,name,q.stderr)
   if name=='fonts':assert all(re.search(r'\byes\s+yes\s+yes\s+\d+\s+\d+\s*$',s) for s in q.stdout.splitlines()[2:]),q.stdout
  log=(BASE/key/f'{key}.log').read_text(errors='replace')
  ws=[s for s in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined|multiply defined',s)]
  allowed=[r'Underfull \hbox (badness 1152) in paragraph at lines 311--313',r'Underfull \hbox (badness 1253) in paragraph at lines 26--26'] if key=='main' else []
  assert ws==allowed,(key,ws);row['inherited_unrelated_spacing_warnings']=ws
  frozen=json.loads((BASE/key/'frozen-build.json').read_text());assert frozen['pdf_sha256']==sha(p) and frozen['passes']>=2
  # A standalone chapter does not depend on the other 31 chapter bodies.
  assert all(sha(Path(x))==h for x,h in frozen['source_hashes'].items() if not key.startswith('ch') or Path(x).stem==key)
  assert all(1<=x[2]<=len(d) for x in d.get_toc())
  txt=''.join(p.get_text() for p in d);assert '\ufffd' not in txt
  if key=='main':
   # The existing book intentionally uses square signs for proofs, the wave
   # operator, and rectangle-cycle subscripts. Do not confuse these with a
   # missing-font glyph, or silently extend this revision to other chapters.
   oldtxt=''.join(body(p) for p in fitz.open(r.ARCHIVE/'pdf/高中物理竞赛一轮讲义.pdf'))
   newtxt=''.join(body(p) for p in d)
   contexts=lambda s:[s[max(0,i-20):i+21] for i,c in enumerate(s) if c=='\u25a1']
   assert contexts(newtxt)==contexts(oldtxt), 'A new square symbol requires visual review'
   row['unchanged_square_symbol_contexts']=len(contexts(newtxt))
  else:assert '\u25a1' not in txt
  if key in ['ch19','ch20']:
   src=(BOOK/f'generated/chapters/{key}.tex').read_text();expected=16 if key=='ch19' else 21
   assert src.count(r'\begin{origexamplebox}')==src.count(r'\begin{xesolution}')==expected
   labels=re.findall(r'\\label\{([^}]+)\}',src);assert len(labels)==len(set(labels))
   figs=[x for x in labels if ':fig:' in x];assert len(figs)==(14 if key=='ch19' else 25)
   assert all(r'\ref{'+x+'}' in src for x in figs),[x for x in figs if r'\ref{'+x+'}' not in src]
   assert not re.search(r'@@BILINGUAL|原扫描|重绘|OCR|标校|学习目标|本节小结',txt)
   assert not re.search(r'式\s*[（(][1-4]\.\d+',txt)
   render=json.loads((BASE/'render'/key/'manifest.json').read_text());assert render['sha256']==sha(p)
   row.update(examples=expected,numbered_source_figures=len(figs),source_sha256=sha(BOOK/f'generated/chapters/{key}.tex'))
   for i,pg in enumerate(d):
    tx=pg.get_text()
    assert not re.search(r'解答\s*\d*\s*$',tx),(key,'orphan answer',i+1)
  else:
   toc=(BASE/key/f'{key}.toc').read_text()
   cp=[(int(ch),pg) for pg,ch in re.findall(r'\\contentsline \{chapter\}.*\{(\d+)\}\{chapter\.(\d+)\}',toc)]
   wanted=list(range(19,27)) if key=='volume4' else list(range(1,33));selected=[(c,p) for c,p in cp if c in wanted][:len(wanted)]
   assert [c for c,p in selected]==wanted
   for (_,printed),entry in zip(selected,[x for x in d.get_toc() if x[0]==1]):assert printed==d[entry[2]-1].get_label()
   row['directory_pages_checked']=len(selected)
  result['pdfs'][key]=row
 for ch in ['ch19','ch20']:
  title=r.book.CHAPTERS[int(ch[2:])]['title'];ind=docs[ch]
  for key in ['main','volume4']:
   a,b=span(docs[key],title);assert b-a==len(ind)-1,(ch,key,b-a,len(ind)-1)
   diffs=[j+1 for j in range(b-a) if body(ind[j+1])!=body(docs[key][a+j]) or raster(ind[j+1])!=raster(docs[key][a+j])]
   assert not diffs,(ch,key,diffs);result['pdfs'][key][ch+'_pages']=[a+1,b]
 old=fitz.open(r.ARCHIVE/'pdf/高中物理竞赛一轮讲义.pdf')
 def retained(d):
  excluded=set()
  for n in [19,20]:
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
 result['geometry']=json.loads((BASE/'geometry-checks.json').read_text())
 (BASE/'release-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':release()
