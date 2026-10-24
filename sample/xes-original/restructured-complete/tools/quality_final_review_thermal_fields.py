#!/usr/bin/env python3
"""Idempotent, narrowly scoped corrections from the 2026-10-24 cross review.

The root generator may call the three apply_* functions.  The CLI applies only
this reviewer's chapters, appendix and advanced units, preserving all other work.
"""
from pathlib import Path


def _replace(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise ValueError(f"Review anchor not found: {old[:100]!r}")
    if text.count(old) != 1:
        raise ValueError(f"Review anchor is ambiguous: {old[:100]!r}")
    return text.replace(old, new, 1)


def apply_chapter_revision(number: int, text: str) -> str:
    if number == 15:
        text = text.replace("\\begin{figure}[htbp]\n\\centering\n\\stellarInteriorRevision", "\\begin{figure}[!t]\n\\centering\n\\stellarInteriorRevision")
        text = _replace(text,
            r"""\par\noindent\begin{minipage}{\linewidth}
\stellarInteriorRevision
\diagramcaption{太阳与红巨星的内部剖面及表面对流细节。箭头表示对流区物质的循环运动；两星大小与内部层厚不按同一比例。}\label{ch15:fig:s29-20-3}
\end{minipage}\par\medskip""",
            r"""\begin{figure}[!t]
\centering
\stellarInteriorRevision
\diagramcaption{太阳与红巨星的内部剖面及表面对流细节。箭头表示对流区物质的循环运动；两星大小与内部层厚不按同一比例。}\label{ch15:fig:s29-20-3}
\end{figure}""")
    elif number == 20:
        text = _replace(text,
            r"\figcap{相切等势双球的逐次电像构造。}\label{ch20:quality:analysis-12}",
            r"\figcap{相切等势双球的逐次电像构造；两列交错符号的像电荷向接触点聚集。}\label{ch20:quality:analysis-12}")
        # This second caption belonged to the very same picture and had no label.
        text = text.replace(r"\diagramcaption{解图：相切双球的像电荷序列。两列交错符号的像电荷向接触点聚集。}" + "\n", "")
        text = _replace(text,
            "两问均用电容器内的电场 $E$ 表示结果。",
            r"两问均用电容器内的电场 $E$ 表示结果。在 $a,b\gg d$ 且 $x,a-x\gg d$ 的内部插入区间求主阶结果，忽略边缘效应对总电容的修正。")
        text = _replace(text,
            "忽略边缘场。插入部分与未插入部分共享相同板间电压，因此",
            "忽略边缘效应对总电容的修正。插入部分与未插入部分共享相同板间电压，因此")
        text = _replace(text,
            "遗漏电源做功，会错误地得到相反的力。",
            "遗漏电源做功，会错误地得到相反的力。微观上，吸入力来自介质前缘附近的非均匀边缘场；上面的电容近似只省略它对总电容的高阶修正，不能据此把局部边缘场也删去。")
    elif number == 24:
        lead = (r"先由整个线框的变化磁通求环流，再按图~\ref{ch24:fig:review-squarevoltmetersdiagram-1}中各电压表与被测边围成的路径求读数。解图~\ref{ch24:quality:a14}保留四个接点，便于逐边检查欧姆压降。" + "\n\n")
        if lead not in text:
            start = text.index(r"\label{ch24:ex:s40-9-14}")
            start = text.index(r"\begin{xesolution}", start) + len(r"\begin{xesolution}")
            text = text[:start] + "\n" + lead + text[start:]
        text = _replace(text,
            r"\figcap{解图：本题条件的分解与计算所用几何。\label{ch24:quality:a10}}",
            r"\figcap{解图：带电小环的切向、径向基矢与支持力正方向；图示 $\theta=0$。\label{ch24:quality:a10}}")
        text = _replace(text,
            r"图~\ref{ch24:quality:a10} 中，环内变化磁通产生的切向感生电场沿整个带电环做功；用 $\oint E_t\,\mathrm dl=-\mathrm d\Phi/\mathrm dt$ 才能建立角加速度方程。",
            r"图~\ref{ch24:quality:a10} 中，带电小环是沿固定大圆轨道滑动的质点。先对半径 $R$ 的圆周使用法拉第定律，由对称性求出小环所在处的 $E_\theta$；再把局部切向电力 $qE_\theta$ 代入 $mR\ddot\theta=qE_\theta$。大环只提供径向约束，不能把它误当成整体带电的受力环。")
    return text


def apply_advanced_revision(name: str, text: str) -> str:
    name = Path(name).stem
    if name == "A2":
        text = _replace(text, "\\qquad b>0.\n", "\\qquad a>0,\quad b>0.\n")
        old = r"""$T<T_c$ 时平衡序参量为
$\phi_\pm=\pm\sqrt{-a(T-T_c)/(2b)}$。熵与热容分别为
\[
 S=-\left(\frac{\partial F}{\partial T}\right)_\phi,
 \qquad C=T\left(\frac{\partial S}{\partial T}\right),
\]
从而在平均场近似中热容出现有限跃变
$\Delta C=a^2T_c/(2b)$。"""
        new = r"""$T<T_c$ 时平衡序参量为
$\phi_\pm=\pm\sqrt{-a(T-T_c)/(2b)}$。先对每个温度极小化，得到
\[
 F_{\rm eq}(T)=F_0(T)-\frac{a^2(T-T_c)^2}{4b}\quad(T<T_c),
 \qquad F_{\rm eq}(T)=F_0(T)\quad(T\ge T_c).
\]
平衡熵和热容应沿这条极小值支求导：
\[
 S_{\rm eq}=-\frac{\dd F_{\rm eq}}{\dd T},
 \qquad C_{\rm eq}=-T\frac{\dd^2F_{\rm eq}}{\dd T^2}.
\]
因此熵在 $T_c$ 连续，而低温侧相对于高温侧的热容跃变量为
$\Delta C=a^2T_c/(2b)$。若在求第二次温度导数时错误地固定 $\phi$，就会漏掉平衡序参量随温度改变的贡献。"""
        text = _replace(text, old, new)
    elif name == "A3-vector":
        text = _replace(text,
            r"$\vect e'_i=M_i{}^j\vect e_j$，同一个几何矢量的分量必须反向变化，",
            r"$\vect e'_i=\vect e_jM^j{}_i$，其中矩阵 $M$ 的第 $i$ 列为新基矢 $\vect e'_i$ 在旧基中的分量。同一个几何矢量的坐标列必须满足 $x=Mx'$，因而反向变化，")
        text = _replace(text,
            r"$c_{12}(u^av_a)=u^au_a$，二阶张量的缩并是迹。",
            r"对未缩并的二阶张量 $T^a{}_b=u^av_b$，有 $c_{12}T=T^a{}_a=u^av_a=\vect u\cdot\vect v$。二阶混合张量的缩并就是迹，不能把原来两个不同矢量误写成同一矢量的模平方。")
        text = _replace(text,
            "在星形区域上，外导数满足 $\\dd^2=0$；每个闭微分形式局部都是恰当形式。特别地",
            "外导数恒满足 $\\dd^2=0$。在星形区域上，每个次数 $k\\ge1$ 的闭微分形式都是恰当形式；对一般区域，这一结论局部成立。零次闭形式只是局部常数，不属于上述正次数结论。特别地")
    elif name == "A3-pde":
        text = _replace(text,
            "或周期边界条件 $y(a)=y(b),\\ p(a)y'(a)=p(b)y'(b)$ 下的非零解。使非零解存在的 $\\lambda$ 称本征值，相应的 $y$ 称本征函数。无穷区间还要求 $\\int |y|^2\\rho\\dd x<\\infty$。",
            "或周期边界条件 $y(a)=y(b),\\ p(a)y'(a)=p(b)y'(b)$ 下的非零解。分离边界条件的各对系数须为不同时为零的实数。使非零解存在的 $\\lambda$ 称本征值，相应的 $y$ 称本征函数。奇异端点和无穷端点还须指定自伴定义域；平方可积性是要求之一，不能代替所有必要的端点条件。")
        text = _replace(text,
            "分离边界条件在每个端点都把 $f,f'$ 与 $g,g'$ 限制为同一线性关系，因此括号为零；周期边界条件下两端贡献相消。奇异端点（例如 Legendre 的 $x=\\pm1$）由 $p=0$ 消去边界项；无穷端点则由平方可积性和允许的衰减条件消去边界项，故式(A3.1)右端为零。",
            "实系数分离边界条件在每个正则端点都把 $f,f'$ 与 $g,g'$ 限制为同一线性关系，因此括号为零；周期边界条件下两端贡献相消。奇异端点须在指定的自伴定义域中取极限，不能仅因 $p\\to0$ 就断言乘积为零。例如 Legendre 多项式采用端点正则分支，满足 $pf',pg'\\to0$ 且 $f,g$ 有界，边界型才消失；若允许平方可积的对数发散支，这一结论不再自动成立。无穷端点也须由所选定义域的衰减条件保证边界型消失。因此式(A3.1)在这些端点条件下为零。")
        text = _replace(text,
            r"令 $k=2\sqrt\varepsilon,u$，",
            r"令 $k=2\sqrt{\varepsilon}\,u$，")
        text = _replace(text,
            r"\qquad |m|\le l.",
            r"\qquad 0\le m\le l.")
        # The later completeness layer replaces only this historical paragraph
        # with an independent endpoint normalization. Keep all other fixes live.
        if r"\input{chapters/completeness-20261024/thermal-fields/associated-definition.tex}" not in text:
            text = _replace(text,
                "这里采用含 Condon--Shortley 相位 $(-1)^m$ 的现代约定；若去掉该相位，下面负阶公式中的相应符号也要同步改变。",
                "这里的 $l,m$ 均为整数，导数定义先用于 $0\\le m\\le l$；负阶由下题关系延拓。采用含 Condon--Shortley 相位 $(-1)^m$ 的现代约定；若去掉该相位，下面负阶公式中的相应符号也要同步改变。")
    return text


def apply_appendix_revision(text: str) -> str:
    return _replace(text,
        "忽略边缘场，已填充区域与真空区域相当于并联：",
        "在薄间隙、介质前缘远离极板两端的内部插入区间，忽略边缘效应对总电容的高阶修正，已填充区域与真空区域相当于并联：")


def main() -> None:
    book = Path(__file__).resolve().parents[1]
    entries = [(book / f"generated/chapters/ch{n:02}.tex", lambda t, n=n: apply_chapter_revision(n, t)) for n in [15, 20, 24]]
    entries += [(book / "advanced" / f"{n}.tex", lambda t, n=n: apply_advanced_revision(n, t)) for n in ["A2", "A3-vector", "A3-pde"]]
    entries += [(book / "generated/appendices/appendix-e.tex", apply_appendix_revision)]
    for path, fn in entries:
        old = path.read_text()
        new = fn(old)
        assert fn(new) == new, path
        if new != old:
            path.write_text(new)
            print(path.relative_to(book))


if __name__ == "__main__":
    main()
