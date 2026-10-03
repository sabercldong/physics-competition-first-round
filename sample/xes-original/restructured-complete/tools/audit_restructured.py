#!/usr/bin/env python3
"""Machine-check the invariant parts of the restructured first-round book.

This audit complements, but does not replace, visual review.  It checks source
hashes, required source-example mappings, global TeX labels and references,
forbidden editorial traces, independent-chapter tail occupancy, and the
top-level outline of the compiled complete book.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "generated"

REQUIRED_SOURCE_EXAMPLES = {
    "k02": 21, "k03": 10, "k04": 14, "k05": 14, "k06": 13,
    "k07": 16, "k08": 5, "k09": 3, "k10": 5, "k11": 8,
    "s38": 17, "s39": 9, "s40": 21, "s41": 0,
    "s42": 13, "s43": 9, "s44": 13, "s45": 10,
}

CHAPTER_MINIMUMS = {
    18: {"examples": 7, "figures": 4},
    25: {"examples": 8, "figures": 8},
    26: {"examples": 5},
    30: {"added_examples": 4},
    31: {"examples": 8, "figures": 6},
    32: {"examples": 12, "figures": 8},
}

FORBIDDEN = re.compile(
    r"学习目标|本节目标|本节小结|标校|能量账本|原讲义|原扫描|原始扫描|"
    r"重新绘制|重绘|重新创作|题源说明|扫描页|原资料|无法求解|条件不足|"
    r"原图缺失|新版|旧版|新稿|旧稿|为了排版|原图|原题|扫描件|题目页|nature science|nature philosophy"
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_hashes() -> list[dict]:
    rows = []
    for item in load_json(ROOT / "audit" / "source-register.json")["sources"]:
        path = Path(item["path"])
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        rows.append({
            "id": item["id"], "path": item["path"],
            "expected_sha256": item["sha256"], "actual_sha256": actual,
            "ok": actual == item["sha256"],
        })
    return rows


def source_example_counts() -> list[dict]:
    found = collections.Counter()
    for chapter in load_json(GENERATED / "source-map.json")["chapters"]:
        for source_map in chapter["source_number_maps"]:
            found[source_map["source"]] += sum(
                obj["source_kind"] == "ex" for obj in source_map["objects"]
            )
    return [
        {"source": source, "expected": expected, "actual": found[source],
         "ok": found[source] == expected}
        for source, expected in REQUIRED_SOURCE_EXAMPLES.items()
    ]


def tex_integrity() -> dict:
    labels, refs, traces = [], [], []
    example_counts = {}
    solution_counts = {}
    figure_counts = {}
    for path in sorted((GENERATED / "chapters").glob("ch*.tex")):
        text = path.read_text(encoding="utf-8")
        example_counts[path.stem] = len(re.findall(r"\\begin\{origexamplebox\}", text))
        solution_counts[path.stem] = len(re.findall(r"\\begin\{xesolution\}", text))
        figure_counts[path.stem] = len(re.findall(
            r"\\(?:figcap|bookcaption|diagramcaption|historyfigure|sourceimage)\b", text
        ))
        labels.extend(re.findall(r"\\label\{([^}]+)\}", text))
        refs.extend(re.findall(r"\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}", text))
        traces.extend({"file": str(path.relative_to(ROOT)), "text": m.group(0)}
                      for m in FORBIDDEN.finditer(text))
    counts = collections.Counter(labels)
    duplicates = sorted(label for label, count in counts.items() if count > 1)
    missing = sorted(set(refs) - set(labels))
    pairing_errors = [
        {"chapter": key, "examples": value, "solutions": solution_counts[key]}
        for key, value in example_counts.items() if solution_counts[key] != value
    ]
    minimum_checks = []
    for chapter, required in CHAPTER_MINIMUMS.items():
        key = f"ch{chapter:02d}"
        row = {
            "chapter": chapter,
            "examples": example_counts.get(key, 0),
            "figures": figure_counts.get(key, 0),
        }
        checks = []
        if "examples" in required:
            checks.append(row["examples"] >= required["examples"])
        if "figures" in required:
            checks.append(row["figures"] >= required["figures"])
        # Chapter 30 already contains the retained diffraction examples; the
        # new polarization source must contribute at least four more.
        if "added_examples" in required:
            source = ROOT / "chapters" / "new" / "ch30-polarization.tex"
            added = len(re.findall(r"\\begin\{origexamplebox\}", source.read_text(encoding="utf-8")))
            row["added_examples"] = added
            checks.append(added >= required["added_examples"])
        row["ok"] = all(checks)
        minimum_checks.append(row)
    return {
        "chapter_example_counts": example_counts,
        "chapter_solution_counts": solution_counts,
        "chapter_figure_counts": figure_counts,
        "example_solution_pairing_errors": pairing_errors,
        "chapter_minimum_checks": minimum_checks,
        "labels": len(labels), "unique_labels": len(counts),
        "duplicate_labels": duplicates, "references": len(refs),
        "missing_references": missing, "forbidden_editorial_traces": traces,
        "ok": (not duplicates and not missing and not traces and not pairing_errors
               and all(row["ok"] for row in minimum_checks)),
    }


def tail_occupancy() -> list[dict]:
    rows = []
    for chapter in range(1, 33):
        path = ROOT / "build" / "chapters" / f"ch{chapter:02d}" / f"ch{chapter:02d}.pdf"
        doc = fitz.open(path)
        page = doc[-1]
        height = page.rect.height
        body = [block for block in page.get_text("blocks")
                if block[1] >= 65 and block[3] <= height - 55 and block[4].strip()]
        bottom = max((block[3] for block in body), default=65)
        fraction = (bottom - 65) / (height - 120)
        rows.append({
            "chapter": chapter, "pages": len(doc),
            "last_page_body_fraction": round(fraction, 4),
            "ok": fraction >= 0.39,
        })
    return rows


def outline() -> dict:
    path = Path("/tmp/xes-main-outlines-v2.json")
    data = load_json(path)["outlines"]
    titles = [item["title"] for item in data]
    pages = [item["destpageposfrom1"] for item in data]
    return {
        "top_level_count": len(data), "titles": titles, "pages": pages,
        "expected": "32 chapters plus one unnumbered symbol index",
        "ok": len(data) == 33 and all(b > a for a, b in zip(pages, pages[1:])),
    }


def main() -> None:
    report = {
        "source_hashes": source_hashes(),
        "required_source_example_counts": source_example_counts(),
        "declared_migrations": [{
            "source": "s44 example 21.2", "destination": "s45 synthetic source number 22.0",
            "reason": "The problem uses the single-slit diffraction formula and belongs in chapter 30.",
        }],
        "tex_integrity": tex_integrity(),
        "chapter_tail_occupancy": tail_occupancy(),
        "complete_book_outline": outline(),
    }
    report["ok"] = (
        all(row["ok"] for row in report["source_hashes"])
        and all(row["ok"] for row in report["required_source_example_counts"])
        and report["tex_integrity"]["ok"]
        and all(row["ok"] for row in report["chapter_tail_occupancy"])
        and report["complete_book_outline"]["ok"]
    )
    target = GENERATED / "audit-book.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)
    print("PASS" if report["ok"] else "FAIL")
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
