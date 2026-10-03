"""Numerical evidence for the 2026-09-23 review; does not edit book content."""
import json, math, re
from pathlib import Path
from scipy.optimize import brentq

book = Path(__file__).resolve().parents[1]
out = book / 'build/review-ch31-ch32-20260923'
z = brentq(lambda x: 5*(1-math.exp(-x))-x, 4, 6)
beta_a = (3.45-1.25)/4.4
beta_b = (2.75-4.95)/4.4
meet_ct = (4.95-1.25)/(beta_a-beta_b)
data = {
    'fig31.4': {
        'end_A_dx_dct': beta_a, 'end_B_dx_dct': beta_b,
        'end_worldline_intersection_ct': meet_ct,
        'end_worldline_intersection_x': 1.25+beta_a*meet_ct,
        'drawn_left_light_dx_dct': -.01/4.4,
        'drawn_simultaneous_line_dct_dx': (2.68-.8)/(4.6-.35),
        'P_x_minus_right_light_x': 2.35-2.2,
    },
    'fig32.1': {
        'peak_dimensionless_root': z,
        'actual_hot_peak_x': 3/z, 'actual_cold_peak_x': 4.4/z,
        'drawn_guides_x': [.88, 1.29],
        'actual_area_ratio_full_domain': (7/3.2)*(4.4/3)**4,
        'physical_T4_ratio': (4.4/3)**4,
    },
    'ex31.2_distance_km': .98*299792458*2.2e-6/math.sqrt(1-.98**2)/1000,
    'ex31.8_exothermic_counterexample_units_mc2': (1.5**2-(1+1)**2)/2,
    'ex32.7_photon_energy_loss_keV': 1.23984/.0710-1.23984/(.0710+.002426),
    'ex32.8_Bragg_angle_degrees': math.degrees(math.asin(1.227/math.sqrt(54)/.4)),
    'ex32.11_Q_MeV': (2.014102+3.016049-4.002603-1.008665)*931.5,
    'source_counts': {},
}
for n, name in [(31, 'ch31-relativity.tex'), (32, 'ch32-modern.tex')]:
    t = (book/'chapters/new'/name).read_text()
    labels = re.findall(r'\\label\{([^}]+)\}', t)
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', t)
    data['source_counts'][str(n)] = {
        'examples': t.count(r'\begin{origexamplebox}'),
        'solution_blocks': t.count(r'\begin{xesolution}'),
        'duplicate_local_labels': sorted({x for x in labels if labels.count(x)>1}),
        'unresolved_local_refs': sorted(set(refs)-set(labels)),
    }
(out/'numerical-checks.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
print(json.dumps(data, ensure_ascii=False, indent=2))
