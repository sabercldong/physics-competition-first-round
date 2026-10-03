"""Narrow rebuild of chapters 13/14; publication is a separate operation."""
import argparse, hashlib, json, os, shutil, subprocess
from pathlib import Path
import build_restructured as book

BASE=book.BOOK/'build/revision-ch13-ch14-20260912'
ARCHIVE=book.PROJECT/'archive/2026-09-12-ch13-ch14-revision'
FORMAL=book.PROJECT/'output/pdf'
OLD_NAMES={
 'ch13':'高中物理竞赛一轮讲义_第13章_流体静力学与动力学_含解答与解图.pdf',
 'ch14':'高中物理竞赛一轮讲义_第14章_温度、物态、理想气体与分子模型_含解答与解图.pdf',
 'volume2':'高中物理竞赛一轮讲义_第2卷_力学.pdf',
 'volume3':'高中物理竞赛一轮讲义_第3卷_热学与统计物理_含解答与解图.pdf',
 'main':'高中物理竞赛一轮讲义.pdf'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def backup():
 if (ARCHIVE/'manifest.json').exists():
  print('Frozen archive already exists; retained.');return
 assert not ARCHIVE.exists(), 'Inspect partial archive before retry'
 (ARCHIVE/'pdf').mkdir(parents=True)
 records={}
 for name in OLD_NAMES.values():
  p=FORMAL/name;shutil.copy2(p,ARCHIVE/'pdf'/name);records[str(p)]=sha(p)
 roots=[book.BOOK,book.LEGACY/'twenty-eighth-section',book.LEGACY/'kinematics-supplement']
 for root in roots:
  for p in root.rglob('*'):
   rel=p.relative_to(root)
   if not p.is_file() or any(x in {'build','.git','__pycache__'} for x in rel.parts):continue
   if p.suffix not in {'.tex','.py','.json','.jsonl','.txt','.map','.sty','.cfg','.md','.png','.jpg','.pdf'}:continue
   dest=ARCHIVE/'source'/root.name/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 protected={str(p):sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch13','ch14'}}
 (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':records,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))
 BASE.mkdir(parents=True,exist_ok=True)
 print('Archived five formal PDFs, corresponding build sources and both external maintenance directories.')
def chapter_text(n):
 spec=book.CHAPTERS[n];parts=[f"\\chapter{{{spec['title']}}}\n"];maps=[]
 for unit in spec['legacy']:
  body,objects=book.extract_legacy(unit,n);parts.append(body);maps.append({'source':unit.key,'objects':objects})
 for name in spec['new']:
  p=book.BOOK/'chapters/new'/name
  parts.append(book._qualify_existing_labels(book.flatten_inputs(p.read_text(),p.parent,set()),n))
 return book.apply_chapter_layout(n,book.normalize_visible_eponyms('\n'.join(parts))),maps
def regenerate():
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 mapping=json.loads((book.GENERATED/'source-map.json').read_text())
 for n,count in [(13,14),(14,11)]:
  text,maps=chapter_text(n)
  assert text.count(r'\begin{origexamplebox}')==text.count(r'\begin{xesolution}')==count
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(text)
  next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
 (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 for v,title,lo,hi in [(2,'力学',5,13),(3,'热学与统计物理',14,18)]:
  (book.GENERATED/f'wrappers/volumes/volume{v}.tex').write_text(book._wrapper(f'第{v}卷　{title}',list(range(lo,hi+1)),toc=True))
 assert all(sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
 print('Regenerated only chapters 13/14 and their wrappers; other 30 chapter sources unchanged.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true')
 p.add_argument('--target',choices=list(OLD_NAMES));p.add_argument('--verify-two-passes',action='store_true');p.add_argument('--verify-only',action='store_true')
 a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:
  key=a.target
  wrapper=book.BOOK/'main.tex' if key=='main' else book.GENERATED/f'wrappers/volumes/{key}.tex' if key.startswith('volume') else book.GENERATED/f'wrappers/chapters/{key}.tex'
  out=BASE/key;out.mkdir(parents=True,exist_ok=True)
  os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
  if not a.verify_only:book.compile_tex(wrapper,out)
  if a.verify_two_passes:
   env=os.environ.copy();env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
   for n in (1,2):
    with (out/f'verify-pass-{n}.txt').open('w') as f:
     subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-synctex=1','-recorder',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
   subprocess.run(['xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{key}.xdv')],cwd=book.BOOK,env=env,check=True)
if __name__=='__main__':main()
