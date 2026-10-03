#!/usr/bin/env python3
"""Render every page for visual review; rendering is not an acceptance result."""
from __future__ import annotations

import argparse
from pathlib import Path
import fitz
from PIL import Image, ImageDraw
from quality import BOOK, load_json, sha256, write_json


def prepare_render_directory(work: Path, digest: str) -> Path:
    """Keep previous renders recoverable, but never mix different PDF versions."""
    target = work / "render"
    if target.exists():
        manifest = target / "manifest.json"
        previous = load_json(manifest).get("pdf_sha256") if manifest.exists() else None
        if previous != digest:
            history = work / "render-history"
            history.mkdir(exist_ok=True)
            token = previous[:16] if isinstance(previous, str) and previous.isalnum() else "unversioned"
            destination = history / token
            serial = 1
            while destination.exists():
                destination = history / f"{token}-{serial}"
                serial += 1
            target.rename(destination)
    target.mkdir(parents=True, exist_ok=True)
    return target


def render(tag: str, dpi: int) -> None:
    work = BOOK / "build" / tag
    pdf = work / "main.pdf"
    digest = sha256(pdf)
    target = prepare_render_directory(work, digest)
    write_json(target / "manifest.json", {"pdf_sha256": digest, "dpi": dpi,
               "status": "rendering"})
    cards = []
    with fitz.open(pdf) as doc:
        for index, page in enumerate(doc):
            number = index + 1
            page.get_pixmap(dpi=dpi, alpha=False).save(target / f"page-{number:03d}.png")
            pix = page.get_pixmap(matrix=fitz.Matrix(.38, .38), alpha=False)
            thumb = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            card = Image.new("RGB", (250, 350), "#e8e8e8")
            thumb.thumbnail((238, 326))
            card.paste(thumb, ((250 - thumb.width) // 2, 18))
            ImageDraw.Draw(card).text((8, 3), f"PDF page {number}", fill="black")
            cards.append(card)
        for start in range(0, len(cards), 12):
            batch = cards[start:start + 12]
            sheet = Image.new("RGB", (1000, 350 * ((len(batch) + 3) // 4)), "white")
            for offset, card in enumerate(batch):
                sheet.paste(card, ((offset % 4) * 250, (offset // 4) * 350))
            sheet.save(target / f"contact-{start // 12 + 1:02d}.jpg", quality=94)
        if sha256(pdf) != digest:
            raise RuntimeError("渲染期间PDF已改变，本次图像不能作为审阅证据")
        write_json(target / "manifest.json", {"pdf_sha256": digest, "dpi": dpi,
                   "pages": len(doc), "status": "rendered_not_reviewed"})
    print(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True, help="e.g. chapter-01 or volume-mechanics")
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    if Path(args.artifact).name != args.artifact or args.dpi < 150:
        parser.error("artifact 必须是内部构建目录名，dpi 不得低于 150")
    render(args.artifact, args.dpi)
