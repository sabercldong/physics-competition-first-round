"""Record explicit manual review; this command is not an automatic visual test."""
import argparse,json,re
from datetime import datetime
import fitz
from check_revision_ch15_ch16 import BASE,BOOK,COUNTS,sha
p=argparse.ArgumentParser();p.add_argument('--confirm-manual-review',action='store_true');a=p.parse_args()
assert a.confirm_manual_review,'View all pages, figure details and collection boundaries before attesting.'
details=json.loads((BASE/'detail-manifest.json').read_text())
collections=json.loads((BASE/'collection-render/manifest.json').read_text())
record={'reviewed_at':datetime.now().astimezone().isoformat(),'chapters':{},'collections':{},
 'method':'Every revised page inspected at contact-sheet scale; all 35 figure groups viewed at 330dpi. Affected figures and final pagination rechecked after adjustments. Counts and successful compilation are not visual approval.'}
for ch,(_,count) in COUNTS.items():
 pdf=BASE/ch/f'{ch}.pdf';d=fitz.open(pdf);rows=[r for r in details if r['chapter']==ch]
 assert len(rows)==count and all(r['pdf_sha256']==sha(pdf) for r in rows)
 labels=[s for s in re.findall(r'\\label\{([^}]+)\}',(BOOK/f'generated/chapters/{ch}.tex').read_text()) if ':fig:' in s]
 assert len(labels)==count
 manifest=json.loads((BASE/'render'/ch/'manifest.json').read_text())
 assert manifest['sha256']==sha(pdf) and manifest['pages']==len(d)
 record['chapters'][ch]={'pdf_sha256':sha(pdf),'source_sha256':sha(BOOK/f'generated/chapters/{ch}.tex'),
  'all_pages_reviewed':len(d),'figure_groups_reviewed':count,'figure_labels_reviewed':labels,'review_passed':True}
for key,item in collections.items():
 assert item['pdf_sha256']==sha(BASE/key/f'{key}.pdf')
 record['collections'][key]={**item,'covers_toc_and_chapter_boundaries_reviewed':True,'review_passed':True}
(BASE/'visual-reviewed.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
