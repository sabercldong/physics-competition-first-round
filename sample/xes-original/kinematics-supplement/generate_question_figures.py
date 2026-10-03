"""Build question-only vector views for all 58 source question figure groups.

Maintained geometry is reused only when it describes givens. Answer overlays,
optimising constructions and conclusions are deliberately removed per case.
The original solution diagrams remain intact and are not counted as question
figures. This file is the maintained specification; data/question-figures.tex
and its JSON mapping are generated artifacts.
"""
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'restructured-complete/tools'))
from build_restructured import balanced_argument

def macro(name):
    for filename in ['figures.tex','figures-ch03.tex','figures-ch04.tex']:
        text=(ROOT/filename).read_text()
        m=re.search(r'\\newcommand\{\\'+name+r'\}(?:\[[^]]+\])?\s*\{',text)
        if m:
            return balanced_argument(text,m.end()-1)[0]
    raise KeyError(name)

def name(n): return 'KQuestion'+chr(65+n//26)+chr(65+n%26)
def label(n): return f'question-figure-2-{n}'
def caption(n,text): return '\\figcap{题图：'+text+'}\\label{'+label(n)+'}'
def diagram(n,body,cap,opts='>=Latex,scale=.9'):
    return '\\begin{center}\\begin{minipage}{.97\\linewidth}\\centering\n\\begin{tikzpicture}['+opts+']\n'+body+'\n\\end{tikzpicture}\n'+caption(n,cap)+'\n\\end{minipage}\\end{center}'
def clone(n,source,cap,drop=(),replace=(),append=''):
    body=macro(source)
    body='\n'.join(l for l in body.splitlines() if not any(x in l for x in drop))
    for old,new in replace:
        assert old in body,(n,old)
        body=body.replace(old,new)
    m=re.search(r'\\figcap\{',body)
    assert m,(n,source)
    _,end=balanced_argument(body,m.end()-1)
    body=body[:m.start()]+caption(n,cap)+body[end:]
    if append:
        body=body.replace(r'\end{tikzpicture}',append+'\n'+r'\end{tikzpicture}',1)
    return body

Q={}
Q[1]=diagram(1,r'''
\draw[kaxis] (-.25,0)--(6.6,0) node[right]{$t/\mathrm s$};
\draw[kaxis] (0,-2.7)--(0,1.2) node[above]{$x/\mathrm m$};
\foreach \t in {1,...,6}{\draw (\t,0)--(\t,.08);\node[above=2pt] at (\t,0){\t};}
\foreach \y/\v in {-2.4/-60,-1.6/-40,-.8/-20,.8/20}{\draw (0,\y)--(.08,\y);\node[left] at (0,\y){$\v$};}
\node[below left] at (0,0){$O$};
''','按表中数据在空坐标系中作图。')
Q[2]=diagram(2,r'''
\foreach \dx/\i in {0/1,4.3/2,8.6/3}{\begin{scope}[xshift=\dx cm]
\draw[kaxis] (-.2,0)--(3.1,0) node[right]{$t$};
\draw[kaxis] (0,-.6)--(0,1.8) node[above]{$x$};
\node[below left] at (0,0){$O$};\node at (1.4,-.85){(\i)};
\end{scope}}
''','分别画出三个运动函数的图像。',opts='>=Latex,scale=.85')
Q[3]=diagram(3,r'''
\foreach \dx/\mode in {0/1,6.2/2}{\begin{scope}[xshift=\dx cm]
\draw[kaxis] (-.2,0)--(4.6,0) node[right]{$t$};
\draw[kaxis] (0,-1.25)--(0,1.3) node[above]{$x$};
\ifnum\mode=1
\draw[kcurve,domain=0:4.25,samples=200] plot(\x,{.8*sin(280*\x)});
\else
\draw[kcurve,domain=0:4.25,samples=240] plot(\x,{1.05*exp(-.85*\x)*cos(450*\x)});
\fi
\node[below left] at (0,0){$O$};\node at (2,-1.6){(\mode)};
\end{scope}}
''','两个质点的一维位置随时间变化，坐标轴未给定数值比例。')
Q[6]=clone(6,'ExampleTwoSixGraphs','从左到右为三幅给定的位置—时间图像。',
    drop=[r'\draw[vector]',r'\node[clearlabel,below]'])
Q[7]=clone(7,'ExampleTwoSevenGraphs','左图给出速度随时间的变化，右侧 A—D 为待选的位置图像。')
Q[8]=clone(8,'ExampleTwoEightGraphs','三个运动过程的速度—时间图像，求相应时间内的路程。',drop=[r'\fill[Blue!12]'])
Q[17]=clone(17,'FreeFallMeetingDiagram','A 球从上方释放，B 球从下方以初速度 $v_0$ 竖直抛出，初始间距为 $h$。')
Q[19]=clone(19,'BounceDiagram','初始高度为 $H$；一次碰撞前、后的速率分别用 $u$、$eu$ 表示。')
Q[22]=diagram(22,r'''
\foreach \x in {-4,-3,-2,-1,1,2,3,4,5}{\draw[RuleGray,thin] (\x,-5.5)--(\x,-.8) (\x,.1)--(\x,5);}
\foreach \y in {-5,-4,-3,-2,-1,1,2,3,4,5}{\draw[RuleGray,thin] (-4,\y)--(-1.05,\y) (.12,\y)--(5.5,\y);}
\draw[kaxis] (-4.2,0)--(5.8,0) node[right]{$x$};
\draw[kaxis] (0,-5.7)--(0,5.3) node[above]{$y$};
\foreach \x in {-3,-2,-1,1,2,3,4,5}\node[below=2pt] at (\x,0){$\x$};
\foreach \y in {-5,-4,-3,-2,-1,1,2,3,4}\node[left=2pt] at (0,\y){$\y$};
\node[above left=3pt] at (0,0){$O$};
''','在直角坐标网格中标出题设各点。',opts='>=Latex,scale=.70')
Q[23]=diagram(23,r'''
\draw[kaxis] (0,0)--(6,0) node[right]{$r$};
\foreach \r in {1,...,5}{\draw (\r,0)--(\r,.1);\node[below] at (\r,0){$\r$};}
\node[left] at (0,0){$O$};
\path[use as bounding box] (-.5,-1.4) rectangle (6.4,1.4);
''','以向右射线为极轴，逆时针为正角方向。')
Q[28]=diagram(28,r'''
\coordinate (A) at (3,0);\coordinate (M) at (0,3);\coordinate (N) at (6,3);
\coordinate (B) at (1.125,3);\coordinate (H) at (3,3);
\draw[kguide] (M)--(N) (A)--(H) (A)--(B);
\node[point,label=below:$A$] at (A){};
\node[left] at (M){$M$};\node[right] at (N){$N$};
\draw[vector] (B)--++(1.1,0) node[midway,above]{$v$};
\draw[vector] (A)--++(0,1.7) node[midway,right]{$u$};
\node[below left] at (B){$B$};\node[above right] at (H){$H$};
\draw[TextGray] (A)++(90:.8) arc(90:122:.8);\node at (2.64,1.13){$\theta$};
\draw[<->] (3.7,0)--(3.7,3) node[midway,right]{$L$};
''',r'潜艇 A 与航线 MN 的垂直距离为 $L$，$\theta$ 从航线法线量起。')
Q[29]=diagram(29,r'''
\coordinate (A) at (0,0);\coordinate (B) at (4,2);\coordinate (X) at (6,0);
\draw[kaxis] (A)--(X) node[right]{$X$};\draw[thick] (A)--(B) node[midway,above left]{$d$};
\draw[vector] (A)--(1.3,0) node[midway,below]{$v$};
\draw[vector] (B)--++(.5,-1.1) node[right]{$v_p$};
\draw (0.8,0) arc(0:26.565:.8);\node at (1.12,.3){$\theta$};
\node[point,label=below left:$A$] at (A){};\node[point,label=above:$B$] at (B){};
''','球沿 AX 运动，队员从 B 开始奔跑；奔跑方向待选。')
Q[30]=clone(30,'TwoParticlesMinimumDistanceDiagram','A、B 初始位于 P、Q，分别沿 PQ、QR 匀速运动。')
Q[31]=clone(31,'RescueRouteDiagram','A 在岸上、B 在水中，C 为待选择的入水点；两垂足间距为 $L$。',
    append=r'\node[below left=3pt] at (-3.5,0){$M$};\node[above left=6pt] at (3.6,0){$N$};')
Q[32]=clone(32,'TennisServeDiagram','A 为水平击球点；全场长 $2L$，球网到对方发球线的距离为 $l$。',
    replace=[('(-.15,0)--(6.7,0)','(-.15,0)--(8.2,0)')],
    append=r'''\draw[thick] (8,-.12)--(8,.25);
\draw[<->,TextGray] (0,-1.4)--(8,-1.4) node[midway,below]{$2L$};
\node[above] at (8,.25){底线};''')
Q[33]=clone(33,'HorizontalThrowImpactDiagram',r'从高度 $h$ 水平抛出，落地速度与水平线成 $45^\circ$。')
Q[34]=clone(34,'ProjectileRangeDiagram',r'初速度为 $v_0$、仰角为 $\theta$，抛出点与落点等高。')
Q[35]=clone(35,'ComplementaryProjectileDiagram','两次初速率相同，两个抛射角互余。')
Q[36]=diagram(36,r'''
\draw[thick] (-.3,0)--(6,0) (5,0)--(5,1.7);
\draw[vector] (0,0)--(52:1.5) node[above left]{$v_0$};
\draw (.7,0) arc(0:52:.7);\node at (1.03,.4){$\theta$};
\node[below left] at (0,0){$A$};
\draw[<->] (0,-.55)--(5,-.55) node[midway,below]{$L$};
\draw[<->] (5.5,0)--(5.5,1.7) node[midway,right]{$H$};
''','A 到障碍物的水平距离为 $L$，障碍物高 $H$。')
reach=macro('ProjectileReachabilityDiagram')
reach=re.sub(r'\\path\[fill=Blue!7\].*?--cycle;', '', reach,flags=re.S)
reach='\n'.join(l for l in reach.splitlines() if not any(x in l for x in ['DeepBlue,very thick','不可达区','可达区','分界线',r'\draw[TextGray]']))
m=re.search(r'\\figcap\{',reach);_,end=balanced_argument(reach,m.end()-1)
Q[37]=reach[:m.start()]+caption(37,'从同一点以同一初速率、不同仰角抛出的轨迹族。')+reach[end:]
Q[39]=clone(39,'HillsideTargetDiagram',r'坡脚 C、坡上目标 T；$\alpha$ 为坡角，$\beta$ 为发射仰角。')
Q[40]=clone(40,'HorizontalAtObstacleDiagram','要求抛体在障碍顶端 T 处的速度平行于水平地面。')
Q[41]=clone(41,'InclinedPlaneNormalImpactDiagram','从斜面底端抛出，要求再次碰到斜面时速度垂直于斜面。')
Q[43]=clone(43,'StairBounceDiagram','A 在首个踏面上方 $H$；台阶宽 $d$、高 $l$，小球逐次反弹。')
Q[45]=diagram(45,r'''
\draw[thick] (-1.8,0)--(4.1,0);\draw[thick] (0,1.3) circle(1.3);
\coordinate (A) at (3.2,0);\coordinate (T) at (0,2.6);\coordinate (O) at (0,1.3);
\draw[kguide] (0,0)--(T);
\draw[kcurve,dashed,domain=0:3.2,samples=100] plot(\x,{2.6+.75*\x-(5/10.24)*\x*\x});
\pgfmathsetmacro{\launchangle}{180-atan(2.375)}
\draw[vector] (A)--++(\launchangle:1.3) node[above right]{$v_0$};
\draw[vector] (T)--++(-.8,-.6) node[above left]{$v_T$};
\draw[<->] (0,-.55)--(3.2,-.55) node[midway,below]{$d$};
\draw (O)--(-1.3,1.3) node[midway,above]{$R$};
\draw (A)++(\launchangle:.75) arc(\launchangle:180:.75);\node at (2.2,.38){$\theta$};
\node[point,label=below:$O$] at (O){};\node[point,label=above left:$T$] at (T){};
\node[point,label=below right:$A$] at (A){};
''','A 为抛出点，T 为球顶；虚线仅示意一条可行轨迹，并非唯一轨迹。')
Q[47]=clone(47,'RadialUniformCollisionDiagram','A 沿半径为 $R$ 的圆周运动，B 沿 OP 匀速运动。')
Q[48]=clone(48,'RadialAcceleratedCollisionDiagram','A 沿圆周匀速运动，B 从 O 由静止沿 OP 匀加速运动。')
Q[49]=clone(49,'SameCirclePursuitDiagram',r'两质点从正上方 P 同时出发，逆时针运动；$\theta$ 标记再次相遇的位置。')
Q[50]=clone(50,'ConcentricCollinearityDiagram','A、B 分别在半径为 $R_1$、$R_2$ 的同心圆上同向运动。')
Q[51]=clone(51,'ProjectileCircleCollisionDiagram','水平圆心 O 上方为 S；B 从 S 水平抛出，A 沿圆周运动。')
Q[52]=diagram(52,r'''
\draw[thick] (0,0) circle(1.5) (0,0) circle(2.6);
\coordinate (O) at (0,0);\coordinate (A) at (75:1.5);\coordinate (B) at (27:2.6);
\draw[kguide] (O)--(27:2.6) (O)--(A);\draw[thick] (A)--(B);
\pgfmathsetmacro{\lineangle}{atan2(1.5*sin(75)-2.6*sin(27),1.5*cos(75)-2.6*cos(27))}
\draw (B)++(\lineangle:.6) arc(\lineangle:207:.6);
\node at ($(B)+(190:.91)$){$\theta$};
\draw[->,DeepBlue] (80:1.78) arc(80:122:1.78) node[above left]{$\omega_1$};
\draw[->,DeepBlue] (5:2.87) arc(5:39:2.87) node[above right]{$\omega_2$};
\draw (O)--(150:1.5);\node at (-1.72,1.05){$R_1$};
\draw (O)--(230:2.6) node[pos=.7,below right]{$R_2$};
\node[point,label=below:$O$] at (O){};\node[point,label=above:$A$] at (A){};\node[point,label=right:$B$] at (B){};
''',r'B 观察 A，视线 BA 与指向圆心的 BO 夹角为 $\theta$；图中未预设最大夹角位置。')
Q[57]=clone(57,'RacetrackDiagram','内、外半圆弯道半径分别为 $R_1,R_2$。')
Q[59]=clone(59,'AccelerationVelocityAngleDiagram',r'速度 $\vect v$ 与加速度 $\vect a$ 的夹角为 $\theta$。')
for n in (60,61):
    Q[n]=diagram(n,r'''
\draw[kaxis] (-3,0)--(3.2,0) node[right]{$x$};
\draw[kaxis] (0,-1.8)--(0,2) node[above]{$y$};\node[below left] at (0,0){$O$};
''','根据给定参数方程在空坐标系中画出轨迹。')
Q[62]=clone(62,'CycloidDiagram','圆沿水平地面无滑动滚动，P 为圆周上的标记点，初始位于接触处。')
Q[63]=diagram(63,r'''
\draw[kaxis] (0,0,0)--(3,0,0) node[right]{$x$};
\draw[kaxis] (0,0,0)--(0,2.8,0) node[below left]{$y$};
\draw[kaxis] (0,0,0)--(0,0,3.5) node[above]{$z$};
\node[below right] at (0,0,0){$O$};
''','在右手直角坐标系中，根据三个坐标随时间的变化画出轨迹。',
    opts='>=Latex,scale=.85,x={(1cm,0cm)},y={(-.50cm,-.28cm)},z={(0cm,.80cm)}')
Q[64]=clone(64,'CircleComponentsDiagram','圆周上 P 点在两个坐标轴上的投影分别为 $x,y$。',drop=[r'\draw[vector]'])
Q[65]=clone(65,'RollingContactDiagram','圆无滑动向右滚动，P 为此刻与地面接触的圆周点。',
    drop=[r'\draw[vector] (P)',r'\node at (1.7',r'\node[clearlabel] at (0,-1.1)'],
    replace=[(r'$\omega=v/R$',r'$\omega$')])
Q[66]=diagram(66,r'''
\draw[kaxis] (0,0)--(6,0) node[right]{$r$};\node[below left] at (0,0){$O$};
\path[use as bounding box] (-.5,-1.35) rectangle (6.4,1.35);
''','以 O 为极点、向右为极轴，描出给定极坐标运动。')
Q[68]=diagram(68,r'''
\draw[kaxis] (-2.2,0)--(2.3,0) node[right]{$x$};
\draw[kaxis] (0,-.7)--(0,2.7) node[above]{$y$};
\draw[kcurve,domain=-1.8:1.8,samples=100] plot(\x,{.65*\x*\x});
\node[below left] at (0,0){$O$};\node[right] at (1.8,2.1){$y=ax^2$};
''','确定抛物线在原点处的曲率半径；这里示意 $a>0$。')
Q[69]=diagram(69,r'\draw[kcurve] \FoldedCurvePath;\FoldedCurvePoints',
    '比较 $P_1,P_2,P_3,P_4$ 的局部弯曲，注意 $P_3$ 后向左下回折。',opts='>=Latex,scale=1.15')
Q[70]=diagram(70,r'''
\draw[thick] (0,0) ellipse(3 and 1.6);\draw (0,0)--(3,0) node[midway,below]{$a$};
\draw (0,0)--(0,1.6) node[midway,left]{$b$};\node[below left] at (0,0){$O$};
''','椭圆的半长轴为 $a$、半短轴为 $b$。')
Q[73]=clone(73,'CrossRiverRoundTripDiagram','两岸正对的 A、B 距离为 $L$，水流速度向右，船速指船相对水的速度。',
    drop=[r'\draw[DeepBlue,very thick,->]',r'\draw[vector] (B)'])
Q[74]=clone(74,'EqualSpeedFrameDiagram',r'地面系中 A 向右运动、B 静止；参考系 $S\prime$ 以速度 $u$ 向右平动。',
    drop=[r'\draw[->,TextGray]',r'\node[below] at (0,-.65)'])
Q[82]=diagram(82,r'''
\draw[thick] (-2,0)--(3,0) (-2,2.7)--(3,2.7);
\node[point,label=below:$A$] at (0,0){};
\draw[vector] (-1.7,1.5)--(-.3,1.5) node[midway,above]{$v_2$};
\draw[vector] (0,0)--(110:1.4) node[pos=.5,right=7pt]{$v_1$};
\draw[<->] (2.4,0)--(2.4,2.7) node[midway,left]{$d$};
''','水流平行于河岸，小船对水速度的大小为 $v_1$，船头方向可以选择。')
Q[85]=diagram(85,r'''
\coordinate (A) at (4,0);\coordinate (B) at (-2,2.4);\coordinate (C) at (2.4,2.4);
\draw[thick] (A)--(B) node[midway,below left]{$L$};
\draw[kguide] (B)--(5.1,2.4) (A)--(4,3.2) (A)--(C);
\draw[vector] (B)--(-.7,2.4) node[midway,above]{$v_1$};
\draw[vector] (A)--($(A)!.43!(C)$) node[left]{$v_2$};
\draw (B)++(-21.801:.85) arc(-21.801:0:.85);\node at (-.7,2.1){$\alpha$};
\draw (A)++(123.690:.65) arc(123.690:158.199:.65);\node at (3.23,.69){$\beta$};
\foreach \p/\pos in {A/below right,B/above left,C/above}\node[point,label=\pos:$\p$] at (\p){};
''','A 为潜艇、B 为敌船初始位置，C 表示可能的相遇点；发射方向待定。')
def first_scope(n,source,cap,drop=()):
    b=macro(source);start=b.index(r'\begin{scope}')+len(r'\begin{scope}')
    end=b.index(r'\end{scope}',start)
    return diagram(n,'\n'.join(l for l in b[start:end].splitlines() if not any(d in l for d in drop)),cap)
Q[87]=first_scope(87,'ThreeBoatsDiagram','三船初始位置及对地速度，图中 A、B、C 等间距。',drop=[r'(a) $t=0$'])
Q[89]=first_scope(89,'SlidingRodDiagram',r'杆的 A、B 端接触墙、地；$\theta$ 从竖直墙量起，$AP=aL$。')
Q[90]=clone(90,'BoatTowDiagram','汽车经岸上定滑轮拉船；绳不可伸长，$h$ 为滑轮相对水面的高度。')
mc=macro('MovingConstraintDiagram')
scope1=mc.split(r'\begin{scope}',1)[1].split(r'\end{scope}',1)[0]
scope2=mc.split(r'\begin{scope}[xshift=7cm]',1)[1].split(r'\end{scope}',1)[0]
Q[91]=diagram(91,'\n'.join(l for l in scope1.splitlines() if '(a)' not in l),
    '斜面向右运动，竖杆位于两侧固定导向之间，杆底 P 与斜面保持接触。')
Q[92]=diagram(92,'\n'.join(l for l in scope2.splitlines() if '(b)' not in l and '1.8,2.7' not in l),
    r'半圆柱向右运动；竖杆横坐标固定，P 为接触点，$\theta$ 从竖直方向量起。')
Q[93]=clone(93,'RodPulleyDiagram','杆 OA 绕 O 转动，绳从 A 经固定转向点 B、C 连到物块 M。',
    drop=[r'\draw[vector] (A)',r'\draw[vector] (-2.85'])
Q[94]=diagram(94,r'''
\draw[thick] (0,0)--(4,0);\node[point,label=left:$A$] at (0,0){};\node[point,label=right:$B$] at (4,0){};
\draw[vector] (0,0)--(0,1.6) node[above]{$v_A$};\draw[vector] (4,0)--(4,1.6) node[above]{$v_B$};
\draw[<->] (0,-.55)--(4,-.55) node[midway,below]{$l$};
''','A、B 用轻杆连接；图示规定竖直向上为端点速度的正方向，各问按给定符号取向。')
Q[95]=clone(95,'RollingBallDiagram','球初始向右平动并逆时针转动，地面为水平面。',drop=[r'\draw[vector] (0,-.65)'])
Q[96]=clone(96,'KnifeFlightDiagram','飞刀的飞行姿态、长度及初始方向；木靶与初始质心等高。',
    drop=[r'\draw (60:1.85)',r'\node[left] at (-1.85'],
    replace=[('(c) 初姿态与最小正转角','(c) 初姿态与速度方向')])
Q[103]=diagram(103,r'''
\coordinate (E) at (0,0);\coordinate (P) at (0,3.3);
\draw[thick] (E)--(P) node[midway,right]{$L$};
\draw (E) circle(.25);\node[below] at (0,-.3){地球 E};
\draw[vector] (P)--++(-135:1.5) node[below left]{$v$};
\draw (P)++(-135:.7) arc(-135:-90:.7);\node at (-.4,2.34){$\theta$};
\node[point,label=above:$P$] at (P){};
''',r'天体初始距地球 $L$，运动方向与指向地球的视线成角 $\theta$。')
mars=macro('MarsRetrogradeDiagram')
mars=mars[:mars.index(r'\begin{scope}[xshift=5.25cm,yshift=-8.6cm]')]+r'\end{tikzpicture}'+caption(105,'七个时刻的日、地、火位置与观测视线；E 为地球、M 为火星、S 为太阳。')+r'\end{minipage}\end{center}'
loop=macro('MarsInclinedDiagram')
loop=loop.replace(r'\node at (0,-2.8){箭头表示时间先后；蓝色区间才是逆行};',r'\node at (0,-2.8){箭头表示观测的时间先后};')
pos=re.search(r'\\figcap\{',loop);_,end=balanced_argument(loop,pos.end()-1)
loop=loop[:pos.start()]+r'\figcap{同一现象在背景星空上的视位置回环示意。}'+loop[end:]
Q[105]=mars+'\n'+loop

CONTRACT=r'''% Question figure contract — source physical pages in question-figure-map.json.
% Mode C; simple physics geometry, restrained blue/grey lines on white paper.
% Each question can be understood while hiding its solution. No solved labels.
% Reference geometry: preserve contacts, axis zero, directions, source point identities.
% Main viewport <=14cm; ordinary labels 9–11pt; all labels transparent.
% Read axes/objects first, givens second; no decoration or filled label rectangles.
% Cloned givens retain exact reviewed coordinates; answer overlays are excluded explicitly.
% Captions + source-specific labels bind each view to its own question, never previous answer.
% Anticipated risks: angle labels near rays, multiple dimensions, clipping tall multi-panels.
% Sketch: [question text] [given geometry or blank axes] -> [answer text + construction].
'''
source_ledger=ROOT.parents[2]/'build/audit-ch01-05-20260923/geometry/source-figure-ledger.json'
ledger=json.loads(source_ledger.read_text())
assert {int(x['source_example'].split('.')[1]) for x in ledger['question_figures']}==set(Q)
parts=[CONTRACT];mapping=[]
for n,body in sorted(Q.items()):
    assert not any(ord(c)<32 and c not in '\n\t\r' for c in body),(n,'control character')
    balanced_argument('{'+body+'}',0)
    parts.append(f'% Source example 2.{n}; question-only view.\n\\newcommand{{\\{name(n)}}}{{%\n'+body+'\n}\n')
    source=next(x for x in ledger['question_figures'] if x['source_example']==f'2.{n}')
    mapping.append({'source_example':f'2.{n}','source_pages':source['source_physical_pages'],'macro':name(n),'label':label(n),'role':'question','solution_retained':True})
(ROOT/'data/question-figures.tex').write_text('\n'.join(parts))
(ROOT/'data/question-figure-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
print('Generated',len(Q),'question figure groups; 8 blank templates included.')
