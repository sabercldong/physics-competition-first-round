"""Read-only evidence capture: do not alter chapter sources or published PDFs."""
from pathlib import Path
import hashlib,json,re,subprocess
import fitz
from PIL import Image,ImageDraw
BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
BASE=BOOK/'build/review-ch15-ch16-20260915'
BASE.mkdir(parents=True,exist_ok=True)
files={
 'ch15':ROOT/'output/pdf/高中物理竞赛一轮讲义_第15章_热力学第一定律_含解答与解图.pdf',
 'ch16':ROOT/'output/pdf/高中物理竞赛一轮讲义_第16章_热力学第二定律_含解答与解图.pdf',
 'main':ROOT/'output/pdf/高中物理竞赛一轮讲义.pdf',
 'source':Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020寒】兴趣一阶-热学.pdf')}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'scope':'Read-only audit, no teaching content or formal PDF changes','files':{},'chapters':{}}
for key,p in files.items():
 d=fitz.open(p);manifest['files'][key]={'path':str(p),'sha256':sha(p),'pages':len(d)}
 if key=='main':continue
 out=BASE/key;out.mkdir(exist_ok=True)
 pages=list(range(18,46)) if key=='source' else list(range(1,len(d)+1))
 manifest['files'][key]['rendered_physical_pages']=pages
 for pn in pages:
  pg=d[pn-1];pg.get_pixmap(dpi=220,alpha=False).save(out/f'page-{pn:03}.png')
  (out/f'page-{pn:03}.txt').write_text(pg.get_text())
 for start in range(0,len(pages),6):
  sheet=Image.new('RGB',(1320,1300),'#ddd');dr=ImageDraw.Draw(sheet)
  for j,pn in enumerate(pages[start:start+6]):
   im=Image.open(out/f'page-{pn:03}.png');im.thumbnail((430,615));x=j%3*440+5;y=j//3*650+25
   sheet.paste(im,(x,y));dr.text((x,y-20),str(pn),fill='black')
  sheet.save(out/f'contact-{start//6+1}.png')
 if key.startswith('ch'):
  for cmd in ('qpdf','pdffonts'):
   r=subprocess.run([cmd,'--check',str(p)] if cmd=='qpdf' else [cmd,str(p)],capture_output=True,text=True)
   (out/f'{cmd}.txt').write_text(r.stdout+r.stderr)
  n=int(key[2:]);tex=BOOK/f'generated/chapters/{key}.tex';s=tex.read_text()
  manifest['chapters'][key]={'source_sha256':sha(tex),'examples':s.count(r'\begin{origexamplebox}'),
   'solutions':s.count(r'\begin{xesolution}'),'figure_labels':re.findall(r'\\label\{('+key+r':fig:[^}]+)\}',s),
   'bookmarks':d.get_toc(),'rendered_figure_numbers':sorted(set(re.findall(r'图\s*'+str(n)+r'\.(\d+)', ''.join(x.get_text() for x in d))),key=int)}
  master=fitz.open(files['main']);tops=[r for r in master.get_toc() if r[0]==1]
  begin=tops[n-1][2]-1;end=tops[n][2]-1;clip=fitz.Rect(42,51,552,780)
  body=lambda pg:re.sub(r'\s+','',pg.get_text(clip=clip))
  manifest['chapters'][key]['master_physical_pages']=[begin+1,end]
  manifest['chapters'][key]['master_body_text_equal']=[body(x) for x in d][1:]==[body(master[j]) for j in range(begin,end)]
  manifest['chapters'][key]['master_body_raster_diff_pages']=[j+1 for j in range(end-begin) if d[j+1].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False).samples!=master[begin+j].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False).samples] if len(d)-1==end-begin else 'page-count-difference'
manifest['teaching_source_hashes']={str(p):sha(p) for unit in ('twenty-ninth-section','thirtieth-section') for p in (ROOT/'sample/xes-original'/unit).glob('*.tex')}
(BASE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(manifest,ensure_ascii=False,indent=2))
