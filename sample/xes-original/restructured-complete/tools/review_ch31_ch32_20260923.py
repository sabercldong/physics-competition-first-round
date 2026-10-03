"""Read-only content review: render delivered PDFs and bounded source pages."""
import hashlib,json,re,subprocess
from pathlib import Path
import fitz
from PIL import Image,ImageDraw

BOOK=Path(__file__).resolve().parents[1]
ROOT=BOOK.parents[2]
OUT=BOOK/'build/review-ch31-ch32-20260923'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def contacts(files,out):
 for start in range(0,len(files),6):
  part=files[start:start+6]; sheet=Image.new('RGB',(1380,660*((len(part)+2)//3)),'#ddd');draw=ImageDraw.Draw(sheet)
  for j,p in enumerate(part):
   im=Image.open(p);im.thumbnail((445,630));x=j%3*460;y=j//3*660
   sheet.paste(im,(x+5,y+23));draw.text((x+5,y+5),p.name,fill='black')
  sheet.save(out/f'contact-{start//6+1}.jpg',quality=92)
result={'pdfs':{},'figures':[]}
for n in (31,32):
 p=next((ROOT/'output/pdf').glob(f'*第{n}章*'));d=fitz.open(p);out=OUT/f'ch{n}';out.mkdir(exist_ok=True)
 texts=[];files=[]
 for i,pg in enumerate(d):
  dst=out/f'page-{i+1:03}.png';pg.get_pixmap(dpi=160).save(dst);files.append(dst)
  texts.append(f'\n--- PHYSICAL PAGE {i+1} ---\n'+pg.get_text())
  for b in pg.get_text('blocks'):
   m=re.match(rf'图\s*({n}\.\d+)\s*[：:]',b[4])
   if not m:continue
   rect=fitz.Rect(40,max(40,b[1]-350),555,min(pg.rect.height-40,b[3]+6))
   f=out/f'fig-{m[1]}.png';pg.get_pixmap(matrix=fitz.Matrix(3.4,3.4),clip=rect).save(f)
   result['figures'].append({'number':m[1],'page':i+1,'path':str(f)})
 (out/'text.txt').write_text(''.join(texts));contacts(files,out)
 q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
 fonts=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True)
 (out/'qpdf.txt').write_text(q.stdout+q.stderr);(out/'fonts.txt').write_text(fonts.stdout)
 result['pdfs'][str(n)]={'path':str(p),'sha256':sha(p),'pages':len(d),'bookmarks':d.get_toc(),'qpdf':q.returncode,'replacement_chars':''.join(texts).count('\ufffd')}
source=Path('/Users/dongxingxi/Downloads/学而思资料/二轮/兴趣二阶春季.pdf')
d=fitz.open(source);out=OUT/'source';out.mkdir(exist_ok=True);files=[]
for n in [114,115,116,117,118,119,120,121,141,142,143,144,145,146,147]:
 p=out/f'page-{n:03}.png';d[n-1].get_pixmap(dpi=180).save(p);files.append(p)
contacts(files,out)
result['source']={'path':str(source),'sha256':sha(source),'rendered_pages':[int(p.stem.split('-')[1]) for p in files]}
(OUT/'inspection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
