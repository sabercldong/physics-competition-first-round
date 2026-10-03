"""Render technical figures and compute independent geometry diagnostics."""
import json,math,hashlib
from pathlib import Path
import fitz,numpy as np
BOOK=Path(__file__).resolve().parent.parent;BASE=BOOK/'build/review-ch17-ch18-20260919';ROOT=BOOK.parents[2]
out=BASE/'details';out.mkdir(exist_ok=True)
clips={'ch17':[(2,475,655),(4,270,465),(5,55,192),(5,340,504),(6,175,360),(7,155,285),(7,575,775),(9,320,468),(10,460,625),(11,310,470),(13,585,735)],
 'ch18':[(3,270,413),(4,653,746),(6,55,188),(7,195,302),(7,650,780)]}
records=[]
for ch,items in clips.items():
 p=next((ROOT/'output/pdf').glob('*第'+ch[2:]+'章*'));d=fitz.open(p)
 for k,(pg,y0,y1) in enumerate(items,1):
  dest=out/f'{ch}-{k:02}.png';d[pg-1].get_pixmap(dpi=330,clip=fitz.Rect(45,y0,552,y1),alpha=False).save(dest)
  records.append({'chapter':ch,'page':pg,'clip':[45,y0,552,y1],'path':str(dest),'pdf_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(BASE/'detail-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
def curve(points):
 t=np.linspace(0,1,10001)[:,None];p=np.array(points);return (1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]
def area(segments,y):
 return sum(np.trapz(c[:,1]-y,c[:,0]) for c in map(curve,segments))
M=(2.1,2.65);A=(3.15,1.78);P=(4.23,2.65);B=(5.18,3.35);N=(6.55,2.65)
s1=-area([[M,(2.45,2.25),(2.75,1.85),A],[A,(3.55,1.65),(3.85,2.25),P]],2.65)
s2=area([[P,(4.55,2.98),(4.82,3.35),B],[B,(5.62,3.42),(6.05,2.9),N]],2.65)
cooker=curve([(3.65,1.05),(4.55,1.78),(5.2,3.15),(5.75,4.75)])
cloud1=curve([(.5,.18),(2.3,.42),(3.65,1.7),(5.15,4.75)])
cloud2=curve([(.5,.55),(2.2,1.05),(3.8,2.35),(5.15,4.15)])
diag={'maxwell_equal_area':{'S1':s1,'S2':s2,'ratio_S2_S1':s2/s1},
 'critical_marked_tangent_slopes':{'fig17_2':-.05/1.35,'fig17_3a':-.03/.75},
 'bypass_route':{'P':[.9,1.15],'M_on_coexistence':[2.35,1.72],'Q':[4.1,2.72],'critical':[4.15,3.85],'maximum_route_T_less_than_Tc':True},
 'cooker':{'pstar_drawing_y':3.38,'saturation_curve_y_at_marked_120C':float(np.interp(5.35,cooker[:,0],cooker[:,1]))},
 'cloud_at_marked_x_4_45':{'marker_y':3.35,'saturation_y':float(np.interp(4.45,cloud1[:,0],cloud1[:,1])),'actual_y':float(np.interp(4.45,cloud2[:,0],cloud2[:,1]))},
 'maxwell_speed_integrals_to_infinity':[2.3*math.sqrt(math.pi)/4,.82*math.sqrt(math.pi)/(4*.45**1.5)],
 'population_first_five_sum':sum([.95,.57,.34,.20,.12]),
 'energy_gaussian':{'sigma':1.15/math.sqrt(2),'correct_two_sigma':2*1.15/math.sqrt(2),'drawn_two_sigma':2.3,'integral_over_real_line':1.15*math.sqrt(math.pi)},
 'mixing_counts':{'before':[5,6],'after':[7,7]},
 'source_sha256':{ch:hashlib.sha256((BOOK/f'generated/chapters/{ch}.tex').read_bytes()).hexdigest() for ch in clips}}
(BASE/'geometry-diagnostics.json').write_text(json.dumps(diag,ensure_ascii=False,indent=2));print(json.dumps(diag,ensure_ascii=False,indent=2))
