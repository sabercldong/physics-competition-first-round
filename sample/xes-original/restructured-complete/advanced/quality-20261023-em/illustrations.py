"""Geometries and mathematical diagrams for the A4/A6 worked examples."""
SPECS = {}


def tikz(body):
    return r"\begin{tikzpicture}[>=Latex,font=\small,scale=.85,every node/.style={fill=none}]" + "\n" + body + "\n" + r"\end{tikzpicture}"


def put(file, q, qc, ar, a=None, ac=None):
    entry = dict(q=q, qc=qc, ar=ar, ac=ac or "解图：" + qc.removeprefix("题图："))
    if a is not None:
        entry["a"] = a
    SPECS.setdefault(file, []).append(entry)


AXES = r"\draw[->] (-.4,0)--(3,0) node[right]{$x$};\draw[->] (0,-.4)--(0,2) node[above]{$y$};"
CIRCLE_SOURCE = r"""
\draw[thick] (0,0) circle (1);\fill (0,0) circle (1.3pt) node[below]{$O$};
\draw[->] (0,0)--(0,1) node[midway,left]{$R$};
\fill (2.8,0) circle (1.8pt) node[below]{$\boldsymbol r_0$};\draw[dashed] (0,0)--(2.8,0);
"""
WAVEGUIDE = r"""
\draw[thick] (0,0) rectangle (3,1.8);\draw[<->] (0,-.4)--(3,-.4) node[midway,below]{$a$};\draw[<->] (-.4,0)--(-.4,1.8) node[midway,left]{$b$};
\node[below left] at (0,0){$O$};\node[above] at (1.5,2.05){理想导体壁};\node at (1.5,.9){传播方向 $+z\;\odot$};
"""

put("A4-gauge", AXES+r"""
\draw[DeepBlue,thick,domain=0:2.8,samples=70] plot(\x,{.4*sin(360*\x)});
\draw[->] (.4,1.1)--(2.5,1.1) node[midway,above]{$\boldsymbol k$};\node[below] at (1.3,-.6){$\phi=Ae^{\mathrm i(\boldsymbol k\cdot\boldsymbol r-\omega t)}$};
""", r"题图：Klein--Gordon平面波的传播方向和复相位；曲线仅表示某时刻的实部。",
    r"波矢方向给出空间导数 $\nabla\phi=\mathrm i\boldsymbol k\phi$，时间导数给出 $-\mathrm i\omega\phi$；能量与动量密度的比例必须用同一个振幅归一化。")

put("A4-electrostatics", r"""
\draw[->] (-2.5,0)--(2.5,0) node[right]{$x$};\draw[->] (0,-.3)--(0,2.2);
\draw[DeepBlue,domain=-2:2,samples=100] plot(\x,{1.8*exp(-4*\x*\x)});
\draw[dashed,DeepBlue,domain=-2:2,samples=100] plot(\x,{.9*exp(-\x*\x)});
\node[right] at (.9,1.4){两种 $\epsilon$ 的Gaussian核};\node[below] at (0,-.5){核与测试函数 $f(x)$ 配对};
""", r"题图：宽度不同的归一化逼近核，极限须在对测试函数积分之后取。",
    r"核的总面积保持1、质量集中到原点；sinc核虽有负旁瓣，Fourier反演仍可控制配对极限，不能把它当作非负概率密度。")
put("A4-electrostatics", r"""
\draw[thick] (0,0)--(3,0)--(0,3)--cycle;
\foreach \i in {0,1,2,3}{\foreach \j in {0,1,2,3}{\pgfmathtruncatemacro{\k}{\i+\j}\ifnum\k<4\fill[DeepBlue] (\i,\j) circle (1.7pt);\fi}}
\node[below] at (1.5,-.3){$n_1$};\node[left] at (-.2,1.5){$n_2$};\node[right] at (2.1,1.2){$n_3=n-n_1-n_2$};\node[above] at (1.2,3.3){$n=3$ 的指标重数组合};
""", r"题图：完全对称张量的指标重数组合可看作非负整数格点，图用 $n=3$ 示意。",
    r"每个格点代表一个对称分量；取迹把阶数从 $n$ 降到 $n-2$，但不能把各迹条件随意当作独立，满射性必须另证。")
put("A4-electrostatics", r"""
\fill (-.8,0) circle (2pt) node[below]{$-q$};\fill (.8,.6) circle (2pt) node[above]{$+q$};
\draw[DeepBlue,->] (-.8,0)--(.8,.6) node[midway,above]{$\boldsymbol a$};\draw[->] (-1.4,1.2)--(1.8,1.2) node[right]{$\boldsymbol E(\boldsymbol r)$};
\fill (0,.3) circle (1pt) node[below]{$\boldsymbol r$};
""", r"题图：相反电荷关于偶极中心对称分开，外场在这个长度上缓慢变化。",
    r"两电荷位于 $\boldsymbol r\pm\boldsymbol a/2$；合力取两个局部场之差，而力矩的两个力臂均从同一个中心量取，因而可分别作一阶展开。")
put("A4-electrostatics", CIRCLE_SOURCE+r"""
\draw[DeepBlue,->] (2.8,0)--(3.5,.7) node[right]{$\boldsymbol p$};\node at (3.25,.12){$\theta$};\node[below] at (1.7,-.3){$a>R$};\node[above] at (0,1.3){孤立导体，总电荷0};
""", r"题图：外部偶极子相对连心线具有任意取向，球的边界条件是孤立且中性。",
    r"径向与切向偶极分量必须分别映射；球心的补偿像电荷负责保持总感应电荷为零，不能省略后套用接地球的能量。",
    a=CIRCLE_SOURCE+r"""
\fill[DeepBlue] (.36,0) circle (1.8pt) node[above]{$q',\boldsymbol p'$};\fill[DeepBlue] (0,0) circle (2pt) node[below]{$q_0=-q'$};
\draw[DeepBlue,->] (2.8,0)--(3.5,.7) node[right]{$\boldsymbol p$};\node[below] at (1,-.6){像点 $b=R^2/a$；像系不是真实球内电荷};
""", ac=r"解图：像点的点电荷/偶极与球心补偿电荷承担不同的边界条件。")
put("A4-electrostatics", r"""
\fill (0,0) circle (2pt) node[below]{$-Q$};\fill (1.5,0) circle (2pt) node[below]{$+Q$};\draw[thick] (.1,0)--(.4,.2)--(.7,-.2)--(1,.2)--(1.3,0);
\draw[->] (0,1)--(2.4,1) node[right]{$\boldsymbol E$};\draw[<->] (0,-.6)--(1.5,-.6) node[midway,below]{$x$，回复劲度 $k$};
""", r"题图：异号电荷的相对位移谐振子，$x$ 取电场正向。",
    r"电场对相对坐标的势能为 $-QEx$，与 $kx^2/2$ 一起极小化后得到位移；极化强度还需乘数密度 $n$，不能把单分子偶极矩直接当作 $P$。")
put("A4-electrostatics", r"""
\draw[->] (0,0)--(0,2) node[above]{$\boldsymbol E$};\draw[DeepBlue,->] (0,0)--(1.1,1.2) node[right]{$\boldsymbol p$};\node at (.25,.8){$\theta$};\draw[dashed] (0,1.2)--(1.1,1.2);\node[right] at (1.7,0){温度 $T$ 的取向系综};
""", r"题图：永久偶极矩与外场的夹角是系综积分变量，不固定为零。",
    r"场向分量为 $p\cos\theta$，球面取向测度还含 $\sin\theta$；分子能量 $-pE\cos\theta$ 进入Boltzmann权重，归一化后才得到平均投影。")
put("A4-electrostatics", r"""
\draw[thick] (0,0)--(-1.2,2)--(1.2,2)--cycle;\draw (0,2) ellipse (1.2 and .25);\draw[dashed] (0,0)--(0,2.6) node[above]{$z$};
\node at (.3,1){$\alpha$};\draw[->] (0,0)--(1.2,2) node[midway,right]{$r=1$};\node[below] at (0,-.3){顶点 $O$};
""", r"题图：圆锥顶点位于单位球心，半顶角从锥轴量起；上方椭圆示意球面截线。",
    r"薄纬圈面积为 $2\pi\sin\theta\,\mathrm d\theta$，单位球面面积就是立体角；一般经纬小块的两边分别为 $\mathrm d\theta$ 和 $\sin\theta\,\mathrm d\varphi$。")
put("A4-electrostatics", r"""
\draw[->] (0,-1.3)--(0,1.8) node[above]{$z,\boldsymbol E_0$};\fill (0,0) circle (1.8pt);\draw[DeepBlue,->] (0,-.3)--(0,.8) node[right]{$\boldsymbol p$};
\draw[dashed] (0,0)--(1.7,1);\node[right] at (1.7,1){$P(r,\theta)$};\node at (.35,.6){$\theta$};\node[below] at (1.5,-1){分别考虑 $\boldsymbol p\parallel\pm\boldsymbol E_0$};
""", r"题图：共轴偶极与均匀场，场点使用以 $+z$ 为极轴的球坐标。",
    r"固定方位角后，场线切向满足 $\mathrm dr/(r\mathrm d\theta)=E_r/E_\theta$；叠加的是场分量，不能把两套场线的曲线直接相加。")
put("A4-electrostatics", r"""
\draw[->] (0,-1.8)--(0,1.9) node[above]{$z$};\draw[very thick,DeepBlue] (0,-1)--(0,1);\node[left] at (0,1){$+c$};\node[left] at (0,-1){$-c$};
\draw[dashed] (0,0) ellipse (1.2 and 1.55);\fill (1.05,.75) circle (1.6pt) node[right]{$P$};\draw[dashed] (0,1)--(1.05,.75)--(0,-1);
""", r"题图：均匀带电焦线段及到两端点的距离，旋转椭球截线仅表示待验证的候选等势面。",
    r"到两焦点的距离和决定长旋转椭球面，差决定与之正交的双曲面；导体表面电荷密度须由外侧法向场给出，不是把线电荷密度直接投影到面上。")
put("A4-electrostatics", r"""
\fill[DeepBlue!5] (-2,0) rectangle (2,2);\draw[thick] (-2,0)--(2,0);\node[right] at (2,0){$z=0$};
\fill (0,1.3) circle (2pt) node[right]{$\boldsymbol r_0$};\draw[dashed] (0,-1.3)--(0,1.3);\fill[gray] (0,-1.3) circle (1.6pt) node[right]{$\boldsymbol r_0^*$（镜像位置）};
\draw[->] (-1,0)--(-1,-.7) node[left]{$\boldsymbol n$};\node at (-1,1.5){区域 $z>0$};
""", r"题图：上半空间及其边界外法线；像点在求解域之外，像电荷符号尚待边界条件确定。",
    r"区域外法线在平面边界上沿 $-z$；Dirichlet条件用相反号像源抵消边界值，Neumann条件用同号像源抵消法向导数。")
put("A4-electrostatics", CIRCLE_SOURCE+r"\draw[->] (1,0)--(.4,0) node[below]{$\boldsymbol n$};\node[above] at (1.9,1){求解域 $r>R$};",
    r"题图：球外求解域、外部源点与内边界的区域外法线；无穷远行为也属于边界条件。",
    r"球面作为外部区域的内边界，其法线朝球心；Dirichlet单像源利用反演距离恒比，Neumann各球谐阶的导数权重不同，不能由同一个像源系数同时满足。")
put("A4-electrostatics", r"""
\draw[thick] (0,0) circle (1.3);\draw[dashed] (-1.3,0)--(1.3,0);\draw[->] (0,-1.6)--(0,1.8) node[above]{$z$};
\node at (.5,.6){$+V$};\node at (.5,-.6){$-V$};\node[right] at (1.4,0){绝缘缝};\node[left] at (-1.3,.6){半径 $R$};
""", r"题图：赤道分开的两个半球维持相反电势，求解区域在球内。",
    r"边界值关于 $z\mapsto-z$ 反对称，所以仅有奇数阶Legendre多项式；球内正则性舍去原点发散的径向支，赤道跳变点按极限处理。")
put("A4-electrostatics", r"""
\draw[thick] (0,0) rectangle (2,2);\draw[thick] (.6,.5)--(2.6,.5)--(2.6,2.5)--(.6,2.5)--cycle;\draw (0,0)--(.6,.5) (2,0)--(2.6,.5) (2,2)--(2.6,2.5) (0,2)--(.6,2.5);
\fill (1.3,1.25) circle (1.8pt) node[below]{$O$};\node[left] at (0,1){$+V$};\node[right] at (2.6,1.5){$+V$};\node[above] at (1.3,2.7){其余四面 $-V$};
""", r"题图：两个相对面为 $+V$，其余四面为 $-V$，棱边窄缝只用于维持边界电势。",
    r"中心在立方体旋转群下保持不变，六个面的中心影响权重相同且总和为1；因此可将各面单独激励的中心电势线性叠加，而不是对空间位置取普通平均。")
put("A4-electrostatics", r"""
\draw[thick] (0,0) circle (1.3);\draw[very thick,DeepBlue] (0,-1.3)--(0,1.3);\node[right] at (0,.7){均匀线电荷};\draw[->] (-.4,0)--(1.8,0) node[right]{$\rho$};\node[above] at (0,1.6){球面接地，半径 $R$};\node[left] at (-1.3,-.4){总电荷 $Q$};
""", r"题图：带电细线沿接地球的整条直径分布，球面电势为零。",
    r"每个直径线元都可使用球内Dirichlet Green函数；先对真实源坐标积分再检验球面值，线所在处的奇性不能误判成边界条件失败。")

put("A4-magnetostatics", r"""
\draw[thick] (0,0) ellipse (1.2 and .6);\draw[DeepBlue,->] (1.2,0) arc[start angle=0,end angle=65,x radius=1.2,y radius=.6];
\fill (2.5,1.2) circle (1.7pt) node[right]{$\boldsymbol r$};\fill (0,.6) circle (1.5pt) node[above]{$\boldsymbol r'$};\draw[dashed] (0,.6)--(2.5,1.2) node[midway,above]{$|\boldsymbol r-\boldsymbol r'|$};
\node[below] at (0,-.9){局域稳恒电流，$\nabla'\cdot\boldsymbol j=0$};
""", r"题图：源点与场点的导数作用在同一个距离核上，源电流局域且无散。",
    r"同一核满足 $\nabla(1/R)=-\nabla'(1/R)$；对源坐标分部积分时，体项由稳恒连续性为零，远处面项由局域性为零。")
put("A4-magnetostatics", r"""
\draw[thick] (0,0) ellipse (1.1 and .5);\draw[thick] (2.6,.7) ellipse (1.1 and .5);\node at (0,-.8){线圈 $i,I_i$};\node at (2.6,1.6){线圈 $j,I_j$};\draw[dashed] (.5,.35)--(2.1,.45) node[midway,above]{$M_{ij}$};
""", r"题图：相互交链的线圈系统，各电流和磁链都带同一个端口方向约定。",
    r"互感项连接两个不同线圈，能量双重求和中的 $1/2$ 防止把同一对耦合重复计数；电流固定的机械变化必须把电源做功一起核算。")
put("A4-magnetostatics", None, r"题图：端点质点、可变线圈长度和固定截面积，原图保留。",
    r"长度变化改变自感 $L(x)$，理想超导闭回路保持磁链而不是电流；两端以相反速度运动，长度坐标的等效质量须由两质点动能相加得到。")
put("A4-magnetostatics", r"""
\draw[thick] (0,0) circle (1.2);\foreach \x in {-.5,0,.5}{\draw[DeepBlue,->] (\x,-.6)--(\x,.65);}\node[above] at (0,1.5){$\boldsymbol M=M\boldsymbol e_z$};\draw[->] (0,0)--(1.2,0) node[midway,below]{$R$};\node[right] at (1.7,.4){球外无自由电流};
""", r"题图：均匀磁化球、磁化轴与半径，内外场均待求。",
    r"均匀磁化使体束缚电流为零、面束缚电流为 $\boldsymbol M\times\boldsymbol n$；内外标势的连续和法向跃变决定退磁场，不能把 $H$ 与 $B/\mu_0$ 在球内等同。")
put("A4-magnetostatics", r"""
\fill[DeepBlue!8] (0,0) ellipse (1.4 and .65);\draw[thick] (0,0) ellipse (1.4 and .65);\draw[DeepBlue,->] (1.4,0) arc[start angle=0,end angle=65,x radius=1.4,y radius=.65];\draw[->] (0,0)--(0,1.5) node[above]{$\boldsymbol n$};\node at (.3,-.2){张面 $S$};\node[right] at (1.7,0){边界电流 $I$};
""", r"题图：闭合电流圈与任取的跨面，张面法向和边界绕行方向按右手规则关联。",
    r"改变张面只改变标势所用的支路面，真实磁场由边界电流决定；跨面势函数可有跳跃，而绕过电流圈的环路不允许全局单值标势。")
put("A4-magnetostatics", r"""
\draw[thick] (0,0) circle (1.4);\node at (-.4,0){$\odot$};\node at (.4,0){$\otimes$};\node[above] at (-.4,.3){$+I$};\node[below] at (.4,-.3){$-I$};\draw[<->] (-.4,-.8)--(.4,-.8) node[midway,below]{$d$};\node[above] at (0,1.7){超导圆柱横截面 $R$};
""", r"题图：两反向长电流及其二维偶极极限，柱面边界在横截面内取圆。",
    r"两导线的标势必须使用相同支路约定，取 $d\to0$ 时保持 $Id$ 固定；超导边界要求法向磁场为零，不能只规定标势本身为零。")
put("A4-magnetostatics", None, r"题图：原圆柱与三圆柱相交边界的切向电流几何保留。",
    r"面电流只能沿实际边界切向流动；接缝处各面流入、流出量须连续，远区偶极矩要对三类面电流共同积分，不能任意把某一完整圆柱场截断。")

put("A4-waves", r"""
\draw[dashed] (-.7,-.8) rectangle (3.2,.9);\fill (0,0) circle (2pt) node[below]{$M,+q$};\fill (1.7,0) circle (2pt) node[below]{$m,-q$};\draw[thick] (.1,0)--(.4,.2)--(.7,-.2)--(1,.2)--(1.3,-.2)--(1.6,0);\draw[<->] (0,-.6)--(1.7,-.6) node[midway,below]{$x$，劲度 $K$};\draw[->] (0,1.4)--(3,1.4) node[right]{$\boldsymbol E$};\node[right] at (3.2,0){原胞体积 $\Omega$};
""", r"题图：离子相对位移、原胞体积与外场；电子极化需另按局域场方程加入。",
    r"离子相对坐标的惯性由约化质量 $Mm/(M+m)$ 决定；纵模与横模采用不同的宏观电场约束，介电函数的零点和极点分别对应LO与TO频率。")
put("A4-waves", WAVEGUIDE, r"题图：单连通矩形空心波导横截面，壁面为理想导体。",
    r"横截面没有内部导体，TEM所需的非平凡横向静电势无法建立；TE$_{00}$ 的候选纵场为横向常数，代入有限频率Maxwell方程后只能得到零场。")
put("A4-waves", WAVEGUIDE, r"题图：矩形波导内的场由横截面边界与沿 $z$ 的传播常数共同决定。",
    r"TM的纵电场在壁面为零，TE的纵磁场满足法向导数为零；纵场的横向梯度决定其余分量，截止处还须检查传播常数变为零的极限。",
    a=r"""
\draw[thick] (0,0) rectangle (2.4,1.6);\draw[dashed] (1.2,0)--(1.2,1.6) (0,.8)--(2.4,.8);\node at (.6,.4){$+$};\node at (1.8,.4){$-$};\node at (.6,1.2){$-$};\node at (1.8,1.2){$+$};\node[above] at (1.2,1.9){TE$_{11}$：$H_z$};
\begin{scope}[xshift=5cm]\draw[thick] (0,0) rectangle (2.4,1.6);\draw[DeepBlue] (1.2,.8) ellipse (.8 and .45);\node at (1.2,.8){$+$};\node[above] at (1.2,1.9){TM$_{11}$：$E_z$};\node[below] at (1.2,-.35){四壁 $E_z=0$};\end{scope}
""", ac=r"解图：同一时空相位处的纵场符号和节点；横向场应由Maxwell方程继续求出。")
put("A4-waves", r"""
\draw[DeepBlue,thick,<->] (0,-.9)--(0,.9) node[above]{$\boldsymbol p(t)$};\draw[dashed,->] (0,0)--(0,2);\draw[->] (0,0)--(2,1.2) node[right]{$\boldsymbol r$};\node at (.3,.8){$\theta$};\node[below] at (1.5,-.8){远区 $r\gg c/\omega$};
""", r"题图：振荡偶极轴、远区方向与极角，辐射角分布待求。",
    r"远区电场取偶极加速度垂直于观察方向的分量，因而能流含 $\sin^2\theta$；求总功率还需对球面立体角积分，并对余弦振荡平方取时间平均。")
put("A4-waves", r"""
\draw[dashed] (0,0) ellipse (1.7 and 1);\fill (-1.1,0) circle (3pt) node[below]{$m_1$};\fill (.6,0) circle (4pt) node[below]{$m_2$};\fill (0,0) circle (1.2pt) node[below right]{质心};\draw[<->] (-1.1,.5)--(.6,.5) node[midway,above]{$R$};\draw[DeepBlue,->] (-1.1,0)--(-1.1,-.7);\draw[DeepBlue,->] (.6,0)--(.6,.8);\node[above] at (0,1.35){轨道角速度 $\Omega$};
""", r"题图：圆轨道双星的相对间距 $R$ 与质心；图示质量比和轨道形状仅作投影。",
    r"两天体的质心位移方向相反，四极矩却共同以 $2\Omega$ 变化，故引力波频率为 $\Omega/\pi$；由轨道能损失求频率增长时要同时使用Kepler关系消去 $R$。")


def refine_text(name, text):
    if name == "A4-electrostatics":
        text = text.replace("对 Gaussian 核令 $x=\\epsilon u$，则对任意连续快速衰减的 $f$，", "对 Gaussian 核令 $x=\\epsilon u$，取任意Schwartz测试函数 $f$（光滑且各阶导数均快速衰减），则")
        text = text.replace("点偶极子在全空间的电场是", "点偶极子在全空间的电场（非 $\\delta$ 项按以原点为中心的球形主值理解）是")
        old = "取迹把 $S^n$ 映到 $S^{n-2}$。这个映射是满射：给定任意\n$B\\in S^{n-2}$，先取对称化的 $\\delta\\odot B$，再减去有限个更高重迹项即可构造迹恰为 $B$ 的张量。因此无迹子空间是迹映射的核，秩--零化度定理给出"
        new = r"""对 $n\ge2$，取迹映射 $\operatorname{Tr}:S^n\to S^{n-2}$。下面补出它满射的依据。
用分量完全缩并作为两空间的正定内积，取迹的伴随映射为
$B\mapsto\operatorname{Sym}(\delta\otimes B)$。把对称张量对应到齐次多项式，这个伴随映射正对应乘以 $r^2=x_1^2+x_2^2+x_3^2$。
非零多项式乘以 $r^2$ 不可能恒为零，所以伴随映射单射；有限维空间中映射与其伴随秩相同，因此取迹映射的秩等于 $\dim S^{n-2}$，确实满射。
无迹子空间是取迹映射的核，秩--零化度定理于是给出"""
        text = text.replace(old, new)
        if "$n=0,1$ 不存在取迹约束" not in text:
            text = text.replace("$n=1$ 得3个偶极分量", "$n=0,1$ 不存在取迹约束，分别有1、3个分量，也符合通式。$n=1$ 得3个偶极分量")
        sentence = "$n=0,1$ 不存在取迹约束，分别有1、3个分量，也符合通式。"
        while sentence + sentence in text:
            text = text.replace(sentence + sentence, sentence)
    if name == "A4-magnetostatics":
        text = text.replace("证明线性介质中 $N$ 个线圈的磁能为", "证明真空或线性互易介质中 $N$ 个线圈的磁能为")
        text = text.replace("证明载流 $I$ 的闭合线圈在不穿过线圈的区域可由磁标势描述，并等效于跨任意张面 $S$ 的磁偶极层。", "证明载流 $I$ 的闭合线圈在无电流的单连通子区域内可由磁标势描述，并等效于跨任意张面 $S$ 的磁偶极层；说明跨张面的支路跳跃。")
        anchor = "把总电流写成 $\\vect j=\\sum_iI_i\\vect j_i^{(1)}$"
        if "% EMReciprocalMedium" not in text:
            addition = r"""% EMReciprocalMedium
“互易”是这里不可省略的条件。真空可直接使用前述积分核；对于位置可变但满足 $\mu_{ij}=\mu_{ji}$ 的线性磁介质，忽略无穷远面项后有
\[
 \int\boldsymbol j_1\cdot\boldsymbol A_2\,\mathrm dV
 =\int\boldsymbol H_1\cdot\boldsymbol B_2\,\mathrm dV
 =\int\boldsymbol H_2\cdot\boldsymbol B_1\,\mathrm dV
 =\int\boldsymbol j_2\cdot\boldsymbol A_1\,\mathrm dV.
\]
中间等号才使用介质张量的对称性。一般非互易介质不能仅凭“线性”就声称电感矩阵对称。
"""
            text = text.replace(anchor, addition + "\n" + anchor, 1)
    if name == "A4-waves":
        anchor = "当 $\\omega<\\omega_c$ 时 $\\beta$ 为纯虚数，模式沿 $z$ 倏逝。各壁面把相应场代入"
        if "% EMExplicitWallFields" not in text:
            addition = r"""% EMExplicitWallFields
为完整写出壁面分布，以下省略共同因子 $e^{\mathrm i(\beta z-\omega t)}$，$k_x=\pi/a,k_y=\pi/b$。
法线从腔内指向金属，因此在 $x=0,a$ 两壁分别有
$(\sigma_s,\boldsymbol K_s)=(\varepsilon E_x,H_y\boldsymbol e_z-H_z\boldsymbol e_y)$ 与
$(-\varepsilon E_x,H_z\boldsymbol e_y-H_y\boldsymbol e_z)$；在 $y=0,b$ 两壁分别有
$(\varepsilon E_y,H_z\boldsymbol e_x-H_x\boldsymbol e_z)$ 与
$(-\varepsilon E_y,H_x\boldsymbol e_z-H_z\boldsymbol e_x)$。
将纵场及梯度逐项代入，TE$_{11}$ 给出
\[
\begin{array}{c|c|l}
\text{壁面}&\sigma_s&\boldsymbol K_s\\\hline
x=0,a&-\dfrac{\mathrm i\omega\varepsilon\mu k_yH_0}{k_c^2}\sin k_yy
&-H_0\cos k_yy\,\boldsymbol e_y
-\dfrac{\mathrm i\beta k_yH_0}{k_c^2}\sin k_yy\,\boldsymbol e_z\\[2mm]
y=0,b&\dfrac{\mathrm i\omega\varepsilon\mu k_xH_0}{k_c^2}\sin k_xx
&H_0\cos k_xx\,\boldsymbol e_x
+\dfrac{\mathrm i\beta k_xH_0}{k_c^2}\sin k_xx\,\boldsymbol e_z
\end{array}
\]
TM$_{11}$ 则为
\[
\begin{array}{c|c|c}
\text{壁面}&\sigma_s&\boldsymbol K_s\\\hline
x=0,a&\dfrac{\mathrm i\varepsilon\beta k_xE_0}{k_c^2}\sin k_yy
&\dfrac{\mathrm i\omega\varepsilon k_xE_0}{k_c^2}\sin k_yy\,\boldsymbol e_z\\[2mm]
y=0,b&\dfrac{\mathrm i\varepsilon\beta k_yE_0}{k_c^2}\sin k_xx
&\dfrac{\mathrm i\omega\varepsilon k_yE_0}{k_c^2}\sin k_xx\,\boldsymbol e_z
\end{array}
\]
每一行同时适用于所列的两相对壁面，是因为纵场变号与法线反向在这些11模中恰相抵消。取实部才是实际电荷、电流；直接代入可验证各壁面的 $-\mathrm i\omega\sigma_s+\nabla_s\cdot\boldsymbol K_s=0$，并在接缝处满足电流连续。
"""
            text = text.replace(anchor, addition + "\n" + anchor, 1)
    if name == "A6-quantum-phenomena":
        anchor = "它在 $t<0$ 严格为零，并在 $t=0^+$ 满足"
        addition = r"""题目未限定阻尼区间，还需给出另外两个分支。临界阻尼 $\Gamma=2\omega_0$ 时取 $\Omega\to0$，得
\[
 \chi(t)=\Theta(t)\,\omega_p^2t\,e^{-\Gamma t/2}.
\]
过阻尼 $\Gamma>2\omega_0$ 时令 $\Lambda=\sqrt{\Gamma^2/4-\omega_0^2}$，得到
\[
 \chi(t)=\Theta(t)\frac{\omega_p^2}{\Lambda}
 e^{-\Gamma t/2}\sinh(\Lambda t).
\]
三种分支的响应本身在 $t=0$ 连续为零，导数的跳跃均为 $\omega_p^2$，来自把运动方程在脉冲附近积分。
以下关于初值与因果性的检查适用于这三个分支。"""
        if "题目未限定阻尼区间，还需给出另外两个分支" not in text:
            text = text.replace(anchor, addition + "\n" + anchor)
    if name == "A6-quantum-mechanics":
        anchor = "尺度压缩 $R\\to0$ 时动能按 $R^{-2}$ 发散，而 Coulomb 势能只按\n$-R^{-1}$ 发散，所以总能量必在有限尺度取最小值。"
        addition = r"""
上述是尺度解释，不能只凭一族试探函数就断言所有态都有下界。对任意归一化、有限动能且使分部积分面项消失的波函数，令 $a_0=\hbar^2/(mk_ee^2)$，利用 $\nabla\cdot\hat{\boldsymbol r}=2/r$ 可直接配方：
\[
 \langle H\rangle=
 \frac{\hbar^2}{2m}\int\left|\nabla\psi+
 \frac{\hat{\boldsymbol r}}{a_0}\psi\right|^2\mathrm dV
 -\frac{\hbar^2}{2ma_0^2}
 \ge-\frac{mk_e^2e^4}{2\hbar^2}.
\]
这里 $k_e=1/(4\pi\varepsilon_0)$；平方项展开后的交叉项恰是 $-k_ee^2\langle1/r\rangle$。这个对所有允许态成立的界排除了无限塌缩。等号态的径向衰减为 $e^{-r/a_0}$，也说明下面的硬球试探态只能给出较粗的变分上界。
"""
        if "上述是尺度解释，不能只凭一族试探函数" not in text:
            text = text.replace(anchor, anchor + "\n" + addition)
        anchor2 = "用传播矩阵消去 $A,B,r$ 后，"
        replacement = r"""为看清消元所依据的四个匹配条件，势垒内部的传播可写成
\[
 \begin{pmatrix}\Psi(a)\\\Psi'(a)\end{pmatrix}
 =\begin{pmatrix}
 \cosh\kappa a&\sinh(\kappa a)/\kappa\\
 \kappa\sinh\kappa a&\cosh\kappa a
 \end{pmatrix}
 \begin{pmatrix}\Psi(0)\\\Psi'(0)\end{pmatrix}.
\]
代入 $\Psi(0)=1+r$、$\Psi'(0)=\mathrm ik(1-r)$，以及 $\Psi(a)=te^{\mathrm ika}$、$\Psi'(a)=\mathrm ikte^{\mathrm ika}$，两式相减即可消去 $r$。整理后，"""
        text = text.replace(anchor2, replacement)
    return text


# A6: quantum states and operators are represented by their actual domain,
# eigenfunctions, spectral intervals, or vector projections, not flow charts.
put("A6-quantum-mechanics", r"""
\draw[thick] (0,0) circle (1.3);\fill (0,0) circle (1.5pt) node[below]{$O$};\draw[->] (0,0)--(1.3,0) node[midway,below]{$R$};\node[above] at (0,1.6){$\psi(R)=0$};\node[right] at (1.7,.5){球内允许，球外 $\psi=0$};
""", r"题图：球形禁闭区域与Dirichlet边界；Coulomb问题另以此态作变分试探。",
    r"半径 $R$ 同时决定边界和径向驻波波数；球内基态用 $u=r\psi$ 消去球坐标的一阶导数，变分能量还须连同势能一起计算。")
WELL = r"""
\draw[->] (-.7,0)--(4.2,0) node[right]{$x$};\draw[very thick] (0,2)--(0,0)--(3,0)--(3,2);\node[below] at (0,0){0};\node[below] at (3,0){$a$};\node at (1.5,1){$V=0$};\node[left] at (0,2){$\infty$};\node[right] at (3,2){$\infty$};
"""
put("A6-quantum-mechanics", WELL, r"题图：无限深阱的两个硬壁位于 $0,a$，波函数在两壁为零。",
    r"两个端点同时为节点，所以只有整数个半波可放入宽度 $a$；$n=0$ 的曲线恒为零，不能归一化，因而不构成态。",
    a=r"""
\foreach \shift/\n/\freq in {0/1/60,5/2/120}{\begin{scope}[xshift=\shift cm]
\draw[->] (-.3,0)--(3.5,0) node[right]{$x$};\draw[->] (0,-.9)--(0,1.1) node[above]{$\Psi_{\n}$};\draw[dashed] (3,-.9)--(3,1.1);\node[below] at (3,-.9){$a$};
\draw[DeepBlue,thick,domain=0:3,samples=80] plot(\x,{.7*sin(\freq*\x)});\end{scope}}
""",
    ac=r"解图：$n=1,2$ 的驻波在两端均为零，第二态还在阱中点有节点；两图纵轴共同按波函数幅值取示意比例。")
BARRIER = r"""
\draw[->] (-1.5,0)--(4.5,0) node[right]{$x$};\draw[thick] (-1.4,0)--(0,0)--(0,1.5)--(2.5,1.5)--(2.5,0)--(4.2,0);
\draw[dashed] (-1.3,.8)--(4,.8) node[right]{$E$};\node[above] at (1.2,1.5){$V_0$};\node[below] at (0,0){0};\node[below] at (2.5,0){$a$};\node[below] at (-.8,-.5){I};\node[below] at (1.2,-.5){II};\node[below] at (3.5,-.5){III};
"""
put("A6-quantum-mechanics", BARRIER, r"题图：三区方势垒，能量位于阱外势能与垒顶之间。",
    r"I、III区具有同一实波数 $k$，II区具有实衰减系数 $\kappa$；因此透射流比可直接取 $|t|^2$，而势垒内须同时保留两个指数项以满足两个界面的匹配。")
put("A6-quantum-mechanics", r"""
\draw[->] (-2,0)--(2.3,0) node[right]{$x$};\draw[->] (0,-.2)--(0,2.2) node[above]{$V$};\draw[DeepBlue,domain=-1.7:1.7,samples=70] plot(\x,{.65*\x*\x});\node[right] at (1.2,.8){$V=m\omega^2x^2/2$};
""", r"题图：一维谐势及坐标原点，束缚态需在左右无穷远可归一化。",
    r"抛物势的两端都上升，允许态要同时满足两端衰减；引入升降算符后，基态被降算符湮灭，逐级升高能量而不改变相邻间隔 $\hbar\omega$。",
    a=r"""
\draw[->] (-1.8,0)--(2,0) node[right]{$x$};\draw[DeepBlue,domain=-1.5:1.5] plot(\x,{.7*\x*\x});\foreach \y/\n in {.35/0,.85/1,1.35/2}{\draw[thick] (-1.5,\y)--(1.5,\y);\node[right] at (1.5,\y){$E_{\n}$};}\draw[->] (-1.7,.4)--(-1.7,.8) node[left]{$a^\dagger$};
""", ac=r"解图：谐势内的等间隔能级，最低能级高于势能最低点。")
VECTORS = r"""
\draw[DeepBlue,thick,->] (0,0)--(2.7,0) node[right]{$|a\rangle$};\draw[DeepBlue,thick,->] (0,0)--(1.5,1.6) node[above]{$|b\rangle$};\fill (0,0) circle (1pt) node[below]{$0$};
"""
put("A6-quantum-mechanics", VECTORS, r"题图：两个Hilbert空间向量；图示为它们张成子空间的示意，复相位仍由内积规定。",
    r"把 $|b\rangle$ 分成沿 $|a\rangle$ 的投影与正交余量，余量范数非负给出不等式；等号要求余量为零，即两个向量线性相关。",
    a=VECTORS+r"\draw[dashed] (1.5,0)--(1.5,1.6);\fill (1.5,0) circle (1.5pt) node[below]{$\lambda|a\rangle$};\node[right] at (1.5,.8){$|b\rangle-\lambda|a\rangle$};",
    ac=r"解图：经适当相位选择后，投影与正交余量的实平面截面。")
put("A6-quantum-mechanics", r"""
\coordinate (a) at (0,0);\coordinate (b) at (3,.3);\coordinate (c) at (1.3,1.7);\draw[thick] (a)--(b)--(c)--cycle;\node[left] at (a){$a$};\node[right] at (b){$b$};\node[above] at (c){$c$};\node[below] at (1.5,.1){$d(a,b)$};\node[left] at (.6,.9){$d(a,c)$};\node[right] at (2.2,1){$d(c,b)$};
""", r"题图：三个态向量在其仿射实平面中的距离三角形，距离由Hilbert范数定义。",
    r"沿 $a\to c\to b$ 的向量位移相加等于 $a\to b$，展开范数平方后用Cauchy--Schwarz控制交叉项，才得到长度的三角不等式。")
put("A6-quantum-mechanics", AXES+r"""
\draw[DeepBlue,->] (0,0)--(1.3,1.1) node[above]{$\lambda$};\draw[dashed] (1.3,-1.1)--(1.3,1.1);\node[below] at (1.3,-1.1){$\lambda^*$};\node[right] at (2,1.5){复系数平面};
""", r"题图：反线性作用会共轭复系数，图只表示复系数而非Hilbert空间的物理位置。",
    r"$\lambda$ 与 $\lambda^*$ 在复系数平面关于实轴对称，故 $\Theta(\lambda|a\rangle)=\lambda^*\Theta|a\rangle$；再结合内积第一槽反线性，才能逐槽判断题中双线性类型。")
TRANSLATION = r"""
\draw[->] (-1,0)--(4.5,0) node[right]{$x$};\draw[DeepBlue,domain=-.8:2,samples=60] plot(\x,{exp(-3*(\x-.5)^2)});\draw[DeepBlue,dashed,domain=.5:3.5,samples=60] plot(\x,{exp(-3*(\x-2)^2)});\draw[->] (.5,1.3)--(2,1.3) node[midway,above]{$+\epsilon$};\node[below] at (2,-.5){虚线为 $\psi(x-\epsilon)$};
"""
put("A6-quantum-mechanics", TRANSLATION, r"题图：实轴上的波包与主动平移后的波包，图中取 $\epsilon>0$。",
    r"主动向右平移作用在函数上是自变量替换 $x\mapsto x-\epsilon$，其逆为 $-\epsilon$；内积保持说明幺正，不能由此直接断言平移算符自伴。")
put("A6-quantum-mechanics", r"""
\draw[->] (-1,0)--(4.7,0) node[right]{$x$};\draw[very thick,DeepBlue] (.5,0)--(3,0);\draw (.5,-.15)--(.5,.15) (3,-.15)--(3,.15);\node[below] at (.5,0){$a$};\node[below] at (3,0){$b$};\draw[<->] (1.5,.7)--(1.9,.7) node[midway,above]{$\mathrm dx$};\node[above] at (3.2,1.3){位置谱区间投影};
""", r"题图：连续位置谱中的一个区间及微元，区间投影与点本征态不同。",
    r"蓝色区间对应 $P_{[a,b]}=\int_a^b|x\rangle\langle x|\,\mathrm dx$；点核是算符值密度，位置算符还需再乘坐标 $x$ 积分，三者的量纲和作用都不同。")
put("A6-quantum-mechanics", r"""
\fill[DeepBlue!12] (.8,1.2) rectangle (1.6,1.8);\draw (0,0) grid[xstep=.8,ystep=.6] (2.4,1.8);\node at (1.2,1.5){$A_{ij}$};\node[above] at (1.2,2){正交归一基};\node[below] at (1.2,-.4){行 $i$，列 $j$（以非对角元示意）};
""", r"题图：算符矩阵的一个行列元素，索引由所选正交归一基决定。",
    r"行列交换来自交换内积的两个基向量，复共轭来自伴随定义；因此必须把转置和共轭同时执行，不能仅对每个元素取共轭而保持索引不变。",
    a=r"""
\fill[DeepBlue!12] (.8,1.2) rectangle (1.6,1.8);\draw (0,0) grid[xstep=.8,ystep=.6] (2.4,1.8);\node at (1.2,1.5){$A_{ij}$};\node[above] at (1.2,2){$[A]$};
\begin{scope}[xshift=4.2cm]\fill[DeepBlue!12] (0,.6) rectangle (.8,1.2);\draw (0,0) grid[xstep=.8,ystep=.6] (2.4,1.8);\node at (.4,.9){$A_{ij}^*$};\node[above] at (1.2,2){$[A^\dagger]$};\end{scope}
\node[below] at (3.3,-.5){原来的 $(i,j)$ 元素进入伴随矩阵的 $(j,i)$ 位置并取复共轭};
""", ac=r"解图：非对角矩阵元的位置对换与复共轭同时进行。")
SPIN = r"""
\draw[->] (0,-1.4)--(0,1.7) node[above]{$z$};\draw[->] (-1.5,0)--(1.7,0) node[right]{$x$};\draw[->] (-.9,-.7)--(.9,.7) node[above right]{$y$};\draw[dashed] (0,0) circle (1.1);\fill[DeepBlue] (0,1.1) circle (2pt) node[left]{$|\uparrow\rangle$};\fill[DeepBlue] (0,-1.1) circle (2pt) node[left]{$|\downarrow\rangle$};
"""
put("A6-quantum-mechanics", SPIN, r"题图：自旋1/2态的Bloch球示意，南北极对应 $\sigma_z$ 的两个本征方向。",
    r"投影算符保留各自极点的态并湮灭正交态；$\sigma_+$ 从下态升到上态而在上态作用为零，$\sigma_-$ 相反。Bloch方向不等于一个粒子的空间轨道。")
put("A6-quantum-mechanics", SPIN+r"\draw[DeepBlue,->,thick] (0,0)--(1,1.3) node[right]{$\boldsymbol n$};",
    r"题图：单位方向 $\boldsymbol n$ 决定自旋算符指数的轴，指数参数为 $\theta$。",
    r"沿 $\boldsymbol n$ 的两个本征态分别获得 $e^{\pm\mathrm i\theta}$ 相位；相对相位变为 $2\theta$，对 $U=e^{+\mathrm i\theta\boldsymbol n\cdot\boldsymbol\sigma}$，Bloch向量的主动转角为 $-2\theta$。")

put("A6-quantum-phenomena", r"""
\draw[very thick] (0,0) circle (1.2);\foreach \a in {0,60,120,180,240,300}{\draw[DeepBlue,->] (\a:.5)--(\a:1.05);}\draw[->] (0,0)--(1.2,0) node[midway,below]{$R$};\node[above] at (0,1.6){膜质量 $m$，肥皂泡张力系数 $\alpha$};\node[below] at (0,-1.5){内部热辐射 $T$，外界真空};
""", r"题图：辐射压作用于球形薄膜，肥皂泡模型包含内外两个表面。",
    r"径向膨胀使两表面面积都增加，所以表面能是 $8\pi\alpha R^2$；快速振动保持辐射绝热量 $TR$，接触热库的稳定性则需另检验，二者不能混为一谈。")
put("A6-quantum-phenomena", r"""
\draw[->] (-1.5,0)--(5.8,0) node[right]{$t$};\draw[->,DeepBlue,thick] (0,0)--(0,1.6) node[above]{$\delta(t)$};\node[below] at (0,-.2){0};\node[right,align=left,text width=4cm] at (1.1,1.1){初态静止\\响应在 $t<0$ 为零};
""", r"题图：只在 $t=0$ 作用的单位脉冲，因果响应不能先于激励。",
    r"零时刻的脉冲改变响应导数而不使响应本身跳变；之后的曲线按阻尼大小选择欠阻尼、临界或过阻尼分支，三者都只支撑在 $t\ge0$。",
    a=r"""
\draw[->] (-1.5,0)--(5,0) node[right]{$t$};\draw[DeepBlue,very thick] (-1.4,0)--(0,0);\draw[DeepBlue,domain=0:4.6,samples=120] plot(\x,{1.25*exp(-.5*\x)*sin(150*\x)});\draw[gray,dashed,domain=0:4.6,samples=80] plot(\x,{1.6*\x*exp(-1.5*\x)});\node[above] at (2.9,1.3){实线：欠阻尼示意；虚线：临界示意};
""", ac=r"解图：同为因果的振荡/非振荡脉冲响应，幅值和时间刻度只作形状示意。")

put("A6-relativity", r"""
\draw[very thick] (0,0)--(3,0);\fill (0,0) circle (1.5pt) node[below]{尾};\fill (3,0) circle (1.5pt) node[below]{头};\draw[->] (.3,1)--(1.6,1) node[midway,above]{$v$};\draw[->] (2,1)--(3.2,1) node[midway,above]{$a$};\node[below] at (1.5,-.6){本征长 $L$；地面同时长度 $\ell$ 待求};
""", r"题图：沿杆方向的速度与缓慢加速度；本征长和地面同时长度属于不同测量口径。",
    r"地面长度由同一地面时刻截取两端世界线得到，信号传播却连接不同时刻的两个事件；Born刚性还要求两端本征加速度按位置改变，不能给整根杆同一个本征加速度。",
    a=r"""
\draw[->] (-.3,0)--(4,0) node[right]{$x$};\draw[->] (0,-.2)--(0,3.3) node[above]{$ct$};
\draw[thick] (.3,0)..controls(.5,1.7)and(.9,2.5)..(1.3,3);\draw[thick] (2.1,0)..controls(2.3,1.7)and(2.7,2.5)..(3.1,3);
\draw[dashed] (0,1.4)--(3.5,1.4) node[right]{地面同时截面};\draw[DeepBlue,->] (.35,.2)--(2.5,2.35) node[midway,above left]{光信号};
\node[below] at (.3,0){尾};\node[below] at (2.1,0){头};
""", ac=r"解图：局部短杆世界线的示意，水平截面用于测长，斜光线用于频移；曲线不作精确Born刚性比例图。")
put("A6-relativity", None, r"题图：保留下加速段、磁场半圆与上减速段的原始TikZ几何。",
    r"$X,Y,Z$ 是不同空间位置的束流截面，换系后应在新系同一时刻重新截取每个区域的电荷；不能把实验室同时装入区域的全部粒子不加说明地当作新系同时的同一集合。")
put("A6-relativity", None, r"题图：保留椭圆柱的正负面电荷层、切向正电流与运动方向。",
    r"柱面法向随极角改变，所以面密度变换除四流外还须包含面积元素的变化；圆截面是在新系同一时刻取得，不能把椭圆照片与同时截面混用。")
put("A6-relativity", r"""
\draw[DeepBlue,->] (-2,0)--(0,0) node[midway,above]{$\nu_\tau,E_\nu$};\fill (0,0) circle (2pt) node[below]{$n$ 静止};\draw[->] (.4,0)--(1.5,0);\node[above] at (1.7,0){$\tau^-+p$};
\fill (2.4,0) circle (1.5pt);\draw[dashed] (2.4,0)--(4.6,0);\draw[DeepBlue,->] (2.4,0)--(4.3,1.097) node[right]{$e^-$};\node at (3.1,.18){$30^\circ$};\node[below] at (3.8,-.5){衰变另有两中微子};
""", r"题图：固定中子靶的产生反应与随后定角电子探测，两个过程分别使用能动量守恒。",
    r"电子探测角从原入射束方向量起，未必等于相对 $\tau$ 运动方向的角；先保留入射能量参数并优化允许的 $\tau$ 运动，再讨论无界入射能量极限。")

# Existing detailed source-geometry inputs are retained for these seven tasks.
put("A6-source-exercises", None, r"题图：闭合轨道、切口O与随轨道增大的弧长 $s$，原TikZ图保留。",
    r"切口O两侧是同一个空间位置的不同同步支路；每段固有走时用 $m\,\mathrm ds/p$，同一实验室校准时刻的读数梯度用 $-p/(mc^2)$，两种积分不能混为一个时间差。")
put("A6-source-exercises", None, r"题图：发射晶体、反冲核和迎面运动的吸收晶体，原TikZ图保留。",
    r"光子沿探测方向传播、发射核向反方向反冲，吸收晶体的迎面速度产生蓝移；发射与吸收各自的反冲能都需进入共振条件。")
put("A6-source-exercises", None, r"题图：两入射与两出射光子外线及题给角度，内部电子线表示虚传播子。",
    r"波矢端点的允许集合由总能量与总三动量共同确定；闭合电子内线不是四个可同时满足正能量壳条件的真实电子，不能把图的顶点当作逐步经典碰撞。")
put("A6-source-exercises", None, r"题图：有限质量靶的散射几何与两个参考系的角度，原TikZ图保留。",
    r"实验室中的重入射粒子偏转角与动量中心系散射角不同，最大实验室偏转受靶反冲限制；角度分支应与速度矢量三角形一致。")
put("A6-source-exercises", None, r"题图：中子菱形干涉仪的四段光路与两个输出端口，原TikZ图保留。",
    r"两条到达同一输出端口的路径须保持相干，重力相位取两路势能积分之差；另一个端口的相位与分束振幅相联，不能把某端口变暗解释成中子消失。")
put("A6-source-exercises", None, r"题图：发光杆、脉冲和观察方向的原TikZ配置保留。",
    r"杆长由新系同时截面测得，照片方向由同一接收时刻的迟延光决定；激光脉冲长度还涉及两个端点事件的选择，三个测量问题必须各自指定事件。")
put("A6-source-exercises", None, r"题图：雷达鼠和电波狗的初始垂直速度及连线，原TikZ图保留。",
    r"追及曲线中的连线连接同一时刻的两个位置，接收频移中的光线却连接发射与接收两个迟延事件；频移必须用后者的传播方向。")

put("A6-source-more", r"""
\fill (0,0) circle (2pt) node[below]{光源};\draw[->] (0,-.5)--(2,-.5) node[midway,below]{$v$};\draw[dashed,->] (0,0)--(3.5,0);\draw[DeepBlue,->] (0,0)--(2.4,1.4) node[right]{观察光线};\node at (.9,.2){$\theta$};\draw[gray,dashed] (0,0) circle (1.1);
""", r"题图：运动方向、观察方向与源静止系各向同性条件；球形虚线不预设实验室角分布。",
    r"光行差改变立体角元，多普勒因子改变单光子能量；若强度按观察者接收时间定义，还需计入光行时压缩，不能与按发射实验室时间定义的功率混用。")
put("A6-source-more", r"""
\draw[thick] (0,0) circle (.9);\fill (0,0) circle (2pt) node[below]{核};\fill (.9,0) circle (1.5pt) node[right]{$e^-$};\draw[DeepBlue,->] (.9,0)--(.9,.7);\node[below] at (0,-1.3){经典Coulomb圆轨道};
\begin{scope}[xshift=4.1cm]\draw[thick] (0,0) circle (1.1);\draw[DeepBlue,->] (1.1,0)--(1.1,.8);\node[right] at (1.1,.2){近光速电子};\node[below] at (0,-1.3){存储环弯转半径 $\rho$};\end{scope}
""", r"题图：原子圆轨道与存储环弯转轨道分别使用各自的动力学和辐射近似。",
    r"原子模型需用能量损失求半径随时间收缩，不能用初始能量除初始功率替代整个积分；存储环的近光速辐射含相对论增强，周长也不能直接替代偏转磁铁的弯曲半径。")
put("A6-source-more", r"""
\draw[->] (0,0)--(3,0) node[right]{$x$};\draw[->] (0,0)--(0,2) node[above]{$y$};\draw[DeepBlue,->] (.4,.4)--(2,.4) node[midway,above]{$v_1\boldsymbol e_x$};\draw[DeepBlue,->] (2,.5)--(2,1.7) node[right]{$v_2\boldsymbol e_{y'}$};
""", r"题图：两次正交换系的速度分别相对各自前一参考系定义。",
    r"$S$ 同时测量要求 $t$ 固定，$x''$ 轴还须满足 $y''=0$；合并两条件才得到右下方倾斜的轴线，该倾角不应直接称为标准推动分解中的Wigner旋转角。",
    a=r"""
\draw[->] (-.3,0)--(3.2,0) node[right]{$x$};\draw[->] (0,-1.2)--(0,1.5) node[above]{$y$};\draw[DeepBlue,thick,->] (0,0)--(2.6,-.9) node[right]{$x''$（$S$ 同时截面）};\node at (1,-.12){$\psi<0$};\node[above] at (1.4,1){$v_1,v_2>0$ 的示意};
""", ac=r"解图：同时截面上的轴倾斜向右下，斜率由两个推动共同决定。")
WIRE_Q = r"""
\draw[very thick] (-1,0)--(4.5,0);\draw[->] (0,0)--(1.5,0) node[midway,below]{$I>0$};\fill (1.8,1.3) circle (2pt) node[above]{$q$};\draw[DeepBlue,->] (1.8,1.3)--(3.4,1.3) node[midway,above]{$v_x$};\draw[<->] (.4,0)--(.4,1.3) node[midway,left]{$a$};\node[right] at (4.5,0){$x$};
"""
put("A6-source-more", WIRE_Q, r"题图：中性载流导线、电荷高度与电荷速度；换系沿导线方向。",
    r"电荷处的实验室磁场出纸面，取 $qv_x>0$ 时力指向导线；换系后同时出现电场和磁场，必须在同一事件相加电力与磁力后再比较三维力。",
    a=WIRE_Q+r"\node at (1.1,1.1){$\boldsymbol B\;\odot$};\draw[->] (1.8,1.1)--(1.8,.4) node[right]{$\boldsymbol F\ (qv_x>0)$};",
    ac=r"解图：实验室磁力方向及其符号条件，其他参考系的电磁力须重新分解。")
put("A6-source-more", r"""
\node[draw,circle,minimum size=1.1cm] (a) at (0,0){$A_N$};\draw[->] (.7,0)--(1.6,0);\node[draw,circle,minimum size=.8cm] (b) at (2.4,0){$A_{N-1}$};\node[draw,circle,minimum size=.5cm] (c) at (4,0){$m$};\draw[DeepBlue,->] (b)--(1.6,-.6);\draw[DeepBlue,->] (c)--(4.8,.6);\node[below] at (2,-1.2){从20核子初态连续放出19个核子};
""", r"题图：每一步都是二体反冲，所画箭头在该步母核静止系中相反。",
    r"每次反冲应在当次母核静止系计算，再用快度相加组合到初始系；最大末速度要求后继核的反冲方向逐步同向，最后二核子到单核子的质量公式须单独处理。")
put("A6-source-more", r"""
\fill (-1,0) circle (3pt) node[below]{$t$};\fill (1,0) circle (3pt) node[below]{$\bar t$};\draw[DeepBlue,->] (-1,0)--(-.3,0);\draw[DeepBlue,->] (1,0)--(.3,0);\draw[<->] (-1,.7)--(1,.7) node[midway,above]{$r$};\fill (0,0) circle (1pt) node[below]{质心};\node[above] at (0,1.4){$U(r)=-4\alpha_s k/(3r)$};
""", r"题图：等质量夸克对的相对距离与共同质心，库仑型势只作题设估算模型。",
    r"$r$ 是两体相对距离，单体绕质心半径为 $r/2$，径向方程使用约化质量 $m_t/2$；能否形成轨道结构还要比较公转时间与题给寿命。")
put("A6-source-more", r"""
\draw[very thick] (0,1.4)--(0,0)--(4,0)--(4,1.4);\draw[<->] (0,-.5)--(4,-.5) node[midway,below]{$L$};\node[above] at (2,1.6){$N$ 个自旋1/2费米子};\draw[->] (4,.6)--(4.9,.6) node[right]{$F$};
""", r"题图：一维刚性盒的长度、粒子数与右边界力，粒子数在求长度导数时保持不变。",
    r"每个空间能级最多容纳两个相反自旋，零温填充从低能级向上进行；奇数粒子的最高空间态只有一个粒子，有限粒子数结果应区分奇偶。",
    a=r"""
\foreach \y/\n in {0/1,.6/2,1.6/3}{\draw[thick] (0,\y)--(3,\y);\node[right] at (3,\y){$n=\n$};}\foreach \y in {0,.6}{\draw[DeepBlue,->] (1,\y-.18)--(1,\y+.18);\draw[DeepBlue,->] (2,\y+.18)--(2,\y-.18);}\draw[DeepBlue,->] (1,1.42)--(1,1.78);\node[above] at (1.5,2.2){$N=5$ 的奇数填充示意};
""", ac=r"解图：两个反向自旋占同一空间能级，奇数粒子的最后一级单占。")
put("A6-source-more", r"""
\draw[thick] (0,0) circle (1.15);\draw[->] (0,0)--(0,1.15) node[midway,right]{$R$};\fill (0,1.15) circle (1.6pt);\draw[DeepBlue,->] (0,1.15)--(-1.1,1.15) node[left]{$\boldsymbol\pi=m\boldsymbol v$};\node[right] at (1.8,.4){电子 $q=-e$};\node[right] at (1.8,-.1){$\boldsymbol B=B\boldsymbol e_z\;\odot$};
""", r"题图：电子在出纸面磁场中的逆时针局部回旋，机械动量沿轨道切线。",
    r"轨道按电子运动方向逆时针积分时磁通为正，但电荷 $q=-e$ 使磁通项为负；正则作用量是机械项加 $q\Phi$，导引中心简并与沿场自由动能仍需保留。",
    a=r"""
\fill[DeepBlue!7] (0,0) circle (1.1);\draw[thick] (0,0) circle (1.1);\node at (0,0){$\Phi>0\;\odot$};
\draw[DeepBlue,thick,->] (0,1.1)--(-1.3,1.1) node[left]{$\boldsymbol\pi$};\draw[->] (0,1.5)--(-.65,1.5) node[left]{$\boldsymbol P$};\draw[->] (0,.75)--(.65,.75) node[right]{$q\boldsymbol A$};
\node[right,align=left] at (1.8,0){对称规范，原点取导引中心\\$\boldsymbol P=\boldsymbol\pi+q\boldsymbol A$\\上方三箭头仅平移分层以便比较};
""", ac=r"解图：在对称规范下，电子的磁通项使闭轨正则作用量减小；各动量箭头按同一比例画出。")
put("A6-source-more", r"""
\draw[thick] (0,0) circle (1.15);\fill (0,0) circle (1.5pt) node[below]{$O$};\draw[DeepBlue,->] (1.15,0)--(1.15,.8) node[right]{$p$};\draw[->] (0,0)--(1.15,0) node[midway,below]{$r$};\node[right] at (2,0){$n=n(r)$ 或 $V=V(r)$};\draw[dashed] (0,0) circle (1.4);
""", r"题图：圆对称介质/势场中的候选圆轨道，虚圆表示半径的邻近变分。",
    r"半径变分比较的是固定能量的空间简化作用量，故圆轨道条件来自 $\mathrm d[rn(r)]/\mathrm dr=0$；绕同一时刻的一周相位闭合再给出早期圆轨道量子化，两种条件不能互相替代。")
