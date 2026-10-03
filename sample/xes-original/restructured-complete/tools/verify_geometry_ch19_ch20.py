"""Additional analytic constraints, independent of drawing-path choices."""
import json
import numpy as np
from build_review_ch19_ch20 import BASE
p=BASE/'geometry-checks.json';d=json.loads(p.read_text())
errors=[]
for b in [.65,1.4,2.6]:
 k=.7;e=np.sqrt(1+(b/k)**2);p0=b*b/k;alpha=np.arccos(1/e)
 psi=np.linspace(-alpha*.99,alpha*.99,501);den=e*np.cos(psi)-1
 r=p0/den;dr=p0*e*np.sin(psi)/den**2
 angular=-b/r**2;vr=dr*angular;vt=r*angular
 errors.append(float(np.max(abs((vr*vr+vt*vt)/2+k/r-.5))))
assert max(errors)<1e-12;d['rutherford-energy-residual']=errors
d['rutherford-angular-momentum']='r² dψ/dt = −b v∞, v∞=1, exact parameterization'
theta=np.linspace(.01,np.pi-.01,400);eps=4;chi=(eps-1)/(eps+2)
etout=-(1-chi)*np.sin(theta);etin=-3/(eps+2)*np.sin(theta)
enout=(1+2*chi)*np.cos(theta);enin=3/(eps+2)*np.cos(theta)
assert max(abs(etout-etin))<1e-12 and max(abs(enout-eps*enin))<1e-12
d['dielectric-tangential-E-error']=float(max(abs(etout-etin)))
d['dielectric-normal-D-error']=float(max(abs(enout-eps*enin)))
X=np.cos(theta);Y=np.sin(theta)
E=np.array([3*X*X,3*X*Y]).T
t=np.array([-Y,X]).T
d['conducting-sphere-tangential-E-error']=float(max(abs((E*t).sum(axis=1))))
assert d['conducting-sphere-tangential-E-error']<1e-12
xi=np.linspace(1.01,4,51)[:,None];eta=np.linspace(-.98,.98,51)[None,:]
# r(xi,eta)=(a xi eta,a sqrt((xi²−1)(1−eta²))).
dot=eta*xi+xi*np.sqrt((1-eta*eta)/(xi*xi-1))*(-eta*np.sqrt((xi*xi-1)/(1-eta*eta)))
d['rod-coordinate-tangent-dot-max']=float(np.max(abs(dot)));assert np.max(abs(dot))<1e-12
p.write_text(json.dumps(d,ensure_ascii=False,indent=2));print('Independent boundary and scattering checks passed')
