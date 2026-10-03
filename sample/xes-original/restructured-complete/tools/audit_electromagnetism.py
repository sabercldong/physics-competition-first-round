#!/usr/bin/env python3
"""Compare the 2019-autumn and 2020-spring electromagnetism TeX sources.

The report is deliberately conservative: it never decides that a source block
may be dropped merely because its heading is similar.  It records the best
textual match and leaves low-similarity items in the ``unique_candidates``
list for manual physics review.
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

from build_restructured import LegacyUnit, balanced_argument, extract_legacy

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent


OLD = {
    19: [
        LegacyUnit("s18", "eighteenth-section", "电场的基本性质"),
        LegacyUnit("s19", "nineteenth-section", "电势能与电势"),
    ],
    20: [
        LegacyUnit("s20", "twentieth-section", "静电平衡"),
        LegacyUnit("s21", "twenty-first-section", "电介质与电容器"),
    ],
    21: [
        LegacyUnit("s22", "twenty-second-section", "恒定电流"),
        LegacyUnit("s23", "twenty-third-section", "复杂电阻网络"),
    ],
    22: [LegacyUnit("s24", "twenty-fourth-section", "洛伦兹力")],
    23: [LegacyUnit("s25", "twenty-fifth-section", "安培力与安培定律")],
    24: [LegacyUnit("s26", "twenty-sixth-section", "电磁感应")],
    26: [LegacyUnit("s27", "twenty-seventh-section", "电磁场与超导体")],
}

NEW = {
    19: [
        LegacyUnit("s32", "thirty-second-section", "电场的基本性质"),
        LegacyUnit("s33", "thirty-third-section", "电势能与电势"),
    ],
    20: [
        LegacyUnit("s34", "thirty-fourth-section", "静电平衡"),
        LegacyUnit("s35", "thirty-fifth-section", "电介质与电容器"),
    ],
    21: [
        LegacyUnit("s36", "thirty-sixth-section", "恒定电流"),
        LegacyUnit("s37", "thirty-seventh-section", "复杂电阻网络"),
    ],
    22: [LegacyUnit("s38", "thirty-eighth-section", "洛伦兹力")],
    23: [LegacyUnit("s39", "thirty-ninth-section", "安培力与安培定律")],
    24: [LegacyUnit("s40", "fortieth-section", "电磁感应")],
    26: [LegacyUnit("s41", "forty-first-section", "电磁场与超导体")],
}


def normalize(tex: str) -> str:
    tex = re.sub(r"%[^\n]*", "", tex)
    tex = re.sub(r"\\(?:label|ref|eqref|pageref|autoref)\{[^}]*\}", "", tex)
    tex = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", "", tex)
    tex = tex.replace("{", "").replace("}", "")
    tex = re.sub(r"\s+", "", tex)
    return tex


def macro_blocks(tex: str, environment: str) -> list[dict[str, str]]:
    begin = "\\begin{" + environment + "}"
    end_marker = "\\end{" + environment + "}"
    blocks: list[dict[str, str]] = []
    pos = 0
    while True:
        idx = tex.find(begin, pos)
        if idx < 0:
            break
        brace = idx + len(begin)
        while brace < len(tex) and tex[brace].isspace():
            brace += 1
        title = ""
        body_start = brace
        if brace < len(tex) and tex[brace] == "{":
            title, body_start = balanced_argument(tex, brace)
        end = tex.find(end_marker, body_start)
        if end < 0:
            break
        body = tex[body_start:end]
        blocks.append({"title": title.strip(), "text": body.strip(), "normalized": normalize(title + body)})
        pos = end + len(end_marker)
    return blocks


def headings(tex: str) -> list[str]:
    result: list[str] = []
    for macro in ("section", "subsection", "subsubsection", "paragraph"):
        for match in re.finditer(r"\\" + macro + r"\*?\s*\{", tex):
            try:
                value, _ = balanced_argument(tex, match.end() - 1)
            except ValueError:
                continue
            value = normalize(value)
            if value:
                result.append(value)
    return result


def figures(tex: str) -> list[str]:
    values = []
    for macro in ("diagramcaption", "figcap", "origcaption", "bookcaption"):
        for match in re.finditer(r"\\" + macro + r"\s*\{", tex):
            try:
                value, _ = balanced_argument(tex, match.end() - 1)
            except ValueError:
                continue
            values.append(value.strip())
    return values


def collect(units: list[LegacyUnit], chapter: int) -> dict:
    payload = {"units": [], "examples": [], "headings": [], "figures": []}
    for unit in units:
        tex, _ = extract_legacy(unit, chapter)
        payload["units"].append(unit.key)
        for example in macro_blocks(tex, "origexamplebox"):
            example["source"] = unit.key
            payload["examples"].append(example)
        payload["headings"].extend({"source": unit.key, "text": value} for value in headings(tex))
        payload["figures"].extend({"source": unit.key, "text": value} for value in figures(tex))
    return payload


def best_match(item: dict, candidates: list[dict]) -> dict:
    best = {"ratio": 0.0, "source": "", "title": ""}
    for candidate in candidates:
        ratio = difflib.SequenceMatcher(None, item["normalized"], candidate["normalized"]).ratio()
        if ratio > best["ratio"]:
            best = {"ratio": round(ratio, 4), "source": candidate["source"], "title": candidate["title"]}
    return best


def main() -> None:
    report = {"policy": {"duplicate_threshold": 0.82, "manual_review_threshold": 0.55}, "chapters": []}
    for chapter in sorted(OLD):
        old = collect(OLD[chapter], chapter)
        new = collect(NEW[chapter], chapter)
        comparison = []
        for item in old["examples"]:
            match = best_match(item, new["examples"])
            status = "probable_duplicate" if match["ratio"] >= 0.82 else (
                "manual_review" if match["ratio"] >= 0.55 else "unique_candidate"
            )
            comparison.append({
                "source": item["source"], "title": item["title"],
                "normalized_length": len(item["normalized"]),
                "best_2020_match": match, "status": status,
            })
        report["chapters"].append({
            "chapter": chapter,
            "old_units": old["units"], "new_units": new["units"],
            "counts": {
                "old_examples": len(old["examples"]), "new_examples": len(new["examples"]),
                "old_figures": len(old["figures"]), "new_figures": len(new["figures"]),
                "old_headings": len(old["headings"]), "new_headings": len(new["headings"]),
            },
            "example_comparison": comparison,
            "old_headings": old["headings"], "new_headings": new["headings"],
            "old_figures": old["figures"], "new_figures": new["figures"],
        })
    target = BOOK / "generated" / "audit-electromagnetism.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)
    for chapter in report["chapters"]:
        statuses = [item["status"] for item in chapter["example_comparison"]]
        print(chapter["chapter"], chapter["counts"], {name: statuses.count(name) for name in sorted(set(statuses))})


if __name__ == "__main__":
    main()
