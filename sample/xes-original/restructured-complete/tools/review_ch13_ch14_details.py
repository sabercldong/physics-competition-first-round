"""Render clipped details from audited originals and current delivery PDFs."""
from pathlib import Path
import json
import fitz
BASE=Path(__file__).resolve().parent.parent/'build/review-ch13-ch14-20260912'
meta=json.loads((BASE/'manifest.json').read_text());out=BASE/'details';out.mkdir(exist_ok=True)
rects={
 'ch13':[(2,430,525),(3,63,158),(3,345,418),(4,150,282),(9,520,637),(10,610,755),(11,526,662),(12,326,505),(13,154,276),(14,58,194)],
 'ch14':[(2,450,784),(3,375,587),(4,480,648),(4,664,788),(5,281,402),(6,648,790),(7,65,226),(9,229,441),(9,447,647),(10,66,268),(10,297,415),(11,342,486),(11,494,631),(13,277,389),(14,207,316),(15,59,273),(16,70,292),(16,651,787),(17,108,252),(17,645,782),(18,75,263),(18,624,788),(19,59,73),(19,136,322),(20,163,326),(21,174,292),(22,396,559)],
 'thermal':[(6,20,80),(7,15,120),(8,385,465),(10,233,390),(11,28,185),(12,30,136),(15,389,496),(16,36,142)],
}
items=[]
for key,rs in rects.items():
 d=fitz.open(meta['files'][key]['path'])
 for j,(pn,y0,y1) in enumerate(rs,1):
  pg=d[pn-1]
  # Teaching PDF is A4; original scanned thermal pages use another media box.
  if key=='thermal':
   continue
  r=fitz.Rect(45,y0,551,y1);p=out/f'{key}-{j:02}-p{pn:02}.png'
  pg.get_pixmap(dpi=330,clip=r,alpha=False).save(p)
  items.append({'id':f'{key}-{j:02}','physical_page':pn,'clip':list(r),'path':str(p)})
(BASE/'detail-manifest.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print(len(items),'detail crops rendered')
