"""Focused mathematical/geometry regression; not a claim of exhaustive correctness."""
from pathlib import Path
import hashlib,json,math,re
B=Path(__file__).resolve().parent.parent; L=B.parent; OUT=B/'build/review-ch07-20260908'
checks=[]
def check(name,residual,tol=1e-9):
    assert abs(residual)<=tol,(name,residual)
    checks.append({'name':name,'residual':residual,'tolerance':tol})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def minus(a,b): return tuple(x-y for x,y in zip(a,b))
def unit(a):
    n=math.hypot(*a);return tuple(x/n for x in a)
def polar(a,r=1): return (r*math.cos(math.radians(a)),r*math.sin(math.radians(a)))
def diagram(src,name): return src.split('\\newcommand{\\'+name+'}')[1].split('\\newcommand')[0]
def coords(src):
    return {k:tuple(map(float,(x,y))) for k,x,y in re.findall(r'\\coordinate \((\w+)\) at \(([-.\d]+),([-.\d]+)\)',src)}
def pgf(src):
    env={'sin':lambda v:math.sin(math.radians(v)),'cos':lambda v:math.cos(math.radians(v)),'sqrt':math.sqrt}
    values={}
    for key,expr in re.findall(r'\\pgfmathsetmacro\{\\(\w+)\}\{([^{}]+)\}',src):
        values[key]=eval(expr.replace('\\',''),{'__builtins__':{}},env|values)
    return values
files=[B/'generated/chapters/ch07.tex',L/'momentum-common-diagrams.tex',B/'tools/build_restructured.py',B/'tools/build_review_ch07.py']
for folder in ['seventh-section','eighth-section','ninth-section','twelfth-section']:
    files.extend(sorted((L/folder).glob('*.tex')))
t=files[0].read_text();old=(B.parents[2]/'archive/2026-09-08-ch07-revision/source/unified/generated/chapters/ch07.tex').read_text()
labels=re.findall(r'\\label\{(ch07:ex:[^}]+)\}',old)
assert len(labels)==36 and all(t.count('\\label{'+s+'}')==1 for s in labels)
check('example and solution counts',t.count(r'\begin{origexamplebox}')-36)
check('solution count',t.count(r'\begin{xesolution}')-36)
check('numbered diagram groups',t.count(r'\label{ch07:fig:')-54)
for name in re.findall(r'\\label\{(ch07:fig:[^}]+)\}',t): assert '\\ref{'+name+'}' in t
assert not re.search(r'sollabel/\.style=\{[^\n]*fill=white',t)
s7=(L/'seventh-section/diagrams.tex').read_text();s8=(L/'eighth-section/diagrams.tex').read_text();s12=(L/'twelfth-section/diagrams.tex').read_text()
for name,src in [('probdiagThreeFour',s7),('probdiagFourNineteen',s12)]:
    d=diagram(src,name);angle=float(re.search(r'rotate=([\d.]+)',d)[1]);normal=polar(angle+90)
    for x,y in re.findall(r'\(([-.\d]+),([-.\d]+)\) rectangle',d):
        check(name+' bottom corner on support',dot(polar(angle,float(x)),normal)+float(y))
d=diagram(s7,'soldiagThreeFour');assert '(0,0)--(2,2)' in d and '(2,2)--(4,8)' in d
check('illustrative post-break acceleration / initial = 3',(8-2)/(4-2)-3)
for name in ['probdiagThreeFifteen','soldiagThreeFifteen']:
    v=pgf(diagram(s8,name));l,h,xL,xH,xR=v['ell'],v['yH'],v['xL'],v['xH'],v['xR']
    check(name+' left rod length',math.hypot(xH-xL,h)-l)
    check(name+' right rod length',math.hypot(xR-xH,h)-l)
    check(name+' weighted horizontal center',2*xL+xH+xR)
    check(name+' geometric midpoint',2*xH-xL-xR)
    check(name+' angle',dot(unit((xL-xH,-h)),unit((xR-xH,-h)))-math.cos(math.radians(2*v['half'])))
v=pgf(diagram(s8,'soldiagThreeEighteen'));r=v['rad'];th=math.radians(v['ang']);X=v['X']
ax=X+r*math.sin(th);ay=r*(1-math.cos(th))
check('bowl point lies on current circle',(ax-X)**2+(ay-r)**2-r*r)
check('bowl horizontal COM, M=m',X+ax-r)
check('bowl ground ellipse',(ax-r/2)**2/(r/2)**2+(ay-r)**2/r**2-1)
d=diagram(s7,'probdiagThreeEight');p=coords(d);S,O=p['S'],p['O'];A=(-.5+2.8*1.5/1.8,-1.4)
vin=unit(minus(O,S));vout=unit(minus(A,O))
check('wall reflection tangential component unchanged',vin[0]-vout[0]);check('wall reflection normal reversed',vin[1]+vout[1])
angle=math.atan(.4);normal=(math.sin(angle),math.cos(angle));vin=(-1,0)
ref=tuple(vin[i]-2*dot(vin,normal)*normal[i] for i in range(2));arrow=polar(180-2*math.degrees(angle))
check('cone reflected x matches drawn arrow',ref[0]-arrow[0]);check('cone reflected y matches drawn arrow',ref[1]-arrow[1])
d=diagram(s8,'soldiagThreeSixteen');assert '.3+2.8*\\x' in d and '2.2-.9*\\x-1.3*\\x*\\x' in d
check('bullet plotted landing height',2.2-.9-1.3)
check('bullet initial velocity components match curve derivative',(.3-1.42)/(.3-.3+1.84-2.2)-2.8/.9)
contact=coords(diagram(s12,'probdiagFourEighteen'));normal=unit(minus(contact['B'],contact['A']))
check('two balls tangent',math.dist(contact['A'],contact['B'])-.8)
tri=coords(diagram(s12,'soldiagFourEighteen'));va=minus(tri['A'],tri['O']);vb=minus(tri['B'],tri['A']);v0=minus(tri['B'],tri['O'])
check('collision momentum x',va[0]+vb[0]-v0[0]);check('collision momentum y',va[1]+vb[1]-v0[1])
check('collision energy',dot(va,va)+dot(vb,vb)-dot(v0,v0));check('collision outgoing A/B perpendicular',dot(va,vb))
check('collision outgoing B follows contact normal',dot(unit(vb),normal)-1)
for x in [1.21115,4.78885]: check('spring turning-point intersection',.35*(x-3)**2-1.12,1e-5)
# Wall-kick feasible interval and optimum: independently sample the original kinematics.
cases=0;worst=0
for mu in [.1,.4,1,2,4]:
    for eta in [.05,.2,.5,.8,.9,1,1.1]:
        D=1-4*eta*(eta-mu)
        possible=eta<=1 and D>0
        if possible:
            lo=max(0,(1-math.sqrt(1-eta**2))/eta,(1-math.sqrt(D))/(2*eta))
            hi=min((1+math.sqrt(1-eta**2))/eta,(1+math.sqrt(D))/(2*eta))
        for i in range(1,1500):
            th=(math.pi/2)*i/1500;z=math.tan(th);c=math.cos(th);s=math.sin(th)
            h1=eta*z-eta**2/(2*c*c);vy=s-eta/c;vp=vy+mu*c
            feasible=h1>=-1e-12 and vp>1e-10
            interval=possible and lo-1e-12<=z<=hi+1e-12 and eta*z*z-z+eta-mu<-1e-10
            assert feasible==interval,(mu,eta,z,feasible,interval)
            if feasible:
                post=h1+vp*vp/2;closed=.5*(z+mu)**2/(1+z*z)-mu*eta
                worst=max(worst,abs(post-closed))
                opt=min(max(1/mu,lo),hi);sup=.5*(opt+mu)**2/(1+opt*opt)-mu*eta
                assert post<=sup+1e-9
                if vy>=0: assert post>=s*s/2-1e-10
            cases+=1
check('wall-kick height identity across feasible samples',worst)
assert 2*2/(1+2**2)<.9 and .9<=1 and .9<1.5
# Accretion formulas satisfy m dv/dt = mg - v dm/dt (and droplet counterpart).
for g in [1,9.8]:
    for ratio in [1,1.1,2,5,10]:
        m0=2.;k=.3;m=m0*ratio
        y=2*g/(3*k)*(m-m0**3/m**2);dy=2*g/(3*k)*(1+2*m0**3/m**3)
        a=k*dy/2
        check('constant-area accretion ODE',m*a-m*g+k*y)
        check('constant-area accretion acceleration',a-(g/3+2*g/(3*ratio**3)))
        alpha=.1;r0=.5;r=r0*ratio;y=2*g/(7*alpha)*(r-r0**7/r**6);dy=2*g/(7*alpha)*(1+6*r0**7/r**7)
        a=alpha*dy/2
        check('droplet accretion ODE',a-g+3*alpha*y/r)
        check('droplet acceleration',a-(g/7+6*g/(7*ratio**7)))
result={'checks':checks,'wall_kick_samples':cases,'source_hashes':{str(p):sha(p) for p in files},
        'examples_retained':36,'solution_groups':36,'numbered_diagram_groups':54,
        'limitation':'Focused equations and source-bound geometry; not an exhaustive proof of source-paragraph completeness or of absence of every graphical defect.'}
(OUT/'geometry-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(f'{len(checks)} equation/geometry checks and {cases} wall-kick samples passed.')
