"""Audit-only numerical counterexamples and enlarged PDF evidence."""
from pathlib import Path
import json, math
import fitz

BOOK = Path(__file__).resolve().parent.parent
BASE = BOOK / 'build/review-ch19-ch20-20260920'
manifest = json.loads((BASE / 'manifest.json').read_text())
out = BASE / 'enlargements'
out.mkdir(exist_ok=True)
# Physical pages, with normalized crop coordinates. These are review evidence,
# never illustrations to be inserted into the teaching manuscript.
cases = [
 ('ch19',3,'torsion',(.14,.31,.90,.66)),
 ('ch19',10,'dipole',(.10,.30,.91,.65)),
 ('ch19',11,'quadrupole',(.10,.28,.94,.66)),
 ('ch19',15,'equipotential-gallery',(.11,.40,.93,.78)),
 ('ch19',16,'zero-potential',(.10,.08,.91,.35)),
 ('ch19',16,'ionization',(.10,.67,.92,.97)),
 ('ch19',24,'two-lines',(.11,.06,.96,.45)),
 ('ch19',25,'finite-rod',(.11,.06,.96,.33)),
 ('ch19',27,'rutherford',(.10,.25,.95,.47)),
 ('ch20',3,'conductors',(.13,.31,.94,.59)),
 ('ch20',6,'sphere-image',(.12,.68,.95,.96)),
 ('ch20',17,'uniform-sphere',(.12,.53,.94,.82)),
 ('ch20',19,'edge-field',(.12,.40,.95,.67)),
 ('ch20',20,'coaxial',(.13,.055,.95,.255)),
 ('ch20',23,'dielectric-experiment',(.10,.07,.93,.44)),
 ('ch20',29,'dielectric-sphere',(.12,.56,.96,.81)),
 ('ch20',32,'y-circuit',(.25,.13,.85,.28)),
 ('source',15,'ionization-original',(.07,.025,.92,.235)),
]
for key, n, name, box in cases:
    with fitz.open(manifest[key]['path']) as pdf:
        p = pdf[n-1]
        w, h = p.rect.width, p.rect.height
        clip = fitz.Rect(box[0]*w, box[1]*h, box[2]*w, box[3]*h)
        p.get_pixmap(dpi=300, clip=clip, alpha=False).save(out/f'{key}-p{n:02}-{name}.png')

records = {}
a = 1.55
records['two_lines_equipotential_circles'] = [
 {'center':cx,'radius':r,'required_c2_minus_r2':a*a,'actual':cx*cx-r*r}
 for cx,r in [(2.25,.72),(2.75,1.28),(4,2.48)]
]
records['finite_rod_focal_lengths'] = {
 'required':1.5,'actual':[math.sqrt(A*A-B*B) for A,B in [(2.1,1),(2.8,1.85),(3.55,2.65)]]}
records['zero_potential_distance_ratio'] = {
 'left_circle_point':1.9/1.9,'right_circle_point':4.8/1.0,
 'condition':'distance ratio must be constant everywhere on this circle'}
records['grounded_sphere'] = {
 'radius':1.62,'CP':math.hypot(-.15-1.15,2.05),
 'required_image_distance':1.62**2/5.25,'drawn_image_distance':1.0}
records['coaxial_bottom_arc'] = {
 'side_bottoms':[[-1.45,-1.55],[1.45,-1.55]],
 'arc_start':[0,-1.55],'arc_end':[2.90,-1.55]}
records['rutherford'] = {
 'unused_angle_parameter':[34,20,12],
 'all_drawn_terminal_angles_degrees':math.degrees(math.atan2(.75,1.7)),
 'reason':'Every curve is a vertical translation; the ang loop variable is never used.'}
records['uniform_sphere_top_fieldline'] = {
 'endpoint_radius':math.hypot(.9,1.02),'sphere_radius':1.35,
 'angle_from_normal_degrees':abs(math.degrees(math.atan2(1.02,.9)-math.atan2(.68,1.1)))}
records['dielectric_sphere_join'] = {
 'radius':1.45,
 'drawn_join_radii':[math.hypot(1.32,.72*y) for y in [0,.5,1]],
 'problem':'The drawn inside/outside joins do not lie on the spherical boundary.'}
(BASE/'geometry-counterexamples.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps(records,ensure_ascii=False,indent=2))
