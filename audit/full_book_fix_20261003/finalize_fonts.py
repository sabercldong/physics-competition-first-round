from pathlib import Path
import os,subprocess,json,concurrent.futures,hashlib,re
root=Path.cwd();book=root/'sample/xes-original/restructured-complete';audit=root/'audit/full_book_fix_20261003';env=os.environ.copy();env['TEXFONTMAPS']=str(book)+':'+env.get('TEXFONTMAPS','')
rows=json.loads((audit/'builds.json').read_text());assert len(rows)==11
# Re-run one converged pass with the project's text extraction mappings.
def one(row):
 pdf=Path(row['staged']);cmd=['/Library/TeX/texbin/xelatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',f'-output-directory={pdf.parent}',row['source']]
 p=subprocess.run(cmd,cwd=book,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(pdf.parent/'font-map-pass.txt').write_text(p.stdout)
 assert p.returncode==0,(row['slug'],p.stdout[-2000:]);log=pdf.with_suffix('.log').read_text(errors='replace')
 row['warnings']=[x for x in log.splitlines() if re.search(r'undefined references|Reference .*undefined|multiply defined|Missing character:|Overfull',x)]
 row['sha256']=hashlib.sha256(pdf.read_bytes()).hexdigest();row['passes']+=1;row['project_font_map']=True;print(row['slug'],'font mappings retained',flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,rows))
(audit/'final_builds.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('Eleven derived builds finalized.')
