"""Reproducible question/solution illustration audit for chapters 21--32.

The handwritten TikZ fragments in the sibling data module depict the actual
question conditions. Legacy solution figures are retained, including physical
corrections made in the previous optical and electromagnetic reviews. No source
figure is copied with its old label. The overlay is safe to call repeatedly.
"""
from pathlib import Path
import argparse
import importlib.util
import re

BOOK = Path(__file__).resolve().parent.parent
MARKER = "% EMOpticsQuality20261023"
DATA_PATH = BOOK / "chapters/quality-20261023/em-optics/illustrations.py"
_spec = importlib.util.spec_from_file_location("em_optics_illustrations", DATA_PATH)
_data = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_data)


def braced(text, pos):
    """Return a TeX braced argument and its exclusive end position."""
    if text[pos] != "{":
        raise ValueError("expected a braced TeX argument")
    depth = 1
    j = pos + 1
    while depth:
        if text[j] == "{" and text[j - 1] != "\\":
            depth += 1
        elif text[j] == "}" and text[j - 1] != "\\":
            depth -= 1
        j += 1
    return text[pos + 1:j - 1], j


def macro_bodies(text):
    result = {}
    for m in re.finditer(r"\\(?:newcommand|renewcommand|providecommand)\{\\([A-Za-z]+)\}(?:\s*\[[^\]]*\]){0,2}\s*(\{)", text):
        result[m[1]] = braced(text, m.start(2))[0]
    return result


def has_figure(text, bodies, seen=None):
    if r"\begin{tikzpicture}" in text or r"\begin{axis}" in text:
        return True
    seen = set() if seen is None else set(seen)
    for name in re.findall(r"\\([A-Za-z]+)", text):
        if name in bodies and name not in seen:
            if has_figure(bodies[name], bodies, seen | {name}):
                return True
    return False


def picture_only(text, bodies):
    """Extract genuine geometry; expand one no-argument figure macro if needed."""
    start = text.find(r"\begin{tikzpicture}")
    if start >= 0:
        end = text.index(r"\end{tikzpicture}", start) + len(r"\end{tikzpicture}")
        return text[start:end]
    for macro in re.finditer(r"\\([A-Za-z]+)", text):
        name = macro[1]
        if name in bodies and has_figure(bodies[name], bodies):
            body = bodies[name]
            pos = macro.end()
            if "#1" in body and pos < len(text) and text[pos] == "{":
                arg, _ = braced(text, pos)
                body = body.replace("#1", arg)
            return picture_only(body, bodies)
    raise ValueError("cannot extract an editable TikZ picture")


def figure(picture, caption, label):
    picture = re.sub(r"\\label\{[^}]*\}", "", picture)
    return ("\n\\begin{center}\\begin{minipage}{.96\\linewidth}\\centering\n"
            + picture + "\n\\figcap{" + caption + "}\\label{" + label + "}\n"
            + "\\end{minipage}\\end{center}\n")


def attach_figure_label(answer, bodies, label):
    """Keep the label inside a real caption, including legacy figure macros."""
    captions = list(re.finditer(r"\\(?:figcap|diagramcaption)\s*(\{)", answer))
    if captions:
        pos = braced(answer, captions[-1].start(1))[1] - 1
        return answer[:pos] + r"\label{" + label + "}" + answer[pos:]
    macros = [m for m in re.finditer(r"\\([A-Za-z]+)", answer)
              if m[1] in bodies and has_figure(bodies[m[1]], bodies)]
    if not macros:
        raise ValueError("figure label has no caption or figure macro")
    macro = macros[-1]
    body = bodies[macro[1]]
    end = macro.end()
    if "#1" in body and end < len(answer) and answer[end] == "{":
        arg, end = braced(answer, end)
        body = body.replace("#1", arg)
    captions = {
        "ch22:quality:a4": "裂变产物的共同轨道、反向碰撞与碰后圆心。",
        "ch22:quality:a5": "近轴螺旋束的含轴投影与屏上聚焦条件。",
        "ch22:quality:a6": "磁场中的圆桶碰撞：两圆交点与相邻碰撞的固定转角。",
        "ch22:quality:a7": "交叉场速度选择器中的电力与磁力方向。",
        "ch22:quality:a8": "从正极板静止释放的摆线轨迹与最大横向位移。",
        "ch22:quality:a9": "重力与磁场共同作用下的回旋漂移及地面边界。",
        "ch22:quality:a10": "交替电场、磁场层中的连续轨迹与跨界速度。",
        "ch22:quality:a11": "霍尔电荷分离、横向电场与电压正方向。",
        "ch22:quality:a12": "科尔比诺圆环中的径向电流及方位漂移。",
        "ch22:quality:a13": "圆轨道的微小径向扰动与相对原圆心的周期。",
        "ch22:quality:a14": "径向电场与轴向磁场共同决定的圆轨道及扰动。",
        "ch22:quality:a15": "线性阻尼下的磁场螺旋轨迹与有限收敛点。",
        "ch22:quality:a16": "交叉场和阻尼共同决定的稳态漂移方向。",
        "ch22:quality:a17": "回旋磁矩方向与缓变磁场中的磁镜运动。",
    }
    if label not in captions:
        raise ValueError(f"uncaptioned legacy figure needs a specific caption: {label}")
    caption = "\n\\figcap{" + captions[label] + r"\label{" + label + "}}\n"
    # Expand only this invocation. Keep the old macro's drawing and explanatory
    # text, and put its caption before the innermost figure group closes.
    for closing in (r"\end{rTwoFigure}", r"\end{minipage}", r"\end{center}"):
        pos = body.rfind(closing)
        if pos >= 0:
            body = body[:pos] + caption + body[pos:]
            break
    else:
        body += caption
    return answer[:macro.start()] + body + answer[end:]


def repair_existing_labels(number, text):
    bodies = macro_bodies(text)
    def repair(m):
        answer = m[1]
        labels = re.findall(r"\\label\{(ch\d+:quality:a\d+)\}", answer)
        for label in labels:
            label_pos = answer.index(r"\label{" + label + "}")
            caption_spans = [(c.start(1), braced(answer, c.start(1))[1])
                             for c in re.finditer(r"\\(?:figcap|diagramcaption)\s*(\{)", answer)]
            if any(start < label_pos < end for start, end in caption_spans):
                continue
            answer = answer.replace(r"\label{" + label + "}", "", 1)
            answer = attach_figure_label(answer, bodies, label)
        return r"\begin{xesolution}" + answer + r"\end{xesolution}"
    return re.sub(r"\\begin\{xesolution\}(.*?)\\end\{xesolution\}", repair, text, flags=re.S)


def normalize_caption_labels(number, text):
    """The caption's local counter must still be active when writing a label."""
    captions = list(re.finditer(r"\\(?:figcap|diagramcaption)\s*(\{)", text))
    for match in reversed(captions):
        _, end = braced(text, match.start(1))
        labels = re.match(r"\s*((?:\\label\{ch" + str(number) + r":[^}]+\}\s*)+)", text[end:])
        if labels:
            label_pattern = r"\\label\{ch" + str(number) + r":[^}]+\}"
            commands = "".join(re.findall(label_pattern, labels[0]))
            whitespace = re.sub(label_pattern, "", labels[0])
            text = text[:end - 1] + commands + "}" + whitespace + text[end + labels.end():]
    return text


def refresh_inserted_figures(number, text):
    """Permit correction of a handwritten figure without double insertion."""
    bodies = macro_bodies(text)
    pattern = (r"\\begin\{center\}\\begin\{minipage\}\{\.96\\linewidth\}\\centering\s*"
               r"(.*?)\\label\{ch" + str(number) + r":quality:([qa])(\d+)\}\}?\s*"
               r"\\end\{minipage\}\\end\{center\}")
    def refresh(m):
        role, i = m[2], int(m[3])
        spec = _data.SPECS.get((number, i), {})
        label = f"ch{number}:quality:{role}{i}"
        if role == "q" and "q" in spec:
            return figure(_data.tikz(spec["q"]), spec["qc"], label).strip()
        if role == "a" and "a" in spec:
            return figure(_data.tikz(spec["a"]), spec.get("ac", "解图：本题条件的分解与计算所用几何。"), label).strip()
        if role == "a" and "a_macro" in spec:
            return figure(picture_only(bodies[spec["a_macro"]], bodies), spec["ac"], label).strip()
        if role == "a" and "q" in spec:
            return figure(_data.tikz(spec["q"]), spec.get("ac", "解图：本题条件的分解与计算所用几何。"), label).strip()
        return m[0]
    return re.sub(pattern, refresh, text, flags=re.S)


def add_notes(number, text):
    theory = BOOK / f"chapters/quality-20261023/em-optics/ch{number}-notes.tex"
    insertion = "\n\\input{chapters/quality-20261023/em-optics/" + theory.name + "}\n"
    if theory.exists() and insertion not in text:
        end = text.rfind(r"\endgroup")
        return text[:end] + insertion + text[end:]
    return text


def ensure_figure_references(number, text):
    bodies = macro_bodies(text)
    matches = list(re.finditer(r"\\begin\{origexamplebox\}\{([^}]*)\}(.*?)\\end\{origexamplebox\}", text, re.S))
    for i, m in reversed(list(enumerate(matches, 1))):
        a = re.search(r"\\begin\{xesolution\}(.*?)\\end\{xesolution\}", text[m.end():], re.S)
        answer = a[1]
        if re.search(r"\\ref\{[^}]*(?::fig:|:quality:[qa])[^}]*\}", answer):
            continue
        spec = _data.SPECS.get((number, i), {})
        if "ar" not in spec:
            continue
        label = f"ch{number}:quality:a{i}"
        answer = attach_figure_label(answer, bodies, label)
        answer += "\n图~\\ref{" + label + "} 中，" + spec["ar"] + "\n"
        start, end = m.end() + a.start(), m.end() + a.end()
        text = text[:start] + r"\begin{xesolution}" + answer + r"\end{xesolution}" + text[end:]
    return text


def editorial_fixes(number, text):
    if number == 21:
        text = text.replace("有一个正四面体框架的电阻网络，每条边电阻为 $R$，试求任意两点间的等效电阻。", "有一个正四面体框架的电阻网络，每条边电阻为 $R$，试求任意两顶点间的等效电阻。")
    if number == 24:
        text = text.replace("两只电压表的引线与圆环组成不同闭合路径", "各电压表的引线与圆环组成不同闭合路径")
    if number == 28:
        text = re.sub(r"图\s*~?\s*(\\ref\{ch28:ex:s43-20-3\})", r"例~\1", text)
    if number == 31:
        text = text.replace(r"\begingroup\tcbset{breakable/.default=true}\begin{starread}", r"\begingroup\tcbset{breakable/.default=true,after={\par\smallskip\penalty0}}\begin{starread}")
        anchor = "对一个封闭粒子系，令总四动量为"
        if "% EMSpacetimeBoxSplit" not in text:
            text = text.replace(anchor, "% EMSpacetimeBoxSplit\n\\end{starread}\\par\\penalty0\n\\begin{starread}{系统不变质量与四电流}\n" + anchor, 1)
    return text


def apply_chapter_revision(number: int, text: str) -> str:
    if number not in range(21, 33):
        return text
    text = editorial_fixes(number, text)
    if MARKER in text:
        revised = add_notes(number, ensure_figure_references(number, refresh_inserted_figures(number, repair_existing_labels(number, text))))
        return normalize_caption_labels(number, revised)
    bodies = macro_bodies(text)
    examples = list(re.finditer(r"\\begin\{origexamplebox\}\{([^}]*)\}(.*?)\\end\{origexamplebox\}", text, re.S))
    expected = {21: 18, 22: 17, 23: 9, 24: 21, 25: 8, 26: 5,
                27: 15, 28: 11, 29: 14, 30: 17, 31: 8, 32: 12}
    if len(examples) != expected[number]:
        raise ValueError(f"chapter {number}: expected {expected[number]} base examples, found {len(examples)}")
    for i, m in reversed(list(enumerate(examples, 1))):
        match = re.search(r"\\begin\{xesolution\}(.*?)\\end\{xesolution\}", text[m.end():], re.S)
        if match is None:
            raise ValueError(f"chapter {number} example {i}: no solution")
        answer_start = m.end() + match.start()
        answer_end = m.end() + match.end()
        question = m[2]
        answer = match[1]
        gap = text[m.end():answer_start]
        key = number, i
        qlabel = f"ch{number}:quality:q{i}"
        alabel = f"ch{number}:quality:a{i}"
        spec = _data.SPECS.get(key, {})
        # Several old chapters placed the only solution drawing in the gap
        # between the question and the solution. Put it into the solution.
        if has_figure(gap, bodies):
            answer = gap + answer
            gap = "\n"
        if not has_figure(question, bodies):
            if "q" not in spec:
                raise ValueError(f"chapter {number} example {i}: missing question geometry")
            question += figure(_data.tikz(spec["q"]), spec["qc"], qlabel)
        # A short, correct answer may reuse the condition geometry. Its
        # caption and accompanying explanation identify the actual operation
        # on that geometry; no decorative decision/flow chart is inserted.
        if not has_figure(answer, bodies):
            if "a_macro" in spec:
                picture = picture_only(bodies[spec["a_macro"]], bodies)
            elif "a" in spec:
                picture = _data.tikz(spec["a"])
            else:
                picture = picture_only(question, bodies)
            answer = figure(picture, spec.get("ac", "解图：本题条件的分解与计算所用几何。"), alabel) + answer
            if "ar" not in spec:
                raise ValueError(f"chapter {number} example {i}: missing diagram-based explanation")
            answer += "\n图~\\ref{" + alabel + "} 中，" + spec["ar"] + "\n"
        # Existing drawings generally have a precise explanatory reference;
        # when that was absent, attach a stable label and explicit reference.
        elif r"\ref{" not in answer and "ar" in spec:
            answer = attach_figure_label(answer, bodies, alabel)
            answer += "\n图~\\ref{" + alabel + "} 中，" + spec["ar"] + "\n"
        replacement = (r"\begin{origexamplebox}{" + m[1] + "}" + question
                       + r"\end{origexamplebox}" + gap
                       + r"\begin{xesolution}" + answer + r"\end{xesolution}")
        text = text[:m.start()] + replacement + text[answer_end:]
    if number == 32:
        # The question's Wien peak is 500 nm, so the main curve must be at
        # 5796 K. Both curves retain the same absolute Planck radiance scale.
        text = text.replace("T=4000,6000 K", "T=4000,5796 K")
        text = text.replace("14387.77/(6000*x)", "14387.77/(5796*x)")
        text = text.replace(r"\addlegendentry{$6000\,\mathrm K$}", r"\addlegendentry{$5796\,\mathrm K$}")
        text = text.replace(".48296203365,0)--(axis cs:.48296203365,10.0053244776", ".4999606953,0)--(axis cs:.4999606953,8.41620919")
        text = text.replace("黑体单色辐出度随温度的变化：升温后总面积增大，峰值向短波移动。", "本题主曲线为 $5796\\,\\mathrm K$，谱峰在 $500\\,\\mathrm{nm}$；$4000\\,\\mathrm K$ 虚线仅作同绝对刻度的对照。")
    return normalize_caption_labels(number, add_notes(number, ensure_figure_references(number, MARKER + "\n" + text)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("chapters", nargs="*", type=int, default=list(range(21, 33)))
    args = parser.parse_args()
    for number in args.chapters:
        path = BOOK / f"generated/chapters/ch{number:02d}.tex"
        old = path.read_text()
        new = apply_chapter_revision(number, old)
        if new != old:
            path.write_text(new)
            print(f"updated ch{number:02d}")


if __name__ == "__main__":
    main()
