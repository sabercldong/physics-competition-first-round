#!/usr/bin/env python3
"""Render selected PDF pages and a contact sheet for visual review."""
from pathlib import Path
import argparse
import fitz
from PIL import Image, ImageOps, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    pdf = fitz.open(args.pdf)
    numbers = []
    for token in args.pages.split(","):
        if "-" in token:
            a, b = map(int, token.split("-"))
            numbers.extend(range(a, b + 1))
        else:
            numbers.append(int(token))
    tiles = []
    for number in numbers:
        page = pdf[number - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.25, 1.25), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.save(args.output / f"page-{number:04d}.png")
        tile = Image.new("RGB", (310, 458), "#e7e7e7")
        thumb = ImageOps.contain(img, (300, 425))
        tile.paste(thumb, ((310 - thumb.width) // 2, 25))
        ImageDraw.Draw(tile).text((8, 7), f"PDF page {number}", fill="black")
        tiles.append(tile)
    for offset in range(0, len(tiles), 12):
        group = tiles[offset:offset + 12]
        sheet = Image.new("RGB", (310 * 3, 458 * ((len(group) + 2) // 3)), "white")
        for i, tile in enumerate(group):
            sheet.paste(tile, ((i % 3) * 310, (i // 3) * 458))
        sheet.save(args.output / f"contact-{offset // 12 + 1:02d}.png")
    print(f"rendered {len(numbers)} pages to {args.output}")


if __name__ == "__main__":
    main()
