#!/usr/bin/env python3
"""Build the auditable page/object ledger used by the final book rebuild.

The ledger deliberately separates three facts:

* an object exists in a source PDF;
* the object has a declared destination;
* the destination has passed human content/figure review.

The last state is never inferred merely from the existence of a generated PDF.
Born-digital advanced notes are indexed with LiteParse text boxes.  Scanned
primary PDFs are registered page by page and remain ``needs_object_audit`` until
their OCR/manual object inventories are attached.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
REGISTER = BOOK / "audit" / "source-register.json"
ACCEPTANCE = BOOK / "audit" / "source-acceptance.json"
OUT = BOOK / "generated" / "ledger"

ADVANCED_ID = "r2-comprehensive"
ADVANCED_EXPECTED = {"example": 148, "definition": 48, "theorem": 77}
ADVANCED_UNITS = {
    1: ("A1", "力学", 5, 66),
    2: ("A2", "热学", 67, 86),
    3: ("A3", "数学工具", 87, 130),
    4: ("A4", "电磁学", 131, 160),
    5: ("A5", "光学", 161, 190),
    6: ("A6", "近代物理", 191, 221),
}

# Sources without ranges in the original register are scanned books.  These
# ranges classify pages; object-level acceptance still requires the OCR/manual
# pass and is therefore not silently marked complete here.
DEFAULT_TEACHING_RANGES: dict[str, list[tuple[int, int, list[int]]]] = {
    "r1-mechanics": [(3, 82, [5, 6, 7, 8, 9])],
    "r1-calculus": [(1, 20, [1, 9])],
    "r1-summer": [(3, 80, [5, 6, 7, 8, 9])],
    "r1-autumn-em-1": [(5, 52, [19, 20, 21])],
    "r1-autumn-em-2": [(5, 81, [22, 23, 24, 26])],
    "r1-thermal": [(5, 52, [14, 15, 16, 17])],
}


def run_text(command: list[str]) -> str:
    return subprocess.check_output(command, text=True, errors="replace")


def pdf_pages(path: Path) -> int:
    info = run_text(["pdfinfo", str(path)])
    match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    if not match:
        raise RuntimeError(f"cannot read page count: {path}")
    return int(match.group(1))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_ranges(source: dict[str, Any]) -> list[dict[str, Any]]:
    if source.get("ranges"):
        return source["ranges"]
    return [
        {"pages": [start, end], "targets": targets}
        for start, end, targets in DEFAULT_TEACHING_RANGES.get(source["id"], [])
    ]


def page_target(page: int, ranges: list[dict[str, Any]]) -> list[Any] | None:
    for item in ranges:
        start, end = item["pages"]
        if start <= page <= end:
            return item.get("targets")
    return None


def excluded_reason(page: int, total: int, ranges: list[dict[str, Any]]) -> str:
    if not ranges:
        return "尚未建立教学页范围"
    starts = [item["pages"][0] for item in ranges]
    ends = [item["pages"][1] for item in ranges]
    if page < min(starts):
        return "封面、目录或分部页"
    if page > max(ends):
        return "空白页、广告或版权页"
    return "讲次分隔页或空白页"


def parse_pdfimages(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in run_text(["pdfimages", "-list", str(path)]).splitlines():
        fields = line.split()
        if len(fields) < 15 or not fields[0].isdigit() or fields[2] != "image":
            continue
        rows.append({
            "page": int(fields[0]),
            "image_number": int(fields[1]),
            "width": int(fields[3]),
            "height": int(fields[4]),
            "color": fields[5],
            "encoding": fields[8],
            "object_id": int(fields[10]),
        })
    return rows


def advanced_unit(number: str) -> tuple[str, str]:
    major = int(number.split(".", 1)[0])
    unit, title, _, _ = ADVANCED_UNITS[major]
    return unit, title


def advanced_label(kind: str, number: str) -> str:
    unit, _ = advanced_unit(number)
    slug = number.replace(".", "-")
    short = {"example": "ex", "definition": "def", "theorem": "thm", "figure": "fig"}[kind]
    return f"adv{unit}:{short}:{slug}"


def resolve_evidence(paths: list[str]) -> list[str]:
    """Resolve and validate every file/directory cited as review evidence."""
    resolved: list[str] = []
    for raw in paths:
        path = (BOOK / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
        if not path.exists():
            raise RuntimeError(f"review evidence missing: {path}")
        resolved.append(str(path))
    return resolved


def accepted_page(page: int, acceptance: dict[str, Any]) -> bool:
    return any(start <= page <= end for start, end in acceptance["accepted_teaching_ranges"])


def load_acceptance(register: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if not ACCEPTANCE.exists():
        raise RuntimeError(f"source acceptance manifest missing: {ACCEPTANCE}")
    payload = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    indexed = {item["source_id"]: item for item in payload["sources"]}
    registered_ids = {item["id"] for item in register["sources"]}
    if set(indexed) != registered_ids:
        missing = sorted(registered_ids - set(indexed))
        extra = sorted(set(indexed) - registered_ids)
        raise RuntimeError(f"acceptance/register mismatch: missing={missing}, extra={extra}")
    for source in register["sources"]:
        item = indexed[source["id"]]
        if item["accepted_sha256"] != source["sha256"]:
            raise RuntimeError(f"acceptance hash mismatch: {source['id']}")
        item["resolved_evidence"] = resolve_evidence(item["evidence"])
        declared = normalized_ranges(source)
        for entry in declared:
            start, end = entry["pages"]
            if not all(accepted_page(page, item) for page in range(start, end + 1)):
                raise RuntimeError(
                    f"acceptance does not cover declared teaching range: "
                    f"{source['id']} {start}-{end}"
                )
    return indexed


def parse_advanced(
    source: dict[str, Any], acceptance: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        from liteparse import LiteParse
    except ImportError as exc:
        raise SystemExit(
            "LiteParse is required for the advanced layout ledger. "
            "Run this script with the project audit environment."
        ) from exc

    path = Path(source["path"])
    result = LiteParse(
        ocr_enabled=False,
        target_pages="5-221",
        output_format="json",
        preserve_very_small_text=True,
        quiet=True,
    ).parse(path)

    object_patterns = {
        "example": re.compile(r"例\s*([1-6](?:\.\d+){2})"),
        "definition": re.compile(r"定义\s*([1-6](?:\.\d+){2})"),
        "theorem": re.compile(r"定理\s*([1-6](?:\.\d+){2})"),
        "figure": re.compile(r"图\s*([1-6]\.\d{1,2})(?!\.)"),
    }
    seen: dict[str, set[str]] = {kind: set() for kind in object_patterns}
    ledger: list[dict[str, Any]] = []
    layout_pages: list[dict[str, Any]] = []

    for page in result.pages:
        page_number = page.page_num
        major = next(major for major, (_, _, start, end) in ADVANCED_UNITS.items()
                     if start <= page_number <= end)
        unit, title, _, _ = ADVANCED_UNITS[major]
        unit_acceptance = acceptance["units"][unit]
        unit_evidence = resolve_evidence(unit_acceptance["evidence"])
        page_items = []
        for index, item in enumerate(page.text_items, start=1):
            item_data = asdict(item)
            item_data["index"] = index
            page_items.append(item_data)
            ledger.append({
                "source_id": ADVANCED_ID,
                "physical_page": page_number,
                "source_object": f"text-box-{page_number:03d}-{index:03d}",
                "object_type": "layout_text_box",
                "source_number": None,
                "target": unit,
                "target_label": None,
                "status": "accepted_retypeset_review",
                "review_evidence": unit_evidence,
                "bbox": [item.x, item.y, item.width, item.height],
                "text": item.text,
            })
        layout_pages.append({
            "physical_page": page_number,
            "unit": unit,
            "unit_title": title,
            "width": page.width,
            "height": page.height,
            "text": page.text,
            "text_items": page_items,
        })
        for kind, pattern in object_patterns.items():
            for number in pattern.findall(page.text):
                if number in seen[kind]:
                    continue
                seen[kind].add(number)
                target, _ = advanced_unit(number)
                ledger.append({
                    "source_id": ADVANCED_ID,
                    "physical_page": page_number,
                    "source_object": f"{kind}-{number}",
                    "object_type": kind,
                    "source_number": number,
                    "target": target,
                    "target_label": advanced_label(kind, number),
                    "status": "accepted_retypeset_review",
                    "review_evidence": unit_evidence,
                })

    for image in parse_pdfimages(path):
        page = image["page"]
        major = next(major for major, (_, _, start, end) in ADVANCED_UNITS.items()
                     if start <= page <= end)
        unit, _, _, _ = ADVANCED_UNITS[major]
        unit_evidence = resolve_evidence(acceptance["units"][unit]["evidence"])
        ledger.append({
            "source_id": ADVANCED_ID,
            "physical_page": page,
            "source_object": f"embedded-image-{image['image_number']:03d}",
            "object_type": "embedded_image",
            "source_number": image["image_number"],
            "target": unit,
            "target_label": f"adv{unit}:img:{image['image_number']:03d}",
            "status": "accepted_redraw_review",
            "review_evidence": unit_evidence,
            "image_metadata": image,
        })

    counts = {kind: len(seen[kind]) for kind in ("example", "definition", "theorem", "figure")}
    for kind, expected in ADVANCED_EXPECTED.items():
        if counts[kind] != expected:
            raise RuntimeError(f"advanced {kind}: expected {expected}, found {counts[kind]}")
    packet_index = json.loads(
        (BOOK / "audit" / "advanced-packets" / "index.json").read_text(encoding="utf-8")
    )
    packets = {item["unit"]: item for item in packet_index}
    for unit, unit_acceptance in acceptance["units"].items():
        actual = packets[unit]["counts"]
        expected = unit_acceptance["expected_counts"]
        if any(actual.get(kind) != value for kind, value in expected.items()):
            raise RuntimeError(
                f"advanced packet count mismatch for {unit}: expected={expected}, actual={actual}"
            )
    layout = {
        "source_id": ADVANCED_ID,
        "path": str(path),
        "sha256": sha256(path),
        "included_pages": [5, 221],
        "excluded_pages": [1, 4],
        "counts": counts,
        "embedded_images": len(parse_pdfimages(path)),
        "pages": layout_pages,
    }
    return ledger, layout


def build() -> dict[str, Any]:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    acceptance = load_acceptance(register)
    OUT.mkdir(parents=True, exist_ok=True)
    ledger: list[dict[str, Any]] = []
    source_summary: list[dict[str, Any]] = []

    for source in register["sources"]:
        path = Path(source["path"])
        total = pdf_pages(path)
        actual_sha = sha256(path)
        if source.get("sha256") and actual_sha != source["sha256"]:
            raise RuntimeError(f"source hash changed: {path}")
        ranges = normalized_ranges(source)
        source_acceptance = acceptance[source["id"]]
        teaching_count = 0
        excluded_count = 0
        for page in range(1, total + 1):
            targets = page_target(page, ranges)
            if targets is None:
                excluded_count += 1
                ledger.append({
                    "source_id": source["id"],
                    "physical_page": page,
                    "source_object": f"page-{page:03d}",
                    "object_type": "excluded_page",
                    "source_number": None,
                    "target": None,
                    "target_label": None,
                    "status": "excluded",
                    "reason": excluded_reason(page, total, ranges),
                })
            else:
                teaching_count += 1
                ledger.append({
                    "source_id": source["id"],
                    "physical_page": page,
                    "source_object": f"page-{page:03d}",
                    "object_type": "teaching_page",
                    "source_number": None,
                    "target": targets,
                    "target_label": None,
                    "status": ("accepted_layout_indexed" if source["id"] == ADVANCED_ID
                               else "accepted_page_object_mapping"),
                    "review_evidence": source_acceptance["resolved_evidence"],
                })
        source_summary.append({
            "id": source["id"],
            "path": str(path),
            "role": source["role"],
            "pages": total,
            "teaching_pages": teaching_count,
            "excluded_pages": excluded_count,
            "sha256": actual_sha,
            "acceptance_basis": source_acceptance["basis"],
            "review_evidence": source_acceptance["resolved_evidence"],
        })

    advanced_source = next(item for item in register["sources"] if item["id"] == ADVANCED_ID)
    advanced_objects, advanced_layout = parse_advanced(
        advanced_source, acceptance[ADVANCED_ID]
    )
    ledger.extend(advanced_objects)

    payload = {
        "schema_version": 2,
        "status_semantics": {
            "accepted_page_object_mapping": "教学页已由内容映射、独立成品与人工审查证据共同验收",
            "accepted_layout_indexed": "高阶源页版面已索引且纳入对应分讲验收",
            "accepted_retypeset_review": "正文、公式、例题、定义或定理已通过复排与数量核验",
            "accepted_redraw_review": "源图实例已通过重绘登记与物理关系复核",
            "excluded": "非教学页，已给出排除理由",
        },
        "sources": source_summary,
        "objects": ledger,
    }
    (OUT / "source-ledger.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "advanced-layout.json").write_text(
        json.dumps(advanced_layout, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    fields = [
        "source_id", "physical_page", "source_object", "object_type",
        "source_number", "target", "target_label", "status", "reason",
    ]
    with (OUT / "source-ledger.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in ledger:
            clean = dict(row)
            if isinstance(clean.get("target"), list):
                clean["target"] = ",".join(map(str, clean["target"]))
            writer.writerow(clean)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    payload = build()
    counts: dict[str, int] = {}
    for item in payload["objects"]:
        counts[item["object_type"]] = counts.get(item["object_type"], 0) + 1
    print(json.dumps({"sources": len(payload["sources"]), "object_counts": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
