"""Publish four artifacts only after source, visual, numeric and PDF regression gates."""
from pathlib import Path
from datetime import datetime
import hashlib,json,os,shutil
import build_restructured as book

BOOK=book.BOOK;ROOT=book.PROJECT
BASE=BOOK/'build/revision-ch11-ch12-20260912'
ARCHIVE=ROOT/'archive/2026-09-12-ch11-ch12-revision'
FORMAL=ROOT/'output/pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

checks=read(BASE/'release-checks.json')
visual=read(BASE/'visual-reviewed.json')
geometry=read(BASE/'geometry-checks.json')
ledger_path=BOOK/'audit/source-review/ch11-ch12-revision-ledger-20260912.json'
assert sha(ledger_path)==checks['source_ledger']['sha256']
assert checks['source_ledger']['unresolved_recorded_targets']==0
assert not checks['unchanged_body_text_differences'] and not checks['unchanged_body_raster_differences']
assert checks['other_generated_chapters_unchanged']==30
assert checks['recorded_frozen_source_xelatex_passes_per_pdf']==2
for ch,count in [('ch11',6),('ch12',21)]:
    item=checks['pdfs'][ch];v=visual['chapters'][ch]
    assert v['pdf_sha256']==item['sha256']==sha(BASE/ch/f'{ch}.pdf')
    assert v['source_sha256']==item['source_sha256']==sha(BOOK/f'generated/chapters/{ch}.tex')
    assert geometry['generated_source_sha256'][ch]==item['source_sha256']
    assert v['all_pages_reviewed']==item['pages'] and v['technical_figure_groups_reviewed']==count
    assert len(v['figure_labels_reviewed'])==count and v['review_passed']
    assert all(x['solution_same_page'] for x in item['question_solution_adjacency'])
    for collection in ('volume2','main'):
        assert not checks['pdfs'][collection][ch+'_raster_difference_body_pages']
    n=int(ch[2:]);spec=book.CHAPTERS[n]
    parts=[f"\\chapter{{{spec['title']}}}\n"]
    for name in spec['new']:
        p=BOOK/'chapters/new'/name
        parts.append(book.flatten_inputs(p.read_text(),p.parent,set()))
    regenerated=book.apply_chapter_layout(n,book.normalize_visible_eponyms('\n'.join(parts)))
    assert regenerated==(BOOK/f'generated/chapters/{ch}.tex').read_text(),'Maintenance source changed after final build'

targets=[
 ('ch11','高中物理竞赛一轮讲义_第11章_有心力、万有引力与天体运动_含解答与解图.pdf','高中物理竞赛一轮讲义_第11章_有心力、万有引力与天体运动.pdf'),
 ('ch12','高中物理竞赛一轮讲义_第12章_弹性体与机械波_含解答与解图.pdf','高中物理竞赛一轮讲义_第12章_弹性体与机械波.pdf'),
 ('volume2','高中物理竞赛一轮讲义_第2卷_力学.pdf','高中物理竞赛一轮讲义_第2卷_力学.pdf'),
 ('main','高中物理竞赛一轮讲义.pdf','高中物理竞赛一轮讲义.pdf')]
baseline=read(ARCHIVE/'manifest.json')
assert all(sha(Path(p))==h for p,h in baseline['protected_generated_chapters'].items())
for key,old,new in targets:
    assert sha(BASE/key/f'{key}.pdf')==checks['pdfs'][key]['sha256']
    assert sha(FORMAL/old)==baseline['old_formal'][str(FORMAL/old)]==sha(ARCHIVE/'pdf'/old)
    assert old==new or not (FORMAL/new).exists()

stage=BASE/'publish';stage.mkdir(exist_ok=True)
for key,old,new in targets:
    shutil.copy2(BASE/key/f'{key}.pdf',stage/new)
    assert sha(stage/new)==checks['pdfs'][key]['sha256']
(ARCHIVE/'superseded').mkdir(exist_ok=True)
for key,old,new in targets:
    os.replace(stage/new,FORMAL/new)
    if old!=new:shutil.move(str(FORMAL/old),ARCHIVE/'superseded'/old)

record={'published_at':datetime.now().astimezone().isoformat(),'files':{},'archive':str(ARCHIVE),
 'source_ledger_sha256':sha(ledger_path),'second_round_modified':False,'other_generated_chapters_modified':False}
for key,old,new in targets:
    assert sha(FORMAL/new)==checks['pdfs'][key]['sha256']
    record['files'][new]={'sha256':sha(FORMAL/new),'pages':checks['pdfs'][key]['pages']}
(BASE/'publication.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
