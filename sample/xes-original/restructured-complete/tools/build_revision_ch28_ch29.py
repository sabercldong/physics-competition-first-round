"""Scoped 28/29/A5 revision build; publication is a separate explicit step."""
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path
import build_review_ch15_ch16 as common
book=common.book
BASE=book.BOOK/'build/revision-ch28-ch29-20260923'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regenerate():
 maps=[]
 for n,count in [(28,10),(29,13)]:
  body,m=common.chapter_text(n)
  body=body.replace(r'\subsection*{',r'\section{')
  body=body.replace(r'\section{光学仪器}',r'\section{成像与仪器原理}').replace(r'\section{光的干涉}',r'\section{干涉现象与相干条件}')
  pat=r'(\\historyfigure(?:\[[^\]]*\])?\{[^}]+\}\{[^\n]*?)\}\\label\{([^}]+)\}'
  body=re.sub(pat,lambda x:x[1]+r'\label{'+x[2]+'}}',body)
  body=body.replace(r'\begin{center}',r'\begin{center}\begin{minipage}{\linewidth}\centering').replace(r'\end{center}',r'\end{minipage}\end{center}')
  body=r'\begingroup\tcbset{breakable/.default=false}'+'\n'+body+'\n'+r'\endgroup'
  body=body.replace(r'\begin{starread}',r'\tcbset{breakable/.default=true}\begin{starread}').replace(r'\end{starread}',r'\end{starread}\tcbset{breakable/.default=false}')
  body=body.replace(r'\end{origexamplebox}',r'\end{origexamplebox}\par\nopagebreak[3]')
  body=body.replace(r'\begin{origexamplebox}',r'\Needspace{8\baselineskip}\begin{origexamplebox}')
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
  maps.append({'chapter':n,'source_number_maps':m})
 (BASE/'chapter-mapping.json').write_text(json.dumps(maps,ensure_ascii=False,indent=2))
 # Re-read immediately before narrow map update, retaining peer chapters.
 path=book.GENERATED/'source-map.json';mapping=json.loads(path.read_text())
 for m in maps:next(c for c in mapping['chapters'] if c['chapter']==m['chapter'])['source_number_maps']=m['source_number_maps']
 path.write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 print('Regenerated only chapters 28/29.')
def build(key,passes=3):
 wrapper=book.BOOK/'main.tex' if key=='main' else book.BOOK/'advanced/A5-standalone.tex' if key=='A5' else book.GENERATED/f'wrappers/volumes/{key}.tex' if key.startswith('volume') else book.GENERATED/f'wrappers/chapters/{key}.tex'
 stem=wrapper.stem;out=BASE/key;out.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','');env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
 before={str(p):sha(p) for p in book.BOOK.rglob('*.tex') if 'build' not in p.relative_to(book.BOOK).parts}
 for i in range(1,passes+1):
  with (out/f'pass-{i}.txt').open('w') as f:
   proc=subprocess.run(['/Library/TeX/texbin/xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT)
  if proc.returncode:raise RuntimeError((out/f'pass-{i}.txt').read_text()[-3000:])
 subprocess.run(['/Library/TeX/texbin/xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{stem}.xdv')],cwd=book.BOOK,env=env,check=True)
 actual={}
 for l in (out/f'{stem}.fls').read_text().splitlines():
  if not l.startswith('INPUT '):continue
  p=Path(l[6:]);p=p if p.is_absolute() else book.BOOK/p;p=p.resolve()
  if p.is_file() and p.suffix in {'.tex','.png','.jpg','.pdf','.sty','.map'} and str(p).startswith(str(book.PROJECT)) and '/build/' not in str(p):actual[str(p)]=sha(p)
 changed=[p for p,h in actual.items() if p in before and before[p]!=h]
 assert not changed, f'Inputs changed during compilation: {changed}'
 log=(out/f'{stem}.log').read_text();bad=[l for l in log.splitlines() if any(t in l for t in ['Missing character','undefined','multiply defined','Overfull'])]
 manifest={'target':key,'pdf':str(out/f'{key}.pdf'),'pdf_sha256':sha(out/f'{key}.pdf'),'input_hashes':actual,'warnings':bad,'passes':passes}
 (out/'frozen-build.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(key,'built; warnings:',bad)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--passes',type=int,default=3);p.add_argument('--regenerate',action='store_true');p.add_argument('--target',choices=['ch28','ch29','A5','volume5','volume7','main']);a=p.parse_args();BASE.mkdir(parents=True,exist_ok=True)
 if a.regenerate:regenerate()
 if a.target:build(a.target,a.passes)
