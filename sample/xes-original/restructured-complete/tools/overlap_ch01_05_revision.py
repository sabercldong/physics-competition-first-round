"""Run the single-page skill checker on EACH content page, not the title page."""
import concurrent.futures
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import pymupdf as fitz

BASE=Path(__file__).resolve().parents[1]/'build/revision-ch01-05-20260923'
CHECKER=Path('/Users/dongxingxi/.codex/skills/thesis-figure-skill/references/pdf-overlap-checker.py')
spec=importlib.util.spec_from_file_location('diagram_checker',CHECKER)
checker=importlib.util.module_from_spec(spec);sys.modules[spec.name]=checker;spec.loader.exec_module(checker)

def chapter(n):
    target=f'ch{n:02}';path=BASE/target/(target+'.pdf');doc=fitz.open(path);pages=[]
    with tempfile.TemporaryDirectory(prefix='overlap-pages-',dir=BASE) as temp:
        for i in range(1,len(doc)):
            one=fitz.open();one.insert_pdf(doc,from_page=i,to_page=i)
            p=Path(temp)/f'p{i+1:03}.pdf';one.save(p);one.close()
            issues=checker.validate_pdf(str(p))
            pages.append(dict(page=i+1,issues=[dict(level=x.level,category=x.category,message=x.message) for x in issues]))
    result=dict(target=target,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),pages=pages,
        note='Each content page checked independently; title excluded. Candidate findings require visual triage, especially math glyphs and physical line intersections.')
    (BASE/f'{target}-overlap-allpages.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return target,len(pages),sum(len(x['issues']) for x in pages)

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(chapter,range(1,6)):print(r,flush=True)
