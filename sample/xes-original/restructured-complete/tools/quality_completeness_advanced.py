#!/usr/bin/env python3
"""Expand the audited A5/A6 knowledge blocks and keep the cover undated."""
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]


def section_input(text, heading, following, source):
    start = text.index(heading)
    end = text.index(following, start + len(heading))
    replacement = heading + "\n\n" + r"\input{" + source + "}\n\n"
    return text[:start] + replacement + text[end:]


def apply_file_revision(name, text):
    prefix = "chapters/completeness-20261024/advanced/"
    if name == "A5-wave.tex":
        text = section_input(text, r"\subsection{偏振密度矩阵}",
                             r"\subsection{晶体光学}", prefix + "polarization-matrix.tex")
    elif name == "A6-relativity.tex":
        text = section_input(text, r"\subsection{常见四矢量与相对论动力学}",
                             r"\begin{advexamplebox}{加速杆的收缩率、本征加速度与信号频移}",
                             prefix + "four-vectors.tex")
    elif name == "A6-quantum-mechanics.tex":
        text = section_input(text, r"\subsection{Schrödinger 方程与定态问题}",
                             r"\begin{advexamplebox}{球形禁闭、动能下界与氢原子稳定性}",
                             prefix + "schrodinger-states.tex")
    elif name == "main.tex":
        text = text.replace("  \\vspace{1.2em}\n  {\\Large 2026年10月24日\\par}\n", "")
    return text


if __name__ == "__main__":
    for rel in ["advanced/A5-wave.tex", "advanced/A6-relativity.tex",
                "advanced/A6-quantum-mechanics.tex", "main.tex"]:
        path = BOOK / rel
        old = path.read_text()
        new = apply_file_revision(path.name, old)
        if old != new:
            path.write_text(new)
            print(f"completeness revised {rel}")
