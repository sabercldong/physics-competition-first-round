"""Scoped thermal-volume review; never publishes implicitly."""
import argparse, hashlib, json, os, shutil, subprocess, re
from pathlib import Path
import fitz
from PIL import Image, ImageDraw
import build_review_ch15_ch16 as common
book = common.book
BASE = book.BOOK/'build/revision-volume3-20260927'
ARCHIVE = book.PROJECT/'archive/20260927-volume3-before-revision'
NAMES = {f'ch{n}':f'高中物理竞赛一轮讲义_第{n}章_{book.CHAPTERS[n]["title"]}.pdf' for n in range(14,19)}
NAMES.update(volume3='高中物理竞赛一轮讲义_第3卷_热学与统计物理.pdf', main='高中物理竞赛一轮讲义.pdf')
HEAT = Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020寒】兴趣一阶-热学.pdf')
STATS = Path('/Users/dongxingxi/Downloads/学而思资料/二轮/兴趣二阶寒假班.pdf')

def backup():
    BASE.mkdir(parents=True, exist_ok=True)
    if (ARCHIVE/'manifest.json').exists():
        return
    (ARCHIVE/'pdf').mkdir(parents=True,exist_ok=True)
    records = {}
    for key,name in NAMES.items():
        p=common.FORMAL/name
        shutil.copy2(p,ARCHIVE/'pdf'/name)
        records[key]={'path':str(p),'sha256':common.sha(p),'pages':len(fitz.open(p))}
        if key.startswith('ch'):
            target=BASE/'baseline'/key
            target.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,target/f'{key}.pdf')
    for root in [book.BOOK]+[book.LEGACY/name for name in ['twenty-eighth-section','twenty-ninth-section','thirtieth-section','thirty-first-section']]:
        shutil.copytree(root,ARCHIVE/'source'/root.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('build','__pycache__','.git','.venv*'))
    protected={str(p):common.sha(p) for p in (book.GENERATED/'chapters').glob('*.tex') if p.stem not in NAMES}
    (ARCHIVE/'manifest.json').write_text(json.dumps({'formal':records,'other_chapters_at_start':protected},ensure_ascii=False,indent=2))

def render_pdf(pdf, dest, key, pages=None):
    dest.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(pdf); pages=list(pages or range(1,len(doc)+1)); rows=[]
    expected={f'{key}-p{n:03}.png' for n in pages}
    for stale in dest.glob(f'{key}-p[0-9][0-9][0-9].png'):
        if stale.name not in expected:
            archive=dest/'obsolete';archive.mkdir(exist_ok=True)
            shutil.move(str(stale),archive/f'{common.sha(stale)[:8]}-{stale.name}')
    for n in pages:
        page=doc[n-1]; path=dest/f'{key}-p{n:03}.png'
        page.get_pixmap(dpi=160,alpha=False).save(path)
        rows.append({'page':n,'image':str(path),'text':page.get_text()})
    for start in range(0,len(pages),8):
        sheet=Image.new('RGB',(1600,1180),'#dddddd'); draw=ImageDraw.Draw(sheet)
        for j,n in enumerate(pages[start:start+8]):
            im=Image.open(dest/f'{key}-p{n:03}.png');im.thumbnail((386,552))
            x=j%4*400+7;y=j//4*590+25
            sheet.paste(im,(x,y));draw.text((x,y-20),f'{key} page {n}',fill='black')
        sheet.save(dest/f'{key}-overview-{pages[start]:03}.jpg',quality=92)
    (dest/f'{key}-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))

def regenerate():
    before={p:common.sha(p) for p in (book.GENERATED/'chapters').glob('*.tex') if p.stem not in NAMES}
    mapping=json.loads((book.GENERATED/'source-map.json').read_text())
    for n,count in [(14,11),(15,11),(16,5),(17,6),(18,7)]:
        body,maps=common.chapter_text(n)
        assert body.count(r'\begin{origexamplebox}')==body.count(r'\begin{xesolution}')==count
        (book.GENERATED/f'chapters/ch{n}.tex').write_text(body)
        next(c for c in mapping['chapters'] if c['chapter']==n)['source_number_maps']=maps
    (book.GENERATED/'source-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
    assert all(common.sha(p)==h for p,h in before.items())

def structured_body(n):
    return common.chapter_text(n)

def stage():
    folder=BASE/'staged';folder.mkdir(parents=True,exist_ok=True)
    for n in range(14,19):
        body,maps=structured_body(n)
        (folder/f'ch{n}-body.tex').write_text(body)
        wrapper=book._wrapper(f'第{n}章　{book.CHAPTERS[n]["title"]}',[n],toc=False)
        wrapper=wrapper.replace(f'generated/chapters/ch{n}.tex',str(folder/f'ch{n}-body.tex'))
        (folder/f'ch{n}.tex').write_text(wrapper)

def compile_target(key, passes=3):
    wrapper=book.BOOK/'main.tex' if key=='main' else book.GENERATED/f'wrappers/{"volumes" if key=="volume3" else "chapters"}/{key}.tex'
    out=BASE/key;out.mkdir(parents=True,exist_ok=True)
    if key.startswith('ch'):
        wrapper=BASE/'staged'/f'{key}.tex'
    env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','')
    env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
    inputs=list((BASE/'staged').glob('*.tex')) if key.startswith('ch') else list((book.GENERATED/'chapters').glob('*.tex'))
    inputs += [wrapper, book.BOOK/'style.tex']
    before={str(p):common.sha(p) for p in inputs}
    for n in range(1,passes+1):
        with (out/f'pass-{n}.txt').open('w') as log:
            subprocess.run(['/Library/TeX/texbin/xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['/Library/TeX/texbin/xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{key}.xdv')],cwd=book.BOOK,env=env,check=True)
    assert all(common.sha(Path(p))==h for p,h in before.items()), 'Inputs changed during build'
    (out/'frozen-build.json').write_text(json.dumps({'chapter_hashes':before,'passes':passes,'pdf_sha256':common.sha(out/f'{key}.pdf')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--baseline',action='store_true');p.add_argument('--sources',action='store_true');p.add_argument('--regenerate',action='store_true');p.add_argument('--stage',action='store_true');p.add_argument('--target',choices=NAMES);p.add_argument('--render',action='store_true');a=p.parse_args()
    if a.backup:backup()
    if a.baseline:
        for n in range(14,19):render_pdf(BASE/f'baseline/ch{n}/ch{n}.pdf',BASE/'baseline/visual',f'ch{n}')
    if a.sources:
        render_pdf(HEAT,BASE/'sources','heat',range(5,52))
        render_pdf(STATS,BASE/'sources','stats',range(68,77))
    if a.regenerate:regenerate()
    if a.stage:stage()
    if a.target:compile_target(a.target)
    if a.render:
        for n in range(14,19):render_pdf(BASE/f'ch{n}/ch{n}.pdf',BASE/'visual',f'ch{n}')
