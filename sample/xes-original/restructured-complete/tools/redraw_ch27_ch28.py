"""Deterministic optical constructions; writes TikZ, never raster source crops."""
import math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parents[1]/'build/revision-ch27-ch28-20260923'
checks=[]
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def mul(a,s):return (a[0]*s,a[1]*s)
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def norm(a):return math.hypot(*a)
def unit(a):return mul(a,1/norm(a))
def polar(r,d):return (r*math.cos(math.radians(d)),r*math.sin(math.radians(d)))
def coord(p):return '(%.7f,%.7f)'%p
def ray(a,b,style='DeepBlue,thick,->'):return f'\\draw[{style}] {coord(a)}--{coord(b)};\n'
def line(a,b):return ray(a,b,'gray,dashed,thin')
def label(p,s,pos='above'):return f'\\node[{pos},fill=none,inner sep=2pt] at {coord(p)} {{{s}}};\n'
def point(p,s,pos='below'):return f'\\fill {coord(p)} circle (1.2pt);\n'+label(p,s,pos)
def circle(c,r,style='thick'):return f'\\draw[{style}] {coord(c)} circle ({r});\n'
def path(points,style='thick'):return '\\draw['+style+'] '+'--'.join(map(coord,points))+';\n'
def curve(points,style='thick'):return '\\draw['+style+'] plot coordinates {'+' '.join(map(coord,points))+'};\n'
def arc(c,r,a,b):return curve([add(c,polar(r,a+(b-a)*i/100)) for i in range(101)])
def axis(a,b):return ray(a,b,'gray,thin,->')
def scope(x,y,s):return f'\\begin{{scope}}[shift={{{coord((x,y))}}}]\n{s}\\end{{scope}}\n'
def fig(s,caption):return '\\begin{center}\n\\begin{tikzpicture}[>=Latex,font=\\small,every node/.style={fill=none}]\n'+s+'\\end{tikzpicture}\n\\figcap{'+caption+'}\n\\end{center}\n'
def macro(name,s,caption):return '\\newcommand{\\'+name+'}{%\n'+fig(s,caption)+'}\n'
def reflect(d,n):return sub(d,mul(n,2*dot(d,n)))
def refract(d,n,eta):
 # n points into the transmitted medium, d.n positive.
 t=sub(d,mul(n,dot(d,n)));st=mul(t,eta)
 assert dot(st,st)<=1+1e-12
 return add(st,mul(n,math.sqrt(max(0,1-dot(st,st)))))
def verify(name,value,tol=1e-7):
 assert abs(value)<tol,(name,value)
 checks.append({'check':name,'residual':value,'tolerance':tol})
def spherehit(p,d,r):return add(p,mul(d,-2*dot(p,d)))
def lensmark(x,h=1.5):return ray((x,-h),(x,h),'DeepBlue,thick,<->')

ch27=[];ch28=[]
# Atmosphere: all shells concentric; tangent at observer differs from far direction.
s=''
c=(0,-3.5)
for r in (3.5,3.8,4.1):s+=arc(c,r,35,145)
s+=point((0,0),'$O$','below left')+line((-3,0),(3,0))+label((3.2,-.2),'局地水平','right')
# outgoing reversed ray has slope .45 at O and .13 far away, curvature toward Earth for incoming light.
pts=[(x,.13*x+.32*(1-math.exp(-x))) for x in [i*.035 for i in range(101)]]
s+=curve(pts,'DeepBlue,thick,<-')+line((0,0),(3.5,1.575))+line((0,0),(3.5,.455))
s+=label((3.5,1.58),'视方向','right')+label((3.5,.38),'真实方向','right')+label((-1.5,-.4),'地表','below')
t=''
for r in (.45,.85,1.25):t+=arc((0,0),r,-50,50)
t+=ray((0,0),(1.65,0))+label((.8,-1.15),'同心波面与法线','below')
s+=scope(-4.0,2.5,t)
ch27.append(macro('AtmosphereWavefrontPanel',s,'图 19.1：观测点 $O$ 在地表；按到眼光线的切线反向看，太阳视方向高于真实方向。左侧为同心波面。'))
# exact plane reflections
s=ray((-1.4,1.4),(0,0))+ray((0,0),(1.4,1.4))+path([(-1.8,0),(1.8,0)])+line((0,-.2),(0,1.8))+label((-.4,.8),'$i$')+label((.4,.8),'$r$')
s+=label((0,-.35),'反射角等于入射角','below')
t='';p=(-.9,-.1);q=add(p,mul(polar(1,40),1.8));d2=polar(1,-80)
t+=path([add(p,polar(1.1,200)),add(p,polar(1.1,20))])+path([add(q,polar(1.1,160)),add(q,polar(1.1,-20))])
t+=ray(add(p,(-1.5,0)),p)+ray(p,q)+ray(q,add(q,mul(d2,1.4)))+label((0,-.7),'两镜夹角 $40^\circ$','below')+label((0,-1.1),'方向转过 $80^\circ$','below')
s=scope(-4.1,0,s)+scope(.3,0,t)
t=path([(-1.2,1.3),(-1.2,-1.2),(1.6,-1.2)])
pts=[(1.5,1),(-1.2,-.35),(.5,-1.2),(2.0,-.45)]
for a,b in zip(pts,pts[1:]):t+=ray(a,b)
verify('corner antiparallel',dot(unit(sub(pts[1],pts[0])),unit(sub(pts[-1],pts[-2])))+1)
t+=label((.15,-1.5),'直角反射器','below')
ch27.append(macro('ReflectionPanel',s+scope(4.7,0,t),'图 19.3--19.4：单镜、双镜与直角反射器。各段在镜面交点处等角反射。'))
# Snell interface + prism, true face intersection; deviation curve separate figure.
s=path([(-2,0),(2,0)])+line((0,-1.8),(0,1.8))+ray((-1.5,1.5),(0,0))+ray((0,0),(.801784,-1.5))
s+=label((-1.6,.4),'$n_1=1$')+label((-1.5,-1.1),'$n_2=1.5$')+label((-.35,.9),'$i$')+label((.75,-.85),'$r$','right')+line((.72,-.85),(.2,-.7))
t=path([(-1.5,-1),(0,1.598076),(1.5,-1),(-1.5,-1)])
p=(-.8,1.598076-math.sqrt(3)*.8);ni=polar(1,-30);d=polar(1,18)
t+=ray(sub(p,mul(d,1.7)),p)+line(add(p,mul(ni,-.55)),add(p,mul(ni,.7)))
for n,col in [(1.50,'red!65!black'),(1.53,'Blue')]:
 e=refract(d,ni,1/n)
 # right boundary y=1.598076-sqrt(3)*x
 dt=(1.598076-math.sqrt(3)*p[0]-p[1])/(e[1]+math.sqrt(3)*e[0]);q=add(p,mul(e,dt))
 no=polar(1,30);o=refract(e,no,n)
 t+=ray(p,q,col+',thick,->')+ray(q,add(q,mul(o,1.45)),col+',thick,->')
 if n==1.50:t+=line(add(q,mul(no,-.5)),add(q,mul(no,.65)))
 verify('prism exit on face '+str(n),q[1]+math.sqrt(3)*q[0]-1.598076)
 verify('prism Snell '+str(n),n*(e[0]*no[1]-e[1]*no[0])-(o[0]*no[1]-o[1]*no[0]))
t+=label((0,1.0),'$A$')+label((0,-1.3),'各颜色只在界面改变方向','below')
ch27.append(macro('RefractionPrismPanel',scope(-3.2,0,s)+scope(3.0,0,t),'图 19.6--19.7：平界面折射与棱镜色散；虚线为界面法线。'))
n=1.5;A=math.radians(60);rc=math.asin(1/n);data=[]
for j in range(161):
 r1=A-rc+1e-5+(2*rc-A-2e-5)*j/160;i=math.asin(n*math.sin(r1));de=i+math.asin(n*math.sin(A-r1))-A
 data.append((math.degrees(i),math.degrees(de)))
t=axis((0,0),(6.1,0))+axis((0,0),(0,3.3))
t+=curve([((i-20)/12,(d-35)/10) for i,d in data],'DeepBlue,thick')
imin=math.degrees(math.asin(n*math.sin(A/2)));dmin=2*imin-60
pm=((imin-20)/12,(dmin-35)/10)
t+=point(pm,'')+line(pm,(2.4,1.15))+label((2.4,1.2),'对称光路','above')
for i in (30,50,70,90):t+=label(((i-20)/12,-.08),f'${i}^\circ$','below')
for d in (40,50,60):t+=label((-.05,(d-35)/10),f'${d}^\circ$','left')
t+=label((6.1,0),'$i_1$','right')+label((0,3.3),'$\delta$')+label((4,2.8),'$A=60^\circ,\ n=1.5$')
ch27.append(macro('PrismDeviationDiagram',t,'偏向角随入射角的变化；最低点是两内部折射角相等的光路。\\label{ch27:fig:deviation}'))
# fiber and Cartesian oval solve positive branch near vertex.
t=path([(-2.6,-.65),(2.6,-.65)])+path([(-2.6,.65),(2.6,.65)])+line((-2.6,-.9),(2.6,-.9))+line((-2.6,.9),(2.6,.9))
ps=[(-2.6,0),(-1.95,.65),(-.65,-.65),(.65,.65),(1.95,-.65),(2.6,0)]
for a,b in zip(ps,ps[1:]):t+=ray(a,b)
t+=label((0,1.05),'包层 $n_2<n_1$')+label((0,-1.05),'芯层内，反射点均在边界','below')
def ovalx(y):
 lo,hi=0,1.5
 for _ in range(70):
  x=(lo+hi)/2;val=math.hypot(x+2,y)+1.6*math.hypot(x-3,y)-6.8
  if val>0:lo=x
  else:hi=x
 return (lo+hi)/2
ys=[-1.05+2.1*j/100 for j in range(101)];cvs=[(ovalx(y),y) for y in ys]
u=curve(cvs)+axis((-2.3,0),(3.4,0))+point((-2,0),'$O$')+point((3,0),'$I$')
p=(ovalx(.85),.85)
u+=ray((-2,0),p)+ray(p,(3,0))+point(p,'$P$','above')+label((0,-1.35),'$OP+nPI=s_o+ns_i$','below')
verify('oval equal optical path',norm(sub(p,(-2,0)))+1.6*norm(sub(p,(3,0)))-6.8)
ch27.append(macro('FiberFermatPanel',scope(-3.7,0,t)+scope(3,0,u),'图 19.10：左为平直芯包界面导光；右为等光程非球面，离轴点 $P$ 也连接同一物、像点。'))
# mirror actual circular intersection; rotating plane through wall origin
R=3;p=polar(R,25);d=(1,0);o=reflect(d,unit(p));m=add(p,mul(o,-p[1]/o[1]))
t=arc((0,0),R,-38,38)+axis((-.7,0),(3.6,0))+point((0,0),'$C$')+point((R,0),'$V$','below right')+point(m,'$M$','below')
t+=ray((-1,p[1]),p)+ray(p,m)+line((0,0),p)+point(p,'')+line(p,add(p,(-.55,.45)))+label(add(p,(-.6,.5)),'$P$','above left')
th=math.radians(22);C=(-math.tan(th),1);D=(0,1+math.tan(th)*math.tan(2*th))
u=path([(0,-.3),(0,2.6)])+path([(0,0),(-.95,.95/math.tan(th))])+point((0,0),'$O$','below')+point((0,1),'$A$','right')+point(C,'$C$','left')+point(D,'$D$','right')
u+=ray((0,1),C)+ray(C,D)+arc((0,0),.42,90,112)+label((-.8,.35),r'$\theta$','left')+line((-.75,.4),(-.08,.42))+ray((.6,0),(.6,1),'gray,<->')+label((.6,.5),'$d$','right')
ch27.append(macro('SphericalMirrorRotatingDiagram',scope(-3,0,t)+scope(4,0,u),'图 19.11：左侧球面镜的 $P$ 在圆周上，$CP$ 为法线；右侧转镜的转轴 $O$ 位于墙上。'))
# cylinder: normal incidence at right mirror and two Snell transitions
R=2;a=(-math.sqrt(3),1);b=(-math.sqrt(3),-1);p=(2,0)
t=circle((0,0),2)+arc((0,0),2.035,-27,27)+axis((-2.4,0),(2.5,0))
for aa,bb in [((-3.2,1),a),(a,p),(p,b),(b,(-3.2,-1))]:t+=ray(aa,bb)
t+=line(a,(0,0))+line(b,(0,0))+point(a,'$A$','above left')+point(b,'$B$','below left')+point(p,'$P$','right')+point((0,0),'$C$')
t+=ray((-3.5,-1),(-3.5,1),'gray,<->')+label((-3.5,0),'$d$','left')+label((1.5,-2.2),'右侧镀银；两外部光线反向平行','below')
verify('cylinder reflection',norm(sub(reflect(unit(sub(p,a)),(1,0)),unit(sub(b,p)))))
ch27.append(macro('CylinderDiagram',t,'图 19.12：$d$ 是入射与出射两平行线的间距；圆内两段只在反射面 $P$ 处折转。'))
# absorbing shell critical ray tangent + gradient
b=2;a=.8;n=1.5;rho=n*a;p=(-math.sqrt(b*b-rho*rho),rho);di=refract((1,0),mul(unit(p),-1),1/n);tangent=sub(p,mul(di,dot(p,di)))
t=circle((0,0),b)+circle((0,0),a,'very thick')+ray((-3,rho),p)+ray(p,tangent)+line(p,(0,0))+line((0,0),tangent)+point(tangent,'')+label(add(tangent,(.25,.25)),'$T$','above right')
t+=ray((0,0),(2,0),'gray,<->')+label((1,0),'$b$','below')+label((-.4,-.2),'$a$')+label((0,-2.25),'内球面为吸收层','below')
verify('shell tangent',dot(tangent,di));verify('shell tangent radius',norm(tangent)-a)
u=axis((-.6,0),(3.2,0))+axis((0,-.3),(0,3.2))+label((3.2,0),'$x$','right')+label((0,3.2),'$y$')
points=[(3*math.sin(q),3*(1-math.cos(q))) for q in [math.acos(.4)*j/100 for j in range(101)]]
u+=ray((-.6,0),(0,0))+curve(points,'DeepBlue,thick,->')+line((0,3),points[-1])+line((0,3),(0,0))+point((0,3),'$C$','left')+label((.8,2.1),'$R$','below')+label((1.9,-.3),r'$x=R\sin\theta$','below')+label((1.9,-.75),r'$y=R(1-\cos\theta)$','below')
ch27.append(macro('ShellAndGradientDiagram',scope(-3,0,t)+scope(3,0,u),'图 19.13--19.14：临界折射线在 $T$ 与吸收层相切；梯度光线从原点水平入射并向上弯曲。'))
# lake full angle 30 degrees, houses outside, shoreline feet, actual optimum
beta=math.radians(15);h=.8;c=2.8;k=2*math.sin(beta);tt=c-k*h/math.sqrt(1-k*k)
e1=(-math.sin(beta),-math.cos(beta));e2=(math.sin(beta),-math.cos(beta));C=mul(e1,c);A=add(C,mul((-math.cos(beta),math.sin(beta)),h));B=(-A[0],A[1]);P=mul(e1,tt);Q=mul(e2,tt)
t=path([mul(e1,3.7),(0,0),mul(e2,3.7)])+line((0,0),(0,-3.6))+line((0,0),A)+line(A,C)+point((0,0),'$D$','above')+point(A,'$A$','left')+point(B,'$B$','right')+point(C,'$C$','below right')+point(P,'')+point(Q,'')+label((-1.65,-1.8),'$P$','left')+line((-1.6,-1.8),P)+label(add(Q,(.18,.3)),'$Q$','above right')
for aa,bb in [(A,P),(P,Q),(Q,B)]:t+=ray(aa,bb)
t+=label((-1.65,-2.85),'$h$','left')+line((-1.6,-2.85),mul(add(A,C),.5))+label((-1,.5*A[1]),'$l$','left')+arc((0,0),.65,-105,-75)+line((.7,-.8),(.05,-.55))+label((.75,-.85),r'$\alpha$','right')+label((0,-3.8),'湖湾内划船，岸外步行','below')
# slab object to eye upper ray, exact Snell and extension
theta=.26;tg=math.asin(math.sin(theta)/1.5);x0=-2.5;x1=-.5;x2=1;xeye=2.8;y1=2*math.tan(theta);y2=y1+1.5*math.tan(tg);ye=y2+1.8*math.tan(theta);xiv=x2-y2/math.tan(theta)
u=path([(x1,-.6),(x1,2)])+path([(x2,-.6),(x2,2)])+axis((-2.7,0),(3,0))+point((x0,0),'$O$','below')+point((xiv,0),'$I$','below')
for aa,bb in [((x0,0),(x1,y1)),((x1,y1),(x2,y2)),((x2,y2),(xeye,ye))]:u+=ray(aa,bb)
u+=line((xiv,0),(x2,y2))+label((xeye,ye),'眼','above')+label((.25,1.6),'$n$')
for aa,bb,ss in [(x0,x1,'$S$'),(x1,x2,'$D$'),(x2,xeye,'$L$')]:u+=ray((aa,-.65),(bb,-.65),'gray,<->')+label(((aa+bb)/2,-.65),ss,'below')
ch27.append(macro('FisherPlateDiagram',scope(-3.1,1.8,t)+scope(3.6,-.2,u),r'图 19.15--19.16：湖湾顶角为完整的 $\alpha$，$A,B$ 在陆地；平行玻璃板的入出射方向平行，$I$ 在末段反向延长线上。'))
# rainbows exact sphere intersection and Snell
rain=''
for order,shift in [(1,-3),(2,3)]:
 n=4/3;i=math.asin(math.sqrt(((order+1)**2-n*n)/((order+1)**2-1)));p=(-2*math.cos(i),2*math.sin(i));d=(1,0)
 t=circle((0,0),2)+ray(add(p,(-1.1,0)),p)+line((0,0),p)+point(p,'')+label(add(p,(.6,.65)),'$A$','above right')+line(p,add(p,(.55,.6)))
 d=refract(d,mul(unit(p),-1),1/n)
 ideg=math.degrees(i);ddeg=math.degrees(math.atan2(d[1],d[0]))
 t+=line(p,add(p,mul(unit(p),.65)))+arc(p,.32,180-ideg,180)+arc(p,.43,-ideg,ddeg)
 t+=label(add(p,polar(.75,180-ideg/2)),'$i$','above')+label(add(p,polar(.80,(-ideg+ddeg)/2)),'$r$','right')
 for j in range(order):
  q=spherehit(p,d,2);t+=ray(p,q)+line((0,0),q);verify(f'rainbow {order} hit {j}',norm(q)-2);d=reflect(d,unit(q));p=q
 q=spherehit(p,d,2);t+=ray(p,q)+line((0,0),q);o=refract(d,unit(q),n);t+=ray(q,add(q,mul(o,1.4)))+label((0,-3.3),'主虹：一次内反射' if order==1 else '次虹：两次内反射','below')
 rain+=scope(shift,0,t)
ch27.append(macro('RainbowDiagram',rain,'主虹与次虹的球内路径；虚线为法线，$i,r$ 在入射点 $A$ 测量。离球后的箭头指向接收这束光的观察者。\\label{ch27:fig:rainbow}'))

# sphere refraction exact selected ray, near-axis limit separate in text
R=2;u=4;n=2;phi=.22;c=(R,0);a=(R-R*math.cos(phi),R*math.sin(phi));inc=unit(sub(a,(-u,0)));d=refract(inc,unit(sub(c,a)),1/n);image=add(a,mul(d,-a[1]/d[1]))
t=arc(c,R,145,215)+axis((-4.6,0),(max(6,image[0]+.4),0))+point((-u,0),'$S$')+point((0,0),'$V$','below left')+point(c,'$C$')+point(image,'$P$')+point(a,'$A$','above left')+line(c,a)+ray((-u,0),a)+ray(a,image)+label((-2,1),'$n_1=1$')+label((3,1),'$n_2=2$')
ch28.append(macro('SphereRefractionPanel',t,'图 20.1：球面顶点 $V$、球心 $C$ 与球面点 $A$；图中 $P$ 为所示有限孔径光线的轴交点。'))
# Virtual sign two actual plane boundaries with n ratios. left real object -> virtual image; right virtual object -> real image.
s=''
for typ,xshift in [(0,-3.2),(1,3.2)]:
 t=path([(0,-1.4),(0,1.4)])+axis((-2.7,0),(2.7,0))
 for sg in (-1,1):
  a=(0,sg*.55)
  if typ==0:
   inc=unit(sub(a,(-2,0)));out=refract(inc,(1,0),1/1.5);q=add(a,mul(out,2.5));imx=-a[1]/out[1]*out[0]
   t+=ray((-2,0),a)+ray(a,q)+line((imx,0),a)
  else:
   inc=unit(sub((2,0),a));out=refract(inc,(1,0),1.5);q=add(a,mul(out,-a[1]/out[1]));imx=q[0]
   t+=ray(sub(a,mul(inc,2.5)),a)+line(a,(2,0))+ray(a,q)
 t+=point((imx,0),'')+line((imx,0),(imx,-.6))+label((imx,-.65),'虚像' if typ==0 else '实像','below')
 ox=-2 if typ==0 else 2
 t+=point((ox,0),'')+line((ox,0),(ox,.85))+label((ox,.9),'实物' if typ==0 else '虚物','above')
 t+=label((0,-1.6),'空气到玻璃' if typ==0 else '玻璃到空气','below');s+=scope(xshift,0,t)
ch28.append(macro('VirtualSignPanel',s,'图 20.2：左图出射光的反向延长线交于虚像；右图虚线为未遇界面时的会聚路径。有限孔径轴交点随角度略变。'))
# Eye schematic: anatomical closed contours + explicit equivalent thin-plane model
t='\\draw[thick] (0,0) ellipse (2.4 and 1.3);\n'
t+='\\draw[thick] (-1.3,-.7) .. controls (-1.65,-.2) and (-1.65,.2) .. (-1.3,.7) .. controls (-.95,.2) and (-.95,-.2) .. cycle;\n'
for h0 in (-.55,.55):t+=ray((-3.6,h0),(-1.3,h0))+ray((-1.3,h0),(2.4,0))
t+=line((-1.3,-1),(-1.3,1))+label((-2.3,1.15),'角膜')+label((-.8,1.5),'晶状体')+line((-.8,1.4),(-1.1,.45))+point((2.4,0),'视网膜','right')+label((0,-1.55),'虚线平面表示眼的等效折射系统','below')
ch28.append(macro('EyePanel',t,'图 20.3：远物平行光在正常眼视网膜同一点会聚。光线按等效薄系统画，解剖轮廓用于辨认结构。'))
# Apparent depth exact from Snell +/- height .45; both directions panels
s=''
for mode,shift in [(0,-3),(1,3)]:
 n1,n2=(4/3,1) if mode==0 else (1,4/3);depth=1.8;yobj=-depth
 t=path([(-2,0),(2,0)])+point((0,yobj),'')+line((0,yobj),(-.7,yobj))+label((-.75,yobj),'$O$','left')+line((0,-2),(0,1.6))
 for sx in (-.6,.6):
  p=(sx,0);d=refract(unit(sub(p,(0,yobj))),(0,1),n1/n2);im=(0,-abs(sx)*d[1]/abs(d[0]));t+=ray((0,yobj),p)+ray(p,add(p,mul(d,1.4)))+line(p,im)
 t+=point(im,'')+line(im,(.7,im[1]))+label((.75,im[1]),'$I$','right')+label((-1.3,-1),'水' if mode==0 else '空气','left')+label((-1.3,.6),'空气中的眼' if mode==0 else '水中的眼','left')
 s+=scope(shift,0,t)
ch28.append(macro('ApparentDepthDiagram',s,'图 20.4：从空气看水中（左）和从水中看空气（右）。虚像取所示两斜光线的反向交点；近轴极限为 $|v|=n_2u/n_1$。'))
# six closed lenses, labels clear
t=''
forms=[r'(-.12,-1).. controls (-.65,-.3) and (-.65,.3)..(-.12,1)--(.12,1)..controls(.65,.3)and(.65,-.3)..(.12,-1)--cycle',r'(0,-1)--(0,1)--(.12,1)..controls(.65,.3)and(.65,-.3)..(.12,-1)--cycle',r'(-.1,-1)..controls(.3,-.3)and(.3,.3)..(-.1,1)--(.1,1)..controls(.9,.3)and(.9,-.3)..(.1,-1)--cycle',r'(-.55,-1)..controls(-.05,-.3)and(-.05,.3)..(-.55,1)--(.55,1)..controls(.05,.3)and(.05,-.3)..(.55,-1)--cycle',r'(0,-1)--(0,1)--(.65,1)..controls(.1,.3)and(.1,-.3)..(.65,-1)--cycle',r'(-.45,-1)..controls(.45,-.3)and(.45,.3)..(-.45,1)--(.2,1)..controls(.6,.3)and(.6,-.3)..(.2,-1)--cycle']
names=['双凸','平凸','会聚弯月','双凹','平凹','发散弯月']
for j,(f,name) in enumerate(zip(forms,names)):
 t+=scope(-5+j*2,0,'\\draw[thick,fill=DeepBlue!5] '+f+';\n'+label((0,-1.3),name,'below'))
# Preserve the source's second subfigure: finite thickness, both radii and interfaces.
ys=[-.8+1.6*j/100 for j in range(101)]
front=[(2-math.sqrt(4-y*y),y) for y in ys]
back=[(-1.4+math.sqrt(4-y*y),y) for y in reversed(ys)]
O=(-4,0);C1=(2,0);C2=(-1.4,0);P=(2-math.sqrt(4-.35**2),.35)
d=refract(unit(sub(P,O)),unit(sub(C1,P)),1/1.54)
w=sub(P,C2);travel=-dot(w,d)+math.sqrt(dot(w,d)**2-dot(w,w)+4)
Q=add(P,mul(d,travel));out=refract(d,unit(sub(Q,C2)),1.54);I=add(Q,mul(out,-Q[1]/out[1]))
u=path(front+back+[front[0]],'thick,fill=DeepBlue!5')+axis((-4.4,0),(I[0]+.45,0))
u+=point(O,'$O$','above')+point(I,'$I$','above')+point(P,'$P$','above left')+point(Q,'$Q$','above right')
u+=ray(O,P)+ray(P,Q)+ray(Q,I)+line(C1,P)+line(C2,Q)
u+=point(C1,'')+point(C2,'')+line(C1,(C1[0],-.9))+line(C2,(C2[0],-.9))
u+=label((C1[0],-.95),'$C_1$','below')+label((C2[0],-.95),'$C_2$','below')
u+=label((-1.2,1),'$C_1P=R_1$')+label((2.2,1),'$C_2Q=|R_2|$')
u+=ray((-4,-1.5),(0,-1.5),'gray,<->')+label((-2,-1.5),'$u$','below')
u+=ray((.6,-1.5),(I[0],-1.5),'gray,<->')+label(((.6+I[0])/2,-1.5),'$v$','below')
verify('two-surface lens exit on second sphere',norm(sub(Q,C2))-2)
verify('two-surface lens outward second normal',norm(out)-1)
ch28.append(macro('ThinLensPanel',t+scope(0,-4,u),'图 20.5：上为六种闭合透镜截面，置于空气中时左三种会聚、右三种发散；下为两球面分别折射的光路，$C_1P,C_2Q$ 是两面的半径和法线。'))
# three rays lens f1.5, object4.2
f=100/(.54*6)*.06;u=4.2;v=f*u/(u-f);h=1.5;ih=-v/u*h
t=axis((-4.8,0),(4,0))+lensmark(0,1.85)+ray((-u,0),(-u,h),'black,thick,->')+label((-u,h),'物')+ray((v,0),(v,ih),'black,thick,->')+label((v,ih),'像','below')
for x,ss in [(-2*f,'$2F$'),(-f,'$F$'),(f,"$F'$"),(2*f,"$2F'$")]:
 t+=point((x,0),'')+label((x,-.5 if x<0 else .2),ss,'below' if x<0 else 'above')
for hh in (h,0,ih):t+=ray((-u,h),(0,hh))+ray((0,hh),(v,ih))
verify('third lens ray through front focal point',h+(ih-h)*((u-f)/u))
ch28.append(macro('LensImagingDiagram',t,r'图 20.6：$u=70.0\,\mathrm{cm}$、$f\approx30.9\,\mathrm{cm}$、$v\approx55.2\,\mathrm{cm}$ 时的三条近轴特征光线；通过物方焦点的那条出射后平行光轴。'))
# magnifier image same; pupil at x .3 tall enough; naked eye baseline separate panel
t=axis((-3.6,0),(1.7,0))+lensmark(0,1.2)+point((-1.5,0),'$F$')+ray((-1,0),(-1,.65),'black,thick,->')+label((-1,.65),'物','left')+ray((-3,0),(-3,1.95),'black,thick,->')+label((-3,1.95),'虚像')
for hh in (.65,0):
 out_slope=(hh-1.95)/3;t+=ray((-1,.65),(0,hh))+ray((0,hh),(1.2,hh+1.2*out_slope))+line((-3,1.95),(0,hh))
t+=path([(.4,-.34),(.4,.50)],'Gold,very thick')+label((.5,1.25),'眼瞳位置','right')+line((.8,1.2),(.4,.5))
u=ray((-1.6,0),(-1.6,.65),'black,thick,->')+ray((-1.6,.65),(1.4,0))+line((-1.6,0),(1.4,0))+label((1.4,0),'裸眼','right')+ray((-1.6,-.45),(1.4,-.45),'gray,<->')+label((-.1,-.45),'$L_0$','below')+label((0,1.2),r'$\theta_0\simeq H/L_0$')
ch28.append(macro('MagnifierDiagram',scope(-2.6,0,t)+scope(3.8,.7,u),'图 20.7：左为放大镜的正立虚像及进入眼瞳的光；右为裸眼在明视距离观察同样大小物体的基准视角。'))
# spherical mirror exact finite ray
c=(0,0);R=3;O=(-3,0);p=polar(R,14);d=unit(sub(p,O));out=reflect(d,unit(p));I=add(p,mul(out,-p[1]/out[1]))
t=arc(c,R,-28,28)+axis((-3.6,0),(3.6,0))+point(O,'$O$')+point(c,'$C$')+point((R,0),'$V$','below right')+point(p,'')+line(p,add(p,(-.55,.45)))+label(add(p,(-.6,.5)),'$P$','above left')+point(I,'$I$')+line(c,p)+ray(O,p)+ray(p,I)
ch28.append(macro('SphericalMirrorDiagram',t,'图 20.8：球面镜真实反射光路，$CP$ 是法线。所示有限高度轴交点趋向近轴像点，但不与所有孔径光线严格重合。'))
# aplanatic closed crescent: c2=0 R2=2 c1=-1.333 R1=2.7, aperture +-0.9
n=1.5;R=2;c1=(-R/n,0);Q=(-n*R,0)
left=[(c1[0]+math.sqrt(2.7**2-y*y),y) for y in [-.9+1.8*j/80 for j in range(81)]]
right=[(math.sqrt(R*R-y*y),y) for y in [.9-1.8*j/80 for j in range(81)]]
t=path(left+right+[left[0]])+axis((-3.4,0),(3.5,0))+point(Q,'$Q$','below')+point(c1,'$C_1$','above')+point((0,0),'')+line((0,0),(0,-.65))+label((0,-.7),'$C_2$','below')
for yy in (-.75,.75):
 p=(math.sqrt(R*R-yy*yy),yy);di=unit(sub(p,c1));first=add(c1,mul(di,2.7));o=unit(sub(p,Q));t+=ray(c1,first)+ray(first,p)+ray(p,add(p,mul(o,1.1)))+line(Q,p)+line((0,0),p)
 verify('aplanatic '+str(yy),norm(sub(p,Q))-n*norm(sub(p,c1)))
t+=label((1.4,1.05),'$S_1$','left')+label((2.1,1.05),'$S_2$','right')
u='\\draw[pattern=north east lines] (-1.8,.9) rectangle (1.8,1.6);\\draw[pattern=north east lines] (-1.8,-1.6) rectangle (1.8,-.9);\n'
u+=scope(-1,0,'\\draw[thick,fill=DeepBlue!5] '+forms[3]+';\n')+scope(1.1,0,'\\draw[thick,fill=DeepBlue!5] '+forms[0]+';\n')
u+=label((-1,-2.55),'凹透镜','below')+label((1.1,-2.55),'凸透镜','below')+label((-2.1,0),'室外','left')+label((2.1,0),'室内','right')+ray((-1,-1.95),(1.1,-1.95),'gray,<->')+label((.05,-1.95),r'$2.1\,\mathrm{cm}$','below')
ch28.append(macro('SpecialAndCatEyePanel',scope(-3.2,0,t)+scope(4,0,u),'图 20.9--20.10：无球差透镜的 $Q$ 为虚像，虚线是出射光反向延长线；猫眼的两透镜装在同一贯通门孔中。'))
# silver lens equivalent folded plane model + dimensioned prism actual diagonal
u=3;v=1;h=.9
t=axis((-3.5,0),(.5,0))+path([(0,-1.4),(0,1.4)],'very thick,double')+ray((-u,0),(-u,h),'black,thick,->')+ray((-v,0),(-v,-h/3),'black,thick,->')
for yy in (.9,0):t+=ray((-u,h),(0,yy))+ray((0,yy),(-v,-h/3))
t+=label((-3,h),'$H$')+label((-1,-.5),'$-H/3$','below')+label((0,1.5),'薄透镜与银面重合的等效平面')+label((-2,-1.2),'$u=2f,\ v=2f/3$','below')
# triangle vertices(0,1.2),(1.2,1.2),(1.2,0); ray down .6 hits diagonal y=x then right
q=path([(0,1.2),(1.2,1.2),(1.2,0),(0,1.2)])+ray((.6,2.4),(.6,.6))+ray((.6,.6),(4.8,.6))
q+=ray((.6,2.4),(.9,2.4),'black,thick,->')+label((.6,2.4),'$A$','above left')+label((.9,2.4),'$B$','above right')
q+=scope(0,.6,lensmark(2.4,1.4))+path([(4.2,-.8),(4.2,2)],'DeepBlue,thick')+ray((4.2,2),(4.2,1.7))+ray((4.2,-.8),(4.2,-.5))+label((2.4,2.15),'$f_1=10$')+label((4.2,2.15),'$f_2=-10$')
q+=ray((-.25,1.2),(-.25,2.4),'gray,<->')+label((-.25,1.8),'$6$','left')+ray((-.25,0),(-.25,1.2),'gray,<->')+label((-.25,.6),'$6$','left')
for a,b,ss in [(1.2,2.4,'$10$'),(2.4,4.2,'$15$')]:q+=ray((a,-.6),(b,-.6),'gray,<->')+label(((a+b)/2,-.6),ss,'below')
q+=label((2.4,-1.6),'长度单位：cm（横向比例压缩）','below')
ch28.append(macro('SilveredAndTrainPanel',scope(-3.7,0,t)+scope(1.3,0,q),'图 20.11：左为镀银薄透镜的等效折返光路；右为累次成像，光轴在棱镜的斜面上转过直角，$AB$ 位于上方。'))
# A generic two-stage real image (the intermediate image is not another element).
u=3;f1=1;f2=1;L=4;h=.6;v1=f1*u/(u-f1);u2=L-v1;v2=f2*u2/(u2-f2);h1=-v1*h/u;h2=-v2*h1/u2
t=axis((-3.4,0),(6.2,0))+lensmark(0,1.8)+lensmark(L,1.8)
for x,yy,ss in [(-u,h,'物 $O$'),(v1,h1,'中间像 $I_1$'),(L+v2,h2,'最终像 $I_2$')]:
 t+=ray((x,0),(x,yy),'black,thick,->')
 if yy<0:t+=line((x,yy),(x,1))+label((x,1.05),ss,'above')
 else:t+=label((x,yy),ss,'above')
for y in (.4,0):
 inc=(y-h)/u;d1=inc-y/f1;yl=y+L*d1;d2=d1-yl/f2
 t+=ray((-u,h),(0,y))+ray((0,y),(L,yl))+ray((L,yl),(L+v2,h2))
 verify('two-lens final convergence '+str(y),yl+v2*d2-h2)
t+=label((0,1.9),'$f_1$')+label((L,1.9),'$f_2$')+ray((0,-2),(L,-2),'gray,<->')+label((L/2,-2),'$D$','below')
ch28.append(macro('SequentialImagingDiagram',t,r'两透镜逐级成像：$I_1$ 同时是第二透镜的物，$u_2=D-v_1$；实际光线穿过 $I_1$ 时没有折转。\label{ch28:fig:sequential}'))
# supplemental microscope and telescope, computed by thin lens equations
def two_lens(fo,fe,L,obj=None,theta=None,title=''):
 t=axis((-2,0),(L+2,0))+lensmark(0,2.1)+lensmark(L,2.1)
 t+=label((0,2.2),'物镜')+label((L,2.2),'目镜')
 if obj:
  u,h=obj;v=fo*u/(u-fo);ih=-v*h/u;t+=ray((-u,0),(-u,h),'black,thick,->')+point((v,ih),'')
 else:v=fo;ih=fo*theta;t+=point((v,ih),'')
 t+=line((v,ih),(v-.5,1.15))+label((v-.5,1.2),'中间实像' if obj else '中间像点','above')
 t+=line((v,-1.5),(v,1.4))
 for y in (.65,-.15):
  inc=(y-h)/u if obj else theta
  out=inc-y/fo;ye=y+L*out;oe=out-ye/fe
  start=(-u,h) if obj else (-1.6,y-1.6*inc)
  t+=ray(start,(0,y))+ray((0,y),(L,ye))+ray((L,ye),(L+1.8,ye+1.8*oe))
  verify(title+' intermediate intersection '+str(y),y+v*out-ih)
  verify(title+' afocal output '+str(y),oe+ih/fe)
 t+=ray((fo,-1.85),(v,-1.85),'gray,<->') if obj else ''
 if obj:t+=label(((fo+v)/2,-1.85),'$L$','below')+point((fo,0),'')+line((fo,0),(fo,-.95))+label((fo,-1),"$F'_o$",'below')
 t+=ray((v,-2.5),(L,-2.5),'gray,<->')+label(((v+L)/2,-2.5),'$f_e$','below')
 return t
mic=two_lens(1,1.2,6.2,(1.25,.3),title='microscope')
tel=two_lens(4,1.5,5.5,theta=-.12,title='telescope')
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'forty-second-section/diagrams.tex').write_text('\n'.join(ch27))
(ROOT/'forty-third-section/diagrams.tex').write_text('\n'.join(ch28))
(OUT/'microscope.tex').write_text(fig(mic,'显微镜的中间像在目镜前焦面；两透镜之间不发生折转。$L$ 从物镜后焦点量到中间像平面。\\label{ch28:fig:microscope}'))
(OUT/'telescope.tex').write_text(fig(tel,'无焦望远镜：公共焦面处光线相交但不折转；目镜后的两条出射线严格平行。\\label{ch28:fig:telescope}'))
(OUT/'geometry-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print(f'{len(ch27)} + {len(ch28)} diagrams; {len(checks)} geometric assertions passed.')
