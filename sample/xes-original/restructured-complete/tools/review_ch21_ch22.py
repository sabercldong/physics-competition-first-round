"""Read-only inspection of formal PDFs; writes review evidence, never book sources."""
import fitz,json,hashlib,re,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
OUT=BOOK/'build/review-ch21-ch22-20260920'
OUT.mkdir(parents=True,exist_ok=True)
paths={f'ch{n}':next((ROOT/'output/pdf').glob(f'*第{n}章_*.pdf')) for n in (21,22)}
paths['source']=Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020春】高一物理.pdf')
info={}
for key,p in paths.items():
 d=fitz.open(p);out=OUT/key;out.mkdir(exist_ok=True)
 pages=list(range(48,86)) if key=='source' else list(range(len(d)))
 rows=[]
 for i in pages:
  pg=d[i];pg.get_pixmap(dpi=160,alpha=False).save(out/f'page-{i+1:03}.png')
  (out/f'page-{i+1:03}.txt').write_text(pg.get_text())
  rows.append({'page':i+1,'text':pg.get_text()})
 for start in range(0,len(pages),4):
  im=Image.new('RGB',(1200,1740),'#ddd');draw=ImageDraw.Draw(im)
  for j,i in enumerate(pages[start:start+4]):
   a=Image.open(out/f'page-{i+1:03}.png');a.thumbnail((590,830));x=600*(j%2)+5;y=870*(j//2)+25
   im.paste(a,(x,y));draw.text((x,y-20),str(i+1),fill='black')
  im.save(out/f'contact-{start//4+1:02}.png')
 info[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(d),'review_pages':[i+1 for i in pages],'toc':d.get_toc()}
 if key!='source':
  for cmd in ['qpdf','pdffonts']:
   args=[cmd,'--check',str(p)] if cmd=='qpdf' else [cmd,str(p)]
   q=subprocess.run(args,capture_output=True,text=True);(out/(cmd+'.txt')).write_text(q.stdout+q.stderr)
   info[key][cmd+'_returncode']=q.returncode
  (out/'all-text.txt').write_text('\n'.join(f'\n---PDF {r["page"]}---\n'+r['text'] for r in rows))
  s=(BOOK/f'generated/chapters/{key}.tex').read_text()
  labels=re.findall(r'\\label\{([^}]+)\}',s)
  info[key].update(examples=s.count(r'\begin{origexamplebox}'),solutions=s.count(r'\begin{xesolution}'),figure_labels=[x for x in labels if ':fig:' in x],unreferenced_figures=[x for x in labels if ':fig:' in x and r'\ref{'+x+'}' not in s],duplicate_labels=[x for x in set(labels) if labels.count(x)>1])
(OUT/'manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
print(json.dumps(info,ensure_ascii=False,indent=2))
