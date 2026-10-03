"""Scoped correction of chapters 7--10. Shared books require coordinated publication."""
import argparse,json,re,hashlib,os,subprocess
from pathlib import Path
import build_revision_ch28_ch29 as compiler
book=compiler.book
BASE=book.BOOK/'build/revision-ch06-ch10-20260923'
compiler.BASE=BASE

def source_snapshot(wrapper):
 pending=[wrapper];seen={}
 while pending:
  p=pending.pop().resolve()
  if str(p) in seen:continue
  raw=p.read_text();seen[str(p)]=compiler.sha(p)
  for name in re.findall(r'\\(?:input|include)\{([^}]+)\}',raw):
   if not name.endswith('.tex'):name+='.tex'
   q=book.BOOK/name
   if not q.exists():q=p.parent/name
   if q.exists():pending.append(q)
 return seen

sha=compiler.sha

def build(key,passes=3):
 wrapper=book.BOOK/'main.tex' if key=='main' else book.BOOK/'advanced/A5-standalone.tex' if key=='A5' else book.GENERATED/f'wrappers/volumes/{key}.tex' if key.startswith('volume') else book.GENERATED/f'wrappers/chapters/{key}.tex'
 stem=wrapper.stem;out=BASE/key;out.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','');env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
 before=source_snapshot(wrapper)
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

def regenerate():
 for n,questions,figures in [(7,36,54),(8,17,27),(9,19,31),(10,9,33)]:
  spec=book.CHAPTERS[n];parts=[f"\\chapter{{{spec['title']}}}\n"]
  if spec.get('legacy'):
   for unit in spec['legacy']:
    body,_=book.extract_legacy(unit,n);parts.append(body)
  else:
   for name in spec['new']:
    p=book.BOOK/'chapters/new'/name;parts.append(book.flatten_inputs(p.read_text(),p.parent,set()))
  body=book.apply_chapter_layout(n,book.normalize_visible_eponyms('\n'.join(parts)))
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==questions
  assert body.count(r'\label{ch'+f'{n:02}'+':fig:')==figures,(n,body.count(r'\label{ch'+f'{n:02}'+':fig:'))
  (book.GENERATED/f'chapters/ch{n:02}.tex').write_text(body)
  (book.GENERATED/f'wrappers/chapters/ch{n:02}.tex').write_text(book._wrapper(f"第{n}章　{spec['title']}",[n],toc=False))
  print(n,questions,figures,flush=True)
 # Source problem identifiers are retained. Additional analysis/initial-state labels
 # supplement the existing mapping without changing any peer chapter's map.
 p=book.GENERATED/'source-map.json';m=json.loads(p.read_text())
 for n in (9,10):
  c=next(c for c in m['chapters'] if c['chapter']==n)
  c['revision_20260923']={'description':'题图与解图分离；原题映射锚点保留','added_figure_labels':(['ch09:fig:bounce-analysis','ch09:fig:rod-analysis'] if n==9 else ['ch10:fig:'+k+'-problem' for k in ['friction','governor','chain','wedges']])}
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--regenerate',action='store_true');p.add_argument('--target');p.add_argument('--passes',type=int,default=3);a=p.parse_args();BASE.mkdir(parents=True,exist_ok=True)
 if a.regenerate:regenerate()
 if a.target:build(a.target,a.passes)
