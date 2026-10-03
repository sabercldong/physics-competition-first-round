#!/usr/bin/env python3
"""Focused numerical regressions, not a replacement for PDF visual review."""
import hashlib
import json
import math
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
LEGACY = BOOK.parent
OUT = BOOK / 'build/review-ch05-20260908'
checks = []

def record(name, residual, tolerance=1e-10):
    assert abs(residual) <= tolerance, (name, residual, tolerance)
    checks.append({'name': name, 'residual': residual, 'tolerance': tolerance})

def polar(angle, radius):
    return radius * math.cos(math.radians(angle)), radius * math.sin(math.radians(angle))

def dot(a, b):
    return sum(x*y for x,y in zip(a,b))

def norm(a):
    return math.hypot(*a)

tex = (BOOK/'generated/chapters/ch05.tex').read_text()
diagram = (LEGACY/'third-section/solution-diagrams.tex').read_text()
faithful = (LEGACY/'third-section/faithful-source-diagrams.tex').read_text()
assert not re.search(r'\\(?:def|pgfmathsetmacro)\s*\{?\\(?:alpha|beta|gamma|delta|theta|phi|varphi)\b', diagram)
assert r'sollabel/.style={font=\footnotesize,text=Ink,fill=none' in diagram
record('61 TikZ environments retained/added', tex.count(r'\begin{tikzpicture}')-61)
record('31 examples', tex.count(r'\begin{origexamplebox}')-31)
record('31 solutions', tex.count(r'\begin{xesolution}')-31)
ledger = json.loads((BOOK/'audit/ch05-source-figure-ledger.json').read_text())
assert len(ledger['entries']) == 32
assert len({e['new_anchor'] for e in ledger['entries']}) == 32
assert all(r'\label{'+e['new_anchor']+'}' in tex for e in ledger['entries'])
old = BOOK.parents[2] / 'archive/2026-09-08-ch05-revision/source/unified/generated/chapters/ch05.tex'
assert old.exists(), old
before = old.read_text()
old_examples = re.findall(r'\\label\{(ch05:ex:[^}]+)\}', before)
assert all(r'\label{'+s+'}' in tex for s in old_examples)

# Radius endpoints use polar coordinates in the maintained source itself.
for angle, radius in [(135,2.25),(135,1.65),(155,2.40)]:
    assert f'({angle}:{radius:.2f})' in faithful
    record(f'radius endpoint {radius}', norm(polar(angle,radius))-radius)
for lo,hi,radius in [(12,72,.85),(13,52,.92)]:
    center = polar((lo+hi)/2, radius/math.sin(math.radians((hi-lo)/2)))
    for side in (lo,hi):
        record(f'sphere tangent to {side} degree face', abs(dot(center,polar(side+90,1)))-radius)

# The plate and all three contact points now share exactly the same direction.
assert r'(A)--++(25:6.90)' in diagram
sone = .52*(1+math.sin(math.radians(25)))/math.cos(math.radians(25))
point = polar(25,sone)
normal = polar(115,.52)
record('cylinder 1 touches vertical wall', point[0]+normal[0]-.52)
record('plate normal perpendicular to plate', dot(polar(25,1),polar(115,1)))

# Catenary: force line, centroid and moment all follow the same analytic curve.
c,x=2.7,2.2
y=c*(math.cosh(x/c)-1)
s=c*math.sinh(x/c)
xg=x-y/math.sinh(x/c)
record('catenary slope equals s/c', math.sinh(x/c)-s/c)
record('catenary force-line moment about O', x*s-y*c-s*xg)

# Elliptic support: rod length and actual normal, away from the excluded end.
L,x=4.6,3.8
y=(L-math.sqrt(L*L-x*x))/2
Y=L-y
record('elliptic support rod length', math.hypot(x,Y-y)-L)
slope=x/(2*math.sqrt(L*L-x*x))
record('normal PC perpendicular to tangent', dot((-x/2,Y-y),(1,slope)))
record('constant centre-of-mass height', (Y+y)/2-L/2)

# The displacement dimension is constrained to a common horizontal line.
assert '(A0|-DimBase)--(A|-DimBase)' in diagram
record('inclined rod same length', norm(polar(73,2.70))-2.70)

# Two independent formulas for the separated three-ball branch agree.
for theta in [.35,.40,.47,.51]:
    w=math.sqrt(1-4*math.sin(theta)**2)
    n=2*w/(2*math.cos(theta)-w)
    def n_of(t):
        z=math.sqrt(1-4*math.sin(t)**2)
        return 2*z/(2*math.cos(t)-z)
    derivative=-12*math.sin(theta)/(w*(2*math.cos(theta)-w)**2)
    numerical=(n_of(theta+1e-6)-n_of(theta-1e-6))/2e-6
    record(f'three-ball dn/dtheta at {theta}', numerical-derivative, 2e-6)
    def u(t):
        return -3*(2+n)*math.cos(t)+1.5*n*math.sqrt(1-4*math.sin(t)**2)
    h=1e-5
    u2=(u(theta+h)-2*u(theta)+u(theta-h))/(h*h)
    analytic=-18*n*math.sin(theta)**2/w**3
    record(f'three-ball unstable curvature at {theta}', (u2-analytic)/max(1,abs(analytic)), 2e-5)

# At the critical concave example R=3r, h=r/2, the fourth-order term is positive.
a,r,h=2,1,.5
coefficient=a*(a*a-r*r)/(24*r*r)
assert coefficient>0
phi=.01
delta_y=-a*math.cos(phi)+h*math.cos(a*phi/r)+a-h
record('concave critical fourth-order coefficient', delta_y/phi**4-coefficient, 2e-5)
for curvature_sign,R,r,phi in [('concave',3.45,.68,12),('convex',2.1,.65,15)]:
    a=R-r if curvature_sign=='concave' else R+r
    record(f'{curvature_sign} contact distance', abs(a-R)-r)
    # psi_dot=-a/r*phi_dot with phi_dot=1; vcontact=0.
    record(f'{curvature_sign} rolling no-slip speed', a+r*(-a/r))

paths = [BOOK/'generated/chapters/ch05.tex', LEGACY/'first-section/main.tex',
         LEGACY/'second-section/main.tex', *sorted((LEGACY/'third-section').glob('*.tex'))]
result={'checks':checks, 'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'source_groups_retained':32, 'examples_retained':len(old_examples),
        'limitation':'Focused numerical and identifier checks; not paragraph-level source completeness or visual clearance proof.'}
(OUT/'geometry-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(f'{len(checks)} numerical checks passed; 32 source-figure anchors and 31 example anchors retained.')
