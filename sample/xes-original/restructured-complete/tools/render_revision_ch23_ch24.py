"""Review images from actual compiled pages; never changes book content."""
import fitz,json,re
from PIL import Image,ImageDraw
import build_review_ch23_ch24 as r
records=[]
for key in ('ch23','ch24'):
 d=fitz.open(r.BASE/key/f'{key}.pdf');out=r.BASE/'visual'/key;out.mkdir(parents=True,exist_ok=True)
 for i,p in enumerate(d):
  p.get_pixmap(dpi=160,alpha=False).save(out/f'page-{i+1:03}.png')
  blocks=p.get_text('blocks')
  caps=[]
  for b in blocks:
   for line in b[4].splitlines():
    if re.match(r'^图\s*2[34]\.\d+\s*[：:]',line):caps.append((b,line))
  for b,line in caps:
   number=re.search(r'2[34]\.\d+',line)[0]
   preceding=[x for x in blocks if x[3]<b[1] and re.search(r'图\s*'+re.escape(number)+r'\s*中',x[4])]
   top=max(45,preceding[-1][3]+2) if preceding else max(45,b[1]-370)
   # A short in-figure paragraph sometimes contains the same phrase. Include all artwork.
   if b[1]-top<80:top=max(45,b[1]-220)
   rect=fitz.Rect(45,top,550,min(p.rect.height-40,b[3]+4))
   p.get_pixmap(matrix=fitz.Matrix(3.6,3.6),clip=rect,alpha=False).save(out/f'fig-{number}.png')
   records.append({'chapter':key,'figure':number,'physical_page':i+1,'clip':list(rect),'file':str(out/f'fig-{number}.png')})
 for start in range(0,len(d),6):
  sheet=Image.new('RGB',(1500,2130),'#ddd');dr=ImageDraw.Draw(sheet)
  for j in range(min(6,len(d)-start)):
   im=Image.open(out/f'page-{start+j+1:03}.png');im.thumbnail((490,680));x=500*(j%3)+5;y=710*(j//3)+25
   sheet.paste(im,(x,y));dr.text((x,y-20),f'{key} PDF {start+j+1}',fill='black')
  sheet.save(out/f'contact-{start//6+1}.jpg')
(r.BASE/'visual/figures.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('Rendered figures:',len(records))
