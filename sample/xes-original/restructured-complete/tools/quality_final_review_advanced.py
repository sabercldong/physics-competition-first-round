#!/usr/bin/env python3
"""Idempotent, independently reviewed advanced-text corrections, 2026-10-24."""
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]


def replace_once(text, old, new):
    if old == new or new in text:
        return text
    if old not in text:
        if new in text:
            return text
        raise ValueError(f"Final-review anchor missing: {old[:90]!r}")
    if text.count(old) != 1:
        raise ValueError(f"Final-review anchor not unique: {old[:90]!r}")
    return text.replace(old, new, 1)


def replace_between(text, start, end, replacement):
    if replacement in text:
        return text
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + replacement + text[b:]


def apply_file_revision(name, text):
    if name == "A5-geometric.tex":
        text = replace_once(text,
            "把局部折射率分层、切向、法向和梯度放在同一幅图中；\n其中所有标签都避开了曲线。",
            "把局部折射率分层、切向、法向和梯度放在同一幅图中，便于比较梯度的切向与法向分量。")
        text = replace_once(text,
            r"\frac{\dd x}{\dd y}=\tan\theta" + "\n" + r" =\sqrt{\frac{y}{y_m-y}}.",
            r"\frac{\dd x}{\dd y}=\pm\tan\theta" + "\n" + r" =\pm\sqrt{\frac{y}{y_m-y}}.")
        text = replace_once(text,
            r" =y_m\arcsin\sqrt{\frac{y}{y_m}}" + "\n" + r" -\sqrt{y(y_m-y)}}.",
            r" =\pm\left[y_m\arcsin\sqrt{\frac{y}{y_m}}" + "\n" + r" -\sqrt{y(y_m-y)}\right]}.")
        text = replace_once(text,
            r"x-x_c=y_m\!\left(u-\frac12\sin2u\right).",
            r"x-x_c=\pm y_m\!\left(u-\frac12\sin2u\right),\quad 0\le u\le\frac\pi2.")
        text = replace_once(text,
            "正文所积正号表达另一支，镜像或反向参数化即得到本图。",
            "它对应上式的负号分支。两支关于 $x=x_c$ 镜像；仅反向参数化只会改变传播方向，不会改变轨迹的斜率。")
        text = replace_once(text,
            "角放大率定义为 $B=\\tan u'/\\tan u$，傍轴下为 $u'/u$。拉格朗日--亥姆霍兹不变量给出\n\\[\n nyu=n'y'u',\\qquad\n \\boxed{B=\\frac{n}{n'\\beta}}.\n\\]",
            r"""对图~\ref{advA5:fig:angular-magnification}中轴上共轭点的光锥，
角放大率定义为 $B=\tan u'/\tan u\simeq u'/u$，倾角取有向值。
用一条轴上光线和另一条从邻近离轴物点发出的光线组成拉格朗日不变量，得到
\[
 nyu=n'y'u',\qquad
 \boxed{B=\frac{n}{n'\beta}}.
\]
这里 $y,y'$ 是邻近共轭物像的高度，$u,u'$ 是轴上光线的倾角，不能把同一任意光线的 $nyu$ 当作不变量。
对离轴点的光束，应比较两条光线的倾角差，写成
$B=\Delta u'/\Delta u$，由 $ny\Delta u=n'y'\Delta u'$ 得到同一结果。""")
    elif name == "A5-photometry.tex":
        text = replace_once(text,
            "最后一式对同一频率、无损被动传输成立，",
            "最后一式对同一频率、无吸收、无反射损失且无截光的理想传输通道成立，")
    elif name == "A5-wave.tex":
        text = replace_once(text,
            "在相邻双缝面之间，同侧传播距离为 $L$，",
            "采用窄缝离散传播模型：每缝内的振幅和相位近似均匀，忽略斜程的振幅差及单缝包络变化。若缝宽为 $a$，除 $a\\ll D$ 外，还需 $2\\pi aD/(\\lambda L)\\ll1$。\n在相邻双缝面之间，同侧传播距离为 $L$，")
        text = replace_between(text,
            "从零场准静态建立电场，单位体积外界所做功为",
            "\n实对称介电张量可正交对角化为",
            r"""从零场准静态建立电场，电场能密度的增量为
$\dd u=\vect E\cdot\dd\vect D$。若 $u$ 是状态函数，定义电共能
$u^*(\vect E)=\vect E\cdot\vect D-u$，则
\[
 \dd u^*=\vect D\cdot\dd\vect E,\qquad
 D_i=\frac{\partial u^*}{\partial E_i}.
\]
因此二阶偏导可交换给出
\[
 \varepsilon_{ij}=\frac{\partial D_i}{\partial E_j}
 =\frac{\partial^2u^*}{\partial E_j\partial E_i}
 =\frac{\partial^2u^*}{\partial E_i\partial E_j}
 =\varepsilon_{ji}.
\]
对这种线性介质才进一步有 $u=u^*=\tfrac12\vect E\cdot\vect D$。
若存在吸收，频域介电张量可为复数；互易性与无耗散是不同条件。
反 Hermitian 部分决定单色场的平均吸收，色散介质的储能还涉及介电响应的频率导数，不能简单照搬上述实对称、无色散结论。
""")
    elif name == "A6-quantum-phenomena.tex":
        text = replace_once(text,
            "利用 Parseval 公式，电磁场 Hamilton 量成为独立谐振子之和\n\\[\n H=\\sum_{\\vect k,r}\n \\left(\\frac{|p_{\\vect k,r}|^2}{2m}\n +\\frac{m\\omega_{\\vect k}^2|q_{\\vect k,r}|^2}{2}\\right).\n\\]",
            r"""经典场为实场；选取 $\vect e_{-\vect k,r}=\vect e_{\vect k,r}$ 后，
复系数满足 $q_{-\vect k,r}=q_{\vect k,r}^*$，不能把它们当作独立复坐标。
对每一对 $\pm\vect k$ 改用正弦、余弦两个实模式，并按 Parseval 公式归一化，
可把 Hamilton 量写成独立实谐振子之和
\[
 H=\sum_{\lambda}
 \left(\frac{P_{\lambda}^2}{2m}
 +\frac{m\omega_{\lambda}^2Q_{\lambda}^2}{2}\right).
\]
指标 $\lambda$ 枚举独立实模式与偏振；每对波矢的两个实模式对应全波矢球中的两点，态密度无须再额外乘二。""")
        text = replace_once(text,
            r"\omega_p^2=\frac{n_eZe^2}{m\varepsilon_0}.",
            r"\omega_p^2=\frac{n_ee^2}{m\varepsilon_0}.")
        text = replace_once(text,
            "写 $\\chi=\\chi_1+\\ii\\chi_2$，实部控制色散，虚部控制吸收。",
            "这里 $n_e$ 是参与该振子响应的电子数密度；若每个原子有 $Z$ 个等效电子，则 $n_e=Zn_{\\rm atom}$。\n写 $\\chi=\\chi_1+\\ii\\chi_2$，实部控制色散，虚部控制吸收。")
        text = replace_between(text,
            "右端按 $\\pm n$ 成对求和后局部一致收敛，",
            "\n再写\n",
            r"""固定 $z\notin\mathbb Z$，取边界 $C_N$ 为
$|\operatorname{Re}w|,|\operatorname{Im}w|\le N+1/2$ 的正向方框。
在其边界上 $\cot\pi w$ 一致有界，且对固定 $z$，
$|w^2-z^2|$ 为 $N^2$ 量级；因此
\[
 \oint_{C_N}\frac{\pi\cot\pi w}{w^2-z^2}\,\dd w=O(N^{-1})\longrightarrow0.
\]
框内整数 $k=-N,\ldots,N$ 处的留数为 $1/(k^2-z^2)$，
而 $w=z,-z$ 两处的留数之和为 $\pi\cot(\pi z)/z$。
留数定理给出
\[
 0=\frac{\pi\cot\pi z}{z}
   +\lim_{N\to\infty}\sum_{k=-N}^{N}\frac1{k^2-z^2}.
\]
把 $k=0$ 项分出、其余按正负整数配对并乘以 $z$，即得所需展开。
配对项 $2z/(z^2-n^2)$ 在避开整数的任意固定紧集上一致为 $O(n^{-2})$，
故级数局部一致收敛。这里的固定紧集估计不能直接用于随 $N$ 扩大的边界。
""")
        text = replace_once(text, "\n再写\n", "\n在 $|z|<1$ 内再作幂级数展开：\n")
        text = replace_once(text, "用\n\\[\n \\int_0^\\infty", "用（$\\operatorname{Re}s>1$）\n\\[\n \\int_0^\\infty")
        text = replace_once(text,
            "薄膜弹性等效于表面张力系数为 $\\alpha$ 的肥皂泡。",
            "薄膜弹性等效于表面张力系数为常量 $\\alpha$ 的肥皂泡；忽略膜的内能、热容量及辐射对径向运动的惯性贡献。\n振动比膜与辐射之间的换热快，但比光跨越球内的时间慢，使球内辐射可保持近似均匀。")
        text = replace_once(text,
            "因此态振幅必须是复数：",
            "上述仅含 $x,z$ 两方向的序列尚不足以确定一般相对相位。要描述任意空间方向的自旋态，\n在固定的 $z$ 基底中写成")
        text = replace_once(text,
            "概率由模方给出。相位 $\\phi$ 不影响单次 $S_z$ 概率，却影响其他方向的干涉结果，\n这正是实概率模型无法表达的结构。",
            r"""概率由模方给出。除 $P_{z,+}=\cos^2(\theta/2)$ 外，沿另两轴测量得到
\[
 P_{x,+}=\frac{1+\sin\theta\cos\phi}{2},\qquad
 P_{y,+}=\frac{1+\sin\theta\sin\phi}{2}.
\]
例如 $|y+\rangle=(|z+\rangle+\ii|z-\rangle)/\sqrt2$，其 $S_y$ 结果确定，
而 $S_x,S_z$ 各为等概率。固定这一基底后，若只允许两个实振幅，就只能表达
$\phi=0,\pi$ 的实截面，不能覆盖所有三维测量方向；可观测的是相对相位，整体相位仍可任取。""")
    elif name == "A6-quantum-mechanics.tex":
        text = replace_between(text,
            "若 $b=0$ 显然成立。若 $b\\ne0$，对任意复数 $\\lambda$，",
            "\n图~\\ref{advA6:quality:A6-quantum-mechanics:a5}",
            r"""按解图把 $b$ 分解为沿 $a$ 的投影和正交余量。若 $a=0$ 显然成立；
若 $a\ne0$，对任意复数 $\lambda$ 都有
\[
 0\le\|b-\lambda a\|^2.
\]
取 $\lambda=\langle a|b\rangle/\langle a|a\rangle$，余量与 $a$ 正交，且
\[
 0\le\langle b|b\rangle
 -\frac{|\langle a|b\rangle|^2}{\langle a|a\rangle}.
\]
乘以正数 $\langle a|a\rangle$ 即得不等式。等号要求余量为零，
即 $b=\lambda a$；连同零向量情形，等号当且仅当两个向量线性相关。
""")
        text = replace_once(text, r"\begin{advdefinition}{态等价与量子态}", r"\begin{advdefinition}{态等价与纯量子态}")
        text = replace_once(text,
            "代表同一物理态。量子态是非零 Hilbert 向量在此等价关系下的等价类；\n计算时通常选取范数为 $1$ 的代表元。",
            "代表同一纯态。纯量子态是非零 Hilbert 向量在此等价关系下的等价类；\n计算时通常选取范数为 $1$ 的代表元。一般混态需用密度算符描述，不能都表示为单条态矢射线。")
        text = replace_once(text,
            "则 $\\Theta$ 为反幺正，且",
            "若 $\\Theta$ 还把整个空间映满，则称为反幺正；有限维等维情形下满射性由上述保内积条件推出。此时")
        text = replace_once(text,
            "在理想选择性测量中，得到 $A_i$ 后的态为",
            "在理想选择性测量中，对 $p_i>0$ 的实际结果，得到 $A_i$ 后的态为")
        text = replace_between(text,
            r"\begin{advdefinition}{期望值",
            "\n\\begin{advdefinition}{对易子}",
            r"""\begin{advdefinition}{期望值、矩阵元与跃迁振幅}\label{advA6:def:expectation-transition}
归一化态中算符 $A$ 的期望值为 $\langle A\rangle_\psi=\langle\psi|A|\psi\rangle$。
矩阵元 $A_{\phi\psi}=\langle\phi|A|\psi\rangle$ 与 $A$ 具有相同量纲，
不能无条件把它的模方当作跃迁概率。真正的演化振幅是
\[
 \mathcal A_{\psi\to\phi}(t)=\langle\phi|U(t,0)|\psi\rangle,
\]
其中 $U$ 是时间演化算符。对时间无关的 $H_0$ 的不同本征态 $i,f$，
若附加弱扰动 $V(t)$，相互作用表象的一阶振幅为
\[
 c_f^{(1)}(t)=-\frac{\ii}{\hbar}\int_0^t
 \langle f|V(t')|i\rangle\,
 \e^{\ii(E_f-E_i)t'/\hbar}\,\dd t'.
\]
积分和 $1/\hbar$ 使振幅无量纲；在一阶微扰适用且该一阶振幅非零时，$|c_f^{(1)}|^2$ 给出相应跃迁概率的最低非零阶。若一阶振幅被选择定则禁止，则需继续计算高阶项。
\end{advdefinition}
""")
        text = replace_once(text,
            "一组对易可观测量若共同量子数能唯一标记基态，",
            "一组对易可观测量若共同量子数能唯一标记每个共同本征态，")
    elif name == "A6-source-exercises.tex":
        text = replace_once(text,
            "\\figcap{解图：两入射与两出射光子外线及题给角度，内部电子线表示虚传播子。}",
            "\\figcap{解图：出射波矢端点允许面是旋转椭球面；此图为含总波矢 $\\boldsymbol K$ 轴的截面，O与第二焦点的间距为 $k_0$。}")
        text = replace_once(text,
            "图~\\ref{advA6:quality:A6-source-exercises:a3} 中，波矢端点的允许集合由总能量与总三动量共同确定；闭合电子内线不是四个可同时满足正能量壳条件的真实电子，不能把图的顶点当作逐步经典碰撞。",
            "图~\\ref{advA6:quality:A6-source-exercises:a3} 中，O到P及P到第二焦点的两矢量首尾相接为 $\\boldsymbol K$，两段长度之和为 $2k_0$；这同时表达动量守恒与能量守恒，所以允许集合是椭球表面而非内部区域。")
        text = replace_once(text,
            "\\figcap{解图：雷达鼠和电波狗的初始垂直速度及连线，原TikZ图保留。}\\label{advA6:quality:A6-source-exercises:a7}\n\n\\bookcaption{同速追逐的受力方向：力改变动量方向而不改变其大小}\\label{advA6:fig:pursuit-force-solution}",
            "\\figcap{同速追逐的受力方向：力垂直于瞬时速度，改变动量方向而不改变其大小。}\\label{advA6:quality:A6-source-exercises:a7}\\label{advA6:fig:pursuit-force-solution}")
    return text


if __name__ == "__main__":
    for path in sorted((BOOK / "advanced").glob("A*.tex")):
        old = path.read_text()
        new = apply_file_revision(path.name, old)
        if old != new:
            path.write_text(new)
            print(f"final reviewed {path.name}")
