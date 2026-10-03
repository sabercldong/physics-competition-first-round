"""Narrow, recoverable first-five-chapter revision; never publishes by building."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import build_restructured as book

BASE = book.BOOK / 'build/revision-ch01-05-20260923'
ARCHIVE = book.PROJECT / 'archive/20260923-ch01-05-before-revision'
COUNTS = {1:36, 2:21, 3:51, 4:32, 5:31}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def backup():
    assert not ARCHIVE.exists(), 'Backup already exists; do not overwrite it.'
    ARCHIVE.mkdir(parents=True)
    manifest = {}
    dirs = [book.BOOK/'chapters', book.BOOK/'generated', book.BOOK/'tools',
            *(book.LEGACY/x for x in ['kinematics-supplement','fourteenth-section',
              'fifteenth-section','first-section','second-section','third-section'])]
    for root in dirs:
        for p in root.rglob('*'):
            if p.is_file() and p.suffix in {'.tex','.json','.jsonl','.py','.sty'} and 'build' not in p.relative_to(root).parts:
                dst = ARCHIVE/'sources'/p.relative_to(book.PROJECT)
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(p,dst)
                manifest[str(p)] = sha(p)
    formal = {}
    for p in book.OUTPUT.glob('*.pdf'):
        if any(f'第{n:02}章_' in p.name for n in COUNTS) or any(f'第{v}卷_' in p.name for v in (1,2)) or p.name == '高中物理竞赛一轮讲义.pdf':
            dst=ARCHIVE/'pdf'/p.name
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dst)
            formal[str(p)]=sha(p)
    (ARCHIVE/'manifest.json').write_text(json.dumps({'sources':manifest,'formal':formal},ensure_ascii=False,indent=2))
    BASE.mkdir(parents=True,exist_ok=True)
    print('Archived',len(manifest),'source files and',len(formal),'formal PDFs.')

def regenerate():
    protected={str(p):sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if int(p.stem[2:]) not in COUNTS}
    mapping_path=book.GENERATED/'source-map.json'
    mapping=json.loads(mapping_path.read_text())
    for n,count in COUNTS.items():
        spec=book.CHAPTERS[n]
        parts=[f"\\chapter{{{spec.get('display_title',spec['title'])}}}\n"]
        rendered,maps={},[]
        for unit in spec['legacy']:
            rendered[unit.key],objects=book.extract_legacy(unit,n)
            maps.append({'source':unit.key,'objects':objects})
        if n==1:
            source=(book.BOOK/'chapters/new/ch01-math-foundations.tex').read_text()
            tmark,pmark=r'\section{泰勒展开与近似的阶}',r'\section{复数相量}'
            basics,rest=source.split(tmark,1)
            taylor,tail=rest.split(pmark,1)
            parts.extend([book._qualify_existing_labels(basics,n),rendered['s14'],book._qualify_existing_labels(tmark+taylor,n),rendered['s15'],book._qualify_existing_labels(pmark+tail,n)])
        else:
            parts.extend(rendered.values())
        content=book.normalize_visible_eponyms('\n'.join(parts))
        assert content.count(r'\begin{origexamplebox}')==count,(n,'examples')
        assert content.count(r'\begin{xesolution}')==count,(n,'solutions')
        content=book.apply_chapter_layout(n,content)
        (book.GENERATED/f'chapters/ch{n:02}.tex').write_text(content)
        next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
        (book.GENERATED/f'wrappers/chapters/ch{n:02}.tex').write_text(book._wrapper(f"第{n}章　{spec.get('display_title',spec['title'])}",[n],toc=False))
    mapping_path.write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
    assert all(sha(p)==h for p,h in protected.items())
    (BASE/'protected-chapters.json').write_text(json.dumps(protected,indent=2))
    print('Regenerated chapters 1–5 only; 171 examples and solutions preserved.')

def build(target):
    os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
    wrapper=(book.BOOK/'main.tex' if target=='main' else book.GENERATED/f'wrappers/volumes/{target}.tex' if target.startswith('volume') else book.GENERATED/f'wrappers/chapters/{target}.tex')
    book.compile_tex(wrapper,BASE/target)
    env=os.environ.copy()
    env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
    for n in (1,2):
        with (BASE/target/f'verify-pass-{n}.txt').open('w') as log:
            subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={BASE/target}',str(wrapper)],cwd=book.BOOK,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['xdvipdfmx','-q','-o',str(BASE/target/(wrapper.stem+'.pdf')),str(BASE/target/(wrapper.stem+'.xdv'))],cwd=book.BOOK,env=env,check=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--backup',action='store_true')
    p.add_argument('--regenerate',action='store_true')
    p.add_argument('--target',choices=['ch01','ch02','ch03','ch04','ch05','volume1','volume2','main'])
    a=p.parse_args()
    if a.backup: backup()
    if a.regenerate: regenerate()
    if a.target: build(a.target)
