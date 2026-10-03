"""Figure-detail crops from the current internal PDFs, with hash binding."""
import json,re,hashlib
from pathlib import Path
import fitz
BOOK=Path(__file__).resolve().parent.parent
BASE=BOOK/'build/revision-ch13-ch14-20260912'
out=BASE/'details';out.mkdir(exist_ok=True)
records=[]
for ch in ['ch13','ch14']:
 p=BASE/ch/f'{ch}.pdf';d=fitz.open(p)
 for i,pg in enumerate(d):
  captions=[]
  for b in pg.get_text('dict')['blocks']:
   for ln in b.get('lines',[]):
    t=''.join(s['text'] for s in ln['spans'])
    m=re.match(r'^图\s*('+ch[2:]+r'\.\d+)：',t)
    if m:captions.append((m[1],ln['bbox'][1],ln['bbox'][3]))
  previous=52.
  for num,y0,y1 in captions:
   rects=[]
   for item in pg.get_drawings():
    r=item['rect']
    if r.y0<previous or r.y1>y0+1 or (r.width>450 and r.height>20):continue
    if r.width>470 and r.height<1:continue
    rects.append(r)
   for img in pg.get_image_info():
    r=fitz.Rect(img['bbox'])
    if r.y0>=previous and r.y1<=y0+1:rects.append(r)
   top=min((r.y0 for r in rects),default=y0-160)
   clip=fitz.Rect(45,max(previous,top-26),552,min(780,y1+25))
   dest=out/f'{ch}-fig-{num.split(".")[1]:0>2}.png'
   pg.get_pixmap(dpi=330,clip=clip,alpha=False).save(dest)
   records.append(dict(chapter=ch,figure=num,page=i+1,path=str(dest),clip=list(clip),pdf_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
   previous=y1+10
(BASE/'detail-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(len(records),'figure groups rendered')
