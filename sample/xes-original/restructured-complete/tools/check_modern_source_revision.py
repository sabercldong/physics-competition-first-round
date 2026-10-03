"""Render internal PDFs and record structural checks without claiming content acceptance."""
import json, subprocess, hashlib
from pathlib import Path
import fitz
from PIL import Image, ImageDraw

BOOK=Path(__file__).resolve().parents[1]
BASE=BOOK/'build/modern-source-revision-20260923'
FILES={'ch31':BASE/'ch31/ch31.pdf','ch32':BASE/'ch32/ch32.pdf','A6':BASE/'A6/A6-standalone.pdf'}

def run():
    records={}
    for key,p in FILES.items():
        before=hashlib.sha256(p.read_bytes()).hexdigest()
        q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
        if q.returncode:
            raise RuntimeError(f'{key}: PDF is incomplete or invalid; do not render during compilation.\n{q.stdout}{q.stderr}')
        doc=fitz.open(p);out=BASE/'render'/key;out.mkdir(parents=True,exist_ok=True)
        if not len(doc):raise RuntimeError(f'{key}: zero-page PDF is not a valid inspection target')
        rows=[]
        for i,page in enumerate(doc):
            page.get_pixmap(dpi=180).save(out/f'page-{i+1:02d}.png')
            rows.append({'physical_page':i+1,'text_length':len(page.get_text()),'first_text':page.get_text()[:90]})
        for offset in range(0,len(doc),8):
            sheet=Image.new('RGB',(1000,1440),'#dddddd');draw=ImageDraw.Draw(sheet)
            for j in range(offset,min(offset+8,len(doc))):
                im=Image.open(out/f'page-{j+1:02d}.png');im.thumbnail((480,328))
                x=(j-offset)%2*500;y=(j-offset)//2*360
                sheet.paste(im,(x+(480-im.width)//2,y+25));draw.text((x+10,y+5),f'{key} / physical page {j+1}',fill='black')
            sheet.save(out/f'contact-{offset+1:02d}.jpg')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=before:
            raise RuntimeError(f'{key}: PDF changed during render; rerun after build completes')
        f=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True)
        records[key]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(doc),'page_text':rows,
            'qpdf_returncode':q.returncode,'qpdf':q.stdout+q.stderr,'pdffonts':f.stdout,'bookmarks':doc.get_toc(),
            'visual_acceptance':'pending_manual_review'}
    (BASE/'structural-checks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(json.dumps({k:{'pages':v['pages'],'qpdf':v['qpdf_returncode']} for k,v in records.items()}))

def check_figure_pages():
    # Upstream checker examines page 1 only. Split actual diagram pages first,
    # otherwise a clean title page would be a meaningless PASS.
    import os
    exe='/Users/dongxingxi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    checker='/Users/dongxingxi/.codex/skills/thesis-figure-skill/references/pdf-overlap-checker.py'
    env=os.environ.copy();env['PYTHONPATH']='/Users/dongxingxi/Library/Python/3.14/lib/python/site-packages'
    terms={'ch31':['地面标记左移','同一比例尺','质心系阈值末态'],
        'ch32':['发射极K','吸能电离'],
        'A6':['出纸面','圆截面右移','面积A']}
    out=BASE/'overlap';out.mkdir(exist_ok=True)
    for key,p in FILES.items():
        doc=fitz.open(p)
        for i,page in enumerate(doc):
            text=''.join(page.get_text().split())
            if not any(t in text for t in terms[key]):continue
            one=fitz.open();one.insert_pdf(doc,from_page=i,to_page=i);part=out/f'{key}-{i+1:02d}.pdf';one.save(part)
            result=subprocess.run([exe,checker,str(part),'--json'],env=env,capture_output=True,text=True)
            (out/f'{key}-{i+1:02d}.json').write_text(result.stdout)
            (out/f'{key}-{i+1:02d}.stderr.txt').write_text(result.stderr)
            print(key,i+1,result.returncode,result.stdout[-150:])

def check_cropped_figures():
    import os
    # Bounds verified visually against the current internal PDFs, in PDF points.
    specs=[('ch31',6,(205,50,390,232)),('ch31',8,(150,363,447,482)),
        ('ch31',12,(185,276,402,393)),('ch32',4,(165,48,410,171)),
        ('ch32',6,(162,216,433,344)),('A6',5,(180,538,410,688)),
        ('A6',7,(110,265,480,397)),('A6',25,(202,260,395,383))]
    exe='/Users/dongxingxi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    checker='/Users/dongxingxi/.codex/skills/thesis-figure-skill/references/pdf-overlap-checker.py'
    env=os.environ.copy();env['PYTHONPATH']='/Users/dongxingxi/Library/Python/3.14/lib/python/site-packages'
    out=BASE/'figure-checks';out.mkdir(exist_ok=True)
    for key,n,rect in specs:
        doc=fitz.open(FILES[key]);r=fitz.Rect(rect);one=fitz.open();page=one.new_page(width=r.width,height=r.height)
        page.show_pdf_page(page.rect,doc,n-1,clip=r)
        # Rendering honors this clip; PDF text extractors can still see invisible
        # content outside it. Their overlap results are leads, not a clean gate.
        part=out/f'{key}-{n:02d}.pdf';one.save(part)
        page.get_pixmap(dpi=300).save(out/f'{key}-{n:02d}.png')
        result=subprocess.run([exe,checker,str(part),'--json'],env=env,capture_output=True,text=True)
        (out/f'{key}-{n:02d}.json').write_text(result.stdout)
        print(key,n,result.returncode,result.stdout[-120:])

if __name__=='__main__':
    import sys
    if '--overlap' in sys.argv:check_figure_pages()
    elif '--figures' in sys.argv:check_cropped_figures()
    else:run()
