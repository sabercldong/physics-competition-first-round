"""Read-only source/PDF render evidence for the problem-figure audit."""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/problem-figure-audit-20260923'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = Path('/Users/dongxingxi/Downloads/学而思资料/二轮/兴趣二阶春季.pdf')
doc = fitz.open(SOURCE)
if '--record' in sys.argv:
    project = ROOT.parents[2]
    paths = [SOURCE,
        project / 'output/pdf/高中物理竞赛一轮讲义.pdf',
        project / 'output/pdf/高中物理竞赛一轮讲义_第31章_狭义相对论.pdf',
        project / 'output/pdf/高中物理竞赛一轮讲义_第32章_量子现象、原子与原子核物理.pdf',
        ROOT / 'chapters/new/ch31-relativity.tex',
        ROOT / 'chapters/new/ch32-modern.tex',
        ROOT / 'advanced/A6-relativity.tex',
        ROOT / 'advanced/A6-quantum-mechanics.tex']
    groups = [
        (193,10,1,1,None,'未找到对应题图'),
        (194,10,2,2,None,'未找到对应题图'),
        (197,10,5,1,'advA6:ex:relativistic-accelerator','已画，标注拥挤且原题解答未完成'),
        (200,11,1,2,None,'未找到对应题图'),
        (201,11,2,2,None,'未找到对应题图'),
        (202,11,3,1,None,'未找到对应题图'),
        (204,11,6,2,'advA6:ex:elliptic-cylinder','已画，缺多项原图变量标注'),
        (219,14,4,1,None,'未找到对应题图；一般卢瑟福推导不等价'),
        (220,14,5,1,None,'未找到对应题图；一般布拉格图不等价')]
    payload = {
        'date':'2026-09-23',
        'type':'findings_not_acceptance',
        'scope':'current chapters 31-32 plus corresponding A6 problems; not a full-book audit',
        'source_pages':list(range(193,207))+list(range(217,222)),
        'source_problem_count':21,
        'source_figures':[dict(source_object_id=f'r2-spring:exercise:L{le}:Q{q}:figure-group',physical_page=p,printed_page=p-144,panels=n,target=t,finding=s) for p,le,q,n,t,s in groups],
        'main_solution_explanation_priorities':['31.2','31.4','31.8','32.1','32.3','32.7'],
        'advanced_problem_priorities':['A6.2','A6.3','A6.1','A6.4'],
        'formal_pdfs_modified':False,
        'files':[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]}
    target=ROOT/'audit/source-review/ch31-ch32-problem-figure-findings-20260923.json'
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print(target)
    print('groups',len(groups),'panels',sum(g[3] for g in groups),'unmatched panels',sum(g[3] for g in groups if g[4] is None))
    sys.exit(0)
if '--ocr' in sys.argv:
    binary = ROOT.parents[2] / 'tmp/pdfs/vision_ocr'
    pages = list(range(193, 207)) + list(range(217, 222))
    def ocr(p):
        output = OUT / f'source-{p:03}.txt'
        if not output.exists():
            subprocess.run([str(binary), str(OUT / f'source-{p:03}.png'), str(output)], check=True)
        return p
    with ThreadPoolExecutor(max_workers=3) as pool:
        print(list(pool.map(ocr, pages)))
    sys.exit(0)
for start in range(193, 225, 8):
    sheet = Image.new('RGB', (1600, 2400), 'white')
    draw = ImageDraw.Draw(sheet)
    for j, p in enumerate(range(start, min(start+8, len(doc)+1))):
        image_path = OUT / f'source-{p:03}.png'
        doc[p-1].get_pixmap(matrix=fitz.Matrix(2, 2)).save(str(image_path))
        im = Image.open(image_path).convert('RGB')
        im.thumbnail((780, 560))
        x, y = (j % 2)*800, (j//2)*600
        sheet.paste(im, (x, y+30))
        draw.text((x+10, y+5), f'physical page {p}', fill='black')
    sheet.save(OUT / f'contact-{start}.jpg')
print(OUT)
