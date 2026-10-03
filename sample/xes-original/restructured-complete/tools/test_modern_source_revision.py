"""Numerical regression for corrected formulae. Not a substitute for source audit."""
import math,json
from pathlib import Path

BOOK=Path(__file__).resolve().parents[1]
results={}
N,P,M,me=939.6,938.2,1777.,.511
eth=((M+P)**2-N*N)/(2*N)
gamma=(eth+N)/(M+P);beta=eth/(eth+N)
def endpoint(ev):
    s=N*N+2*N*ev
    lam=max(0.,(s-(M+P)**2)*(s-(M-P)**2))
    et=(s+M*M-P*P)/(2*math.sqrt(s));pt=math.sqrt(lam)/(2*math.sqrt(s))
    h=(et*(M*M+me*me)+pt*(M*M-me*me))/(2*M*M)
    a=ev+N;b=ev*math.cos(math.pi/6);y=math.sqrt(s)*h
    ee=(a*y+b*math.sqrt(y*y-(a*a-b*b)*me*me))/(a*a-b*b)
    assert math.isclose(a*ee-b*math.sqrt(ee*ee-me*me),y,rel_tol=1e-10)
    return ee
assert math.isclose(endpoint(eth),1720.409939,rel_tol=1e-8)
results['neutrino']={'threshold_MeV':eth,'gamma_c':gamma,'beta_c':beta,
    'electron_endpoint_at_threshold_MeV':endpoint(eth),
    'electron_endpoints_MeV':{str(e):endpoint(e) for e in (1e4,1e5,1e8)},
    'massless_supremum_MeV':N/(1-math.cos(math.pi/6))}
for beta in (.01,.3,.8,.98):
    gamma=1/math.sqrt(1-beta*beta)
    for theta in (.1,.5,1.2,2.4,4.8):
        # c=mu0=sigma0*u=B0=1; surface normal=(cos,sin).
        co,si=math.cos(theta),math.sin(theta)
        sigma=-gamma*beta*si;kx=-gamma*si;ky=co/gamma
        ey=gamma*beta;bz=gamma;vn=beta*co
        assert math.isclose(kx*co+ky*si,sigma*vn,rel_tol=1e-10,abs_tol=1e-12)
        assert math.isclose(-bz*si,kx,rel_tol=1e-10)
        assert math.isclose(bz*co,ky+vn*ey,rel_tol=1e-10)
        assert math.isclose(ey,beta*bz,rel_tol=1e-10)
results['moving_surface']='20 angle/speed samples: continuity, Ampere displacement term, Faraday passed'
# Closed source curve tangent, computed from the same parameterization.
t=math.radians(345);h=1e-5
def xy(t):return (1.7*math.cos(t)+.45*math.cos(2*t),1.7*math.sin(t))
d=(-1.7*math.sin(t)-.9*math.sin(2*t),1.7*math.cos(t))
for k in range(2):assert math.isclose((xy(t+h)[k]-xy(t-h)[k])/(2*h),d[k],rel_tol=1e-8)
results['closed_curve_tangent']='analytic derivative equals finite difference'
# Photon ellipse and elastic recoil geometry use a shared vector scale.
for theta in (.0,.3,1.,2.,math.pi):
    k=3/(2*(2-math.cos(theta)))
    other=math.hypot(k*math.sin(theta),1-k*math.cos(theta))
    assert math.isclose(k+other,2.,rel_tol=1e-12)
results['photon_scattering']='5 angular samples conserve vector momentum and scalar photon energy'
# Compare the Doppler ratio with retarded arrival-time differentiation.
def pursuit_times(beta,theta):
    u=math.tan(theta/2);ell=(1+u*u)/2
    te=((1-u*u)/4-math.log(u)/2)/beta
    q=math.sqrt(1-beta*beta*math.sin(theta)**2);a=q-beta*math.cos(theta)
    return te,te+ell/a
for beta in (.1,.4,.9):
    theta=math.pi/3;h=1e-6
    lo=pursuit_times(beta,theta-h);hi=pursuit_times(beta,theta+h)
    derivative=(hi[0]-lo[0])/(hi[1]-lo[1])
    q=math.sqrt(1-beta*beta*math.sin(theta)**2);a=q-beta*math.cos(theta)
    assert math.isclose(derivative,a*q/(1-beta*q),rel_tol=1e-8)
results['pursuit_frequency']='3 speeds: independent retarded-time derivative agrees'
for n in (1,2,3,4,19,20):
    m=n//2
    exact=m*(m+1)*(2*m+1)/3+(m+1)**2*(n%2)
    direct=sum((i//2+1)**2 for i in range(n))
    assert exact==direct
results['finite_N_fermi']='N=1,2,3,4,19,20 exact occupancy sums agree'
# Explicit four-momentum recursion for a representative fictional nuclear chain.
q=.01;a=1+q;eta=0.;emitted=[]
for j in range(20,1,-1):
    mother=j*a;daughter=(j-1)*a if j>2 else 1.
    ed=(mother*mother+daughter*daughter-1)/(2*mother)
    pp=math.sqrt(max(0.,ed*ed-daughter*daughter));ee=mother-ed
    emitted.append((math.cosh(eta)*ee-math.sinh(eta)*pp,
        math.sinh(eta)*ee-math.cosh(eta)*pp))
    eta+=math.acosh(ed/daughter)
assert math.isclose(sum(x[0] for x in emitted)+math.cosh(eta),20*a,rel_tol=1e-12)
assert abs(sum(x[1] for x in emitted)+math.sinh(eta))<1e-11
results['nuclear_chain']={'Q_over_mc2':q,'maximum_speed_over_c':math.tanh(eta),
    'last_emitted_lab_momentum_over_mc':emitted[-1][1],'energy_momentum_conserved':True}
out=BOOK/'build/modern-source-revision-20260923/numerical-checks.json'
out.write_text(json.dumps(results,indent=2,ensure_ascii=False));print(json.dumps(results,ensure_ascii=False))
