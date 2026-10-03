"""Read-only numerical checks supporting the 2026-09-12 chapter audit.

These diagnostics do not certify acceptance or rebuild/publish teaching PDFs.
"""
from pathlib import Path
import hashlib
import json
import math
import re

import fitz
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build/review-ch13-ch14-20260912"
meta = json.loads((OUT / "manifest.json").read_text())
results = {"purpose": "audit evidence, not acceptance", "checks": {}}
c = results["checks"]

# All three diagrams use q=r/r0 and U=A(q^-12-2q^-6).
potentials = []
for name, amplitude, energy, drawn in [
    ("figure14.4", 1.30, -.48, [.79, 1.63]),
    ("unnumbered thermal-expansion diagram", 1.15, -.42, [.82, 1.47]),
    ("example14.11 amplitude diagram", 1.25, -.45, [.75, 1.55]),
]:
    roots = [(1 + math.sqrt(1 + energy / amplitude)) ** (-1 / 6),
             (1 - math.sqrt(1 + energy / amplitude)) ** (-1 / 6)]
    potentials.append({"diagram": name, "energy_level": energy,
                       "correct_turning_points": roots, "drawn_x": drawn,
                       "U_at_drawn_x": [amplitude * (q**-12 - 2*q**-6) for q in drawn]})
c["potential_endpoints"] = potentials
c["elastic_wall_reflection_slopes"] = {
    "figure14.7_incident": (2.05-.40)/(3.55-.20),
    "figure14.7_reflected": (3.20-2.05)/(3.55-.40),
    "supplement_incident": (2.50-1.25)/(4-1.25),
    "supplement_reflected": (3.15-2.50)/(4-2),
    "supplement_reflected_endpoint_y": 3.15, "container_top_y": 3.0,
    "supplement_collision_y": 2.5, "marked_patch_max_y": 2.45,
}
c["ch13_streamlines"] = {"upper_shared_point": [0, 1.55],
                           "upper_curves_through_point": 3,
                           "lower_shared_point": [0, -1.55],
                           "lower_curves_through_point": 3}
g, l1, l2 = 9.8, .32, .60
freqs = {}
for gamma in [1.4, 1.0]:
    K = g*np.array([[1+gamma, gamma], [gamma, 1+gamma]])
    w2 = np.linalg.eigvals(np.diag([1/l1, 1/l2]) @ K)
    w = np.sqrt(np.sort(w2))
    freqs[str(gamma)] = {"omega_rad_s": w.tolist(), "f_Hz": (w/(2*math.pi)).tolist()}
c["example13.9_frequencies"] = freqs

# Independent finite-difference check of the printed Couette radial integral.
R1, R2, rho, C = 1., 2.5, 1.7, .37
def p(r):
    return rho*C*C*((r*r-R1*R1)/2 - 2*R2*R2*math.log(r/R1)
                    - R2**4/2*(1/r**2-1/R1**2))
errors = []
for r in np.linspace(1.1, 2.4, 10):
    dp = (p(r+1e-5)-p(r-1e-5))/2e-5
    expected = rho*(C*(R2*R2/r-r))**2/r
    errors.append(abs(dp-expected))
c["example13.10_radial_pressure_max_abs_derivative_error"] = max(errors)
c["example13.10_missing_condition"] = "p(r) is at fixed z, or gravity must be explicitly neglected; vertical cylinders also have dp/dz=-rho*g."
theta = math.atan(1/3) + math.asin((4*1000*.0003*1.5/(.26*10))/math.sqrt(10))
c["example13.14_angle"] = {"solution_degrees": math.degrees(theta),
                            "drawn_degrees": math.degrees(math.atan(.95/2.25)),
                            "orthogonal_pipe_vectors_dot": (-.95)*2.25+(-2.25)*(-.95)}
c["chapter14_results"] = {"ex14.5_pressure_cmHg": 72+2*8/10,
                           "ex14.6_T_leaves_B_K": 297/.9,
                           "ex14.6_T_reaches_A_K": 297/.9*1.1,
                           "ex14.6_final_p_over_p0": 399.3/(297/.9*1.1),
                           "ex14.7_initial_T_K": 60/(1.8/1.5-1),
                           "ex14.7_final_T_K": 60/(1.8/1.5-1)*1.8,
                           "ex14.8_remaining_Hg_at_max_cm": (100-76)/2,
                           "ex14.8_max_T_K_using_T0_300": 300*(76+12)*(100-12)/((76+20)*50),
                           "ex14.11_alpha_midpoint_in_kB_over_epsilon": 7/72,
                           "ex14.11_alpha_statistical_in_kB_over_epsilon": 7/48}
c["argon_ideal_density_g_per_L"] = {str(T): 101325*.039948/(8.314462618*T) for T in [273.15, 298.15]}

# The L-tube last-stage clipping formula is algebraically sound for its stated model.
maxerr = 0.
for a,b,cc,d,b0 in [(1,2,3,4,8), (5,1,3,2,.1), (10,2,3,2,1), (.5,1,2,1,10)]:
    xstar = (b0+cc+d-a)/2
    xhat = min(cc+d, max(cc+d-b, xstar))
    xs = np.linspace(0,cc+d,30001)
    hs = np.where(xs<cc-b,0,np.where(xs<cc,xs+b-cc,np.where(xs<cc+d-b,b,cc+d-xs)))
    ts = (b0+hs)*(a+xs)/(b0*a)
    exact = (b0+cc+d-xhat)*(a+xhat)/(b0*a)
    maxerr = max(maxerr, abs(float(ts.max())-exact))
c["example14.10_clipped_max_vs_dense_sampling_abs_error"] = maxerr

unchanged = {}
for path, old_hash in meta["teaching_source_hashes"].items():
    unchanged[path] = hashlib.sha256(Path(path).read_bytes()).hexdigest() == old_hash
for key in ["ch13", "ch14", "main"]:
    obj = meta["files"][key]
    unchanged[obj["path"]] = hashlib.sha256(Path(obj["path"]).read_bytes()).hexdigest() == obj["sha256"]
for key in ["ch13", "ch14"]:
    path = ROOT / f"generated/chapters/{key}.tex"
    unchanged[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest() == meta["chapters"][key]["source_sha256"]
results["scope_files_unchanged"] = unchanged
assert all(unchanged.values()), "Audit must not modify teaching source or formal PDFs"
results["visual_review"] = {
    "method": "human inspection of rendered pages/contact sheets and 330-dpi detail crops; not automated certification",
    "current_pages_inspected": {"ch13": list(range(1,15)), "ch14": list(range(1,24))},
    "source_teaching_pages_inspected_full_size": {"kinematics": list(range(78,82)), "notes": list(range(123,129)), "exercises": list(range(53,57)), "thermal": list(range(5,18))},
    "detail_crops_inspected": [x["id"] for x in json.loads((OUT/"detail-manifest.json").read_text())],
    "limitation": "Findings recorded; existing accepted/locked statuses are not renewed. This is not a zero-omission certification.",
}
(OUT / "physics-and-scope-checks.json").write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(c,ensure_ascii=False,indent=2))
print("Teaching sources and formal PDFs unchanged:", all(unchanged.values()))
