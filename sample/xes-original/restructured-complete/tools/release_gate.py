#!/usr/bin/env python3
"""Fail closed until every promised final-delivery invariant is satisfied."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "generated"

ADVANCED_EXPECTED = {
    "A1": {"examples": 42, "definitions": 18, "theorems": 25},
    "A2": {"examples": 27, "definitions": 3, "theorems": 8},
    "A3": {"examples": 23, "definitions": 16, "theorems": 21},
    "A4": {"examples": 27, "definitions": 1, "theorems": 13},
    "A5": {"examples": 11, "supplemental_examples": 4, "definitions": 0, "theorems": 4},
    # Keep the 18 advanced-source examples; add 16 separately mapped spring exercises.
    "A6": {"examples": 18, "supplemental_examples": 16, "definitions": 10, "theorems": 6},
}


def expanded_tex(path: Path, seen: set[Path] | None = None) -> str:
    """Read a TeX unit together with project-local ``\\input`` children."""
    seen = set() if seen is None else seen
    resolved = path.resolve()
    if resolved in seen:
        return ""
    seen.add(resolved)
    text = path.read_text(encoding="utf-8")
    chunks = [text]
    for raw_child in re.findall(r"\\input\{([^}]+)\}", text):
        child = ROOT / raw_child
        if child.suffix == "":
            child = child.with_suffix(".tex")
        if child.exists():
            chunks.append(expanded_tex(child, seen))
    return "\n".join(chunks)


def mainline_checks() -> list[dict]:
    required = {
        18: (7, 4), 25: (8, 8), 26: (5, 0),
        31: (8, 6), 32: (12, 8),
    }
    rows = []
    for chapter, (min_examples, min_figures) in required.items():
        text = (GENERATED / "chapters" / f"ch{chapter:02d}.tex").read_text(encoding="utf-8")
        examples = len(re.findall(r"\\begin\{origexamplebox\}", text))
        solutions = len(re.findall(r"\\begin\{xesolution\}", text))
        figures = len(re.findall(
            r"\\(?:figcap|bookcaption|diagramcaption|historyfigure|sourceimage)\b", text
        ))
        rows.append({
            "chapter": chapter,
            "examples": examples,
            "solutions": solutions,
            "figures": figures,
            "ok": examples == solutions and examples >= min_examples and figures >= min_figures,
        })
    return rows


def advanced_checks() -> list[dict]:
    rows = []
    for unit, expected in ADVANCED_EXPECTED.items():
        total_examples=expected["examples"]+expected.get("supplemental_examples",0)
        path = ROOT / "advanced" / f"{unit}.tex"
        if path.exists():
            text = expanded_tex(path)
            examples = len(re.findall(r"\\begin\{advexamplebox\}", text))
            solutions = len(re.findall(r"\\begin\{advsolution\}", text))
            definitions = len(re.findall(r"\\begin\{advdefinition\}", text))
            theorems = len(re.findall(r"\\begin\{advtheorem\}", text))
            unfinished = len(re.findall(r"证明课内介绍|TODO|待补|未完成", text))
        else:
            examples = solutions = definitions = theorems = unfinished = 0
        rows.append({
            "unit": unit,
            "path": str(path),
            "expected": expected,
            "examples": examples,
            "solutions": solutions,
            "definitions": definitions,
            "theorems": theorems,
            "unfinished_markers": unfinished,
            "ok": (
                path.exists()
                and examples == total_examples
                and solutions == total_examples
                and definitions == expected["definitions"]
                and theorems == expected["theorems"]
                and unfinished == 0
            ),
        })
    return rows


def source_ledger_check() -> dict:
    path = GENERATED / "ledger" / "source-ledger.json"
    if not path.exists():
        return {"ok": False, "reason": "source ledger missing"}
    data = json.loads(path.read_text(encoding="utf-8"))
    pending = {}
    accepted = {}
    for item in data["objects"]:
        status = item["status"]
        if item["object_type"] != "excluded_page" and not status.startswith("accepted_"):
            pending[status] = pending.get(status, 0) + 1
        elif status.startswith("accepted_"):
            if not item.get("review_evidence"):
                pending["accepted_without_evidence"] = pending.get("accepted_without_evidence", 0) + 1
            accepted[status] = accepted.get(status, 0) + 1
    source_failures = [
        source["id"] for source in data["sources"]
        if not source.get("review_evidence") or not source.get("acceptance_basis")
    ]
    return {
        "ok": not pending and not source_failures,
        "accepted_status_counts": accepted,
        "pending_status_counts": pending,
        "sources_without_evidence": source_failures,
    }


def appendix_check() -> dict:
    path = GENERATED / "appendix-e-difference-ledger.json"
    if not path.exists():
        return {"ok": False, "reason": "appendix difference ledger missing"}
    data = json.loads(path.read_text(encoding="utf-8"))
    unresolved = [item for item in data["comparisons"] if any(
        marker in item["status"] for marker in ("manual", "needs", "probable")
    )]
    return {
        "included_unique_examples": len(data["included"]),
        "unresolved_manual_comparisons": len(unresolved),
        "ok": len(unresolved) == 0,
    }


def deliverable_check() -> dict:
    path = GENERATED / "deliverables.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    count = sum(len(value) if isinstance(value, list) else 1 for value in data.values())
    return {"declared": count, "expected": 47, "ok": count == 47}


def final_artifact_checks() -> dict:
    rows = {}
    for name in ("release-qa.json", "visual-qa.json"):
        path = GENERATED / name
        if not path.exists():
            rows[name] = {"ok": False, "reason": "missing"}
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rows[name] = {"ok": bool(data.get("ok"))}
    return {"reports": rows, "ok": all(item["ok"] for item in rows.values())}


def build_report() -> dict:
    report = {
        "mainline": mainline_checks(),
        "advanced": advanced_checks(),
        "source_ledger": source_ledger_check(),
        "appendix_e": appendix_check(),
        "deliverables": deliverable_check(),
        "final_artifacts": final_artifact_checks(),
    }
    report["ok"] = (
        all(item["ok"] for item in report["mainline"])
        and all(item["ok"] for item in report["advanced"])
        and report["source_ledger"]["ok"]
        and report["appendix_e"]["ok"]
        and report["deliverables"]["ok"]
        and report["final_artifacts"]["ok"]
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    report = build_report()
    target = GENERATED / "release-gate.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"] and not args.report_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
