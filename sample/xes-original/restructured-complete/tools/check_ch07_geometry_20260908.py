"""Reproduce selected Chapter 7 audit findings; never edit the student files."""
from pathlib import Path
import hashlib
import json
import math
import fitz

BOOK = Path(__file__).resolve().parent.parent
ROOT = BOOK.parents[2]
OUT = ROOT / 'tmp/pdfs/ch07-audit-20260908'
chapter = ROOT / 'output/pdf/高中物理竞赛一轮讲义_第07章_动量、变质量系统与碰撞_含解答与解图.pdf'
master = ROOT / 'output/pdf/高中物理竞赛一轮讲义.pdf'
tex = BOOK / 'generated/chapters/ch07.tex'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]

def distance(p, a, b):
    ab = (b[0]-a[0], b[1]-a[1])
    return cross(ab, (p[0]-a[0], p[1]-a[1]))/math.hypot(*ab)

checks = {}
for name, c in [('A', (-1.65, -.55)), ('B', (.55, .50))]:
    a = math.radians(25)
    bottom = (c[0]+.37*math.sin(a), c[1]-.37*math.cos(a))
    checks['7.4_block_'+name] = {
        'center_signed_distance_to_slope': distance(c, (-3, -1.2), (2.9, 1.6)),
        'bottom_midpoint_signed_distance_to_slope': distance(bottom, (-3, -1.2), (2.9, 1.6)),
        'expected_bottom_distance': 0,
    }
checks['7.4_slope_ratio_B_after_before'] = ((3.8-2.2)/(5.5-2.45))/(2.2/2.45)
checks['7.6_BC_angle_below_horizontal_degrees'] = math.degrees(math.atan2(1.43,1.65))
checks['7.6_required_angle_degrees'] = 60
checks['7.15_center_of_mass_x'] = {
    'problem_diagram': (2*(-1.65)+.45+2.55)/4,
    'solution_diagram': (2*(-1.75)+.35+2.45)/4,
    'marked_value': 0,
}
checks['7.8_specular_target_x'] = {'correct': -.35+2.6*1.85/2.05, 'drawn':1.12}
checks['7.18_contact_radius'] = {'actual':math.hypot(1.04, 1.30), 'required':1.70}
checks['7.7_unconstrained_optimum_counterexample'] = {
    'mu':2, 'g_s0_over_v0_squared':.9,
    'optimum_degrees':math.degrees(math.atan(.5)),
    'range_at_optimum_over_v0_squared_div_g':math.sin(2*math.atan(.5)),
    'range_at_45_degrees_over_v0_squared_div_g':1,
    'post_kick_upward_speed_at_45_over_v0':3/math.sqrt(2)-.9*math.sqrt(2),
}

manifest = json.loads((OUT/'manifest.json').read_text())
source_figures = [
    (48,'3.1',1,1),(50,'3.4',4,6),(51,'3.5',5,8),(51,'3.6',6,10),
    (52,'3.8',8,13),(57,'3.15',15,21),(57,'3.16',16,23),
    (59,'3.18',18,26),(60,'3.21',21,30),(63,'3.26',26,36),
    (81,'4.20',36,53),
]
mapping = []
for source_page, source_number, target_number, figure_index in source_figures:
    f = manifest['figures'][figure_index-1]
    mapping.append({'source_physical_page':source_page,'source_example':source_number,
                    'target_example':f'7.{target_number}','target_pdf_page':f['page'],
                    'figure_evidence':f['file'],
                    'status':'counterpart_present_not_geometry_accepted'})

d = fitz.open(chapter)
m = fitz.open(master)
main_text = '\n'.join(m[i].get_text() for i in range(215,252))
(OUT/'master-ch07-text.txt').write_text(main_text)
for page in (221,223,231,232,234,235,249):
    m[page-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(OUT/f'master-{page}.png')

# Same-page-body comparison excludes running heads/folio. Typography may differ
# even when text is unchanged, so record the evidence, not an equality claim.
raster_comparison = []
for small_page in range(2,39):
    large_page = small_page+214
    clip = fitz.Rect(32,65,563,775)
    a = d[small_page-1].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip)
    b = m[large_page-1].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip)
    raster_comparison.append({'chapter_page':small_page,'master_page':large_page,
                              'body_pixels_identical':a.samples==b.samples})

out = {'geometry_checks':checks,'source_figure_mapping':mapping,
       'example_mapping':[{'source_example':f'3.{n}' if n<=30 else f'4.{n-16}',
                           'target_example':f'7.{n}',
                           'target_pdf_pages':manifest['examples'].get(str(n),[])}
                          for n in range(1,37)],
       'original_duplicate_pairs':[[f'3.{n}',f'3.{n+5}'] for n in range(19,24)],
       'raster_comparison':raster_comparison,
       'protected_sha256':{'chapter':sha(chapter),'master':sha(master),'tex':sha(tex)},
       'limits':'Existence mapping only; not a zero-omission paragraph/formula certificate.'}
(OUT/'geometry-and-source-mapping.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(checks,ensure_ascii=False,indent=2))
print('Identical body raster pages:',sum(r['body_pixels_identical'] for r in raster_comparison),'/37')
print(json.dumps(out['protected_sha256'],indent=2))
