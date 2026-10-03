"""Reproducible diagnostics only. No student-source or PDF modifications."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import fitz

BOOK = Path(__file__).resolve().parent.parent
ROOT = BOOK.parents[2]
OUT = BOOK / 'build/review-ch09-20260909'
manifest = json.loads((OUT / 'manifest.json').read_text())
pdf = Path(manifest['current']['path'])
tex = (BOOK / 'generated/chapters/ch09.tex').read_text()
result = {}

# Normalize v0^2/g to one. These are algebraic consistency tests, not fits.
theta = math.pi / 6
r_correct = math.tan(theta)
r_written = 1 / math.tan(theta)
result['funnel'] = {
    'normalization': 'v0^2/g = 1',
    'r_correct': r_correct, 'r_written': r_written,
    'wrong_over_correct': r_written / r_correct,
    'correct_h0': 1, 'written_h0': 3,
    'turning_points': [],
}
for k in [1, 2, .5]:
    x = (k*k + k*math.sqrt(k*k+8)) / 4
    old_x = (k*k + k*math.sqrt(k*k+24)) / 12
    result['funnel']['turning_points'].append({
        'k': k, 'correct_other_positive_x': x,
        'written_other_positive_x': old_x,
        'energy_residual_correct': .5*k*k + 1 - (.5*k*k/(x*x) + x),
        'energy_residual_written': .5*k*k + 1 - (.5*k*k/(old_x*old_x) + old_x),
    })
assert abs(r_written/r_correct - 3) < 1e-12
assert all(abs(t['energy_residual_correct']) < 1e-12 for t in result['funnel']['turning_points'])

x = Q(1,2)
s = 1-x
shear = (1-x)*(1-3*x)/4
ic = s**3/12
first = shear*s/2 - ic*Q(3,2)
second = x*(1-x)**2/4
result['chimney'] = {
    'normalization': 'm=g=L=sin(theta)=1, x=L/2',
    'Q': str(shear), 'first_line_of_M': str(first),
    'claimed_equal_second_line': str(second),
    'equal': first == second, 'same_magnitude': abs(first) == abs(second),
}
assert first == -second and first != second

def angle(a, b):
    return (math.degrees(math.atan2(b[1], b[0])) -
            math.degrees(math.atan2(a[1], a[0]))) % 360

result['geometry'] = {
    'funnel_drawn_theta_degrees': angle((0,4.35), (1.52,2.64)),
    'torque_work_drawn_theta_degrees': angle((4.7,0), (4.4,-2.45)),
    'particle_drawn_phi_degrees': angle((-3.4,-1.55),(2.2,0)),
    'particle_vector_angle_degrees': math.degrees(math.atan2(1.55,3.4)),
    'two_wheels_contact_x_expected': 1.8,
    'two_wheels_contact_x_drawn': 1.73,
    'bounce_gap_over_radius': .35,
    'kepler_radius_endpoint_x_expected': 4.18,
    'kepler_radius_endpoint_x_drawn': 1.9,
    'egg_contact': [],
}
dx, dy = 8.4,-3.45
norm = math.hypot(dx,dy)
n = (-dy/norm,dx/norm)
phi = math.radians(-22)
u = (math.cos(phi),math.sin(phi))
v = (-math.sin(phi),math.cos(phi))
normal_radius = math.sqrt((.58*(n[0]*u[0]+n[1]*u[1]))**2 +
                          (.78*(n[0]*v[0]+n[1]*v[1]))**2)
for c in [(1.55,2.72),(4.55,1.48)]:
    distance = n[0]*(c[0]+.7)+n[1]*(c[1]-3.45)
    result['geometry']['egg_contact'].append({
        'center': c, 'center_distance_from_ramp': distance,
        'ellipse_support_radius_normal_to_ramp': normal_radius,
        'penetration_depth': normal_radius-distance,
    })

# The CM positions and visual comparison depend on the actual PDF, not logs.
bound_path = ROOT/'output/pdf/高中物理竞赛一轮讲义.pdf'
bound = fitz.open(bound_path)
independent = fitz.open(pdf)
start = next(t[2] for t in bound.get_toc() if t[0] == 1 and t[1] == '角动量与刚体动力学')
comparisons=[]
for i in range(1,len(independent)):
    a = independent[i]
    b = bound[start+i-2]
    def interior(p):
        r=p.rect
        # Omit changing running headers/folios only.
        clip=fitz.Rect(r.x0,r.height*.095,r.x1,r.height*.925)
        return p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=clip,alpha=False)
    ap,bp=interior(a),interior(b)
    comparisons.append({'independent_page':i+1,'bound_page':start+i-1,
                        'interior_pixels_identical':ap.width==bp.width and ap.height==bp.height and ap.samples==bp.samples})
result['bound_regression']={
    'path':str(bound_path),'sha256':hashlib.sha256(bound_path.read_bytes()).hexdigest(),
    'pages':len(bound),'chapter_start':start,'chapter_end':start+len(independent)-2,
    'comparisons':comparisons,
    'all_interiors_identical':all(x['interior_pixels_identical'] for x in comparisons),
}
labels=re.findall(r'\\label\{([^}]+)\}',tex)
refs=re.findall(r'\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}',tex)
result['static']={
    'duplicate_labels':{k:v for k,v in Counter(labels).items() if v>1},
    'unknown_explicit_reference_keys':sorted(set(refs)-set(labels)),
    'example_labels':re.findall(r'\\label\{(ch09:ex:[^}]+)\}',tex),
    'white_fill_occurrences':len(re.findall(r'fill\s*=\s*white',tex)),
    'note':'Static keys do not detect handwritten wrong references or prove figure completeness.',
}
for name,command in [('qpdf',['qpdf','--check',str(pdf)]),('pdffonts',['pdffonts',str(pdf)])]:
    process=subprocess.run(command,text=True,capture_output=True)
    (OUT/f'{name}.txt').write_text(process.stdout+process.stderr)
    result[name+'_exit_code']=process.returncode
result['current_source_unchanged'] = hashlib.sha256(tex.encode()).hexdigest()==manifest['generated_source_sha256']
result['current_pdf_unchanged'] = hashlib.sha256(pdf.read_bytes()).hexdigest()==manifest['current']['sha256']
(OUT/'physics-and-structure-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['bound_regression','static']},ensure_ascii=False,indent=2))
print('Bound page interiors identical:',result['bound_regression']['all_interiors_identical'])
print('Static:',result['static'])
