"""Preserve the pre-revision formal files and reproducible TeX sources."""
from pathlib import Path
import hashlib, json, shutil

BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
ARCH=ROOT/'archive/2026-09-08-ch07-revision'
assert not ARCH.exists(), 'Backup already exists; never overwrite it.'
ARCH.mkdir(parents=True)
(ARCH/'pdf').mkdir()
names=['高中物理竞赛一轮讲义_第07章_动量、变质量系统与碰撞_含解答与解图.pdf',
       '高中物理竞赛一轮讲义_第2卷_力学.pdf','高中物理竞赛一轮讲义.pdf']
for name in names:
    shutil.copy2(ROOT/'output/pdf'/name, ARCH/'pdf'/name)
for part in ['seventh-section','eighth-section','ninth-section','twelfth-section']:
    target=ARCH/'source'/part
    target.mkdir(parents=True)
    for file in (ROOT/'sample/xes-original'/part).glob('*.tex'):
        shutil.copy2(file,target/file.name)
u=ARCH/'source/unified'
u.mkdir()
for part in ['generated','chapters','advanced','appendices','assets','tools']:
    shutil.copytree(BOOK/part,u/part,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['main.tex','style.tex','texglyphlist.txt']:
    shutil.copy2(BOOK/name,u/name)
shutil.copy2(BOOK/'build/review-ch06-20260908/main/main.log',u/'previous-main.log')
record={str(f.relative_to(ARCH)):hashlib.sha256(f.read_bytes()).hexdigest()
        for f in ARCH.rglob('*') if f.is_file()}
(ARCH/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('Archived',len(record),'files at',ARCH)
