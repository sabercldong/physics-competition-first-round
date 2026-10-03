"""Candidate crops for every caption, including diagrams below size thresholds."""
from pathlib import Path
import fitz,re,json
B=Path(__file__).resolve().parent.parent/'build/review-ch06-20260908'
d=fitz.open(B/'ch06/ch06.pdf'); out=B/'visual'; records=[]
for i,p in enumerate(d):
    bands=[]
    for v in p.get_drawings():
        r=v['rect']
        if r.width>p.rect.width*.76 or r.y0<48 or r.height>360: continue
        if r.width<.7 and r.height<.7: continue
        bands.append(r)
    clusters=[]
    for r in sorted(bands,key=lambda r:r.y0):
        if clusters and r.y0<clusters[-1].y1+55: clusters[-1]|=r
        else: clusters.append(fitz.Rect(r))
    for block in p.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            text=''.join(s['text'] for s in line['spans'])
            if not re.match(r'^(?:解图[：:]|图\s*6\.\d+[：:])',text.strip()): continue
            cap=fitz.Rect(line['bbox'])
            candidates=[r for r in clusters if r.y1<=cap.y0+3 and cap.y0-r.y1<65]
            assert candidates,(i+1,text)
            r=max(candidates,key=lambda r:r.y1)
            clip=fitz.Rect(max(42,r.x0-62),max(48,r.y0-25),min(552,r.x1+90),min(780,cap.y1+8))
            fn=f'all-{len(records)+1:02}-p{i+1:02}.png'
            p.get_pixmap(matrix=fitz.Matrix(3.5,3.5),clip=clip).save(out/fn)
            records.append({'page':i+1,'caption':text,'path':fn,'rect':list(clip)})
assert len(records)==50,len(records)
(B/'all-figure-crops.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps(records,ensure_ascii=False,indent=2))
