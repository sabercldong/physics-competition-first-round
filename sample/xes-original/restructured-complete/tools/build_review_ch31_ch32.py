"""Scoped modern-physics revision; archive first, stage builds, publish separately."""
import argparse, json, shutil, re
from pathlib import Path
import build_review_ch25_ch26 as shared
common=shared.common
book=common.book
BASE=book.BOOK/'build/revision-ch31-ch32-20260923'
ARCHIVE=book.PROJECT/'archive/2026-09-23-ch31-ch32-revision'
OLD_NAMES={'ch31':'高中物理竞赛一轮讲义_第31章_狭义相对论_含解答与解图.pdf',
 'ch32':'高中物理竞赛一轮讲义_第32章_量子现象、原子与原子核物理_含解答与解图.pdf',
 'volume6':'高中物理竞赛一轮讲义_第6卷_近代物理_含解答与解图.pdf',
 'main':'高中物理竞赛一轮讲义.pdf'}
def backup():
 if (ARCHIVE/'manifest.json').exists(): return
 # Resume an interrupted copy without deleting its recoverable partial archive.
 (ARCHIVE/'pdf').mkdir(parents=True,exist_ok=True)
 old={}
 for name in OLD_NAMES.values():
  p=common.FORMAL/name
  if not p.exists() and '_含解答与解图' in name:
   p=common.FORMAL/name.replace('_含解答与解图','')
  assert p.exists(),p
  target=ARCHIVE/'pdf'/p.name
  if target.exists(): assert common.sha(target)==common.sha(p)
  else: shutil.copy2(p,target)
  old[str(p)]=common.sha(p)
 shutil.copytree(book.BOOK,ARCHIVE/'source'/book.BOOK.name,dirs_exist_ok=True,
  ignore=shutil.ignore_patterns('build','.venv*','__pycache__','.git','*.synctex.gz','*.xdv','*.aux','*.log','*.fls','*.fdb_latexmk','*.out','*.toc'))
 protected={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch31','ch32'}}
 (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':old,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))
 BASE.mkdir(parents=True,exist_ok=True)
def regenerate():
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 mapping=json.loads((book.GENERATED/'source-map.json').read_text())
 for n,count in [(31,8),(32,12)]:
  body,maps=common.chapter_text(n)
  body=body.replace(r'\begin{center}',r'\begin{center}\begin{minipage}{\linewidth}\centering')
  body=body.replace(r'\end{center}',r'\end{minipage}\end{center}')
  reserve=r'''\renewcommand{\Needspace}[1]{\par\begingroup
\dimen0=#1\relax\vskip0pt plus\dimen0\penalty-100
\vskip0pt plus-\dimen0\vskip\dimen0\penalty9999\vskip-\dimen0
\vskip0pt\endgroup}
'''
  body=r'\begingroup\tcbset{breakable/.default=false}'+'\n'+reserve+body+'\n'+r'\endgroup'
  body=body.replace(r'\begin{starread}',r'\tcbset{breakable/.default=true}\begin{starread}')
  body=body.replace(r'\end{starread}',r'\end{starread}\tcbset{breakable/.default=false}')
  body=body.replace(r'\end{origexamplebox}',r'\end{origexamplebox}\par\nopagebreak[3]')
  # Unbreakable question boxes reserve their own height; duplicate elastic
  # reservations before them can trigger a second, premature page break.
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
  next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
 (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 # Refresh only the affected volume wrapper, retaining simple naming and cover.
 (book.GENERATED/'wrappers/volumes/volume6.tex').write_text(book._wrapper('第6卷　近代物理',[31,32],toc=True))
 assert all(common.sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
def build(key):
 paths=[book.BOOK/'chapters/new'/f for f in ('ch31-relativity.tex','ch32-modern.tex')]
 paths+=list((book.BOOK/'assets/diagrams-modern').glob('*.tex'))
 canonical={str(p):common.sha(p) for p in paths}
 shared.BASE=BASE; shared.build(key)
 assert all(common.sha(Path(p))==h for p,h in canonical.items())
 p=BASE/key/'frozen-build.json';data=json.loads(p.read_text());data['source_hashes'].update(canonical)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true');p.add_argument('--target',choices=OLD_NAMES);a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:build(a.target)
