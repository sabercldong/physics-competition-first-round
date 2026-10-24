"""Idempotent, independently checked final corrections for chapters 1--12 and A1."""
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
FREQUENCY_CAPTION = "一个周期内的高度—时间图。除最高点和碰撞点外，同一高度对应下降、上升两个相位；二者只有在图示特殊位置才相差半周期。"


def apply_chapter_revision(number: int, text: str) -> str:
    if number == 1:
        text = text.replace(
            "这说明连续函数在某点附近的函数值变化量，近似正比于自变量的变化量，比例系数就是\n函数在该点的导数。",
            "这说明可导函数在该点附近满足 $\\Delta f=f'(x_0)\\Delta x+o(\\Delta x)$；\n在一阶近似下，函数增量与自变量增量成正比，比例系数为该点的导数。")
    if number == 2:
        text = text.replace(
            r"\figcap{本题解答中的位置、分量与辅助量。}\label{mech:legacy:ch02:k02-2-21}",
            "\\figcap{" + FREQUENCY_CAPTION + r"}\label{mech:legacy:ch02:k02-2-21}")
        text = text.replace(
            "\\end{qualityfigure}\n\\figcap{" + FREQUENCY_CAPTION + "}\n\\end{center}",
            "\\end{qualityfigure}\n\\end{center}")
    if number == 3:
        text = text.replace(
            "判断质点是“加速”还是“减速”要看 $\\vect a$ 在 $\\vect v$ 方向上的投影：$\\vect a\\cdot\\vect v>0$ 时速率增加，$<0$ 时速率减小，等于零时加速度只改变方向。",
            "当 $\\vect v\\ne\\vect0$ 时，判断质点是“加速”还是“减速”要看 $\\vect a$ 在 $\\vect v$ 方向上的投影：由 $\\dd v/\\dd t=(\\vect a\\cdot\\vect v)/v$，内积大于零时速率增加，小于零时速率减小，等于零时瞬时速率变化率为零，非零加速度只有法向分量。在瞬时静止处速度方向未定，不能根据内积为零断言“只改变方向”；例如由静止做匀加速直线运动，初始内积虽为零，随后速率仍增加。")
    if number == 5:
        text = text.replace("\\clearpage\n\\subsection{重力}", "\\subsection{重力}")
    if number == 12:
        text = text.replace(
            r"P=Tk\omega A^2\sin^2(kx-\omega t)>0",
            r"P=Tk\omega A^2\sin^2(kx-\omega t)\ge0")
    return text


def apply_advanced_revision(name: str, text: str) -> str:
    """Apply only the confirmed corrections belonging to the A1 cross-review."""
    name = Path(name).name
    if name == "A1.tex":
        text = text.replace(
            "第二式左边每项均为加速度；若漏掉 $r\\ddot\\theta$ 中的 $r$，量纲会立即失配。",
            "第二式括号内每项均为加速度；乘以质量 $m$ 后与右端力同量纲。若漏掉 $r\\ddot\\theta$ 中的 $r$，量纲会立即失配。")
        text = text.replace(
            "当等号成立时二阶恢复力消失，必须保留四阶项；超过阈值时最低点变为不稳定点。",
            "当 $|J|/I=\\sqrt{g/a}$ 时二阶恢复力消失，但有效势的首个非零增量为\n"
            "\\[\n U_{\\rm eff}(\\theta)-U_{\\rm eff}(0)\n"
            " =mga\\left(\\frac18+\\frac{ma^2}{2I}\\right)\\theta^4+\\order{\\theta^6}>0\n\\]\n"
            "（充分小的非零 $\\theta$），所以最低点仍为稳定平衡，只是线性小振动频率为零，有限小振幅的周期须由非线性项决定。"
            "因此稳定范围含等号；上式严格不等号对应非零的线性回复频率。超过阈值时最低点变为不稳定点。")
        text = text.replace(
            "对地球上的傅科摆，若将当地竖直方向的地球自转分量记为 $\\Omega_E\\sin\\lambda$，则上式的速度耦合系数是\n"
            "$\\Omega=2\\Omega_E\\sin\\lambda$，所以进动角速度是 $\\Omega_E\\sin\\lambda$。",
            "对地球上的傅科摆，取 $x$ 向东、$y$ 向北、竖直向上为正，地球自转的竖直分量为 $\\Omega_E\\sin\\lambda$。"
            "科里奥利力的水平分量为 $F_x=2m\\Omega_E\\sin\\lambda\\,\\dot y$、$F_y=-2m\\Omega_E\\sin\\lambda\\,\\dot x$，"
            "故按本节的力和复坐标约定，应代入\n"
            "$\\Omega=-2\\Omega_E\\sin\\lambda$，振动平面的有符号进动角速度为 $-\\Omega_E\\sin\\lambda$；"
            "北半球从上方看为顺时针，进动速率的大小为 $|\\Omega_E\\sin\\lambda|$。")
    if name == "A1-rigid.tex":
        text = text.replace(
            "所以刚体上的点在刚体坐标中满足 $\\vect v=\\vect\\omega\\times\\vect r$。",
            "所以刚体上固定材料点的惯性系速度在刚体系中的分量满足\n"
            "\\[\n \\vect v_{\\rm body}=\\mathsf A^{\\mathsf T}\\dot{\\vect R}\n"
            " =\\vect\\omega\\times\\vect r.\n\\]\n"
            "这里 $\\vect\\omega$ 也取刚体系分量；材料点相对刚体坐标的速度 $\\dot{\\vect r}$ 则为零，不能与 $\\vect v_{\\rm body}$ 混同。")
        text = text.replace(
            "稳定无章动还要求 $V_{\\rm eff}''(\\theta_0)>0$；若小于零，则微小扰动指数增长。",
            "具有非零线性回复频率的稳定无章动要求 $V_{\\rm eff}''(\\theta_0)>0$；若小于零，则微小扰动指数增长。"
            "若等于零，线性化不能判定稳定性，须继续检查有效势的高阶项；正四次项仍可给出稳定平衡。")
        text = text.replace(
            "它要求 $\\omega^2\\ge8g/(3\\sqrt3\\,l)$。",
            "非竖直支要求 $\\omega^2>8g/(3\\sqrt3\\,l)$；等号时 $\\phi=0$，该支与竖直支重合，不能再视为非竖直定常解。")
    if name == "A1-continuum.tex":
        text = text.replace(
            "流体没有由静态形变直接决定的恢复应力，其应力取决于形变速率，并且常与热学自由度耦合。因此用欧拉描述：速度、密度、压强和温度是空间与时间的场",
            "流体在静止时不能维持剪切应力，但仍有各向同性压强；压强由密度、温度等状态量决定，黏滞应力则与形变速率有关。以下采用欧拉描述：速度、密度、压强和温度是空间与时间的场")
        text = text.replace("忽略全部黏滞偏应力，即", "忽略全部黏滞应力，即")
        text = text.replace(
            "(2) 对不可压缩理想流体，证明即使不使用准静态绝热条件，也有",
            "(2) 仍取定常流动，对密度处处相同的不可压缩理想流体，证明即使不使用准静态绝热条件，也有")
        text = text.replace(
            "(2) 不可压缩欧拉方程是",
            "(2) 在定常、密度处处相同的条件下，不可压缩欧拉方程是")
        text = text.replace(
            "其时间分量是能量密度与能流，空间分量是动量密度与动量流。",
            "$\\nu=0$ 对应能量密度与能流；空间平移给出正则动量流。须注意，这里的“动量”取决于被平移的坐标。"
            "对于用材料坐标描述的弹性棒，$\\mathcal L=\\rho\\xi_t^2/2-E\\xi_x^2/2$，上述空间坐标平移给出"
            "$T^0{}_1=\\rho\\xi_t\\xi_x$，是正则动量（也称伪动量）密度；真实机械动量密度为 $\\rho\\xi_t$，由下题的位移场平移 $\\xi\\mapsto\\xi+\\varepsilon$ 产生。二者不能直接等同。")
        # Place the annulus solution figure where its boundary data enter the
        # flux integral, instead of leaving a nearly empty final figure page.
        label = r"\label{advA1:fig:falling-cylinder}"
        start_marker = r"\begin{center}\begin{minipage}{\linewidth}\centering"
        if label in text and "环隙中箭头标明的是向上净回流" not in text:
            label_at = text.index(label)
            start = text.rfind(start_marker, 0, label_at)
            end_marker = r"\end{minipage}\end{center}"
            end = text.index(end_marker, label_at) + len(end_marker)
            old_after = "\n图\\ref{advA1:fig:falling-cylinder}明确画出 $r<R$、共轴和侧面环隙；液体在环隙内向上净回流，端部局部损失按长环隙近似忽略。"
            if text[end:].startswith(old_after):
                end += len(old_after)
            figure = text[start:text.index(end_marker, label_at) + len(end_marker)]
            figure = figure.replace(
                r"\draw[<->,TextGray] (-.75,1.38)--(.75,1.38)",
                r"\foreach\xx in{-1.50,1.55}{\draw[->,DeepBlue,thick](\xx,-.95)--(\xx,.35);}" + "\n"
                + r"\draw[->,TextGray](-2.45,1)--(-2.45,-1.1) node[below]{$z$};" + "\n"
                + r"\node[TextGray,font=\scriptsize] at(-1.45,.68){净回流};" + "\n"
                + r"\draw[<->,TextGray] (-.75,1.38)--(.75,1.38)")
            figure += "\n图\\ref{advA1:fig:falling-cylinder}中，$z$ 向下；环隙中箭头标明的是向上净回流，靠内壁的液体仍满足 $u(r)=v>0$，外壁处 $u(R)=0$。因此整体通量为负，而不能把整个环隙的 $u(s)$ 都取为负。\n"
            text = text[:start] + text[end:]
            anchor = "圆柱每秒排开 $\\pi r^2v$ 的液体，故环隙必须向上回流："
            text = text.replace(anchor, figure + anchor)
    return text


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapters", nargs="*", type=int, default=list(range(1, 13)))
    parser.add_argument("--advanced", action="store_true", help="also apply A1 cross-review fixes")
    arguments = parser.parse_args()
    for number in arguments.chapters:
        path = BOOK / "generated/chapters" / f"ch{number:02d}.tex"
        before = path.read_text()
        after = apply_chapter_revision(number, before)
        if before != after:
            path.write_text(after)
            print(f"revised ch{number:02d}")
    if arguments.advanced:
        for name in ("A1.tex", "A1-rigid.tex", "A1-continuum.tex"):
            path = BOOK / "advanced" / name
            before = path.read_text()
            after = apply_advanced_revision(name, before)
            if before != after:
                path.write_text(after)
                print(f"revised {name}")
