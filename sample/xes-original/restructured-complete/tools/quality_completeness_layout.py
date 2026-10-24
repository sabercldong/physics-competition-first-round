#!/usr/bin/env python3
"""Balance chapter endings at complete reasoning steps; do not shrink body text."""
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]


def keep_tail(text, anchor, fraction, key):
    marker = f"% CompletenessTail20261024 {key}"
    if marker in text:
        return text
    if text.count(anchor) != 1:
        raise ValueError(f"Tail anchor not unique: {key}")
    block = marker + "\n" + rf"\par\Needspace{{{fraction}\textheight}}" + "\n"
    return text.replace(anchor, block + anchor, 1)


def apply_chapter_revision(number, text):
    if number == 8:
        text = text.replace("% CompletenessTail20261024 ch08-collision-and-summary\n"
                            + r"\par\Needspace{.67\textheight}" + "\n", "")
        return keep_tail(text, "以“子弹+木块”为系统。碰撞时间内水平外力冲量可忽略，所以水平动量守恒。设碰后共同速度为 $v$，",
                         ".60", "ch08-collision-calculation-and-summary")
    if number == 14:
        return keep_tail(text, r"三次项 $\lambda<0$ 使势阱右缓左陡。热膨胀所需的是平均间距，",
                         ".70", "ch14-statistical-average")
    if number == 19:
        return keep_tail(text, r"\textbf{2. 卢瑟福微分截面。}", ".60", "ch19-cross-section")
    return text


def apply_file_revision(name, text):
    if name == "A4-electrostatics.tex":
        old = r"""\draw[thick] (0,0) circle (1);\fill (0,0) circle (1.3pt) node[below]{$O$};
\draw[->] (0,0)--(0,1) node[midway,left]{$R$};
\fill (2.8,0) circle (1.8pt) node[below]{$\boldsymbol r_0$};\draw[dashed] (0,0)--(2.8,0);

\fill[DeepBlue] (.36,0) circle (1.8pt) node[above]{$q',\boldsymbol p'$};\fill[DeepBlue] (0,0) circle (2pt) node[below]{$q_0=-q'$};
\draw[DeepBlue,->] (2.8,0)--(3.5,.7) node[right]{$\boldsymbol p$};\node[below] at (1,-.6){像点 $b=R^2/a$；像系不是真实球内电荷};"""
        new = r"""% CompletenessFigure20261024 dipole-image-labels
\draw[thick] (0,0) circle (1);
\draw[->] (0,0)--(-.707,.707) node[midway,below left]{$R$};
\fill (2.8,0) circle (1.8pt) node[below]{$\boldsymbol r_0$};
\draw[dashed] (0,0)--(2.8,0);
\fill[DeepBlue] (0,0) circle (2pt) node[below]{$O$};
\draw[TextGray,thin] (0,0)--(-.55,-.6)--(-1.10,-.6);
\node[left,DeepBlue] at (-1.10,-.6) {$q_0=-q'$};
\fill[DeepBlue] (.36,0) circle (1.8pt);
\draw[TextGray,thin] (.36,0)--(.65,.65)--(1.15,.65);
\node[right,DeepBlue] at (1.15,.65) {$q',\boldsymbol p'$};
\draw[DeepBlue,->] (2.8,0)--(3.5,.7) node[right]{$\boldsymbol p$};
\node at (1.9,-.65) {$b=R^2/a$};"""
        if old in text:
            return text.replace(old, new, 1)
        if "CompletenessFigure20261024 dipole-image-labels" not in text:
            raise ValueError("Dipole image label block missing")
        return text
    if name == "A1-continuum.tex":
        return keep_tail(text, r"图\ref{advA1:fig:falling-cylinder}中，$z$ 向下；",
                         ".60", "a1-annular-flow-calculation")
    if name == "ch21-conduction-devices.tex":
        text = text.replace("% CompletenessTail20261024 ch21-diode-model\n"
                            + r"\par\Needspace{.85\textheight}" + "\n", "")
        return keep_tail(text, r"\begin{origexamplebox}{二极管的工作状态与负载线}",
                         ".75", "ch21-diode-example")
    if name == "main.tex":
        text = text.replace(r"\input{frontmatter/reading-guide.tex}" + "\n", "")
        start = text.find(r"\bookmarksetup{startatroot}" + "\n" + r"\backmatter")
        if start >= 0:
            end = text.index(r"\end{document}", start)
            text = text[:start] + "% CompletenessNotationMoved20261024\n" + text[end:]
        return text
    return text


if __name__ == "__main__":
    for number in [8, 14, 19]:
        path = BOOK / f"generated/chapters/ch{number:02d}.tex"
        old = path.read_text()
        new = apply_chapter_revision(number, old)
        if old != new:
            path.write_text(new)
            print(f"balanced {path.relative_to(BOOK)}")
    for rel in ["advanced/A1-continuum.tex", "advanced/A4-electrostatics.tex",
                "chapters/quality-20261023/ch21-conduction-devices.tex",
                "main.tex"]:
        path = BOOK / rel
        old = path.read_text()
        new = apply_file_revision(path.name, old)
        if old != new:
            path.write_text(new)
            print(f"balanced {rel}")
