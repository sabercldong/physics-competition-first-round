"""Generate exact layered-field trajectory data and check revised geometry."""
import math,json
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[2]/'thirty-eighth-section/assets/trajectory-data'
P.mkdir(parents=True,exist_ok=True)
rows=[];joins=[]
x,y,vx,vy=6.,0.,0.,0.
a=1.25
for k in range(1,4):
 t=(-vy+math.sqrt(vy*vy+2*a))/a
 for s in np.linspace(0,t,90):rows.append((x+vx*s,y+vy*s+a*s*s/2))
 x+=vx*t;y+=vy*t+a*t*t/2;vy+=a*t
 joins.append({'layer':k,'start':[x,y],'velocity':[vx,vy]})
 tturn=math.atan2(vy,-vx)
 def rise(t):return vx*(1-math.cos(t))+vy*math.sin(t)
 if rise(tturn)<1:t=tturn
 else:
  lo,hi=0.,tturn
  for _ in range(65):
   mid=(lo+hi)/2
   if rise(mid)<1:lo=mid
   else:hi=mid
  t=(lo+hi)/2
 for s in np.linspace(0,t,110):rows.append((x+vx*math.sin(s)+vy*(math.cos(s)-1),y+rise(s)))
 x+=vx*math.sin(t)+vy*(math.cos(t)-1);y+=rise(t)
 vx,vy=vx*math.cos(t)-vy*math.sin(t),vx*math.sin(t)+vy*math.cos(t)
 assert abs(vx+k)<1e-10 or k==3
np.savetxt(P/'layers.dat',rows,fmt='%.10f')
xs=np.linspace(0,6,601);bs=1+.15*xs
vparallel=np.sqrt(2-.36*bs);freq_over_v=bs/vparallel
phase=np.zeros_like(xs);phase[1:]=np.cumsum((freq_over_v[1:]+freq_over_v[:-1])/2*np.diff(xs))*5
np.savetxt(P/'mirror.dat',np.column_stack((xs,.65/np.sqrt(bs)*np.sin(phase))),fmt='%.10f')
# Equal-radius fission: continuous circles, elastic reversals, full return.
J=np.array([[0.,-1.],[1.,0.]])
rot=lambda t:np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
pos=np.zeros(2);v1=np.array([-2.,0.]);v2=-v1/2;fission=[]
for k in range(6):
 center=pos+J@v1
 r1=center+rot(4*math.pi/3)@(pos-center)
 r2=center+rot(-2*math.pi/3)@(pos-center)
 assert np.linalg.norm(r1-r2)<1e-12
 w1=rot(4*math.pi/3)@v1;w2=rot(-2*math.pi/3)@v2
 assert np.linalg.norm(w1+2*w2)<1e-12
 pos=r1;v1=-w1;v2=-w2;fission.append(pos.tolist())
assert np.linalg.norm(pos)<1e-12 and np.linalg.norm(v1-[-2,0])<1e-12
# Bucket diagram and formula, theta=30 degrees.
R=2.3;theta=math.pi/6;delta=2*math.atan2(math.cos(theta),R+math.sin(theta))
C=np.array([-math.cos(theta),-R-math.sin(theta)]);P0=np.array([0.,-R]);Q=np.array([-R*math.sin(delta),-R*math.cos(delta)])
assert abs(np.linalg.norm(Q-C)-1)<1e-12
assert abs(np.dot(P0-C,[-math.sin(theta),math.cos(theta)]))<1e-12
# Exact damped trajectories initial derivatives and equations.
def spiral(t):
 aa=.22;w=1.;v=2.;e=math.exp(-aa*t)
 return np.array([v/(aa*aa+w*w)*(aa+e*(-aa*math.cos(t)+w*math.sin(t))),v/(aa*aa+w*w)*(w+e*(-aa*math.sin(t)-w*math.cos(t)))])
def drift(t):
 aa=.25;w=1.;b=1.;uinf=1j*b/(aa+1j*w)
 return uinf*t+(3-uinf)*(1-np.exp(-(aa+1j*w)*t))/(aa+1j*w)
h=1e-5
assert np.linalg.norm((spiral(h)-spiral(-h))/(2*h)-[2,0])<1e-8
assert abs((drift(h)-drift(-h))/(2*h)-3)<1e-8
out=Path(__file__).resolve().parent.parent/'build/revision-ch21-ch22-20260920'
out.mkdir(parents=True,exist_ok=True)
(out/'geometry-checks.json').write_text(json.dumps({'checks_passed':True,'layer_joins':joins,'layer_turning_point':[x,y],'fission_collision_points_r_equals_2':fission,'bucket_delta':delta,'damped_initial_velocities_verified':True},indent=2))
print('Geometry checks passed; exact field-layer coordinates generated.')
