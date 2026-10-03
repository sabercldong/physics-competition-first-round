#!/usr/bin/env python3
"""Split the advanced source layout into six bounded editorial work packets."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER_DIR = ROOT / "generated" / "ledger"
OUT = ROOT / "audit" / "advanced-packets"

UNITS = {
    "A1": ("力学", 5, 66),
    "A2": ("热学", 67, 86),
    "A3": ("数学工具", 87, 130),
    "A4": ("电磁学", 131, 160),
    "A5": ("光学", 161, 190),
    "A6": ("近代物理", 191, 221),
}


def marker_context(page_text: str, kind: str, number: str) -> str:
    prefix = {"example": "例", "definition": "定义", "theorem": "定理", "figure": "图"}[kind]
    match = re.search(re.escape(prefix) + r"\s*" + re.escape(number), page_text)
    if not match:
        return ""
    start = match.start()
    # Retain the complete remainder of the physical page.  Multi-page objects
    # are resolved during retypesetting using the adjacent page packet.
    return page_text[start:].strip()


def main() -> None:
    layout = json.loads((LEDGER_DIR / "advanced-layout.json").read_text(encoding="utf-8"))
    ledger = json.loads((LEDGER_DIR / "source-ledger.json").read_text(encoding="utf-8"))
    pages = {item["physical_page"]: item for item in layout["pages"]}
    source_objects = [
        item for item in ledger["objects"]
        if item["source_id"] == "r2-comprehensive"
        and item["object_type"] in {"example", "definition", "theorem", "figure", "embedded_image"}
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for unit, (title, start, end) in UNITS.items():
        unit_objects = [item for item in source_objects if item["target"] == unit]
        records = []
        for item in unit_objects:
            page = pages[item["physical_page"]]
            record = dict(item)
            if item["object_type"] in {"example", "definition", "theorem", "figure"}:
                record["source_page_context"] = marker_context(
                    page["text"], item["object_type"], str(item["source_number"])
                )
            records.append(record)
        packet = {
            "unit": unit,
            "title": title,
            "physical_pages": [start, end],
            "counts": {
                kind: sum(item["object_type"] == kind for item in unit_objects)
                for kind in ("example", "definition", "theorem", "figure", "embedded_image")
            },
            "pages": [pages[number] for number in range(start, end + 1)],
            "objects": records,
            "acceptance": {
                "all_text_retypeset": False,
                "all_formulas_checked": False,
                "all_examples_solved": False,
                "all_figures_redrawn": False,
            },
        }
        path = OUT / f"{unit}.json"
        path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        index.append({"unit": unit, "title": title, "path": str(path), "counts": packet["counts"]})
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(index, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
