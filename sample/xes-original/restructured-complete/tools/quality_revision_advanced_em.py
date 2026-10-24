"""Editable question/solution illustration overlay for advanced A4 and A6.

This module follows TikZ inputs before deciding whether a figure is absent.
It never changes A1--A3 or shared layout/style files.
"""
from pathlib import Path
import importlib.util
import re
from quality_revision_em_optics import braced, figure, picture_only

BOOK = Path(__file__).resolve().parent.parent
MARKER = "% AdvancedEMQuality20261023"
_spec = importlib.util.spec_from_file_location("advanced_em_illustrations", BOOK / "advanced/quality-20261023-em/illustrations.py")
_data = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_data)


def expand_inputs(text, seen=None):
    seen = set() if seen is None else set(seen)
    def expand(m):
        path = BOOK / m[1]
        if path.suffix != ".tex":
            path = path.with_suffix(".tex")
        if path in seen or not path.exists():
            return m[0]
        return expand_inputs(path.read_text(), seen | {path})
    return re.sub(r"\\input\{([^}]+)\}", expand, text)


def has_diagram(text):
    return r"\begin{tikzpicture}" in expand_inputs(text)


def diagram_caption(text, caption, label):
    # Inputs in these advanced answers are literal diagram assets. Attach the
    # counter at the diagram, before equations alter the current reference.
    ends = [m.end() for m in re.finditer(r"\\end\{tikzpicture\}|\\input\{[^}]+\}", text)]
    if not ends:
        raise ValueError("caption has no TikZ diagram")
    pos = ends[-1]
    return text[:pos] + "\n\\figcap{" + caption + "}\\label{" + label + "}\n" + text[pos:]


def refresh_figures(name, text):
    prefix = f"adv{name.split('-')[0]}:quality:{name}:"
    pattern = (r"\\begin\{center\}\\begin\{minipage\}\{\.96\\linewidth\}\\centering\s*"
               r"(.*?)\\label\{" + re.escape(prefix) + r"([qa])(\d+)\}\s*"
               r"\\end\{minipage\}\\end\{center\}")
    def refresh(m):
        spec = _data.SPECS[name][int(m[3]) - 1]
        role = m[2]
        if role == "q" and spec.get("q") is not None:
            return figure(_data.tikz(spec["q"]), spec["qc"], prefix + "q" + m[3]).strip()
        if role == "a" and "a" in spec:
            return figure(_data.tikz(spec["a"]), spec["ac"], prefix + "a" + m[3]).strip()
        return m[0]
    return re.sub(pattern, refresh, text, flags=re.S)


def keep_heading_with_diagram(text):
    heading = ("\n% EMAdvFigureHeading\n\\raggedright{\\bfseries\\color{DeepBlue}解答}"
               "\\par\\smallskip\\centering\n")
    text = text.replace(heading, "")
    pattern = (r"(?:\\global\\AdvHideHeadingtrue\s*)?\\begin\{advsolution\}"
               r"(\s*\\begin\{center\}\\begin\{minipage\}\{\.96\\linewidth\}\\centering)")
    return re.sub(pattern, lambda m: "\\global\\AdvHideHeadingtrue\n\\begin{advsolution}" + m[1] + heading, text)


def apply_advanced_revision(filename: str, text: str) -> str:
    name = Path(filename).stem
    if name not in _data.SPECS:
        return text
    if MARKER in text:
        return keep_heading_with_diagram(_data.refine_text(name, refresh_figures(name, text)))
    examples = list(re.finditer(r"\\begin\{advexamplebox\}(\{)", text))
    specs = _data.SPECS[name]
    if len(examples) != len(specs):
        raise ValueError(f"{name}: expected {len(specs)} examples, found {len(examples)}")
    for i, m in reversed(list(enumerate(examples, 1))):
        title, pos = braced(text, m.start(1))
        qend = text.index(r"\end{advexamplebox}", pos)
        end = qend + len(r"\end{advexamplebox}")
        q = text[pos:qend]
        a = re.search(r"\\begin\{advsolution\}(.*?)\\end\{advsolution\}", text[end:], re.S)
        if a is None:
            raise ValueError(f"{name} example {i}: no solution")
        answer = a[1]
        gap = text[end:end + a.start()]
        spec = specs[i - 1]
        prefix = f"adv{name.split('-')[0]}:quality:{name}:"
        qlabel, alabel = prefix + f"q{i}", prefix + f"a{i}"
        if has_diagram(q):
            q = diagram_caption(q, spec["qc"], qlabel)
        else:
            q += figure(_data.tikz(spec["q"]), spec["qc"], qlabel)
        if has_diagram(answer):
            answer = diagram_caption(answer, spec["ac"], alabel)
        else:
            payload = _data.tikz(spec["a"]) if "a" in spec else picture_only(expand_inputs(q), {})
            answer = figure(payload, spec["ac"], alabel) + answer
        answer += "\n图~\\ref{" + alabel + "} 中，" + spec["ar"] + "\n"
        replacement = (r"\begin{advexamplebox}{" + title + "}" + q + r"\end{advexamplebox}"
                       + gap + r"\begin{advsolution}" + answer + r"\end{advsolution}")
        text = text[:m.start()] + replacement + text[end + a.end():]
    text = _data.refine_text(name, text)
    return keep_heading_with_diagram(MARKER + "\n" + text)


def main():
    for name in _data.SPECS:
        path = BOOK / "advanced" / (name + ".tex")
        old = path.read_text()
        new = apply_advanced_revision(name, old)
        if new != old:
            path.write_text(new)
            print(f"updated {name}")


if __name__ == "__main__":
    main()
