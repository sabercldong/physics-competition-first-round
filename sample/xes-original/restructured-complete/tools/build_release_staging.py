#!/usr/bin/env python3
"""Build all declared release PDFs in an isolated staging directory.

Every wrapper is run through XeLaTeX twice.  Nothing is copied to the public
output directory; publication is a separate, gated operation.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "generated" / "deliverables.json"
STAGING = ROOT / "build" / "release-staging"


def rows() -> list[dict]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result: list[dict] = []
    for kind, value in payload.items():
        entries = value if isinstance(value, list) else [value]
        for index, entry in enumerate(entries, start=1):
            result.append({"kind": kind, "index": index, **entry})
    return result


def slug(row: dict) -> str:
    if row["kind"] == "chapters":
        return f"chapter-{row['chapter']:02d}"
    if row["kind"] == "advanced":
        return f"advanced-{row['unit']}"
    if row["kind"] == "volumes":
        return f"volume-{row['volume']}"
    if row["kind"] == "appendices":
        return f"appendix-{row['appendix']}"
    return "complete"


def warning_counts(log_text: str) -> dict[str, int]:
    patterns = {
        "undefined_references": r"undefined references|Reference .* undefined",
        "multiply_defined_labels": r"multiply defined|Label .* multiply defined",
        "missing_characters": r"Missing character:",
        "overfull_hbox": r"Overfull \\hbox",
        "overfull_vbox": r"Overfull \\vbox",
        "underfull_hbox": r"Underfull \\hbox",
    }
    return {key: len(re.findall(pattern, log_text, re.IGNORECASE)) for key, pattern in patterns.items()}


def build_one(row: dict, ordinal: int, total: int) -> dict:
    name = slug(row)
    wrapper = ROOT / row["wrapper"]
    work = STAGING / "work" / name
    pdf_dir = STAGING / "pdf"
    work.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
        f"-output-directory={work}", str(wrapper),
    ]
    print(f"[{ordinal:02d}/{total:02d}] {name}: pass 1", flush=True)
    first = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if first.returncode:
        (work / "pass1.stdout").write_text(first.stdout, encoding="utf-8")
        raise RuntimeError(f"XeLaTeX pass 1 failed for {name}; see {work / 'pass1.stdout'}")
    print(f"[{ordinal:02d}/{total:02d}] {name}: pass 2", flush=True)
    second = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (work / "pass1.stdout").write_text(first.stdout, encoding="utf-8")
    (work / "pass2.stdout").write_text(second.stdout, encoding="utf-8")
    if second.returncode:
        raise RuntimeError(f"XeLaTeX pass 2 failed for {name}; see {work / 'pass2.stdout'}")
    built = work / f"{wrapper.stem}.pdf"
    log = work / f"{wrapper.stem}.log"
    if not built.exists() or not log.exists():
        raise RuntimeError(f"missing PDF/log after build: {name}")
    target = pdf_dir / row["output"]
    shutil.copy2(built, target)
    log_text = log.read_text(encoding="utf-8", errors="replace")
    return {
        "name": name,
        "kind": row["kind"],
        "wrapper": str(wrapper),
        "output": str(target),
        "passes": 2,
        "bytes": target.stat().st_size,
        "warnings": warning_counts(log_text),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        help="comma-separated build slugs to replace in an existing staging report",
    )
    args = parser.parse_args()
    all_entries = rows()
    wanted = set(args.only.split(",")) if args.only else None
    entries = [entry for entry in all_entries if wanted is None or slug(entry) in wanted]
    if wanted is not None and {slug(entry) for entry in entries} != wanted:
        missing = sorted(wanted - {slug(entry) for entry in entries})
        raise SystemExit(f"unknown release build slug(s): {missing}")
    STAGING.mkdir(parents=True, exist_ok=True)
    report_path = STAGING / "build-report.json"
    prior: dict[str, dict] = {}
    if args.only and report_path.exists():
        old = json.loads(report_path.read_text(encoding="utf-8"))
        prior = {item["name"]: item for item in old["items"]}
    results = []
    for ordinal, row in enumerate(entries, start=1):
        result = build_one(row, ordinal, len(entries))
        prior[result["name"]] = result
        results.append(result)
    ordered = [prior[slug(row)] for row in all_entries if slug(row) in prior]
    report_path.write_text(
        json.dumps({"expected": len(all_entries), "completed": len(ordered), "items": ordered},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"completed": len(ordered), "rebuilt": len(results), "staging": str(STAGING)},
                     ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
