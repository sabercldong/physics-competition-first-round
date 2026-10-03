"""Read-only audit: render evidence, compare editions and test graph geometry."""
from pathlib import Path
import difflib
import json
import math
import re
import fitz

BOOK = Path(__file__).resolve().parent.parent
BASE = BOOK / 'build/review-ch15-ch16-20260915'
manifest = json.loads((BASE / 'manifest.json').read_text())
out = BASE / 'details'
out.mkdir(exist_ok=True)
regions = {
    'ch15': [(2,160,730), (4,60,740), (5,350,730), (6,60,400),
             (7,490,710), (8,295,405), (9,140,345), (10,70,720),
             (11,285,440), (12,365,535), (13,465,675), (15,410,660),
             (16,335,535), (17,260,455), (19,60,470), (20,440,625),
             (21,65,230), (21,610,758), (22,240,490)],
    'ch16': [(3,60,255), (4,75,300), (5,90,280), (5,530,745),
             (7,345,510), (7,580,770), (9,60,250), (9,565,680),
             (10,645,785), (11,340,475), (12,455,640)]}
index = []
for key, areas in regions.items():
    doc = fitz.open(manifest['files'][key]['path'])
    for page, y0, y1 in areas:
        name = f'{key}-p{page:02}-{y0}.png'
        clip = fitz.Rect(45, y0, 551, y1)
        doc[page-1].get_pixmap(dpi=330, clip=clip, alpha=False).save(out/name)
        index.append({'file':name,'chapter':key,'physical_page':page,
                      'printed_page':page-1,'clip_points':list(clip)})
(out/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))

master = fitz.open(manifest['files']['main']['path'])
diffs = {}
for key in ('ch15', 'ch16'):
    chapter = fitz.open(manifest['files'][key]['path'])
    first = manifest['chapters'][key]['master_physical_pages'][0]-1
    changes = []
    for j in range(1,len(chapter)):
        a = chapter[j].get_text(clip=fitz.Rect(42,51,552,780))
        b = master[first+j-1].get_text(clip=fitz.Rect(42,51,552,780))
        aa = re.sub(r'\s+','',a)
        bb = re.sub(r'\s+','',b)
        if aa != bb:
            hunks = []
            for tag,i1,i2,j1,j2 in difflib.SequenceMatcher(None,aa,bb,autojunk=False).get_opcodes():
                if tag!='equal':
                    hunks.append({'op':tag,'standalone':aa[max(0,i1-35):i2+35],
                                  'master':bb[max(0,j1-35):j2+35]})
            changes.append({'printed_page':j,'physical_page':j+1,'changes':hunks})
        if j in manifest['chapters'][key]['master_body_raster_diff_pages']:
            master[first+j-1].get_pixmap(dpi=220,alpha=False).save(out/f'master-{key}-body{j:02}.png')
    diffs[key] = changes
(BASE/'edition-differences.json').write_text(json.dumps(diffs,ensure_ascii=False,indent=2))

def bezier(points,t):
    w = ((1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3)
    return [sum(ww*p[k] for ww,p in zip(w,points)) for k in (0,1)]

cvpoints = [(5,1.05),(3.4,1.3),(1.8,2.35),(1.25,4.2)]
mid = bezier(cvpoints,.5)
entropy_points = [(1,3.55),(2,2.95),(3,1.70),(4.25,.85)]
emid = bezier(entropy_points,.5)
checks = {
    'carnot16_endpoint_PV': {'1':1.35*4,'2':4.35*2.48,'3':5.55*1.10,'4':2.05*1.70},
    'carnot16_background_curve_power':-.43,
    'carnot15_adiabatic_expansion_deltaV':2.1-3,
    'brayton15_isobar_deltaP':[2.35-3.05,1.2-.75],
    'otto15_compression_endpoint_tangent':{'dV_dt':3*(.85-1.45),'dP_dt':3*(.8-1)},
    'cycle15_9':{'endpoint_PV':5.25,'midpoint':mid,'midpoint_PV':mid[0]*mid[1],
                  'relative_error':mid[0]*mid[1]/5.25-1},
    'entropy16_isotherm':{'start_PV':3.55,'end_PV':4.25*.85,'midpoint':emid,
                         'midpoint_PV':emid[0]*emid[1]},
    'capillary15_meniscus':{'wall_y':1.35,'center_y':1.35+.24,
                           'center_minus_wall':.24,'required_for_wetting':'center lower than wall'},
    'otto16_connecting_rod_lengths': [math.hypot(.52*math.cos(math.radians(a)),
                      y+1.78-.52*math.sin(math.radians(a)))
                     for y,a in ((.05,220),(.52,300),(.72,80),(-.10,155),(.18,235))],
    'three_bodies16_4':{'temperatures':[400,150,150], 'energy_sum':700,
                       'product':400*150*150,'initial_product':300*300*100,
                       'bound':'For X >= 700/3, X*(700-X)^2/4 is decreasing; >= 9e6 implies X <= 400.'},
}
(BASE/'geometry-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print(json.dumps({'edition_differences':diffs,'geometry':checks},ensure_ascii=False,indent=2))
