from pathlib import Path
import json,hashlib,shutil,os
from pypdf import PdfReader
root=Path.cwd();a=root/'audit/full_book_fix_20261003';formal=root/'output/pdf'
check=json.loads((a/'verification.json').read_text());assert check['ok'] and check['derived_files']==48
visual=json.loads((a/'visual_review.json').read_text());assert visual['approved']
rows=json.loads((a/'final_builds.json').read_text());assert len(rows)==12
hashof=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in rows:assert hashof(Path(row['staged']))==row['sha256']
assert hashof(Path(next(x['staged'] for x in rows if x['slug']=='main')))==check['main_sha256']
# Every current output must still match the snapshot taken before this publication.
before=json.loads((a/'before_outputs.json').read_text())
for row in before:assert hashof(formal/row['name'])==row['sha256'],row['name']
source19=formal/'高中物理竞赛一轮讲义_第19章_静电场与电势_含解答与解图.pdf'
canonical19=formal/'高中物理竞赛一轮讲义_第19章_静电场与电势.pdf'
# Fully prepare same-directory temporary copies before replacing any formal PDF.
pairs=[]
for row in rows:
 target=Path(row['output']);tmp=target.with_suffix('.pdf.pending');shutil.copy2(row['staged'],tmp);assert hashof(tmp)==row['sha256'];pairs.append((tmp,target))
tmp=canonical19.with_suffix('.pdf.pending');shutil.copy2(source19,tmp);pairs.append((tmp,canonical19));sha19=hashof(source19)
for tmp,target in pairs:os.replace(tmp,target)
assert hashof(canonical19)==sha19
source19.unlink() # Retire only the now-identical alternate filename.
records=[]
for p in sorted(formal.glob('*.pdf')):records.append(dict(file=p.name,pages=len(PdfReader(p).pages),sha256=hashof(p),bytes=p.stat().st_size))
assert len(records)==49
manifest=dict(date='2026-10-03',scope='一轮讲义合订本与派生文件；不含子目录中的二轮和暂停中的习题册',files=records)
(formal/'发布清单_20261003.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(a/'published.json').write_text(json.dumps(dict(updated=[p.name for _,p in pairs],retired=[source19.name],main_sha256=check['main_sha256'],formal_pdf_count=49),ensure_ascii=False,indent=2))
print('Published',len(pairs),'files; retired one identical alternate; official PDFs:',len(records))
