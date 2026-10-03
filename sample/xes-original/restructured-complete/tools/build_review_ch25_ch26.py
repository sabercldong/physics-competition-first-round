"""Narrow chapter 25/26 revision; internal builds and explicit later publication."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
import build_review_ch15_ch16 as common
book=common.book
BASE=book.BOOK/'build/revision-ch25-ch26-20260922'
ARCHIVE=book.PROJECT/'archive/2026-09-22-ch25-ch26-revision'
OLD_NAMES={'ch25':'高中物理竞赛一轮讲义_第25章_交流电、相量与RLC电路_含解答与解图.pdf',
 'ch26':'高中物理竞赛一轮讲义_第26章_电磁场、电磁波与超导体_含解答与解图.pdf',
 'volume4':'高中物理竞赛一轮讲义_第4卷_电磁学.pdf','main':'高中物理竞赛一轮讲义.pdf'}
def backup():
 if (ARCHIVE/'manifest.json').exists():return
 assert not ARCHIVE.exists()
 (ARCHIVE/'pdf').mkdir(parents=True)
 old={}
 for name in OLD_NAMES.values():
  p=common.FORMAL/name;shutil.copy2(p,ARCHIVE/'pdf'/name);old[str(p)]=common.sha(p)
 for root in [book.BOOK,book.LEGACY/'forty-first-section']:
  shutil.copytree(root,ARCHIVE/'source'/root.name,ignore=shutil.ignore_patterns('build','__pycache__','.git','*.synctex.gz','*.xdv','*.aux','*.log','*.fls','*.fdb_latexmk','*.out','*.toc'))
 protected={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch25','ch26'}}
 (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':old,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))
 BASE.mkdir(parents=True,exist_ok=True)
def regenerate():
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 mapping=json.loads((book.GENERATED/'source-map.json').read_text())
 for n,count in [(25,8),(26,5)]:
  body,maps=common.chapter_text(n)
  # Bind each drawing to its caption; reserve room for question and opening reasoning.
  body=body.replace(r'\begin{center}',r'\begin{center}\begin{minipage}{\linewidth}\centering')
  body=body.replace(r'\end{center}',r'\end{minipage}\end{center}')
  body=r'\begingroup\tcbset{breakable/.default=false}'+'\n'+body+'\n'+r'\endgroup'
  body=body.replace(r'\end{origexamplebox}',r'\end{origexamplebox}\par\nopagebreak[3]')
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
  next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
 (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 assert all(common.sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
def build(key):
 out=BASE/key;out.mkdir(parents=True,exist_ok=True)
 hashes={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('*.tex')}
 for p in [book.BOOK/'chapters/new/ch25-ac.tex',book.BOOK/'chapters/new/ch26-em-waves.tex',
           book.LEGACY/'forty-first-section/content.tex',book.LEGACY/'forty-first-section/diagrams.tex',
           book.LEGACY/'forty-first-section/faithful-redraws.tex',book.BOOK/'style.tex']:
  hashes[str(p)]=common.sha(p)
 wrapper=book.BOOK/'main.tex' if key=='main' else book.GENERATED/f'wrappers/volumes/{key}.tex' if key.startswith('volume') else book.GENERATED/f'wrappers/chapters/{key}.tex'
 env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','');env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
 # A complete two-pass XeLaTeX run, with a third pass if the TOC changes.
 previous_toc=None
 for n in (1,2,3):
  with (out/f'verify-pass-{n}.txt').open('w') as f:
   subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  toc=out/f'{key}.toc';current_toc=common.sha(toc) if toc.exists() else None
  log=(out/f'{key}.log').read_text(errors='replace')
  if n>=2 and current_toc==previous_toc and 'Rerun to get' not in log and 'has changed. Rerun' not in log:break
  previous_toc=current_toc
 subprocess.run(['xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{key}.xdv')],cwd=book.BOOK,env=env,check=True)
 assert all(common.sha(Path(p))==h for p,h in hashes.items())
 # Bind the assets and local TeX inputs actually loaded, not merely the output PDF.
 for line in (out/f'{key}.fls').read_text(errors='replace').splitlines():
  if not line.startswith('INPUT '):continue
  p=Path(line[6:]);p=(book.BOOK/p).resolve() if not p.is_absolute() else p.resolve()
  if p.is_file() and p.is_relative_to(book.PROJECT) and 'build' not in p.parts and p.suffix.lower() in {'.tex','.sty','.png','.jpg','.jpeg','.pdf','.otf','.ttf'}:
   hashes[str(p)]=common.sha(p)
 (out/'frozen-build.json').write_text(json.dumps({'source_hashes':hashes,'passes':n,'pdf_sha256':common.sha(out/f'{key}.pdf')},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true');p.add_argument('--target',choices=OLD_NAMES);a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:build(a.target)
