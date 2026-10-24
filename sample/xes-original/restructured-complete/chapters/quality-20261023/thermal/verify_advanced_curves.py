"""Independent high-precision checks of the quantitative added curves."""
from pathlib import Path
import csv
import json
import re
import mpmath as mp

mp.mp.dps = 35
folder = Path(__file__).resolve().parent
source = (folder / "A2-statistics.tex").read_text()
curve = re.search(r"plot coordinates\{(\(1\.500000,1\.92567168\).*?)\};", source).group(1)
points = [(mp.mpf(x)/mp.mpf("1.5"), mp.mpf(y))
          for x, y in re.findall(r"\(([\d.]+),([\d.]+)\)", curve)]
rows = []
for t, plotted in points:
    if t == 1:
        exact = mp.mpf(15)/4*mp.zeta(mp.mpf(5)/2)/mp.zeta(mp.mpf(3)/2)
        z = mp.mpf(1)
    else:
        target = mp.zeta(mp.mpf(3)/2)/t**mp.mpf("1.5")
        lower, upper = mp.mpf(0), mp.mpf(20)
        for _ in range(90):
            middle = (lower+upper)/2
            if mp.polylog(mp.mpf(3)/2, mp.exp(-middle)) > target:
                lower = middle
            else:
                upper = middle
        z = mp.exp(-(lower+upper)/2)
        g = lambda s: mp.polylog(s, z)
        exact = mp.mpf(15)/4*g(mp.mpf(5)/2)/g(mp.mpf(3)/2)-mp.mpf(9)/4*g(mp.mpf(3)/2)/g(mp.mpf(1)/2)
    rows.append([float(t), float(z), float(exact), float(plotted), float(abs(exact-plotted))])
error = max(row[-1] for row in rows)
assert error < 6e-9
assert all(rows[i+1][2] < rows[i][2] for i in range(len(rows)-1))
with (folder / "bec-curve-verification.csv").open("w") as stream:
    writer = csv.writer(stream)
    writer.writerow(["T/Tc", "z", "Cv/(Nk) exact", "Cv/(Nk) plotted", "absolute error"])
    writer.writerows(rows)

heat_areas = [mp.quad(lambda x: mp.exp(-x*x)/mp.sqrt(mp.pi), [-mp.inf, mp.inf]),
              mp.quad(lambda x: mp.exp(-x*x/4)/(2*mp.sqrt(mp.pi)), [-mp.inf, mp.inf])]
parseval_norms = [mp.quad(lambda x: mp.exp(-x*x/4), [-mp.inf, mp.inf]),
                  mp.quad(lambda k: 4*mp.exp(-4*k*k), [-mp.inf, mp.inf])]
assert max(abs(area-1) for area in heat_areas) < mp.mpf("1e-30")
assert abs(parseval_norms[0]-parseval_norms[1]) < mp.mpf("1e-30")
checks = {
    "bec-sample-max-absolute-error": error,
    "bec-critical-Cv-per-Nk": rows[0][2],
    "bec-upper-branch-strictly-decreasing": True,
    "heat-kernel-two-areas": [float(area) for area in heat_areas],
    "parseval-gaussian-two-squared-norms": [float(area) for area in parseval_norms],
    "landau-three-minima-factorization": "c phi^2 (phi^2 - b/(2c))^2, b,c>0",
}
(folder / "advanced-curve-checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2)+"\n")
print(json.dumps(checks, ensure_ascii=False, indent=2))
