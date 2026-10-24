#!/usr/bin/env python3
"""Replay the five thermal/field completeness repairs after older overlays.

Editable content and TikZ are independent input files, so regenerated older
answers can be replaced without copying or overwriting unrelated chapters.
"""
from pathlib import Path
import argparse

PREFIX = "chapters/completeness-20261024/thermal-fields/"


def _input(name: str) -> str:
    return rf"\input{{{PREFIX}{name}.tex}}"


def _replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise ValueError(f"Completeness anchor missing or ambiguous: {old[:100]!r}")
    return text.replace(old, new, 1)


def _answer(text: str, label: str, name: str) -> str:
    replacement = _input(name)
    if replacement in text:
        return text
    example = text.index(r"\label{" + label + "}")
    start = text.index(r"\begin{advsolution}", example) + len(r"\begin{advsolution}")
    end = text.index(r"\end{advsolution}", start)
    return text[:start] + "\n" + replacement + "\n" + text[end:]


def apply_file_revision(name: str, text: str) -> str:
    """Apply only to the named advanced source; accept paths or .tex names."""
    name = Path(name).stem
    if name == "A2-statistics":
        return _answer(text, "advA2:ex:fermi-heat-capacity", "fermi-sommerfeld")
    if name == "A2":
        replacement = _input("gl-functional")
        if replacement not in text:
            lead = "在共存点序参量从0跳到"
            start = text.index(lead, text.index(r"\label{advA2:ex:landau-first-order}"))
            keep = text.index("有下界。", start) + len("有下界。")
            end = text.index(r"\end{advsolution}", keep)
            text = text[:keep] + "\n\n" + replacement + "\n" + text[end:]
        return text
    if name == "A3-pde":
        text = _replace_once(
            text,
            "这个谱定理保证后面的模态展开不是形式猜测。正则问题的一维本征空间来自二阶方程的 Wronskian 与两端边界条件；离散性和完备性可由自伴算符的 Green 函数是紧算符来证明。",
            _input("sl-spectrum-proof"),
        )
        new_definition = _input("associated-definition")
        if new_definition not in text:
            marker = r"\label{advA3:ex:associated-legendre}"
            example = text.rfind(r"\begin{advexamplebox}", 0, text.index(marker))
            start = text.rfind("这里的 $l,m$ 均为整数", 0, example)
            if start < 0:
                raise ValueError("Independent negative-order definition anchor missing")
            text = text[:start] + new_definition + "\n\n" + text[example:]
        return _answer(text, "advA3:ex:associated-legendre", "associated-proof")
    return text


def apply_appendix_revision(text: str) -> str:
    replacement = _input("two-spheres-derivation")
    if replacement in text:
        return text
    heading = r"\subsection{两等势导体球的有限间距推广}"
    start = text.index(heading) + len(heading)
    end = text.index(r"\endgroup", start)
    return text[:start] + "\n\n" + replacement + "\n\n" + text[end:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report stale inputs without writing")
    args = parser.parse_args()
    book = Path(__file__).resolve().parents[1]
    entries = [
        (book / "advanced" / name, lambda t, name=name: apply_file_revision(name, t))
        for name in ["A2.tex", "A2-statistics.tex", "A3-pde.tex"]
    ]
    entries.append((book / "generated/appendices/appendix-e.tex", apply_appendix_revision))
    changed = []
    for path, fn in entries:
        before = path.read_text()
        after = fn(before)
        if fn(after) != after:
            raise AssertionError(f"Non-idempotent completeness overlay: {path}")
        if after != before:
            changed.append(path)
            if not args.check:
                path.write_text(after)
            print(path.relative_to(book))
    if args.check and changed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
