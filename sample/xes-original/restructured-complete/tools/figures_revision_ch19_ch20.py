"""Deterministic electrostatic geometry. All labels have transparent backgrounds."""
import json, csv, io, urllib.request, shutil
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc
from matplotlib.font_manager import FontProperties
from build_review_ch19_ch20 import book,BASE
OUT=book.BOOK/'assets/revision-ch19-ch20';OUT.mkdir(parents=True,exist_ok=True)
BLUE='#355f79';GRAY='#888888';GOLD='#a77827';INK='#30343a'
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':11,'pdf.fonttype':42,'axes.linewidth':.65})
ZH=FontProperties(fname='/System/Library/Fonts/Supplemental/Songti.ttc',size=10)
checks={}
def canvas(w=7,h=3.5):
 f,a=plt.subplots(figsize=(w,h));a.set_aspect('equal');a.axis('off');return f,a
def save(f,name):
 f.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.1)
 f.savefig(OUT/(name+'.png'),bbox_inches='tight',pad_inches=.1,dpi=180);plt.close(f)
def line(a,x,y,style='-',color=BLUE,lw=.9):a.plot(x,y,style,color=color,lw=lw)
def arrow(a,p,q,color=BLUE):a.annotate('',xy=q,xytext=p,arrowprops={'arrowstyle':'->','color':color,'lw':.9,'shrinkA':0,'shrinkB':0})
def label(a,p,s,dx=0,dy=0,**kw):a.text(p[0]+dx,p[1]+dy,s,ha='center',va='center',color=INK,**kw)
def charge(a,x,q):
 a.plot([x],[0],'o',ms=4,color=BLUE if q>0 else INK)
 label(a,(x,-.23),('$+' if q>0 else '$-')+(str(abs(q)) if abs(q)!=1 else '')+'q$',dy=-.04)
def fields(X,Y,qs,dim=3):
 V=np.zeros_like(X);Ex=V.copy();Ey=V.copy();F=V.copy()
 for x,q in qs:
  r=np.maximum(np.hypot(X-x,Y),1e-8)
  V+=q/r if dim==3 else -q*np.log(r)
  Ex+=q*(X-x)/r**dim;Ey+=q*Y/r**dim;F+=q*(X-x)/r
 return V,Ex,Ey,F
def contours(a,X,Y,U,levels,color=GRAY,ls='--',field=None):
 cs=a.contour(X,Y,U,levels=sorted(levels),colors=color,linewidths=.65,linestyles=ls)
 if field:
  for segs in cs.allsegs:
   for seg in segs:
    if len(seg)<25:continue
    # A small tangent arrow at an interior point; orient by the exact field.
    i=int(.55*len(seg));p=seg[max(0,i-3)];q=seg[min(len(seg)-1,i+3)]
    if np.linalg.norm(q-p)<.04:continue
    e=np.array(field(*((p+q)/2)))
    if np.dot(q-p,e)<0:p,q=q,p
    mid=(p+q)/2;u=(q-p)/np.linalg.norm(q-p);arrow(a,mid-.07*u,mid+.07*u,color)
 return cs
def mesh(xlim=(-4,4),ylim=(-2.6,2.6),n=601):return np.meshgrid(np.linspace(*xlim,n),np.linspace(*ylim,n))

def apollonius():
 f,a=canvas(7,3.2);xp,xm=-2.7,1.1;mu=2
 c=(mu**2*xm-xp)/(mu**2-1);R=mu*abs(xm-xp)/(mu**2-1)
 P=np.array([c+R*np.cos(2.05),R*np.sin(2.05)])
 a.add_patch(Circle((c,0),R,fill=False,color=BLUE,lw=1.2))
 for x,s in [(xp,'$+Q$'),(xm,'$-q$')]:a.plot(x,0,'o',color=INK,ms=4);label(a,(x,-.3),s);line(a,[x,P[0]],[0,P[1]],'--',GRAY)
 a.plot(*P,'o',color=INK,ms=3);label(a,P,'$P$',dy=.25)
 label(a,((xp+P[0])/2,P[1]/2),'$r_+$',dx=-.2,dy=.13)
 label(a,((xm+P[0])/2,P[1]/2),'$r_-$',dx=.22)
 label(a,(c,-R-.4),r'$Q=2q,\quad r_+=2r_-$')
 a.set_xlim(-3.3,c+R+.4);a.set_ylim(-R-.7,R+.5)
 theta=np.linspace(0,2*np.pi,1001);xx=c+R*np.cos(theta);yy=R*np.sin(theta)
 checks['zero-potential-distance-ratio-error']=float(np.max(abs(np.hypot(xx-xp,yy)/np.hypot(xx-xm,yy)-mu)))
 save(f,'zero-potential')

def line_families():
 f,a=canvas();d=1.55;X,Y=mesh();rp=np.hypot(X-d,Y);rm=np.hypot(X+d,Y)
 V=np.ma.masked_where(np.minimum(rp,rm)<.10,np.log(rm/rp))
 contours(a,X,Y,V,[-2,-1.2,-.6,0,.6,1.2,2],BLUE,'-')
 # Exact circle arcs through the two line charges. The same circle has two branches.
 for cy in [-2,-.7,0,.7,2]:
  r=np.hypot(d,cy);t=np.linspace(0,2*np.pi,1800);xx=r*np.cos(t);yy=cy+r*np.sin(t)
  mask=(np.hypot(xx-d,yy)>.12)&(np.hypot(xx+d,yy)>.12)
  xx=np.where(mask,xx,np.nan);yy=np.where(mask,yy,np.nan);line(a,xx,yy,'--',GRAY,.7)
  for top in [True,False]:
   py=cy+(r if top else -r);E=fields(np.array(0.),np.array(py),[(d,1),(-d,-1)],2)[1:3]
   arrow(a,(.10,py),(-.10,py),GRAY)
 line(a,[-4,4],[0,0],'--',GRAY,.65)
 a.plot([-d,d],[0,0],'o',ms=4,color=INK)
 label(a,(-d,-3.0),r'$-\lambda,\ x=-a$');label(a,(d,-3.0),r'$+\lambda,\ x=a$')
 a.set_xlim(-4,4);a.set_ylim(-2.7,2.7)
 checks['two-lines-equations']='V=ln(r_minus/r_plus); field circles R^2-cy^2=a^2 exactly'
 save(f,'two-lines')

def rod():
 f,a=canvas();d=1.5;t=np.linspace(0,2*np.pi,900)
 for A in [1.75,2.2,2.9,3.7]:
  B=np.sqrt(A*A-d*d);line(a,A*np.cos(t),B*np.sin(t),'-',BLUE)
 for eta in [-.92,-.7,-.4,0,.4,.7,.92]:
  xi=np.linspace(1,4.5,700);x=d*xi*eta;y=d*np.sqrt((xi*xi-1)*(1-eta*eta))
  for sign in [-1,1]:
   line(a,x,sign*y,'--',GRAY,.75);i=110;arrow(a,(x[i],sign*y[i]),(x[i+20],sign*y[i+20]),GRAY)
 line(a,[-d,d],[0,0],'-',INK,2.8)
 a.set_xlim(-4,4);a.set_ylim(-2.7,2.7);save(f,'finite-rod')
 checks['finite-rod-focus-error']=float(max(abs(A*A-(np.sqrt(A*A-d*d))**2-d*d) for A in [1.75,2.2,2.9,3.7]))

def scattering():
 f,a=canvas(7,4);B0=.7
 for b,col in zip([.65,1.4,2.6],[BLUE,GOLD,GRAY]):
  theta=2*np.arctan(B0/b);e=np.sqrt(1+(b/B0)**2);alpha=np.arccos(1/e);p=b*b/B0
  psi=np.linspace(alpha-.0001,-alpha+.0001,6000);r=p/(e*np.cos(psi)-1);ang=np.pi/2+theta/2+psi
  x=r*np.cos(ang);y=r*np.sin(ang);mask=(x>-7)&(x<6)&(y<6)
  line(a,x[mask],y[mask],'-',col,1.2)
  idx=np.where(mask&(y>3))[0];i=idx[-min(200,len(idx))] if len(idx)>200 else np.where(mask)[0][len(np.where(mask)[0])//2]
  direction=np.array([x[i+1]-x[i],y[i+1]-y[i]]);direction/=np.linalg.norm(direction)
  mid=np.array([x[i],y[i]]);arrow(a,mid-.13*direction,mid+.13*direction,col)
  line(a,[-7,-4],[b,b],'--',col,.6)
  # outgoing asymptote through the focal offset, not through the nucleus.
  # Outgoing straight line has signed distance -b from origin.
  tangent=np.array([np.cos(theta),np.sin(theta)]);normal=np.array([-np.sin(theta),np.cos(theta)])
  base=b*normal;u=np.linspace(1,7,100);xy=base[:,None]+tangent[:,None]*u
  line(a,xy[0],xy[1],':',col,.6)
  checks[f'scattering-b{b}-angle-deg']=float(np.degrees(theta))
 a.plot(0,0,'o',ms=6,color=INK);label(a,(.2,-.35),'$+Ze$')
 arrow(a,(-6.5,-.6),(-5,-.6));label(a,(-5.7,-.9),r'$v_\infty$')
 origin=np.array([2.,-1.8]);theta=2*np.arctan(B0/1.4)
 arrow(a,origin,origin+np.array([2.,0]),GOLD)
 arrow(a,origin,origin+2*np.array([np.cos(theta),np.sin(theta)]),GOLD)
 a.add_patch(Arc(origin,1.6,1.6,theta1=0,theta2=np.degrees(theta),color=GOLD,lw=.8))
 label(a,origin+np.array([1.1,.5]),r'$\Theta$',fontsize=12)
 for xx,b,col in zip([-4.8,0.,4.8],[.65,1.4,2.6],[BLUE,GOLD,GRAY]):
  line(a,[xx-1.1,xx-.6],[-2.7,-2.7],'-',col,1.2);label(a,(xx+.4,-2.7),rf'$b={b:g}$',fontsize=11)
 a.set_xlim(-7,6.3);a.set_ylim(-3.2,6);save(f,'rutherford')

def point_panels():
 X,Y=mesh((-3,3),(-2.2,2.2))
 for name,qs in [('quadrupole', [(-1,-1),(0,2),(1,-1)]),('unequal',[(-1,4),(1,-1)]),('dipole-exact',[(-.7,-1),(.7,1)])]:
  f,a=canvas();V,Ex,Ey,F=fields(X,Y,qs)
  mask=sum((np.hypot(X-x,Y)<.14) for x,q in qs)>0
  lev=np.linspace(-sum(abs(q) for x,q in qs)+.12,sum(abs(q) for x,q in qs)-.12,25)
  contours(a,X,Y,np.ma.masked_where(mask,F),lev,BLUE,'-',lambda x,y:fields(np.array(x),np.array(y),qs)[1:3])
  for x,q in qs:
   a.plot(x,0,'o',ms=4,color=BLUE if q>0 else INK)
   label(a,(x,-2.5),('$+' if q>0 else '$-')+(str(abs(q)) if abs(q)!=1 else '')+'q$')
  a.set_xlim(-3,3);a.set_ylim(-2.2,2.2);save(f,name)
 f,axs=plt.subplots(1,3,figsize=(9,3.2))
 for a in axs:a.set_aspect('equal');a.axis('off');a.set_xlim(-2.6,2.6);a.set_ylim(-2,2)
 a=axs[0]
 for x in np.linspace(-2,2,6):line(a,[x,x],[-1.4,1.4],'--',GRAY)
 for y in [-1,0,1]:arrow(a,(-2.2,y),(2.2,y))
 label(a,(0,-2.5),'(a)');a=axs[1]
 for R in [.45,.9,1.4,1.9]:a.add_patch(Circle((0,0),R,fill=False,ls='--',lw=.65,color=GRAY))
 for t in np.linspace(0,2*np.pi,12,endpoint=False):arrow(a,.18*np.array([np.cos(t),np.sin(t)]),1.9*np.array([np.cos(t),np.sin(t)]))
 a.plot(0,0,'o',ms=7,color=INK);a.text(0,0,'+',ha='center',va='center',color='white',fontsize=7)
 label(a,(0,-2.5),'(b)')
 a=axs[2];qs=[(-.7,-1),(.7,1)];V,Ex,Ey,F=fields(X,Y,qs);mask=(np.hypot(X-.7,Y)<.16)|(np.hypot(X+.7,Y)<.16)
 contours(a,X,Y,np.ma.masked_where(mask,V),[-4,-2,-1,-.5,0,.5,1,2,4])
 contours(a,X,Y,np.ma.masked_where(mask,F),[-1.9,-1.6,-1.2,-.8,-.4],BLUE,'-',lambda x,y:fields(np.array(x),np.array(y),qs)[1:3])
 for x,q in qs:
  a.plot(x,0,'o',ms=7,color=INK);a.text(x,0,'+' if q>0 else '−',ha='center',va='center',color='white',fontsize=7)
 label(a,(0,-2.5),'(c)');save(f,'equipotentials')

def image_sphere():
 f,a=canvas();C=np.array([1.15,0.]);R=1.62;Q=np.array([-4.1,0.]);L=np.linalg.norm(Q-C);I=C+R*R/L**2*(Q-C)
 P=C+R*np.array([np.cos(2.05),np.sin(2.05)])
 a.add_patch(Circle(C,R,fill=False,lw=1.2,color=BLUE))
 for p,s,off in [(Q,'$+Q$',(-.1,-.3)),(I,'$-q$',(-.1,-.32)),(C,'$C$',(.15,-.2)),(P,'$P$',(.15,.23))]:
  a.plot(*p,'o',ms=3,color=INK);label(a,p,s,*off)
 for p,s,off in [(Q,'$r_1$',(-.2,.2)),(I,'$r_2$',(-.25,0)),(C,'$R$',(.25,.1))]:
  line(a,[p[0],P[0]],[p[1],P[1]],'--',GRAY);label(a,(p+P)/2,s,*off)
 line(a,[Q[0],C[0]],[0,0],':',GRAY)
 for y,p1,p2,s in [(-2.0,Q[0],C[0],'$L$'),(-1.2,I[0],C[0],'$l$')]:
  a.annotate('',xy=(p1,y),xytext=(p2,y),arrowprops={'arrowstyle':'<->','lw':.7,'color':INK});label(a,((p1+p2)/2,y-.18),s)
 a.set_xlim(-4.7,3.2);a.set_ylim(-2.5,2.1);save(f,'grounded-sphere')
 checks['sphere-image-Ll-minus-R2']=float(L*np.linalg.norm(I-C)-R*R)
 checks['sphere-P-radius-error']=float(abs(np.linalg.norm(P-C)-R))
 checks['sphere-distance-ratio-error']=float(abs(np.linalg.norm(P-Q)/np.linalg.norm(P-I)-L/R))

def uniform_sphere(dielectric=False):
 f,a=canvas();R=1.;eps=4.;chi=(eps-1)/(eps+2) if dielectric else 1.
 X,Y=mesh((-3.2,3.2),(-2,2));r=np.maximum(np.hypot(X,Y),1e-8)
 V=-X+chi*X/r**3;flux=.5*Y**2*(1+2*chi/r**3)
 if dielectric:
  V=np.where(r<1,-3*X/(eps+2),V);flux=np.where(r<1,.5*eps*3/(eps+2)*Y**2,flux)
 else:V=np.ma.masked_where(r<1,V);flux=np.ma.masked_where(r<1,flux)
 def E(x,y):
  rr=np.hypot(x,y)
  if rr<1:return (3/(eps+2),0)
  return (1+chi*(3*x*x/rr**5-1/rr**3),3*chi*x*y/rr**5)
 contours(a,X,Y,flux,[.06,.18,.4,.7,1.,1.4,2.,2.6],BLUE,'-',E)
 if not dielectric:contours(a,X,Y,V,[-2,-1.3,-.6,0,.6,1.3,2])
 a.add_patch(Circle((0,0),1,fill=False,lw=1.2,color=INK))
 arrow(a,(-2.9,2.22),(-1.9,2.22));label(a,(-2.4,2.43),'$E_0$')
 arrow(a,(1.8,-2.22),(2.9,-2.22));label(a,(3.03,-2.22),'$z$')
 label(a,(0,2.42) if dielectric else (0,-.17),r'$\varepsilon_r=4$' if dielectric else '$E=0$',fontsize=12)
 a.set_xlim(-3.3,3.3);a.set_ylim(-2.4,2.6);save(f,'dielectric-sphere' if dielectric else 'uniform-sphere')
 checks['dielectric-normal-D-relative-error']=abs(eps*3/(eps+2)-(1+2*chi)) if dielectric else 0

def sphere_images(d=1.55,R=.75,desired=(1,0)):
 # Exact repeated Kelvin reflections. Each foreign source is cancelled on the other sphere.
 def basis(side):
  qs=[];x=(-d,d)[side];q=1.;owner=side
  for i in range(45):
   qs.append((x,q,owner));other=1-owner;c=(-d,d)[other];dist=abs(x-c)
   x=c+R*R/(x-c);q=-R/dist*q;owner=other
  return qs
 bs=[basis(0),basis(1)]
 M=np.array([[sum(q for x,q,o in b if o==i) for b in bs] for i in [0,1]])
 weights=np.linalg.solve(M,np.array(desired));qs=[(x,q*w) for b,w in zip(bs,weights) for x,q,o in b]
 return qs
def conductor_pair(neutral=True):
 f,a=canvas();d=1.55;R=.75;qs=sphere_images(d,R,(1,0) if neutral else (1,-1));X,Y=mesh()
 V,Ex,Ey,F=fields(X,Y,qs);mask=(np.hypot(X-d,Y)<R)|(np.hypot(X+d,Y)<R)
 contours(a,X,Y,np.ma.masked_where(mask,V),np.linspace(.08,.95,9) if neutral else [-.9,-.6,-.3,0,.3,.6,.9])
 contours(a,X,Y,np.ma.masked_where(mask,F),np.linspace(-.95,.95,21) if neutral else np.linspace(.06,1.96,20),BLUE,'-',lambda x,y:fields(np.array(x),np.array(y),qs)[1:3])
 for c,s in [(-d,'$+Q$'),(d,'$Q=0$' if neutral else '$-Q$')]:
  a.add_patch(Circle((c,0),R,fill=False,color=INK,lw=1.2));label(a,(c,0),s)
 t=np.linspace(0,2*np.pi,1000);res=[]
 for c in [-d,d]:
  v,*_=fields(c+R*np.cos(t),R*np.sin(t),qs);res.append(float(np.ptp(v)))
 checks['neutral-pair-boundary-range' if neutral else 'capacitor-pair-boundary-range']=res
 a.set_xlim(-4,4);a.set_ylim(-2.6,2.6);save(f,'conductor-pair' if neutral else 'capacitor-pair')

def cylinders():
 f,a=canvas();d=1.7;R=.85;focus=np.sqrt(d*d-R*R);X,Y=mesh();rp=np.hypot(X-focus,Y);rm=np.hypot(X+focus,Y)
 V=np.log(rm/rp);F=np.arctan2(Y,X-focus)-np.arctan2(Y,X+focus)
 mask=(np.hypot(X-d,Y)<R)|(np.hypot(X+d,Y)<R)
 contours(a,X,Y,np.ma.masked_where(mask,V),[-1,-.5,0,.5,1])
 contours(a,X,Y,np.ma.masked_where(mask,F),[-2.7,-2.1,-1.5,-.9,-.3,.3,.9,1.5,2.1,2.7],BLUE,'-',lambda x,y:fields(np.array(x),np.array(y),[(focus,1),(-focus,-1)],2)[1:3])
 for c,s in [(-d,r'$-\lambda$'),(d,r'$+\lambda$')]:a.add_patch(Circle((c,0),R,fill=False,color=INK,lw=1.2));label(a,(c,0),s)
 a.annotate('',xy=(-d,-1.3),xytext=(d,-1.3),arrowprops={'arrowstyle':'<->','lw':.7});label(a,(0,-1.5),'$L$')
 line(a,[d,d+R],[.25,.25],'-',INK,.6);label(a,(d+R/2,.45),'$R$')
 a.set_xlim(-3.5,3.5);a.set_ylim(-2.2,2.2);save(f,'two-cylinders');checks['cylinders-focus-identity']=float(d*d-focus*focus-R*R)

def dipole_vectors():
 f,axs=plt.subplots(1,2,figsize=(9,3.4));a,b=axs
 for ax in axs:ax.set_aspect('equal');ax.axis('off')
 P=np.array([3.,1.5]);th=np.arctan2(P[1],P[0]);er=np.array([np.cos(th),np.sin(th)]);et=np.array([-np.sin(th),np.cos(th)])
 vr=1.2*er;vt=1.2*.5*np.tan(th)*et
 charge(a,-.32,-1);charge(a,.32,1);line(a,[0,P[0]],[0,P[1]],'--',GRAY);line(a,[0,3.5],[0,0],':',GRAY)
 arrow(a,P,P+vr);arrow(a,P,P+vt);arrow(a,P,P+vr+vt,GOLD)
 line(a,[P[0]+vr[0],P[0]+vr[0]+vt[0]],[P[1]+vr[1],P[1]+vr[1]+vt[1]],':',GRAY)
 label(a,P,'$P$',dx=-.12,dy=-.2);label(a,P+vr,'$E_r$',dx=.2,dy=-.14)
 label(a,P+vt,r'$E_\theta$',dx=-.22,dy=.08);label(a,P+vr+vt,'$E$',dx=.1,dy=.23)
 a.add_patch(Arc((0,0),1.6,1.6,theta1=0,theta2=np.degrees(th),color=GRAY,lw=.7));label(a,(1.05,.2),r'$\theta$')
 label(a,(1.6,1.0),'$r$',dx=-.12);arrow(a,(-.3,-.65),(.4,-.65));label(a,(.7,-.65),'$p$');a.set_xlim(-.8,4.8);a.set_ylim(-1.1,3)
 theta=np.linspace(.015,np.pi-.015,1000)
 for C in [1,2,3,4]:
  r=C*np.sin(theta)**2
  for sg in [-1,1]:
   x=r*np.cos(theta);y=sg*r*np.sin(theta);line(b,x,y)
   i=470;arrow(b,(x[i],y[i]),(x[i+35],y[i+35]))
 b.plot(0,0,'o',color=INK,ms=3);arrow(b,(1.4,0),(2.1,0));label(b,(2.35,0),'$p$')
 label(b,(0,-4.7),r'$r=C\sin^2\theta$');b.set_xlim(-2,2.7);b.set_ylim(-5,4.3)
 save(f,'dipole-far');checks['dipole-components-ratio']=float(np.linalg.norm(vt)/np.linalg.norm(vr))

def plate_edges():
 f,a=canvas(7,3.5);N=110;edges=2*np.sin(np.linspace(-np.pi/2,np.pi/2,N+1));left=edges[:-1];right=edges[1:];mid=(left+right)/2;h=.55
 def F(u,y):
  rr=np.maximum(np.hypot(u,y),1e-30);return u*np.log(rr)-u+abs(y)*np.arctan(u/np.maximum(abs(y),1e-30))
 def influence(x,y,y0):return -(F(x[...,None]-left,y[...,None]-y0)-F(x[...,None]-right,y[...,None]-y0))
 A=influence(mid,np.full(N,h),h)-influence(mid,np.full(N,h),-h);q=np.linalg.solve(A,np.ones(N))
 X,Y=mesh((-3.7,3.7),(-2.1,2.1),421);Ex=np.zeros_like(X);Ey=Ex.copy();V=Ex.copy()
 for y0,sg in [(h,1),(-h,-1)]:
  for l,r,qq in zip(left,right,q*sg):
   yy=Y-y0;u=X-l;v=X-r
   Ex+=qq*np.log(np.maximum(np.hypot(u,yy),1e-30)/np.maximum(np.hypot(v,yy),1e-30))
   yy=np.where(abs(yy)<1e-10,1e-10,yy)
   Ey+=qq*(np.arctan(u/yy)-np.arctan(v/yy))
 mask=((abs(Y-h)<.022)|(abs(Y+h)<.022))&(abs(X)<2.01)
 seeds=np.array([(x,0) for x in np.r_[np.linspace(-3.6,-2.2,4),np.linspace(-1.8,1.8,9),np.linspace(2.2,3.6,4)] ]+[(x,y) for x in [-2.,-1.,0.,1.,2.] for y in [-2.,2.]])
 a.streamplot(X[0],Y[:,0],np.ma.masked_where(mask,Ex),np.ma.masked_where(mask,Ey),density=2,start_points=seeds,color=BLUE,linewidth=.8,arrowsize=.8,broken_streamlines=False,maxlength=20)
 for yy,s in [(h,'$+$'),(-h,'$-$')]:
  line(a,[-2,2],[yy,yy],'-',INK,2.5)
 a.set_xlim(-3.7,3.7);a.set_ylim(-2.1,2.1);save(f,'plate-edges')
 test=(left*.35+right*.65);Vtest=(influence(test,np.full(N,h),h)-influence(test,np.full(N,h),-h))@q
 checks['plate-potential-relative-error-away-from-collocation']=float(np.max(abs(Vtest-1)))

def gallery():
 f,axs=plt.subplots(1,3,figsize=(10.5,3.5));X,Y=mesh((-3,3),(-3,3),401)
 for j,a in enumerate(axs):
  a.set_aspect('equal');a.axis('off');a.set_xlim(-3,3);a.set_ylim(-3,3)
  if j<2:
   qs=[(-1,0,1),(1,0,-1)] if j==0 else [(0,1,1),(0,-1,1),(-1,0,-1),(1,0,-1)]
   Ex=np.zeros_like(X);Ey=Ex.copy();mask=np.zeros(X.shape,bool)
   for xx,yy,q in qs:
    R=np.maximum(np.hypot(X-xx,Y-yy),1e-8);mask|=R<.17
    Ex+=q*(X-xx)/R**3;Ey+=q*(Y-yy)/R**3
  else:
   # Lienard-Wiechert field, c=1, x_q(t)=0.2 sin(2.5t), observation time 0.
   tr=-np.hypot(X,Y)
   for _ in range(20):
    xr=.2*np.sin(2.5*tr);R=np.maximum(np.hypot(X-xr,Y),1e-8);nx=(X-xr)/R
    beta=.5*np.cos(2.5*tr);tr-=(tr+R)/(1-nx*beta)
   xr=.2*np.sin(2.5*tr);R=np.maximum(np.hypot(X-xr,Y),1e-8);nx=(X-xr)/R;ny=Y/R
   beta=.5*np.cos(2.5*tr);acc=-1.25*np.sin(2.5*tr);den=(1-nx*beta)**3
   Ex=(1-beta**2)*(nx-beta)/(den*R**2)-acc*ny**2/(den*R)
   Ey=(1-beta**2)*ny/(den*R**2)+acc*nx*ny/(den*R)
   mask=np.hypot(X,Y)<.18;qs=[(0,0,1)]
  a.streamplot(X[0],Y[:,0],np.ma.masked_where(mask,Ex),np.ma.masked_where(mask,Ey),density=.42,color=BLUE,linewidth=.65,arrowsize=.65,broken_streamlines=False,maxlength=20)
  for xx,yy,q in qs:
   a.plot(xx,yy,'o',color=BLUE if q>0 else INK,ms=8,zorder=5);a.text(xx,yy,'+' if q>0 else '−',ha='center',va='center',color='white',fontsize=7,zorder=6)
  a.text(0,-3.8,['(a) 异号电荷','(b) 四极分布','(c) 振荡电荷的瞬时场'][j],ha='center',fontproperties=ZH)
 save(f,'field-gallery')

def apollonius_example():
 f,a=canvas(7,3);d=2.;mu=2.;c=-d/(mu*mu-1);R=d*mu/(mu*mu-1)
 a.add_patch(Circle((c,0),R,fill=False,color=BLUE,lw=1.2))
 line(a,[-2.3,3],[0,0],'-',GRAY,.65)
 for x,s in [(0,'$-q$'),(d,'$+Q$')]:a.plot(x,0,'o',color=INK,ms=4);label(a,(x,-.24),s)
 a.plot(c,0,'+',ms=4,color=INK);label(a,(c,-.25),'$x_c$')
 a.annotate('',xy=(c-R,1.7),xytext=(c+R,1.7),arrowprops={'arrowstyle':'<->','color':GRAY,'lw':.7});label(a,(c,1.92),'$2R_0$')
 label(a,(2.,1.05),r'$Q=2q$');label(a,(2.,.62),r'$a=2$')
 a.set_xlim(-2.4,3);a.set_ylim(-1.6,2.1);save(f,'apollonius-example')

def ionization():
 url='https://physics.nist.gov/cgi-bin/ASD/ie.pl?spectra=H-Hs%20I&units=1&format=2&order=0&at_num_out=on&el_name_out=on&ion_charge_out=on&e_out=0&unc_out=on&biblio=on'
 path=OUT/'nist-first-ionization.csv'
 if not path.exists():path.write_bytes(urllib.request.urlopen(url).read())
 rows=[]
 for row in csv.DictReader(io.StringIO(path.read_text())):
  clean={k:v.strip('=" ') for k,v in row.items() if k and v is not None}
  if clean.get('Ion Charge')!='0':continue
  rows.append((int(clean['At. num']),float(clean['Ionization Energy (eV)']),clean['Prefix']))
 assert [r[0] for r in rows]==list(range(1,109))
 cats={
 '碱金属':{3,11,19,37,55,87},'碱土金属':{4,12,20,38,56,88},
 '卤素':{9,17,35,53,85},'稀有气体':{2,10,18,36,54,86},
 '镧系':set(range(57,72)),'锕系':set(range(89,104)),
 '类金属':{5,14,32,33,51,52,84},'其他非金属':{1,6,7,8,15,16,34},
 '其他金属':{13,31,49,50,81,82,83},'过渡金属':set(range(21,31))|set(range(39,49))|set(range(72,81))|set(range(104,109))}
 assert set.union(*cats.values())==set(range(1,109))
 f,a=plt.subplots(figsize=(9,4.7));data=np.array([(z,e) for z,e,p in rows]);a.plot(*data.T,color='#aaa',lw=.6,zorder=1)
 for (name,zs),col,mark in zip(cats.items(),plt.get_cmap('tab10').colors,['o','s','^','D','v','p','h','*','X','+']):
  sub=[(z,e,p) for z,e,p in rows if z in zs];a.scatter([v[0] for v in sub],[v[1] for v in sub],s=17,marker=mark,color=col,label=name,zorder=3)
  est=[v for v in sub if v[2] in ['[','(']]
  if est:a.scatter([v[0] for v in est],[v[1] for v in est],s=10,facecolor='white',edgecolor=col,lw=.5,zorder=4)
 for z,s in [(2,'He'),(10,'Ne'),(18,'Ar'),(36,'Kr'),(54,'Xe'),(86,'Rn')]:
  val=rows[z-1][1];a.annotate(s,(z,val),xytext=(3,6),textcoords='offset points',fontsize=9)
 a.set_xlim(0,110);a.set_ylim(0,28);a.set_xlabel('原子序数 Z',fontproperties=ZH);a.set_ylabel('第一电离能 / eV',fontproperties=ZH,labelpad=10)
 a.grid(axis='y',alpha=.2);a.spines[['top','right']].set_visible(False);a.legend(prop=ZH,ncol=5,loc='upper center',bbox_to_anchor=(.5,-.17),frameon=False,columnspacing=1.4)
 f.subplots_adjust(bottom=.26);save(f,'ionization');checks['ionization']={'neutral_elements':len(rows),'source':url,'range':[1,108],'categories':10}

if __name__=='__main__':
 for fn in [apollonius,line_families,rod,scattering,point_panels,image_sphere,uniform_sphere,lambda:uniform_sphere(True),conductor_pair,lambda:conductor_pair(False),cylinders,dipole_vectors,plate_edges,gallery,apollonius_example,ionization]:fn()
 BASE.mkdir(parents=True,exist_ok=True);(BASE/'geometry-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
 print(json.dumps(checks,ensure_ascii=False,indent=2))
