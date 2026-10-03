"""Narrow chapter 11/12 revision build. Publication is a separate, gated operation."""
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
import build_restructured as book
BASE=book.BOOK/'build/revision-ch11-ch12-20260912'
ARCHIVE=book.PROJECT/'archive/2026-09-12-ch11-ch12-revision'
FORMAL=book.PROJECT/'output/pdf'
OLD_NAMES={
 'ch11':'高中物理竞赛一轮讲义_第11章_有心力、万有引力与天体运动_含解答与解图.pdf',
 'ch12':'高中物理竞赛一轮讲义_第12章_弹性体与机械波_含解答与解图.pdf',
 'volume2':'高中物理竞赛一轮讲义_第2卷_力学.pdf',
 'main':'高中物理竞赛一轮讲义.pdf'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def backup():
 if (ARCHIVE/'manifest.json').exists():
  print('Existing frozen archive retained.');return
 assert not ARCHIVE.exists(), 'Inspect partial archive before retrying'
 (ARCHIVE/'pdf').mkdir(parents=True)
 records={}
 for name in OLD_NAMES.values():
  p=FORMAL/name;shutil.copy2(p,ARCHIVE/'pdf'/name);records[str(p)]=sha(p)
 for p in book.BOOK.rglob('*'):
  rel=p.relative_to(book.BOOK)
  if not p.is_file() or rel.parts[0] in {'build','.git','__pycache__'}:continue
  if p.suffix not in {'.tex','.py','.json','.jsonl','.txt','.map','.sty','.cfg','.md'}:continue
  dest=ARCHIVE/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 protected={str(p):sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch11','ch12'}}
 record={'old_formal':records,'protected_generated_chapters':protected,'scope':'Chapter 11 and 12 only; source assets outside this project remain referenced in place.'}
 (ARCHIVE/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
 BASE.mkdir(parents=True,exist_ok=True)
 print('Archived four PDFs and the corresponding text/build source snapshot.')
def regenerate():
 assert (ARCHIVE/'manifest.json').exists()
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 for n in (11,12):
  spec=book.CHAPTERS[n];parts=[f"\\chapter{{{spec['title']}}}\n"]
  for name in spec['new']:
   path=book.BOOK/'chapters/new'/name
   parts.append(book.flatten_inputs(path.read_text(),path.parent,set()))
  text=book.apply_chapter_layout(n,book.normalize_visible_eponyms('\n'.join(parts)))
  assert text.count(r'\begin{origexamplebox}')==(8 if n==11 else 14)
  assert text.count(r'\begin{xesolution}')==(8 if n==11 else 14)
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(text)
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{spec['title']}",[n],toc=False))
 (book.GENERATED/'wrappers/volumes/volume2.tex').write_text(book._wrapper('第2卷　力学',list(range(5,14)),toc=True))
 assert all(sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
 print('Regenerated only chapters 11 and 12; all other generated chapter hashes unchanged.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true')
 p.add_argument('--target',choices=list(OLD_NAMES));p.add_argument('--verify-two-passes',action='store_true');p.add_argument('--verify-only',action='store_true')
 a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:
  key=a.target;wrapper=(book.BOOK/'main.tex' if key=='main' else book.GENERATED/'wrappers/volumes/volume2.tex' if key=='volume2' else book.GENERATED/f'wrappers/chapters/{key}.tex')
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
