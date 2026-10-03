"""Scoped chapter 21/22 build, archive first and publish separately."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
import build_review_ch15_ch16 as common
book=common.book
BASE=book.BOOK/'build/revision-ch21-ch22-20260920'
ARCHIVE=book.PROJECT/'archive/2026-09-20-ch21-ch22-revision'
OLD_NAMES={'ch21':'高中物理竞赛一轮讲义_第21章_恒定电流与复杂电路_含解答与解图.pdf',
 'ch22':'高中物理竞赛一轮讲义_第22章_洛伦兹力与带电粒子运动_含解答与解图.pdf',
 'volume4':'高中物理竞赛一轮讲义_第4卷_电磁学.pdf','main':'高中物理竞赛一轮讲义.pdf'}
def backup():
 if (ARCHIVE/'manifest.json').exists():return
 (ARCHIVE/'pdf').mkdir(parents=True,exist_ok=True)
 old={}
 for name in OLD_NAMES.values():
  p=common.FORMAL/name;shutil.copy2(p,ARCHIVE/'pdf'/name);old[str(p)]=common.sha(p)
 for root in [book.BOOK]+[book.LEGACY/(n+'-section') for n in ['thirty-sixth','thirty-seventh','thirty-eighth']]:
  shutil.copytree(root,ARCHIVE/'source'/root.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('build','__pycache__','.git','*.synctex.gz','*.xdv','*.aux','*.log','*.fls','*.fdb_latexmk','*.out','*.toc'))
 protected={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch21','ch22'}}
 (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':old,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))
def regenerate():
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 mapping=json.loads((book.GENERATED/'source-map.json').read_text())
 for n,count in [(21,18),(22,17)]:
  body,maps=common.chapter_text(n)
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
  next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
 (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 assert all(common.sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true');p.add_argument('--target',choices=OLD_NAMES);p.add_argument('--verification-only',action='store_true');a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:
  key=a.target;out=BASE/key;out.mkdir(parents=True,exist_ok=True)
  start_hashes={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('*.tex')}
  wrapper=book.BOOK/'main.tex' if key=='main' else book.GENERATED/f'wrappers/volumes/{key}.tex' if key.startswith('volume') else book.GENERATED/f'wrappers/chapters/{key}.tex'
  os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
  if not a.verification_only:book.compile_tex(wrapper,out)
  env=os.environ.copy();env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
  for n in (1,2):
   with (out/f'verify-pass-{n}.txt').open('w') as f:
    subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  subprocess.run(['xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{key}.xdv')],cwd=book.BOOK,env=env,check=True)
  assert all(common.sha(Path(p))==h for p,h in start_hashes.items()), 'Sources changed during compilation; repeat build after edits stop.'
  (out/'frozen-build.json').write_text(json.dumps({'source_hashes':start_hashes,'passes':2,'pdf_sha256':common.sha(out/f'{key}.pdf')},indent=2))
