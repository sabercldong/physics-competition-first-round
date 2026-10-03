"""Crop every numbered figure for inspection, using vector bounds and captions."""
from pathlib import Path
import re,json
import fitz
BASE=Path(__file__).resolve().parents[1]/'build/review-ch08-20260909'
d=fitz.open(BASE/'ch08/ch08.pdf'); out=BASE/'visual'; records=[]
for i,p in enumerate(d):
    captions=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            s=''.join(x['text'] for x in l['spans'])
            m=re.match(r'^图\s*8\.(\d+)(?:\s|$)',s)
            if m and max(x['size'] for x in l['spans'])<9:
                captions.append((int(m[1]),fitz.Rect(l['bbox'])))
    bands=[]
    for dr in p.get_drawings():
        r=dr['rect']
        if r.width>p.rect.width*.76 or r.y0<48 or r.height>360: continue
        if r.width<.5 and r.height<.5: continue
        bands.append(r)
    groups=[]
    for r in sorted(bands,key=lambda r:r.y0):
        if groups and r.y0<groups[-1].y1+14: groups[-1]|=r
        else: groups.append(fitz.Rect(r))
    for n,cap in captions:
        eligible=[r for r in groups if r.y1<cap.y1 and cap.y0-r.y1<50]
        if not eligible: raise RuntimeError((i+1,n,cap,groups))
        r=eligible[-1]
        y0=max(48,r.y0-30)
        if n in [7,9,10,11,17]: y0=max(48,cap.y0-(250 if n==17 else 190))
        clip=fitz.Rect(38,y0,p.rect.width-30,cap.y1+12)
        name=f'numbered-{n:02}.png'
        p.get_pixmap(matrix=fitz.Matrix(3.3,3.3),clip=clip).save(out/name)
        records.append({'number':n,'page':i+1,'path':name,'clip':list(clip)})
assert sorted(x['number'] for x in records)==list(range(1,28)),records
(BASE/'numbered-figures.json').write_text(json.dumps(records,indent=2))
print([(r['number'],r['page']) for r in records])
