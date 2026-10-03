"""Render candidate pages and each captioned figure; no formal-file writes."""
from pathlib import Path
import re,json,hashlib
import fitz
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parents[1]
BASE=BOOK/'build/review-ch09-20260909'
OUT=BASE/'candidate-render'; OUT.mkdir(exist_ok=True)
doc=fitz.open(BASE/'ch09/ch09.pdf')
records=[]
for i,p in enumerate(doc):
    p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(OUT/f'page-{i+1:02}.png')
    caps=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            s=''.join(x['text'] for x in l['spans'])
            m=re.match(r'^图\s*9\.(\d+)：',s)
            if m and max(x['size'] for x in l['spans'])<11:
                caps.append((int(m[1]),fitz.Rect(l['bbox'])))
    for n,cap in caps:
        # All new diagrams are kept with their captions. Full upper page avoids
        # falsely clipping long vector labels; crop refinement is optional.
        prev=max([r.y1+5 for k,r in caps if r.y1<cap.y0]+[49])
        heights=[0,125,105,230,225,290,285,210,120,190,215,140,120,150,230,190,180,205,170,185,185,140,150,175,180,210,150,200,190,210]
        prev=max(prev,cap.y0-heights[n])
        clip=fitz.Rect(36,prev,p.rect.width-27,cap.y1+10)
        p.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,alpha=False).save(OUT/f'figure-{n:02}.png')
        records.append({'number':n,'page':i+1,'clip':list(clip)})
for start in range(0,len(doc),9):
    canvas=Image.new('RGB',(960,1425),'#ccc'); draw=ImageDraw.Draw(canvas)
    for j in range(start,min(start+9,len(doc))):
        im=Image.open(OUT/f'page-{j+1:02}.png');im.thumbnail((310,438))
        x=((j-start)%3)*320;y=((j-start)//3)*475
        canvas.paste(im,(x,y+24));draw.text((x+8,y+5),str(j+1),fill='black')
    canvas.save(OUT/f'contact-{start+1:02}.png')
assert sorted(r['number'] for r in records)==list(range(1,30)),records
(BASE/'candidate-figures.json').write_text(json.dumps(records,indent=2))
print('Pages:',len(doc),'figures:',[(r['number'],r['page']) for r in records])
