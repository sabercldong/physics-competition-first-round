from pathlib import Path
import os,json,subprocess,hashlib
root=Path.cwd();book=root/'sample/xes-original/restructured-complete';audit=root/'audit/full_book_fix_20261003';env=os.environ.copy();env['TEXFONTMAPS']=str(book)+':'+env.get('TEXFONTMAPS','')
rows=json.loads((audit/'final_builds.json').read_text());assert len(rows)==11
main=book/'build/fix-20261003/main/main.pdf';xdv=main.with_suffix('.xdv');assert xdv.exists()
p=subprocess.run(['/Library/TeX/texbin/xdvipdfmx','-o',str(main),str(xdv)],cwd=book,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(main.parent/'font-map-conversion.txt').write_text(p.stdout);assert p.returncode==0
rows.append(dict(slug='main',source=str(book/'main.tex'),staged=str(main),output=str(root/'output/pdf/高中物理竞赛一轮讲义.pdf'),sha256=hashlib.sha256(main.read_bytes()).hexdigest(),project_font_map=True))
(audit/'final_builds.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('All twelve builds finalized.')
