#!/usr/bin/env python3
"""Regenerate only chapter 3 from its maintained sources, leaving other chapters intact."""
import argparse
import json
import os
from pathlib import Path
import build_restructured as book


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile", action="store_true")
    args = parser.parse_args()
    number = 3
    spec = book.CHAPTERS[number]
    parts = [f"\\chapter{{{spec['title']}}}\n"]
    maps = []
    for unit in spec["legacy"]:
        rendered, objects = book.extract_legacy(unit, number)
        parts.append(rendered)
        maps.append({"source": unit.key, "objects": objects})
    text = book.normalize_visible_eponyms("\n".join(parts))
    assert text.count(r"\begin{origexamplebox}") == 51
    assert text.count(r"\begin{xesolution}") == 51
    target = book.GENERATED / "chapters/ch03.tex"
    target.write_text(text, encoding="utf-8")
    source_map = book.GENERATED / "source-map.json"
    mapping = json.loads(source_map.read_text())
    chapter = next(x for x in mapping["chapters"] if x["chapter"] == 3)
    chapter["source_number_maps"] = maps
    source_map.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    wrapper = book.GENERATED / "wrappers/chapters/ch03.tex"
    wrapper_text = book._wrapper(f"第3章　{spec['title']}", [3], toc=False)
    wrapper_text = wrapper_text.replace("（含解答与解图）", "")
    wrapper_text = wrapper_text.replace(r"{\color{TextGray}含完整解答与解图\par}", "")
    wrapper.write_text(wrapper_text, encoding="utf-8")
    print("Regenerated chapter 3 only: 51 examples and 51 solutions.")
    if args.compile:
        os.environ["TEXINPUTS"] = str(book.BOOK) + "//:" + os.environ.get("TEXINPUTS", "")
        book.compile_tex(wrapper, book.BOOK / "build/review-ch03-20260904")


if __name__ == "__main__":
    main()
