"""Compare chapter bodies and bookmark destinations across compiled editions."""
import fitz, hashlib, json, re
from pathlib import Path
import build_review_ch21_ch22 as r
names={21:'恒定电流与复杂电路',22:'洛伦兹力与带电粒子运动'}
def bodytext(p):
 return re.sub(r'\s+','',p.get_text(clip=fitz.Rect(0,64,p.rect.width,p.rect.height-45)))
results={}
for key in ['volume4','main']:
 p=r.BASE/key/f'{key}.pdf'
 if not p.exists():continue
 d=fitz.open(p);toc=d.get_toc();records=[]
 for n,title in names.items():
  ref=fitz.open(r.BASE/f'ch{n}'/f'ch{n}.pdf')
  start=next(x[2]-1 for x in toc if x[0]==1 and x[1]==title)
  differences=[]
  for j in range(1,len(ref)):
   if bodytext(ref[j])!=bodytext(d[start+j-1]):differences.append(j+1)
  records.append({'chapter':n,'start_physical_page':start+1,'body_pages':len(ref)-1,'text_difference_pages':differences})
  assert not differences,(key,n,differences)
  out=r.BASE/key/'review';out.mkdir(exist_ok=True)
  for i in [start-1,start,start+len(ref)-2,start+len(ref)-1]:
   if 0<=i<len(d):d[i].get_pixmap(dpi=120,alpha=False).save(out/f'boundary-{i+1:03}.png')
 assert all(1<=x[2]<=len(d) for x in toc)
 for i in range(min(4,len(d))):d[i].get_pixmap(dpi=100,alpha=False).save(r.BASE/key/'review'/f'front-{i+1:02}.png')
 results[key]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'chapters':records,'bookmark_destinations_valid':True}
(r.BASE/'combined-regression.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
