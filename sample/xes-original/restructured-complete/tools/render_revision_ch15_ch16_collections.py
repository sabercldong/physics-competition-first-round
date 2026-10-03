"""Render collection front matter and revised-chapter boundaries."""
import json
import fitz
from PIL import Image,ImageDraw
from check_revision_ch15_ch16 import BASE,TITLES,span,sha
records={}
for key in ('volume3','main'):
 p=BASE/key/f'{key}.pdf';d=fitz.open(p);out=BASE/'collection-render'/key;out.mkdir(parents=True,exist_ok=True)
 first=next(r[2] for r in d.get_toc() if r[0]==1)-1
 selected=set(range(first))
 for ch in TITLES:
  a,b=span(d,TITLES[ch]);selected.update(i for i in [a-1,a,b-1,b] if 0<=i<len(d))
 pages=sorted(selected)
 for i in pages:d[i].get_pixmap(dpi=220,alpha=False).save(out/f'page-{i+1:03}.png')
 for start in range(0,len(pages),6):
  canvas=Image.new('RGB',(1320,1300),'#ddd');dr=ImageDraw.Draw(canvas)
  for j,i in enumerate(pages[start:start+6]):
   im=Image.open(out/f'page-{i+1:03}.png');im.thumbnail((430,610))
   x=440*(j%3)+5;y=650*(j//3)+25;canvas.paste(im,(x,y));dr.text((x,y-20),str(i+1),fill='black')
  canvas.save(out/f'contact-{start//6+1:02}.png')
 records[key]={'pdf_sha256':sha(p),'physical_pages_rendered':[i+1 for i in pages],'directory':str(out)}
(BASE/'collection-render/manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps(records,ensure_ascii=False,indent=2))
