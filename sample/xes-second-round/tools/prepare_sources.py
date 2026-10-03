#!/usr/bin/env python3
"""Cache all source pages independently of the mapping ledger.

Text/OCR regions are discovery aids, NOT a verified teaching-object inventory.
Page classification and object-by-object checking are deliberately manual.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import fitz
from quality import BOOK, MAIN_SOURCE_IDS, load_json, sha256, write_json

CACHE = BOOK / "build/source-pages"


def prepare_page(task: tuple[dict, int]) -> tuple[str, int, str]:
    source, number = task
    base = CACHE / source["source_id"] / f"page-{number:03d}"
    meta = base.with_suffix(".json")
    if meta.exists():
        old = load_json(meta)
        if old.get("source_sha256") == source["sha256"] and base.with_suffix(".txt").exists():
            return source["source_id"], number, "cached"
    base.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(source["path"]) as doc:
        page = doc[number - 1]
        page.get_pixmap(dpi=120, colorspace=fitz.csRGB, alpha=False).save(
            base.with_suffix(".jpg"), jpg_quality=85)
        text = page.get_text(sort=True)
        blocks = []
        for block in page.get_text("dict")["blocks"]:
            row = {"bbox": list(block["bbox"]), "type": block["type"]}
            if block["type"] == 0:
                row["text"] = "\n".join("".join(s["text"] for s in line["spans"])
                                          for line in block["lines"])
            blocks.append(row)
        method = "native"
        if len(text.strip()) < 30:
            method = "ocr_unverified"
            env = dict(os.environ, OMP_THREAD_LIMIT="1")
            proc = subprocess.run(
                ["tesseract", "stdin", str(base), "-l", "chi_sim+eng", "--psm", "3", "txt", "tsv"],
                input=page.get_pixmap(dpi=250, colorspace=fitz.csRGB, alpha=False).tobytes("png"),
                capture_output=True, env=env, timeout=180)
            if proc.returncode:
                raise RuntimeError(f"{source['source_id']} p{number}: {proc.stderr.decode()}")
        else:
            base.with_suffix(".txt").write_text(text, encoding="utf-8")
        write_json(meta, {"source_id": source["source_id"], "physical_page": number,
                          "source_sha256": source["sha256"], "page_size_pt": list(page.rect),
                          "method": method, "native_regions": blocks,
                          "human_verified": False})
    return source["source_id"], number, method


def initialize_inventory(sources: list[dict]) -> None:
    path = BOOK / "page_inventory.jsonl"
    rows = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            key = (row["source_id"], row["physical_page"])
            if key in rows:
                raise SystemExit(f"页清单重复：{key}")
            rows[key] = row
    for source in sources:
        for number in range(1, source["pages"] + 1):
            key = (source["source_id"], number)
            if key in rows:
                if rows[key].get("source_sha256") != source["sha256"]:
                    raise SystemExit(f"原件已变，须先复核页清单，拒绝静默覆盖：{key}")
                continue
            rows[key] = {"source_id": source["source_id"], "physical_page": number,
                         "source_sha256": source["sha256"], "printed_page": None,
                         "classification": "unreviewed", "object_inventory_verified": False,
                         "exclusion_reason": None, "object_ids": [], "review_notes": ""}
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n"
                            for _, row in sorted(rows.items())), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=sorted(MAIN_SOURCE_IDS))
    parser.add_argument("--first", type=int)
    parser.add_argument("--last", type=int)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    catalog = load_json(BOOK / "sources.json")
    sources = [dict(s) for s in catalog["sources"] if s["source_id"] in MAIN_SOURCE_IDS]
    for source in sources:
        source["sha256"] = sha256(Path(source["path"]))
        with fitz.open(source["path"]) as doc:
            if len(doc) != source["pages"]:
                raise SystemExit(f"原件页数已变：{source['path']}")
    initialize_inventory(sources)
    tasks = []
    for source in sources:
        if args.source and args.source != source["source_id"]:
            continue
        tasks.extend((source, n) for n in range(args.first or 1, (args.last or source["pages"]) + 1)
                     if 1 <= n <= source["pages"])
    with ProcessPoolExecutor(max_workers=max(1, min(args.workers, 4))) as pool:
        jobs = [pool.submit(prepare_page, task) for task in tasks]
        for done, future in enumerate(as_completed(jobs), 1):
            source_id, page, method = future.result()
            print(f"{done}/{len(tasks)} {source_id} p{page}: {method}", flush=True)
    print("工作页准备完成；人工核对未自动通过。", flush=True)


if __name__ == "__main__":
    main()
