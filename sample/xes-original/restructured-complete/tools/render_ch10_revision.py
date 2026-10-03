"""Render every candidate page and deterministic figure inspection crops."""
from pathlib import Path
import re,json,hashlib
import fitz
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parent.parent
BASE=BOOK/'build/review-ch10-20260909'
pdf=BASE/'ch10/ch10.pdf';doc=fitz.open(pdf)
out=BASE/'revised';out.mkdir(exist_ok=True)
figs=[]
for i,p in enumerate(doc):
    p.get_pixmap(dpi=240,alpha=False).save(out/f'page-{i+1:03}.png')
    caps=[]
    for b in p.get_text('blocks'):
        txt=re.sub(r'\s+','',b[4])
        m=re.search(r'图10\.(\d+)[：:]',txt)
        if m and (m.start()==0 or 16<=int(m[1])<=19):
            caps.append((int(m[1]),fitz.Rect(b[:4]),txt))
    drawings=[d['rect'] for d in p.get_drawings() if d['rect'].y0>54 and d['rect'].y1<780]
    drawings += [b['bbox'] for b in p.get_text('dict')['blocks'] if b['type']==1]
    for number,cap,txt in caps:
        low=max([r.y1 for _,r,_ in caps if r.y1<cap.y0] or [54])
        rs=sorted([fitz.Rect(r) for r in drawings if low<fitz.Rect(r).y0<cap.y0 and fitz.Rect(r).y1<=cap.y0+4],key=lambda r:r.y0)
        clusters=[]
        for r in rs:
            if not clusters or r.y0>clusters[-1].y1+40:clusters.append(fitz.Rect(r))
            else:clusters[-1]|=r
        top=max(low,clusters[-1].y0-35) if clusters else max(low,cap.y0-240)
        if 15<=number<=19 and clusters: top=max(low,clusters[0].y0-35)
        rect=fitz.Rect(42,top,552,min(790,cap.y1+4))
        p.get_pixmap(dpi=300,clip=rect,alpha=False).save(out/f'figure-10-{number:02}.png')
        figs.append({'number':number,'physical_page':i+1,'clip':list(rect),'caption':txt})
for start in range(0,len(doc),8):
    sheet=Image.new('RGB',(4*340,2*495),'#dddddd');dr=ImageDraw.Draw(sheet)
    for j in range(start,min(start+8,len(doc))):
        im=Image.open(out/f'page-{j+1:03}.png');im.thumbnail((330,465))
        x=(j-start)%4*340+5;y=(j-start)//4*495+20
        sheet.paste(im,(x,y));dr.text((x,y-16),str(j+1),fill='black')
    sheet.save(out/f'contact-{start//8+1}.png')
(out/'figures.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2))
(out/'text.txt').write_text('\n'.join(f'\n===PAGE {i+1}===\n'+p.get_text() for i,p in enumerate(doc)))
print(json.dumps({'pages':len(doc),'figures':len(figs),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}))
