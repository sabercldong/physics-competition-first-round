"""Geometry regressions for Chapter 3 high-risk technical figures."""
import math
from pathlib import Path
import re
import unittest

BOOK = Path(__file__).resolve().parents[1]


class StaticsRegressions(unittest.TestCase):
    def _geometry_values(self):
        log = (BOOK / "build/chapter-03/main.log").read_text(encoding="utf-8")
        return {name: list(map(float, nums.split(",")))
                for name, nums in re.findall(r"R2GEO:([A-Z0-9]+)=([-0-9.,]+)", log)}

    def test_two_cylinders_have_all_three_exact_tangencies(self):
        R, r, wall, ax, ay, bx, by, _ = self._geometry_values()["TWOCYL"]
        self.assertAlmostEqual(ay, R, delta=1e-5)          # A-floor
        self.assertAlmostEqual(wall - ax, R, delta=1e-5)  # A-wall
        self.assertAlmostEqual(wall - bx, r, delta=1e-5)  # B-wall
        self.assertAlmostEqual(math.hypot(bx-ax, by-ay), R+r, delta=1e-4)
        self.assertGreater(by, ay)                         # B is above A

    def test_euler_rotation_is_proper_and_angles_are_not_collapsed(self):
        determinant, psi, theta, phi = self._geometry_values()["EULER3D"]
        self.assertAlmostEqual(determinant, 1.0, delta=1e-8)
        self.assertNotEqual(psi, 0)
        self.assertNotEqual(theta, 0)
        self.assertNotEqual(phi, 0)

    def test_accelerating_box_internal_geometry_and_piecewise_threshold(self):
        ell, ag, xp, yp, xs = self._geometry_values()["BOXTIP"]
        self.assertAlmostEqual(math.hypot(xp, yp-2*ell), ell, delta=1e-4)
        self.assertLess(xp, 0)
        self.assertLess(xs, 0)
        for kappa in (4/3, 2, 10):
            force = 9*kappa/(3*kappa-1)
            self.assertLessEqual(3*kappa/(3*kappa-1), kappa+1e-12)
            self.assertGreaterEqual(force, 3)
        self.assertAlmostEqual(9*(4/3)/(3*(4/3)-1), 4)

    def test_unwinding_cylinder_conserves_energy_and_angular_momentum(self):
        gamma, omega = 3.0, 1.0
        A = gamma + 1
        for x in (0.0, 0.2, 0.7, 1.0):
            xdot = omega
            qdot = -omega*(A-x*x)/(A+x*x)
            energy = A*qdot*qdot + x*x*(xdot-qdot)**2
            momentum = (A+x*x)*qdot-x*x*xdot
            self.assertAlmostEqual(energy, A*omega*omega, delta=1e-12)
            self.assertAlmostEqual(momentum, -A*omega, delta=1e-12)
        X = 1.0
        self.assertAlmostEqual(gamma, X*X+2*X)
        # Independent Simpson evaluation of the stated X=1 time integral.
        n = 10000
        f = lambda th: math.sqrt(
            X*((X+1)**2-math.cos(th)**2)/((X+1)**2*(X+2*math.cos(th))))
        h = (math.pi/2)/n
        integral = h/3*(f(0)+f(math.pi/2)
                        +4*sum(f((2*k-1)*h) for k in range(1,n//2+1))
                        +2*sum(f(2*k*h) for k in range(1,n//2)))
        self.assertAlmostEqual(integral, 1.01494743, delta=2e-8)

    def test_fire_hose_energy_force_and_gravity_free_limit(self):
        gR, L, mass = 3.2, 7.0, 2.3
        for v0 in (0.0, 1.7, 8.0):
            for u in (1.0, 0.63, 0.15):
                speed2 = (v0*v0 + 4*gR*(1-u**1.5)/3)/u
                initial_energy = .75*mass*v0*v0 + mass*gR
                energy = .75*mass*u*speed2 + mass*gR*u**1.5
                self.assertAlmostEqual(energy, initial_energy, delta=1e-12)
                force = mass/L*((v0*v0+4*gR/3)/(2*u)-5*gR*math.sqrt(u)/3)
                # Differentiate P=M*u*v with du/dt=-v/L independently.
                derivative = -(v0*v0+4*gR/3)/u**2-(2*gR/3)/math.sqrt(u)
                momentum_rate = mass/L*(-speed2-u*derivative/2)
                self.assertAlmostEqual(momentum_rate, -force, delta=1e-12)
        large_lambda = 1000.0
        dimensionless_time = math.sqrt(large_lambda**2+4/3)-large_lambda
        self.assertAlmostEqual(dimensionless_time, 2/(3*large_lambda), delta=1e-9)

    def test_farm_cart_impact_and_two_stage_stopping(self):
        """Independently check the coefficients used in practice 3.6."""
        mass, g, ell, radius = 1.0, 9.8, 3.0, 0.4
        phi = math.asin(2*radius/(3*ell))
        inertia_frame = 4*mass*ell**2/3
        omega_before = math.sqrt(g*radius)/ell
        omega_locked = inertia_frame/(inertia_frame+2*mass*radius**2)*omega_before
        # Initial horizontal momentum comes only from the two handle centres.
        px_before = mass*ell*omega_locked*math.sin(phi)
        self.assertAlmostEqual(px_before, 2*mass*radius*omega_locked/3)
        mu = math.tan(phi)/3
        vertical_impulse = mass*ell*omega_locked*math.cos(phi)
        v0 = (px_before-mu*vertical_impulse)/(6*mass)
        stated_v0 = omega_locked*(radius/9-mu*ell*math.cos(phi)/6)
        self.assertAlmostEqual(v0, stated_v0)
        # Slip stage: V=V0-mu*g*t and r*omega=(8/3)mu*g*t.
        t1 = 3*v0/(11*mu*g)
        v1 = v0-mu*g*t1
        self.assertAlmostEqual(v1, 8*v0/11)
        x1 = v0*t1-mu*g*t1*t1/2
        x2 = v1*v1/(2*(mu*g/12))
        self.assertAlmostEqual(x1+x2, 825*v0*v0/(242*mu*g))

    def test_cone_stability_threshold_has_the_correct_geometry(self):
        h, alpha = 2.0, math.radians(30)
        r_critical = .75*h*math.tan(alpha)
        self.assertAlmostEqual(r_critical/math.tan(alpha), .75*h)
        self.assertLess(r_critical, h*math.tan(alpha))

    def test_three_photon_region_is_medial_triangle_not_hexagon(self):
        vertices = ((.5, .5, 0), (.5, 0, .5), (0, .5, .5))
        self.assertEqual(len(vertices), 3)
        for point in vertices:
            self.assertAlmostEqual(sum(point), 1)
            self.assertLessEqual(max(point), .5)


if __name__ == "__main__":
    unittest.main()
