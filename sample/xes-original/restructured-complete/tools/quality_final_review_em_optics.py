"""Idempotent corrections confirmed in the final ch25--32 book review."""
import re


def _picture(text, label, replacement):
    """Replace the picture belonging to a stable caption label, keeping refs."""
    pos = text.find(r"\label{" + label + "}")
    if pos < 0:
        return text
    start = text.rfind(r"\begin{tikzpicture}", 0, pos)
    end = text.rfind(r"\end{tikzpicture}", 0, pos)
    if start < 0 or end < start:
        raise ValueError(f"picture not found for {label}")
    end += len(r"\end{tikzpicture}")
    return text[:start] + replacement.strip() + text[end:]


def _series_source(note):
    return r"""\begin{tikzpicture}[>=Latex,scale=.88,font=\small]
\draw[thick](0,.35)--(0,1.4)--(.7,1.4);
\draw[thick](.7,1.18)rectangle(1.7,1.62);
\node[above]at(1.2,1.7){$R$};
\draw[thick](1.7,1.4)--(2.3,1.4)
 ..controls(2.3,1.9)and(2.8,1.9)..(2.8,1.4)
 ..controls(2.8,1.9)and(3.3,1.9)..(3.3,1.4)
 ..controls(3.3,1.9)and(3.8,1.9)..(3.8,1.4)
 ..controls(3.8,1.9)and(4.3,1.9)..(4.3,1.4)--(4.9,1.4);
\node[above]at(3.3,1.95){$L$};
\draw[thick](4.9,1.03)--(4.9,1.77)(5.2,1.03)--(5.2,1.77);
\node[above]at(5.05,1.87){$C$};
\draw[thick](5.2,1.4)--(6,1.4)--(6,-.6)--(0,-.6)--(0,-.35);
\draw[thick](0,0)circle(.35);\node at(0,0){$\sim$};
\node[left]at(-.4,0){$U$};
\node[below]at(3,-.65){""" + note + r"""};
\end{tikzpicture}"""


COMPENSATION = r"""\begin{tikzpicture}[>=Latex,scale=.88,font=\small]
\draw[thick](0,0)--(0,.65)(0,1.35)--(0,2)--(4.4,2);
\draw[thick](0,0)--(4.4,0);
\draw[thick](0,1)circle(.35);\node at(0,1){$\sim$};
\node[left]at(-.4,1){$U,\omega$};
\draw[thick](2,2)--(2,1.4)(2,.6)--(2,0);
\draw[thick](1.7,.6)rectangle(2.3,1.4);\node at(2,1){$Z_L$};
\node[below]at(2,-.15){感性负载};
\draw[thick](4.4,2)--(4.4,1.15)(4.05,1.15)--(4.75,1.15)
 (4.05,.85)--(4.75,.85)(4.4,.85)--(4.4,0);
\node[right]at(4.85,1){$C$};
\foreach\x in{2,4.4}{\fill(\x,0)circle(1.5pt);\fill(\x,2)circle(1.5pt);}
\end{tikzpicture}"""


TRANSFORMER = r"""\begin{tikzpicture}[>=Latex,scale=.88,font=\small]
\draw[thick,TextGray](3.1,-1.3)--(3.1,1.3)(3.3,-1.3)--(3.3,1.3);
\foreach\x/\sgn in{2.4/1,4/-1}{
 \draw[thick](\x,1)
 ..controls(\x+\sgn*.6,1)and(\x+\sgn*.6,.5)..(\x,.5)
 ..controls(\x+\sgn*.6,.5)and(\x+\sgn*.6,0)..(\x,0)
 ..controls(\x+\sgn*.6,0)and(\x+\sgn*.6,-.5)..(\x,-.5)
 ..controls(\x+\sgn*.6,-.5)and(\x+\sgn*.6,-1)..(\x,-1);
 \fill[DeepBlue](\x-\sgn*.2,.9)circle(1.8pt);}
\draw[thick](2.4,1)--(2.4,1.6)--(.2,1.6)--(.2,.35)
 (2.4,-1)--(2.4,-1.6)--(.2,-1.6)--(.2,-.35);
\draw[thick](.2,0)circle(.35);\node at(.2,0){$\sim$};
\node[left]at(-.2,0){$U_1$};
\draw[thick](4,1)--(4,1.6)--(6.2,1.6)--(6.2,.55)
 (4,-1)--(4,-1.6)--(6.2,-1.6)--(6.2,-.55);
\draw[thick](6,-.55)rectangle(6.4,.55);\node[right]at(6.5,0){$R_L$};
\node[left]at(2.05,0){$N_1$};\node[right]at(4.3,0){$N_2$};
\node[above]at(3.2,1.85){$N_1:N_2=n:1$};
\end{tikzpicture}"""


LIGHT_CLOCK = r"""\begin{tikzpicture}[>=Latex,font=\small,scale=.88]
\draw[DeepBlue,thick,->](0,0)--(2,1.5);
\draw[DeepBlue,thick,->](2,1.5)--(4,0);
\draw[dashed](0,0)--(4,0)(2,0)--(2,1.5);
\fill(0,0)circle(1.5pt)node[below]{$A$};
\fill(2,1.5)circle(1.5pt)node[above]{$B$};
\fill(4,0)circle(1.5pt)node[below]{$C$};
\draw[<->](0,-.6)--(2,-.6)node[midway,below]{$v\Delta t/2$};
\draw[dashed](2,1.5)--(4.7,1.5)(4,0)--(4.7,0);
\draw[<->](4.7,0)--(4.7,1.5)node[midway,right]{$L$};
\node[above left]at(1,.75){$c\Delta t/2$};
\end{tikzpicture}"""


PRISM_TRAIN_QUESTION = r"""\begin{tikzpicture}[>=Latex,font=\small,every node/.style={fill=none},scale=.88]
\draw[thick](0,1.1)--(2.2,1.1)--(2.2,-1.1)--cycle;
\node[anchor=west]at(2.35,1.8){$n=1.5$};
\draw[TextGray,thin](2.35,1.58)--(1.8,.65);
\draw[DeepBlue,->](1.1,2.2)--(1.1,1.15);
\draw[DeepBlue,->](1.1,1.1)--(1.1,0);
\draw[DeepBlue,->](1.1,0)--(3.3,0);
\node[above]at(1.1,2.2){物 $AB$};
\draw[<->,thick](3.8,-1)--(3.8,1);
\draw[>-<,thick](5.5,-1)--(5.5,1);
\node[above]at(3.8,1){$f_1=10$};
\node[above]at(5.5,1.6){$f_2=-10$};
\node[below]at(3.1,-1.4){棱镜右侧 $10\,\mathrm{cm}$};
\node[below]at(5.1,-1.9){两镜相距 $15\,\mathrm{cm}$};
\end{tikzpicture}"""


COHERENCE_OLD = r"""对于两束近单色光，令复相干度为 $\gamma_{12}$，平均强度可写成
\[
 I=I_1+I_2+2\sqrt{I_1I_2}\,|\gamma_{12}|
 \cos(\Delta\varphi+\arg\gamma_{12}).
\]"""
COHERENCE_NEW = r"""沿用前文 $\Gamma_{12}=\langle U_1^*U_2\rangle$ 的定义，它已经包含两路的全部相位。若把可控的传播相位差单独记为 $\Delta\varphi$，就须另外定义去掉这一相位后的复相干度 $\gamma_{12}^{(0)}$，使
\[
 \Gamma_{12}=\sqrt{I_1I_2}\,\gamma_{12}^{(0)}e^{\mathrm i\Delta\varphi},\qquad
 \gamma_{12}=\gamma_{12}^{(0)}e^{\mathrm i\Delta\varphi}.
\]
因此平均强度为
\[
 I=I_1+I_2+2\sqrt{I_1I_2}\,|\gamma_{12}^{(0)}|
 \cos\!\left(\Delta\varphi+\arg\gamma_{12}^{(0)}\right).
\]
两种复相干度的模相同；不能把已包含传播相位的 $\arg\gamma_{12}$ 再与同一 $\Delta\varphi$ 相加。"""


def apply_chapter_revision(number, text):
    if number == 25:
        text = _picture(text, "ch25:quality:q3", _series_source(r"$U=10\,\mathrm V$（有效值）"))
        text = _picture(text, "ch25:quality:q4", _series_source(r"保持有效值 $U$，改变 $\omega$"))
        text = _picture(text, "ch25:quality:q6", COMPENSATION)
        for role in ("q8", "a8"):
            text = _picture(text, "ch25:quality:" + role, TRANSFORMER)
    if number == 28:
        text = _picture(text, "ch28:quality:q8", PRISM_TRAIN_QUESTION)
        text = text.replace("在水下向空气看，$n_1>n_2$，所以近轴视深小于真实深度。",
                            "在空气中看水下物体，$n_1>n_2$，所以近轴视深小于真实深度。")
    if number == 29:
        # Also applied to the persistent authored notes source. The normal
        # chapter generator inputs that source without regenerating its text.
        text = text.replace(COHERENCE_OLD, COHERENCE_NEW)
    if number == 30:
        start = text.find(r"\begin{origexamplebox}{晶片后的两束横向分离}")
        if start >= 0:
            end = text.index(r"\end{xesolution}", start)
            text = text[:start] + text[start:end].replace(r"\Delta y", r"\Delta x") + text[end:]
    if number == 31:
        text = _picture(text, "ch31:quality:a1", LIGHT_CLOCK)
        text = text.replace(
            r"实验室半周期 $\Delta t$ 内，光程为三角形斜边 $c\Delta t$，镜面横移为 $v\Delta t$",
            r"实验室半周期 $\Delta t/2$ 内，光程为三角形斜边 $c\Delta t/2$，镜面横移为 $v\Delta t/2$")
    return text


ADDITION_PROOF_OLD = r"""固定第二方向，右边是关于第一方向的 $l$ 阶球谐函数，并在同时旋转两方向时不变，因此只能是 $C_lP_l(\cos\gamma)$。令两方向重合并在球面上积分：正交归一性给出右边积分为
$\sum_m1=2l+1$；而旋转对称性说明
$\sum_m|Y_{lm}|^2$ 是常数，其球面积分为 $2l+1$，故常数为 $(2l+1)/(4\pi)$。于是 $C_l=(2l+1)/(4\pi)$ 的倒数，得到公式。"""
ADDITION_PROOF_NEW = r"""先定义尚未归一化的核
\[
 K_l(\Omega,\Omega')=\sum_{m=-l}^{l}Y_{lm}(\Omega)Y_{lm}^*(\Omega').
\]
旋转在固定 $l$ 的球谐空间中作酉变换，所以同时旋转两方向不改变 $K_l$。固定第二方向后，它是绕该方向轴对称的 $l$ 阶球谐函数，故
$K_l=C_lP_l(\cos\gamma)$。令两方向重合，$P_l(1)=1$，旋转不变性使 $K_l(\Omega,\Omega)=C_l$ 为常数。再用正交归一性，
\[
 4\pi C_l=\int K_l(\Omega,\Omega)\,\dd\Omega
 =\sum_{m=-l}^{l}\int |Y_{lm}|^2\,\dd\Omega=2l+1.
\]
因此 $C_l=(2l+1)/(4\pi)$；将 $K_l=C_lP_l$ 两边乘以 $4\pi/(2l+1)$，即得所列公式。"""

HUANG_PICTURE = r"""\begin{tikzpicture}[>=Latex,font=\small,scale=.85,every node/.style={fill=none}]
\draw[dashed](-2,-2.2)rectangle(6,1.35);
\draw[dashed,TextGray](0,-.2)--(0,.95)(4,-.2)--(4,.95);
\fill(.6,0)circle(2pt)node[below left]{$M,+q$};
\fill(3.4,0)circle(2pt)node[below right]{$m,-q$};
\draw[thick](.7,0)--(1.05,.18)--(1.4,-.18)--(1.75,.18)--(2.1,-.18)--(2.45,.18)--(2.8,-.18)--(3.3,0);
\draw[DeepBlue,->](0,.7)--(.6,.7)node[midway,above]{$u_+$};
\draw[DeepBlue,->](4,.7)--(3.4,.7)node[midway,above]{$u_-$};
\draw[->](-.2,1.8)--(3.5,1.8)node[right]{$\boldsymbol E$，位移正向};
\node at(2,-1.05){$x=u_+-u_-$，$p=qx$，回复劲度 $K$};
\node at(2,-1.8){虚线为平衡位置，原胞体积 $\Omega$};
\end{tikzpicture}"""

BINARY_PICTURE = r"""\begin{tikzpicture}[>=Latex,font=\small,scale=.85,every node/.style={fill=none}]
\draw[dashed] (0,0)ellipse(1.6 and .85)(0,0)ellipse(.9 and .478125);
\fill(-1.6,0)circle(3pt)node[left]{$m_1$};
\fill(.9,0)circle(4pt)node[right]{$m_2$};
\fill(0,0)circle(1.2pt);\draw[TextGray](0,-.12)--(0,-1.12)node[below]{质心};
\draw[DeepBlue,->](-1.6,0)--(-1.6,-.7);
\draw[DeepBlue,->](.9,0)--(.9,.65);
\draw[dashed,TextGray](-1.6,.1)--(-1.6,1.18)(.9,.1)--(.9,1.18);
\draw[<->](-1.6,1.18)--(.9,1.18)node[midway,above]{$R$};
\node[above]at(0,1.85){共同轨道角速度 $\Omega$};
\end{tikzpicture}"""


BINARY_OLD = r"""质量四极矩的三阶时间导数代入引力四极辐射公式，得到
\[
 \boxed{P_{\rm GW}=\frac{32}{5}\frac{G}{c^5}"""
BINARY_NEW = r"""以下采用弱场、慢速的最低阶四极近似，要求 $GM/(Rc^2)\ll1$，并把轨道衰减视为相对一个公转周期很慢的过程。取相对位矢
$\boldsymbol R(t)=R(\cos\Omega t,\sin\Omega t,0)$，无迹质量四极矩为
\[
 I_{ij}=\mu\left(R_iR_j-\frac13R^2\delta_{ij}\right).
\]
除去不随时间变化的项，有
$I_{xx}=(\mu R^2/2)\cos2\Omega t$、
$I_{yy}=-(\mu R^2/2)\cos2\Omega t$、
$I_{xy}=I_{yx}=(\mu R^2/2)\sin2\Omega t$。
分别求三阶导数，两个对角项及两个非对角项的平方相加，得到
\[
 \sum_{i,j}(\dddot I_{ij})^2=32\mu^2R^4\Omega^6.
\]
代入 $P_{\rm GW}=G\langle\sum_{i,j}(\dddot I_{ij})^2\rangle/(5c^5)$，得到
\[
 \boxed{P_{\rm GW}=\frac{32}{5}\frac{G}{c^5}"""


def apply_advanced_revision(name, text):
    """Final physical cross-check of A4; run after the earlier quality layer."""
    name = str(name).rsplit('/', 1)[-1]
    if name == 'A4-electrostatics.tex':
        text = text.replace(ADDITION_PROOF_OLD, ADDITION_PROOF_NEW)
    if name == 'A4-magnetostatics.tex':
        text = text.replace(
            r"两条无限长 $z$ 向导线位于 $x=\pm d/2$，载流分别为 $+I,-I$。求磁标势；取 $p=Id$、$d\to0$ 的二维偶极极限。再把该偶极置于半径 $R$ 的超导圆柱轴线上，求柱内平衡场。",
            r"两条无限长 $z$ 向导线分别位于 $x=+d/2$ 和 $x=-d/2$，相应载流为 $+I$ 和 $-I$。求磁标势；取 $p=Id$、$d\to0$ 的二维偶极极限。再把该偶极置于半径 $R$ 的无限长超导圆柱空腔轴线上，求腔内平衡场。")
        for role in ('q6', 'a6'):
            label = 'advA4:quality:A4-magnetostatics:' + role
            pos = text.find(r'\label{' + label + '}')
            if pos >= 0:
                start = text.rfind(r'\begin{tikzpicture}', 0, pos)
                end = text.rfind(r'\end{tikzpicture}', 0, pos) + len(r'\end{tikzpicture}')
                picture = text[start:end]
                picture = picture.replace(
                    r"\node at (-.4,0){$\odot$};\node at (.4,0){$\otimes$};\node[above] at (-.4,.3){$+I$};\node[below] at (.4,-.3){$-I$};",
                    r"\node at (-.4,0){$\otimes$};\node at (.4,0){$\odot$};\node[above] at (-.4,.3){$-I$};\node[above] at (.4,.3){$+I$};")
                picture = picture.replace(r'超导圆柱横截面 $R$', r'超导圆柱空腔横截面 $R$')
                text = text[:start] + picture + text[end:]
        text = text.replace(r'\node[below] at (.4,-.3){$+I$};', r'\node[above] at (.4,.3){$+I$};')
        text = text.replace(r'因此成对电流给出单值势', r'因此在共同选定的割线之外，成对电流的标势为')
        text = text.replace(r'在 $r=R$ 直接计算 $H_r=0$；$R\to\infty$ 时附加均匀场消失，退回自由空间偶极。', r'在 $r=R$ 直接计算 $H_r=0$；例如自由空间中 $x=0,y\ne0$ 处有 $H_y=-p/(2\pi y^2)$，也与右侧 $+I$、左侧 $-I$ 的 Biot--Savart 场相符。$R\to\infty$ 时附加均匀场消失，退回自由空间偶极。')
        if r'球外是真空，另有' not in text:
            text = text.replace(r'在 $r=R$ 检查 $B_n$ 连续、$H_t$ 连续，边界条件满足。',
                            r'球外是真空，另有 $\boldsymbol H_{\rm out}=\boldsymbol B_{\rm out}/\mu_0$。在 $r=R$ 检查 $B_n$ 连续、$H_t$ 连续，边界条件满足。')
    if name == 'A4-waves.tex':
        text = text.replace('在线性、各向同性、无色散介质中', '在均匀、线性、各向同性、无色散介质中')
        if r'以下各行波的 TE 单位矢量' not in text:
            text = text.replace(r'电场振幅的 Fresnel 反射系数为',
            r'以下各行波的 TE 单位矢量统一取垂直于入射面的 $\boldsymbol s$，TM 单位矢量取 $\boldsymbol p=\boldsymbol s\times\hat{\boldsymbol k}$；反射波的 $\boldsymbol p$ 随其传播方向重新确定。在此约定下，电场振幅的 Fresnel 反射系数为')
        for role in ('q1', 'a1'):
            text = _picture(text, 'advA4:quality:A4-waves:' + role, HUANG_PICTURE)
        text = text.replace(r'相对位移为 $x$，谐回复劲度为 $K$。',
                            r'沿电场正向的位移分别为 $u_+,u_-$，相对位移 $x=u_+-u_-$，谐回复劲度为 $K$。')
        text = text.replace(r'远区 $r$ 远大于源尺度时',
                            r'取源尺度 $a_s\ll c/\omega$ 的电偶极近似，并在辐射区 $r\gg c/\omega$ 观察；此时源内部的传播相位差可忽略，因而')
        text = text.replace(BINARY_OLD, BINARY_NEW)
        for role in ('q5', 'a5'):
            text = _picture(text, 'advA4:quality:A4-waves:' + role, BINARY_PICTURE)
        text = text.replace('圆轨道双星的相对间距 $R$ 与质心；图示质量比和轨道形状仅作投影。', '圆轨道双星的相对间距 $R$ 与质心；两条同心椭圆分别为两天体圆轨道的投影。')
    return text
