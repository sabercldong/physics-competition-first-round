from pathlib import Path
import subprocess,concurrent.futures,json
from PIL import Image,ImageDraw
r=Path.cwd();b=r/'sample/xes-original/restructured-complete/build/fix-20261003';out=r/'audit/full_book_fix_20261003/visual';out.mkdir(exist_ok=True);tasks=[]
for n in [11,17,24,31,32]:
 pdf=b/f'chapter{n}'/f'ch{n}.pdf';s=subprocess.check_output(['/opt/homebrew/bin/pdftotext','-layout',str(pdf),'-']).decode().split('\f')[:-1]
 if n==11:nums=[2,3]
 elif n==17:
  i=next(i for i,p in enumerate(s,1) if '例 17.8' in p);nums=list(range(i,len(s)+1))
 elif n==24:
  i=next(i for i,p in enumerate(s,1) if '例 24.6' in p);nums=[i,i+1,i+2]
 else:nums=list(range(2,len(s)+1))
 tasks.extend((f'ch{n}-{i}',pdf,i) for i in nums)
def one(t):
 name,pdf,i=t;p=out/name
 subprocess.run(['/opt/homebrew/bin/pdftoppm','-f',str(i),'-l',str(i),'-scale-to','1200','-singlefile','-png',str(pdf),str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 return name,p.with_suffix('.png')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:results=list(ex.map(one,tasks))
for b in range(0,len(results),8):
 im=Image.new('RGB',(1600,1200),'#ddd');d=ImageDraw.Draw(im)
 for j,(name,p) in enumerate(results[b:b+8]):
  tile=Image.open(p);tile.thumbnail((390,560));x=(j%4)*400;y=(j//4)*600;im.paste(tile,(x+(400-tile.width)//2,y+28));d.text((x+12,y+6),name,fill='black')
 im.save(out/f'contact{b//8+1}.jpg',quality=90)
(out/'pages.json').write_text(json.dumps([dict(file=str(p),page=n) for _,p,n in tasks],ensure_ascii=False,indent=2));print('Rendered',len(results),'pages')
