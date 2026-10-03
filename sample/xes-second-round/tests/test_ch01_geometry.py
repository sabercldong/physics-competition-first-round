"""Numerical checks of values emitted by the actual TikZ compilation.

These checks cover selected constraints, not visual or full physics acceptance.
"""
import math
from pathlib import Path
import re
import unittest

BOOK = Path(__file__).resolve().parents[1]


class CompiledGeometry(unittest.TestCase):
    # PGF prints about 4–5 significant decimal digits. Coordinates are cm:
    # 0.0005 cm is 5 micrometres, <0.06 pixel at the 300-dpi review scale.
    # This is a rendering tolerance, not permission to change the geometry.
    coordinate_tolerance = 5e-4
    @classmethod
    def setUpClass(cls):
        log = (BOOK / "build/chapter-01/main.log").read_text(encoding="utf-8")
        cls.values = {name: list(map(float, values.split(","))) for name, values in
                      re.findall(r"R2GEO:([A-Z]+)=([-0-9.,]+)", log)}

    def test_curvature_circle_center_and_radius(self):
        x, y, radius = self.values["FRENET"]
        self.assertAlmostEqual(x, .545, delta=self.coordinate_tolerance)
        self.assertAlmostEqual(y, .55 + 1.09 / .6, delta=self.coordinate_tolerance)
        self.assertAlmostEqual(radius, 1.09 ** 1.5 / .6, delta=self.coordinate_tolerance)
        self.assertAlmostEqual(math.hypot(x, y - .55), radius, delta=self.coordinate_tolerance)
        self.assertAlmostEqual(x - .3 * (y - .55), 0, delta=self.coordinate_tolerance)
        self.assertGreater(y, .55)  # Positive f'' puts the normal above P.

    def test_rotating_frame_is_orthonormal_and_right_handed(self):
        xi, eta, zeta = [self.values[k] for k in ("XI", "ETA", "ZETA")]
        for vector in (xi, eta, zeta):
            self.assertAlmostEqual(sum(x*x for x in vector), 1, delta=5e-5)
        for a, b in ((xi, eta), (eta, zeta), (zeta, xi)):
            self.assertAlmostEqual(sum(x*y for x, y in zip(a, b)), 0, delta=5e-5)
        cross = [xi[1]*eta[2]-xi[2]*eta[1], xi[2]*eta[0]-xi[0]*eta[2], xi[0]*eta[1]-xi[1]*eta[0]]
        for actual, expected in zip(cross, zeta):
            self.assertAlmostEqual(actual, expected, delta=5e-5)

    def test_projectile_lands_on_the_slope(self):
        x, slope, height, launch, bend = self.values["SLOPELAND"]
        self.assertAlmostEqual(height+launch*x-bend*x*x, -slope*x, delta=self.coordinate_tolerance)
        self.assertGreater(x, 0)
        self.assertLess(launch-2*bend*x, -slope)

    def test_negative_plot_parameters_are_not_unparenthesized_powers(self):
        source = (BOOK / "chapters/ch01-diagrams.tex").read_text(encoding="utf-8")
        # Macro expansion of -2.5^2 is not (-2.5)^2 in PGF arithmetic.
        self.assertNotRegex(source, r"\\(?:x|xx|slope)\s*\^")

    def test_cycloid_point_lies_on_the_rolling_circle(self):
        u, x, y = self.values["CYCLOID"]
        self.assertAlmostEqual((x-u)**2+(y-1)**2, 1, delta=self.coordinate_tolerance)
        self.assertAlmostEqual(x, u-math.sin(u), delta=self.coordinate_tolerance)
        self.assertAlmostEqual(y, 1-math.cos(u), delta=self.coordinate_tolerance)
        self.assertGreater(y, 0)
        self.assertLess(x, u)


if __name__ == "__main__":
    unittest.main()
