"""Internal, scoped modern-source revision. Never publishes on compilation."""
import argparse, json, shutil, subprocess, os
from pathlib import Path
import build_review_ch31_ch32 as previous

book=previous.book
BASE=book.BOOK/'build/modern-source-revision-20260923'
ARCHIVE=book.PROJECT/'archive/2026-09-23-modern-source-revision'

def backup():
    if (ARCHIVE/'manifest.json').exists(): return
    (ARCHIVE/'pdf').mkdir(parents=True,exist_ok=True)
    saved={}
    for p in previous.common.FORMAL.glob('*.pdf'):
        if any(s in p.name for s in ('第31章','第32章','第6卷','第7卷','A6')) or p.name=='高中物理竞赛一轮讲义.pdf':
            shutil.copy2(p,ARCHIVE/'pdf'/p.name);saved[str(p)]=previous.common.sha(p)
    shutil.copytree(book.BOOK,ARCHIVE/'source'/book.BOOK.name,dirs_exist_ok=True,
        ignore=shutil.ignore_patterns('build','__pycache__','.git','*.synctex.gz','*.xdv','*.aux','*.log','*.fls','*.fdb_latexmk','*.out','*.toc'))
    protected={str(p):previous.common.sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem not in {'ch31','ch32'}}
    (ARCHIVE/'manifest.json').write_text(json.dumps({'old_formal':saved,'protected_generated_chapters':protected},ensure_ascii=False,indent=2))

def regenerate():
    previous.ARCHIVE=ARCHIVE; previous.BASE=BASE
    previous.regenerate()

def build_a6():
    out=BASE/'A6';out.mkdir(parents=True,exist_ok=True)
    wrapper=book.BOOK/'advanced/A6-standalone.tex'
    env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','')
    for n in (1,2):
        with (out/f'verify-pass-{n}.txt').open('w') as f:
            subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['xdvipdfmx','-q','-o',str(out/'A6-standalone.pdf'),str(out/'A6-standalone.xdv')],cwd=book.BOOK,env=env,check=True)
    hashes={}
    for line in (out/'A6-standalone.fls').read_text().splitlines():
        if not line.startswith('INPUT '):continue
        p=Path(line[6:]);p=(book.BOOK/p).resolve() if not p.is_absolute() else p.resolve()
        if p.is_file() and p.is_relative_to(book.PROJECT) and 'build' not in p.parts:
            hashes[str(p)]=previous.common.sha(p)
    (out/'frozen-build.json').write_text(json.dumps({'source_hashes':hashes,'passes':2,'pdf_sha256':previous.common.sha(out/'A6-standalone.pdf')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--regenerate',action='store_true')
    p.add_argument('--target',choices=['ch31','ch32','A6','volume6','volume7','main'])
    a=p.parse_args()
    if a.backup: backup()
    if a.regenerate: regenerate()
    if a.target=='A6':build_a6()
    elif a.target:
        # Chapter bodies inline TikZ inputs: compiling without regeneration
        # would silently retain old drawings despite newer canonical assets.
        if not a.regenerate:regenerate()
        previous.BASE=BASE; previous.build(a.target)
