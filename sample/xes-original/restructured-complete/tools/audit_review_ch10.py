"""Read-only PDF/source evidence for the Chapter 10 review."""
from pathlib import Path
import hashlib, json, re, subprocess
import fitz
from PIL import Image, ImageDraw

BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
OUT=BOOK/'build/review-ch10-20260909'
OUT.mkdir(parents=True,exist_ok=True)
SOURCES=Path('/Users/dongxingxi/Downloads/学而思资料/二轮')
FILES={
 'current':(ROOT/'output/pdf/高中物理竞赛一轮讲义_第10章_简谐振动、阻尼、受迫振动和共振_含解答与解图.pdf',None),
 'source':(SOURCES/'2020秋季高二物理竞赛学生版讲义.pdf',list(range(73,99))),
 'exercises':(SOURCES/'2020秋季高二物理竞赛习题.pdf',list(range(36,40))),
}
manifest={}
for key,(path,selection) in FILES.items():
 doc=fitz.open(path);pages=selection or list(range(1,len(doc)+1))
 dest=OUT/key;dest.mkdir(exist_ok=True);texts=[]
 for n in pages:
  p=doc[n-1]
  p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(dest/f'page-{n:03}.png')
  texts.append(f'\n===== PHYSICAL PAGE {n} =====\n'+p.get_text())
 (dest/'text.txt').write_text('\n'.join(texts))
 for start in range(0,len(pages),6):
  batch=pages[start:start+6]
  sheet=Image.new('RGB',(1500,1470),'white');draw=ImageDraw.Draw(sheet)
  for j,n in enumerate(batch):
   im=Image.open(dest/f'page-{n:03}.png');im.thumbnail((490,690))
   x=(j%3)*500;y=(j//3)*735
   draw.text((x+8,y+5),f'{key} physical page {n}',fill='black')
   sheet.paste(im,(x+(500-im.width)//2,y+25))
  sheet.save(dest/f'contact-{batch[0]:03}.jpg',quality=92)
 manifest[key]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'total_pages':len(doc),'review_pages':pages,'toc':doc.get_toc() if key=='current' else []}
tex=(BOOK/'generated/chapters/ch10.tex').read_text()
manifest['source_hashes']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BOOK/'generated/chapters/ch10.tex',BOOK/'chapters/new/ch10-oscillation.tex',BOOK/'chapters/new/ch10-source-exercises.tex']}
manifest['examples']=len(re.findall(r'\\begin\{origexamplebox\}',tex))
manifest['solutions']=len(re.findall(r'\\begin\{xesolution\}',tex))
manifest['tikz_pictures']=len(re.findall(r'\\begin\{tikzpicture\}',tex))
manifest['figure_labels']=re.findall(r'\\label\{(ch10:fig:[^}]+)\}',tex)
manifest['figure_references']=re.findall(r'\\(?:ref|cref|autoref)\{(ch10:fig:[^}]+)\}',tex)
manifest['white_fill_mentions']=len(re.findall(r'fill\s*=\s*white',tex))
current=fitz.open(FILES['current'][0]);main=fitz.open(ROOT/'output/pdf/高中物理竞赛一轮讲义.pdf')
details=OUT/'details';details.mkdir(exist_ok=True)
figure_crops={
 'figure-10-1':(2,(140,345,475,540)),
 'figure-10-2':(4,(70,248,550,435)),
 'figure-10-3':(5,(110,350,530,487)),
 'figure-10-4':(6,(140,463,470,550)),
 'figure-10-5':(7,(180,374,440,580)),
 'figure-10-6':(9,(150,164,460,290)),
}
for name,(n,box) in figure_crops.items():
 current[n-1].get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(box),alpha=False).save(details/f'{name}.png')
manifest['figure_crops']=figure_crops
toc=main.get_toc();chstart=next(x[2] for x in toc if x[0]==1 and x[1]==current.get_toc()[0][1])
def bodytext(page):
 return re.sub(r'\s+','',page.get_text(clip=fitz.Rect(42,51,552,780)))
clip=fitz.Rect(42,51,552,780)
manifest['main']={'path':str(ROOT/'output/pdf/高中物理竞赛一轮讲义.pdf'),'sha256':hashlib.sha256((ROOT/'output/pdf/高中物理竞赛一轮讲义.pdf').read_bytes()).hexdigest(),'pages':len(main),'chapter_physical_pages':[chstart,chstart+len(current)-2],
 'body_text_matches_standalone':all(bodytext(current[i])==bodytext(main[chstart+i-2]) for i in range(1,len(current))),
 'body_raster_matches_standalone':all(current[i].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False).samples==main[chstart+i-2].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False).samples for i in range(1,len(current)))}
for cmd,name in [(['qpdf','--check',str(FILES['current'][0])],'qpdf.txt'),(['pdffonts',str(FILES['current'][0])],'pdffonts.txt')]:
 r=subprocess.run(cmd,capture_output=True,text=True);(OUT/name).write_text(r.stdout+r.stderr)
 manifest[name]={'exit_code':r.returncode}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k not in FILES},ensure_ascii=False,indent=2))
