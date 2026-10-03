"""Scoped, non-publishing revision of chapters 17 and 18."""
import argparse, json, os, subprocess
import build_review_ch15_ch16 as common
book=common.book
BASE=book.BOOK/'build/revision-ch17-ch18-20260920'
ARCHIVE=book.PROJECT/'archive/2026-09-20-ch17-ch18-revision'
OLD_NAMES={
 'ch17':'高中物理竞赛一轮讲义_第17章_相变与表面现象_含解答与解图.pdf',
 'ch18':'高中物理竞赛一轮讲义_第18章_统计物理基础_含解答与解图.pdf',
 'volume3':'高中物理竞赛一轮讲义_第3卷_热学与统计物理.pdf',
 'main':'高中物理竞赛一轮讲义.pdf'}
def backup():
 import shutil
 if (ARCHIVE/'manifest.json').exists():return
 assert not ARCHIVE.exists()
 (ARCHIVE/'pdf').mkdir(parents=True)
 old={}
 for name in OLD_NAMES.values():
  p=common.FORMAL/name;shutil.copy2(p,ARCHIVE/'pdf'/name);old[str(p)]=common.sha(p)
 for root in [book.BOOK,book.LEGACY/'thirty-first-section']:
  shutil.copytree(root,ARCHIVE/'source'/root.name,ignore=shutil.ignore_patterns('build','__pycache__','.git'))
 protected={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch17','ch18'}}
 (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':old,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))
def regenerate():
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 mapping=json.loads((book.GENERATED/'source-map.json').read_text())
 for n,count in [(17,6),(18,7)]:
  body,maps=common.chapter_text(n)
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
  assert '@@BILINGUAL-' not in body
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
  next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
 (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 assert all(common.sha(__import__('pathlib').Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true');p.add_argument('--target',choices=OLD_NAMES);p.add_argument('--verify',action='store_true');p.add_argument('--extra-pass',action='store_true')
 a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:
  key=a.target;out=BASE/key;out.mkdir(parents=True,exist_ok=True)
  wrapper=book.BOOK/'main.tex' if key=='main' else book.GENERATED/f'wrappers/volumes/{key}.tex' if key.startswith('volume') else book.GENERATED/f'wrappers/chapters/{key}.tex'
  os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
  if not a.verify:book.compile_tex(wrapper,out)
  else:
   env=os.environ.copy();env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
   hashes={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('*.tex')}
   passes=(1,2)
   if a.extra_pass:
    prior=json.loads((out/'frozen-build.json').read_text())
    assert prior['source_hashes']==hashes and prior['pdf_sha256']==common.sha(out/f'{key}.pdf')
    passes=(prior['passes']+1,)
   for n in passes:
    with (out/f'verify-pass-{n}.txt').open('w') as f:
     subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-synctex=1','-recorder',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
   subprocess.run(['xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{key}.xdv')],cwd=book.BOOK,env=env,check=True)
   assert all(common.sha(__import__('pathlib').Path(p))==h for p,h in hashes.items())
   (out/'frozen-build.json').write_text(json.dumps({'source_hashes':hashes,'passes':passes[-1],'pdf_sha256':common.sha(out/f'{key}.pdf')},indent=2))
