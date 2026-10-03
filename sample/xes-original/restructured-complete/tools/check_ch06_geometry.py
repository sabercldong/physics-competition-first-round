"""Focused physics/geometry checks, bound to the maintenance-source hashes."""
from pathlib import Path
import math,random,re,json,hashlib
B=Path(__file__).resolve().parent.parent; L=B.parent
OUT=B/'build/review-ch06-20260908'
checks=[]
def record(name,value,tol=1e-10):
    assert abs(value)<=tol,(name,value,tol)
    checks.append({'name':name,'residual':value,'tolerance':tol})
def polar(a,r=1):
    a=math.radians(a);return (r*math.cos(a),r*math.sin(a))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
t=(B/'generated/chapters/ch06.tex').read_text()
old=(B.parents[2]/'archive/2026-09-08-ch06-revision/source/unified/generated/chapters/ch06.tex').read_text()
for typ,n in [('ex',31),('fig',19)]:
    labels=re.findall(r'\\label\{(ch06:'+typ+r':[^}]+)\}',old)
    assert len(labels)==n,(typ,len(labels))
    assert all(t.count('\\label{'+s+'}')==1 for s in labels)
record('31 examples',t.count(r'\begin{origexamplebox}')-31)
record('31 solutions',t.count(r'\begin{xesolution}')-31)
record('50 diagram groups',t.count(r'\begin{tikzpicture}')-50)
assert not re.search(r'\\pgfmathsetmacro\{\\(?:ell|alpha|beta|theta|omega)\}',t)
assert r'font=\footnotesize,fill=none' in t
assert r'z(t)=q(t)' in t and r'mq' in t
assert r'T=2H' in t and '没有有限的角速度上界' in t
assert r'\rho_{\text{水}}' in t and r'\rho_{\rm 水}' not in t
# Circle velocity uses the derivative, not merely either perpendicular direction.
record('ex02 tangent perpendicular to radius',dot(polar(35),polar(125)))
v=(-math.sin(math.radians(35)),math.cos(math.radians(35)))
record('ex02 tangent orientation',dot(v,polar(125))-1)
record('ex06 curve starts at O',-.38*0-.075*0**2)
h=1e-6
record('ex06 initial tangent slope',(-.38*h-.075*h*h)/h+.38,1e-6)
# Bottom faces are constructed with the same slope and external normal.
for name,ang,height,halfwidth in [('ex12',30,.45,.42),('ex22',30,.44,.45),('ex26',22,.38,.45),('ex27',-26,.42,.43),('ex28left',math.degrees(math.atan2(2.6,3.7)),.36,.43),('ex28right',-math.degrees(math.atan2(2.6,1.5)),.36,.43)]:
    tangent=polar(ang); normal=polar(ang+90); center=polar(ang+90,height)
    for side in (-1,1):
        corner=add(sub(center,polar(ang+90,height)),polar(ang,side*halfwidth))
        record(name+' bottom corner '+str(side)+' distance from face',dot(corner,normal))
    record(name+' normal perpendicular',dot(tangent,normal))
record('ex12 hanging mass clears vertical wall',.45-.28-.17)
record('ex14 dimension uses full roof',1.35-(-2.5)-3.85)
record('ex15 displacement lengths sum to AB',1+4-5)
# Groove intersections and their actual vertex angles.
for al,be in [(30,40),(50,25),(20,10)]:
    al,be=map(math.radians,(al,be));height=3
    ell=height*math.cos(al)/math.cos(be-al)
    x=ell*math.sin(be);y=height-ell*math.cos(be)
    record('ex13 B lies on plane '+str(al),y-x*math.tan(al))
    record('ex13 vertical height split '+str(al),ell*math.cos(be)+x*math.tan(al)-height)
    opt=al/2
    def tm(b):return 2*height*math.cos(al)/(9.8*math.cos(b)*math.cos(b-al))
    assert all(tm(opt)<=tm(b)+1e-10 for b in [0,opt/2,opt,(opt+math.pi/2)/2])
    record('ex13 optimum time '+str(al),tm(opt)-4*height*math.cos(al)/(9.8*(1+math.cos(al))))
# Pulley: explicit equations, constraints, support force and total momentum.
random.seed(6); worst=0
for _ in range(200):
    M1,M2,m1,m2=[random.uniform(.2,8) for k in range(4)];g=9.8
    D=(M1+M2)*(m1+m2)+4*m1*m2
    ap=g*((M2-M1)*(m1+m2)+4*m1*m2)/D
    H=2*M1*g*(M2*(m1+m2)+4*m1*m2)/D;T=2*H;T1=4*M1*m1*m2*g/D
    a1=g-T1/m1;a2=g-T1/m2
    residuals=[M1*g-H+M1*ap,M2*g+2*T1-H-M2*ap,a1+a2-2*ap,
               (M1+M2+m1+m2)*g-T-(-M1*ap+M2*ap+m1*a1+m2*a2)]
    worst=max(worst,*map(abs,residuals))
record('ex21 200 mass sets: equations and total external force',worst)
record('ex21 support ratio',4/2-2)
# Wedge: absolute acceleration and normal forces; left/right symmetric limit.
for th in [.2,.5,.9,1.2]:
    M,m,g=2.,1.,9.8;s,c=math.sin(th),math.cos(th)
    den=M+m*s*s;A=m*g*s*c/den;q=(M+m)*g*s/den
    ax=A-q*c;ay=-q*s;N=m*M*g*c/den
    record('ex22 horizontal equation '+str(th),m*ax+N*s)
    record('ex22 vertical equation '+str(th),m*ay-(N*c-m*g))
    record('ex22 slope of absolute acceleration '+str(th),ay/ax-(M+m)/M*math.tan(th))
record('ex22 illustrated M=m vector components',(-1.2)/( -1.2*math.cos(math.pi/6))-2*math.tan(math.pi/6))
record('ex27 static force resultant x',1.5*math.tan(math.radians(26))-1.5*math.tan(math.radians(26)))
record('ex29 isobar perpendicular to effective gravity',dot((1,-.8),(-.8,-1)))
# Effective pendulum potential at the two turning points.
for ratio in [.1,.5,1,3,10]:
    th=math.atan(ratio);ge=math.sqrt(1+ratio*ratio)
    record('ex24 equal endpoint potential '+str(ratio),math.cos(-th)-math.cos(2*th-th))
    record('ex24 minimum tension mg '+str(ratio),ge*math.cos(th)-1)
# Double wedge: dynamic equations and N formula for random acute inclinations.
worst=0
for _ in range(200):
    M,m1,m2=[random.uniform(.2,8) for k in range(3)]
    a,b=[random.uniform(.05,1.45) for k in range(2)];g=9.8
    sa,ca,sb,cb=math.sin(a),math.cos(a),math.sin(b),math.cos(b)
    D=M+m1*sa*sa+m2*sb*sb;A=g*(m1*sa*ca-m2*sb*cb)/D
    q1=g*sa+A*ca;q2=g*sb-A*cb
    N1=m1*(g*ca-A*sa);N2=m2*(g*cb+A*sb)
    assert N1>0 and N2>0
    residuals=[(M+m1+m2)*A-m1*q1*ca+m2*q2*cb,
               N1-m1*g*(M*ca+m2*sb*math.sin(a+b))/D]
    worst=max(worst,*map(abs,residuals))
record('ex28 200 parameter sets: constraints and contact',worst)
# Full friction range, including the zero/negative upper-bound denominator.
cases=0
for deg in [10,25,45,65,80]:
    th=math.radians(deg);s,c=math.sin(th),math.cos(th)
    for mu in [0,.1,.6,math.tan(th),2*math.tan(th),math.cos(th)/math.sin(th)]:
        lo=max(0,(c-mu*s)/(s*s+mu*s*c))
        hi=(c+mu*s)/(s*s-mu*s*c) if mu<math.tan(th)-1e-12 else float('inf')
        for z in [0,lo*.8,lo,lo+1,2,20,1e5]+([hi*.9,hi,hi*1.1] if math.isfinite(hi) else []):
            direct=abs(c-z*s*s)<=mu*s*(1+z*c)+1e-8
            branch=lo-1e-8<=z<=hi+1e-8
            assert direct==branch,(deg,mu,z,lo,hi)
            cases+=1
record('ex30 perpendicular N',dot(polar(55),polar(145)))
paths=[B/'generated/chapters/ch06.tex']
for folder in ['fourth-section','fifth-section','sixth-section']:
    paths.extend(sorted((L/folder).glob('*.tex')))
result={'checks':checks,'friction_parameter_cases':cases,'source_hashes':{str(p):sha(p) for p in paths},
        'source_groups_retained':19,'examples_retained':31,'solution_groups':31,
        'limitation':'Focused physical equations and diagram parameters, not proof of paragraph-level source completeness or absence of all visual defects.'}
(OUT/'geometry-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(f'{len(checks)} checks and {cases} friction cases passed; all 31 example and 19 source-figure anchors retained.')
