"""Bounded counterexamples for the 2026-09-23 audit; never edits delivery files."""
from pathlib import Path
import hashlib
import json
import math
import re

BOOK = Path(__file__).resolve().parents[1]
OUT = BOOK / 'build/review-ch29-ch30-20260923'
manifest = json.loads((OUT / 'inspection-manifest.json').read_text())
evidence = {}

# A symmetric closed overlap interval, measured in fringe spacings.
D = 3.4
centres = [m for m in range(-10, 11) if abs(m) <= D / 2]
assert len(centres) == 3 and math.floor(D) + 1 == 4
evidence['billet'] = {'D_over_spacing': D, 'centres': centres,
                      'actual_count': len(centres), 'printed_formula_count': math.floor(D)+1}

# Dimensionless example b=lambda=tan(theta)=1, thickness bound h=6.
# Equal spacing sqrt(2) samples orders 0,1,4,9,16, all in the allowed wedge.
positions = [j*math.sqrt(2) for j in range(5)]
orders = [y*y/2 for y in positions]
assert all(abs(m-round(m)) < 1e-12 for m in orders)
assert max(positions) <= 6
evidence['wedge_equal_spacing_counterexample'] = {'positions': positions, 'orders': orders}

L, y, d = 10., .2, .1
r1, r2 = math.hypot(L, y-d/2), math.hypot(L, y+d/2)
assert r2-r1 > 0
evidence['young_sign'] = {'r1_minus_r2': r1-r2, 'positive_yd_over_L': y*d/L}

# Source-code coordinates in the current ch29 drawing.
ray_y_at_virtual_source = .45 + (-1.15-.45)/(4+.3)*(-4+.3)
evidence['biprism_collinearity'] = {
    'extrapolated_y_at_x_minus4': ray_y_at_virtual_source,
    'drawn_virtual_source_y': .7, 'vertical_residual': ray_y_at_virtual_source-.7}
assert abs(ray_y_at_virtual_source-.7) > 1

# Vertical splitter rotated +45 degrees has normal (1,1)/sqrt(2).
v, n = (1., 0.), (2**-.5, 2**-.5)
dot = sum(a*b for a,b in zip(v,n))
reflected = [v[i]-2*dot*n[i] for i in range(2)]
assert reflected[1] < -.99
evidence['michelson'] = {'computed_reflection': reflected, 'drawn_arm_direction': [0,1]}

cy = .9 - 2.6*math.sin(math.radians(220))
bottom = cy - 2.6
evidence['newton_contact'] = {'arc_bottom_y': bottom, 'plane_y': -.7, 'gap': bottom+.7}
assert bottom+.7 > .6

theta_in = math.degrees(math.atan2(1.05,1.7))
theta_out = math.degrees(math.atan2(-1.85,1.15))
evidence['half_wave_plate'] = {'input_angle_deg': theta_in, 'drawn_output_deg': theta_out,
                              'expected_if_x_is_fast_deg': -theta_in}
assert abs(theta_out+theta_in) > 26

radii = [.42,.74,1.02,1.28,1.52]
squares = [r*r for r in radii]
increments = [squares[0]]+[squares[i]-squares[i-1] for i in range(1,len(squares))]
evidence['zone_plate'] = {'radii_squared': squares, 'successive_increments': increments}
assert max(increments)-min(increments) > .49

# Common textbook symmetric Fresnel-mirror setup only: this is not a substitute
# for restoring the source's full geometry and finite aperture boundaries.
R, L, alpha, lam = .1, 2.1, math.radians(20/60), 600e-9
evidence['fresnel_mirror_standard_geometry'] = {
    'printed_spacing_mm': lam*L/(2*R*alpha)*1e3,
    'with_virtual_source_plane_mm': lam*(L+R*math.cos(alpha))/(2*R*math.sin(alpha))*1e3,
    'status': 'conditional on the conventional symmetric placement; rebuild geometry before revising count'}

beam_radius = 3.84e8*1.22*632.8e-9/100e-6
evidence['moon_beam'] = {'radius_m': beam_radius, 'transverse_plane_area_m2': math.pi*beam_radius**2,
                          'moon_mean_radius_m': 1737.4e3,
                          'radius_source': 'https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html'}
assert beam_radius > 1737.4e3

for chapter in (29,30):
    source = BOOK / f'generated/chapters/ch{chapter}.tex'
    content = source.read_text()
    ex = content.count(r'\begin{origexamplebox}')
    sol = content.count(r'\begin{xesolution}')
    assert ex == sol
    key = f'ch{chapter}'
    current = hashlib.sha256(Path(manifest[key]['path']).read_bytes()).hexdigest()
    assert current == manifest[key]['sha256'], 'Formal PDF changed during read-only audit'
    evidence[key] = {'examples': ex, 'solutions': sol, 'pdf_unchanged': True,
                     'tex_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'figure_labels': len(re.findall(r'\\label\{ch\d+:fig:', content))}

target = OUT / 'counterexamples.json'
target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
print(json.dumps(evidence, ensure_ascii=False, indent=2))
