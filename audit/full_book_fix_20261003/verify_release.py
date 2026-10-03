from pathlib import Path
import json,re,subprocess,hashlib,collections,concurrent.futures
from pypdf import PdfReader
root=Path.cwd();book=root/'sample/xes-original/restructured-complete';audit=root/'audit/full_book_fix_20261003';rows=json.loads((audit/'final_builds.json').read_text());main=Path(next(x['staged'] for x in rows if x['slug']=='main'))
def pages(p):
 s=subprocess.check_output(['/opt/homebrew/bin/pdftotext','-layout',str(p),'-']).decode();ps=s.split('\f');return ps[:-1] if not ps[-1].strip() else ps
def norm(p):return re.sub(r'\s+','','\n'.join(x for x in p.splitlines() if '高中物理竞赛一轮讲义' not in x and not re.fullmatch(r'\s*\d+\s*',x)))
ps=pages(main);lookup={norm(p):i+1 for i,p in enumerate(ps)};bag={tuple(sorted(collections.Counter(norm(p)).items())):i+1 for i,p in enumerate(ps)}
reader=PdfReader(main);dest=[(d.title,reader.get_destination_page_number(d)+1) for d in reader.outline if isinstance(d,dict)]
(audit/'new_outline.json').write_text(json.dumps(dest,ensure_ascii=False,indent=2))
assert '记号说明' in ps[-1] and '符号与常数索引' not in ''.join(ps)
assert '比耐方程' not in ''.join(ps)
for n,count in [(31,8),(32,12)]:
 start=dest[n-1][1]-1;end=dest[n][1]-1
 seq=[int(x) for x in re.findall(r'例\s*'+str(n)+r'\.(\d+)',''.join(ps[start:end]))]
 assert seq==list(range(1,count+1)),(n,seq)
# All new finite-resistance initial-value and cloud assumptions appear in the PDF.
assert '比熵处处相同' in ''.join(ps);assert '先等待暂态结束再取' in ''.join(ps)
assert not re.search(r'\?\?|TODO|FIXME',''.join(ps))
log=main.with_suffix('.log').read_text(errors='replace')
errors=[s for s in log.splitlines() if re.search(r'undefined references|Reference .*undefined|multiply defined|Missing character:|Overfull',s)]
assert not errors,errors
# Compare every official derived file to the rebuilt full book, using replacements for affected files.
replacements={Path(row['output']).name:Path(row['staged']) for row in rows if row['slug']!='main'}
replacements['高中物理竞赛一轮讲义_第19章_静电场与电势.pdf']=root/'output/pdf/高中物理竞赛一轮讲义_第19章_静电场与电势_含解答与解图.pdf'
files=[]
for p in sorted((root/'output/pdf').glob('*.pdf')):
 if p.name in ['高中物理竞赛一轮讲义.pdf','高中物理竞赛一轮讲义_第19章_静电场与电势_含解答与解图.pdf']:continue
 files.append((p.name,replacements.get(p.name,p)))
def verify(item):
 name,p=item;parts=pages(p);bad=[];reordered=[];matched=[];ignored=[]
 for n,s in enumerate(parts,1):
  txt=norm(s)
  if txt in lookup:matched.append(lookup[txt]);continue
  key=tuple(sorted(collections.Counter(txt).items()))
  if key in bag:reordered.append(dict(local=n,main=bag[key]));matched.append(bag[key]);continue
  # Each standalone has a title sheet; volume/combined/advanced may also have a contents section.
  if n==1 or (n<=5 and (re.search(r'^\s*目录',s) or re.search(r'高中物理竞赛一轮讲义\s+目录',s))):ignored.append(n);continue
  bad.append(dict(page=n,start=s[:160]))
 q=subprocess.run(['/opt/homebrew/bin/qpdf','--check',str(p)],capture_output=True,text=True)
 assert q.returncode==0,(name,q.stderr,q.stdout)
 return dict(name=name,pages=len(parts),body_pages=len(matched),frontmatter=ignored,reordered_extraction=reordered,unmatched=bad,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(verify,files))
fail=[r for r in results if r['unmatched']];report=dict(main_pages=len(ps),main_sha256=hashlib.sha256(main.read_bytes()).hexdigest(),main_warnings=errors,derived_files=len(results),versions=results,ok=not fail)
(audit/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('Main pages',len(ps),'derived',len(results),'unmatched files',len(fail))
for r in fail:print(r['name'],len(r['unmatched']),r['unmatched'][:2])
assert not fail
