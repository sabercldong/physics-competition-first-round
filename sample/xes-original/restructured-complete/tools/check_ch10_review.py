"""Reproduce selected Chapter 10 physics and geometry review findings.

This script creates internal evidence only. It does not edit teaching sources
or certify complete source preservation or complete pedagogical correctness.
"""
from pathlib import Path
import hashlib, json, math

BOOK=Path(__file__).resolve().parent.parent
OUT=BOOK/'build/review-ch10-20260909'
def bisect(f,a,b):
 assert f(a)*f(b)<0
 for _ in range(100):
  c=(a+b)/2
  if f(a)*f(c)<=0:b=c
  else:a=c
 return (a+b)/2

# Re-evaluate the two-stage dry-friction motion, in SI units throughout.
M,m,k,mu,g,l0=3.6,1.8,24.,.3,10.,.3
w=math.sqrt(k*(1/M+1/m))
theta=bisect(lambda z:z-4*math.sin(z),2.,3.)
t1=theta/w;r1=.6+.6*math.cos(theta);u1=-.6*w*math.sin(theta)
wB=math.sqrt(k/m);rB=l0+mu*m*g/k
def r2(t):return rB+(r1-rB)*math.cos(wB*t)+u1/wB*math.sin(wB*t)
tau=bisect(r2,0.,.15)
vB=-(r1-rB)*wB*math.sin(wB*tau)+u1*math.cos(wB*tau)
spring_initial=.5*k*(1.2-l0)**2
spring_final=.5*k*l0*l0
xA1=-.5*t1*t1-(m/(M+m))*(r1-1.2)
xB1=-.5*t1*t1+(M/(M+m))*(r1-1.2)
friction_loss=mu*M*g*xA1+mu*m*g*(-xB1+r1)
energy_residual=spring_initial-(spring_final+.5*m*vB*vB+friction_loss)
assert abs(energy_residual)<1e-10

# Exact matrices of the dimensionless second-order three-charge potential.
# U=(KQ^2/R)[sqrt(3)+1/2 a^T H_a a+1/2 z^T H_z z]+O(3).
fa=5/(12*math.sqrt(3));fz=1/(3*math.sqrt(3))
Ha=[[2*fa if i==j else -fa for j in range(3)] for i in range(3)]
Hz=[[fz for j in range(3)] for i in range(3)]
def matvec(mat,v):return [sum(a*b for a,b in zip(row,v)) for row in mat]
mode_checks=[]
for kind,mat,v,eig in [
 ('a-zero',Ha,[1,1,1],0),('a-vibration-1',Ha,[1,-1,0],3*fa),
 ('a-vibration-2',Ha,[1,1,-2],3*fa),('z-vibration',Hz,[1,1,1],3*fz),
 ('z-zero-1',Hz,[1,-1,0],0),('z-zero-2',Hz,[1,1,-2],0),
]:
 residual=max(abs(a-eig*b) for a,b in zip(matvec(mat,v),v))
 assert residual<1e-12
 mode_checks.append({'mode':kind,'eigenvalue':eig,'max_residual':residual})

# Wedge equations and normal force, with m=g=k=1, across a whole cycle.
wedge_residuals=[]
for th in [0,.5,1.,math.pi,2*math.pi,3*math.pi,4*math.pi]:
 q=(math.cos(th)-1)/4;qdd=-math.cos(th)/3
 sdd=(1-qdd)/math.sqrt(2);N=(1+qdd)/math.sqrt(2)
 residual=max(abs(4*qdd+math.sqrt(2)*sdd+4*q),abs(math.sqrt(2)*qdd+2*sdd-math.sqrt(2)),abs(N/math.sqrt(2)-1+sdd/math.sqrt(2)))
 assert residual<1e-12
 wedge_residuals.append({'phase':th,'N_over_mg':N,'equation_residual':residual})

# Counterexamples to unconditional statements in current theory.
# At a turning point of a damped trajectory, E>0 but dE/dt=-b v^2=0.
gamma=.4;w0=1.;wd=math.sqrt(w0*w0-gamma*gamma)
psi=-math.atan(gamma/wd);x=math.cos(psi);v=-gamma*math.cos(psi)-wd*math.sin(psi)
E=(v*v+x*x)/2
phase_lag=math.atan2(.2*2,1-2*2)
angle=math.degrees(math.atan2(2.7,3.3))
arc_center=[2.20-2.7*math.cos(math.pi/6),.95-1.65*math.sin(math.pi/6)]
result={
 'scope':'Selected independent computations and explicit counterexamples, not full acceptance.',
 'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BOOK/'generated/chapters/ch10.tex',BOOK/'chapters/new/ch10-oscillation.tex',BOOK/'chapters/new/ch10-source-exercises.tex']},
 'ex10_4':{'theta1':theta,'t1_s':t1,'r1_m':r1,'r_dot1_m_per_s':u1,'stage2_s':tau,'collision_t_s':t1+tau,'vA_m_per_s':0,'vB_m_per_s':vB,'energy_residual_J':energy_residual},
 'ex10_7':{'normal_force_checks':wedge_residuals,'rod_length_at_second_max':'L0-mg/k'},
 'ex10_8':{'dimensionless_Ha':Ha,'dimensionless_Hz':Hz,'mode_checks':mode_checks,'published_nonzero_eigenvalues_correct':True},
 'fig10_1':{'required_direction':'clockwise in x-right/v-up axes','drawn_direction':'counterclockwise, parameter angle 30 to 75 degrees','drawn_arrow_ellipse_center':arc_center,'main_ellipse_center':[0,0]},
 'fig10_6':{'drawn_incline_degrees':angle,'labeled_degrees':45,'error_degrees':angle-45},
 'damping_energy_counterexample':{'gamma':gamma,'omega0':w0,'x':x,'v':v,'exact_dE_dt':-2*gamma*v*v,'incorrect_unconditional_exponential_dE_dt':-2*gamma*E},
 'forced_phase_example':{'m':1,'k':1,'b':.2,'omega':2,'correct_delta_deg':math.degrees(phase_lag),'principal_arctan_deg':math.degrees(math.atan(.4/-3))},
 'normal_mode_counterexample':{'M':1,'K':-1,'satisfies_current_stated_conditions':True,'solutions':'C1 exp(t)+C2 exp(-t), not harmonic oscillations'},
 'displacement_peak_condition':'0<gamma<omega0/sqrt(2); at and above threshold maximum for omega>=0 is at omega=0',
}
(OUT/'physics-and-geometry-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},ensure_ascii=False,indent=2))
