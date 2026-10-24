"""Handwritten, editable TikZ geometries for the October 2026 audit.

Each key is (chapter, base-example ordinal). Question drawings contain given
conditions only; calculated curves, projections and auxiliary constructions
belong to the solution. Positive field/electric-charge conventions are explicit.
"""


def tikz(body):
    return (r"\begin{tikzpicture}[>=Latex,font=\small,every node/.style={fill=none},scale=.88]" + "\n"
            + body + "\n" + r"\end{tikzpicture}")


SPECS = {}


def add(ch, i, q=None, qc=None, ar=None, a=None, ac=None, a_macro=None):
    spec = {k: v for k, v in locals().items() if k not in ("ch", "i") and v is not None}
    SPECS[ch, i] = spec


RING = r"""
\draw[thick] (0,0) circle (1.15);
\draw[->] (0,0)--(1.15,0) node[midway,below]{$r$};
\fill (0,0) circle (1.2pt) node[below left]{$O$};
\draw[DeepBlue,thick,->] (1.15,0)--(1.15,.8) node[right]{$\omega>0$};
\draw[thick] (-1.4,-.12)--(-.9,-.12) (-1.4,.12)--(-.9,.12);
\node[left] at (-1.4,0){截面 $S$};
"""
CONDUCTOR = r"""
\draw[thick] (0,-.35) rectangle (3.3,.35);
\draw (0,0)--(-.7,0) (3.3,0)--(4,0);
\node[above] at (1.65,.35){$l,S,R$};
\node[below] at (1.65,-.35){$t=0$ 接通电压 $U$};
\draw[DeepBlue,->] (.45,0)--(2.75,0) node[midway,above]{$I$ 正方向};
"""
ORBIT_Q = r"""
\fill (0,0) circle (2pt) node[below]{$P$};
\draw[DeepBlue,thick,->] (0,0)--(1.5,0) node[above]{$\boldsymbol v\perp\boldsymbol B$};
\node at (3,0){$\boldsymbol B\;\odot$};
\node[below] at (3,-.45){$m,\ q$};
"""
ORBIT_A = r"""
\draw[thick] (0,0) circle (1.15);
\fill (0,0) circle (1.3pt) node[left]{$C$};
\fill (0,1.15) circle (2pt) node[above]{$P$};
\draw[DeepBlue,thick,->] (0,1.15)--(1.4,1.15) node[right]{$\boldsymbol v$};
\draw[->] (0,1.15)--(0,.4) node[right]{$\boldsymbol F_B$};
\draw[dashed] (0,0)--(0,1.15) node[midway,left]{$r$};
\node[right,align=left] at (1.5,-.25){$q>0,\ \boldsymbol B\;\odot$\\$\boldsymbol L,\boldsymbol\mu\;\otimes$};
"""
PLATES_B = r"""
\draw[very thick] (-.5,1.15)--(4,1.15) (-.5,-1.15)--(4,-1.15);
\node[above] at (1.7,1.15){正极板}; \node[below] at (1.7,-1.15){负极板};
\draw[->] (3,.7)--(3,-.5) node[midway,right]{$\boldsymbol E$};
\draw[<->] (-.8,-1.15)--(-.8,1.15) node[midway,left]{$d$};
\fill (0,.95) circle (1.8pt) node[below]{$+Q,\ v(0)=0$};
\node at (1.6,-.5){$\boldsymbol B\;\otimes$};
"""

# Current, resistance and actual source transformations.
add(21, 1, RING, r"题图：骤停前铜环的转向与被考察的导线截面。",
    r"截面 $S$ 固定在骤停后的晶格上；电子继续沿原切向运动，而常规电流反向，因此积分的是穿过该截面的电荷量。")
add(21, 2, CONDUCTOR, r"题图：圆柱导体在 $t=0$ 突然接通恒压源，箭头规定常规电流正向。",
    r"$I$ 的正向与电场相同，电子漂移反向；曲线初值 $I(0)=0$ 与远时极限 $U/R$ 分别确定积分常数和稳态。")
add(21, 3, ar=r"固定截面每经过一个周期 $T$ 收到整环电荷 $Q$；应以电荷正负决定常规电流相对转向的方向。")
add(21, 4, ar=r"电势曲线在阴极 $x=0$ 处斜率为零，正是空间电荷限制状态的边界；阳极 $x=L$ 的纵坐标为 $U$。")
add(21, 5, ar=r"半径为 $r$ 的球面面积为 $4\pi r^2$，该面上的总电流不随 $r$ 改变；从 $a$ 到 $b$ 的径向积分给出两壳电压。")
add(21, 6, ar=r"电子收集结束于 $t_e$，斜率随即减少；离子在 $t_i$ 收集完成后信号大小达到 $Ne/C$，实际阳极电压为其负值。")
add(21, 7, ar=r"两段弧连接同一对节点 $a,b$，故是并联；移动 $b$ 只改变 $R_1,R_2$ 的分配而保持两者之和为 $R$。")
add(21, 8, ar=r"两个电源支路和负载都接在同一对公共节点上；三个向右参考电流的代数和为零，某个电源支路电流为负即表示向左供电。",
    ac=r"解图：以公共节点电势差统一表示三个支路电流。")
add(21, 9, r"""
\draw (0,-.8) rectangle (2.8,.8);
\draw (1.4,0) circle (.3);\draw[->] (1.4,-.2)--(1.4,.2);
\draw (1.4,.3)--(1.4,.8) (1.4,-.3)--(1.4,-.8);
\draw (2,-.8)--(2,-.3) rectangle (2.3,.3);\draw (2.15,.3)--(2.15,.8);
\node[right] at (2.3,0){$r$};\node[left] at (1.1,0){$I_N$};
\draw (2.8,.8)--(4,.8) (2.8,-.8)--(4,-.8);
\fill (4,.8) circle (1.5pt) node[right]{$+$};\fill (4,-.8) circle (1.5pt) node[right]{$-$};
\node[right] at (4,0){$U$};\draw[->] (3,.8)--(3.8,.8) node[midway,above]{$I$};
""", r"题图：有并联内阻 $r$ 的电流源端口，$I$ 取向负载输出为正。",
    r"端口的 $U,I$ 参考方向在两种表示中相同；并联内阻分走 $U/r$，所以负载电流是 $I_N-U/r$。")
add(21, 11, ar=r"固定端点 $A,B$ 后，$C,D$ 可由网络对称性互换，因而 $CD$ 无电流；其余三条通路才参与端口并联。",
    ac=r"解图：端点固定后检查 $C,D$ 的等势对称性。")
add(21, 10, ar=r"相邻端点激励的电势分布与对角激励不同；相邻情形的左边中点为 $7V/10$，直接决定从输入端流出的第二条支路电流。")
add(21, 12, ar=r"中间 $N-2$ 个节点全部等势，因此它们之间的内部支路不载流；每个中间节点仍各通过一个电阻连接端点 $A$ 和 $B$。")
add(21, 13, ar=r"六个中间节点为 $V/2$，它们之间虽有连线但不载流；$A,B$ 间没有直接电阻，端口电流仅来自六条 $2R$ 通路。")
add(21, 14, ar=r"三种端点选择分别改变等势层，须对每个内部节点检验KCL；体对角接法在输入端的三个邻点均为 $3V/5$。")
add(21, 15, ar=r"虚线框内的无限尾部从第一对节点看仍为 $X$，它与竖直电阻 $R$ 并联；入口上下两只 $R$ 则串在该并联块两侧。")
add(21, 16, ar=r"两个有效横向模式分别为 $(1,0,-1)$ 与 $(1,-2,1)$，不能只以一个端口电阻代替三端尾部；输入向量投影到各模式后分别响应。")
add(21, 17, ar=r"中点以内的尾网边长为 $a/2$，故三端等效三角形每支为 $k\rho a/2$；外侧六段金属丝仍各有电阻 $\rho a/2$。")
add(21, 18, ar=r"相似子网的拓扑因子为 $5/3$，每段实际长度缩小又使电阻乘 $1/2$；两者同时作用才得到随阶数变化的 $5/6$。")

# Charged-particle kinematics: initial conditions are separated from trajectories.
add(22, 1, ORBIT_Q, r"题图：粒子经加速电势差 $U$ 后在 $P$ 垂直进入磁场。",
    r"磁力始终沿 $PC$ 的向心方向且不做功；先由加速区求动量，再以 $p=|q|Br$ 求半径。", a=ORBIT_A,
    ac=r"解图：取正电荷、磁场出纸面的一种旋向；负电荷的圆心在初速度另一侧。")
add(22, 2, r"""
\draw[thick] (0,-1)--(0,1);\draw[thick] (1,-1)--(1,1);
\node[above] at (.5,1){相同加速电压 $U$};
\draw[DeepBlue,->] (1.3,0)--(3,0) node[midway,above]{$e^-,p,\alpha$};
\draw[dashed] (3.3,-1)--(3.3,1);\node[right] at (3.4,.5){同一 $\boldsymbol B\;\odot$};
""", r"题图：三种粒子分别经历相同电势差并进入同一磁场。",
    r"三种粒子在磁场区的半径由 $m/|q|$ 的平方根控制，而周期由 $m/|q|$ 本身控制；电子的弯曲方向须另按负电荷反向。",
    a=ORBIT_A, ac=r"解图：以一个正电荷的回旋圆说明半径与周期所用的几何。")
add(22, 3, ORBIT_Q, r"题图：给定 $m,q,v,B$ 的垂直入射初态，轨道圆心待定。",
    r"$CP$ 是回旋半径，$\boldsymbol L$ 由 $\boldsymbol{CP}\times m\boldsymbol v$ 决定；正电荷的常规环流顺时针，磁矩因而入纸面，与外磁场相反。",
    a=ORBIT_A, ac=r"解图：轨道半径、速度及磁矩的方向约定（图示 $q>0$）。")
add(22, 5, r"""
\draw[->] (0,0)--(5,0) node[right]{$z$};
\fill (0,0) circle (1.5pt) node[below]{$O$};
\draw[DeepBlue,->] (0,0)--(3,.75);\draw[DeepBlue,->] (0,0)--(3,-.75);
\draw[thick] (4,-1.15)--(4,1.15) node[above]{荧光屏};
\node[below] at (2,-.95){$z=L$；最大初始夹角 $\theta$};
\node[above] at (1.7,.7){$\boldsymbol B\parallel+z$};
""", r"题图：出射口、屏的位置及初始发散锥；直线只表示出射方向。",
    r"轴向飞行时间近似为 $L/v$；横向回旋位移在屏处为零的条件是同一时间内完成整数圈。")
add(22, 7, r"""
\draw[thick] (0,1)--(4,1) (0,-1)--(4,-1);
\draw[DeepBlue,->] (-1,0)--(.5,0) node[midway,above]{$\alpha,\ v$};
\draw[->] (2,.6)--(2,-.6) node[right]{$\boldsymbol E$};
\node at (3,0){$\boldsymbol B\;\otimes$};
\draw[thick] (4,-1)--(4,-.15) (4,.15)--(4,1);
""", r"题图：向右的正粒子束与交叉场；出口狭缝限定直线通过。",
    r"$\boldsymbol E$ 向下、$\boldsymbol B$ 入纸面时，正粒子所受电力向下、磁力向上；两者抵消只对 $v=E/B$ 成立。")
add(22, 9, r"""
\draw[thick] (-1,-1)--(4.5,-1) node[right]{$y=0$ 地面};
\fill (0,1) circle (1.8pt) node[above]{$P_0=(0,H)$};
\draw[DeepBlue,->] (0,1)--(0,.1) node[right]{$v_0$};
\draw[->] (3,1)--(3,.1) node[right]{$\boldsymbol g$};
\node at (1.6,.2){$\boldsymbol B\;\odot$};
\draw[<->] (-.6,-1)--(-.6,1) node[midway,left]{$H$};
""", r"题图：从高度 $H$ 竖直向下的初速度、重力与水平地面。",
    r"地面是 $y=0$，而不是初始位置所在的 $y=H$；比较的是整条回旋漂移轨迹的最低点与地面的间隙。")
add(22, 10, r"""
\foreach \y in {0,2}{\fill[DeepBlue!7] (0,\y) rectangle (4,\y+1);\node at (3,\y+.5){$\boldsymbol E\uparrow$};}
\foreach \y in {1,3}{\fill[gray!12] (0,\y) rectangle (4,\y+1);\node at (3,\y+.5){$\boldsymbol B\;\otimes$};}
\foreach \y in {0,1,2,3,4}{\draw[thin] (0,\y)--(4,\y);}
\fill (1,0) circle (1.8pt) node[below]{$+q,\ v_0=0$};
\draw[<->] (4.4,1)--(4.4,2) node[midway,right]{$d$};
""", r"题图：等厚的交替电场层与磁场层，粒子从最下电场层底部释放。",
    r"界面平行于 $x$ 轴；电场层增加动能，磁场层只改变速度方向。跨界时切向速度连续，不能在每一电场层重新设成零。")
add(22, 13, r"""
\draw[dashed] (0,0) circle (1.1);\fill (0,0) circle (1.2pt) node[below]{$C$};
\fill (0,1.1) circle (1.8pt) node[above]{$P$};
\draw[DeepBlue,->] (0,1.1)--(1.4,1.1) node[right]{$v$};
\draw[->] (0,1.15)--(0,1.8) node[right]{$\delta r$};
\draw[dashed,->] (0,0)--(0,1.1) node[midway,left]{$R$};
\node at (2.7,0){$\boldsymbol B\;\odot$};
""", r"题图：原半径 $R$ 的圆轨道，以及相对原圆心的微小径向扰动。",
    r"径向坐标以原圆心 $C$ 为参考；扰动轨道相对这个点的径向变化满足频率 $qB/m$ 的线性方程，因此径向周期等于回旋周期。")
add(22, 15, ORBIT_Q.replace(r"\odot", r"\otimes") + r"\draw[->] (1.3,-.6)--(.4,-.6) node[midway,below]{$\boldsymbol f=-\gamma\boldsymbol v$};",
    r"题图：垂直磁场中的初速度与线性阻尼力。",
    r"阻尼使速度大小指数衰减，磁力只转动速度方向；最后收敛点与初始回旋圆心一般不同。")
add(22, 16, ORBIT_Q + r"\draw[->] (4.4,-.8)--(4.4,.6) node[right]{$\boldsymbol E\parallel+y$};\node[below] at (0,-.6){$\boldsymbol f=-\gamma\boldsymbol v$};",
    r"题图：恒定交叉场与阻尼，初速度须与题设同时保留。",
    r"远时轨迹的切线沿稳态漂移速度；稳态电力、磁力和阻尼力的矢量和为零，不能继续把 $E/B$ 当成含阻尼时的全部漂移速率。")
add(22, 17, r"""
\draw[thick] (0,0) circle (1.1);\draw[dashed] (0,0)--(1.1,0) node[midway,below]{$r$};
\draw[DeepBlue,->] (0,1.1)--(1.1,1.1) node[right]{$\boldsymbol v$};
\node at (2.5,.2){$\boldsymbol B(z)\;\odot$};
\node[right] at (1.3,-.6){磁场沿轨道轴线缓慢变化};
""", r"题图：局部回旋轨道与其法向磁场，沿轴线的变化尺度远大于一圈内的变化。",
    r"环流法向由常规电流的右手法则确定，故 $\boldsymbol\mu=q\boldsymbol L/(2m)$；缓变场中守恒的是近似的 $E_\perp/B$，不能据此声称任意快速变场也保持轨道磁矩不变。")
add(22, 4, ar=r"同一段轨道上的两个半径相同、角速度大小却相差两倍；碰撞后切向速度反向，新的共同圆心关于碰撞点与旧圆心对称。")
add(22, 6, ar=r"相邻碰撞点 $P,Q$ 在桶心张角为 $\delta$；回旋圆心与桶心不是同一点，逃出条件是这个固定转角的整数倍恰为整周。")
add(22, 8, ar=r"摆线沿两板的方向漂移，真正决定是否撞到负板的是从正板量起的最大纵向位移；临界轨迹只与负板相切。")
add(22, 11, ar=r"电流沿 $+x$、外磁场沿 $+y$，正载流子被推向上表面；表面电荷建立向下霍尔场，规定上减下的电压因而为正。")
add(22, 12, ar=r"内外圆柱面之间的电场径向分布，磁力把径向漂移偏向方位方向；圆周无端点积累出可抵消整圈偏转的静电霍尔电势。")
add(22, 14, ar=r"圆轨道半径与小扰动都以同一轴心为参考；电场梯度改变径向回复项，须把磁力与角动量约束共同线性化。")

add(23, 8, r"""
\draw[->] (-2,0)--(4.5,0) node[right]{$z$};
\draw[thick] (0,0) ellipse (.25 and 1.2);\node[above] at (0,1.2){圆线圈 $R,I$};
\fill (-1.8,0) circle (1.6pt) node[below]{物点};
\draw[DeepBlue,->] (-1.8,0)--(-.6,.25) node[midway,above]{$v_0,\theta$};
\draw[<->] (-1.8,-.7)--(0,-.7) node[midway,below]{$u$};
""", r"题图：物点、圆线圈和近轴初始射线；成像位置由磁场聚焦决定。",
    r"线圈附近的高度 $\xi$ 近似不变，斜率突变等于 $-\xi/f$；左侧物距 $u$ 与右侧像距 $v$ 分别进入前后两段斜率。")
add(23, 9, r"""
\draw[->,thick] (0,0)--(0,2) node[above]{$\boldsymbol B_0$};
\draw[DeepBlue,->,thick] (0,0)--(1.2,1.3) node[right]{$\boldsymbol s$};
\draw[dashed] (1.2,0)--(1.2,1.3);
\draw[->] (2.2,0)--(3.4,0) node[right]{$\boldsymbol B_1(t)\perp\boldsymbol B_0$};
""", r"题图：初始自旋与纵向恒定场，以及待施加的横向旋转弱场。",
    r"$\boldsymbol s$ 在纵向场中的投影保持不变；共振横向场需在同向转动的随动系中分析，而不是把自旋简单画成沿合场静止。")
add(24, 10, ar=r"环内变化磁通产生的切向感生电场沿整个带电环做功；用 $\oint E_t\,\mathrm dl=-\mathrm d\Phi/\mathrm dt$ 才能建立角加速度方程。")
add(24, 13, ar=r"各电压表的引线与圆环组成不同闭合路径，所围变化磁通不同；两读数相减须连同两条引线路径一起使用法拉第定律。")
add(24, 14, ar=r"电压表接线限定了测量路径；即使两端点相同，绕过变化磁通的不同路径也不能直接等同为同一个静电势差。")
add(24, 16, r"""
\draw (0,0) rectangle (4,2);\draw (2,0)--(2,.7) rectangle (2.35,1.3);\draw (2.175,1.3)--(2.175,2);
\draw (0,.8) rectangle (.3,1.4);\node[left] at (0,1.1){$R_1$};
\draw (3.7,.8) rectangle (4,1.4);\node[right] at (4,1.1){$R_2$};
\node[right] at (2.35,1){$R_3$};
\node at (1,1){$S_1$};\node at (3.1,1){$S_2$};
\node[above] at (2,2.15){$\boldsymbol B(t)\;\odot$};
\draw[->] (.6,.4)--(1.2,.4);\draw[->] (2.6,.4)--(3.2,.4);
""", r"题图：任意网络的两个相邻独立回路示意；面积和绕行方向必须与回路方程一致。",
    r"$R_3$ 是两个回路的共有支路，按图中同为逆时针的回路电流取向，其支路电流是两个网孔电流之差；每个回路另有感应电动势 $-kS_j$。",
    ac=r"解图：独立回路的面积、方向与共有电阻决定线性方程的系数。")
add(24, 19, ar=r"串联路径中的同一电流依次改变电容电荷、产生电阻压降和自感电动势；取 $I=-\dot q$ 时，电容放电方向与电荷减少一致。")
add(24, 20, ar=r"电源与串联的 $R,L,C$ 在同一回路中；稳态特解叠加的衰减自由振荡必须一起满足接通瞬间的电荷与电流初值。")


def series(names, bottom="正弦电源"):
    body = r"\draw (0,0)--(0,1.4)--(.5,1.4);"
    for j, name in enumerate(names):
        x = .5 + j * 1.5
        body += f"\n\\draw ({x},1.15) rectangle ({x+1},1.65);\\node at ({x+.5},1.4){{$" + name + "$};"
        if j + 1 < len(names):
            body += f"\\draw ({x+1},1.4)--({x+1.5},1.4);"
    x = .5 + (len(names)-1) * 1.5 + 1
    body += f"\n\\draw ({x},1.4)--({x+.5},1.4)--({x+.5},0)--(0,0);"
    body += f"\n\\node[below] at ({(x+.5)/2},0){{{bottom}}};"
    return body


WAVES = r"""
\draw[->] (0,0)--(4.8,0) node[right]{$t$};\draw[->] (0,-1.1)--(0,1.5) node[above]{$u$};
\draw[DeepBlue,thick] (0,1)--(2,1)--(2,-1)--(4,-1);
\draw[dashed] (2,-1.1)--(2,1.2);\node[below] at (2,-1.15){$T/2$};\node[below] at (4,-1.15){$T$};
\node[left] at (0,1){$U_0$};\node[left] at (0,-1){$-U_0$};
\begin{scope}[xshift=6cm]
\draw[->] (0,0)--(4.6,0) node[right]{$t$};\draw[->] (0,-1.1)--(0,1.5) node[above]{$u$};
\draw[DeepBlue,thick] (0,-1)--(2,1)--(4,-1);
\node[below] at (4,-1.15){$T$};\node[left] at (0,1){$U_0$};
\end{scope}
"""
add(25, 1, WAVES, r"题图：同幅值、同周期的方波与对称三角波；跳变线只表示方波的瞬时切换。",
    r"两条曲线的有符号面积在一周期内均抵消，但求有效值时必须先平方再积分；三角波在线性上升段的 $u^2$ 平均值为 $U_0^2/3$。",
    ac=r"解图：按每段波形的实际持续时间计算平均值与均方值。")
add(25, 2, ar=r"上、下两支路有相同端口电压，故应先把各自阻抗取倒数得到导纳再相加；纯电阻端口要求两个无功导纳相抵。",
    ac=r"解图：并联支路按导纳相加，不能把两支路阻抗直接相加。")
add(25, 3, series(["R", "L", "C"], r"$U=10\,\mathrm V$，有效值"),
    r"题图：串联RLC及有效值电源，三个元件流过同一电流。",
    r"串联电流相同，电感与电容电压分别超前和滞后电流 $\pi/2$；谐振时它们互相抵消，电源电压才等于电阻电压。",
    a=r"""
\draw[->] (0,0)--(3,0) node[right]{$I,\ U_R=IR$};
\draw[DeepBlue,->] (0,0)--(0,1.6) node[above]{$U_L$};
\draw[DeepBlue,->] (0,0)--(0,-1.6) node[below]{$U_C$};
\node[right,align=left] at (.7,-.9){谐振时 $U_L=U_C$\\合电压沿 $U_R$};
""", ac=r"解图：以电流为相位基准的谐振电压相量。")
add(25, 4, series(["R", "L", "C"], r"恒定有效值 $U$，改变 $\omega$"),
    r"题图：在相同电源有效值下扫描串联RLC的频率。",
    r"$P/P_{\max}=1/2$ 对应电抗的两个有号取值 $X=\pm R$；低频支由电容占优，高频支由电感占优。",
    a=r"""
\draw[->] (0,0)--(5,0) node[right]{$\omega$};\draw[->] (0,-1.5)--(0,1.6) node[above]{$X$};
\draw[DeepBlue,thick] plot[smooth] coordinates{(.5,-1.4)(1,-1)(2,0)(3.2,1)(4.4,1.5)};
\draw[dashed] (0,-1)--(1,-1)--(1,0) (0,1)--(3.2,1)--(3.2,0);
\node[left] at (0,1){$R$};\node[left] at (0,-1){$-R$};
\node[below] at (1,0){$\omega_1$};\node[below] at (2,0){$\omega_0$};\node[below] at (3.2,0){$\omega_2$};
""", ac=r"解图：电抗 $X=\omega L-1/(\omega C)$ 单调增加，分别与 $\pm R$ 相交。曲线只示意单调性。")
add(25, 5, ar=r"电容支路提供正的导纳虚部，实际线圈支路提供负的导纳虚部；电阻 $r$ 使线圈导纳不能简写为 $1/(\mathrm i\omega L)$。",
    ac=r"解图：实际线圈的串联损耗电阻与并联电容。")
add(25, 6, r"""
\draw (0,0) rectangle (4,2);\draw (1,0)--(1,.7) rectangle (1.8,1.3);\draw (1.4,1.3)--(1.4,2);
\node[right] at (1.8,1){感性负载};
\draw (3.2,0)--(3.2,.8) (2.9,.8)--(3.5,.8) (2.9,1.1)--(3.5,1.1) (3.2,1.1)--(3.2,2);
\node[right] at (3.5,1){$C$};\node[left] at (0,1){$U,\omega$};
""", r"题图：电容并联在原负载两端，负载端电压和有功功率保持题设值。",
    r"电容电流竖直向上，抵消负载电流的滞后分量；水平有功分量 $P/U$ 保留，因此补偿后的电源电流最小。",
    a=r"""
\draw[->] (0,0)--(3,0) node[right]{$U,\ P/U$};
\draw[DeepBlue,->] (0,0)--(3,-1.4) node[right]{$I_{\rm load}$};
\draw[->] (3,-1.4)--(3,0) node[midway,right]{$I_C$};
\draw[dashed] (0,0)--(0,1);\node at (1.1,-.3){$\varphi$};
""", ac=r"解图：以电压为相位基准，电容补偿负载的无功电流。")
add(25, 7, ar=r"$i_1$ 从同名端流入，$u_2$ 的正端也取在线圈2的同名端，所以 $u_2=M\dot i_1$；若仅反接一组端点，公式符号才反转。",
    ac=r"解图：互感电压的正负由同名端和参考方向共同确定。")
add(25, 8, r"""
\draw[thick] (0,-1)--(0,1) (1.7,-1)--(1.7,1);
\foreach \y in {-.7,-.2,.3}{\draw (0,\y) arc[start angle=-90,end angle=90,x radius=.3,y radius=.25];\draw (1.7,\y) arc[start angle=270,end angle=90,x radius=.3,y radius=.25];}
\draw[thick] (.7,-1)--(.7,1) (.9,-1)--(.9,1);
\draw (1.7,1)--(3,1)--(3,.3) rectangle (3.35,-.3);\draw (3.175,-.3)--(3.175,-1)--(1.7,-1);
\node[right] at (3.35,0){$R_L$};\node[left] at (0,0){$U_1$};\node[above] at (.85,1.2){$N_1:N_2=n:1$};
""", r"题图：理想变压器与纯电阻副边负载。两侧导线没有电连接。",
    r"两绕组电压之比为 $n$，电流大小之比为 $1/n$；这两个比例共同使原边输入阻抗变为 $n^2R_L$，而两侧平均功率相等。",
    ac=r"解图：按电压比和电流比把副边负载折算到原边。")

add(26, 2, r"""
\fill[DeepBlue!8] (0,-.6) rectangle (4,.6);\draw[DeepBlue,->,thick] (0,0)--(3.5,0) node[midway,above]{$P,\ A$};
\draw[very thick] (4,-1)--(4,1) node[above]{完全吸收面};
\draw[->] (2,-.9)--(3,-.9) node[midway,below]{$\boldsymbol k\parallel\boldsymbol n$};
""", r"题图：均匀激光束正入射于完全吸收面，$A$ 为光束横截面积。",
    r"横截面 $A$ 垂直于传播方向，所以 $I=P/A$；完全吸收面每秒收到的法向动量为 $P/c$，除以面积才得到压力。",
    ac=r"解图：由垂直截面的能流确定场幅，再由吸收动量通量确定压力。")
add(26, 3, r"""
\draw[very thick] (-1,0)--(3.7,0) node[right]{薄膜 $A$};
\draw[dashed,->] (1,0)--(1,2) node[above]{$\boldsymbol n$};
\draw[DeepBlue,thick,->] (-.7,1.8)--(1,0);
\node[above left] at (-.5,1.6){入射光强 $I$};\node at (.65,.85){$\theta$};
""", r"题图：入射方向与薄膜法线成 $\theta$，$A$ 为薄膜本身的面积。",
    r"反射只反转法向动量，单个光子的法向变化量为 $2(E/c)\cos\theta$；薄膜截获的光功率还需乘投影因子 $\cos\theta$，所以共出现两个余弦。",
    a=r"""
\draw[thick] (-1,0)--(3.7,0);\draw[dashed] (1,0)--(1,2);
\draw[DeepBlue,thick,->] (-.7,1.8)--(1,0);\draw[DeepBlue,thick,->] (1,0)--(2.7,1.8);
\draw[->] (1,-.1)--(1,-1) node[right]{$\boldsymbol F_{\rm film}$};
\node at (.65,.8){$\theta$};\node at (1.35,.8){$\theta$};
""", ac=r"解图：镜面反射的切向动量不变，薄膜获得沿入射法向的冲量。")
add(26, 4, r"""
\fill[gray!10] (2,-1) rectangle (5,1);\draw[thick] (2,-1.1)--(2,1.1);
\draw[DeepBlue,->] (-.5,0)--(1.6,0) node[midway,above]{$E_i$};
\node[below] at (.5,-.6){真空 $n_1=1$};\node[below] at (3.5,-.6){介质 $n_2=n$};
\node[above] at (2,1.1){无自由面电流、无吸收};
""", r"题图：平面波由真空法向入射到无耗非磁介质。",
    r"界面左侧切向电场为 $E_i+E_r$，而磁场因反射传播方向倒转为 $(E_i-E_r)/Z_0$；右侧磁场为 $nE_t/Z_0$，两种连续条件缺一不可。",
    a=r"""
\draw[thick] (2,-1)--(2,1);\draw[DeepBlue,->] (-.5,.5)--(1.6,.5) node[midway,above]{$E_i,H_i$};
\draw[->] (1.6,-.5)--(-.5,-.5) node[midway,below]{$E_r,H_r$};
\draw[DeepBlue,->] (2.4,0)--(4.5,0) node[midway,above]{$E_t,H_t$};
\node[below] at (2,-1.15){$E_i+E_r=E_t,\quad H_i-H_r=H_t$（有号波幅）};
""", ac=r"解图：两侧的传播方向与界面切向场分解；磁场符号按传播方向单独判断。")
add(26, 5, r"""
\draw[very thick] (0,0) circle (1.05);\draw[->] (0,0)--(0,1.8) node[above]{$\Phi_{\rm ext}$ 法向};
\node[right,align=left] at (1.5,0){总电感 $L$\\$\Phi_{\rm ext}+LI=n\Phi_0$};
""", r"题图：超导环、外加磁通的正向与量子化约束。",
    r"每一条抛物线表示固定整数 $n$ 的电感能；平衡态取这些曲线的下包络，相邻曲线的交点才是简并磁通。",
    a=r"""
\draw[->] (0,0)--(5,0) node[right]{$\Phi_{\rm ext}/\Phi_0$};\draw[->] (0,0)--(0,2.1) node[above]{$U$};
\foreach \j in {1,2,3}{\draw[DeepBlue,domain=-.8:.8,smooth] plot ({\j*1.3+\x},{2*\x*\x});\node[below] at (\j*1.3,0){$\j$};}
\draw[dashed] (1.95,0)--(1.95,.85) (3.25,0)--(3.25,.85);
\node[above] at (2.6,1.6){$U_n\propto(\Phi_{\rm ext}/\Phi_0-n)^2$};
""", ac=r"解图：固定 $n$ 的能量抛物线及相邻量子态的交叉。")

# Geometrical optics. Angles are measured from the local surface normal.
MIRROR_Q = r"""
\draw[thick] (1,-1.732) arc[start angle=-60,end angle=60,radius=2];
\draw[->] (-1,0)--(2.6,0);\fill (0,0) circle (1.3pt) node[below]{$C$};
\fill (2,0) circle (1.3pt) node[below right]{$V$};
\draw[DeepBlue,->] (-1,1)--(1.732,1) node[pos=.5,above]{入射光};
\draw[dashed] (0,0)--(1.732,1) node[midway,below]{$R$};
\draw[<->] (-.65,0)--(-.65,1) node[midway,left]{$d$};
\node[above right] at (1.732,1){$P$};
"""
add(27, 1, MIRROR_Q, r"题图：平行光在高度 $d$ 处入射球面，半径 $CP$ 是局部法线。",
    r"$CP$ 与轴的夹角为 $\alpha$，反射线 $PM$ 因而与轴成 $2\alpha$；从 $V$ 向 $C$ 为正时，$s$ 是有向轴坐标，几何距离须取 $|s|$。",
    a=MIRROR_Q+r"\draw[DeepBlue,->] (1.732,1)--(1.1547,0);\fill (1.1547,0) circle (1.5pt) node[below]{$M$};\node at (.65,.24){$\alpha$};",
    ac=r"解图：由半径法线构成反射角，再延长反射线与轴相交。图示为 $s>0$ 的一种口径。")
ROTATING_MIRROR = r"""
\draw[very thick] (0,-.2)--(0,2.4) node[above]{墙};
\draw[thick] (0,0)--(-1,2.47) node[left]{$B$};
\fill (0,0) circle (1.5pt) node[right]{$O$};
\fill (0,1) circle (1.5pt) node[right]{$A$};
\fill (-.404,1) circle (1.5pt) node[left]{$C$};
\draw[DeepBlue,->] (0,1)--(-.404,1);
\draw[DeepBlue,->] (-.404,1)--(0,1.39) node[right]{$D$};
\draw[<->] (.7,0)--(.7,1) node[midway,right]{$d$};
\node at (-.19,.55){$\theta$};
"""
add(27, 2, ROTATING_MIRROR, r"题图：镜面在墙左侧，转轴在 $O$，入射点为 $C$。图示属于能反射回墙的姿态。",
    r"入射点 $C$ 到墙的水平距离为 $d\tan\theta$；反射线 $CD$ 与向右水平线成 $2\theta$，故 $AD=d\tan\theta\tan2\theta$，并须满足 $\cos2\theta>0$。",
    ac=r"解图：把光点高度拆为固定的 $OA$ 与随镜角变化的 $AD$。")
add(27, 3, r"""
\draw[thick] (0,0) circle (1.2);\draw[very thick] (.6,-1.039) arc[start angle=-60,end angle=60,radius=1.2];
\draw[DeepBlue,->] (-2.4,.6)--(-1.039,.6);\draw[DeepBlue,->] (-1.039,-.6)--(-2.4,-.6);
\draw[<->] (-2.7,-.6)--(-2.7,.6) node[midway,left]{$d$};
\draw[dashed] (0,0)--(0,1.2) node[midway,right]{$R$};\node[below] at (0,0){$C$};
\node[above] at (1.7,.3){镀银面};
""", r"题图：圆柱横截面、右侧反射面及两条反向平行的外部光线。",
    r"入射点 $A$ 与出射点 $B$ 对称于水平轴，$d$ 是两外部光线的间距；角度必须相对半径法线量取。",
    a_macro="CylinderDiagram", ac=r"解图：两次折射和一次反射的完整圆内光路。")
add(27, 4, r"""
\draw[thick] (0,0) circle (1.5);\fill[gray!25] (0,0) circle (.65);
\draw[<->] (0,0)--(1.5,0) node[midway,below]{$b$};
\draw[<->] (0,0)--(0,.65) node[midway,left]{$a$};
\foreach \y in {-.9,0,.9}{\draw[DeepBlue,->] (-2.6,\y)--(-1.55,\y);}
\node[right] at (1.4,1.2){透明材料 $n$};\node[below] at (0,-1.7){内表面完全吸收};
""", r"题图：平行入射光束、外球半径与涂黑内球面；实际吸收边界由折射决定。",
    r"吸收横截面的边缘光线在内球面相切；半径、入射高度和折射角共同确定允许入射的最大冲量参数。")
add(27, 5, r"""
\fill[DeepBlue!7] (0,-1) rectangle (1.2,1);\draw[thick] (0,-1)--(0,1) (1.2,-1)--(1.2,1);
\draw[dashed] (-2,0)--(3.3,0);\fill (-2,0) circle (1.6pt) node[above]{观察者};\fill (3.3,0) circle (1.6pt) node[above]{光源};
\draw[<->] (-2,-.5)--(0,-.5) node[midway,below]{$L$};
\draw[<->] (0,-.5)--(1.2,-.5) node[midway,below]{$D,n$};
\draw[<->] (1.2,-.5)--(3.3,-.5) node[midway,below]{$S$};
""", r"题图：观察者、两平行界面与点光源的真实间距。",
    r"只有玻璃内的厚度 $D$ 要换成近轴视厚度 $D/n$；观察者一侧的 $L$ 和光源一侧的 $S$ 都在空气中，保持原值。")
PRISM = r"""
\draw[thick] (0,1.5)--(-1.5,-1)--(1.5,-1)--cycle;
\node[above] at (0,1.5){$A$};\node at (0,-.4){$n$};
\draw[DeepBlue,->] (-2.5,.9)--(-.65,.417);
\draw[DeepBlue,->] (-.65,.417)--(.65,.417);
\draw[DeepBlue,->] (.65,.417)--(2.4,-.15);
\draw[dashed] (-1.3,.807)--(0,.027) (0,.027)--(1.3,.807);
\node[above] at (-1.6,.75){$i_1$};\node at (-.35,.2){$r_1$};\node at (.35,.2){$r_2$};\node[above] at (1.55,.6){$i_2$};
"""
add(27, 6, PRISM, r"题图：棱镜的顶角、两次入射角与内部折射角，角度均从法线量起。",
    r"内部两角满足 $r_1+r_2=A$；可出射边界对应第二面折射角达到临界值或第一面掠入射，最小偏向由对称光路 $r_1=r_2$ 给出。",
    ac=r"解图：以两条界面法线分解偏向角，分别检查对称点与可出射边界。")
DROPLET_Q = r"""
\draw[thick] (0,0) circle (1.3);\fill (0,0) circle (1.2pt) node[below]{$O$};
\draw[DeepBlue,->] (-2.6,.6)--(-1.153,.6);\draw[dashed] (-1.153,.6)--(0,0);
\node[left] at (-2.4,.9){平行日光};\node at (.3,.7){$n$};
\draw[->] (0,0)--(1.3,0) node[midway,below]{$R$};
"""
add(27, 7, DROPLET_Q, r"题图：球形水滴中的初次入射，半径给出界面法线。",
    r"入滴、一次内反射、出滴三段构成主虹路径；特征方向由总偏转角对入射角的一阶导数为零确定，而非由全反射临界角确定。",
    a_macro="RainbowDiagram", ac=r"解图：水滴中的折射、内反射与出射方向。")
add(27, 8, r"""
\draw[thick] (-2,0) circle (.8);\node[below] at (-2,-1){球形水滴};
\draw[thick] (1:.9)--(61:.9)--(121:.9)--(181:.9)--(241:.9)--(301:.9)--cycle;
\node[below] at (0,-1){六角冰晶截面};
\draw[DeepBlue,->] (-4,.3)--(-2.9,.3);\draw[DeepBlue,->] (-1.1,.3)--(-.6,.3);
\node[above,align=center] at (-1,1.2){比较太阳方位、角半径\\及可能的折射/反射界面};
""", r"题图：两种常见散射体的截面。判断彩色弧带须结合光源方位和界面几何。",
    r"球形水滴与有固定面角的冰晶具有不同的可用光路；先用弧带相对太阳的位置筛选几何，再用色散和反射次数检验，不能单凭颜色就命名为彩虹。",
    ac=r"解图：把球面折射和固定棱角折射作为不同的待检验模型。")
add(27, 9, PRISM.replace("{$n$}", "{$n_C,n_D,n_F$}"),
    r"题图：固定棱镜时各色光共用同一入射方向，分别具有不同的折射率。",
    r"固定的是 $i_1$ 而不是每个颜色的最小偏向状态；先从 $\sin i_1=n_D\sin(A/2)$ 求共同入射角，再分别计算 $C,F$ 的第二面出射角。",
    ac=r"解图：在相同外部入射角下逐色应用两次斯涅尔定律。")
add(27, 10, r"""
\draw[thick] (0,0) rectangle (3,1.8);\node at (2,.6){玻璃 $n$};
\draw[DeepBlue,->] (-1.1,.1)--(0,.8);\draw[DeepBlue,->] (0,.8)--(1.3,1.8);
\draw[dashed] (-.6,.8)--(.8,.8) (1.3,1.1)--(1.3,2.4);
\node at (.45,1){$r$};\node at (1.1,1.45){$90^\circ-r$};
\node[above] at (2.4,2.3){相邻侧面};
""", r"题图：光由一个侧面折射入砖，随后遇到与其垂直的相邻界面。",
    r"两侧面的法线互相垂直，第二面的入射角为 $90^\circ-r$；第一面可达的最大折射角与第二面的临界角必须同时比较。",
    ac=r"解图：相邻侧面的两个内部入射角互余，边界由两次折射的可达角联合限制。")
add(27, 11, r"""
\fill[DeepBlue!8] (0,0)--(3.5,2.021)--(3.5,-2.021)--cycle;
\draw[thick] (0,0)--(3.5,2.021) (0,0)--(3.5,-2.021);
\fill (0,0) circle (1.5pt) node[left]{$D$};
\fill (1.7,1.674) circle (1.5pt) node[above]{$A$};\fill (1.7,-1.674) circle (1.5pt) node[below]{$B$};
\draw[dashed] (1.7,1.674)--(2,1.155) node[right]{$C$};\node[right] at (1.95,1.6){$h$};
\draw[dashed] (0,0)--(1.7,1.674) node[midway,above left]{$l$};
\node at (.7,0){$\alpha$};\node[right] at (3.6,0){湖中速度 $v/2$};
""", r"题图：两直岸、对称房屋和垂足，阴影为水域。",
    r"上、下岸关于角平分线对称，最优水陆交点应与这个对称性相容；每段距离须乘其所在区域的慢度，不能把跨岸线段都按步行速度处理。")
add(27, 12, r"""
\foreach \y in {-1,0,1}{\draw[DeepBlue,->] (3,\y)--(.2,\y);}
\draw[dashed,thick] (0,-1.4)--(0,1.4) node[above]{待设计反射面};
\fill (1,0) circle (1.8pt) node[below]{$F$};\node[above] at (2,1.3){所有平行光均须到达 $F$};
""", r"题图：给定平行入射方向和要求的共同焦点，反射面形状未知。",
    r"同一入射波面到 $F$ 的总光程必须相同；对右方来的光，令反射点轴坐标为 $x$，便有 $PF-x$ 为常数，化简得到抛物线截面。",
    a=r"""
\draw[thick,domain=-1.6:1.6,smooth,variable=\y] plot ({\y*\y/4},\y);
\foreach \y in {-1.4,-.7,.7,1.4}{\pgfmathsetmacro{\xx}{\y*\y/4}\draw[DeepBlue,->] (3,\y)--(\xx,\y);\draw[DeepBlue,->] (\xx,\y)--(1,0);}
\fill (1,0) circle (1.7pt) node[below]{$F$};\draw[->] (-.4,0)--(3.4,0) node[right]{$x$};
\node[above] at (1.8,1.7){$y^2=4fx$，图示 $f=1$};
""", ac=r"解图：抛物线的每个反射点都满足同一等光程条件；旋转后得到抛物面。")
add(27, 13, r"""
\fill[DeepBlue!6] (0,0) rectangle (3,2.3);\draw[->] (-.5,0)--(3.5,0) node[right]{$x$};\draw[->] (0,-.3)--(0,2.6) node[above]{$y$};
\draw[DeepBlue,thick,->] (-1,0)--(0,0);\draw[DeepBlue,thick,->] (0,0) arc[start angle=-90,end angle=-25,radius=2];
\draw[dashed] (0,0)--(0,2)--(1.813,1.155);
\node[left] at (0,1){$R$};\node[right] at (2,2){$n=n(y)$};
""", r"题图：初始沿 $+x$ 的光线与题设圆弧，介质位于第一象限。",
    r"圆心位于入射点上方，初始切线沿 $+x$；高度增大时切线逐渐转向竖直，守恒量是 $n\cos\theta=n_0$，其中 $\theta$ 从 $x$ 轴量起。")
add(27, 14, r"""
\fill[gray!15] (0,0) circle (1);\draw[thick] (0,0) circle (1);\draw[DeepBlue,dashed] (0,0) circle (1.6);
\draw[->] (0,0)--(1,0) node[midway,below]{$R$};\draw[<->] (1,0)--(1.6,0) node[midway,below]{$h_0$};
\draw[DeepBlue,->] (1.6,0)--(1.6,.9) node[right]{切向发射};
\node[above] at (0,1.9){$n(h)=n_0-\alpha h$};
""", r"题图：行星表面、候选圆形光线及高度 $h_0$；虚圆只表示题目要求的圆轨道。",
    r"圆形光线的半径是 $r_0=R+h_0$，不等于高度 $h_0$；径向折射率需满足 $\mathrm d(nr)/\mathrm dr=0$，且求得点须位于 $h\ge0,n>0$ 的材料域内。",
    ac=r"解图：在半径 $r_0$ 处把折射率梯度所需的弯曲率与 $1/r_0$ 匹配。")
add(27, 15, ar=r"初始点 $y_0$ 和初始斜率 $\alpha_0$ 分别决定余弦项与正弦项的系数；回复曲率 $y''=-g^2y$ 决定空间周期 $2\pi/g$。",
    ac=r"解图：题设初始高度和斜率用于确定近轴简谐光线的两个积分常数。")

# Imaging: source locations, physical light paths and virtual extensions differ.
add(28, 1, r"""
\fill[DeepBlue!6] (-1,-1.7) rectangle (3.3,0);\draw[thick] (-1,0)--(3.3,0) node[right]{液面};
\draw[very thick] (-.7,.6)--(0,0)--(2,-1.7);\node[above] at (-.7,.6){直杆};
\node at (.6,-.22){$\alpha$};\node[right] at (2,-1.5){液体 $n$};
\draw[->] (2.3,1.3)--(2.3,.4) node[midway,right]{近于正上方观察};
""", r"题图：杆与液面成 $\alpha$，采用近轴视深条件从上方观察。",
    r"真实深度 $h$ 沿法线压缩为 $h/n$，水平投影 $x$ 保持不变；像杆角度因而由两条具有同一水平投影的直角三角形比较得到。")
BALL_Q = r"""
\draw[thick] (0,0) circle (1);\draw[dashed] (-2.5,0)--(3.1,0);
\fill (-2.2,0) circle (1.7pt) node[below]{$O$};\node at (0,.4){$n$};
\draw[->] (0,0)--(0,1) node[midway,right]{$R$};
\draw[DeepBlue,->] (-2.2,0)--(-1,.18);\node[above] at (1.9,.6){球外实像位置待定};
\node[below] at (-1,-.3){第一面};\node[below] at (1,-.3){第二面};
"""
add(28, 2, BALL_Q, r"题图：球外实物、两个折射面及球半径，光线限于近轴窄孔径。",
    r"第二面的物距要从第二面量起，等于 $2R-v_1$；第一面所成的像对第二面可能是虚物，不能把两个面当作互不相干的薄透镜。",
    ac=r"解图：从第一面像距换算第二面物距，再检查最终实像位于球外的参数域。")
add(28, 3, r"""
\draw[->] (-2.5,0)--(3,0);\fill (-.8,0) circle (1.6pt) node[below]{$C_1$};\fill (0,0) circle (1.6pt) node[below]{$C_2$};
\draw[thick] (.59256,-.97508) arc[start angle=-35,end angle=35,radius=1.7];
\draw[thick] (.98298,-.68829) arc[start angle=-35,end angle=35,radius=1.2];
\node[above] at (1.2,1.4){$S_1,\ S_2$，弯月透镜};
\draw[DeepBlue,->] (-.8,0)--(.82481,.5);\node[left] at (-1,.6){物在 $C_1$};
\node[below] at (0,-.7){$C_1C_2=R_2/n$};
""", r"题图：两球心均位于相应球面的左侧，物位于第一球心。示意弧面不代替实际口径域。",
    r"第一面入射沿半径，因而不偏折；第二面出射线的反向延长线在 $Q$ 相交，$Q$ 属于虚像位置，不是光线实际到达的点。")
LENS_OBJECT = r"""
\draw[->] (-3,0)--(3,0);\draw[<->,thick] (0,-1.4)--(0,1.4);\node[above] at (0,1.4){凸透镜 $f$};
\draw[thick] (-1.8,0) circle (.7);\fill (-1.8,0) circle (1.2pt) node[below]{$a$};
\draw[->] (-3,.8)--(-3,1.4) node[above]{$y$};\node[above] at (-1.8,.8){物圆 $R$};
"""
add(28, 4, LENS_OBJECT, r"题图：物图形处于包含光轴的平面，圆心在轴上；每个物点分别满足近轴成像关系。",
    r"物图形具有不同的轴向坐标 $x$，各点的横向倍率 $-f/(x-f)$ 也不同；不能用一个共同倍率直接缩放整条圆或整条抛物线。",
    ac=r"解图：对物图形上的每一点分别应用透镜映射，再消去物坐标检验像的曲线类型。")
add(28, 5, r"""
\draw[->] (-2,0)--(4,0);\draw[<->,thick] (0,-1)--(0,1) node[above]{$f$};\draw[very thick] (3,-1)--(3,1) node[above]{平面镜};
\fill (-1.4,0) circle (1.7pt) node[below]{光源};\draw[<->] (0,-.6)--(3,-.6) node[midway,below]{$L$};
\draw[DeepBlue,->] (-1.4,0)--(-.2,.5);
""", r"题图：透镜、轴上点光源与垂直光轴的平面镜，光需往返通过透镜。",
    r"往返两次通过透镜的间隔由到镜面再返回的实际传播距离确定；要求出射回到原光源，等价于往返系统的相应传输矩阵元为零。")
add(28, 6, r"""
\draw[->] (-2,0)--(4.5,0);\draw[>-<,thick] (0,-1)--(0,1);\draw[<->,thick] (2,-1)--(2,1);
\node[above] at (0,1){$f_1=-1.0\,\mathrm{cm}$};\node[above] at (2,1.6){$f_2=3.5\,\mathrm{cm}$};
\draw[<->] (0,-.7)--(2,-.7) node[midway,below]{$2.1\,\mathrm{cm}$};
\node[below] at (-1.4,-1.2){室外};\node[below] at (3.4,-1.2){室内};
""", r"题图：猫眼的室外负透镜与室内正透镜，标明实际观察方向。",
    r"两侧观察时光线先遇到的透镜不同；逐面计算时必须交换先后次序，且最后还要检查眼睛是否能接收到出射光束。")
add(28, 7, r"""
\draw[->] (-3,0)--(1.4,0);\draw[<->,thick] (0,-1.1)--(0,1.1);\draw[very thick] (.2,-1.1)--(.2,1.1);
\draw[DeepBlue,->,thick] (-2,0)--(-2,.8) node[above]{$H$};
\draw[<->] (-2,-.5)--(0,-.5) node[midway,below]{$2f$};\node[right] at (.4,.5){平面镀银};
""", r"题图：物在凸面一侧，透镜平面镀银，反射光再次通过同一透镜。",
    r"透镜折射作用发生两次，镀银面的反射使光返回物侧；虚像延长线和实际返程光必须用不同线型区分。")
add(28, 8, r"""
\draw[thick] (0,1.1)--(0,-1.1)--(2.2,1.1)--cycle;\node at (.6,.4){$n=1.5$};
\draw[DeepBlue,->] (.5,2.2)--(.5,1.4);\node[above] at (.5,2.2){物 $AB$};
\draw[<->,thick] (3.8,-1)--(3.8,1);\draw[>-<,thick] (5.5,-1)--(5.5,1);
\node[above] at (3.8,1){$f_1=10$};\node[above] at (5.5,1.6){$f_2=-10$};
\node[below] at (3.1,-1.4){棱镜右侧 $10\,\mathrm{cm}$};\node[below] at (5.1,-1.9){两镜相距 $15\,\mathrm{cm}$};
""", r"题图：物、全反射棱镜及后续两透镜；长度的数值单位均为厘米，图不按比例。",
    r"先展开棱镜内的反射光路并按折射率换算视距离，再把前一元件的像转换成后一元件的物；每个距离须从该元件自己的参考面量起。")
MICROSCOPE = r"""
\draw[->] (-1,0)--(6,0);\draw[<->,thick] (0,-1)--(0,1) node[above]{物镜};\draw[<->,thick] (4,-1)--(4,1) node[above]{目镜};
\draw[DeepBlue,->] (-.7,0)--(-.7,.55) node[above]{标本};\draw[dashed] (3,-.8)--(3,.8) node[above]{中间像};
\draw[<->] (0,-1.3)--(4,-1.3) node[midway,below]{$\ell$ 固定};
\draw[<->] (3,-.4)--(4,-.4) node[midway,below]{$u_e$};\node[right] at (5,.4){眼};
"""
add(28, 9, MICROSCOPE, r"题图：两透镜的固定间距、中间像及目镜物距 $u_e$；横向展开表示竖直镜筒。",
    r"两镜距离 $\ell$ 固定，故 $u_e=\ell-v_o$；镜筒朝标本移动使物镜物距减小，进而使中间像距 $v_o$ 增大、$u_e$ 减小。",
    ac=r"解图：用中间像位置而非目镜单独移动来判断调焦方向。")
TELESCOPE = r"""
\draw[->] (-2,0)--(4.8,0);\draw[<->,thick] (0,-1.2)--(0,1.2);\draw[<->,thick] (3.2,-.7)--(3.2,.7);
\foreach \y in {-.6,.6}{\draw[DeepBlue,->] (-1.8,\y)--(0,\y);\draw[DeepBlue,->] (0,\y)--(2,0);}
\node[above] at (0,1.2){物镜 $D,f_o$};\node[above] at (3.2,.9){目镜 $f_e$};
\draw[dashed] (2,-.8)--(2,.8) node[below]{中间焦面};
"""
add(28, 10, r"""
\draw[thick] (1,-1.3)--(1,1.3) node[above]{口径 $D$};
\draw[DeepBlue,->] (-1.5,.9)--(1,.3);\draw[DeepBlue,->] (-1.5,-.9)--(1,-.3);
\draw[dashed] (-1.5,0)--(2.5,0);\node[above] at (-.7,.2){$0.50''$};
\node[right] at (2,.7){$\lambda=550\,\mathrm{nm}$};
""", r"题图：两颗星的不同入射方向与同一圆形口径；角距远小于示意图。",
    r"两束光的入射角差对应两艾里斑中心的角距；瑞利边界把其中一斑中心放在另一斑的第一暗环上，因而需 $1.22\lambda/D\le0.50''$。",
    ac=r"解图：把天体角距与口径产生的第一衍射暗环角半径比较。")
add(28, 11, TELESCOPE, r"题图：双正透镜的天文望远镜具有可放置附件的实中间焦面。",
    r"实中间焦面位于物镜焦点附近，可以安放十字丝或探测器；物镜有效口径 $D$ 决定集光与衍射分辨，目镜主要改变角放大率。",
    ac=r"解图：将中间成像、目镜放大与物镜口径分别对应到实际位置。")

# Interference: every relevant source, optical path and overlap boundary is shown.
PLANE_WAVES = r"""
\draw[thick] (3,-1.6)--(3,1.6) node[above]{屏};\draw[dashed,->] (0,0)--(4,0) node[right]{法线 $x$};
\draw[DeepBlue,thick,->] (0,-1.2)--(3,0);\draw[DeepBlue,thick,->] (0,1)--(3,0);
\node at (1.8,-.25){$\alpha$};\node at (1.7,.25){$\beta$};\draw[->] (3.6,.2)--(3.6,1.2) node[right]{$y$};
"""
add(29, 1, PLANE_WAVES, r"题图：两束等波长平面波位于屏法线的两侧，沿屏的正方向取 $+y$。",
    r"下方入射波的波矢沿屏投影为 $+k\sin\alpha$，上方入射波的投影为 $-k\sin\beta$；相位差的屏面梯度因此是两者之差。",
    ac=r"解图：条纹间距取决于波矢差沿屏面的投影。")
YOUNG = r"""
\fill (-2,0) circle (1.7pt) node[left]{$S$};\draw[thick] (0,-1.3)--(0,-.45) (0,-.3)--(0,.3) (0,.45)--(0,1.3);
\fill (0,.375) circle (1.5pt) node[right]{$S_1$};\fill (0,-.375) circle (1.5pt) node[right]{$S_2$};
\draw[DeepBlue,->] (-2,0)--(0,.375);\draw[DeepBlue,->] (-2,0)--(0,-.375);
\draw[thick] (4,-1.3)--(4,1.3) node[above]{屏};\draw[dashed] (-2,0)--(4,0);
\draw[<->] (0,-1.6)--(4,-1.6) node[midway,below]{$L$};\draw[<->] (-.4,-.375)--(-.4,.375) node[midway,left]{$d$};
"""
add(29, 2, YOUNG+r"\draw[->] (-2,.15)--(-2,.9) node[above]{$\delta s$};",
    r"题图：点光源沿双缝连线方向上移，两缝位置与屏距保持不变。",
    r"光源上移使到上缝的路程缩短，初始光程差改变；屏上须向相反方向移动才能补偿这项差值，而两缝间距并未改变。")
add(29, 3, YOUNG.replace("{$S$}", "{白光源 $S$}"),
    r"题图：宽光谱通过同一对双缝，各波长具有相同的几何光程差。",
    r"$d,L$ 对各色相同，而条纹间距正比于波长；零光程差处各色明纹重合，离中心后不同波长的级次逐渐错开并互相冲淡。",
    ac=r"解图：用同一双缝几何比较各波长的相位差及条纹尺度。")
add(29, 4, r"""
\draw[very thick] (0,0)--(2,0);\node[below] at (1,0){有限镜长 $l$};
\fill (-1,.55) circle (1.7pt) node[above]{$S$};\draw[thick] (5,-.1)--(5,2) node[above]{屏};
\draw[<->] (-1,.15)--(0,.15) node[midway,above]{$b$};\draw[<->] (-1,-.7)--(5,-.7) node[midway,below]{$L$};
\draw[<->] (-1.5,0)--(-1.5,.55) node[midway,left]{$d$};
""", r"题图：光源高于镜面 $d$，镜面只有从距光源水平位置 $b$ 到 $b+l$ 的有限长度。",
    r"两条边界反射线分别经过镜的左右端点，只有它们在屏上夹出的区间能同时收到直射与反射光；反射相位须另加 $\pi$。")
add(29, 5, r"""
\fill (-2,0) circle (1.7pt) node[left]{$S$};\draw[thick] (0,-1.3)--(.2,0)--(0,1.3)--(-.2,0)--cycle;
\node[above] at (0,1.3){双棱镜 $n,\alpha$};\draw[thick] (4,-1.3)--(4,1.3) node[above]{屏};
\draw[dashed] (-2,0)--(4,0);\draw[<->] (-2,-1.7)--(0,-1.7) node[midway,below]{$L_1$};\draw[<->] (0,-1.7)--(4,-1.7) node[midway,below]{$L_2$};
\draw[gray] (.7,.2) rectangle (.85,1);\node[right] at (.85,.8){可加肥皂膜 $n'$};
""", r"题图：双棱镜的上下两半由同一缝光源照明，一半光路可插入薄膜。",
    r"两个虚光源的间距由两半棱镜的小角偏折确定；插膜只在一束中增加 $(n'-1)t$ 光程，零级亮纹要向增加光程的一侧移动。")
DOUBLE_MIRROR_Q = r"""
\draw[thick] (0,0)--(2,-2.2) (0,0)--(2.2,-2);
\fill (0,0) circle (1.5pt) node[left]{$O$};\fill (0,1.2) circle (1.7pt) node[above]{$S$};
\draw[dashed] (0,0)--(0,1.2) node[midway,left]{$R$};\draw[thick] (4,-1.6)--(4,1.6) node[above]{$x=L$};
\draw[dashed,->] (-.5,0)--(4.6,0) node[right]{$x$};\node[right] at (.65,-.65){小夹角 $\alpha$};
"""
add(29, 6, DOUBLE_MIRROR_Q, r"题图：双镜方向接近 $-45^\circ$，分别偏转 $\mp\alpha/2$；图中小夹角作了夸大。",
    r"两面镜反射所得的虚光源到交线距离均为 $R$，公共照明区还受两实际反射半平面的限制；条纹数须在该重叠区内计数。",
    a_macro="DoubleMirrorDiagram", ac=r"解图：用两个虚光源及有限公共照明区确定间距和条纹数。")
add(29, 7, r"""
\fill (-2,0) circle (1.7pt) node[left]{$S$};\draw[<->,thick] (0,.35)--(0,1.5);\draw[<->,thick] (0,-1.5)--(0,-.35);
\draw[<->] (.4,-.35)--(.4,.35) node[midway,right]{$\delta$};\draw[thick] (4,-1.4)--(4,1.4) node[above]{屏};
\draw[dashed] (-2,0)--(4,0);\node[above] at (-1,1.1){$l_1>f$};\node[below] at (2,-1.6){屏距 $L>l_2$，公共区全宽 $D$};
""", r"题图：透镜沿直径分开并横向对称移开，两半的焦距相同。",
    r"两半透镜各成一个实像，这两个像才是屏前的相干次级光源；亮纹中心落在公共区端点时是否计入，取决于题目指定的计数规则。")
add(29, 8, r"""
\fill (-2,0) circle (1.7pt) node[left]{$S$};\draw[<->,thick] (0,.15)--(0,1.3);\draw[<->,thick] (1,-1.3)--(1,-.15);
\draw[dashed] (-2,0)--(5,0);\draw[thick] (4,-1.4)--(4,1.4) node[above]{观察屏};
\draw[<->] (0,-1.7)--(1,-1.7) node[midway,below]{轴向错开 $8\,\mathrm{cm}$};\node[above] at (1,1.6){两半焦距相同};
""", r"题图：两半透镜沿光轴错开，两个共轭像点的轴向位置不同；屏位于题设两像的中点。",
    r"两个等效点源在同一轴线上，光程差只依赖屏面半径，因而形成圆环；若屏夹在两焦点之间，必须同时跟踪会聚与发散波的相位。")
add(29, 9, DOUBLE_MIRROR_Q.replace(r"\fill (0,1.2) circle (1.7pt) node[above]{$S$};", r"\draw[very thick] (-.45,1.2)--(.45,1.2);\node[above] at (0,1.2){均匀非相干线源，全宽 $w$};"),
    r"题图：线源沿 $x$ 方向展开，每个源点分别产生一套条纹，不同源点之间不相干。",
    r"源宽沿 $x$ 方向，不是沿虚光源的间距方向；应先求每个源点造成的条纹相位平移，再叠加强度并取可见度。")
FILM = r"""
\draw[thick] (-1,0)--(4,0);\draw[thick] (-1,-.35)--(4,-.65);\node[right] at (4,-.35){油膜 $n$};
\draw[DeepBlue,->] (-.8,1.4)--(.5,0);\draw[DeepBlue,->] (.5,0)--(1.8,1.4);
\draw[DeepBlue,->] (.5,0)--(.85,-.46)--(1.3,0)--(2.7,1.4);
\draw[<->] (3,0)--(3,-.59) node[midway,left]{$t(x)$};\node[above] at (2.5,1.6){两界面反射光};
"""
add(29, 10, FILM, r"题图：油膜两个界面的反射光，膜厚随位置变化。",
    r"两束反射光的几何光程差含 $2nt\cos r$，还要加入两界面的反射相位差；不同位置的 $t$ 选择不同增强波长，故出现彩色。",
    ac=r"解图：在同一出射方向比较上、下两界面的反射光。")
add(29, 11, r"""
\draw[thick] (0,2.2)--(0,-.4);\draw[thick] (.1,2.2)--(.65,-.4);\node[right] at (.7,1.1){竖直液膜};
\draw[->] (2,1.9)--(2,.7) node[midway,right]{$\boldsymbol g$};
\draw[DeepBlue,->] (-1,1.8)--(0,1.4);\draw[DeepBlue,->] (-1,.3)--(0,0);
\node[left] at (-.2,2.35){顶端逐渐变薄};\node[below] at (.3,-.6){空气/液体/空气};
""", r"题图：液体在重力下排向下方，膜顶更薄；图中为两侧空气的自由液膜。",
    r"同一高度的膜厚随排液而减小，使增强波长依次变化；极薄时两反射光之间的半波损失主导，低级反射趋于相消而发黑。",
    ac=r"解图：厚度随高度和时间改变，局部两界面反射决定颜色。")
add(29, 12, r"""
\fill[DeepBlue!7] (0,0)--(0,2.3)--(1.5,2.3)--cycle;\draw[thick] (0,0)--(0,2.3)--(1.5,2.3)--cycle;
\draw[->] (-1,0)--(3.2,0) node[right]{$x$};\draw[->] (-.5,-.2)--(-.5,2.7) node[above]{$y$};
\foreach \y in {.5,1,1.5,2}{\pgfmathsetmacro{\xx}{1.5*\y/2.3}\draw[DeepBlue,->] (-1,\y)--(\xx,\y);\draw[thick] (\xx,\y-.08)--(\xx,\y+.08);}
\draw[<->] (0,2.55)--(1.5,2.55) node[midway,above]{$h$};\node[right] at (1.6,1.5){挡板各狭缝};
\node[right] at (1.7,.6){$x_y=y\tan\theta$};
""", r"题图：各高度光线经历的厚度 $x_y$ 不同，挡板缝的坐标沿 $y$ 量取；微台阶界面按题设处理。",
    r"横向坐标 $y$ 决定介质厚度 $x_y$，而附加光程应对沿传播方向的 $n(x)-1$ 积分；不能把整个厚度直接乘出口折射率。")
NEWTON = r"""
\draw[thick] (-2,0)--(2,0);\draw[thick,domain=-1.8:1.8,smooth] plot (\x,{.18*\x*\x});\draw[thick] (-1.8,.9)--(1.8,.9);
\fill (0,0) circle (1.5pt) node[below]{$O$ 接触点};\node[right] at (1.5,.3){空气膜};
\draw[DeepBlue,->] (-1.4,1.6)--(-.8,.3);\draw[<->] (1.1,0)--(1.1,.218) node[right]{$t(r)$};
\draw[<->] (0,-.6)--(1.1,-.6) node[midway,below]{$r$};
"""
add(29, 13, NEWTON, r"题图：凸面与底板之间的空气膜及接触中心；底板的反射相位仍需按题设材料确定。",
    r"空气膜厚度近轴为 $r^2/(2R)$，所以等光程差线为同心圆；透明玻璃底板产生一次半波损失，中心为暗，金属镀层须另行指定相位。",
    a_macro="NewtonRingsDiagram", ac=r"解图：由接触几何确定膜厚，再连同反射相位判断明暗级次。")
MICHELSON = r"""
\draw[thick] (-.35,-.35)--(.35,.35);\draw[very thick] (3,-.7)--(3,.7);\draw[very thick] (-.7,2)--(.7,2);
\draw[DeepBlue,->] (-2,0)--(0,0);\draw[DeepBlue,->] (0,0)--(2.8,0);\draw[DeepBlue,->] (0,0)--(0,1.8);\draw[->] (0,0)--(0,-1.1);
\node[below] at (-1.5,0){光源};\node[right] at (0,-1){探测窗};\draw[->] (3.2,1)--(4.2,1) node[right]{$v$};
\node[above] at (3,.7){动镜};\node[above] at (0,2){定镜};
"""
add(29, 14, MICHELSON, r"题图：迈克耳孙两臂，动镜沿一臂传播方向匀速移动。",
    r"动镜单程位移 $\Delta x$ 在往返光路中改变 $2\Delta x$，因此单色条纹频率为 $2v/\lambda$；两相近波长的拍频是各自条纹频率之差。",
    ac=r"解图：动镜所在光臂的往返光程变化包含两次镜位移。")

# Diffraction, polarization and crystal optics.
SLIT = r"""
\draw[thick] (0,-1.5)--(0,-.4) (0,.4)--(0,1.5);\draw[<->] (.35,-.4)--(.35,.4) node[midway,right]{$a$};
\draw[DeepBlue,->] (-2,0)--(-.2,0) node[midway,above]{$\lambda$};\draw[thick] (4,-1.5)--(4,1.5) node[above]{屏};
\draw[dashed] (0,0)--(4,0);\draw[<->] (0,-1.8)--(4,-1.8) node[midway,below]{$L$};
"""
add(30, 1, SLIT, r"题图：可调缝宽 $a$ 与固定屏距 $L$；更换颜色和缝宽时分别代入。",
    r"中央亮斑边界由两侧第一暗纹决定，角半宽为 $\lambda/a$；比较的是每一种配置的波长与缝宽之比。",
    ac=r"解图：单缝两侧第一暗纹的间隔为 $2L\lambda/a$。")
add(30, 2, r"""
\draw[thick] (0,-1)--(0,1);\fill (0,.25) circle (2pt);\fill (0,-.25) circle (2pt);
\draw[DeepBlue] (0,.25)--(3,0)--(0,-.25);\draw[<->] (-.4,-.25)--(-.4,.25) node[midway,left]{$p$};
\draw[<->] (0,-1.3)--(3,-1.3) node[midway,below]{$L=10\,\mathrm{cm}$};\node[right] at (3,0){眼};
""", r"题图：相邻像素中心间距 $p$ 与观看距离 $L$ 决定张角。",
    r"眼处两条视线的夹角近似为 $p/L$；将给定角分辨率先化为弧度，才可把得到的 $p$ 换算成每英寸像素数。",
    ac=r"解图：像素中心的视角与眼的角分辨率直接比较。")
STAR = r"""
\foreach \a in {0,60,120,180,240,300}{\draw[DeepBlue,thick] (0,0)--(\a:1.25);}
\fill (0,0) circle (2pt);\node[below] at (0,-1.5){观测到的六向星芒};
\draw[dashed] (3,0) circle (.8);\node[below,align=center] at (3,-1.2){孔径或支撑结构\\形状待判别};
"""
add(30, 3, STAR, r"题图：观测现象是六个亮芒方向；仅凭该图样不能预先指定光阑边数。",
    r"每组平行直边给出一对法向衍射方向；六边形的三组对边与三角形的三条边都可能给出六向星芒，所以反推结构并不唯一。",
    a=r"""
\draw[thick] (0:1)--(60:1)--(120:1)--(180:1)--(240:1)--(300:1)--cycle;
\begin{scope}[xshift=3.4cm]\draw[thick] (90:1)--(210:1)--(330:1)--cycle;\end{scope}
\foreach \a in {30,90,150,210,270,330}{\draw[DeepBlue,->] (0,0)--(\a:1.45);\draw[DeepBlue,->] (3.4,0)--++(\a:1.45);}
\node[below] at (0,-1.8){六边形的三组对边};\node[below] at (3.4,-1.8){三角形的三条边};
""", ac=r"解图：两种孔径均能给出三组相反方向的直边衍射，星芒数不足以唯一反演孔径。")
PINHOLE = r"""
\draw[thick] (0,-1.2)--(0,-.2) (0,.2)--(0,1.2);\node[above] at (0,1.2){手指小缝};
\draw[<->,thick] (2,-1)--(2,1);\draw[thick] (4,-1.2)--(4,1.2) node[above]{视网膜};
\draw[DeepBlue,->] (-1.5,.12)--(2,.12);\draw[DeepBlue] (2,.12)--(4,-.08);
\draw[DeepBlue,->] (-1.5,-.12)--(2,-.12);\draw[DeepBlue] (2,-.12)--(4,.08);
\draw[dashed] (.2,.8)--(2,.8)--(4,-.5) (.2,-.8)--(2,-.8)--(4,.5);
"""
add(30, 4, PINHOLE, r"题图：小缝挡去部分边缘光线，虚线表示被挡掉的边缘光在屈光不正时的假想传播。",
    r"实线仅保留窄范围入瞳位置，几何弥散圈因而变小；继续减小缝宽会增加 $\lambda/D$ 的衍射角，故清晰度存在折中。",
    ac=r"解图：对照保留的近轴光和被挡去的边缘光，区分几何模糊与衍射模糊。")
add(30, 5, r"""
\draw[thick] (0,-.7)--(0,.7);\draw[DeepBlue,->] (-1,0)--(.5,0);\node[above] at (0,.7){出光口 $D$};
\draw[dashed] (.5,0)--(4.5,0);\draw[thick] (4.5,0) circle (.75);\node[above] at (4.5,.75){月球};
\draw[<->] (0,-1)--(4.5,-1) node[midway,below]{$L=3.84\times10^8\,\mathrm m$};
""", r"题图：给定激光出光口径与地月距离，远处束斑大小待求；图不按比例。",
    r"第一暗环半径属于垂直光轴的假想平面，不能直接等同于弯曲月面的面积；须另与月球投影半径比较。")
CCD = r"""
\draw[<->,thick] (0,-1.2)--(0,1.2);\draw[thick] (3,-1.2) rectangle (3.4,1.2);
\foreach \y in {-1,-.6,-.2,.2,.6,1}{\draw (3,\y)--(3.4,\y);}
\draw[DeepBlue,->] (-1.5,.7)--(0,.7);\draw[DeepBlue] (0,.7)--(3,0);\draw[DeepBlue,->] (-1.5,-.7)--(0,-.7);\draw[DeepBlue] (0,-.7)--(3,0);
\draw[<->] (0,-1.6)--(3,-1.6) node[midway,below]{$f$};\node[above] at (0,1.2){口径 $D$};\node[right] at (3.5,.7){CCD像素};
"""
add(30, 6, CCD, r"题图：有限口径镜头在CCD焦平面成像；光圈数为 $f/D$。",
    r"焦平面衍射尺度由角尺度再乘焦距 $f$ 得到；CCD像素间距由感光面边长除以每边像素数求出，不能把总像素数直接当作每边像素数。",
    ac=r"解图：把角衍射尺度转换为焦平面线尺度后，再与像素采样间距比较。")
add(30, 7, r"""
\foreach \x/\y in {0/0,.25/.12,.48/-.05,.72/.1}{\fill[DeepBlue] (\x,\y) circle (2pt);}
\node[below] at (.35,-.6){分子局部结构};\draw[<->,thick] (2,-1)--(2,1) node[above]{有限NA物镜};
\draw[->] (1,0)--(1.8,0);\node[right] at (2.7,.6){可见光 $\lambda$};
""", r"题图：分子尺度结构通过有限数值孔径的普通远场物镜成像。",
    r"相邻分子态的间距远小于 $0.61\lambda/\mathrm{NA}$，各点产生的扩散斑强烈重叠；提高后续倍率不会增加物镜已截止的空间频率。",
    a=r"""
\draw[DeepBlue!55,thick] (-.25,0) circle (.9);\draw[DeepBlue!55,thick] (.25,0) circle (.9);
\fill (-.25,0) circle (1.6pt);\fill (.25,0) circle (1.6pt);\draw[<->] (-.25,-1.2)--(.25,-1.2) node[midway,below]{数纳米};
\node[right,align=left] at (1.5,0){扩散斑约 $200\,\mathrm{nm}$\\图示中心间距已夸大};
""", ac=r"解图：两个分子位置的普通光学点扩散斑重叠，几何放大不能分开已丢失的细节。")
add(30, 8, r"""
\draw[thick] (0,0) circle (.65);\node[below] at (0,-.85){地球上尺度 $s$};
\draw[<->,thick] (5,-.9)--(5,.9) node[above]{望远镜口径 $D$};
\draw[DeepBlue,->] (.7,.12)--(4.8,.02);\draw[DeepBlue,->] (.7,-.12)--(4.8,-.02);
\draw[<->] (.7,-1.4)--(5,-1.4) node[midway,below]{$L\ge10^8\,\mathrm{ly}$};
""", r"题图：目标的物理尺度 $s$、传播距离 $L$ 和接收口径 $D$；距离同时决定光行时。",
    r"目标在望远镜处只张角 $s/L$，该角必须大于口径的衍射角；收到哪一时代的光则由 $L/c$ 单独决定，不由口径决定。",
    ac=r"解图：角分辨率与光行时是两个独立的约束，分别使用 $s/L$ 与 $L/c$。")
GRID = r"""
\foreach \x in {0,.3,.6,.9}{\draw (\x,-.6)--(\x,.6);}\foreach \y in {-.6,-.3,0,.3,.6}{\draw (0,\y)--(.9,\y);}
\node[below] at (.45,-.85){正交织物间距 $a$};
\foreach \x in {3.3,3.9,4.5}{\foreach \y in {-.6,0,.6}{\fill[DeepBlue] (\x,\y) circle (2pt);}}
\draw[<->] (3.3,1)--(3.9,1) node[midway,above]{$\Delta x$};\node[below] at (3.9,-.85){观察到的方形亮点阵};
"""
add(30, 9, GRID, r"题图：织物的两组正交周期与观察到的最近邻亮斑距离。",
    r"两组正交纤维分别产生两个正交衍射方向；最近邻亮点对应一级空间频率，故 $a\sin\theta=\lambda$、$\tan\theta=\Delta x/L$。",
    ac=r"解图：把亮点阵的一个坐标方向化成一维光栅，再由屏面位移反求周期。")
GRATING = r"""
\draw[thick] (0,-.4)--(0,1.4);\fill (0,0) circle (2pt) node[right]{$A$};\fill (0,1) circle (2pt) node[right]{$B$};
\draw[DeepBlue,->] (-2,-1)--(0,0);\draw[DeepBlue,->] (-2,0)--(0,1);
\draw[DeepBlue,->] (0,0)--(2,1.3);\draw[DeepBlue,->] (0,1)--(2,2.3);
\draw[dashed,->] (-.5,0)--(2.6,0) node[right]{法线};\draw[<->] (-.4,0)--(-.4,1) node[midway,left]{$a$};
\node at (-1,-.2){$\theta_i$};\node at (1,.3){$\theta_m$};
"""
add(30, 10, GRATING, r"题图：相邻缝 $A,B$ 和入、出射波矢；两个角相对同一正法线取有向值。",
    r"两相邻缝在入射波中已有相位差 $ka\sin\theta_i$，出射远场又引入 $ka\sin\theta_m$；相减后等于 $2\pi m$，才得到有向角光栅方程。",
    ac=r"解图：同时保留入射与出射的波矢投影，避免漏掉入射的原有相位差。")
POLARIZERS = r"""
\foreach \x/\a/\lab in {0/0/0,2/45/45,4/90/90}{\draw[thick] (\x,0) circle (.55);\draw[DeepBlue,thick] (\x,0)++(\a:.5)--++(\a+180:1);\node[above] at (\x,.7){$\lab^\circ$};}
\draw[->] (-1.6,0)--(-.65,0) node[midway,above]{$I_0$};\draw[->] (.65,0)--(1.35,0);\draw[->] (2.65,0)--(3.35,0);\draw[->] (4.65,0)--(5.3,0);
"""
add(30, 11, POLARIZERS, r"题图：自然光依次通过三片偏振片，各圆以正视图表示该片的透光轴。",
    r"第一片把自然光强度减半，后两片各有 $45^\circ$ 的相对轴夹角；应用马吕斯定律时用相邻两片夹角，不能直接用最后一片相对第一片的 $90^\circ$。",
    ac=r"解图：逐片跟踪偏振方向，两个 $\cos^245^\circ$ 分别对应后两片。")
WAVEPLATE = r"""
\draw[->] (-.4,0)--(2,0) node[right]{快轴 $x$};\draw[->] (0,-.4)--(0,2) node[above]{慢轴 $y$};
\draw[DeepBlue,thick,->] (0,0)--(1.3,1.3) node[above right]{$\boldsymbol E_{\rm in}$};
\draw[dashed] (1.3,0)--(1.3,1.3)--(0,1.3);\node at (.7,.28){$45^\circ$};
"""
add(30, 12, WAVEPLATE, r"题图：入射线偏振与波片快、慢轴成 $45^\circ$，因此两本征分量等幅。",
    r"沿快、慢轴的两分量等幅；加入 $\pi/2$ 相位延迟后，在固定空间点消去时间即得圆，而改变幅值比或延迟会给出一般椭圆。",
    a=r"""
\draw[->] (-1.5,0)--(1.7,0) node[right]{$E_x$};\draw[->] (0,-1.5)--(0,1.7) node[above]{$E_y$};
\draw[DeepBlue,thick] (0,0) circle (1.1);\draw[DeepBlue,->] (1.1,0) arc[start angle=0,end angle=55,radius=1.1];
\node[right,align=left] at (2,0){$E_x=A\cos\omega t$\\$E_y=A\sin\omega t$\\图示一种时间相位约定};
""", ac=r"解图：等幅且正交相位的两个分量在 $E_x,E_y$ 平面上扫过圆。")
add(30, 13, r"""
\fill[DeepBlue!7] (0,-1) rectangle (2.4,1);\draw[thick] (0,-1) rectangle (2.4,1);
\draw[DeepBlue,->] (-1,.4)--(3.3,.4) node[right]{$E_f,n_f$};\draw[DeepBlue,->] (-1,-.4)--(3.3,-.4) node[right]{$E_s,n_s$};
\draw[<->] (0,-1.3)--(2.4,-1.3) node[midway,below]{$d$};\node[above] at (1.2,1.2){$\lambda_0=600\,\mathrm{nm}$};
""", r"题图：两本征分量经过相同几何厚度 $d$，光程差由折射率差产生。",
    r"几何长度相同而光程相差 $(n_s-n_f)d$；最薄四分之一波片取延迟 $\pi/2$，五倍厚度给 $5\pi/2$，模 $2\pi$ 后仍等效于四分之一波片。",
    ac=r"解图：以同厚度的两条本征光路求相位差，区分零级厚度与模 $2\pi$ 的等效延迟。")
add(30, 14, r"""
\draw[->] (-.4,0)--(2,0) node[right]{快轴 $x$};\draw[->] (0,-.4)--(0,1.6) node[above]{慢轴 $y$};
\draw[DeepBlue,thick,->] (0,0)--(1.5,.546) node[above right]{$\boldsymbol E_{\rm in}$};
\draw[dashed] (1.5,0)--(1.5,.546)--(0,.546);\node at (.8,.13){$\alpha=20^\circ$};
""",
    r"题图：入射偏振与半波片快轴成 $\alpha$，检偏器的方向待定。",
    r"半波延迟使一个本征分量变号，等效于把线偏振方向关于快轴反射；入射 $+\alpha$ 变为 $-\alpha$，两方向相差 $2\alpha$。",
    a=r"""
\draw[->] (-.5,0)--(2.3,0) node[right]{快轴};
\draw[DeepBlue,thick,->] (0,0)--(1.6,.582) node[right]{入射 $+20^\circ$};
\draw[DeepBlue,thick,->] (0,0)--(1.6,-.582) node[right]{出射 $-20^\circ$};
\draw[dashed] (-.4,.146)--(1.9,-.691);\node[below] at (1,-1){最大透射时检偏轴沿出射偏振};
""", ac=r"解图：半波片使偏振方向关于快轴对称；检偏轴应随出射方向选择。")
add(30, 15, r"""
\draw[->] (-.8,0)--(1.3,0) node[right]{$x$};\draw[->] (0,-.8)--(0,1.3) node[above]{$y$};
\draw[DeepBlue,thick] (0,0)--(35:1);\node[right] at (.6,.25){检偏轴 $\theta$};
\node[below,align=left] at (.4,-1.2){$I_x=1.5I_0,\ I_y=I_0$\\可在前方加入本征轴沿 $x,y$ 的四分之一波片};
""", r"题图：检偏器横截面与两个已测正交方向；入射光允许含非偏振成分。",
    r"直接旋转检偏轴只测两个线偏振分量及其相关项；四分之一波片把原来的正交相位相关变为可由旋转检偏器测出的强度变化。")
add(30, 16, r"""
\draw[->] (0,-.3)--(0,2) node[above]{光轴};\draw[DeepBlue,->,thick] (0,0)--(1.4,1.4) node[right]{$\boldsymbol k$};
\node at (.3,.85){$45^\circ$};\node[right,align=left] at (2,0){$n_o=1.66$\\$n_e=1.49$};
""", r"题图：角度从晶体光轴量到波矢，题目求的是相位折射率。",
    r"$45^\circ$ 是波矢与光轴的夹角；代入折射率椭球截面的方向关系后，所得有效折射率必须在 $n_e$ 与 $n_o$ 之间，且不能把能流走离角代入同一个公式。",
    ac=r"解图：明确波矢角度的参考轴，再检验折射率的上下界。")
WALKOFF = r"""
\fill[DeepBlue!7] (0,-.5) rectangle (3,1.5);\draw[thick] (0,-.5)--(0,1.5) (3,-.5)--(3,1.5);
\draw[DeepBlue,->] (0,0)--(3,0) node[right]{o光};\draw[DeepBlue,->] (0,0)--(3,1) node[right]{e光能流};
\draw[<->] (0,-.9)--(3,-.9) node[midway,below]{$d$};\draw[<->] (3.6,0)--(3.6,1) node[midway,right]{$\Delta y$};\node at (1,.16){$\rho$};
"""
add(30, 17, WALKOFF, r"题图：两束从同一点进入晶片，e光能流相对法线走离，图中 $\Delta y$ 待求。",
    r"$d$ 沿法线量取，而 $\Delta y$ 沿出射面量取，二者形成直角三角形；因此使用 $\tan\rho$，不能用光程长度误代 $d$。",
    ac=r"解图：厚度与横移是走离角所对应的邻边和对边。")

# Relativity: events, frames and simultaneous lengths stay explicit.
CLOCK_Q = r"""
\draw[very thick] (-.8,0)--(.8,0) (-.8,1.8)--(.8,1.8);
\draw[DeepBlue,->] (0,0)--(0,1.7);\draw[DeepBlue,->] (.2,1.8)--(.2,.1);
\draw[<->] (-1.1,0)--(-1.1,1.8) node[midway,left]{$L$};
\draw[->] (1.3,.9)--(3,.9) node[midway,above]{$v=0.80c$};\node[below] at (0,-.35){光钟自身的两面镜};
"""
add(31, 1, CLOCK_Q, r"题图：两镜间距沿垂直运动方向量取，整只光钟相对实验室横向运动。",
    r"实验室半周期 $\Delta t$ 内，光程为三角形斜边 $c\Delta t$，镜面横移为 $v\Delta t$；两镜的横向间距 $L$ 不受纵向尺缩影响。",
    a=r"""
\draw[thick] (0,0)--(2,1.6)--(4,0);\draw[dashed] (0,0)--(4,0);
\fill (0,0) circle (1.5pt) node[below]{$A$};\fill (2,1.6) circle (1.5pt) node[above]{$B$};\fill (4,0) circle (1.5pt) node[below]{$C$};
\draw[<->] (0,-.6)--(2,-.6) node[midway,below]{$v\Delta t$};\draw[<->] (2.4,0)--(2.4,1.6) node[midway,right]{$L$};
\node[above left] at (1,.8){$c\Delta t$};\node[above] at (3.6,1.6){$\Delta t=T/2$};
""", ac=r"解图：实验室中光的往返路径。$A,B,C$ 属于不同时间的三个事件。")
add(31, 2, r"""
\draw[->] (-.5,0)--(5,0) node[right]{$x$};\fill (0,0) circle (1.8pt) node[below]{产生事件};
\draw[DeepBlue,->] (0,.2)--(3.5,.2) node[midway,above]{$v=0.98c$};\draw[dashed] (4,-.5)--(4,.8) node[above]{衰变事件（平均位置待求）};
\node[below] at (2,-.7){粒子自身静止系平均寿命 $\tau_0$};
""", r"题图：同一粒子的产生和衰变事件，固有寿命在粒子静止系测量。",
    r"两事件在粒子系中同地，故 $\tau_0$ 是固有时；实验室的飞行距离应使用实验室寿命 $\gamma\tau_0$ 乘实验室速度。")
add(31, 4, r"""
\draw[->] (0,0)--(3,0) node[right]{$x$};\draw[->] (0,0)--(0,2) node[above]{$y$};
\draw[DeepBlue,thick,->] (0,0)--(2,1) node[right]{$\boldsymbol u=(.60c,.30c)$};
\draw[->] (.6,-.7)--(2.5,-.7) node[midway,below]{$S'\text{ 沿 }+x\text{ 以 }.50c\text{ 运动}$};
""", r"题图：实验室中的二维速度与沿 $+x$ 的参考系变换。",
    r"两个速度分量均除以相同的 $1-vu_x/c^2$，横向分量还含 $1/\gamma_v$；不能只对纵向分量做相对论变换而保留 $u_y$ 不变。")
SHIPS = r"""
\draw[->] (-1,0)--(5,0) node[right]{地面系 $x$};
\fill (0,0) circle (2pt) node[below]{$A$};\fill (4,0) circle (2pt) node[below]{$B$};
\draw[DeepBlue,->] (0,.4)--(1.7,.4) node[midway,above]{$+0.80c$};\draw[DeepBlue,->] (4,.4)--(2.6,.4) node[midway,above]{$-0.60c$};
"""
add(31, 5, SHIPS, r"题图：两船速度先都相对地面取值，右行船 $A$ 是所求新参考系。",
    r"$A$ 系由沿 $+x$ 以 $0.80c$ 的洛伦兹变换得到，故把 $B$ 的地面速度 $-0.60c$ 代入同一速度合成式；所得负号表示在 $A$ 系仍向左。",
    ac=r"解图：先固定谁是观察者，再把另一船的有号地面速度变换过去。")
ENERGY_Q = r"""
\draw[thick] (0,0) rectangle (1.5,.65);\node at (.75,.325){$mc^2$};
\draw[DeepBlue,thick] (1.5,0) rectangle (3,.65);\node at (2.25,.325){$K=mc^2$};
\node[above] at (1.5,.9){粒子总能量的两部分};\node[below] at (1.5,-.35){静质量 $m$，速度 $v$ 待求};
"""
add(31, 6, ENERGY_Q, r"题图：题设给出动能与静止能相等，两部分组成粒子的总能量。",
    r"左块为静止能，右块为题给动能，总能量才等于 $\gamma mc^2$；因此先得到 $\gamma=2$，再由 $1-v^2/c^2=1/\gamma^2$ 求速率。",
    ac=r"解图：区分静止能、动能和总能量，避免把 $K$ 直接等同于 $\gamma mc^2$。")
add(31, 8, r"""
\fill (0,0) circle (2pt) node[below]{$a,m_a$};\draw[DeepBlue,->] (0,.3)--(1.7,.3) node[midway,above]{$\boldsymbol p_a$};
\fill (2.5,0) circle (3pt) node[below]{$b,m_b,\ v_b=0$};
\draw[->] (3.1,0)--(4.3,0);\draw[dashed] (5,0) circle (.5);\node[above] at (5,.7){末态总静质量至少 $M_f$};
""", r"题图：实验室固定靶反应的初态；入射总动量非零，末态在实验室不能全部静止。",
    r"靶在实验室静止使初态不变量含 $2m_bc^2E_a$；阈值的末态仅在动量中心系无相对运动，在实验室仍共同平移。")

# Modern physics: given spectra and apparatus belong in questions; measured or
# calculated energy, momentum and decay curves belong in solutions.
add(32, 1, r"""
\draw[->] (0,0)--(4.8,0) node[right]{$\lambda$};\draw[->] (0,0)--(0,2) node[above]{单位波长谱};
\draw[DeepBlue,thick] (0.15,.05)..controls(.45,.2)and(.55,1.65)..(.9,1.65)..controls(1.5,1.65)and(1.8,.55)..(4.4,.12);
\draw[dashed] (.9,0)--(.9,1.65);\node[below] at (.9,0){$500\,\mathrm{nm}$};\node[above] at (3.1,1.3){黑体近似，$T$ 待求};
""", r"题图：给定单位波长谱的峰值位置；纵轴只示意形状，不代表额外的强度测量。",
    r"主曲线峰值在题给 $500\,\mathrm{nm}$，因此由位移律求得 $5796\,\mathrm K$；曲线的全波长积分给辐出度，不能把峰值纵坐标当作总功率。")
PHOTO_Q = r"""
\draw[very thick] (0,-.7)--(0,1) (4,-.7)--(4,1);
\node[below] at (0,-.7){阴极 K};\node[below] at (4,-.7){收集极 A};
\draw[DeepBlue,->] (-1.2,1.6)--(0,.5) node[pos=.15,left]{入射光};
\draw[->] (.4,.2)--(2,.2) node[midway,above]{$e^-$};
\node[above] at (2,1.1){反向截止电压 $U_s$ 待求};
"""
add(32, 2, PHOTO_Q, r"题图：单色光照射阴极，反向电压阻碍光电子抵达收集极；给定 $W$ 与入射波长。",
    r"从阴极到较低电势收集极，电子电势能增加 $eU_s$；能量上限由单光子能量减逸出功确定。")
add(32, 3, r"""
\draw[->] (0,0)--(4.5,0) node[right]{$f/(10^{14}\,\mathrm{Hz})$};\draw[->] (0,0)--(0,2) node[above]{$U_s/\mathrm V$};
\fill[DeepBlue] (1.5,.5) circle (2pt) node[left]{$(6.0,.50)$};\fill[DeepBlue] (3,1.33) circle (2pt) node[right]{$(8.0,1.33)$};
\node[below] at (2,-.55){同一种金属的两次测量，横轴按示意比例};
""", r"题图：两组已知频率与截止电压，阈频和拟合直线尚未给出。",
    r"两点的电压差除以频率差为 $h/e$，纵截距是 $-W/e$；应在同一组数据单位下求斜率，不能遗漏横轴的 $10^{14}$ 因子。")
add(32, 4, r"""
\draw[DeepBlue,thick,->] (-2,0)--(0,0) node[midway,above]{$\gamma,\lambda$};\draw[DeepBlue,thick,->] (0,0)--(0,1.8) node[midway,right]{$\gamma',\lambda'$};
\fill (0,0) circle (2pt) node[below]{$e^-\text{ 初始静止}$};\draw[dashed] (0,0)--(2,0);\node at (.5,.45){$90^\circ$};
""", r"题图：入射光子与散射光子的夹角为 $90^\circ$，电子初始静止。",
    r"入射与散射光子的动量互相垂直，电子反冲动量是两者之差；电子动能仍应由相对论能量关系确定，不能直接令电子也转过 $90^\circ$。")
ELECTRON_ACCEL = r"""
\draw[very thick] (0,-1)--(0,1) (3,-1)--(3,1);
\fill (-.6,0) circle (1.8pt) node[below]{$e^-,\ v_0=0$};\draw[DeepBlue,->] (.2,0)--(2.7,0);
\draw[<->] (0,-1.4)--(3,-1.4) node[midway,below]{加速电势差大小 $U$};\node[above] at (1.5,1.2){动能增加 $eU$};
"""
add(32, 5, ELECTRON_ACCEL, r"题图：电子从静止跨过加速电势差，$U$ 是使电子动能增加的电压大小。",
    r"加速区只确定获得的动能 $eU$；先用适用的能量与动量关系得到 $p$，再用 $\lambda=h/p$，波长并不直接等于 $hc/(eU)$。",
    ac=r"解图：把电势差转为电子动能，再按低能或相对论关系求动量。")
add(32, 6, r"""
\foreach \y in {0,-.5,-1}{\draw[thick] (-1,\y)--(3.5,\y);}
\draw[DeepBlue,->] (-1,1)--(.5,0);\draw[DeepBlue,->] (.5,0)--(2,1);
\draw[<->] (3,0)--(3,-.5) node[midway,right]{$d=.200\,\mathrm{nm}$};\node at (-.1,.18){$\theta_B$};
\node[above] at (1,1.4){电子经 $54.0\,\mathrm V$ 加速};
""", r"题图：晶面间距 $d$ 与电子束相对晶面的布拉格角 $\theta_B$。",
    r"布拉格角从晶面量起，不是从法线量起；相邻晶面的往返额外路程是 $2d\sin\theta_B$，一级反射令其等于电子德布罗意波长。")
HYDROGEN = r"""
\draw[thick] (0,0)--(3,0) node[right]{$n=2$};\draw[thick] (0,1)--(3,1) node[right]{$n=3$};\draw[dashed] (0,2)--(3,2) node[right]{$n\to\infty$，电离限};
\draw[DeepBlue,->] (1,1)--(1,.1);\draw[->] (2,1)--(2,1.9);\node[left] at (0,1){初态};
"""
add(32, 7, HYDROGEN, r"题图：从 $n=3$ 向 $n=2$ 跃迁与从同一初态电离是两种不同能量差；能级高度仅示意。",
    r"向下箭头的光子能量取 $E_3-E_2>0$；电离箭头的终态在 $E=0$ 连续谱边界，所需能量为 $-E_3$。")
add(32, 8, r"""
\draw[thick] (0,0)--(3,0) node[right]{$n_f=2$};\draw[thick] (0,1)--(3,1) node[right]{$n=3$};\draw[thick] (0,1.5)--(3,1.5) node[right]{$n=4$};\draw[dashed] (0,2)--(3,2) node[right]{$n\to\infty$};
\draw[DeepBlue,->] (.6,1)--(.6,.08);\draw[DeepBlue,->] (1.4,1.5)--(1.4,.08);\draw[DeepBlue,->] (2.2,2)--(2.2,.08);
""", r"题图：巴耳末系所有跃迁共有终态 $n_f=2$，初态从3逐渐增加到电离限。",
    r"最短能级落差对应最长波长，故取 $3\to2$；初态趋于电离限给最大能量差和短波极限，两极值次序不能颠倒。")
add(32, 9, r"""
\draw[thick] (0,0) circle (.65);\node at (0,0){$^{235}\mathrm U$};\draw[->] (.9,0)--(2,0);
\draw[thick] (2.7,.4) circle (.45);\draw[thick] (3.4,-.4) circle (.45);\node[right] at (4,0){总核子数仍近似235};
\node[below] at (0,-1){$\bar b_i=7.6\,\mathrm{MeV}$};\node[below] at (3,-1){$\bar b_f=8.5\,\mathrm{MeV}$};
""", r"题图：仅按平均每核子结合能粗估裂变，按题设忽略中子与各产物的细小差别。",
    r"比较的是全部235个核子的总结合能，不是两个平均值本身；末态结合能更大表示末态总静质量更小，差额可释放为动能和辐射。")
add(32, 10, r"""
\node at (0,0){$^2\mathrm H$};\node at (1.3,0){$+\ {}^3\mathrm H$};\draw[->] (2.2,0)--(3.1,0);\node at (4,0){$^4\mathrm{He}+n$};
\node[below,align=center] at (1,-.35){中性氘、氚原子\\质量按题给};\node[below,align=center] at (4,-.35){中性氦原子与中子\\质量按题给};
\node[above] at (2,1){左右核子数5、电荷数2相等};
""", r"题图：氘氚聚变前后粒子及守恒量，质量表采用题给中性原子质量。",
    r"初态中性原子共有两个电子，末态中性氦也有两个电子，因此电子静质量在质量差中抵消；$Q$ 应按初态减末态计算。")
add(32, 11, r"""
\draw[->] (0,0)--(5,0) node[right]{$t$};\foreach \x/\lab in {0/0,1.4/1,2.8/2,4.2/3}{\draw (\x,-.1)--(\x,.1);\node[below] at (\x,-.2){$\lab T_{1/2}$};}
\node[above] at (2.1,.7){同一核素：每段长度均为一个半衰期};
""", r"题图：从初态起依次经历三个相等的半衰期，核数比例待求。",
    r"三个相等时间段各乘同一因子 $1/2$，所以末点是 $N_0/8$；同一核素的活度曲线与核数曲线成固定比例，而不是相差一个新的衰减常数。",
    a=r"""
\draw[->] (0,0)--(5,0) node[right]{$t/T_{1/2}$};\draw[->] (0,0)--(0,2.3) node[above]{$N/N_0$};
\draw[DeepBlue,thick,domain=0:3.4,samples=80] plot ({1.3*\x},{2*exp(-ln(2)*\x)});
\foreach \x/\v/\lab in {0/2/1,1.3/1/{1/2},2.6/.5/{1/4},3.9/.25/{1/8}}{\fill[DeepBlue] (\x,\v) circle (1.5pt);\node[right] at (\x,\v+.15){$\lab$};}
\draw[dashed] (3.9,0)--(3.9,.25);\node[below] at (3.9,0){3};
""", ac=r"解图：单核素的指数衰减曲线及整数半衰期处的剩余比例。")
add(32, 12, r"""
\node[draw,minimum width=1.2cm,minimum height=.7cm] (a) at (0,0){母核1};
\node[draw,minimum width=1.2cm,minimum height=.7cm] (b) at (2.7,0){子核2};
\node[draw,minimum width=1.2cm,minimum height=.7cm] (c) at (5.4,0){稳定核};
\draw[->] (a)--(b) node[midway,above]{$\lambda_1$};\draw[->] (b)--(c) node[midway,above]{$\lambda_2=2\lambda_1$};
\node[below] at (0,-.6){$N_1(0)=N_{10}$};\node[below] at (2.7,-.6){$N_2(0)=0$};
""", r"题图：每次母核衰变产生一个子核，子核同时以自己的衰变常数损失。",
    r"子核曲线先增后减，峰值要求流入率 $\lambda_1N_1$ 等于流出率 $\lambda_2N_2$；它不是母核数最多或子核活度恒定的时刻。")
