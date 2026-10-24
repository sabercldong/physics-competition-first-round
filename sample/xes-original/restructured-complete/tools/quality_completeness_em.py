"""Reproducible teaching-completeness additions, applied after older overlays.

Only A4 and chapters 31/32 are owned here.  Stable input markers make these
additions idempotent without altering public layout or rebuilding other units.
"""
from pathlib import Path


PREFIX = "chapters/completeness-20261024/em/"


def _include(stem):
    return "% CompletenessEM:" + stem + "\n\\input{" + PREFIX + stem + ".tex}\n"


def _insert_before(text, anchor, stem):
    if "% CompletenessEM:" + stem in text:
        return text
    if text.count(anchor) != 1:
        raise ValueError(f"expected one anchor for {stem}, found {text.count(anchor)}")
    return text.replace(anchor, _include(stem) + "\n" + anchor, 1)


def _replace_range(text, start, stop, stem):
    if "% CompletenessEM:" + stem in text:
        return text
    a = text.find(start)
    if a < 0:
        raise ValueError(f"start anchor missing for {stem}")
    b = text.find(stop, a)
    if b < 0:
        raise ValueError(f"end anchor missing for {stem}")
    return text[:a] + _include(stem) + "\n" + text[b:]


def apply_file_revision(name, text):
    """Apply to the named advanced fragment (filename including .tex)."""
    name = Path(name).name
    if name == "A4-electrostatics.tex":
        text = _insert_before(text, "先构造接地球的像系：", "a4-dipole-construction")
        text = _insert_before(text, "固定偶极矩大小和空间方向求", "a4-dipole-field-force")
        text = _replace_range(text, "扁旋转椭球取极半轴", "最后用互易定理。", "a4-oblate")
        text = text.replace("最后用互易定理。令状态1为外点电荷",
                            "最后用互易定理回到长旋转椭球情形（$A>B$、$c=\\sqrt{A^2-B^2}$）。令状态1为外点电荷", 1)
        text = _replace_range(text, "Neumann Green 函数取常数法向导数",
                              r"\begin{advtheorem}{静电 Green 函数的对称性}", "a4-neumann")
    elif name == "A4-magnetostatics.tex":
        # Preserve the subsection and all original problem/solution figures.
        start = "磁化强度 $\\vect M$ 等效为束缚电流"
        text = _replace_range(text, start, r"\begin{advexamplebox}{均匀磁化球的内外磁场}",
                              "a4-magnetic-medium")
        old = "对场点求梯度并用 Stokes 定理，可得"
        if "% CompletenessEM:a4-loop-stokes" not in text:
            if text.count(old) != 1:
                raise ValueError("loop Stokes anchor not unique")
            text = text.replace(old, _include("a4-loop-stokes"), 1)
        text = _insert_before(text, "三个正交圆柱公共区域的体积为", "a4-triple-volume")
    elif name == "A4-waves.tex":
        text = _replace_range(text, "Helmholtz 方程和波动方程的外向 Green 函数分别为",
                              r"\begin{advexamplebox}{电偶极辐射与 Larmor 公式}", "a4-retarded")
        old = "只保留 $1/r$ 辐射项，"
        if "% CompletenessEM:a4-radiation-bridge" not in text:
            if text.count(old) != 1:
                raise ValueError("radiation bridge anchor not unique")
            text = text.replace(old, _include("a4-radiation-bridge"), 1)
    return text


def apply_chapter_revision(number, text):
    """Apply to current generated chapters or their persistent authored source."""
    if number == 31:
        text = _replace_range(text, "同样的变换也适用于电荷与电流。",
                              r"\end{starread}", "ch31-current-force")
    elif number == 32:
        text = _replace_range(text, "自旋是粒子的内禀角动量，",
                              r"\end{starread}", "ch32-spin-pauli")
        stem = "ch32-neutrinos-particles"
        if "% CompletenessEM:" + stem not in text:
            heading = r"\subsection{中微子与粒子物理概览}"
            a = text.find(heading)
            if a < 0:
                raise ValueError("neutrino subsection missing")
            a += len(heading)
            # Authored source ends at this subsection; generated source has a
            # closing bookmark/group tail that must remain in place.
            b = text.find(r"\hypersetup{bookmarksdepth=2}", a)
            if b < 0:
                b = len(text)
            text = text[:a] + "\n\n" + _include(stem) + "\n" + text[b:]
    return text


def main():
    root = Path(__file__).resolve().parents[1]
    targets = [(root / "advanced" / name, lambda s, n=name: apply_file_revision(n, s))
               for name in ("A4-electrostatics.tex", "A4-magnetostatics.tex", "A4-waves.tex")]
    for n, name in ((31, "ch31-relativity.tex"), (32, "ch32-modern.tex")):
        for path in (root / "generated/chapters" / f"ch{n}.tex", root / "chapters/new" / name):
            targets.append((path, lambda s, n=n: apply_chapter_revision(n, s)))
    for path, apply in targets:
        original = path.read_text()
        revised = apply(original)
        if apply(revised) != revised:
            raise AssertionError(f"non-idempotent result for {path}")
        if revised != original:
            path.write_text(revised)
            print(path.relative_to(root))


if __name__ == "__main__":
    main()
