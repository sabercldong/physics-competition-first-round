"""Record explicit manual review after inspecting rendered pages; never auto-approve."""
import argparse,json,re
from datetime import datetime
import fitz
from check_revision_ch13_ch14 import BASE,BOOK,COUNTS,sha
p=argparse.ArgumentParser()
p.add_argument('--confirm-manual-review',action='store_true',
 help='Only use after viewing all contact sheets, figure details and collection boundaries.')
a=p.parse_args()
assert a.confirm_manual_review,'Manual review must be explicitly attested.'
details=json.loads((BASE/'detail-manifest.json').read_text())
collections=json.loads((BASE/'collection-render/manifest.json').read_text())
record={'reviewed_at':datetime.now().astimezone().isoformat(),'chapters':{},'collections':{},
 'method':'All revised pages inspected at contact-sheet scale; all 44 figure groups viewed as 330dpi detail crops. Final typography-only adjustments rechecked on their affected pages. No automatic approval from figure count.'}
for ch,(_,count) in COUNTS.items():
 pdf=BASE/ch/f'{ch}.pdf';d=fitz.open(pdf);old=fitz.open(BASE/'proof-before-final'/f'{ch}.pdf')
 assert len(d)==len(old)
 changed=[i+1 for i in range(len(d)) if d[i].get_pixmap(dpi=110,alpha=False).samples!=old[i].get_pixmap(dpi=110,alpha=False).samples]
 assert set(changed)<=({'ch13':{17},'ch14':{8,12,16,17,20,25}}[ch]),(ch,changed)
 rows=[r for r in details if r['chapter']==ch]
 assert len(rows)==count and all(r['pdf_sha256']==sha(pdf) for r in rows)
 labels=[s for s in re.findall(r'\\label\{([^}]+)\}',(BOOK/f'generated/chapters/{ch}.tex').read_text()) if ':fig:' in s]
 assert len(labels)==count
 manifest=json.loads((BASE/'render'/ch/'manifest.json').read_text())
 assert manifest['sha256']==sha(pdf) and manifest['pages']==len(d)
 record['chapters'][ch]={'pdf_sha256':sha(pdf),'source_sha256':sha(BOOK/f'generated/chapters/{ch}.tex'),
 'all_pages_reviewed':len(d),'figure_groups_reviewed':count,'figure_labels_reviewed':labels,
 'proof_before_final_sha256':sha(BASE/'proof-before-final'/f'{ch}.pdf'),
 'last_typography_adjustment_pages':changed,'review_passed':True}
for key,item in collections.items():
 assert item['pdf_sha256']==sha(BASE/key/f'{key}.pdf')
 record['collections'][key]={**item,'covers_toc_and_chapter_boundaries_reviewed':True,'review_passed':True}
(BASE/'visual-reviewed.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
