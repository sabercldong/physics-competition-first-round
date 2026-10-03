#!/usr/bin/env python3
"""Archive the protected formal set and atomically publish the gated 47 PDFs."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT.parents[2]
GENERATED = ROOT / "generated"
STAGING = ROOT / "build" / "release-staging" / "pdf"
FORMAL = PROJECT / "output" / "pdf"
ARCHIVE = PROJECT / "archive" / "pre-advanced-release" / "20260828"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pages(path: Path) -> int:
    output = subprocess.check_output(["pdfinfo", str(path)], text=True, errors="replace")
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise RuntimeError(f"cannot read page count: {path}")


def report_ok(name: str) -> None:
    data = json.loads((GENERATED / name).read_text(encoding="utf-8"))
    if not data.get("ok"):
        raise RuntimeError(f"publication gate failed: {name}")


def declared_outputs() -> list[str]:
    data = json.loads((GENERATED / "deliverables.json").read_text(encoding="utf-8"))
    names: list[str] = []
    for value in data.values():
        for item in value if isinstance(value, list) else [value]:
            names.append(item["output"])
    if len(names) != 47 or len(set(names)) != 47:
        raise RuntimeError("deliverable manifest is not a unique 47-file set")
    return names


def main() -> None:
    for name in ("release-gate.json", "release-qa.json", "visual-qa.json"):
        report_ok(name)
    names = declared_outputs()
    staged = [STAGING / name for name in names]
    if any(not path.exists() for path in staged):
        raise RuntimeError("staged release is incomplete")
    if ARCHIVE.exists():
        raise RuntimeError(f"archive target already exists: {ARCHIVE}")

    old = sorted(FORMAL.glob("*.pdf"))
    protected = FORMAL / "高中物理竞赛一轮讲义.pdf"
    if not protected.exists() or pages(protected) != 616:
        raise RuntimeError("protected 616-page formal book is missing or changed")

    ARCHIVE.mkdir(parents=True)
    archive_pdf = ARCHIVE / "pdf"
    archive_pdf.mkdir()
    shutil.copytree(ROOT / "build" / "complete", ARCHIVE / "build-complete-616")
    before = [
        {"name": path.name, "pages": pages(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in old
    ]
    for path in old:
        shutil.move(str(path), archive_pdf / path.name)

    try:
        for source in staged:
            shutil.copy2(source, FORMAL / source.name)
        actual = sorted(path.name for path in FORMAL.glob("*.pdf"))
        if actual != sorted(names):
            raise RuntimeError("formal directory does not equal declared 47-file set")
        for source in staged:
            target = FORMAL / source.name
            if sha256(source) != sha256(target):
                raise RuntimeError(f"published hash mismatch: {source.name}")
    except Exception:
        for path in FORMAL.glob("*.pdf"):
            path.unlink()
        for path in archive_pdf.glob("*.pdf"):
            shutil.move(str(path), FORMAL / path.name)
        raise

    after = [
        {"name": name, "pages": pages(FORMAL / name), "bytes": (FORMAL / name).stat().st_size,
         "sha256": sha256(FORMAL / name)}
        for name in names
    ]
    payload = {
        "archive": str(ARCHIVE),
        "formal_directory": str(FORMAL),
        "archived_pdf_count": len(before),
        "published_pdf_count": len(after),
        "protected_book_before": next(item for item in before if item["name"] == protected.name),
        "complete_book_after": next(item for item in after if item["name"] == protected.name),
        "before": before,
        "after": after,
        "ok": True,
    }
    (ARCHIVE / "publication-manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (GENERATED / "publication-report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({key: payload[key] for key in (
        "archive", "formal_directory", "archived_pdf_count", "published_pdf_count",
        "protected_book_before", "complete_book_after", "ok")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
