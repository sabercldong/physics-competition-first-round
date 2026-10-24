#!/usr/bin/env python3
"""Verify final source replay, stable labels and a separate portable build."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import fitz

parser = argparse.ArgumentParser()
parser.add_argument("--repo", type=Path, required=True)
parser.add_argument("--portable", type=Path)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--check-overlays", action="store_true")
args = parser.parse_args()
repo = args.repo.resolve()
relative_book = Path("sample/xes-original/restructured-complete")
book = repo / relative_book
build = book / "build/quality-main"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    return {str(p.relative_to(book)): digest(p) for p in book.rglob("*.tex")
            if "build" not in p.relative_to(book).parts}


report = {"date": "2026-10-24"}
if args.check_overlays:
    before = source_hashes()
    for _ in range(2):
        subprocess.run([sys.executable, str(book / "tools/apply_quality_revision.py")],
                       cwd=book, check=True, stdout=subprocess.DEVNULL)
    after = source_hashes()
    report["overlay_idempotence_files"] = len(before)
    report["overlay_idempotence_failures"] = [p for p in before if before[p] != after.get(p)]
    if report["overlay_idempotence_failures"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit("Source changed on replay; inspect and compile again.")

for ext in ["aux", "toc"]:
    previous = build / f"main.previous.{ext}"
    report[f"stable_original_{ext}"] = previous.exists() and previous.read_bytes() == (build / f"main.{ext}").read_bytes()

log = (build / "main.log").read_text()
report["log_problem_counts"] = {token: log.count(token) for token in [
    "Overfull", "Missing character", "undefined references", "multiply defined", "! LaTeX Error"]}
inputs = set()
for line in (build / "main.fls").read_text().splitlines():
    if not line.startswith("INPUT "):
        continue
    path = Path(line[6:])
    if not path.is_absolute():
        path = book / path
    path = path.resolve()
    if path.is_file() and path.is_relative_to(repo) and "build" not in path.relative_to(repo).parts:
        inputs.add(path)
report["active_input_types"] = dict(Counter(p.suffix for p in inputs))
report["active_inputs"] = [{"file": str(p.relative_to(repo)), "sha256": digest(p)} for p in sorted(inputs)]

if args.portable:
    portable = args.portable.resolve()
    portable_build = portable / relative_book / "build/quality-portable"
    for item in report["active_inputs"]:
        target = portable / item["file"]
        item["portable_matches"] = target.exists() and digest(target) == item["sha256"]
    for ext in ["aux", "toc"]:
        report[f"portable_{ext}_matches"] = (build / f"main.{ext}").read_bytes() == (portable_build / f"main.{ext}").read_bytes()
    portable_log = (portable_build / "main.log").read_text()
    report["portable_log_problem_counts"] = {t: portable_log.count(t) for t in report["log_problem_counts"]}
    report["original_checkout_references"] = [line for line in (portable_build / "main.fls").read_text().splitlines()
                                             if str(repo) in line]
    external_content = set()
    for line in (portable_build / "main.fls").read_text().splitlines():
        if not line.startswith("INPUT "):
            continue
        dependency = Path(line[6:])
        if not dependency.is_absolute():
            dependency = portable / relative_book / dependency
        dependency = dependency.resolve()
        if (dependency.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf", ".dat", ".csv", ".svg"}
                and not dependency.is_relative_to(portable)):
            external_content.add(str(dependency))
    report["unbundled_portable_content_inputs"] = sorted(external_content)
    with fitz.open(build / "main.pdf") as original_pdf, fitz.open(portable_build / "main.pdf") as portable_pdf:
        report["original_pdf_pages"] = len(original_pdf)
        report["portable_pdf_pages"] = len(portable_pdf)
        report["portable_page_text_mismatches"] = [
            i + 1 for i in range(min(len(original_pdf), len(portable_pdf)))
            if original_pdf[i].get_text() != portable_pdf[i].get_text()]
        # CMEX subset fonts can expose legacy slot letters versus Unicode math
        # symbols to text extraction. Compare the actual page display as well.
        report["portable_render_dpi"] = 144
        report["portable_render_mismatches"] = []
        for i in range(min(len(original_pdf), len(portable_pdf))):
            left = original_pdf[i].get_pixmap(dpi=144, colorspace=fitz.csRGB, alpha=False)
            right = portable_pdf[i].get_pixmap(dpi=144, colorspace=fitz.csRGB, alpha=False)
            if (left.width, left.height, left.digest) != (right.width, right.height, right.digest):
                report["portable_render_mismatches"].append(i + 1)

args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
summary = {k: v for k, v in report.items() if k != "active_inputs"}
if "portable_page_text_mismatches" in summary:
    summary["portable_page_text_mismatch_count"] = len(summary.pop("portable_page_text_mismatches"))
summary["active_input_count"] = len(inputs)
summary["portable_input_mismatches"] = sum(not x.get("portable_matches", True) for x in report["active_inputs"])
print(json.dumps(summary, ensure_ascii=False, indent=2))
checks = [report["stable_original_aux"], report["stable_original_toc"], not any(report["log_problem_counts"].values())]
if args.portable:
    checks += [report["portable_aux_matches"], report["portable_toc_matches"],
               not report["original_checkout_references"], not summary["portable_input_mismatches"],
               not report["unbundled_portable_content_inputs"],
               not any(report["portable_log_problem_counts"].values()),
               report["original_pdf_pages"] == report["portable_pdf_pages"],
               not report["portable_render_mismatches"]]
if not all(checks):
    raise SystemExit(1)
