"""Scoped optical revision. Back up before edits; never publish on build."""
import argparse,json,shutil,re
from pathlib import Path
import build_review_ch25_ch26 as shared
common=shared.common
book=common.book
BASE=book.BOOK/'build/revision-ch29-ch30-20260923'
ARCHIVE=book.PROJECT/'archive/2026-09-23-ch29-ch30-revision'
OLD_NAMES={'ch29':'高中物理竞赛一轮讲义_第29章_光的干涉_含解答与解图.pdf',
 'ch30':'高中物理竞赛一轮讲义_第30章_衍射、偏振与晶体光学_含解答与解图.pdf',
 'volume5':'高中物理竞赛一轮讲义_第5卷_光学.pdf','main':'高中物理竞赛一轮讲义.pdf'}
def backup():
 if (ARCHIVE/'manifest.json').exists():return
 assert not ARCHIVE.exists()
 (ARCHIVE/'pdf').mkdir(parents=True)
 old={}
 for name in OLD_NAMES.values():
  p=common.FORMAL/name;shutil.copy2(p,ARCHIVE/'pdf'/name);old[str(p)]=common.sha(p)
 for root in [book.BOOK,book.LEGACY/'forty-fourth-section',book.LEGACY/'forty-fifth-section']:
  shutil.copytree(root,ARCHIVE/'source'/root.name,ignore=shutil.ignore_patterns('build','__pycache__','.git','*.synctex.gz','*.xdv','*.aux','*.log','*.fls','*.fdb_latexmk','*.out','*.toc'))
 protected={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch29','ch30'}}
 (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':old,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))
 BASE.mkdir(parents=True,exist_ok=True)
def regenerate():
 baseline=json.loads((ARCHIVE/'manifest.json').read_text())
 mapping=json.loads((book.GENERATED/'source-map.json').read_text())
 for n,count in [(29,13),(30,16)]:
  body,maps=common.chapter_text(n)
  body=body.replace(r'\subsection*{',r'\section{')
  body=body.replace(r'\section{光的干涉}',r'\section{干涉现象与相干条件}')
  body=body.replace(r'\section{光的衍射}',r'\section{衍射现象与波动模型}')
  pattern=r'(\\historyfigure(?:\[[^\]]*\])?\{[^}]+\}\{[^\n]*?)\}\\label\{([^}]+)\}'
  body=re.sub(pattern,lambda m:m[1]+r'\label{'+m[2]+'}}',body)
  body=body.replace(r'\begin{center}',r'\begin{center}\begin{minipage}{\linewidth}\centering')
  body=body.replace(r'\end{center}',r'\end{minipage}\end{center}')
  body=r'\begingroup\tcbset{breakable/.default=false}'+'\n'+body+'\n'+r'\endgroup'
  body=body.replace(r'\begin{starread}',r'\tcbset{breakable/.default=true}\begin{starread}')
  body=body.replace(r'\end{starread}',r'\end{starread}\tcbset{breakable/.default=false}')
  body=body.replace(r'\end{origexamplebox}',r'\end{origexamplebox}\par\nopagebreak[3]')
  body=body.replace(r'\begin{origexamplebox}',r'\Needspace{7\baselineskip}\begin{origexamplebox}')
  assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
  (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
  next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
  (book.GENERATED/f'wrappers/chapters/ch{n}.tex').write_text(book._wrapper(f"第{n}章　{book.CHAPTERS[n]['title']}",[n],toc=False))
 (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
 assert all(common.sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
def build(key):
 paths=[]
 if key!='ch30':
  paths.extend(book.LEGACY/'forty-fourth-section'/name for name in ('content.tex','diagrams.tex'))
  paths.append(book.BOOK/'chapters/new/ch29-wave-coherence.tex')
 if key!='ch29':
  paths.extend(book.LEGACY/'forty-fifth-section'/name for name in ('content.tex','diagrams.tex'))
  paths.extend(book.BOOK/'chapters/new'/name for name in ('ch30-diffraction-theory.tex','ch30-polarization.tex'))
 canonical={str(p):common.sha(p) for p in paths}
 shared.BASE=BASE
 shared.build(key)
 assert all(common.sha(Path(p))==h for p,h in canonical.items())
 manifest=BASE/key/'frozen-build.json'
 frozen=json.loads(manifest.read_text());frozen['source_hashes'].update(canonical)
 manifest.write_text(json.dumps(frozen,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true');p.add_argument('--target',choices=OLD_NAMES);a=p.parse_args()
 if a.backup:backup()
 if a.regenerate:regenerate()
 if a.target:build(a.target)
