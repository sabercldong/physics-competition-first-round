#!/usr/bin/env python3
"""Produce review candidates; source heuristics never certify physics or layout."""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path


def uncomment(text: str) -> str:
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def group(text: str, pos: int) -> tuple[str, int]:
    if pos >= len(text) or text[pos] != "{":
        return "", pos
    depth, start = 1, pos + 1
    pos += 1
    while pos < len(text):
        if text[pos] == "\\":
            pos += 2
            continue
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if not depth:
                return text[start:pos], pos + 1
        pos += 1
    raise ValueError("unbalanced TeX group")


def definitions(text: str) -> dict[str, str]:
    result = {}
    pattern = re.compile(
        r"\\(?:newcommand|renewcommand|providecommand|NewDocumentCommand|RenewDocumentCommand)\*?\s*"
        r"(?:\{(\\[A-Za-z@]+)\}|(\\[A-Za-z@]+))"
    )
    for m in pattern.finditer(text):
        pos = m.end()
        while pos < len(text) and text[pos].isspace():
            pos += 1
        while pos < len(text) and text[pos] == "[":
            end = text.find("]", pos)
            if end < 0:
                break
            pos = end + 1
            while pos < len(text) and text[pos].isspace():
                pos += 1
        body, end = group(text, pos)
        if "DocumentCommand" in m.group(0):
            while end < len(text) and text[end].isspace():
                end += 1
            body, end = group(text, end)
        result[m.group(1) or m.group(2)] = body
    for m in re.finditer(r"\\(?:def|gdef|long\s*\\def)\s*(\\[A-Za-z@]+)[^{]*", text):
        body, _ = group(text, m.end())
        result[m.group(1)] = body
    return result


def drawing_commands(text: str, *, tikz_only: bool = False) -> set[str]:
    defs = definitions(text)
    names = {r"\tikz"} if tikz_only else {r"\includegraphics", r"\tikz", r"\pgfuseimage"}
    # The legacy rigid-body chapter stores editable TikZ by filename and calls
    # it through \csname faithful@#2\endcsname, not through an ordinary macro.
    registered = []
    for match in re.finditer(r"\\registerfaithful\{[^}]+\}\s*", text):
        body, _ = group(text, match.end())
        registered.append(body)
    if registered and all(r"\begin{tikzpicture}" in body for body in registered):
        if "faithful@" in defs.get(r"\sourcefigure", ""):
            names.add(r"\sourcefigure")
    for _ in range(len(defs) + 1):
        added = {
            name for name, body in defs.items()
            if re.search(r"\\begin\{(?:tikzpicture|axis)\}", body)
            or set(re.findall(r"\\[A-Za-z@]+", body)) & names
        }
        if added <= names:
            break
        names |= added
    return names


def has_drawing(text: str, macros: set[str]) -> bool:
    return bool(re.search(r"\\begin\{(?:tikzpicture|axis)\}", text)) or bool(
        set(re.findall(r"\\[A-Za-z@]+", text)) & macros
    )


def reachable_prose(text: str, defs: dict[str, str]) -> str:
    """Inspect called macro bodies without pretending to interpret TeX arguments."""
    bodies, seen = [text], set()
    pending = set(re.findall(r"\\[A-Za-z@]+", text)) & defs.keys()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        body = defs[name]
        bodies.append(body)
        pending |= (set(re.findall(r"\\[A-Za-z@]+", body)) & defs.keys()) - seen
    return "\n".join(bodies)


def source_review(book: Path) -> dict:
    shared = uncomment((book / "style.tex").read_text())
    chapters = []
    issues = []
    files = sorted((book / "generated/chapters").glob("ch*.tex"))
    files += sorted((book / "generated/appendices").glob("*.tex"))
    files += [book / f"advanced/A{i}.tex" for i in range(1, 7)]
    for file in files:
        raw = file.read_text()
        text = uncomment(raw)
        def include(match):
            path = book / match[1]
            if not path.suffix:
                path = path.with_suffix(".tex")
            return uncomment(path.read_text()) if path.exists() else match[0]
        for _ in range(12):
            expanded = re.sub(r"\\input\{([^}]+)\}", include, text)
            if expanded == text:
                break
            text = expanded
        macros = drawing_commands(shared + "\n" + text)
        tikz_macros = drawing_commands(shared + "\n" + text, tikz_only=True)
        defs = definitions(shared + "\n" + text)
        starts = list(re.finditer(r"\\begin\{(origexamplebox|advexamplebox)\}", text))
        examples = []
        for i, start in enumerate(starts):
            stop = starts[i + 1].start() if i + 1 < len(starts) else len(text)
            block = text[start.start():stop]
            title, _ = group(block, len(start[0]))
            question, sep, answer = block.partition("\\end{" + start[1] + "}")
            label = re.search(r"\\label\{([^}]+)\}", question)
            # Include post-answer diagrams, but stop before unrelated theory.
            theory = re.search(r"\\(?:section|subsection)\*?\{", answer)
            if theory:
                answer = answer[:theory.start()]
            # A figure between a problem and its answer does not satisfy the
            # requirement for a figure inside the derivation itself.
            answer = "\n".join(re.findall(
                r"\\begin\{(?:xesolution|advsolution|solutioncontinuation|thinkanswer)\}"
                r"(.*?)\\end\{(?:xesolution|advsolution|solutioncontinuation|thinkanswer)\}",
                answer, re.S))
            prose = reachable_prose(answer, defs)
            entry = {
                "id": f"{file.stem}.{i + 1}", "title": title,
                "label": label[1] if label else None,
                "question_drawing_detected": has_drawing(question, macros),
                "answer_drawing_detected": has_drawing(answer, macros),
                "question_editable_tikz_detected": has_drawing(question, tikz_macros),
                "answer_editable_tikz_detected": has_drawing(answer, tikz_macros),
                "answer_figure_reference": bool(re.search(r"图.{0,12}\\(?:ref|eqref)\{", prose)),
                "answer_han_characters": len(re.findall(r"[\u4e00-\u9fff]", answer)),
            }
            examples.append(entry)
            for field in ["question_drawing_detected", "answer_drawing_detected", "question_editable_tikz_detected", "answer_editable_tikz_detected", "answer_figure_reference"]:
                if not entry[field]:
                    issues.append({"kind": field, "example": entry["id"], "title": title,
                                   "status": "needs_manual_review"})
        terse = []
        headings = list(re.finditer(r"\\(?:subsection|subsubsection)\*?\{", text))
        for i, heading in enumerate(headings):
            title, end = group(text, heading.end() - 1)
            stop = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            block = text[end:stop]
            block = block.split(r"\begin{origexamplebox}")[0]
            han = len(re.findall(r"[\u4e00-\u9fff]", block))
            if han < 100 and (r"\[" in block or r"\begin{equation" in block):
                terse.append({"title": title, "han_characters": han})
        chapters.append({"file": str(file.relative_to(book)), "examples": examples,
                         "drawing_macro_count": len(macros), "terse_theory_candidates": terse,
                         "manual_page_breaks": len(re.findall(r"\\(?:newpage|clearpage|cleardoublepage)\b", text)),
                         "unbreakable_box_override": "breakable/.default=false" in text})
    return {"scope": "32 chapters, appendix E and advanced A1–A6; heuristics require manual confirmation",
            "example_count": sum(len(c["examples"]) for c in chapters),
            "chapters": chapters, "issues": issues}


def pdf_review(path: Path) -> dict:
    import fitz
    pdf = fitz.open(path)
    blank, sparse, outside, orphan_headings = [], [], [], []
    for index, page in enumerate(pdf):
        body = fitz.Rect(35, 65, page.rect.width - 35, page.rect.height - 58)
        text_dict = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)
        spans = [span for block in text_dict["blocks"] if "lines" in block
                 for line in block["lines"] for span in line["spans"]]
        inside = [s for s in spans if fitz.Rect(s["bbox"]).intersects(body)]
        chars = "".join(s["text"] for s in inside).strip()
        image_boxes = [fitz.Rect(b["bbox"]) for b in page.get_image_info()]
        drawings = [d["rect"] for d in page.get_drawings()
                    if d["rect"].intersects(body) and d["rect"].height > 2 and d["rect"].width > 2]
        boxes = [fitz.Rect(s["bbox"]) for s in inside] + image_boxes + drawings
        yend = max((min(b.y1, body.y1) for b in boxes), default=body.y0)
        number = index + 1
        entry = {"pdf_page": number, "body_characters": len(chars),
                 "body_depth_fraction": round((yend - body.y0) / body.height, 3),
                 "preview": chars[:100]}
        if not chars and not image_boxes and not drawings:
            blank.append(entry)
        elif yend < body.y0 + body.height * .35 and index > 1:
            sparse.append(entry)
        if inside:
            last_baseline = max(s["bbox"][1] for s in inside)
            last_line = sorted((s for s in inside if abs(s["bbox"][1] - last_baseline) < 2),
                               key=lambda s: s["bbox"][0])
            last_text = "".join(s["text"] for s in last_line).strip()
            if last_text in {"解答", "解析", "解答（续）", "解答续"}:
                orphan_headings.append({"pdf_page": number, "heading": last_text,
                                        "y": round(last_baseline, 2)})
        for span in spans:
            r = fitz.Rect(span["bbox"])
            if r.x0 < -.5 or r.y0 < -.5 or r.x1 > page.rect.width + .5 or r.y1 > page.rect.height + .5:
                outside.append({"pdf_page": number, "text": span["text"], "bbox": list(r)})
    return {"file": str(path), "pages": len(pdf), "blank_body_pages": blank,
            "sparse_page_candidates": sparse, "text_outside_page": outside,
            "orphan_solution_heading_candidates": orphan_headings,
            "limitations": "Sparse candidates include chapter endings; no automatic overlap or physics certification."}


def figure_reference_review(book: Path, pdf: Path) -> dict:
    """Check references against TeX's actual counters, including caption scope."""
    aux, recorder = pdf.with_suffix(".aux"), pdf.with_suffix(".fls")
    if not aux.exists() or not recorder.exists():
        return {"available": False, "reason": "Compile with -recorder and retain aux beside PDF."}
    labels = {}
    text = aux.read_text()
    for match in re.finditer(r"\\newlabel\{([^}]+)\}", text):
        body, _ = group(text, match.end())
        fields, pos = [], 0
        while pos < len(body) and body[pos] == "{":
            field, pos = group(body, pos)
            fields.append(field)
        if len(fields) >= 4:
            labels[match[1]] = fields
    refs, inputs = set(), set()
    for line in recorder.read_text().splitlines():
        if line.startswith("INPUT "):
            path = Path(line[6:])
            path = path if path.is_absolute() else book / path
            if path.suffix == ".tex" and path.exists() and path.resolve().is_relative_to(book.resolve()):
                inputs.add(path.resolve())
    for path in inputs:
        refs.update(re.findall(r"图\s*~?\s*\\ref\{([^}#]+)\}", uncomment(path.read_text())))
    wrong = [{"label": key, "display": labels[key][0], "anchor": labels[key][3]}
             for key in sorted(refs) if key in labels and not labels[key][3].startswith("figure.")]
    mismatches = []
    for key in sorted(refs):
        if key not in labels or not labels[key][3].startswith("figure."):
            continue
        display, anchor = labels[key][0], labels[key][3][7:]
        advanced = re.fullmatch(r"adv(A[1-6])\.figure\.(\d+)", anchor)
        expected = advanced[1] + "." + advanced[2] if advanced else anchor
        if display != expected:
            mismatches.append({"label": key, "display": display, "expected": expected})
    return {"available": True, "literal_figure_references_checked": len(refs),
            "missing_labels": sorted(refs - labels.keys()), "wrong_counter_anchors": wrong,
            "display_anchor_mismatches": mismatches,
            "limitations": "Literal figure references in active sources; parameterized macro references are checked through the compiled unresolved-reference log."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = source_review(args.book)
    (args.output / "source-review.json").write_text(json.dumps(source, ensure_ascii=False, indent=2))
    counts = collections.Counter(i["kind"] for i in source["issues"])
    print(json.dumps({"source_examples": source["example_count"], "manual_review_candidates": counts}, ensure_ascii=False))
    if args.pdf:
        report = pdf_review(args.pdf)
        (args.output / "pdf-review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(json.dumps({"pdf_pages": report["pages"], "blank_pages": len(report["blank_body_pages"]),
                          "sparse_candidates": len(report["sparse_page_candidates"]),
                          "outside_page_text": len(report["text_outside_page"])}))
        references = figure_reference_review(args.book, args.pdf)
        (args.output / "figure-reference-review.json").write_text(json.dumps(references,ensure_ascii=False,indent=2))
        print(json.dumps({"figure_reference_review": references}, ensure_ascii=False))


if __name__ == "__main__":
    main()
