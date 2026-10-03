#!/usr/bin/env python3
"""Merge a manually authored page inventory; never infers unseen objects."""
import argparse
import json
from pathlib import Path
from quality import BOOK, MAIN_SOURCE_IDS, load_json, sha256


def load_rows(path):
    return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()] if path.exists() else []


def save_rows(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def merge(path: Path):
    data = load_json(path)
    source_id = data["source_id"]
    assert source_id in MAIN_SOURCE_IDS
    source = next(s for s in load_json(BOOK / "sources.json")["sources"] if s["source_id"] == source_id)
    assert data["source_sha256"] == sha256(Path(source["path"])), "原件哈希已变更，必须重查"
    assert data["independent_visual_inventory"] is True, "不得从旧台账自动升级"
    pages = load_rows(BOOK / "page_inventory.jsonl")
    page_map = {(r["source_id"], r["physical_page"]): r for r in pages}
    incoming, mappings, ids = [], [], set()
    manifest = str(path.resolve().relative_to(BOOK))
    targets = "\n".join(p.read_text(encoding="utf-8") for p in (BOOK / "chapters").glob("*.tex"))
    for page in data["pages"]:
        number = page["physical_page"]
        assert (source_id, number) in page_map
        preview = BOOK / page["inspected_render"]
        assert preview.is_file(), "缺已检视的源页预览"
        record = page_map[(source_id, number)]
        objects = page.get("objects", [])
        classification = page["classification"]
        if classification == "excluded":
            assert page.get("exclusion_reason") and not objects
        else:
            assert classification == "teaching" and objects
        declared = []
        for obj in objects:
            identity = f"{source_id}:p{number:03d}:{obj['id']}"
            assert identity not in ids, identity
            ids.add(identity)
            declared.append(identity)
            assert obj["source_locator"] and obj["description"]
            assert "\\label{" + obj["target_id"] + "}" in targets, obj["target_id"]
            incoming.append({"source_object_id": identity, "source_id": source_id,
                             "physical_page": number, "printed_page": page.get("printed_page"),
                             "object_type": obj["object_type"], "source_number": obj.get("source_number"),
                             "source_locator": obj["source_locator"], "description": obj["description"],
                             "review_manifest": manifest})
            mappings.append({"source_object_id": identity, "source_id": source_id,
                             "physical_page": number, "printed_page": page.get("printed_page"),
                             "object_type": obj["object_type"], "source_number": obj.get("source_number"),
                             "source_locator": obj["source_locator"], "target_id": obj["target_id"],
                             "status": obj.get("status", "mapped"), "exclusion_reason": None,
                             "notes": obj.get("notes", "对象落点已确认；不代表整章内容与图形验收通过"),
                             "review_manifest": manifest})
            primary_mapping = mappings[-1]
            # One source exercise may yield a question, new derivation and
            # explanation figure. Keep a single independent source object and
            # explicit one-to-many targets, rather than inventing source figures.
            for extension in obj.get("additional_targets", []):
                target = extension["target_id"]
                assert "\\label{" + target + "}" in targets, target
                assert extension.get("target_object_type") and extension.get("notes")
                mappings.append({**primary_mapping, "source_object_id": identity,
                                 "target_id": target,
                                 "target_object_type": extension["target_object_type"],
                                 "notes": extension["notes"], "mapping_role": "extension"})
        record.update(classification=classification, object_inventory_verified=True,
                      printed_page=page.get("printed_page"), object_ids=declared,
                      exclusion_reason=page.get("exclusion_reason"),
                      review_notes=page.get("notes", ""), review_manifest=manifest)
    for filename, new_rows in (("source_inventory.jsonl", incoming), ("source_ledger.jsonl", mappings)):
        old = load_rows(BOOK / filename)
        old = [r for r in old if r.get("review_manifest") != manifest]
        save_rows(BOOK / filename, old + new_rows)
    save_rows(BOOK / "page_inventory.jsonl", pages)
    print(f"导入{len(data['pages'])}页、{len(incoming)}个独立来源对象；没有升级章节验收状态。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    merge(parser.parse_args().manifest)
