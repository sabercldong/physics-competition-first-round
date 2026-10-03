"""Internal build for teaching-depth improvements; publication is a separate step."""
import argparse, hashlib, json, os, re, shutil, subprocess
from pathlib import Path
import fitz
import build_review_ch15_ch16 as common
book=common.book
BASE=book.BOOK/'build/mechanics-teaching-20260927'
ARCHIVE=book.PROJECT/'archive/20260927-mechanics-before-teaching-expansion'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def backup():
    if (ARCHIVE/'manifest.json').exists(): return
    ARCHIVE.mkdir(parents=True,exist_ok=True)
    records={}
    for p in common.FORMAL.glob('*.pdf'):
        records[p.name]={'sha256':sha(p),'pages':len(fitz.open(p))}
        if p.name in names().values():
            dest=ARCHIVE/'pdf'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
    shutil.copytree(book.BOOK,ARCHIVE/'source',ignore=shutil.ignore_patterns('build','__pycache__','.git'),dirs_exist_ok=True)
    (ARCHIVE/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
def names():
    return {**{f'ch{n:02}':f'高中物理竞赛一轮讲义_第{n:02}章_{book.CHAPTERS[n]["title"]}.pdf' for n in range(5,14)},'volume2':'高中物理竞赛一轮讲义_第2卷_力学.pdf','main':'高中物理竞赛一轮讲义.pdf'}
def stage():
    (BASE/'staged').mkdir(parents=True,exist_ok=True)
    report={}
    for n in range(5,14):
        key=f'ch{n:02}';body,maps=common.chapter_text(n)
        old=(ARCHIVE/f'source/generated/chapters/{key}.tex').read_text()
        oldlabels=set(re.findall(r'\\label\{([^}]+)\}',old))
        newlabels=set(re.findall(r'\\label\{([^}]+)\}',body))
        assert not oldlabels-newlabels,(key,oldlabels-newlabels)
        oldq=old.count(r'\begin{origexamplebox}');newq=body.count(r'\begin{origexamplebox}')
        assert newq>=oldq and newq==body.count(r'\begin{xesolution}'),key
        # Compare every existing diagram block byte-for-byte, independent of order.
        pattern=r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}'
        oldfig=re.findall(pattern,old,re.S);newfig=re.findall(pattern,body,re.S)
        assert all(newfig.count(f)>=oldfig.count(f) for f in set(oldfig)),key
        (BASE/f'staged/{key}-body.tex').write_text(body)
        wrapper=book._wrapper(f'第{n}章　{book.CHAPTERS[n]["title"]}',[n],toc=False)
        wrapper=wrapper.replace(f'generated/chapters/{key}.tex',str(BASE/f'staged/{key}-body.tex'))
        (BASE/f'staged/{key}.tex').write_text(wrapper)
        report[key]={'old_questions':oldq,'questions':newq,'retained_labels':len(oldlabels),'retained_tikz_blocks':len(oldfig)}
    for key,p in [('volume2',book.GENERATED/'wrappers/volumes/volume2.tex'),('main',book.BOOK/'main.tex')]:
        text=p.read_text()
        for n in range(5,14):text=text.replace(f'generated/chapters/ch{n:02}.tex',str(BASE/f'staged/ch{n:02}-body.tex'))
        (BASE/f'staged/{key}.tex').write_text(text)
    (BASE/'retention.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))
def build(key):
    out=BASE/key;out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','');env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
    for i in range(1,4):
        with (out/f'pass-{i}.txt').open('w') as f:
            subprocess.run(['/Library/TeX/texbin/xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error',f'-output-directory={out}',str(BASE/f'staged/{key}.tex')],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['/Library/TeX/texbin/xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{key}.xdv')],cwd=book.BOOK,env=env,check=True)
    print(key,len(fitz.open(out/f'{key}.pdf')))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--stage',action='store_true');p.add_argument('--target');a=p.parse_args()
    if a.backup:backup()
    if a.stage:stage()
    if a.target:build(a.target)
