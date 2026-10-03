"""Render manually selected chapter-2 diagram neighborhoods for inspection."""
import re
from pathlib import Path
import fitz
from quality import BOOK, sha256, write_json


def main():
    work = BOOK / "build/chapter-02"
    destination = work / "figure-review"
    destination.mkdir(exist_ok=True)
    pdf = work / "main.pdf"
    heights = {1: 175, 2: 245, 3: 280, 4: 170, 5: 190, 6: 170,
               7: 210, 8: 245, 9: 230, 10: 215, 11: 245, 12: 115}
    entries = []
    with fitz.open(pdf) as document:
        for page_number, page in enumerate(document, 1):
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    text = "".join(span["text"] for span in line["spans"])
                    match = re.match(r"图\s*2\.(\d+)：", text)
                    if not match:
                        continue
                    number = int(match[1])
                    bottom = line["bbox"][3] + 4
                    rectangle = fitz.Rect(50, max(40, bottom - heights[number]), 546, bottom)
                    image = destination / f"figure-{number:02d}.png"
                    page.get_pixmap(dpi=300, clip=rectangle, alpha=False).save(image)
                    entries.append({"figure": number, "pdf_page": page_number,
                                    "clip": list(rectangle), "path": str(image.relative_to(BOOK))})
    if sorted(e["figure"] for e in entries) != list(range(1, 13)):
        raise RuntimeError("Not all 12 caption neighborhoods found")
    write_json(destination / "manifest.json",
               {"pdf_sha256": sha256(pdf), "status": "rendered_not_reviewed", "figures": entries})
    print(entries)


if __name__ == "__main__":
    main()
