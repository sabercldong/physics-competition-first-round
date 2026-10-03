#!/usr/bin/env python3
"""Render and record evidence for the narrow chapter-seven revision."""
from pathlib import Path
import re, json, hashlib, subprocess, math
import fitz
from PIL import Image, ImageDraw

BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK/'build/review-ch07-20260908'
PDF=ROOT/'ch07/ch07.pdf'
OUT=ROOT/'visual'
OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
d=fitz.open(PDF)
manifest={'pdf_sha256':sha(PDF),'pages':len(d),'toc':d.get_toc(),'examples':{},'figures':[]}
for n in range(1,37):
    manifest['examples'][str(n)]=[i+1 for i,p in enumerate(d) if re.search(rf'例\s*7\.{n}\b',p.get_text())]
for i,p in enumerate(d):
    p.get_pixmap(matrix=fitz.Matrix(2,2)).save(OUT/f'page-{i+1:02}.png')
    # Vector clusters are only candidates; all pages are also rendered to
    # catch small diagrams or text extending beyond a cluster's bounds.
    bands=[]
    for dr in p.get_drawings():
        r=dr['rect']
        if r.width>p.rect.width*.76 or r.y0<48 or r.height>360:
            continue
        if r.width<.7 and r.height<.7:
            continue
        bands.append(r)
    clusters=[]
    for r in sorted(bands,key=lambda r:r.y0):
        if clusters and r.y0<clusters[-1].y1+14:
            clusters[-1]|=r
        else:
            clusters.append(fitz.Rect(r))
    num=0
    for r in clusters:
        if r.width<90 or r.height<50:
            continue
        num+=1
        rect=fitz.Rect(max(36,r.x0-62),max(48,r.y0-28),min(p.rect.width-32,r.x1+82),min(p.rect.height-38,r.y1+36))
        name=f'fig-{i+1:02}-{num}.png'
        p.get_pixmap(matrix=fitz.Matrix(3.3,3.3),clip=rect).save(OUT/name)
        manifest['figures'].append({'page':i+1,'path':name,'rect':list(rect)})
for start in range(0,len(d),6):
    sheet=Image.new('RGB',(1500,1460),'white');draw=ImageDraw.Draw(sheet)
    for k,i in enumerate(range(start,min(start+6,len(d)))):
        im=Image.open(OUT/f'page-{i+1:02}.png');im.thumbnail((480,690))
        x,y=(k%3)*500,(k//3)*730
        sheet.paste(im,(x,y+28));draw.text((x+8,y+6),f'PDF {i+1}',fill='black')
    sheet.save(OUT/f'contact-{start+1:02}.jpg')
t=(BOOK/'generated/chapters/ch07.tex').read_text()
labels=re.findall(r'\\label\{([^}]+)\}',t)
refs=re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}',t)
manifest['duplicate_labels']=sorted({s for s in labels if labels.count(s)>1})
manifest['unknown_references']=sorted(set(refs)-set(labels))
manifest['example_envs']=t.count(r'\begin{origexamplebox}')
manifest['solution_envs']=t.count(r'\begin{xesolution}')
assert manifest['example_envs']==manifest['solution_envs']==36
assert all(manifest['examples'].values())
assert not manifest['duplicate_labels'] and not manifest['unknown_references']
protected=json.loads((ROOT/'protected-chapters.json').read_text())
assert all(sha(Path(p))==h for p,h in protected.items())
manifest['other_generated_chapters_unchanged']=len(protected)
manifest['tex_sha256']=sha(BOOK/'generated/chapters/ch07.tex')
for cmd,args in [('qpdf',['qpdf','--check',str(PDF)]),('pdffonts',['pdffonts',str(PDF)])]:
    r=subprocess.run(args,capture_output=True,text=True)
    (ROOT/f'{cmd}.txt').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(cmd,r.stderr)
(ROOT/'text.txt').write_text('\n\n'.join(f'=== PDF {i+1} ===\n'+p.get_text() for i,p in enumerate(d)))
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k not in ('figures','toc')},ensure_ascii=False,indent=2))
