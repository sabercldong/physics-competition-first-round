#!/usr/bin/env python3
"""Run structural, font, text, bookmark, and log gates on staged PDFs."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "build" / "release-staging"
PDF_DIR = STAGING / "pdf"
MANIFEST = ROOT / "generated" / "deliverables.json"
REPORT = ROOT / "generated" / "release-qa.json"


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True, errors="replace", stderr=subprocess.STDOUT)


def manifest_rows() -> list[dict]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for kind, value in payload.items():
        for item in value if isinstance(value, list) else [value]:
            rows.append({"kind": kind, **item})
    return rows


def outlines(pdf: Path) -> list[dict]:
    data = json.loads(command("qpdf", "--json", "--json-key=outlines", str(pdf)))
    return data["outlines"]


def flatten(items: list[dict]):
    for item in items:
        yield item
        yield from flatten(item.get("kids", []))


def font_check(pdf: Path) -> dict:
    output = command("pdffonts", str(pdf))
    rows = [line for line in output.splitlines()[2:] if line.strip()]
    unembedded = [line for line in rows if re.search(r"\sno\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", line)]
    return {"font_rows": len(rows), "unembedded": unembedded, "ok": bool(rows) and not unembedded}


def pdf_info(pdf: Path) -> tuple[int, int]:
    output = command("pdfinfo", str(pdf))
    pages = int(re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE).group(1))
    size = int(re.search(r"^File size:\s+(\d+) bytes", output, re.MULTILINE).group(1))
    return pages, size


def main() -> None:
    rows = manifest_rows()
    build = json.loads((STAGING / "build-report.json").read_text(encoding="utf-8"))
    build_by_output = {Path(item["output"]).name: item for item in build["items"]}
    results = []
    expected_names = {row["output"] for row in rows}
    actual_names = {path.name for path in PDF_DIR.glob("*.pdf")}
    if actual_names != expected_names:
        raise SystemExit(f"staging PDF set mismatch: missing={expected_names-actual_names}, extra={actual_names-expected_names}")

    for index, row in enumerate(rows, start=1):
        pdf = PDF_DIR / row["output"]
        build_item = build_by_output[pdf.name]
        qpdf_output = command("qpdf", "--check", str(pdf))
        pages, size = pdf_info(pdf)
        text = command("pdftotext", str(pdf), "-")
        font = font_check(pdf)
        outline = outlines(pdf)
        severe = {
            key: value for key, value in build_item["warnings"].items()
            if key != "underfull_hbox" and value
        }
        item = {
            "kind": row["kind"],
            "output": pdf.name,
            "pages": pages,
            "bytes": size,
            "passes": build_item["passes"],
            "text_characters": len(text),
            "outline_entries": len(list(flatten(outline))),
            "fonts": font,
            "severe_log_warnings": severe,
            "qpdf_ok": "No syntax or stream encoding errors found" in qpdf_output,
        }
        item["ok"] = all((
            item["passes"] >= 2,
            item["qpdf_ok"],
            item["pages"] > 0,
            item["text_characters"] > item["pages"] * 100,
            item["outline_entries"] > 0,
            item["fonts"]["ok"],
            not item["severe_log_warnings"],
        ))
        results.append(item)
        print(f"[{index:02d}/{len(rows):02d}] {'OK' if item['ok'] else 'FAIL'} {pdf.name}", flush=True)

    complete = next(item for item in results if item["kind"] == "complete")
    complete_pdf = PDF_DIR / complete["output"]
    top = outlines(complete_pdf)
    top_titles = [item["title"] for item in top]
    required_order = [
        *[next(row["title"] for row in json.loads((ROOT / "generated" / "source-map.json").read_text(encoding="utf-8"))["chapters"] if row["chapter"] == number) for number in range(1, 33)],
        "电磁学补充专题",
        "第7卷　高阶选读",
        "记号说明",
    ]
    ordering_ok = top_titles == required_order
    advanced_part = next(item for item in top if item["title"] == "第7卷　高阶选读")
    advanced_units = [item for item in advanced_part["kids"] if re.fullmatch(r"A[1-6] .*", item["title"])]
    unit_bookmarks_ok = len(advanced_units) == 6
    starts = [item["destpageposfrom1"] for item in advanced_units] + [complete["pages"] + 1]
    for unit, start, end in zip(advanced_units, starts, starts[1:]):
        descendants = list(flatten(unit.get("kids", [])))
        unit_bookmarks_ok &= all(
            item.get("destpageposfrom1") is not None
            and start <= item["destpageposfrom1"] < end
            for item in descendants
        )

    payload = {
        "declared": len(rows),
        "built": len(results),
        "all_items_ok": all(item["ok"] for item in results),
        "complete_top_level_order_ok": ordering_ok,
        "advanced_bookmark_targets_ok": unit_bookmarks_ok,
        "items": results,
    }
    payload["ok"] = all((payload["all_items_ok"], ordering_ok, unit_bookmarks_ok))
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "items"}, ensure_ascii=False))
    if not payload["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
