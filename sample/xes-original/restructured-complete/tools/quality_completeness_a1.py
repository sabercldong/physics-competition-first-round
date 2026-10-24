#!/usr/bin/env python3
"""Add the six A1 completeness proofs after the pre-existing quality overlays."""
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
FILES = ("A1.tex", "A1-rigid.tex", "A1-continuum.tex")
ASSETS = "chapters/completeness-20261024/a1"


def _input(asset: str) -> str:
    return f"% A1CompletenessInput20261024: {asset}\n\\input{{{ASSETS}/{asset}.tex}}\n"


def _span(text: str, start: str, end: str, asset: str, after: int = 0) -> str:
    replacement = _input(asset)
    if replacement in text:
        return text
    a = text.index(start, after)
    b = text.index(end, a)
    return text[:a] + replacement + text[b:]


def _solution_tail(text: str, key: str, start: str, asset: str) -> str:
    if _input(asset) in text:
        return text
    question = text.index(r"\label{advA1:ex:" + key + "}")
    solution = text.index(r"\begin{advsolution}", question)
    return _span(text, start, r"\end{advsolution}", asset, solution)


def apply_file_revision(name: str, text: str) -> str:
    """Pure, idempotent transformation; filenames include their .tex suffix."""
    name = Path(name).name
    if name == "A1.tex":
        old = ("用标准积分\n"
               r"$\frac1{2\pi}\int_{-\pi}^{\pi}\dd k/(a-b\cos k)=1/\sqrt{a^2-b^2}$，得")
        if _input("standard-integral") not in text:
            if text.count(old) != 1:
                raise ValueError("A1 standard-integral anchor missing or not unique")
            text = text.replace(old, _input("standard-integral"), 1)
    elif name == "A1-rigid.tex":
        text = _span(text,
            r"图\ref{advA1:fig:poinsot}(a) 是三维交线的斜投影",
            r"\subsubsection{对称陀螺与章动}", "stability")
    elif name == "A1-continuum.tex":
        old = "周期函数的维廷格不等式给出\n"
        if _input("wirtinger") not in text:
            if text.count(old) != 1:
                raise ValueError("A1 Wirtinger anchor missing or not unique")
            text = text.replace(old, _input("wirtinger"), 1)
        text = _solution_tail(text, "brachistochrone",
            "密度函数不显含 $x$，可用贝尔特拉米恒等式", "brachistochrone")
        text = _solution_tail(text, "minimal-surface", "面积泛函为\n", "minimal-surface")
        text = _span(text,
            r"\begin{advtheorem}{$SO(3)$ 张量积的不可约分解}",
            r"\begin{advexamplebox}{三阶张量的不可约分解计数}", "so3-bridge")
    return text


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="inspect without writing")
    args = parser.parse_args()
    for filename in FILES:
        path = BOOK / "advanced" / filename
        before = path.read_text()
        after = apply_file_revision(filename, before)
        assert apply_file_revision(filename, after) == after
        if before != after:
            if not args.check:
                path.write_text(after)
            print(("pending " if args.check else "revised ") + filename)
        else:
            print("unchanged " + filename)
