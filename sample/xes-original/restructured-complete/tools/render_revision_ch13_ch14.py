"""Render every revised page and contact sheets; derived evidence only."""
from pathlib import Path
import fitz,json,re,hashlib
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parent.parent
BASE=BOOK/'build/revision-ch13-ch14-20260912'
for ch in ('ch13','ch14'):
 p=BASE/ch/f'{ch}.pdf';d=fitz.open(p);out=BASE/'render'/ch;out.mkdir(parents=True,exist_ok=True)
 captions=[]
 for i,pg in enumerate(d):
  pg.get_pixmap(dpi=220,alpha=False).save(out/f'page-{i+1:03}.png')
  (out/f'page-{i+1:03}.txt').write_text(pg.get_text())
  for block in pg.get_text('dict')['blocks']:
   if 'lines' not in block:continue
   for ln in block['lines']:
    txt=''.join(s['text'] for s in ln['spans'])
    if re.match(r'^图\s*'+ch[2:]+r'\.\d+：',txt):captions.append({'page':i+1,'text':txt,'bbox':ln['bbox']})
 for start in range(0,len(d),6):
  canvas=Image.new('RGB',(1320,1300),'#ddd');dr=ImageDraw.Draw(canvas)
  for j,i in enumerate(range(start,min(start+6,len(d)))):
   im=Image.open(out/f'page-{i+1:03}.png');im.thumbnail((430,610));x=440*(j%3)+5;y=650*(j//3)+25
   canvas.paste(im,(x,y));dr.text((x,y-20),str(i+1),fill='black')
  canvas.save(out/f'contact-{start//6+1:02}.png')
 (out/'manifest.json').write_text(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(d),'dpi':220,'captions':captions},ensure_ascii=False,indent=2))
 print(ch,len(d),'pages',len(captions),'captions')
