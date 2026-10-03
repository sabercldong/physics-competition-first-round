"""Independent numerical regressions for corrected dynamics, not full acceptance."""
import math
from pathlib import Path
import re
import unittest

BOOK = Path(__file__).resolve().parents[1]


def simpson(f, a, b, steps=4000):
    step = (b-a)/steps
    return step/3*(f(a)+f(b)+4*sum(f(a+j*step) for j in range(1,steps,2))
                   +2*sum(f(a+j*step) for j in range(2,steps,2)))


class DynamicsRegressions(unittest.TestCase):
    def test_rough_cycloid_stops_at_bottom_not_using_smooth_normal(self):
        source = (BOOK/"chapters/ch02-practice.tex").read_text()
        mu = float(re.search(r"\\mu\\approx([0-9.]+)", source)[1])
        self.assertAlmostEqual(mu*mu, math.exp(-math.pi*mu), delta=3e-6)
        integral = simpson(lambda x: math.exp(-2*mu*x)*
                           (math.sin(x)*math.cos(x)-mu*math.cos(x)**2),
                           0,math.pi/2)
        self.assertAlmostEqual(integral,0,delta=2e-6)
        for angle in (.01,.2,.6,1.,1.5):
            w=8*math.exp(2*mu*angle)*simpson(
                lambda x: math.exp(-2*mu*x)*(math.sin(x)*math.cos(x)-mu*math.cos(x)**2),
                angle,math.pi/2)
            self.assertGreater(w,0)

    def test_pulley_detachment_and_second_derivative_constraint(self):
        for angle in (math.pi/6,.7,.9):
            s,c=math.sin(angle),math.cos(angle)
            ell=1/s
            speed2=2*(2-ell)/(1+c*c)
            a=c*(1+speed2*s*s/ell)/(1+c*c)
            tension=a/c
            aa=a*c-speed2*s*s/ell
            self.assertAlmostEqual(1-tension,aa)
            self.assertGreater(1-tension*s,0)
        s=math.sqrt(2/3)
        self.assertAlmostEqual((2-3*s*s)*(s*s-s+2)/(2-s*s)**2,0)

    def test_magnetic_modes_same_handedness_and_opposite_energy_signs(self):
        m,k,qb=2.,3.,8.
        modes=[(-qb+sign*math.sqrt(qb*qb-4*m*k))/(2*m) for sign in (-1,1)]
        self.assertTrue(all(w<0 for w in modes))
        energies=[]
        for w in modes:
            self.assertAlmostEqual(m*w*w+qb*w+k,0)
            energy=(m*w*w-k)/2
            self.assertAlmostEqual(energy,(w+qb/(2*m))*m*w)
            energies.append(energy)
        self.assertLess(energies[0]*energies[1],0)

    def test_uniform_winding_preserves_energy_and_moment(self):
        # Dimensionless r0=v0=m=1, a=.02; analytic solution is evaluated
        # independently in force, material-flow and energy equations.
        a=.02
        tstar=4/(5*a)
        for t in (0.,5.,15.):
            f=1-t/tstar
            r,v=f**.6,f**.2
            rd=-.6/tstar*f**(-.4)
            vd=-.2/tstar*f**(-.8)
            force=v*v/r
            fd=force*(2*vd/v-rd/r)
            alpha=r/force
            alphad=alpha*(rd/r-fd/force)
            self.assertAlmostEqual(rd*v+r*vd,-a*force)
            self.assertAlmostEqual(alphad,-a*v/(r*force))
            self.assertAlmostEqual(v*vd+(fd*r+force*rd)/2+force*a*v/(2*r),0)

    def test_finite_chain_recursion_matches_closed_form(self):
        v=0
        for n in range(1,50):
            v=n/(n+1)*math.sqrt(v*v+2)
            N=n+1
            self.assertAlmostEqual(v*v,(N-1)*(2*N-1)/(3*N))

    def test_frequent_collision_counts_distinguish_wall_events(self):
        for k,expected in ((100,(8,7)),(1000,(25,24))):
            u,V=1.,0.
            block=wall=0
            while u>V:
                u,V=((1-k)*u+2*k*V)/(1+k),(2*u+(k-1)*V)/(1+k)
                block+=1
                self.assertAlmostEqual(u*u+k*V*V,1)
                if u<0:
                    u=-u
                    wall+=1
                else:
                    break
            self.assertEqual((block,wall),expected)

    def test_tikz_geometry_uses_tangencies_and_physical_flight(self):
        log=(BOOK/"build/chapter-02/main.log").read_text()
        values={name:list(map(float,nums.split(","))) for name,nums in
                re.findall(r"R2GEO:([A-Z]+)=([-0-9.,]+)",log)}
        radius,height,angle,ell,bx=values["PULLEY"]
        angle=math.radians(angle)
        px,py=radius*math.sin(angle),height+radius*math.cos(angle)
        self.assertAlmostEqual((px)*(bx-px)+(py-height)*(-py),0,delta=1e-4)
        th,b,ux,uy,flight=values["SIDESTEP"]
        th=math.radians(th)
        # PGF's fixed-point sin/cos and typeout are rounded; 5e-4 cm is
        # five micrometres (<0.06 pixel at 300 dpi), as in Ch1 tests.
        self.assertAlmostEqual(ux*flight,2*b*math.sin(th),delta=5e-4)
        self.assertAlmostEqual(uy*flight-flight*flight/2,0,delta=5e-4)
        self.assertAlmostEqual(-b*math.sin(th)*ux+b*math.cos(th)*uy,0,delta=5e-4)
        self.assertAlmostEqual(6*math.tan(th),math.pi-2*th,delta=1e-4)
        time,xland=values["WEDGE"]
        self.assertAlmostEqual(1.5+.6*time-.5*time*time,0,delta=1e-4)
        self.assertAlmostEqual(.5+.6*time,xland,delta=1e-4)


if __name__=="__main__":
    unittest.main()
