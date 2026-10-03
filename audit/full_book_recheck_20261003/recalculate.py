"""Independent sampled checks; no manuscript generation or mutation."""
import math,json
from pathlib import Path
checks=[]
def record(name,observed,expected,tol=1e-8,method='direct substitution'):
 err=abs(observed-expected);ok=err<=tol
 checks.append(dict(name=name,observed=observed,expected=expected,tolerance=tol,error=err,passed=ok,method=method))
def simpson(f,a,b,n=10000):
 h=(b-a)/n
 return h/3*(f(a)+f(b)+4*sum(f(a+(2*i-1)*h) for i in range(1,n//2+1))+2*sum(f(a+2*i*h) for i in range(1,n//2)))
# Chapter 2: follow trajectories and sum flights instead of fitting final answers.
g,H,T=9.8,80.,1.3;tf=math.sqrt(2*H/g);v=g*T*(2*tf-T)/(2*(tf-T));dt=tf-T
record('2.18: minimum launch speed reaches ground at the same time',v*dt+g*dt*dt/2,H)
e=.63;u=math.sqrt(2*g*H)
record('2.19: bounce flight-time sum',sum(2*u*e**n/g for n in range(1,500)),2*e*u/(g*(1-e)))
record('2.19: bounce distance sum',sum((u*e**n)**2/g for n in range(1,500)),2*H*e*e/(1-e*e))
v0,a,k=7.,2.,1.8
record('2.20: increasing-acceleration time sum',sum(2*v0/(a*k**n) for n in range(100)),2*v0/a*k/(k-1))
tau=math.sqrt(2*H/g)
def height(t):
 phase=t%(2*tau);fall=min(phase,2*tau-phase);return H-g*fall**2/2
record('2.21: half-period stroboscopic height',height(tau/2),3*H/4)
record('2.21: second exposure height',height(1.5*tau),3*H/4)
# Chapter 4: direct periods and vector cross products.
Tr=1/(1/24+1/(365.2564*24));D=361*Tr/360
record('4.30: new solar day, hours',D,24.000957,0.0000005)
record('4.30: new year, hours',D*360,8640.344,.0005)
k=1.524;q=k**(-1.5);delta=math.acos((k*k*q+1)/(k*(1+q)));syn=365.2564/(1-q)
record('4.31: retrograde days',syn*delta/math.pi,72.74,.005)
record('4.31: direct-motion days',syn*(1-delta/math.pi),706.93,.005)
rx,ry=k*math.cos(delta)-1,k*math.sin(delta);vx,vy=-k*q*math.sin(delta),k*q*math.cos(delta)-1
record('4.31: stationary sightline cross product',rx*vy-ry*vx,0.)
# Chapter 13: conservation integral and ray invariant.
H,R,a=1.2,.4,.008
time=simpson(lambda h:math.pi*(R*h/H)**2/(math.pi*a*a*math.sqrt(2*g*h)),H/2,H)
record('13.16: funnel emptying time, seconds',time,2*R*R/(5*a*a)*math.sqrt(H/(2*g))*(1-2**(-2.5)),1e-7,'numerical volume-flux integral')
y0,C,phi=3.,1.2,1.1;y=y0*(1+math.cos(phi))/2;dx=y0*(1+math.cos(phi))/2;dy=-y0*math.sin(phi)/2
record('13.17: Snell ray invariant',dx/math.hypot(dx,dy)/(C*math.sqrt(y)),1/(C*math.sqrt(y0)))
rho,Q,A,M=1000.,.0003,.0002,.26;u=Q/A
th=math.atan(1/3)+math.asin(4*rho*Q*u/(M*10*math.sqrt(10)))
record('13.18: pipe equilibrium angle, degrees',math.degrees(th),31.1,.05)
record('13.18: angular momentum flux balance',M*10*.4/4*(3*math.sin(th)-math.cos(th)),rho*Q*u*.4)
# Chapter 15: finite-difference generalized force against analytic stiffness.
R,sigma,sigma0,p0=.025,.03,.004,101325.
for kap in [1.,1.4]:
 pR=p0+4*sigma/R;mass=4*math.pi*R*R*sigma0
 def force(r):return 4*math.pi*r*r*(pR*(R/r)**(3*kap)-p0)-16*math.pi*sigma*r
 eps=R*1e-5;omega2=-(force(R+eps)-force(R-eps))/(2*eps)/mass
 expected=(3*kap*R*pR-4*sigma)/(R*R*sigma0)
 record(f'15.10: relative frequency-squared error, kappa={kap}',omega2/expected,1.,1e-8,'finite difference of generalized radial force')
# Chapter 17: dry lapse rate.
Gamma=(.4/1.4)*.0288*9.8/8.314462618
record('17.8: dry lapse rate, K/km',1000*Gamma,9.7,.05)
# Chapter 21: generate Sierpinski edges then solve each resistor network by KCL.
def solve(A,b):
 A=[row[:]+[v] for row,v in zip(A,b)];n=len(b)
 for k in range(n):
  j=max(range(k,n),key=lambda j:abs(A[j][k]));A[k],A[j]=A[j],A[k];p=A[k][k]
  for t in range(k,n+1):A[k][t]/=p
  for j in range(n):
   if j==k:continue
   f=A[j][k]
   for t in range(k,n+1):A[j][t]-=f*A[k][t]
 return [row[-1] for row in A]
for n in range(4):
 side=2**n;triangles=[((0,0),(side,0),(0,side))]
 for _ in range(n):
  sub=[]
  for a,b,c in triangles:
   ab=tuple((x+y)//2 for x,y in zip(a,b));ac=tuple((x+y)//2 for x,y in zip(a,c));bc=tuple((x+y)//2 for x,y in zip(b,c))
   sub.extend([(a,ab,ac),(ab,b,bc),(ac,bc,c)])
  triangles=sub
 edges=set()
 for a,b,c in triangles:edges.update(tuple(sorted(e)) for e in [(a,b),(b,c),(c,a)])
 nodes=set(v for e in edges for v in e);fixed={(0,0):1.,(side,0):0.};unknown=sorted(nodes-fixed.keys());idx={p:i for i,p in enumerate(unknown)}
 neighbors={v:[] for v in nodes}
 for a,b in edges:neighbors[a].append(b);neighbors[b].append(a)
 mat=[[0.]*len(unknown) for _ in unknown];rhs=[0.]*len(unknown)
 for p,i in idx.items():
  mat[i][i]=len(neighbors[p])
  for v in neighbors[p]:
   if v in fixed:rhs[i]+=fixed[v]
   else:mat[i][idx[v]]-=1
 pot=dict(fixed);pot.update(zip(unknown,solve(mat,rhs)))
 current=sum((1-pot[v])*side for v in neighbors[(0,0)])
 record(f'21.18: Sierpinski network resistance, level {n}',1/current,2/3*(5/6)**n,1e-8,'generated graph and nodal KCL; lambda*a=1')
# Chapters 23/24: rate, coupled initial-value models, energy.
f=2.79*1.60e-19/(1.67e-27)/(2*math.pi)
record('23.9: proton frequency, MHz',f/1e6,42.5,.05)
record('23.9: radio wavelength, m',299792458/f,7.05,.005)
m,C,k,v0=2.,.3,1.4,3.;qinf=m*C*k*v0/(m+C*k*k);vinf=v0-k*qinf/m
record('24.6: terminal capacitor voltage and emf',qinf/C,k*vinf)
heat=.5*m*v0*v0-.5*m*vinf*vinf-qinf*qinf/(2*C)
record('24.6: energy loss in small-resistance limit',heat,m*C*k*k*v0*v0/(2*(m+C*k*k)))
# Finite inductance and zero resistance: oscillates instead of settling.
L=.7;om=math.sqrt((1/C+k*k/m)/L);qhalf=qinf*(1-math.cos(math.pi));vhalf=v0-k*qhalf/m
record('24.6: alternative lossless model conserves energy',.5*m*vhalf*vhalf+qhalf*qhalf/(2*C),.5*m*v0*v0)
L,m,k,v0=.7,2.,1.4,3.;om=k/math.sqrt(m*L);t=.61;v=v0*math.cos(om*t);I=v0*math.sqrt(m/L)*math.sin(om*t)
record('24.7: coupled rod-inductor energy',.5*m*v*v+.5*L*I*I,.5*m*v0*v0)
# Chapter 30: coherency-matrix eigenvalues independently give unpolarized share.
a,b,c=1.5,1.,math.sqrt(.75*.25);disc=math.sqrt((a-b)**2+4*c*c);lo=(a+b-disc)/2;hi=(a+b+disc)/2
record('30.15: unpolarized fraction',2*lo/(a+b),.6)
record('30.15: maximum transmitted intensity / I0',hi,1.75)
record('30.16: extraordinary effective refractive index',math.sqrt(2/(1/1.66**2+1/1.49**2)),1.57,.005)
out=Path(__file__).with_name('recalculation.json');out.write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print(f'{len(checks)} checks; {sum(x["passed"] for x in checks)} passed')
for c in checks:
 if not c['passed']:print(c)
assert all(c['passed'] for c in checks)
