"""Render named high-resolution evidence crops; do not alter PDFs."""
from pathlib import Path
import fitz,json
BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
OUT=BOOK/'build/review-ch09-20260909/details';OUT.mkdir(parents=True,exist_ok=True)
doc=fitz.open(ROOT/'output/pdf/高中物理竞赛一轮讲义_第09章_角动量与刚体动力学_含解答与解图.pdf')
items=[
 ('cross',2,.35,.56),('particle',3,.13,.35),('apsides',3,.70,.92),
 ('kepler',4,.29,.58),('inertia',5,.12,.52),('cosmic',6,.06,.32),('gyro',6,.43,.69),
 ('area',14,.66,.84),('conical',16,.22,.51),('dumbbell',17,.13,.42),
 ('collision',18,.17,.39),('seesaw',19,.18,.42),('funnel',20,.18,.40),
 ('euler',21,.44,.69),('rolling',22,.11,.31),('incline',23,.30,.49),
 ('brake',30,.12,.36),('two_wheels',31,.12,.38),('billiard',32,.10,.31),
 ('balls',32,.65,.82),('bounce',33,.40,.61),('egg',34,.20,.59),
 ('pulley',35,.12,.37),('torque',35,.75,.94),('percussion',36,.59,.84),
 ('rod',37,.24,.44),('chimney',38,.12,.43)]
for name,n,lo,hi in items:
    page=doc[n-1];r=page.rect
    clip=fitz.Rect(32,r.height*lo,r.width-25,r.height*hi)
    page.get_pixmap(matrix=fitz.Matrix(3.4,3.4),clip=clip,alpha=False).save(OUT/f'{name}.png')
(OUT/'index.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print(len(items),'figure groups rendered')
