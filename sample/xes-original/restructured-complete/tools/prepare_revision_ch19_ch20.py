"""Reproducible text corrections against the immutable pre-revision sources."""
from pathlib import Path
import re
from build_review_ch19_ch20 import ARCHIVE, book

def source(section,name):
 return (ARCHIVE/'source'/section/name).read_text()
def put(section,name,text):
 (book.LEGACY/section/name).write_text(text)
def rep(text,old,new):
 assert old in text,old[:100]
 return text.replace(old,new)
S32='thirty-second-section';S33='thirty-third-section';S34='thirty-fourth-section';S35='thirty-fifth-section'

t=source(S32,'content.tex')
t=rep(t,'$10^{-15}\\,\\mathrm m$ 的原子核','约 $1$--$10\\,\\mathrm{fm}$（$10^{-15}$--$10^{-14}\\,\\mathrm m$，随核的质量数而变）的原子核')
t=rep(t,'图1.1把原讲义中的层级关系重新画成同一条尺度链','图1.1把这些层级关系放在同一条尺度链上')
t=rep(t,'夸克带有 $e/3$ 的分数电荷','夸克及反夸克的电荷可为 $\\pm e/3$ 或 $\\pm2e/3$')
t=rep(t,'=8.987\\,551\\,787\\,368\\,176\\,4\\times10^9',r'\approx8.99\times10^9')
t=rep(t,'图1.2左侧是库仑的线描肖像，右侧是扭秤的结构示意。扭丝转过的角度反映','图1.2左侧是库仑肖像，中间显示悬丝与横杆，右侧是与横杆同高的水平俯视图。固定带电球 $B$ 与活动带电球 $A$ 处在同一水平面；$O$ 是悬丝转轴，$D$ 是平衡物。$A$ 受到沿 $BA$ 的斥力，只有该力相对 $O$ 的力矩使悬丝扭转。扭丝转过的角度反映')
t=rep(t,'库仑与扭秤实验的重新绘制。图只保留实验所需的悬丝、横杆、带电小球和刻度关系。','库仑与扭秤。活动球 $A$、固定球 $B$ 与横杆同高；俯视图的虚线为横杆零位。')
put(S32,'content.tex',t)

t=source(S32,'examples.tex')
t=rep(t,'规定从垂线向上、向下量得的端点角分别为 $\\theta_1,\\theta_2$。积分给出\n垂直导线方向和平行导线方向的分量',r'''规定从垂线向上、向下量得的端点角分别为 $\theta_1,\theta_2$。
对应端点为 $y_1=a\tan\theta_1$、$y_2=-a\tan\theta_2$。沿用图1.6的坐标，
\[
 \dd E_x=k\lambda\frac{a\,\dd y}{(a^2+y^2)^{3/2}},\qquad
 \dd E_y=-k\lambda\frac{y\,\dd y}{(a^2+y^2)^{3/2}},\quad k=\frac1{4\pi\varepsilon_0}.
\]
负号来自电荷元指向 $P$ 的纵向位移为 $-y$。令 $y=a\tan u$，则 $\dd y=a\sec^2u\dd u$，有
\[
 E_x=\frac{k\lambda}{a}\int_{-\theta_2}^{\theta_1}\cos u\,\dd u,
 \qquad E_y=-\frac{k\lambda}{a}\int_{-\theta_2}^{\theta_1}\sin u\,\dd u.
\]
上下限代入后，垂直导线方向和平行导线方向的分量分别为''')
t=rep(t,r'\textbf{3. 无限大平面。} 取横跨平面的薄圆柱 Gauss 面。',r'''\textbf{3. 无限大平面。} 为直接积分，以 $P$ 在平面上的垂足为圆心，将平面分成半径 $s$、宽度 $\dd s$ 的圆环。
环电荷 $\dd q=2\pi\sigma s\dd s$，到 $P$ 的距离为 $\sqrt{a^2+s^2}$。环内横向场相消，法向分量相加：
\[
 E_\perp=\frac{\sigma a}{2\varepsilon_0}\int_0^\infty
 \frac{s\,\dd s}{(a^2+s^2)^{3/2}}
 =\frac{\sigma a}{2\varepsilon_0}
 \left[-\frac1{\sqrt{a^2+s^2}}\right]_0^\infty
 =\frac{\sigma}{2\varepsilon_0}\quad(a>0).
\]
这个结果由库仑积分独立得到，接着用高斯定律校验。取横跨平面的薄圆柱 Gauss 面。''')
t=rep(t,'分别积分法向与横向分量，得到',r'''电荷元到 $P$ 的方向正比于 $(-x,0,a)$，故
\[
 E_z=\frac{\sigma}{2\pi\varepsilon_0}\int_{-b_1}^{b_2}\frac{a\,\dd x}{a^2+x^2}
 =\frac{\sigma}{2\pi\varepsilon_0}\left[\arctan\frac xa\right]_{-b_1}^{b_2},
\]
\[
 E_x=-\frac{\sigma}{2\pi\varepsilon_0}\int_{-b_1}^{b_2}\frac{x\,\dd x}{a^2+x^2}
 =-\frac{\sigma}{4\pi\varepsilon_0}\ln\frac{a^2+b_2^2}{a^2+b_1^2}.
\]
再用 $\cos\theta_i=a/\sqrt{a^2+b_i^2}$，得到''')
t=rep(t,'一个金属球体内有一个球形空洞，不空的地方均匀带有体电荷密度 $\\rho$。','一个绝缘球体内有一个球形空洞，不空的地方均匀带有固定的体电荷密度 $\\rho$。另比较：若它换成达到静电平衡的金属且空洞内无电荷，会有什么不同？')
t=rep(t,'所以第一问的叠加结果适用于绝缘体中冻结的均匀体电荷；若原题使用“金属”\n一词，只能把它理解为几何形状的口误，或者明确说明尚未达到静电平衡。','所以第一问的叠加结果适用于绝缘体中固定的均匀体电荷；金属静电平衡模型则由等势边界条件决定，不能沿用均匀体电荷假设。')
t=t.replace('两两相距 $l$','相邻两电荷相距 $l$（两端相距 $2l$）')
t=rep(t,'改变常数 $C$ 就得到图中的不同场线；',r'''这一第一积分可以直接核验。令 $F=Q(x+a_0)/r_1-q(x-a_0)/r_2$，
逐项求导得到 $F_x=yE_y/k$、$F_y=-yE_x/k$。沿电场线的切向位移满足
$(\dd x,\dd y)\parallel(E_x,E_y)$，所以
\[
 \dd F=F_x\dd x+F_y\dd y=\frac yk(E_y\dd x-E_x\dd y)=0.
\]
故 $F=C$ 确为场线方程，而不是单凭外观猜出的曲线。改变常数 $C$ 就得到图中的不同场线；''')
put(S32,'examples.tex',t)

t=source(S33,'content.tex')
t=rep(t,'折线仅连接同一电子壳层周期内的代表性数据。','覆盖 $Z=1$--$108$，符号区分元素类别；空心点表示含理论或估计标识的数据。')
t=rep(t,'的能量只能激发原子，原子退激时会发光，形成辉光放电。若电子能量足以电离原子，每次碰撞都会产生更多\n电子，电子数呈雪崩式增长，进入弧光或火花放电阶段。闪电就是大尺度气体击穿。','的能量足以激发原子，原子退激时便可能发光；碰撞能量超过电离阈值时，还可能电离原子并产生新的电子。\n超过阈值不意味着每次碰撞都电离，碰撞过程具有一定概率。电离产生的载流子足以补偿复合、扩散等损失时，\n放电才能持续。辉光放电同样包含电离，并常依靠阴极二次电子发射补充电子，不能说成“只激发、不电离”。\n辉光、弧光、火花是不同的放电状态，区别还取决于气压、电流、气体温度、电极及供电条件；弧光通常具有\n较大的持续电流和明显加热，火花则是击穿时的快速放电。图2.5中的闪电是大尺度气体击穿。')
t=rep(t,r'\boxed{U=\frac12Q\varphi(R)',r'\label{shell-energy}\boxed{U=\frac12Q\varphi(R)')
t=t.replace('与式(2.11)完全一致',r'与式\eqref{shell-energy}完全一致')
put(S33,'content.tex',t)

t=source(S33,'examples.tex')
t=rep(t,'与上一讲的矢量积分一致。',r'''与上一讲的矢量积分一致。非对称时不能只对 $a$ 求导就认为得到了全部电场。
在一般观察点 $(x,y)$、$x>0$ 写成
\[
 \varphi(x,y)=k\lambda\left[\operatorname{arsinh}\frac{L_1-y}{x}
 +\operatorname{arsinh}\frac{L_2+y}{x}\right].
\]
于是先对 $x,y$ 分别求偏导，再令 $(x,y)=(a,0)$：
\[
 E_x=\frac{k\lambda}{a}\left(\frac{L_1}{\sqrt{a^2+L_1^2}}+
 \frac{L_2}{\sqrt{a^2+L_2^2}}\right),\quad
 E_y=k\lambda\left(\frac1{\sqrt{a^2+L_1^2}}-\frac1{\sqrt{a^2+L_2^2}}\right).
\]
这也恢复了非对称有限导线的两个分量。''')
t=rep(t,'有限系统可以取无穷远为零点；',r'''\textbf{6. 无限长条带。} 条带位于 $z=0$，沿 $y$ 方向无限，宽度范围 $-b_1\le u\le b_2$。
取有限参考点 $P_0=(0,0,z_0)$，$z_0>0$。窄条 $\dd\lambda=\sigma\dd u$ 是无限线电荷，因而
\[
 \varphi(x,z)-\varphi(0,z_0)
 =-\frac{\sigma}{4\pi\varepsilon_0}\int_{-b_1}^{b_2}
 \ln\frac{(x-u)^2+z^2}{u^2+z_0^2}\,\dd u.
\]
分母固定参考电势，且比值无量纲。对 $x,z$ 求偏导，积分中的参考项导数为零：
\[
 E_x=\frac{\sigma}{2\pi\varepsilon_0}\int_{-b_1}^{b_2}
 \frac{x-u}{(x-u)^2+z^2}\,\dd u,\qquad
 E_z=\frac{\sigma}{2\pi\varepsilon_0}\int_{-b_1}^{b_2}
 \frac{z}{(x-u)^2+z^2}\,\dd u.
\]
在 $P=(0,0,a)$ 处得到
\[
 E_x=\frac{\sigma}{4\pi\varepsilon_0}\ln\frac{a^2+b_1^2}{a^2+b_2^2},\qquad
 E_z=\frac{\sigma}{2\pi\varepsilon_0}\left(\arctan\frac{b_1}{a}+\arctan\frac{b_2}{a}\right),
\]
与直接积分的条带结果相同；当 $b_1=b_2$ 时横向分量确为零。

有限系统可以取无穷远为零点；''')
t=rep(t,'这是一族通过 $(\\pm a,0)$ 的圆；$\\beta=0$ 对应 $x$ 轴。',r'''这是一族通过 $(\pm a,0)$ 的圆；$y=0$ 是需单独保留的直线分支。
为何有向角不变？令 $u=\ln(r_-/r_+)$，直接求导可得
$\beta_x=u_y$、$\beta_y=-u_x$。而 $\boldsymbol E=-(\lambda/2\pi\varepsilon_0)\nabla u$，
所以 $\nabla\beta\cdot\boldsymbol E=0$，沿场线 $\beta$ 不变。
等势圆的圆心 $(c,0)$ 和半径 $R_c$ 满足 $c^2-R_c^2=a^2$；
场线圆的圆心 $(0,d)$ 和半径 $R_d$ 满足 $R_d^2-d^2=a^2$。
两圆相交于 $P=(x,y)$ 时，相应半径的点积为
$ (x-c,y)\cdot(x,y-d)=x^2+y^2-cx-dy=0$，证明两族曲线正交。''')
t=rep(t,'电势只依赖 $\\xi$，而 $\\xi,\\eta$ 是正交坐标，所以电场线是 $\\eta=$ 常量的坐标线：',r'''由两焦点距离可反解出
\[
 x=a\xi\eta,\qquad s=a\sqrt{(\xi^2-1)(1-\eta^2)},\quad \xi\ge1,\quad -1\le\eta\le1.
\]
两条坐标切向量的点积为
\[
 \frac{\partial(x,s)}{\partial\xi}\cdot\frac{\partial(x,s)}{\partial\eta}
 =a^2\xi\eta-
 a^2\frac{\xi\sqrt{1-\eta^2}}{\sqrt{\xi^2-1}}
 \frac{\eta\sqrt{\xi^2-1}}{\sqrt{1-\eta^2}}=0.
\]
因此它们正交。电势只依赖 $\xi$，场垂直于 $\xi=$ 常量的椭圆，
沿 $\eta=$ 常量的坐标线，即''')
t=rep(t,'一个带电小球 $A$ 的质量为 $m$，电量为 $+q$，用一根长度未知的绳悬挂。小明手持另一个同样带正电的\n小球 $B$ 缓慢移动并排斥 $A$，使其始终近似处于平衡；最终 $B$ 球占据 $A$ 原来的竖直位置，而 $A$ 球上升高度 $h$。\n求这个过程中小明做的功以及电场能量的增量。',r'''一个可视为点电荷的小球 $A$，质量为 $m$、电量为 $+q$，用长度未知的轻绳悬挂。
另一小球 $B$ 也带电 $+q$，初始足够远，以两球初始相互作用能为零的极限处理，$A$ 初始竖直静止。
小明缓慢移动 $B$ 并排斥 $A$，使 $A$ 始终近似平衡；最终 $B$ 占据 $A$ 原来的最低位置，$A$ 上升 $h$。
忽略两球尺寸变化及 $B$ 的重力功（所求手的功仅计克服静电相互作用的部分），求小明做的功和电场能量增量。''')
t=rep(t,'散射角 $\\Theta$ 与瞄准参数满足',r'''为补出角度关系，令 $u=1/r$，以最近点的径向为极角 $\psi=0$。
比奈方程为 $u''+u=-m\kappa/L^2$，其对称解为
\[
 u=\frac{m\kappa}{L^2}(\epsilon\cos\psi-1).
\]
将最近点 $u'(0)=0$ 代入能量式
$E_k=(L^2/2m)(u'^2+u^2)+\kappa u$，得到
$\epsilon^2=1+2E_kL^2/(m\kappa^2)=1+(2E_kb/\kappa)^2$。
两条渐近线处 $u=0$，故 $\cos\psi_\infty=1/\epsilon$。
速度入射方向与入射位置矢量反向，因而偏转角
$\Theta=\pi-2\psi_\infty$，有
$\sin(\Theta/2)=1/\epsilon$。消去 $\epsilon$ 后，散射角 $\Theta$ 与瞄准参数满足''')
t=rep(t,'由 $b(\\Theta)$ 求导：',r'''令 $B_0=\kappa/(2E_k)$，则
\[
 \left|\frac{\dd b}{\dd\Theta}\right|=\frac{B_0}{2}\csc^2\frac\Theta2,
 \qquad \frac{\dd\sigma}{\dd\Omega}=
 \frac{b}{\sin\Theta}\left|\frac{\dd b}{\dd\Theta}\right|.
\]
代入 $b=B_0\cot(\Theta/2)$ 和 $\sin\Theta=2\sin(\Theta/2)\cos(\Theta/2)$，得到''')
put(S33,'examples.tex',t)

t=source(S34,'content.tex')
t=t.replace('对球外任意点 $P$，几何关系保证','对球面上任意点 $P$，几何关系保证')
t=t.replace('再用式(3.1)','再用 $\\sigma=\\varepsilon_0 E_n$')
t=t.replace('式(3.8)','等离子体频率公式')
t=rep(t,'若把碰撞造成的平均阻力写成 $-m\\nu\\dot x$，运动方程会多出 $\\nu\\dot x$ 项。$\\nu$ 很大时振荡很快\n衰减，载流子趋于新的静电平衡；$\\nu$ 较小而外场随时间变化时，体系会在 $\\omega\\approx\\omega_p$ 附近\n出现强烈集体响应。',r'''若平均阻力为 $-m\nu\dot x$，令 $y=x-x_0$，则
\[
 \ddot y+\nu\dot y+\omega_p^2y=0,\qquad
 s_\pm=\frac{-\nu\pm\sqrt{\nu^2-4\omega_p^2}}2.
\]
当 $0<\nu<2\omega_p$ 时为衰减振荡，振幅包络为 $e^{-\nu t/2}$；
$\nu=2\omega_p$ 时为临界阻尼；$\nu>2\omega_p$ 时为非振荡的过阻尼趋近。
特别是 $\nu\gg\omega_p$ 时，慢根 $s_+\simeq-\omega_p^2/\nu$，
弛豫时间约为 $\nu/\omega_p^2$，所以不能笼统说“碰撞越强，平衡越快”。
弱阻尼而外场交变时，在适当驱动下可于 $\omega\approx\omega_p$ 附近出现强响应。''')
t=t.replace('此时 $q=e,m=m_e$','此时带符号电荷为 $q=-e$、$m=m_e$，频率中的 $q^2=e^2$')
t=rep(t,r'\plasmaSlabFigure',r'''图中以正载流子向右位移表示正负面电荷的几何关系。
若载流子是电子，$q=-e$，在向右外场下平衡位移 $x_0<0$，电子向左；
两端面的符号仍应从乘积 $nqx$ 判断，不能仅由位移方向猜测。
\plasmaSlabFigure''')
t=t.replace('法拉第笼的重绘情景图。雷电流沿外表面流动，导体材料和封闭内部保持无静电场。','法拉第笼的屏蔽情景。理想静电极限下腔内无场；雷击瞬态的安全还依赖连接、接地及屏蔽完整性。')
t=t.replace('电离层反射实现远距离通信的重绘示意','电离层反射实现远距离通信')
put(S34,'content.tex',t)

t=source(S34,'examples.tex')
t=t.replace('用一个内半径为 $R$ 的接地金属球壳','用一个内半径为 $R$、外半径为 $R_o>R$ 的同心接地金属球壳')
t=t.replace('若外表面也是半径 $R$ 的球面','外表面为半径 $R_o$ 的球面')
t=t.replace('只是电势整体增加常量 $-q/(4\\pi\\varepsilon_0R)$','只是电势整体增加常量 $-q/(4\\pi\\varepsilon_0R_o)$')
t=t.replace('+q^2/(8\\pi\\varepsilon_0R)','$BAD$') if False else t
t=t.replace(r'+q^2/(8\pi\varepsilon_0R)',r'+q^2/(8\pi\varepsilon_0R_o)')
t=t.replace(r'U_{\rm neutral}=U_{\rm in}+\frac{q^2}{8\pi\varepsilon_0R}',r'U_{\rm neutral}=U_{\rm in}+\frac{q^2}{8\pi\varepsilon_0R_o}')
t=rep(t,r'\textbf{(2) 内表面面电荷密度。}',r'''以上像电荷写法取 $0<d<R$。若真实电荷恰在球心，取 $d\to0$ 的极限即可：
球腔内 $\varphi=-kq/r+kq/R$，$\boldsymbol E=-kq\hat{\boldsymbol r}/r^2$；
内表面 $\sigma_{\rm in}=q/(4\pi R^2)$，避免把发散的像电荷坐标当作真实奇点。

\textbf{(2) 内表面面电荷密度。}''')
t=rep(t,'\n(PLACEHOLDER)', '') if False else t
t=rep(t,'\n\\begin{xesolution}\n接地平面的像电荷为位于板另一侧对称位置的 $-q$。',r'''
\begin{xesolution}
这里“瞬间移动”采用明确的冻结感应电荷近似：在搬运阶段保持原有面电荷分布，
只计算真实电荷在该固定静电场中的势能变化；不把这一步解释为真实电荷的无限速运动。
若实际问极快运动时外力的总功，还必须给出运动过程，并计入惯性和电磁辐射，
仅凭初末位置不能决定这些附加项。
接地平面的像电荷为位于板另一侧对称位置的 $-q$。'''.replace(r'\n'+'\n','\n'))
t=t.replace('并可能有少量电磁辐射','或以电磁辐射形式向外传出；两者的份额取决于暂态动力学，不能由静电模型确定')
t=t.replace('赤道处 $\\sigma=0$，但外侧仍存在切向于远场方向的弯曲场线，\n不会穿入导体内部。','赤道处球面场为零；离开球面后，赤道外侧的场逐渐恢复，场线绕过导体而不进入其内部。')
put(S34,'examples.tex',t)

t=source(S35,'content.tex')
t=t.replace('式(4.1)和式(4.4)形式相同','孤立导体与双极电容器的两式 $Q=CU$ 形式相同')
t=t.replace('外半径 $b$ 固定时，内半径 $a$ 越接近 $b$，靠近内极处的场越强，电势差越小，\n电容迅速增大。','外半径 $b$ 固定时，$a$ 越接近 $b$，$\\ln(b/a)$ 越小，电容迅速增大。\n若保持 $Q$ 不变，电势差减小，而内表面场 $Q/(2\\pi\\varepsilon_0ha)$ 反而随 $a$ 增大而减小；\n若保持电压不变，场强的变化须代入 $Q=CU$ 后另作判断。')
t=t.replace('把两状态代入式(4.11)','把两状态代入倒易关系')
t=rep(t,'它把一个状态的电荷与另一个状态的电势交叉相乘再求和，两种交叉方式所得结果完全相同。该关系与导体\n的具体形状和介质边界无关，是静电学中一类更一般的倒易定理。',r'''它把一个状态的电荷与另一个状态的电势交叉相乘再求和，两种交叉方式所得结果完全相同。
其条件是几何结构、介质分布和线性互易的介电响应在两状态中相同，无穷远边界项消失。
在导体外区域使用 $\boldsymbol E=-\nabla\varphi$、$\boldsymbol D=\varepsilon\boldsymbol E$，
有 $\boldsymbol D\cdot\nabla\varphi'=\boldsymbol D'\cdot\nabla\varphi$。
区域内无自由体电荷时，
\[
 \nabla\cdot(\varphi'\boldsymbol D-\varphi\boldsymbol D')=0.
\]
积分并用散度定理。区域在导体表面的外法线指入导体，故该处通量分别为 $-Q_i$、$-Q_i'$；
又因各导体等势，边界积分便给出
$-\sum_i\varphi_i'Q_i+\sum_i\varphi_iQ_i'=0$。
若区域另有固定点电荷，还须把它们的 $q\varphi'$ 与 $q'\varphi$ 项一起计入。''')
t=rep(t,'矩阵，并由倒易定理证明矩阵是对称的。',r'''矩阵，并由倒易定理证明矩阵是对称的。
还可直接处理一边定电荷、一边接地的混合条件：设状态 A 为 $Q_1=Q$、$\varphi_2=0$，
状态 B 为 $\varphi_1'=0$、$Q_2'=Q'$，则
\[
 Q_2\varphi_2'=Q_1'\varphi_1.
\]
这里两侧分别是“感应电荷乘另一状态的非零电势”，不能误删感应电荷项。
它与分别指定净电荷或指定电势的前两种选择，均由同一个两导体倒易式直接得到。''')
t=t.replace('实验上，把同一种电介质完全填满不同形状的真空电容器','对于均匀、线性、各向同性介质，在几何结构不变且全部有效电场区域被填满的近似下，把同一种电介质完全填满不同形状的真空电容器')
t=rep(t,r'\dielectricMeterFigure',r'''图4.8中先充电再断开电源，接入高输入阻抗静电计；要求静电计输入电容远小于待测电容，
且观测时间远短于漏电时间常数。这样电容器自由电荷近似不变。
右图的介质紧贴两块极板并覆盖全部正对面积，不能留有额外空气层；右侧表针较小的偏转表示 $U$ 降低。
\dielectricMeterFigure''')
t=t.replace('因此电压表读数降低','因此高输入阻抗静电计的电压读数降低')
put(S35,'content.tex',t)

t=source(S35,'examples.tex')
for i in range(1,12):t=t.replace(f'第 {i} 题',f'例题4.{i}')
t=rep(t,'这两列像电荷产生的等势面恰包含两个相切球面。',r'''下面验证这个序列为何成立。令 $K=4\pi\varepsilon_0RV$。
在右球球心 $x=R$ 放 $q_1=K$，其自身在右球面产生常电势 $V$。
左侧第 $n$ 枚电荷在 $x=-R/n$，距右球心为 $R+R/n$；关于右球反演，
\[
 q_{n+1}=-\frac{R}{R+R/n}q_n=-\frac n{n+1}q_n,\qquad
 x_{n+1}=R-\frac{R^2}{R+R/n}=\frac{R}{n+1}.
\]
因此左侧第 $n$ 枚与右侧第 $n+1$ 枚在右球面电势相消，只留下右球心的 $V$。
左右互换同理，故两个球面都是电势 $V$。接触点处取连续极限。
这两列像电荷产生的等势面恰包含两个相切球面。''')
t=rep(t,'这是二维静电问题。采用双极坐标',r'''先说明为什么圆柱截面可由两条虚拟线电荷构造。令 $d=L/2$、$a=\sqrt{d^2-R^2}$，
在图4.13中 $x=\pm a$ 放虚拟线电荷 $\pm\lambda$。它们位于各自圆柱内部，
只在柱外使用对应电势 $\varphi=(\lambda/2\pi\varepsilon_0)\ln(r_-/r_+)$。
取 $\xi=\ln(r_-/r_+)$ 为常量，配方得到圆心 $a\coth\xi$、半径 $a/|\sinh\xi|$；
因此选择 $\cosh\xi_0=d/R$ 就恰好得到两条真实圆柱边界。
每柱外围的高斯面包围一根虚拟线电荷，故计算出的 $\lambda$ 就是真实单位长度总电荷。

这是二维静电问题。采用双极坐标''')
t=rep(t,'代入上式解得\n\\[\n A=',r'''比较两侧 $\cos\theta$ 的系数，第一条边界条件给出 $A=E_0-B/R^3$；
由 $E_r=-\partial\varphi/\partial r$，第二条给出
$\varepsilon_r A=E_0+2B/R^3$。将第一式代入第二式：
\[
 (\varepsilon_r+2)\frac B{R^3}=(\varepsilon_r-1)E_0.
\]
再回代即得
\[
 A=''')
t=rep(t,r'\boldsymbol p_{\rm eff}=4\pi\varepsilon_0R^3',r'\boldsymbol p_{\rm eff}=4\pi\varepsilon_0R^3')
t=rep(t,'大气等效为厚度 $5\\,\\mathrm{km}$ 的另一极板，带正电荷。','把距地表 $5\\,\\mathrm{km}$ 的同心球面作为带正电的等效外极板，两极之间的大气层厚度为 $5\\,\\mathrm{km}$。')
t=rep(t,'这个数量级说明全球雷暴活动确实可以维持大气电路；模型忽略了电离层高度变化、局部天气和电导率随\n高度变化，但抓住了电容与漏电并存的主要物理机制。','这个数值是题设均匀电阻率和固定等效高度模型的预测，不能单凭它认定真实全球雷电次数或验证大气电路。\n真实电导率随高度变化，雷暴供电机制与单次输送电荷也有分布；本模型用于说明电容储能与漏电并存时的收支关系。')
put(S35,'examples.tex',t)
print('Text sources updated from archived baseline.')
