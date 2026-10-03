#!/usr/bin/env python3
"""Create high-resolution review crops for every numbered teaching figure.

The crops are review aids only.  A human must still inspect geometry, labels,
directions and the surrounding text that cites each figure.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from quality import BOOK, sha256, write_json


def figure_captions(page: fitz.Page, chapter: int):
    pattern = re.compile(rf"图\s*{chapter}\.(\d+)：")
    found = []
    for block in page.get_text("blocks"):
        text = block[4].replace("\n", " ")
        match = pattern.search(text)
        if match:
            found.append((int(match.group(1)), fitz.Rect(block[:4]), text.strip()))
    return sorted(found)


def render(artifact: str, chapter: int, dpi: int, height: float) -> Path:
    work = BOOK / "build" / artifact
    pdf = work / "main.pdf"
    digest = sha256(pdf)
    target = work / "figure-review"
    target.mkdir(parents=True, exist_ok=True)
    figures = []
    with fitz.open(pdf) as doc:
        for page_number, page in enumerate(doc, 1):
            captions = figure_captions(page, chapter)
            for number, rect, caption in captions:
                clip = fitz.Rect(42, max(35, rect.y0 - height), page.rect.width - 42,
                                 min(page.rect.height - 35, rect.y1 + 18))
                pix = page.get_pixmap(clip=clip, dpi=dpi, alpha=False)
                path = target / f"figure-{number:02d}.png"
                pix.save(path)
                figures.append({"figure": number, "pdf_page": page_number,
                                "caption": caption, "clip": list(clip),
                                "path": str(path.relative_to(BOOK))})
    numbers = [item["figure"] for item in figures]
    if numbers != list(range(1, max(numbers, default=0) + 1)):
        raise SystemExit(f"图号不连续或有重复：{numbers}")
    cards = []
    for item in figures:
        picture = Image.open(BOOK / item["path"]).convert("RGB")
        picture.thumbnail((470, 330))
        card = Image.new("RGB", (500, 370), "white")
        card.paste(picture, ((500-picture.width)//2, 26))
        ImageDraw.Draw(card).text((8, 6), f"图 {chapter}.{item['figure']}  PDF p.{item['pdf_page']}", fill="black")
        cards.append(card)
    for start in range(0, len(cards), 8):
        batch = cards[start:start+8]
        sheet = Image.new("RGB", (1000, 370*((len(batch)+1)//2)), "white")
        for offset, card in enumerate(batch):
            sheet.paste(card, ((offset % 2)*500, (offset // 2)*370))
        sheet.save(target / f"contact-{start//8+1:02d}.jpg", quality=94)
    write_json(target / "manifest.json", {"pdf_sha256": digest, "dpi": dpi,
               "status": "rendered_not_reviewed", "figures": figures})
    print(target)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--chapter", required=True, type=int)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--height", type=float, default=230,
                        help="points retained above each caption")
    args = parser.parse_args()
    if Path(args.artifact).name != args.artifact or args.dpi < 150 or args.height < 80:
        parser.error("invalid review render parameters")
    render(args.artifact, args.chapter, args.dpi, args.height)
