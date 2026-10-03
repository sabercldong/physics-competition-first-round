"""Read-only source/PDF audit; writes derived evidence, never teaching files."""
from pathlib import Path
import fitz,json,hashlib,re,subprocess
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
BASE=BOOK/'build/review-ch17-ch18-20260919';BASE.mkdir(parents=True,exist_ok=True)
files={ch:next((ROOT/'output/pdf').glob(f'*第{ch[2:]}章*')) for ch in ['ch17','ch18']}
files['source17']=Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020寒】兴趣一阶-热学.pdf')
records={}
for key,p in files.items():
 d=fitz.open(p);out=BASE/key;out.mkdir(exist_ok=True)
 ids=list(range(40,54)) if key=='source17' else list(range(len(d)))
 for i in ids:
  d[i].get_pixmap(dpi=180,alpha=False).save(out/f'page-{i+1:03}.png')
  (out/f'page-{i+1:03}.txt').write_text(d[i].get_text())
 for start in range(0,len(ids),4):
  canvas=Image.new('RGB',(1500,2040),'#ddd');dr=ImageDraw.Draw(canvas)
  for j,i in enumerate(ids[start:start+4]):
   im=Image.open(out/f'page-{i+1:03}.png');im.thumbnail((740,980));x=750*(j%2);y=1020*(j//2)+25
   canvas.paste(im,(x,y));dr.text((x+5,y-20),str(i+1),fill='black')
  canvas.save(out/f'contact-{start//4+1:02}.png')
 records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(d),'rendered_physical_pages':[i+1 for i in ids],'toc':d.get_toc()}
 if key.startswith('ch'):
  for name,cmd in [('qpdf',['qpdf','--check',str(p)]),('fonts',['pdffonts',str(p)])]:
   r=subprocess.run(cmd,capture_output=True,text=True);(out/f'{name}.txt').write_text(r.stdout+r.stderr);records[key][name+'_returncode']=r.returncode
(BASE/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(BASE)
