"""Independent numerical checks for the new teaching examples (no source edits)."""
import cmath
import json
import math
from pathlib import Path

def integrate(function, a, b, n=10000):
    h = (b - a) / n
    return h / 3 * (function(a) + function(b)
                    + 4 * sum(function(a + h*i) for i in range(1, n, 2))
                    + 2 * sum(function(a + h*i) for i in range(2, n, 2)))

checks = []
def check(name, error, tolerance=1e-9):
    checks.append({"name": name, "error": abs(error), "tolerance": tolerance,
                   "passed": abs(error) < tolerance})

# The analyzer acts on each incoherent component before averaging its intensity.
for degrees in [0, 17, 45, 73, 90, 138]:
    t = math.radians(degrees)
    component_sum = .6*math.cos(t)**2 + .2*math.cos(t)**2 + .2*math.sin(t)**2
    check(f"polarizer mixture at {degrees} degrees", component_sum-(.5+.3*math.cos(2*t)))
check("polarization degree from determinant", math.sqrt(1-4*.8*.2)-.6)
for degrees in [0, 30, 60, 90]:
    t = math.radians(degrees)
    amplitude = (math.cos(t)+1j*math.sin(t))/math.sqrt(2)
    check(f"pure circular light is flat under linear analyzer: {degrees}", abs(amplitude)**2-.5)

# Differentiate four-velocity numerically, then transform it to the rest frame.
for speed in [.1, .6, .9]:
    ax, ay, h = .3, .4, 1e-6
    gamma = 1/math.sqrt(1-speed**2)
    def U(t):
        vx, vy = speed+ax*t, ay*t
        g = 1/math.sqrt(1-vx*vx-vy*vy)
        return (g,g*vx,g*vy)
    A = tuple(gamma*(a-b)/(2*h) for a,b in zip(U(h),U(-h)))
    rest = (gamma*(A[0]-speed*A[1]),gamma*(A[1]-speed*A[0]),A[2])
    check(f"four-acceleration orthogonality v={speed}", A[0]-speed*A[1],1e-7)
    check(f"rest longitudinal acceleration v={speed}", rest[1]-gamma**3*ax,1e-7)
    check(f"rest transverse acceleration v={speed}", rest[2]-gamma**2*ay,1e-7)

# Equal superposition in a=1, hbar=1, m=1; check normalization and the local continuity law.
E1, E2 = math.pi**2/2, 2*math.pi**2
def psi(x,t):
    return math.sin(math.pi*x)*cmath.exp(-1j*E1*t)+math.sin(2*math.pi*x)*cmath.exp(-1j*E2*t)
def dxpsi(x,t):
    return math.pi*math.cos(math.pi*x)*cmath.exp(-1j*E1*t)+2*math.pi*math.cos(2*math.pi*x)*cmath.exp(-1j*E2*t)
for phase in [0, .7, math.pi, 4.2]:
    t=phase/(E2-E1)
    check(f"superposition probability phase={phase}", integrate(lambda x:abs(psi(x,t))**2,0,1)-1)
for x in [.13,.37,.72]:
    t,h=.057,1e-6
    dt=(abs(psi(x,t+h))**2-abs(psi(x,t-h))**2)/(2*h)
    def current(y): return (psi(y,t).conjugate()*dxpsi(y,t)).imag
    div=(current(x+h)-current(x-h))/(2*h)
    check(f"probability continuity at x={x}",dt+div,2e-7)

# Independently sum Kelvin images on several physical boundary points.
L,R,V = 2.4,1.,1.
alpha=math.acosh(L/(2*R))
d,q=0.,R*V  # units 4*pi*epsilon_0 = 1
charges=[]
for n in range(90):
    x=d if n%2==0 else L-d
    charges.extend([(x,q),(L-x,q)])
    check(f"image coefficient n={n}",q-(-1)**n*R*V*math.sinh(alpha)/math.sinh((n+1)*alpha))
    d,q=R*R/(L-d),-R*q/(L-d)
for theta in [.1,.5,1.,2.,math.pi]:
    x,y=R*math.cos(theta),R*math.sin(theta)
    potential=sum(q/math.hypot(x-xq,y) for xq,q in charges)
    check(f"two-sphere boundary potential theta={theta}",potential-V)

# Slice the cylinder intersection using the region stated in its new diagram.
split=1/math.sqrt(2)
volume=16*(integrate(lambda x:x*math.sqrt(1-x*x),0,split)
           +integrate(lambda x:1-x*x,split,1))
check("triple-cylinder geometric integral",volume-8*(2-math.sqrt(2)))

result={"checks":checks,"passed":sum(c["passed"] for c in checks),"total":len(checks)}
target=Path(__file__).parent/'completeness-root-checks.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({"passed":result["passed"],"total":result["total"],"failures":[c for c in checks if not c["passed"]]}))
if result['passed']!=result['total']: raise SystemExit(1)
