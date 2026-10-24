from pathlib import Path
import json,math
import sympy as sp
import mpmath as mp
mp.mp.dps=36
out={}
# Direct Fermi integrals at fixed N=1, V and epsilon_F=k=1.
g=lambda e: mp.mpf('1.5')*mp.sqrt(e)
def avg(mu,t,power=0,fluct=False):
 def integrand(e):
  f=1/(mp.exp((e-mu)/t)+1)
  return e**power*g(e)*(f*(1-f) if fluct else f)
 return mp.quad(integrand,[0,max(mp.mpf('.01'),mu-20*t),mu,mu+20*t,mp.inf])
fermi=[]
for t in map(mp.mpf,['.01','.02','.04']):
 mu=mp.findroot(lambda mu:avg(mu,t)-1,1-mp.pi**2*t*t/12)
 u=avg(mu,t,1)
 moments=[avg(mu,t,j,True) for j in range(3)]
 cv=(moments[2]-moments[1]**2/moments[0])/t**2
 fermi.append({'T_over_TF':float(t),'mu':float(mu),'mu_T2_coefficient':float((mu-1)/t**2), 'U_T2_coefficient':float((u-mp.mpf('.6'))/t**2),'Cv_over_T':float(cv/t)})
 assert abs(cv/t/(mp.pi**2/2)-1)<.01
out['fermi_fixed_N']=fermi
out['fermi_leading_coefficients']={'mu':float(-mp.pi**2/12),'U':float(mp.pi**2/4),'Cv_over_T':float(mp.pi**2/2)}
out['sommerfeld_first_moment']=float(2*mp.quad(lambda x:x/(mp.exp(x)+1),[0,mp.inf]))
assert abs(out['sommerfeld_first_moment']-math.pi**2/6)<1e-14
# Independent polynomial endpoint coefficient and parity checks.
x=sp.symbols('x',real=True)
count=0
for l in range(11):
 P=sp.legendre(l,x)
 for m in range(l+1):
  dm=sp.diff(P,x,m)
  assert sp.simplify(dm.subs(x,1)-sp.factorial(l+m)/(2**m*sp.factorial(m)*sp.factorial(l-m)))==0
  assert sp.expand(dm.subs(x,-x)-(-1)**(l+m)*dm)==0
  count+=1
out['associated_endpoint_and_parity_cases']=count
f=sp.tanh(x/sp.sqrt(2))
assert sp.simplify(sp.diff(f,x,2)+f-f**3)==0
out['GL_tanh_ODE_residual']='0 (symbolic)'
# Kelvin recurrence: closed form, all sphere-surface potentials and capacitance.
spheres=[]
for L in [2.001,2.01,2.2,3.,10.]:
 a=math.acosh(L/2);d=0.;q=1.;charges=[];recerr=0.
 for n in range(3000):
  charges.append((d if n%2==0 else L-d,q))
  dc=math.sinh(n*a)/math.sinh((n+1)*a)
  qc=(-1)**n*math.sinh(a)/math.sinh((n+1)*a)
  recerr=max(recerr,abs(d-dc),abs(q-qc))
  if abs(q)<1e-17:break
  q,d=-q/(L-d),1/(L-d)
 errors=[]
 for j in range(41):
  theta=math.pi*j/40;xx=math.cos(theta);yy=math.sin(theta)
  potential=sum(q/(math.hypot(xx-p,yy))+q/(math.hypot(xx-(L-p),yy)) for p,q in charges)
  errors.append(abs(potential-1))
 capacitance=2*sum(q for p,q in charges)
 assert max(errors)<1e-11
 assert recerr<1e-12
 spheres.append({'L_over_R':L,'images_per_chain':len(charges),'max_surface_V_error':max(errors),'recurrence_error':recerr,'C_over_4pi_eps_R':capacitance})
out['sphere_images']=spheres
out['touching_C_over_4pi_eps_R']=2*math.log(2)
# Prüfer parameter derivative, independent direct differentiation versus integral.
angles=[]
for lam in map(mp.mpf,['1.3','4.0','7.0']):
 def yy(a):return mp.sin(mp.sqrt(a))/mp.sqrt(a)
 def zz(a):return mp.cos(mp.sqrt(a))
 derivative=(zz(lam)*mp.diff(yy,lam)-yy(lam)*mp.diff(zz,lam))/(yy(lam)**2+zz(lam)**2)
 integral=mp.quad(lambda s:(mp.sin(mp.sqrt(lam)*s)/mp.sqrt(lam))**2,[0,1])/(yy(lam)**2+zz(lam)**2)
 assert abs(derivative-integral)<mp.mpf('1e-30')
 angles.append({'lambda':float(lam),'theta_lambda':float(derivative),'integral':float(integral)})
out['SL_Pruefer_derivative']=angles
out['Green_jump']='G_x(s+)-G_x(s-)=-s-(1-s)=-1 for p=1'
Path(__file__).with_name('math-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
