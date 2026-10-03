"""Publish four validated artifacts; keep archived predecessors recoverable."""
from datetime import datetime
from pathlib import Path
import json,os,shutil
import build_review_ch15_ch16 as revision
from check_revision_ch15_ch16 import COUNTS,LEDGER,sha
BASE=revision.BASE;ARCHIVE=revision.ARCHIVE;FORMAL=revision.FORMAL;BOOK=revision.book.BOOK
read=lambda p:json.loads(p.read_text())
checks=read(BASE/'release-checks.json');visual=read(BASE/'visual-reviewed.json')
geometry=read(BASE/'geometry-checks.json');baseline=read(ARCHIVE/'manifest.json')
assert sha(LEDGER)==checks['source_ledger']['sha256']
assert checks['source_ledger']['unresolved_recorded_targets']==0
assert not checks['unchanged_body_text_differences'] and not checks['unchanged_body_raster_differences']
assert checks['other_generated_chapters_unchanged']==30
assert checks['recorded_frozen_source_xelatex_passes_per_pdf']==2
for ch,(_,figures) in COUNTS.items():
 item=checks['pdfs'][ch];v=visual['chapters'][ch]
 assert v['pdf_sha256']==item['sha256']==sha(BASE/ch/f'{ch}.pdf')
 assert v['source_sha256']==item['source_sha256']==sha(BOOK/f'generated/chapters/{ch}.tex')
 assert geometry['generated_source_sha256'][ch]==item['source_sha256']
 assert v['all_pages_reviewed']==item['pages'] and v['figure_groups_reviewed']==figures
 assert set(v['figure_labels_reviewed'])==set(item['figure_labels']) and v['review_passed']
 assert all(x['solution_same_page'] for x in item['question_solution_adjacency'])
 assert revision.chapter_text(int(ch[2:]))[0]==(BOOK/f'generated/chapters/{ch}.tex').read_text()
 for key in ('volume3','main'):assert not checks['pdfs'][key][ch+'_raster_difference_body_pages']
for key in ('volume3','main'):
 assert visual['collections'][key]['review_passed']
 assert visual['collections'][key]['pdf_sha256']==checks['pdfs'][key]['sha256']
 assert visual['collections'][key]['covers_toc_and_chapter_boundaries_reviewed']
assert all(sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
names={key:name.replace('_含解答与解图','') for key,name in revision.OLD_NAMES.items()}
for key,old in revision.OLD_NAMES.items():
 assert sha(BASE/key/f'{key}.pdf')==checks['pdfs'][key]['sha256']
 assert sha(FORMAL/old)==baseline['old_formal'][str(FORMAL/old)]==sha(ARCHIVE/'pdf'/old)
 assert old==names[key] or not (FORMAL/names[key]).exists()
stage=BASE/'publish';stage.mkdir(exist_ok=True)
for key,new in names.items():
 shutil.copy2(BASE/key/f'{key}.pdf',stage/new);assert sha(stage/new)==checks['pdfs'][key]['sha256']
(ARCHIVE/'superseded').mkdir(exist_ok=True)
for key,new in names.items():
 os.replace(stage/new,FORMAL/new)
 old=revision.OLD_NAMES[key]
 if old!=new:shutil.move(str(FORMAL/old),ARCHIVE/'superseded'/old)
record={'published_at':datetime.now().astimezone().isoformat(),'files':{},'archive':str(ARCHIVE),
 'source_ledger_sha256':sha(LEDGER),'other_generated_chapters_modified':False,'second_round_modified':False}
for key,new in names.items():
 assert sha(FORMAL/new)==checks['pdfs'][key]['sha256']
 record['files'][new]={'sha256':sha(FORMAL/new),'pages':checks['pdfs'][key]['pages']}
(BASE/'publication.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
