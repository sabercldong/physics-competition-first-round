"""Read-only PDF checks and review renders; never publishes."""
import fitz,json,re,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
import build_review_ch21_ch22 as r
results={}
for key in ('ch21','ch22','volume4','main'):
 p=r.BASE/key/f'{key}.pdf'
 if not p.exists():continue
 d=fitz.open(p);out=r.BASE/key/'review';out.mkdir(exist_ok=True)
 log=(p.with_suffix('.log')).read_text(errors='replace')
 warnings=[s for s in log.splitlines() if re.search(r'Overfull|Underfull|Missing character|undefined|multiply defined|LaTeX Warning',s)]
 inherited=[]
 if key=='main':
  oldlog=r.book.BOOK/'build/revision-ch19-ch20-20260920/main/main.log'
  oldwarnings=[s for s in oldlog.read_text(errors='replace').splitlines() if s.startswith('Underfull \\hbox')]
  inherited=[s for s in warnings if s in oldwarnings]
 q=subprocess.run(['qpdf','--check',str(p)],text=True,capture_output=True)
 (out/'qpdf.txt').write_text(q.stdout+q.stderr)
 fonts=subprocess.run(['pdffonts',str(p)],text=True,capture_output=True)
 (out/'fonts.txt').write_text(fonts.stdout)
 text='\n'.join(pg.get_text() for pg in d)
 (out/'text.txt').write_text(text)
 results[key]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':len(d),'warnings':warnings,'inherited_out_of_scope_warnings':inherited,'new_warnings':[s for s in warnings if s not in inherited],'qpdf':q.returncode,'all_fonts_embedded':all(' yes ' in s for s in fonts.stdout.splitlines()[2:]),'toc_entries':len(d.get_toc()),'replacement_chars':text.count('\ufffd')}
 if key.startswith('ch'):
  for i,pg in enumerate(d):pg.get_pixmap(dpi=180,alpha=False).save(out/f'page-{i+1:03}.png')
  for start in range(0,len(d),4):
   im=Image.new('RGB',(1400,1980),'#ddd');dr=ImageDraw.Draw(im)
   for j in range(min(4,len(d)-start)):
    a=Image.open(out/f'page-{start+j+1:03}.png');a.thumbnail((680,940));x=700*(j%2)+10;y=990*(j//2)+30
    im.paste(a,(x,y));dr.text((x,y-22),f'{key}: PDF {start+j+1}',fill='black')
   im.save(out/f'contact-{start//4+1:02}.png')
baseline=json.loads((r.ARCHIVE/'manifest.json').read_text())
assert all(r.common.sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
(r.BASE/'release-checks.json').write_text(json.dumps({'protected_chapters':30,'pdfs':results},ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
