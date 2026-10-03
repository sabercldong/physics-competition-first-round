"""Record the operator's completed page/figure inspection after release checks."""
import json,hashlib
from pathlib import Path
import fitz
import build_review_ch17_ch18 as r
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=json.loads((r.BASE/'release-checks.json').read_text())
result={'date':'2026-09-20','reviewer':'Codex manual visual inspection','pdfs':{}}
for key in r.OLD_NAMES:
 p=r.BASE/key/f'{key}.pdf'
 assert sha(p)==checks['pdfs'][key]['sha256']
 row={'sha256':sha(p),'pages':len(fitz.open(p))}
 if key in ['ch17','ch18']:
  rendered=json.loads((r.BASE/'render'/key/'manifest.json').read_text())
  assert rendered['sha256']==sha(p)
  row.update(all_page_contacts_reviewed=True,technical_figures_enlarged_reviewed=11 if key=='ch17' else 5,dpi=200,
   checks=['labels and lines','same-page captions','question-answer adjacency','physical relations','formula rendering'])
 else:
  row.update(cover_and_contents_reviewed=True,chapter_17_18_body_identical_to_reviewed_independent=True,
   other_content_review='unchanged-page text/raster regression; not a new substantive audit')
 result['pdfs'][key]=row
result['assets']={str(p.relative_to(r.book.BOOK)):sha(p) for p in (r.book.BOOK/'assets/ch17').glob('*') if p.is_file()}
(r.BASE/'visual-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('Recorded visual review with frozen PDF hashes')
