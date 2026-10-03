"""Scoped, non-publishing revision of optics chapters 27 and 28."""
import argparse,json,shutil,re
from pathlib import Path
import build_review_ch25_ch26 as shared
common=shared.common
book=common.book
BASE=book.BOOK/'build/revision-ch27-ch28-20260923'
ARCHIVE=book.PROJECT/'archive/2026-09-23-ch27-ch28-revision'
OLD_NAMES={'ch27':'高中物理竞赛一轮讲义_第27章_几何光学：光线、反射和折射_含解答与解图.pdf',
 'ch28':'高中物理竞赛一轮讲义_第28章_成像与光学仪器_含解答与解图.pdf',
 'volume5':'高中物理竞赛一轮讲义_第5卷_光学_含解答与解图.pdf','main':'高中物理竞赛一轮讲义.pdf'}
def backup():
 if (ARCHIVE/'manifest.json').exists():return
 # Resume a failed pre-edit backup only when every existing copied PDF matches.
 for p in (ARCHIVE/'pdf').glob('*.pdf'):
  assert common.sha(p)==common.sha(common.FORMAL/p.name)
 (ARCHIVE/'pdf').mkdir(parents=True,exist_ok=True)
 old={}
 for name in OLD_NAMES.values():
  p=common.FORMAL/name;shutil.copy2(p,ARCHIVE/'pdf'/name);old[str(p)]=common.sha(p)
 for root in [book.BOOK,book.LEGACY/'forty-second-section',book.LEGACY/'forty-third-section']:
  shutil.copytree(root,ARCHIVE/'source'/root.name,ignore=shutil.ignore_patterns('build','__pycache__','.git','*.synctex.gz','*.xdv','*.aux','*.log','*.fls','*.fdb_latexmk','*.out','*.toc'))
 protected={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch27','ch28'}}
 (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':old,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))
 BASE.mkdir(parents=True,exist_ok=True)
def regenerate():
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 mapping=json.loads((book.GENERATED/'source-map.json').read_text())
 for n,count in [(27,14),(28,10)]:
  body,maps=common.chapter_text(n)
  body=body.replace(r'\subsection*{',r'\section{')
  body=body.replace(r'\section{光线的性质}',r'\section{光的描述与光学发展}')
  body=body.replace(r'\section{几何光学成像}',r'\section{成像要求与器件加工}')
  # Captions increment the figure within historyfigure's local group.
  # Move auto labels inside that argument so the displayed reference is correct.
  pattern=r'(\\historyfigure(?:\[[^\]]*\])?\{[^}]+\}\{[^\n]*?)\}\\label\{([^}]+)\}'
  body=re.sub(pattern,lambda m:m[1]+r'\label{'+m[2]+'}}',body)
  body=body.replace(r'\begin{center}',r'\begin{center}\begin{minipage}{\linewidth}\centering')
  body=body.replace(r'\end{center}',r'\end{minipage}\end{center}')
  body=r'\begingroup\tcbset{breakable/.default=false}'+'\n'+body+'\n'+r'\endgroup'
  body=body.replace(r'\end{origexamplebox}',r'\end{origexamplebox}\par\nopagebreak[3]')
  body=body.replace(r'\begin{origexamplebox}',r'\Needspace{7\baselineskip}\begin{origexamplebox}')
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
  next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
 (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 assert all(common.sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
def build(key):
 shared.BASE=BASE
 shared.build(key)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true');p.add_argument('--target',choices=OLD_NAMES);a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:build(a.target)
