#!/usr/bin/env python3
"""Independent symbolic/numeric spot checks of revised physics, not a full proof audit."""
import json
import math
import sympy as s

checks = []

def zero(name, expression):
    residual = s.simplify(expression)
    checks.append({"check": name, "passed": residual == 0, "residual": str(residual)})

def near(name, value, expected, tolerance):
    checks.append({"check": name, "passed": abs(value - expected) <= tolerance,
                   "computed": float(value), "expected": expected, "tolerance": tolerance})

t,m,a,b,v0,g = s.symbols("t m a b v0 g", positive=True)
v = v0*s.exp(-a*t/m)
zero("linear drag ODE", m*s.diff(v,t)+a*v)
zero("linear drag initial speed", v.subs(t,0)-v0)
v = v0/(1+b*v0*t/m)
zero("quadratic drag ODE",m*s.diff(v,t)+b*v*v)
v = m*g/a*(1-s.exp(-a*t/m))
zero("vertical drag ODE",m*s.diff(v,t)-m*g+a*v)
zero("vertical drag initial acceleration",s.diff(v,t).subs(t,0)-g)

r,R,sigma,eps = s.symbols("r R sigma eps",positive=True)
phi=sigma/(2*eps)*(s.sqrt(r*r+R*R)-r)
field=sigma/(2*eps)*(1-r/s.sqrt(r*r+R*R))
zero("disk potential gradient",-s.diff(phi,r)-field)

# Solve all eight vertices independently; the corrected text also gives every
# potential, so students can check the original equations rather than a slogan.
vertices=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]
lap=s.zeros(8)
for i,x in enumerate(vertices):
    for j,y in enumerate(vertices):
        if sum(u!=v for u,v in zip(x,y))==1:
            lap[i,i]+=1
            lap[i,j]-=1
for terminal,answer in [(1,s.Rational(7,12)),(2,s.Rational(3,4)),(6,s.Rational(5,6))]:
    indices=[i for i in range(8) if i!=terminal]
    potential=lap.extract(indices,indices).inv()*s.Matrix([int(i==0) for i in indices])
    zero(f"cube unit-current port 0-{terminal}",potential[0]-answer)

p,q=s.symbols("p q",positive=True)
tail=s.Matrix([[p+q,-p,-q],[-p,2*p,-p],[-q,-p,p+q]])
rungs=s.Matrix([[1,-1,0],[-1,2,-1],[0,-1,1]])
admittance=s.eye(3)-(s.eye(3)+tail+rungs).inv()
zero("three-rail Schur p",-admittance[0,1]-(p+1)/(3*p+4))
zero("three-rail Schur q",-admittance[0,2]-(p*p+2*p*q+2*p+3*q+1)/((3*p+4)*(p+2*q+2)))
pv=(s.sqrt(21)-3)/6
qv=(3*s.sqrt(5)-s.sqrt(21))/12
zero("three-rail positive fixed point p",((p+1)/(3*p+4)-p).subs({p:pv,q:qv}))
zero("three-rail positive fixed point q",(-admittance[0,2]-q).subs({p:pv,q:qv}))

eps0=8.8541878128e-12
earth_radius=6.4e6
height=5000
rho=3e13
cap=4*math.pi*eps0*earth_radius*(earth_radius+height)/height
res=rho/(4*math.pi)*(1/earth_radius-1/(earth_radius+height))
near("atmospheric capacitance F",cap,.912,.001)
near("atmospheric resistance ohm",res,291,1)
near("dielectric relaxation time s",res*cap,rho*eps0,1e-8)
near("copper electrolysis grams",1930*.8/(2*96485.33212)*63.5,.508,.001)
near("star three-phase power W",380**2/30,4810,10)
near("delta three-phase power W",3*380**2/30,14440,10)
near("laser threshold gain inverse m",.02+math.log(1/.9)/.6,.196,.001)
near("capacitor ripple peak-to-peak V",.020/(2*50*.001),.200,1e-12)

translation=lambda d,n:s.Matrix([[1,s.Rational(d)/n],[0,1]])
refraction=lambda power:s.Matrix([[1,0],[-power,1]])
telescope=refraction(1)*translation(3,3)*refraction(s.Rational(6,5))*translation(5,1)*refraction(s.Rational(1,5))
zero("thick-eyepiece pupil magnification",telescope[0,0]+s.Rational(1,5))
zero("thick-eyepiece pupil conjugacy",telescope[0,1])
zero("thick-eyepiece afocal condition",telescope[1,0])
zero("thick-eyepiece angular magnification",telescope[1,1]+5)
w,vo,ve,theta=s.symbols("w vo ve theta",real=True)
polynomial=s.sin(theta)**2*(w-vo**2)*(w-ve**2)+s.cos(theta)**2*(w-vo**2)**2
zero("uniaxial crystal retains both polarization roots",s.trigsimp(polynomial-(w-vo**2)*(w-vo**2*s.cos(theta)**2-ve**2*s.sin(theta)**2)))

# Final-audit regressions: test branch signs, polarization probabilities and
# invariant definitions independently of the TeX replacement strings.
u,ym=s.symbols("u ym",positive=True)
ray_y=ym*s.sin(u)**2
for sign in [-1,1]:
    ray_x=sign*ym*(u-s.sin(2*u)/2)
    zero(f"shallow-water ray slope branch {sign}",
         s.trigsimp(s.diff(ray_x,u)/s.diff(ray_y,u)-sign*s.tan(u)))
phi=s.symbols("phi",real=True)
zero("two coherent beams count relative phase once",
     s.expand_complex((1+s.exp(s.I*phi))*(1+s.exp(-s.I*phi)))-2-2*s.cos(phi))
spin=s.Matrix([s.cos(theta/2),s.exp(s.I*phi)*s.sin(theta/2)])
px=s.Matrix([1,1])/s.sqrt(2)
py=s.Matrix([1,s.I])/s.sqrt(2)
for name,bra,expected in [("x",px,(1+s.sin(theta)*s.cos(phi))/2),
                          ("y",py,(1+s.sin(theta)*s.sin(phi))/2)]:
    amplitude=(bra.conjugate().T*spin)[0]
    zero(f"spin projection probability {name}",
         s.trigsimp(s.expand_complex(amplitude*s.conjugate(amplitude)))-expected)
M=s.Matrix([[2,0],[s.Rational(1,3),s.Rational(1,2)]])
ray1=s.Matrix([0,s.Rational(1,5)])
ray2=s.Matrix([1,s.Rational(2,7)])
zero("optical two-ray determinant invariant",
     s.det(s.Matrix.hstack(M*ray1,M*ray2))-s.det(s.Matrix.hstack(ray1,ray2)))
zero("conjugate transverse and angular magnification reciprocal",
     M[0,0]*(M*ray1)[1]/ray1[1]-1)
import cmath
z=.37+.41j
partial=1/z+sum(2*z/(z*z-k*k) for k in range(1,20001))
near("cotangent paired series at complex noninteger z",
     abs(partial-math.pi/cmath.tan(math.pi*z)),0,6e-5)
inertia,bead_mass,radius,gravity=s.symbols("I mb a g",positive=True)
effective=(inertia**2*gravity/radius)/(2*(inertia+bead_mass*radius**2*s.sin(theta)**2))
effective+=bead_mass*gravity*radius*(1-s.cos(theta))
zero("free-ring bead critical quadratic term vanishes",
     s.diff(effective,theta,2).subs(theta,0)/2)
zero("free-ring bead critical quartic stability coefficient",
     s.diff(effective,theta,4).subs(theta,0)/24-
     bead_mass*gravity*radius*(s.Rational(1,8)+bead_mass*radius**2/(2*inertia)))
vx,vy,Omega=s.symbols("vx vy Omega",real=True)
coriolis=-2*s.Matrix([0,0,Omega]).cross(s.Matrix([vx,vy,0]))
zero("east-north-up Coriolis force sign",
     (coriolis-s.Matrix([2*Omega*vy,-2*Omega*vx,0])).dot(s.Matrix([1,2,3])))

print(json.dumps({"scope":"Independent spot checks of specified revised formulas; not certification of every derivation",
                  "checks":checks,"passed":sum(c["passed"] for c in checks),"total":len(checks)},ensure_ascii=False,indent=2))
if not all(c["passed"] for c in checks):
    raise SystemExit(1)
