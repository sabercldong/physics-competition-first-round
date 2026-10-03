"""Render current PDFs and their source pages for a read-only content audit."""
import hashlib,json,re,subprocess
from pathlib import Path
import fitz
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[4]
BOOK=Path(__file__).resolve().parents[1]
OUT=BOOK/'build/review-ch29-ch30-20260923'
SOURCE=Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020寒】兴趣一阶-光学.pdf')
targets={
 'ch29':(ROOT/'output/pdf/高中物理竞赛一轮讲义_第29章_光的干涉_含解答与解图.pdf',None),
 'ch30':(ROOT/'output/pdf/高中物理竞赛一轮讲义_第30章_衍射、偏振与晶体光学_含解答与解图.pdf',None),
 'source29':(SOURCE,range(32,45)),
 'source30':(SOURCE,range(46,55))}
OUT.mkdir(parents=True,exist_ok=True)
manifest={};figures=[]
for key,(path,pages) in targets.items():
 d=fitz.open(path);pages=list(pages or range(1,len(d)+1));folder=OUT/key;folder.mkdir(exist_ok=True)
 texts=[]
 for pn in pages:
  p=d[pn-1];txt=p.get_text();texts.append(f'\n--- PDF PAGE {pn} ---\n'+txt)
  p.get_pixmap(dpi=160,alpha=False).save(folder/f'page-{pn:03}.png')
  if key.startswith('ch'):
   for block in p.get_text('blocks'):
    match=re.search(r'图\s*(?:29|30)\.\d+',block[4])
    if not match or not block[4].lstrip().startswith('图'):continue
    number=re.search(r'(?:29|30)\.\d+',match[0])[0]
    # Figure clips are review aids only. Whole pages are retained to check edges.
    rect=fitz.Rect(35,max(45,block[1]-350),560,min(p.rect.height-40,block[3]+5))
    dest=folder/f'fig-{number}-p{pn}.png'
    p.get_pixmap(matrix=fitz.Matrix(3.3,3.3),clip=rect,alpha=False).save(dest)
    figures.append({'chapter':key,'figure':number,'page':pn,'file':str(dest)})
 (folder/'text.txt').write_text('\n'.join(texts))
 for start in range(0,len(pages),6):
  sheet=Image.new('RGB',(1500,1420),'#ddd');dr=ImageDraw.Draw(sheet)
  for j,pn in enumerate(pages[start:start+6]):
   im=Image.open(folder/f'page-{pn:03}.png');im.thumbnail((490,680))
   x=500*(j%3)+5;y=710*(j//3)+25;sheet.paste(im,(x,y));dr.text((x,y-20),f'{key} PDF {pn}',fill='black')
  sheet.save(folder/f'contact-{start//6+1}.jpg')
 record={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(d),'rendered_pages':pages,'bookmarks':d.get_toc()}
 if key.startswith('ch'):
  q=subprocess.run(['qpdf','--check',str(path)],capture_output=True,text=True)
  f=subprocess.run(['pdffonts',str(path)],capture_output=True,text=True)
  (folder/'qpdf.txt').write_text(q.stdout+q.stderr);(folder/'fonts.txt').write_text(f.stdout)
  record.update(qpdf_exit=q.returncode,replacement_chars=sum(t.count('\ufffd') for t in texts))
 manifest[key]=record
(OUT/'inspection-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'figure-clips.json').write_text(json.dumps(figures,ensure_ascii=False,indent=2))
print({k:{'pages':v['pages'],'rendered':len(v['rendered_pages'])} for k,v in manifest.items()})
