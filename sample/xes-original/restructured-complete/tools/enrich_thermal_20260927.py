"""Thermal teaching expansion: stage privately, publish only after review."""
import argparse,json,shutil,re,hashlib,os,subprocess
from pathlib import Path
from collections import Counter
import fitz
import build_review_ch15_ch16 as common
book=common.book
BASE=book.BOOK/'build/thermal-teaching-20260927'
ARCHIVE=book.PROJECT/'archive/20260927-thermal-before-teaching-expansion'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names():return {**{f'ch{n}':f'高中物理竞赛一轮讲义_第{n}章_{book.CHAPTERS[n]["title"]}.pdf' for n in range(14,19)},'volume3':'高中物理竞赛一轮讲义_第3卷_热学与统计物理.pdf','main':'高中物理竞赛一轮讲义.pdf'}
def backup():
    BASE.mkdir(parents=True,exist_ok=True)
    if (ARCHIVE/'manifest.json').exists():return
    (ARCHIVE/'pdf').mkdir(parents=True,exist_ok=True)
    records={p.name:{'sha256':sha(p),'pages':len(fitz.open(p))} for p in common.FORMAL.glob('*.pdf')}
    for name in names().values():shutil.copy2(common.FORMAL/name,ARCHIVE/'pdf'/name)
    shutil.copytree(book.BOOK,ARCHIVE/'source',ignore=shutil.ignore_patterns('build','__pycache__','.git'),dirs_exist_ok=True)
    (ARCHIVE/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
def stage():
    folder=BASE/'staged';folder.mkdir(parents=True,exist_ok=True);rows={}
    for n in range(14,19):
        k=f'ch{n}';text,_=common.chapter_text(n);old=(ARCHIVE/f'source/generated/chapters/{k}.tex').read_text()
        row={}
        for env in ['origexamplebox','xesolution','tikzpicture']:
            pattern=r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}'
            a=Counter(re.findall(pattern,old,re.S));b=Counter(re.findall(pattern,text,re.S))
            assert not a-b,(k,env)
            row[env]={'old':sum(a.values()),'new':sum(b.values()),'missing':0}
        assert set(re.findall(r'\\label\{([^}]+)\}',old))<=set(re.findall(r'\\label\{([^}]+)\}',text))
        assert row['origexamplebox']['new']==row['xesolution']['new']
        (folder/f'{k}-body.tex').write_text(text)
        wrapper=book._wrapper(f'第{n}章　{book.CHAPTERS[n]["title"]}',[n],toc=False)
        (folder/f'{k}.tex').write_text(wrapper.replace(f'generated/chapters/{k}.tex',str(folder/f'{k}-body.tex')))
        rows[k]=row
    for key,p in [('volume3',book.GENERATED/'wrappers/volumes/volume3.tex'),('main',book.BOOK/'main.tex')]:
        text=p.read_text()
        for n in range(14,19):text=text.replace(f'generated/chapters/ch{n}.tex',str(folder/f'ch{n}-body.tex'))
        (folder/f'{key}.tex').write_text(text)
    (BASE/'retention.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(rows,flush=True)
def freeze_main():
    assert not (BASE/'frozen-shared.json').exists(), 'Shared baseline already frozen; inspect before replacing it'
    if (BASE/'main-build-shared-inputs.json').exists():
        previous=json.loads((BASE/'main-build-shared-inputs.json').read_text())
        em={f'ch{n}.tex' for n in range(19,27)}
        for path,digest in previous.items():
            p=Path(path)
            if p.name not in em:
                assert sha(p)==digest,('Non-EM shared source changed during private build',path)
        for n in range(19,27):
            assert sha(book.GENERATED/f'chapters/ch{n}.tex')==sha(book.BOOK/f'build/revision-em-20260927/staged/ch{n}-body.tex'),('Published EM differs from frozen private input',n)
    dest=ARCHIVE/'latest-shared-before-publication';dest.mkdir(exist_ok=True)
    shutil.copy2(common.FORMAL/names()['main'],dest/'main.pdf')
    shutil.copytree(book.BOOK,dest/'source',ignore=shutil.ignore_patterns('build','__pycache__','.git'),dirs_exist_ok=True)
    files=list((book.GENERATED/'chapters').glob('*.tex'))+[book.BOOK/'style.tex',book.BOOK/'main.tex']
    (BASE/'frozen-shared.json').write_text(json.dumps({str(p):sha(p) for p in files},indent=2))
    (BASE/'publication-baseline.json').write_text(json.dumps({p.name:sha(p) for p in common.FORMAL.glob('*.pdf')},ensure_ascii=False,indent=2))
def build(k):
    out=BASE/k;out.mkdir(exist_ok=True);wrapper=BASE/f'staged/{k}.tex'
    env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','');env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
    dependencies=[wrapper]+[BASE/f'staged/ch{n}-body.tex' for n in range(14,19) if k in {'main','volume3',f'ch{n}'}]
    if k=='main':
        dependencies += [book.BOOK/f'build/revision-em-20260927/staged/ch{n}-body.tex' for n in range(19,27)]
    before={str(p):sha(p) for p in dependencies}
    for i in range(1,4):
        with (out/f'pass-{i}.txt').open('w') as f:subprocess.run(['/Library/TeX/texbin/xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['/Library/TeX/texbin/xdvipdfmx','-q','-o',str(out/f'{k}.pdf'),str(out/f'{k}.xdv')],cwd=book.BOOK,env=env,check=True)
    assert all(sha(Path(p))==h for p,h in before.items())
    (out/'build-inputs.json').write_text(json.dumps(before,indent=2));print(k,len(fitz.open(out/f'{k}.pdf')),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--stage',action='store_true');p.add_argument('--freeze-main',action='store_true');p.add_argument('--target');a=p.parse_args()
    if a.backup:backup()
    if a.stage:stage()
    if a.freeze_main:freeze_main()
    if a.target:build(a.target)
