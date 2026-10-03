"""Independent numeric checks of the parameters used by modern-physics figures."""
import math,json,re,subprocess
from pathlib import Path
from scipy.integrate import quad
from scipy.optimize import brentq
import build_review_ch31_ch32 as r
checks={};details={}
def check(name,ok,detail):
 checks[name]=bool(ok);details[name]=detail
 assert ok,(name,detail)
beta=1/3;L=4;ct=4.2
check('parallel_train_worldlines',abs((1.4-0)/ct-(5.4-L)/ct)<1e-12,{'beta':beta,'separation':5.4-1.4})
P=(L/2,L/2)
check('light_meeting_and_moving_midpoint',P[0]==P[1]==L-P[1] and abs(P[0]-(L/2+beta*P[1]))>0,{'meeting':P,'moving_midpoint_x':L/2+beta*P[1]})
check('primed_axes_consistent',abs(1.8/4.5-2.04/5.1)<1e-12,{'beta':.4})
check('light_clock_triangle',abs(math.hypot(2.4,1.8)-3)<1e-12,{'L':2.4,'horizontal':1.8,'light_path':3})
for b in [.01,.6,.8,.98]:
 g=1/math.sqrt(1-b*b);M=2*g
 check(f'collision_energy_{b}',abs(M-2*g)<1e-14 and M>=2,{'gamma':g,'M_over_m':M})
check('threshold_absorptive_and_release',abs((9-4)/2-2.5)<1e-12 and max(0,(1.5**2-4)/2)==0,{'absorptive_ma_mb_1_Mf_3':2.5,'release_ma_mb_1_Mf_1.5':0})
z=brentq(lambda z:5*(1-math.exp(-z))-z,4,6)
peaks=[]
for T in [4000,6000]:
 x=14387.77/T/z;y=37.4177/(x**5*math.expm1(14387.77/T/x));peaks.append((x,y))
integral=quad(lambda z:z**3/math.expm1(z),1e-8,80)[0]
check('planck_integral',abs(integral-math.pi**4/15)<1e-9,{'dimensionless_integral':integral,'area_ratio':(6000/4000)**4})
check('planck_peak_guides',abs(peaks[0][0]-.72444305047)<1e-10 and abs(peaks[1][1]-10.0053244776)<1e-8,{'peaks':peaks,'z':z})
check('photoelectric_points',abs(.415*6-1.99-.50)<1e-12 and abs(.415*8-1.99-1.33)<1e-12,{'slope':.415,'threshold':1.99/.415})
p_ratio=.071/(.071+.002426)
check('compton_recoil_direction',abs(2.6108/2.7-p_ratio)<1e-5,{'p_prime_over_p':p_ratio,'photon_energy_loss_keV':1.23984/.071-1.23984/.073426})
A=(0,1.4);B=(0,0);C=(-.606218,.35);D=(.606218,.35)
dot=lambda u,v:sum(x*y for x,y in zip(u,v))
check('bragg_normal_projections',abs(dot((A[0]-C[0],A[1]-C[1]),(math.sqrt(3)/2,-.5)))<1e-6 and abs(dot((A[0]-D[0],A[1]-D[1]),(math.sqrt(3)/2,.5)))<1e-6,{'CB_plus_BD':2*math.hypot(*C),'2d_sin_theta':1.4})
check('bragg_angle',abs(math.degrees(math.asin((1.227/math.sqrt(54))/.4))-24.672683)<1e-6,{'theta_degrees':math.degrees(math.asin((1.227/math.sqrt(54))/.4))})
check('hydrogen_upper_levels',abs(5.6-2.2-3.4)<1e-12 and abs(5.6-4.089-13.6/9)<.001,{'n2':-3.4,'n3':-13.6/9,'n4':-.85})
check('decay_peak',abs(math.exp(-math.log(2))-math.exp(-2*math.log(2))-.25)<1e-12,{'x_peak':math.log(2),'N2_over_initial':.25})
check('fusion_Q',round(.018883*931.5,1)==17.6,{'Q_MeV':.018883*931.5})
(r.BASE/'physics-checks.json').write_text(json.dumps(checks,indent=2))
(r.BASE/'physics-calculations.json').write_text(json.dumps(details,indent=2))
print('Physics/geometry checks:',len(checks))
out=r.BASE/'figure-lints';out.mkdir(exist_ok=True)
ref=Path('/Users/dongxingxi/.codex/skills/thesis-figure-skill/references')
for p in (r.book.BOOK/'assets/diagrams-modern').glob('*.tex'):
 for script,args in [('tikz-validator.py',[]),('tikz-design-linter.py',['--type','simple'])]:
  q=subprocess.run(['python3',str(ref/script),str(p),*args],capture_output=True,text=True)
  (out/f'{p.stem}-{script}.txt').write_text(q.stdout+q.stderr)
print('Lint reports written; warnings require manual triage, not automatic rejection.')
