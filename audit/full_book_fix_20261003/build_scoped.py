from pathlib import Path
import json,subprocess,concurrent.futures,hashlib,re,shutil,os
root=Path.cwd();book=root/'sample/xes-original/restructured-complete';base=book/'build/fix-20261003';base.mkdir(exist_ok=True,parents=True)
man=json.loads((book/'generated/deliverables.json').read_text());jobs=[]
for group,ids,key in [('chapters',[11,17,24,31,32],'chapter'),('volumes',[2,3,4,6],'volume')]:
 for row in man[group]:
  if row[key] in ids:jobs.append((f'{key}{row[key]}',book/row['wrapper'],row['output']))
# Combined releases use current chapter sources, with one cover and one contents section.
template=(book/'generated/wrappers/volumes/volume6.tex').read_text()
for title,nums,name in [('第01—02章',[1,2],'高中物理竞赛一轮讲义_第01—02章.pdf'),('第1—7章',list(range(1,8)),'高中物理竞赛一轮讲义_第1—7章.pdf')]:
 s=template.replace('第6卷　近代物理',title);a=s.index(r'\setcounter{chapter}');b=s.index(r'\end{document}')
 s=s[:a]+r'\setcounter{chapter}{0}'+'\n'+''.join(r'\input{generated/chapters/ch'+f'{n:02}'+'.tex}\n' for n in nums)+'\n'+s[b:]
 p=book/'generated/wrappers'/('combined-01-02.tex' if len(nums)==2 else 'combined-01-07.tex');p.write_text(s)
 jobs.append((p.stem,p,name))
def build(job):
 slug,src,name=job;out=base/slug;out.mkdir(exist_ok=True)
 cmd=['/Library/TeX/texbin/xelatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',f'-output-directory={out}',str(src)]
 for passno in range(1,4):
  env=os.environ.copy();env["TEXFONTMAPS"]=str(book)+":"+env.get("TEXFONTMAPS","")
  p=subprocess.run(cmd,cwd=book,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/f'pass{passno}.txt').write_text(p.stdout)
  if p.returncode:raise RuntimeError(f'{slug} failed: {p.stdout[-2500:]}')
  log=(out/(src.stem+'.log')).read_text(errors='replace')
  if passno>=2 and not re.search(r'Rerun to get|Label\(s\) may have changed|Please rerun',log):break
 bad=[x for x in log.splitlines() if re.search(r'undefined references|Reference .*undefined|multiply defined|Missing character:|Overfull',x)]
 pdf=out/(src.stem+'.pdf');print(slug,'complete; warnings',len(bad),flush=True)
 return dict(slug=slug,source=str(src),staged=str(pdf),output=str(root/'output/pdf'/name),passes=passno,warnings=bad,sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(build,jobs):
  results.append(result);(root/'audit/full_book_fix_20261003/builds.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
