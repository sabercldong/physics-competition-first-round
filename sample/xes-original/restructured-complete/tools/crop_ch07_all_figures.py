"""Crop every newly numbered teaching figure for manual visual verification."""
from pathlib import Path
import fitz,re,json
B=Path(__file__).resolve().parent.parent/'build/review-ch07-20260908'
d=fitz.open(B/'ch07/ch07.pdf'); out=B/'visual'; records=[]
for i,p in enumerate(d):
    bands=[]
    for v in p.get_drawings():
        r=v['rect']
        if r.width>p.rect.width*.8 or r.y0<48 or r.height>400: continue
        if r.width<.7 and r.height<.7: continue
        bands.append(r)
    clusters=[]
    for r in sorted(bands,key=lambda r:r.y0):
        if clusters and r.y0<clusters[-1].y1+35: clusters[-1]|=r
        else: clusters.append(fitz.Rect(r))
    for block in p.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            text=''.join(s['text'] for s in line['spans'])
            match=re.match(r'^图\s*7\.(\d+)(?:\s|$)',text.strip())
            if not match or max(s['size'] for s in line['spans'])>8.5: continue
            cap=fitz.Rect(line['bbox'])
            candidates=[r for r in clusters if r.y1<=cap.y0+3 and cap.y0-r.y1<85]
            assert candidates,(i+1,text)
            r=max(candidates,key=lambda r:r.y1)
            clip=fitz.Rect(34,max(48,r.y0-48),562,min(790,cap.y1+28))
            fn=f'all-{int(match[1]):02}-p{i+1:02}.png'
            p.get_pixmap(matrix=fitz.Matrix(3.5,3.5),clip=clip).save(out/fn)
            records.append({'figure':int(match[1]),'page':i+1,'caption':text,'path':fn,'rect':list(clip)})
assert sorted(r['figure'] for r in records)==list(range(1,55)),records
(B/'all-figure-crops.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('54 numbered figure crops saved.')
