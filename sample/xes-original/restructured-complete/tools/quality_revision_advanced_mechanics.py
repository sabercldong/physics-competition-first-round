"""Editable, problem-specific geometry overlay for advanced mechanics A1."""
from pathlib import Path
import re
from quality_revision_mechanics import figure

BOOK=Path(__file__).resolve().parent.parent
MARKER="% AdvancedMechanicsQuality20261023-v1"
FILES=("A1.tex","A1-rigid.tex","A1-continuum.tex")
PATTERN=re.compile(r"(\\begin\{advexamplebox\})(.*?)(\\end\{advexamplebox\})(.*?\\begin\{advsolution\})(.*?)(\\end\{advsolution\})",re.S)


def axes():
    return r"\draw[->](0,0)--(3.5,0)node[right]{$x$};\draw[->](0,0)--(0,3)node[above]{$z$};\draw[->](0,0)--(-1.3,-1)node[left]{$y$};\node[below left]at(0,0){$O$};"


def geometry(key,answer=False):
    a=answer
    if key=="ellipsoid":
        b=r"""\draw[DeepBlue](0,0)ellipse(2.5 and 1.5);\draw[dashed](-2.5,0)arc(180:360:2.5 and .45);\draw(-2.5,0)arc(180:0:2.5 and .45);
\foreach\x/\y/\t in {2.5/0/A,-2.5/0/A',.9/.45/B,-.9/-.45/B',0/1.5/C,0/-1.5/C'}{\fill(\x,\y)circle(2pt)node[above right]{$\t$};}
\draw[dashed](-2.5,0)--(2.5,0)(-.9,-.45)--(.9,.45)(0,-1.5)--(0,1.5);"""
        b+=r"\draw[<->](-2.5,-2.1)--(2.5,-2.1)node[midway,below]{$AA'=2a$};\draw[<->](-3,-1.5)--(-3,1.5)node[midway,left]{$CC'=2c$};\node at(1.7,.85){$BB'=2b$};"
        return b+(r"\node[align=left]at(6.5,0){三组对径端点共用同一中点\\$|\vect u|=2a,\ |\vect v|=2b,\ |\vect w|=2c$\\三条对径矢量两两正交};" if a else "")
    if key in ("expanding-sphere","spherical"):
        b=axes()+r"""\draw[DeepBlue](0,0)circle(2);\coordinate(P)at(1.3,1.3);\fill(P)circle(2pt)node[right]{$P$};\draw[thick](0,0)--(P)node[pos=.65,below right=3pt]{$r$};
\draw[dashed](P)--(1.3,-.45)--(0,0);\draw(0,.7)arc(90:45:.7)node[midway,above]{$\theta$};\draw(.7,0)arc(0:-19.1:.7)node[midway,below]{$\varphi$};"""
        if key=="expanding-sphere":b+=r"\node at(3.5,2){$r(t)=vt$};"
        return b+(r"\draw[->,Gold](P)--(2.1,2.1)node[right]{$\vect e_r$};\draw[->,Gold](P)--(2.1,.5)node[right]{$\vect e_\theta$};\node[align=left]at(4,-1.4){$\dd s_r=\dd r$\\$\dd s_\theta=r\dd\theta$\\$\dd s_\varphi=r\sin\theta\dd\varphi$};" if a else "")
    if key in ("polar","kepler-time"):
        b=r"""\draw[->](0,0)--(4.6,0)node[right]{$x$};\draw[->](0,0)--(0,3.4)node[above]{$y$};\node[below left]at(0,0){$O$};\coordinate(P)at(2.5,1.8);\fill(P)circle(2pt)node[left]{$P$};\draw[thick](0,0)--(P)node[midway,below]{$r$};\draw(.9,0)arc(0:35.75:.9)node[midway,right]{$\theta$};"""
        if key=="kepler-time":b+=r"\draw[->,Gold,very thick](P)--(1.7,1.224)node[above left]{$F_r$};\node at(3,-1){$k=k(t)$};"
        return b+(r"\draw[->,DeepBlue](P)--(3.5,2.52)node[right]{$\vect e_r$};\draw[->,DeepBlue](P)--(1.78,2.8)node[left]{$\vect e_\theta$};" if a else "")
    if key=="omega-transform":
        b=axes()+r"\draw[->,DeepBlue,very thick](0,0)--(1,2)node[above]{$\vect\omega$};\draw[->,Gold,very thick](0,0)--(2,1)node[right]{$\vect\omega'$};\draw[->](.8,1.6)arc(63.435:26.565:1.789)node[midway,above right]{$\mathsf O$};"
        return b+(r"\node at(2,-1.7){正向正交变换保持叉积的方向约定};" if a else "")
    if key=="moving-frame":
        b=r"\draw[->](0,0)--(4.2,0)node[right]{$x$};\draw[->](0,0)--(0,3.2)node[above]{$y$};\node[below left]at(0,0){$O$};"+r"""\coordinate(C)at(1.8,1);\fill(C)circle(2pt)node[below right]{$O'$};\draw[->,Gold](0,0)--(C)node[midway,below]{$\vect R$};\draw[->,DeepBlue](C)--(3.8,2.2)node[right]{$\bar x$};\draw[->,DeepBlue](C)--(.8,2.67)node[above]{$\bar y$};\draw(2.4,1)arc(0:31:.6)node[midway,right]{$\theta$};"""
        return b+(r"\node[align=left]at(4,-1.2){平移原点后再旋转分量\\相同物理矢量使用不同基矢表示};" if a else "")
    if key in ("conical-pendulum","routh-hoop","physical-pendulum","nutation","triangle-top"):
        if key=="routh-hoop":
            return r"""\draw[thick](0,0)ellipse(1.5 and 2);\draw[->](0,-2.4)--(0,2.5)node[above]{竖直转轴};\fill(0,0)circle(2pt)node[left]{$O$};\coordinate(P)at(.7949,-1.6961);\draw[dashed](0,0)--(P);\fill(P)circle(3pt)node[right]{$m$};\draw[DeepBlue](0,-.7)arc(-90:-58:.525 and .7);\node at(.34,-.8){$\theta$};\draw[->,Gold](-.7,.7)arc(180:0:.7 and .2)node[right]{$\varphi$};\node[align=left]at(3.3,0){环半径 $a$\\轴惯量 $I$};"""
        b=r"""\fill(0,2.5)circle(2pt)node[above]{$O$};\draw[dashed](0,2.5)--(0,-1);\coordinate(P)at(1.5,.1);\draw[thick](0,2.5)--(P);\fill(P)circle(3pt)node[right]{$m$};\draw(0,1.6)arc(-90:-58:.9)node[midway,below right]{$\theta$};"""
        if key=="conical-pendulum":b+=r"\draw[dashed](0,.1)ellipse(1.5 and .4);\node[above right]at(.75,1.3){$l(t)=l_0-vt$};"
        if key=="routh-hoop":b+=r"\draw[DeepBlue](0,.5)ellipse(1.7 and 2);\node at(3.5,.7){半径 $a$，轴惯量 $I$};"
        if key=="physical-pendulum":b=b.replace("{$m$}","{$G$}")+r"\node at(3,1.2){$OG=a$};\node at(3,.4){轴惯量 $I$，质量 $M$};"
        if key=="nutation":
            b=b.replace("{$m$}","{$G$}")+r"\draw[->,Gold](.5,1.7)--(1.2,.58)node[right]{对称轴};\node at(3,-1){$\theta=\theta_0+\delta\theta$};"
            return b+(r"\begin{scope}[xshift=4cm,yshift=.3cm]\draw[->](0,0)--(3,0)node[right]{$\theta$};\draw[->](0,0)--(0,2)node[above]{$V_{\rm eff}$};\draw[DeepBlue,domain=.3:2.7,samples=40]plot(\x,{.8*(\x-1.5)^2+.3});\draw[dashed](1.5,0)--(1.5,.3);\node[below]at(1.5,0){$\theta_0$};\node at(1.5,-.9){稳定驻点的局部示意};\end{scope}" if a else "")
        if key=="triangle-top":b=r"""\coordinate(O)at(0,2.5);\coordinate(A)at(-.5,0);\coordinate(B)at(3,0);\draw[thick,fill=PaleBlue](O)--(A)--(B)--cycle;\draw[dashed](0,2.5)--(0,-.5);\coordinate(G)at(.833,.833);\draw[DeepBlue](O)--(G);\fill(G)circle(2pt)node[right]{$G$};\foreach\p in{O,A,B}{\node[above left]at(\p){$\p$};}\node[align=center]at(1.5,-.7){$AB=l$ 且始终水平\\三维姿态的斜投影};\draw(0,1.8)arc(-90:-63.435:.7);\node at(.35,1.55){$\phi$};"""
        return b+((r"\draw[->,Gold](P)--++(0,-1)node[below]{$Mg$};" if key=="physical-pendulum" else r"\draw[->,Gold](P)--++(0,-1)node[below]{$mg$};") if a and key not in ("triangle-top",) else "")
    if key=="scaled-oscillator":
        b=r"""\draw[very thick](0,-.5)--(0,.6);\draw[decorate,decoration={coil,segment length=5pt,amplitude=3pt}](0,0)--(3,0);\draw[fill=PaleBlue](3,-.4)rectangle(4,.4);\draw[->](3.5,-.9)--(5,-.9)node[right]{$q$};\node at(2,1.2){拉格朗日量中的系数同比增长};"""
        return b+(r"\draw[->](0,-2.4)--(5,-2.4)node[right]{$t$};\draw[DeepBlue,domain=0:5,samples=90]plot(\x,{-2.4+.6*exp(-.3*\x)*cos(240*\x)});\node at(2,-3.3){$q=e^{-\gamma t}\bar q$};" if a else "")
    if key=="unwinding-cylinder":
        return r"""\draw[thick](0,0)circle(1.3);\draw[dashed](-1.7,0)--(1.7,0);\draw[very thick](1.3,0)--(1.3,2);\draw[very thick](-1.3,0)--(-1.3,-2);\fill(1.3,2)circle(3pt)node[right]{$m$};\fill(-1.3,-2)circle(3pt)node[left]{$m$};\draw(0,0)--(1.3,0)node[midway,below]{$R$};\node at(0,.4){$M$};\draw[->,Gold](.7,0)arc(0:100:.7)node[midway,above]{$\omega_0$};\node at(3.5,.7){对称解绕；俯视图};"""
    if key=="foucault-polar":
        b=r"""\draw[->](-2.5,0)--(3,0)node[right]{$x$};\draw[->](0,-2)--(0,2.4)node[above]{$y$};\draw[DeepBlue,rotate=25](0,0)ellipse(2 and .5);\draw[dashed,rotate=25](-2.3,0)--(2.3,0)node[right]{共转长轴};\draw(.8,0)arc(0:25:.8)node[midway,right]{$\theta$};"""
        return b+(r"\node[align=center]at(0,-2.6){共转椭圆的主轴以 $\Omega/2$ 转动\\一般初态不必是直线振动};" if a else "")
    if key=="resistor-chain":
        b=r"""\foreach\i in{-2,-1,0,1,2}{\fill(1.5*\i,0)circle(2pt)node[above]{$\i$};\draw(1.5*\i,0)--(1.5*\i,-.3)--++(.12,-.12)--++(-.24,-.2)--++(.24,-.2)--++(-.24,-.2)--++(.12,-.12)--(1.5*\i,-1.5);\node[right]at(1.5*\i,-.8){$r$};}\draw(-3,-1.5)--(3,-1.5)node[right]{公共地};\foreach\i in{-2,-1,0,1}{\draw(1.5*\i,0)--++(.4,0)--++(.1,.15)--++(.2,-.3)--++(.2,.3)--++(.2,-.3)--++(.1,.15)--++(.3,0);\node at(1.5*\i+.75,.5){$R$};}\node at(-3.7,0){$\cdots$};\node at(3.7,0){$\cdots$};"""
        return b+(r"\draw[Gold,thick](-.3,-1.7)rectangle(.3,.7);\node at(0,-2.3){在 $n=0$ 注入电流，两侧衰减解须在无穷远有界};" if a else "")
    if key=="six-atom-ring":
        return r"""\foreach\i in{0,...,5}{\coordinate(P\i)at({60*\i}:1.8);\fill(P\i)circle(2.5pt)node[below right]{$j=\i$};\draw[->,Gold](P\i)--++({60*\i+90}:.55)node[above]{$u_\i$};}\draw[DeepBlue,thick](P0)--(P1)--(P2)--(P3)--(P4)--(P5)--cycle;\node[align=center]at(0,0){$m_j=m$\\$\kappa$};\node at(0,-2.7){沿环方向的小位移，$u_{j+6}=u_j$};"""
    if key in ("moment-translation","convolution"):
        b=axes()+r"""\coordinate(P)at(1.2,1.3);\coordinate(Q)at(3,2);\fill(P)circle(2pt)node[left]{$\vect r'$};\fill(Q)circle(2pt)node[right]{$\vect r$};\draw[->,DeepBlue](0,0)--(P);\draw[->,Gold](P)--(Q)node[midway,below]{$\vect r-\vect r'$};"""
        if key=="moment-translation":b=b.replace("$\\vect r-\\vect r'$","$\\vect a$").replace("$\\vect r$","$\\vect r'+\\vect a$")
        return b+(r"\draw[->,thick](0,0)--(Q);\node at(2,-1.8){同一质量元在求和坐标中的矩贡献};" if a else "")
    if key=="square-moments":
        b=r"""\draw[->](0,0)--(3.5,0)node[right]{$x$};\draw[->](0,0)--(0,3.5)node[above]{$y$};\draw[fill=PaleBlue](0,0)rectangle(3,3);\node[below]at(3,0){$l$};\node[left]at(0,3){$l$};\node at(1.5,2.5){$\sigma$};"""
        return b+(r"\fill[DeepBlue](1.3,1.1)rectangle(1.6,1.4);\node[right]at(1.7,1.2){$\dd m=\sigma\dd x\dd y$};" if a else "")
    if key in ("axis-rotations","matrix-exponential","axis-inertia"):
        b=axes()+r"""\draw[->,Gold,very thick](0,0)--(1.8,2.5)node[above]{$\vect n$};\coordinate(P)at(2.6,.7);\fill(P)circle(2pt)node[right]{$P$};\draw[dashed](0,0)--(P);\draw[->,DeepBlue](1.9,.4)arc(-10:65:.8 and .35)node[right]{$\theta$};"""
        if key=="axis-rotations":b=axes()+r"\draw[->,DeepBlue,thick](0,0)--(2.5,.7)node[right]{$\vect r$};\draw[->,Gold](1.1,1.5)arc(0:160:1.1 and .3)node[left]{$\theta$（绕 $z$ 示例）};"
        return b+(r"\draw[dashed](P)--(1.219,1.694)node[midway,above]{$r_\perp$};\node at(3,-1.6){沿轴与垂轴分量分别处理};" if a and key!="axis-rotations" else (r"\node at(1.7,-1.7){各次主动旋转均遵循右手定则};" if a else ""))
    if key=="max-entropy":
        b=r"\draw[->](-3,0)--(3.3,0)node[right]{$v$};\draw[->](0,0)--(0,2.2)node[above]{$f(v)$};"
        if a:return b+r"\draw[DeepBlue,thick,domain=-2.8:2.8,samples=90]plot(\x,{1.8*exp(-\x*\x)});\node at(1.8,1.8){高斯驻值分布};\node at(0,-.8){曲线面积为 $1$，二阶矩为 $kT/m$};"
        return b+r"\draw[DeepBlue,thick,domain=-2.8:2.8,samples=90]plot(\x,{.9*exp(-2*(\x-1)^2)+.9*exp(-2*(\x+1)^2)});\node at(0,-.8){满足给定矩约束的候选分布示意};"
    if key=="stress-divergence":
        b=r"""\draw[fill=PaleBlue](0,0)rectangle(2.5,1.8);\draw[dashed](0,0)--(-.5,-.4)--(2,-.4)--(2.5,0)(2,-.4)--(2,1.4)--(2.5,1.8);\node at(1.2,.9){$\dd V$};\draw[->,DeepBlue](2.5,.9)--(3.8,.9)node[right]{$\sigma_{xx}(x+\dd x)$};\draw[->,DeepBlue](0,.9)--(-1.3,.9)node[left]{$\sigma_{xx}(x)$};\draw[->](0,-1)--(2.5,-1)node[right]{$x$};"""
        return b+(r"\node at(1.3,2.6){相对两面的牵引力作差后除以体积};\draw[->,Gold](1.2,-1.7)--(2.5,-1.7)node[right]{$\rho_m\ddot{\xi}_x$};" if a else "")
    if key=="beam-bending":
        return r"""\draw[thick](-2.7,0)--(2.7,0)--(2.7,.45)--(-2.7,.45)--cycle;\draw[<->](-2.7,-.6)--(2.7,-.6)node[midway,below]{$L$};\draw[<->](3,0)--(3,.45)node[midway,right]{$h$};\node at(0,1){矩形截面宽 $b$};\draw[->,Gold](-2.7,.8)arc(90:210:.5);\draw[->,Gold](2.7,.8)arc(90:-30:.5);\node at(0,-1.5){端力矩使梁弯成总转角 $\Theta$ 的圆弧};"""
    if key=="cylinder-torsion":
        return r"""\draw[thick](-1,0)--(-1,3)(1,0)--(1,3);\draw[thick](0,3)ellipse(1 and .3);\draw(-1,0)arc(180:360:1 and .3);\draw[dashed](-1,0)arc(180:0:1 and .3);\draw[->](0,-.5)--(0,3.8)node[above]{$z$};\draw[<->](1.5,0)--(1.5,3)node[midway,right]{$L$};\draw(0,3)--(1,3)node[midway,above]{$R$};\draw[->,Gold](0,3.3)arc(90:210:.7 and .3)node[left]{$\Theta$};\node at(0,-1){底面固定};"""
    if key in ("vorticity","strain-rate"):
        b=r"""\draw[DeepBlue,thick](-.7,0)--(-.4,2.5)(.7,0)--(.4,2.5);\draw(0,0)ellipse(.7 and .18);\draw(0,2.5)ellipse(.4 and .12);\draw[->,Gold](0,.4)--(0,2.2)node[right]{$\vect\omega$};\draw[->](-1.4,.3)--(-1.4,-.5)node[left]{$\vect v_1$};\draw[->](-1.4,2.2)--(-1.4,3.4)node[left]{$\vect v_2$};\node at(2.7,1.5){局部速度梯度};"""
        if key=="strain-rate":b=r"""\draw[DeepBlue](0,0)rectangle(2,1.5);\draw[dashed](-.3,-.2)--(2.4,.1)--(2.7,1.9)--(0,1.6)--cycle;\draw[->,Gold](0,0)--(-.3,-.2);\draw[->,Gold](2,1.5)--(2.7,1.9);\node at(1,2.7){相邻流体点的速度差由 $\nabla\vect v$ 给出};"""
        return b+(r"\node[align=left]at(1.5,-1.5){对称部分 $U$ 改变形状\\反对称部分 $W$ 产生局部转动};" if a and key=="strain-rate" else (r"\node at(0,-1.3){涡管伸长与体积膨胀分别进入两项};" if a else ""))
    if key=="hangar-lift":
        return r"""\draw[thick](-3,0)--(3,0);\draw[thick](-2,0)arc(180:0:2);\draw[dashed](0,0)--(1.414,1.414)node[midway,left]{$R$};\draw(.6,0)arc(0:45:.6)node[midway,right]{$\theta$};\draw[->,DeepBlue](3,2.7)--(1.5,2.7)node[midway,above]{$v_0$};\node at(-1,.6){$p_{\rm in}=p_\infty$};\node at(-2.7,1.6){$p(\theta)$};"""
    if key=="bernoulli-principle":
        b=r"""\draw[DeepBlue,->,domain=0:5,samples=60]plot(\x,{.4*\x+.35*sin(72*\x)});\draw[DeepBlue,domain=0:5,samples=60]plot(\x,{.4*\x+.35*sin(72*\x)-.5});\fill(1,.7329)circle(2pt)node[above]{$A$};\fill(4,1.2671)circle(2pt)node[below]{$B$};\node[align=center]at(1,-1.1){$p_A,\rho_A,v_A,\phi_A$};\node[align=center]at(4,-1.1){$p_B,\rho_B,v_B,\phi_B$};"""
        return b+(r"\node at(2.5,3){先沿同一条流线积分；跨流线相等需要无旋条件};" if a else "")
    if key=="cylindrical-couette":
        return r"""\fill[PaleBlue,even odd rule](0,0)circle(2.2)(0,0)circle(1);\draw[thick](0,0)circle(2.2);\draw[thick](0,0)circle(1);\draw(0,0)--(1,0)node[midway,below]{$R_1$};\draw(0,0)--(-1.55,1.55)node[midway,above]{$R_2$};\draw[->,Gold](0,.7)arc(90:190:.7)node[left]{$\omega_1$};\draw[->,Gold](0,2.5)arc(90:30:2.5)node[right]{$\omega_2$};\node at(3.7,0){黏度 $\eta$，高度 $H$};"""
    if key=="falling-cylinder-viscosity":
        return r"""\draw[very thick](-2,3)--(-2,-.5)--(2,-.5)--(2,3);\draw[fill=PaleBlue](-1,0)rectangle(1,2.4);\draw[dashed](0,-.6)--(0,3.3);\draw[<->](1.3,0)--(1.3,2.4)node[midway,right]{$a$};\draw[->,Gold](0,1.7)--(0,.7)node[right]{$v$};\foreach\x in{-1.6,1.6}{\draw[->,DeepBlue](\x,.4)--(\x,1.5);}\draw(0,2.8)--(2,2.8)node[midway,above]{$R$};\draw(0,-.9)--(1,-.9)node[midway,below]{$r$};\node at(3.7,1){环隙回流向上};"""
    if key=="isoperimetric":
        b=r"""\draw[DeepBlue,thick](0,0)..controls(-2,1)and(-.7,3)..(.7,2.2)..controls(3,2.5)and(3,-.5)..(0,0);\node at(.6,1){有向面积 $A$};\node at(2.8,2.4){周长 $C$};\draw[->,Gold](2,.1)..controls(1.7,-.1)and(1.3,-.2)..(.9,-.15);"""
        return b+(r"\draw[dashed](5,1)circle(1.3);\node at(5,-.8){等号对应圆};" if a else "")
    if key=="brachistochrone":
        return r"""\draw[->](0,0)--(5.5,0)node[right]{$x$};\draw[->](0,0)--(0,-3)node[below]{$y$（向下）};\fill(0,0)circle(2pt)node[above left]{$A(0,0)$};\fill(5,-2.4)circle(2pt)node[right]{$B(l,h)$};\draw[dashed](0,0)--(5,-2.4);\draw[DeepBlue](0,0)..controls(.5,-2.8)and(3,-3)..(5,-2.4);\draw[Gold](0,0)..controls(2,0)and(4,-1)..(5,-2.4);\node at(3,-3.6){比较同端点的候选曲线，重力向下};"""
    if key=="least-dissipation":
        b=r"""\draw[thick,fill=PaleBlue](0,0)..controls(-1,1)and(0,3)..(2,2.6)..controls(4,3)and(4,0)..(0,0);\node at(1,1){$D,\sigma(\vect r)>0$};\node at(3.5,2.7){$\partial D$};\draw[->,Gold](.5,1.6)--(2,1.8)node[above]{$\vect K$};\draw[DeepBlue](.5,.5)..controls(1,1)and(2,.5)..(2.8,1);\node[right]at(2.8,1){等势线};"""
        return b+(r"\node at(1.5,-1){变分时必须同时指定边界条件和功率约束};" if a else "")
    if key=="central-brachistochrone":
        b=r"""\fill(0,0)circle(2pt)node[below left]{$O$};\draw[dashed](0,0)circle(2.5);\fill(2.5,0)circle(2pt)node[right]{$A:r_0$};\fill(.7,-.8)circle(2pt)node[below]{$P:r$};\draw(0,0)--(2.5,0);\draw(0,0)--(.7,-.8)node[midway,left]{$r$};\draw[DeepBlue](2.5,0)..controls(2,-1.5)and(1.3,-1.4)..(.7,-.8);\draw[->,Gold](1.6,-.5)--(.8,-.25)node[above]{$\vect g$};"""
        return b+(r"\node at(1,-3.4){先用势能差得到 $v(r)$，再写路径时间泛函};" if a else "")
    if key in ("geodesic","minimal-surface"):
        b=r"""\draw[fill=PaleBlue,thick](0,0)..controls(1,1.4)and(3,-.2)..(4,1)..controls(4.7,2)and(4,3)..(3.5,3)..controls(2,2)and(.5,3)..(0,2)--cycle;\foreach\y in{.6,1.2,1.8}{\draw[gray,thin](.2,\y)..controls(1.5,\y+.7)and(2.5,\y-.3)..(3.8,\y+.6);}\draw[->](.3,.4)--(1.4,.8)node[below]{$u^1$};\draw[->](.3,.4)--(.4,1.6)node[left]{$u^2$};\fill(.8,1.3)circle(2pt)node[left]{$A$};\fill(3,1.8)circle(2pt)node[right]{$B$};\draw[DeepBlue,thick](.8,1.3)..controls(1.5,.8)and(2.3,2.5)..(3,1.8);"""
        if key=="minimal-surface":
            b=b.replace(r"\fill(.8,1.3)circle(2pt)node[left]{$A$};\fill(3,1.8)circle(2pt)node[right]{$B$};\draw[DeepBlue,thick](.8,1.3)..controls(1.5,.8)and(2.3,2.5)..(3,1.8);","")+r"\node at(2,-.7){边界曲线固定，内部曲面可变};\node at(4.4,3){$\Gamma$};"
        return b+(r"\draw[->,Gold](2,1.7)--(2,3.2)node[above]{$\vect n$};\node at(2,-1.4){分离切向重参数化与法向几何变化};" if a else "")
    if key=="rod-noether":
        b=r"""\draw[fill=PaleBlue](0,0)rectangle(5,.6);\draw[->](-.3,-.5)--(5.5,-.5)node[right]{$x$};\draw[dashed](1,-.1)--(1,.9)(3,-.1)--(3,.9);\node[above]at(1,1){$x$};\node[above]at(3,1){$x+\dd x$};\draw[->,DeepBlue](1,.3)--(1.8,.3)node[above]{$\xi$};\node at(2.5,-1.3){局部棒段两端应力通量之差改变机械动量};"""
        return b+(r"\draw[->,Gold](1,.3)--(.2,.3)node[left]{$\sigma(x)$};\draw[->,Gold](3,.3)--(3.8,.3)node[right]{$\sigma(x+\dd x)$};\node at(2.5,1.9){$\pi=\rho_m\dot\xi$};" if a else "")
    if key=="shear-circle":
        b=r"\draw[->](-2,0)--(2,0)node[right]{$x$};\draw[->](0,-2)--(0,2)node[above]{$y$};\draw[thick](0,0)circle(1.3);"
        if a:b+=r"\draw[DeepBlue,thick,rotate=45](0,0)ellipse(1.6 and 1);\draw[dashed](-1.5,-1.5)--(1.5,1.5)node[right]{伸长主轴};\draw[dashed](-1.2,1.2)--(1.2,-1.2);"
        else:b+=r"\draw[->,Gold](1.3,0)--(1.3,.5);\draw[->,Gold](0,1.3)--(.5,1.3);\node at(0,-2.7){小位移 $\vect\xi=\bm\varepsilon\vect r$};"
        return b
    if key=="rank3-decomp":
        if not a:return axes()+r"\node[align=left]at(4.6,1.5){$T_{ijk}$ 有三个矢量指标\\三个指标受同一个 $SO(3)$ 转动};"
        return r"""\node at(0,1.2){前两个角动量 $1\otimes1$};\foreach\y/\j in{0/0,-1.5/1,-3/2}{\node[draw,circle](j\j)at(0,\y){$j_{12}=\j$};}
\node at(4,0){$0\otimes1\to J=1$};\node at(4,-1.5){$1\otimes1\to J=0,1,2$};\node at(4,-3){$2\otimes1\to J=1,2,3$};\foreach\y/\j in{0/0,-1.5/1,-3/2}{\draw[->,DeepBlue](j\j)--(2,\y);}\node at(2,-4.1){每个角动量 $J$ 的维数为 $2J+1$};"""
    raise KeyError(key)


SPECS={
"ellipsoid":("六个对径顶点和三条主轴",r"$A,A'$、$B,B'$、$C,C'$ 各自的中点必须相同；长度条件与正交条件是另外六个标量约束，不能把六个端点各自固定在实验室坐标中。"),
"expanding-sphere":("膨胀球面的瞬时半径和两角坐标",r"$P$ 的径向距离已由非稳定约束固定为 $vt$；仍可独立变化的是 $\theta,\varphi$，而实际微位移还含球面膨胀的径向部分。"),
"polar":("极坐标中随位置旋转的正交基矢",r"径向与横向单位矢量随 $\theta$ 改变。先把速度写成径向、横向两项，再求导时须同时对基矢求导。"),
"spherical":("球坐标的径向、极角和方位角位移",r"三个线元分别为 $\dd r,r\dd\theta,r\sin\theta\dd\varphi$；第三项的纬圈半径是 $r\sin\theta$，不能漏掉这个度量因子。"),
"moving-frame":("原点平移与坐标基矢转动",r"先减去原点位移 $\vect R=(X,Y)$，再将同一个相对位置投影到转过 $\theta$ 的新轴上。对坐标变换求导时，平移和基矢转动均随时间变化。"),
"conical-pendulum":("收短摆绳的摆角和瞬时轨道",r"摆长沿绳方向改变，方位角对应的水平轨道半径为 $l\sin\theta$；因而 $\varphi$ 的广义动量含 $l^2\sin^2\theta$，收绳时不能视为常系数。"),
"kepler-time":("随时间变化的中心引力和极径",r"力始终沿 $PO$，所以对 $O$ 的力矩为零；但力的强度显含时间，角动量守恒与能量是否守恒须分别判断。"),
"scaled-oscillator":("谐振坐标与指数标度后的振动",r"原坐标 $q$ 具有指数包络，标度坐标 $\bar q=e^{\gamma t}q$ 消去了包络；这项坐标变化不能直接把原哈密顿量当成新系统的守恒能量。"),
"unwinding-cylinder":("两侧对称解绕的切线绳段",r"圆筒两侧的直绳段与筒面相切，另一侧由中心对称得到。绳不打滑联系的是筒转角、切点方位和打开长度，公式只在仍有筒面接触的阶段有效。"),
"routh-hoop":("可绕竖直直径转动的圆环与小珠",r"小珠到竖直轴的距离是 $a\sin\theta$；它使绕轴惯量成为 $I+ma^2\sin^2\theta$，消去循环坐标时应固定角动量 $J$。"),
"physical-pendulum":("固定轴与偏离铅垂线的刚体质心",r"质心 $G$ 距支点轴为 $a$，重力矩的力臂是 $a\sin\theta$；小角展开后用刚体对该固定轴的惯量 $I$，不能用质点式 $Ma^2$ 代替。"),
"foucault-polar":("共转坐标中椭圆的主轴与极角",r"椭圆的轴角与质点的瞬时极角不同；只有共转系中的特定线偏振解才有 $J=0$，一般初态应保留椭圆的横向运动。"),
"resistor-chain":("无限电阻链的节点和对地支路",r"每个整数节点均通过 $r$ 接地，相邻节点通过 $R$ 相连；在零号节点注入电流后，两侧节点电势必须满足同一差分方程及无穷远有界条件。"),
"six-atom-ring":("六原子的周期边界与切向小位移",r"相邻原子之间的力取决于位移差，首尾相接给出 $u_{j+6}=u_j$；允许波数由这个周期边界量子化，不能使用自由端链的边界条件。"),
"moment-translation":("同一质量元的坐标整体平移",r"平移前后的质量元相同，改变的是坐标中的三个分量；把每个分量的幂按二项式展开，再对同一个质量测度积分。"),
"square-moments":("第一象限的均匀正方形与面积微元",r"积分区域是从 $0$ 到 $l$ 的正方形，原点在角点；奇数矩一般不为零，不能误用以板中心为原点的对称性。"),
"convolution":("卷积中的两个位置矢量相加",r"$\vect r=\vect r'+(\vect r-\vect r')$ 把卷积积分中的两个独立变量分开；指数因子因此可分解成两项，矩展开则产生三个二项式系数。"),
"axis-rotations":("主动转动的轴、初始矢量与转角",r"主动旋转改变物理矢量，实验室坐标轴保持固定；判断不同轴转动是否对易时必须保持同一右手定则和同一先后次序。"),
"matrix-exponential":("绕固定单位轴的有限转动",r"平行 $\vect n$ 的分量不变，垂直分量在二维平面内转动；叉乘生成元的幂可按这两类分量分别求和。"),
"omega-transform":("同一角速度矢量在转动基底中的分量",r"题设只取 $SO(3)$ 中的正交正向变换；叉乘方向与坐标三重积均按同一右手系变化，才可将叉乘矩阵的共轭变换与矢量变换对应。"),
"axis-inertia":("质量元到任意轴的垂直距离",r"任意轴方向为单位矢量 $\vect n$，质量元到轴的距离是 $r_\perp$；把 $r_\perp^2=r^2-(\vect n\cdot\vect r)^2$ 积分后才得到惯量的二次型。"),
"nutation":("对称陀螺的轴倾角与小偏离",r"恒定倾角 $\theta_0$ 是有效势的一处驻点；小偏离 $\delta\theta$ 的恢复系数来自该处二阶导数，必须同时检查驻点是否稳定。"),
"triangle-top":("等边三角板的支点、中线与水平底边",r"$O$ 是固定支点，$G$ 在中线上，底边 $AB$ 保持水平。进动与章动均需使用板相对 $O$ 的惯量，且微章动时应固定竖直轴角动量。"),
"max-entropy":("速度分布的矩约束与熵极值",r"横轴覆盖整个实数速度区间；归一化、零均值和二阶矩是三个独立积分约束，分别用拉格朗日乘子加入变分。"),
"stress-divergence":("微小体元两侧牵引力的差",r"相对两面的外法线相反，两侧应力分量的差除以体积才形成散度；本构关系随后把应力导数转成位移的二阶导数。"),
"beam-bending":("矩形梁的几何尺寸与端弯矩",r"梁长为 $L$，厚度方向为 $h$，截面宽为 $b$；弯曲后中性层与偏离中性层的纤维长度不同，应变由这段几何长度差求出。"),
"cylinder-torsion":("固定底面与转过小角的圆柱顶面",r"底面取 $z=0$，顶面取 $z=L$；各截面转角按 $z$ 插值，再由半径方向上的位移差求剪应变和剪应力。"),
"vorticity":("流体涡管中的伸长和体积变化",r"流体微团随速度场运动；沿涡度方向的速度梯度使涡管伸长，局部体积膨胀则另由 $\nabla\cdot\vect v$ 控制。两项来源不同。"),
"strain-rate":("流体微团在局部速度梯度下的形变",r"速度梯度的对称部分改变长度和夹角，反对称部分只描述瞬时刚性转动；对它们求随体导数时还须保留基于矩阵乘法的二次项。"),
"hangar-lift":("半圆形机库截面和外部来流",r"屋顶表面为 $r=R$，内压为远处静压；将外部压强差沿屋顶外法线投影到竖直方向，再对半圆周积分。"),
"bernoulli-principle":("同一流线上的两个状态",r"先沿 $A$ 到 $B$ 的同一条流线积分动量方程。不同流线上的常数能否统一，是额外的无旋性问题，不由定常条件单独保证。"),
"cylindrical-couette":("同轴圆柱与黏性环隙",r"两个边界的切向速度分别为 $\omega_1R_1,\omega_2R_2$；剪应力依赖 $\partial_rv_\varphi-v_\varphi/r$，不能直接把平板的速度梯度照搬进来。"),
"falling-cylinder-viscosity":("圆柱下落与封闭杯中的环隙回流",r"小圆柱向下排开的体积必须通过环隙向上返回；因此环隙速度同时受壁面拖曳和压力梯度驱动，不能只保留零压差的 Couette 项。"),
"isoperimetric":("定周长闭曲线的有向面积",r"闭曲线有选定走向，有向面积随走向改变符号，周长则不变；证明须先取绝对值，等号条件再决定几何形状。"),
"brachistochrone":("相同端点之间的下降候选轨道",r"重力沿向下的 $y$ 正向，起点 $A$ 的速度为零；每条候选轨道在深度 $y$ 的速率均由相同势能差给出，时间差来自路径弧长。"),
"least-dissipation":("有给定电导率的区域与固定边界",r"区域内的 $\vect K$ 与 $\sigma$ 已知，电势是待变函数；变分固定边界值并满足同一个功率约束，不能把不同边界条件的试函数混在一起。"),
"central-brachistochrone":("从给定释放半径出发的中心力轨道",r"释放点半径是 $r_0$，路径上的瞬时半径为 $r$；速率由这两个半径对应的势能差确定，再以极坐标弧长建立最速泛函。"),
"geodesic":("曲面参数网格、端点与候选曲线",r"$u^1,u^2$ 是曲面坐标，实际弧长由度量 $g_{ij}$ 给出；曲线加速度的切向部分与法向弯曲必须分开，参数的选取也应说明。"),
"minimal-surface":("固定边界曲线内的曲面变化",r"边界曲线保持固定，内部允许法向微位移；切向变化只对应重新参数化，驻值条件来自法向变分的系数。"),
"rod-noether":("弹性棒局部段的应力与动量通量",r"对 $x$ 与 $x+\dd x$ 之间的小棒段列平衡，应力通量之差改变该段机械动量；场位移 $\xi$ 的整体平移对称性对应这条局域守恒式。"),
"shear-circle":("单位圆在小纯剪切下的主方向",r"位移与原位置的关系取到应变的一阶；主方向相对原坐标转过 $45^\circ$，一个方向伸长、另一方向缩短，不能把纯剪切误作整体转动。"),
"rank3-decomp":("三个矢量指标的共同转动与角动量耦合",r"先把前两个自旋 $1$ 耦合成 $j_{12}=0,1,2$，再各与第三个自旋 $1$ 耦合。相同最终 $J$ 来自不同路径时要保留相应重数。"),
}


def editorial_corrections(text):
    marker="% AdvancedMechanicsAssumptions20261023-v1"
    text=text.replace(r"\dot{\bar q}^{,2}",r"\dot{\bar q}^{\,2}")
    if marker in text:return text
    text=text.replace("从应力张量的局域动量平衡", "对均匀、各向同性的小应变线弹性体，取常量拉梅参数。由应力张量的局域动量平衡")
    text=text.replace("在无黏正压流体中证明",r"在无黏正压流体中，假设单位质量体力为势场 $-\nabla\phi$，证明")
    text=text.replace(r"设理想流体满足 $\rho=\rho(p)$。证明",r"设理想流体满足 $\rho=\rho(p)$，忽略体力，并将速度梯度分为对称部分 $\bm U$ 与反对称部分 $\bm W$。证明")
    text=text.replace("间隙内充满不可压缩牛顿流体，黏度为 $\\eta$。求定常速度场", "间隙内充满不可压缩牛顿流体，黏度为 $\\eta$。忽略端部效应，两个圆柱壁均满足无滑移条件。求定常速度场")
    text=text.replace("这是缓变极限，不是对任意有限 $\\gamma$ 的精确能量守恒。",r"""这是缓变极限，不是对任意有限 $\gamma$ 的精确能量守恒。
还可给出对全部时间成立的界，避免把短时估计直接外推到 $1/\gamma$。
由守恒量 $\mathcal E=m(\dot{\bar q}^{\,2}+\Omega^2\bar q^2)/2$，有
\[
 H-\mathcal E=-m\gamma\bar q\dot{\bar q}+m\gamma^2\bar q^2,
 \quad |H-\mathcal E|\le\frac{\gamma\mathcal E}{\Omega}
 +\frac{2\gamma^2\mathcal E}{\Omega^2}.
\]
因而 $|H(t)-H(0)|\le2\gamma\mathcal E/\Omega+4\gamma^2\mathcal E/\Omega^2$。
在题设固定初值且 $\gamma\to0^+$ 时，$\mathcal E$ 有界、$\Omega\to\omega>0$，
故这个一致界在 $t=1/\gamma$ 时仍趋于零。
""")
    text=text.replace(r"无章动要求",r"以下在球坐标无奇异区域 $0<\theta_0<\pi$ 内讨论。轴向姿态 $\theta_0=0,\pi$ 不能直接代入含 $\sin\theta$ 分母的式，应在横向倾斜坐标中另行线性化。无章动要求")
    return marker+"\n"+text


def apply_file_revision(text):
    text=editorial_corrections(text)
    if MARKER in text:return refresh_figures(text)
    text=text.replace("质量为 $m$ 的质点被约束在 $x^2+y^2+z^2-v^2t^2=0$ 上。", "设 $v>0,t>0$。质量为 $m$ 的质点被约束在 $x^2+y^2+z^2-v^2t^2=0$ 上。")
    text=text.replace("对 $L=(m\\dot q^2-kq^2)/2$：", "设 $m,k>0$；涉及缓变极限时取 $0<\\gamma<\\sqrt{k/m}$，并固定不随 $\\gamma$ 改变的有限初始位置与速度。对 $L=(m\\dot q^2-kq^2)/2$：")
    text=text.replace("若绳总长度为 $L$，讨论", "若两侧可打开绳长的总和为 $L$，讨论")
    text=text.replace("将速度耦合二维谐振子改用极坐标",r"对 $L=m(\dot x^2+\dot y^2)/2-m\omega^2(x^2+y^2)/2-m\Omega(x\dot y-y\dot x)/2$，改用极坐标")
    text=text.replace("区域 $D$ 内电导率为", "区域边界的电势给定，假定以下功率约束存在可行函数。区域 $D$ 内电导率为")
    text=text.replace("绕过顶点 $O$ 的竖直轴定点转动，且 $AB$ 始终水平。", "以顶点 $O$ 为固定支点运动，允许绕过 $O$ 的竖直轴进动，并约束 $AB$ 始终水平。")
    def revise(m):
        label=re.search(r"\\label\{advA1:ex:([^}]+)\}",m[2])
        if not label or label[1] not in SPECS:return m[0]
        key=label[1];caption,link=SPECS[key];question=m[2];answer=m[5]
        question+=figure("advA1:fig:quality-"+key+"-q",caption+"（题设几何）",geometry(key))
        if r"\begin{tikzpicture}" not in answer:
            answer=figure("advA1:fig:quality-"+key+"-a",caption+"（解答辅助图）",geometry(key,True))+"图~\\ref{advA1:fig:quality-"+key+"-a}中，"+link+"\n"+answer
        else:
            answer="题图~\\ref{advA1:fig:quality-"+key+"-q}中，"+link+"\n"+answer
        return m[1]+question+m[3]+m[4]+answer+m[6]
    return MARKER+"\n"+PATTERN.sub(revise,text)


def refresh_figures(text):
    pattern=r"\\begin\{qualityfigure\}\s*\\begin\{tikzpicture\}\[>=Latex,font=\\small\]\n.*?\\end\{tikzpicture\}\s*\\figcap\{(.*?)\}\\label\{(advA1:fig:quality-([a-z-]+)-([qa]))\}\s*\\end\{qualityfigure\}"
    return re.sub(pattern,lambda m:figure(m[2],m[1],geometry(m[3],m[4]=="a")).strip(),text,flags=re.S)


def main():
    import argparse,json
    parser=argparse.ArgumentParser();parser.add_argument("--atlas",action="store_true");parser.add_argument("--render-atlas",action="store_true");parser.add_argument("--audit",action="store_true");parser.add_argument("--pdf-audit",action="store_true");args=parser.parse_args()
    for filename in FILES:
        path=BOOK/"advanced"/filename;old=path.read_text();new=apply_file_revision(old)
        if old!=new:path.write_text(new);print(filename)
    folder=BOOK/"build/quality-mechanics/A1";folder.mkdir(parents=True,exist_ok=True)
    if args.atlas:
        source="\n".join((BOOK/"advanced"/fn).read_text()for fn in FILES)
        entries=[]
        for key,(caption,_)in SPECS.items():
            for side in("q","a"):
                if "advA1:fig:quality-"+key+"-"+side in source:entries.append((key,side,caption,geometry(key,side=="a")))
        preamble=r"""\documentclass[UTF8,zihao=-4,oneside,openany]{ctexbook}
\input{style.tex}\geometry{a4paper,landscape,margin=12mm}\pagestyle{plain}
\newsavebox{\reviewbox}
\newcommand{\ReviewPicture}[1]{\sbox{\reviewbox}{#1}%
\ifdim\wd\reviewbox>.92\linewidth\sbox{\reviewbox}{\resizebox{.92\linewidth}{!}{\usebox{\reviewbox}}}\fi
\ifdim\dimexpr\ht\reviewbox+\dp\reviewbox\relax>.31\textheight\resizebox*{!}{.31\textheight}{\usebox{\reviewbox}}\else\usebox{\reviewbox}\fi}
\begin{document}
"""
        chunks=[preamble]
        for i,(key,side,caption,body)in enumerate(entries):
            if i and i%4==0:chunks.append(r"\clearpage"+"\n")
            elif i and i%2==0:chunks.append(r"\par\vspace{4mm}"+"\n")
            elif i%2:chunks.append(r"\hfill"+"\n")
            chunks.append(r"\noindent\begin{minipage}[t][.43\textheight][t]{.48\linewidth}\centering\small\textbf{"+key+" / "+side+"}\\\\[2mm]"+caption+r"\par\smallskip\ReviewPicture{\begin{tikzpicture}[>=Latex,font=\small]"+body+r"\end{tikzpicture}}\end{minipage}"+"\n")
        chunks.append(r"\end{document}");(folder/"new-figures.tex").write_text("".join(chunks));print("atlas",len(entries))
    if args.render_atlas:
        import fitz
        from PIL import Image
        pdf=fitz.open(folder/"new-figures.pdf")
        for start in range(0,len(pdf),4):
            tiles=[]
            for page in list(pdf)[start:start+4]:
                pix=page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False);tiles.append(Image.frombytes("RGB",[pix.width,pix.height],pix.samples))
            w=max(im.width for im in tiles);h=max(im.height for im in tiles);sheet=Image.new("RGB",(2*w,2*h),"white")
            for i,im in enumerate(tiles):sheet.paste(im,((i%2)*w,(i//2)*h))
            out=folder/f"atlas-sheet-{start//4+1:02d}.png";sheet.save(out);print(out)
    if args.audit:
        rows=[]
        for fn in FILES:
            source=(BOOK/"advanced"/fn).read_text()
            for m in PATTERN.finditer(source):
                key=re.search(r"\\label\{advA1:ex:([^}]+)\}",m[2])[1]
                rows.append({"file":fn,"key":key,"question_tikz":r"\begin{tikzpicture}"in m[2],"solution_tikz":r"\begin{tikzpicture}"in m[5],"numbered_figure_reference":bool(re.search(r"\\ref\{advA1:fig:[^}]+\}",m[5]))})
        (folder/"audit.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2));print("audit",len(rows))
    if args.pdf_audit:
        import fitz
        doc=fitz.open(folder/"A1-standalone.pdf");blank=[]
        for i,page in enumerate(doc):
            core=fitz.Rect(0,50,page.rect.width,page.rect.height-50);text=page.get_text(clip=core).strip()
            pix=page.get_pixmap(matrix=fitz.Matrix(.5,.5),clip=core,colorspace=fitz.csGRAY,alpha=False)
            if len(text)<5 and sum(v<245 for v in pix.samples)/len(pix.samples)<.0003:blank.append(i+1)
        log=(folder/"A1-standalone.log").read_text();aux=(folder/"A1-standalone.aux").read_text();mismatches=[];checked=0
        for m in re.finditer(r"\\newlabel\{(advA1:fig:quality-[^}]+)\}\{\{([^}]+)\}.*?\{figure\.advA1\.figure\.(\d+)\}",aux):
            checked+=1
            if m[2]!="A1."+m[3]:mismatches.append(m[1])
        report={"pages":len(doc),"blank_body_pages":blank,"overfull":log.count("Overfull"),"undefined":log.count("undefined"),"multiply_defined":log.count("multiply defined"),"missing_glyph":log.count("Missing character"),"new_figure_numbers_checked":checked,"figure_number_mismatches":mismatches}
        (folder/"pdf-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2));print("pdf-audit",report)


if __name__=="__main__":main()
