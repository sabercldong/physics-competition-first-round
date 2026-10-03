"""Combine the seven current chapter PDFs without changing their pages."""
from pathlib import Path
import hashlib
import json
import subprocess
import shutil

import fitz
from PIL import Image, ImageDraw

BOOK = Path(__file__).resolve().parent.parent
ROOT = BOOK.parents[2]
OUT = ROOT / 'output/pdf/高中物理竞赛一轮讲义_第1—7章.pdf'
WORK = BOOK / 'build/preview-chapters-01-07'
WORK.mkdir(parents=True, exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

merged = fitz.open()
toc, records, pending_links = [], [], []
for number in range(1, 8):
    candidates = list((ROOT / 'output/pdf').glob(f'高中物理竞赛一轮讲义_第{number:02d}章_*.pdf'))
    assert len(candidates) == 1, candidates
    path = candidates[0]
    with fitz.open(path) as source:
        offset = merged.page_count
        merged.insert_pdf(source, links=False, annots=True)
        for i, page in enumerate(source):
            for link in page.get_links():
                copied = {k: v for k, v in link.items() if k not in ('xref', 'id', 'nameddest')}
                if link['kind'] == fitz.LINK_NAMED and 'nameddest' in link:
                    destination, x, y = source.resolve_link('#nameddest=' + link['nameddest'])
                    assert 0 <= destination < source.page_count, link
                    copied.update(kind=fitz.LINK_GOTO, page=offset+destination, to=fitz.Point(x, y))
                elif link['kind'] == fitz.LINK_GOTO:
                    copied['page'] += offset
                pending_links.append((offset+i, copied))
        source_toc = source.get_toc()
        assert source_toc and source_toc[0][0] == 1
        for level, title, page in source_toc:
            assert 1 <= page <= source.page_count
            if level == 1:
                title = f'第{number}章　{title}'
            toc.append([level, title, offset + page])
        records.append(dict(chapter=number, source=str(path), sha256=sha(path),
                            pages=source.page_count, first_page=offset+1,
                            last_page=merged.page_count))
for page_index, link in pending_links:
    merged[page_index].insert_link(link)
merged.set_toc(toc)
merged.set_metadata({'title': '高中物理竞赛一轮讲义·第1—7章',
                     'subject': '第1—7章合订', 'creator': 'PyMuPDF'})
staged = WORK / OUT.name
merged.save(staged, garbage=3, deflate=True)
merged.close()

with fitz.open(staged) as check:
    assert check.page_count == sum(x['pages'] for x in records)
    assert check.get_toc() == toc
    for record in records:
        with fitz.open(record['source']) as source:
            for i, original in enumerate(source):
                combined = check[record['first_page'] - 1 + i]
                assert original.rect == combined.rect
                assert original.get_text() == combined.get_text(), (record['chapter'], i+1, 'text')
                assert original.get_pixmap(matrix=fitz.Matrix(1, 1)).samples == combined.get_pixmap(matrix=fitz.Matrix(1, 1)).samples, (record['chapter'], i+1, 'image')
                old_links, new_links = original.get_links(), combined.get_links()
                assert len(old_links) == len(new_links), (record['chapter'], i+1, 'links')
                for old, new in zip(old_links, new_links):
                    if old['kind'] == fitz.LINK_NAMED and 'nameddest' in old:
                        destination, x, y = source.resolve_link('#nameddest=' + old['nameddest'])
                        assert new['kind'] == fitz.LINK_GOTO
                        assert new['page'] == destination + record['first_page'] - 1
                        assert abs(new['to'] - fitz.Point(x, y)) < .01
                    else:
                        assert old['kind'] == new['kind']
                        if old['kind'] == fitz.LINK_GOTO:
                            assert new['page'] == old['page'] + record['first_page'] - 1
        assert sha(Path(record['source'])) == record['sha256']
    # Boundary-page sheets: each chapter title, first content page and last page.
    for start in range(0, 7, 4):
        group = records[start:start+4]
        sheet = Image.new('RGB', (3*310, len(group)*450), 'white')
        draw = ImageDraw.Draw(sheet)
        for row, record in enumerate(group):
            for col, page in enumerate([record['first_page'], record['first_page']+1, record['last_page']]):
                pix = check[page-1].get_pixmap(matrix=fitz.Matrix(.5, .5), alpha=False)
                tile = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                tile.thumbnail((300, 420))
                sheet.paste(tile, (col*310, row*450+25))
                draw.text((col*310+8, row*450+6), f'Chapter {record["chapter"]} / PDF page {page}', fill='black')
        sheet.save(WORK / f'boundaries-{start+1}.png')

result = subprocess.run(['qpdf', '--check', str(staged)], capture_output=True, text=True)
assert result.returncode == 0, result.stdout + result.stderr
font_result = subprocess.run(['pdffonts', str(staged)], capture_output=True, text=True, check=True)
font_lines = font_result.stdout.splitlines()[2:]
assert font_lines and all(line.split()[-5] == 'yes' for line in font_lines), font_result.stdout
assert not OUT.exists() or sha(OUT) == sha(staged), f'Existing different preview requires archiving first: {OUT}'
shutil.copy2(staged, OUT)
report = {'output': str(OUT), 'sha256': sha(OUT), 'pages': sum(x['pages'] for x in records),
          'sources': records, 'bookmarks': len(toc), 'qpdf_check': True,
          'all_fonts_embedded': True, 'all_pages_text_and_raster_unchanged': True,
          'all_links_preserved': True, 'source_pdfs_unchanged': True}
(WORK / 'merge-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False, indent=2))
