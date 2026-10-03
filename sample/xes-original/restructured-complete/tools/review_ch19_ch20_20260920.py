"""Read-only audit: render current PDFs and source, preserve hashes."""
from pathlib import Path
import fitz,json,re,hashlib,subprocess
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2];BASE=BOOK/'build/review-ch19-ch20-20260920'
BASE.mkdir(parents=True,exist_ok=True)
files={f'ch{n}':next((ROOT/'output/pdf').glob(f'*第{n}章*')) for n in [19,20]}
files['source']=Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020春】高一物理.pdf')
records={}
for key,p in files.items():
 d=fitz.open(p);out=BASE/key;out.mkdir(exist_ok=True)
 ids=list(range(54)) if key=='source' else list(range(len(d)))
 captions=[]
 for i in ids:
  pg=d[i];pg.get_pixmap(dpi=160,alpha=False).save(out/f'page-{i+1:03}.png')
  (out/f'page-{i+1:03}.txt').write_text(pg.get_text())
  if key.startswith('ch'):
   for block in pg.get_text('dict')['blocks']:
    for ln in block.get('lines',[]):
     s=''.join(x['text'] for x in ln['spans'])
     if re.match(r'^图\s*\d+\.\d+[：:]',s):captions.append({'page':i+1,'text':s,'bbox':ln['bbox']})
 for start in range(0,len(ids),4):
  im=Image.new('RGB',(1500,2100),'#ddd');draw=ImageDraw.Draw(im)
  for j,i in enumerate(ids[start:start+4]):
   pg=Image.open(out/f'page-{i+1:03}.png');pg.thumbnail((740,1000));x=750*(j%2);y=1050*(j//2)+25
   im.paste(pg,(x,y));draw.text((x+8,y-20),str(i+1),fill='black')
  im.save(out/f'contact-{start//4+1:02}.png')
 records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(d),'rendered_pages':[i+1 for i in ids],'captions':captions,'toc':d.get_toc()}
 if key.startswith('ch'):
  for name,cmd in [('qpdf',['qpdf','--check',str(p)]),('fonts',['pdffonts',str(p)])]:
   r=subprocess.run(cmd,capture_output=True,text=True);(out/f'{name}.txt').write_text(r.stdout+r.stderr);records[key][name+'_returncode']=r.returncode
  src=(BOOK/f'generated/chapters/{key}.tex').read_text()
  records[key]['examples']=src.count(r'\begin{origexamplebox}')
  records[key]['answers']=src.count(r'\begin{xesolution}')
  labels=re.findall(r'\\label\{([^}]+)\}',src)
  records[key]['duplicate_labels']=sorted({x for x in labels if labels.count(x)>1})
  records[key]['unreferenced_figure_labels']=[x for x in labels if ':fig:' in x and r'\ref{'+x+'}' not in src]
  txt=''.join(pg.get_text() for pg in d)
  records[key]['text_flags']={x:txt.count(x) for x in ['@@BILINGUAL','□','�','重绘','原讲义','原扫描','标校']}
 (BASE/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 print(key,len(ids),'rendered pages',flush=True)
