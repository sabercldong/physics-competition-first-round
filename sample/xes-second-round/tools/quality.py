"""Shared fingerprints and evidence checks; never upgrades review status automatically."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
MAIN_SOURCE_IDS = {"autumn_student_2020", "autumn_practice_2020",
                   "winter_second_stage", "spring_second_stage"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def input_paths(items: list[dict], book: Path = BOOK) -> list[Path]:
    paths = {book / "style.tex", book / "book.json", book / "tools/build.py"}
    for item in items:
        if item.get("kind") == "advanced":
            paths.update((book / "advanced").glob(f"{item['id'].lower()}*.tex"))
        else:
            paths.update((book / "chapters").glob(f"ch{item['number']:02d}*.tex"))
    if (book / "assets").exists():
        owners = {f"ch{item['number']:02d}" if item.get("kind") != "advanced"
                  else item["id"].lower() for item in items}
        for resource in (book / "assets").rglob("*"):
            if not resource.is_file():
                continue
            owner = resource.relative_to(book / "assets").parts[0]
            # Chapter-owned assets cannot invalidate an unrelated locked chapter.
            # Unclassified/shared resources remain conservative global inputs.
            if not re.fullmatch(r"ch\d{2}|h\d", owner) or owner in owners:
                paths.add(resource)
        # Include explicit cross-chapter image dependencies as well. Literal
        # paths are required by this project; do not silently ignore a reused asset.
        for tex in tuple(paths):
            if tex.suffix != ".tex":
                continue
            source = tex.read_text(encoding="utf-8")
            for name in re.findall(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^{}]+)\}", source):
                candidate = Path(name) if Path(name).is_absolute() else book / name
                if candidate.is_file():
                    paths.add(candidate)
    return sorted(paths)


def fingerprints(items: list[dict], book: Path = BOOK) -> dict[str, str]:
    return {str(p.relative_to(book)): sha256(p) for p in input_paths(items, book)}


def artifact_errors(work: Path, book: Path = BOOK) -> list[str]:
    errors = []
    record = work / "artifact.json"
    if not record.exists():
        return [f"缺构建证据：{record}"]
    data = load_json(record)
    if data.get("successful_compile_passes", 0) < 2:
        errors.append(f"{work.name}：未记录两次成功编译")
    pdf = work / "main.pdf"
    if not pdf.exists() or sha256(pdf) != data.get("pdf_sha256"):
        errors.append(f"{work.name}：PDF与构建记录不一致")
    current = fingerprints(data["items"], book)
    if current != data.get("inputs"):
        errors.append(f"{work.name}：源文件已变更，构建证据失效")
    return errors


def review_errors(work: Path, book: Path = BOOK) -> list[str]:
    """A human-authored record must refer to this exact PDF and build inputs."""
    errors = artifact_errors(work, book)
    path = book / "reviews" / f"{work.name}.json"
    if not path.exists():
        return errors + [f"缺本轮人工审阅记录：{path}"]
    review = load_json(path)
    if review.get("status") != "verified":
        errors.append(f"{work.name}：本轮人工审阅未完成")
    artifact = load_json(work / "artifact.json") if (work / "artifact.json").exists() else {}
    if review.get("pdf_sha256") != artifact.get("pdf_sha256"):
        errors.append(f"{work.name}：审阅的不是当前PDF")
    if review.get("inputs") != artifact.get("inputs"):
        errors.append(f"{work.name}：审阅对应的源文件版本不一致")
    for item in ("page_layout", "figures", "physics", "source_completeness", "pdf_structure"):
        evidence = review.get("checks", {}).get(item, {})
        if evidence.get("status") != "passed" or not evidence.get("evidence"):
            errors.append(f"{work.name}：缺少{item}的通过结论和证据")
        for relative in evidence.get("evidence", []):
            target = (book / relative).resolve()
            if not target.is_relative_to(book.resolve()) or not target.is_file():
                errors.append(f"{work.name}：审阅证据不存在或越出工程：{relative}")
            elif evidence.get("evidence_sha256", {}).get(relative) != sha256(target):
                errors.append(f"{work.name}：审阅证据缺哈希或内容已变更：{relative}")
    if review.get("unresolved_findings") != []:
        errors.append(f"{work.name}：问题清单未清零")
    return errors


def source_inventory_errors(book: Path = BOOK) -> list[str]:
    """Check independent page/object coverage against the ledger, not the reverse."""
    errors = []
    catalog = [s for s in load_json(book / "sources.json")["sources"] if s["source_id"] in MAIN_SOURCE_IDS]
    expected = {(s["source_id"], p) for s in catalog for p in range(1, s["pages"] + 1)}
    def rows(name):
        path = book / name
        if not path.exists():
            errors.append(f"缺独立来源清单：{name}")
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    pages = rows("page_inventory.jsonl")
    objects = rows("source_inventory.jsonl")
    ledger = rows("source_ledger.jsonl")
    page_keys = [(p["source_id"], p["physical_page"]) for p in pages]
    if len(page_keys) != len(set(page_keys)):
        errors.append("独立页清单存在重复页")
    if set(page_keys) != expected:
        errors.append(f"独立页清单缺页{len(expected-set(page_keys))}，多页{len(set(page_keys)-expected)}")
    digests = {s["source_id"]: sha256(Path(s["path"])) for s in catalog}
    by_object = {}
    for obj in objects:
        key = obj.get("source_object_id")
        if not key or key in by_object:
            errors.append(f"来源对象编号缺失或重复：{key}")
        by_object[key] = obj
    declared = set()
    unresolved_pages = []
    for page in pages:
        key = (page["source_id"], page["physical_page"])
        if page.get("source_sha256") != digests.get(page["source_id"]):
            errors.append(f"原件版本不一致：{key}")
        classification = page.get("classification")
        if classification == "excluded":
            if page.get("object_inventory_verified") is not True:
                unresolved_pages.append(key)
            if not page.get("exclusion_reason") or page.get("object_ids"):
                errors.append(f"排除页理由缺失或仍有教学对象：{key}")
            continue
        if classification != "teaching" or page.get("object_inventory_verified") is not True:
            unresolved_pages.append(key)
            continue
        if not page.get("object_ids"):
            errors.append(f"教学页没有任何来源对象：{key}")
        for object_id in page.get("object_ids", []):
            declared.add(object_id)
            obj = by_object.get(object_id, {})
            if (obj.get("source_id"), obj.get("physical_page")) != key:
                errors.append(f"页清单和来源对象归属不一致：{object_id}")
    if unresolved_pages:
        errors.append(f"尚有{len(unresolved_pages)}个源页未完成独立人工分类/对象核对")
    if set(by_object) - declared:
        errors.append(f"存在未归属到已核对源页的来源对象：{len(set(by_object)-declared)}项")
    links = {}
    for row in ledger:
        if row.get("source_id") not in MAIN_SOURCE_IDS or row.get("status") == "excluded":
            continue
        identifier = row.get("source_object_id")
        if not identifier:
            continue
        if identifier not in by_object:
            errors.append(f"台账引用了不存在的来源对象：{identifier}")
        links.setdefault(identifier, []).append(row)
    missing = set(by_object) - set(links)
    if missing:
        errors.append(f"独立来源对象未映射：{len(missing)}项")
    # The old coarse page-to-section rows may remain as history, but cannot
    # stand in for the new per-object rows required above.
    for identifier, mappings in links.items():
        obj = by_object.get(identifier, {})
        if not obj.get("description") or not obj.get("source_locator") or not obj.get("object_type"):
            errors.append(f"来源对象缺类型、描述或页内定位：{identifier}")
        for row in mappings:
            if (row.get("source_id"), row.get("physical_page")) != (obj.get("source_id"), obj.get("physical_page")):
                errors.append(f"映射源页与对象源页不一致：{identifier}")
            if row.get("status") not in {"mapped", "merged"} or not row.get("target_id"):
                errors.append(f"教学对象映射状态不合格：{identifier}")
            if row.get("status") == "merged" and not row.get("notes"):
                errors.append(f"合并缺少差异处理记录：{identifier}")
    return errors
