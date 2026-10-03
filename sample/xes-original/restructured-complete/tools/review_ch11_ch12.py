"""Read-only teaching-source/PDF audit preparation for chapters 11 and 12."""
from pathlib import Path
import hashlib,json,re,subprocess
import fitz
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
BASE=BOOK/'build/review-ch11-ch12-20260912'
BASE.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files={
 'ch11':ROOT/'output/pdf/高中物理竞赛一轮讲义_第11章_有心力、万有引力与天体运动_含解答与解图.pdf',
 'ch12':ROOT/'output/pdf/高中物理竞赛一轮讲义_第12章_弹性体与机械波_含解答与解图.pdf',
 'main':ROOT/'output/pdf/高中物理竞赛一轮讲义.pdf',
 'notes':Path('/Users/dongxingxi/Downloads/学而思资料/二轮/2020秋季高二物理竞赛学生版讲义.pdf'),
 'exercises':Path('/Users/dongxingxi/Downloads/学而思资料/二轮/2020秋季高二物理竞赛习题.pdf')}
manifest={'date':'2026-09-12','scope':'read-only review; no teaching-source or formal-PDF edits','files':{},'chapters':{}}
for key,p in files.items():
 d=fitz.open(p); manifest['files'][key]={'path':str(p),'sha256':sha(p),'pages':len(d)}
 if key=='main':continue
 out=BASE/key;out.mkdir(exist_ok=True)
 pages=(list(range(99,123)) if key=='notes' else list(range(40,44))+list(range(49,53)) if key=='exercises' else list(range(1,len(d)+1)))
 dpi=240 if key.startswith('ch') else 170
 for pn in pages:
  pg=d[pn-1];pg.get_pixmap(dpi=dpi,alpha=False).save(out/f'page-{pn:03}.png')
  (out/f'page-{pn:03}.txt').write_text(pg.get_text())
 for start in range(0,len(pages),6):
  selected=pages[start:start+6];sheet=Image.new('RGB',(3*440,2*650),'#ddd');dr=ImageDraw.Draw(sheet)
  for j,pn in enumerate(selected):
   im=Image.open(out/f'page-{pn:03}.png');im.thumbnail((430,615));x=j%3*440+5;y=j//3*650+25
   sheet.paste(im,(x,y));dr.text((x,y-20),str(pn),fill='black')
  sheet.save(out/f'contact-{start//6+1}.png')
 if key.startswith('ch'):
  for cmd in ('qpdf','pdffonts'):
   args=[cmd,'--check',str(p)] if cmd=='qpdf' else [cmd,str(p)]
   r=subprocess.run(args,capture_output=True,text=True);(out/f'{cmd}.txt').write_text(r.stdout+r.stderr)
  chapter=int(key[2:]); tex=BOOK/f'generated/chapters/{key}.tex';text=tex.read_text()
  manifest['chapters'][key]={'source_sha256':sha(tex),'examples':text.count(r'\begin{origexamplebox}'),
   'solutions':text.count(r'\begin{xesolution}'),'figures':len(set(re.findall(r'图\s*'+str(chapter)+r'\.(\d+)', ''.join(x.get_text() for x in d)))),
   'figure_labels':re.findall(r'\\label\{('+key+r':fig:[^}]+)\}',text),'bookmarks':d.get_toc()}
  master=fitz.open(files['main']); tops=[r for r in master.get_toc() if r[0]==1]
  begin=tops[chapter-1][2]-1;end=tops[chapter][2]-1
  clip=fitz.Rect(42,51,552,780)
  body=lambda pg:re.sub(r'\s+','',pg.get_text(clip=clip))
  manifest['chapters'][key]['master_physical_pages']=[begin+1,end]
  manifest['chapters'][key]['master_body_text_equal']=[body(x) for x in d][1:]==[body(master[j]) for j in range(begin,end)]
  if len(d)-1==end-begin:
   manifest['chapters'][key]['master_body_raster_diff_pages']=[j+1 for j in range(end-begin) if d[j+1].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False).samples!=master[begin+j].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False).samples]
sources=list((BOOK/'chapters/new').glob('ch11-*.tex'))+list((BOOK/'chapters/new').glob('ch12-*.tex'))
manifest['teaching_source_hashes']={str(p):sha(p) for p in sources}
(BASE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(manifest,ensure_ascii=False,indent=2))
