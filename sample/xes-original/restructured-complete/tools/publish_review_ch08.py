#!/usr/bin/env python3
"""Publish only the three independently checked chapter-eight deliverables."""
from pathlib import Path
import hashlib, json, os, shutil
from datetime import datetime

BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
BASE=BOOK/'build/review-ch08-20260909'
FORMAL=ROOT/'output/pdf'
ARCHIVE=ROOT/'archive/2026-09-09-ch08-revision'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

checks=json.loads((BASE/'release-checks.json').read_text())
geometry=json.loads((BASE/'geometry-checks.json').read_text())
visual=json.loads((BASE/'visual-reviewed.json').read_text())
assert visual['all_27_diagram_groups_reviewed']
assert visual['pdf_sha256']==checks['pdfs']['ch08']['sha256']
assert sha(BOOK/'generated/chapters/ch08.tex')==checks['source_sha256']
assert all(sha(Path(p))==h for p,h in geometry['source_hashes'].items())
assert not checks['unchanged_main_body_text_differences']
assert not checks['unchanged_main_body_raster_differences']
assert checks['recorded_frozen_source_xelatex_passes_per_pdf']==2
targets=[
 ('ch08','高中物理竞赛一轮讲义_第08章_功、能量和守恒定律_含解答与解图.pdf','高中物理竞赛一轮讲义_第08章_功、能量和守恒定律.pdf'),
 ('volume2','高中物理竞赛一轮讲义_第2卷_力学.pdf','高中物理竞赛一轮讲义_第2卷_力学.pdf'),
 ('main','高中物理竞赛一轮讲义.pdf','高中物理竞赛一轮讲义.pdf'),
]
for key,old,new in targets:
    assert sha(BASE/key/f'{key}.pdf')==checks['pdfs'][key]['sha256']
    assert sha(FORMAL/old)==sha(ARCHIVE/'pdf'/old), f'Formal file changed since backup: {old}'
    assert old==new or not (FORMAL/new).exists(), f'New target already exists: {new}'

# Prepare all copies before replacing any formal file. All are on one filesystem.
stage=BASE/'publish'
stage.mkdir(exist_ok=True)
for key,old,new in targets:
    shutil.copy2(BASE/key/f'{key}.pdf',stage/new)
    assert sha(stage/new)==checks['pdfs'][key]['sha256']
(ARCHIVE/'superseded').mkdir(exist_ok=True)
for key,old,new in targets:
    os.replace(stage/new,FORMAL/new)
    if old!=new:
        assert not (ARCHIVE/'superseded'/old).exists()
        shutil.move(str(FORMAL/old),ARCHIVE/'superseded'/old)

published={}
for key,old,new in targets:
    assert sha(FORMAL/new)==checks['pdfs'][key]['sha256']
    published[new]={'sha256':sha(FORMAL/new),'pages':checks['pdfs'][key]['pages']}
record={'published_at':datetime.now().astimezone().isoformat(),'source_sha256':checks['source_sha256'],
        'files':published,'archive':str(ARCHIVE),'second_round_modified':False}
(BASE/'publication.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))

