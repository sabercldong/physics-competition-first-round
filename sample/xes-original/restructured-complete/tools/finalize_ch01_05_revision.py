"""Verify and publish only the first five chapters and volume 1, recoverably."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import fitz

BOOK = Path(__file__).resolve().parents[1]
ROOT = BOOK.parents[2]
BASE = BOOK / 'build/revision-ch01-05-20260923'
ARCHIVE = ROOT / 'archive/20260923-ch01-05-before-revision'
COUNTS = {1: 36, 2: 21, 3: 51, 4: 32, 5: 31}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def targets():
    old = json.loads((ARCHIVE / 'manifest.json').read_text())['formal']
    result = {}
    for n in COUNTS:
        result[f'ch{n:02}'] = next(Path(p) for p in old if f'第{n:02}章_' in p)
    result['volume1'] = next(Path(p) for p in old if '第1卷_' in p)
    return result

def verify():
    old = json.loads((ARCHIVE / 'manifest.json').read_text())['formal']
    report = {'scope': 'ch01-ch05 and volume1 only', 'artifacts': {},
              'source_inputs': {}, 'review_reports': {}, 'archive': str(ARCHIVE)}
    for target, dst in targets().items():
        path = BASE / target / (target + '.pdf')
        doc = fitz.open(path)
        text = '\n'.join(p.get_text() for p in doc)
        log = (BASE / target / (target + '.log')).read_text(errors='replace')
        assert not re.search(r'Overfull|Underfull|Missing character|undefined|multiply defined', log), target
        assert '\ufffd' not in text and '??' not in text, target
        check = subprocess.run(['qpdf', '--check', str(path)], capture_output=True, text=True)
        assert check.returncode == 0, check.stdout + check.stderr
        fonts = subprocess.run(['pdffonts', str(path)], capture_output=True, text=True, check=True).stdout
        # pdffonts: embedded/subset/unicode are the three fields before the object ID.
        font_rows = [line.split() for line in fonts.splitlines()[2:] if line.strip()]
        assert font_rows and all(row[-5] == 'yes' for row in font_rows), fonts
        assert doc.get_toc(), target
        assert all(1 <= row[2] <= len(doc) for row in doc.get_toc())
        assert all(p.get_text().strip() for p in doc), target
        for n in (1, 2):
            pass_log = BASE / target / f'verify-pass-{n}.txt'
            assert pass_log.exists() and 'Output written on' in pass_log.read_text(errors='replace')
        assert sha(dst) == old[str(dst)], ('Formal changed since backup', dst)
        assert sha(ARCHIVE / 'pdf' / dst.name) == old[str(dst)]
        report['artifacts'][target] = dict(pages=len(doc), sha256=sha(path),
            formal_path=str(dst), qpdf_ok=True, fonts_embedded=True, tex_warnings=0,
            bookmarks=doc.get_toc(), qpdf_output=check.stdout + check.stderr)
        for line in (BASE / target / (target + '.fls')).read_text(errors='replace').splitlines():
            if not line.startswith('INPUT '):
                continue
            source = Path(line[6:])
            if not source.is_absolute():
                source = BOOK / source
            source = source.resolve()
            if source.is_file() and source.is_relative_to(ROOT) and source.suffix.lower() in {
                    '.tex', '.sty', '.cls', '.png', '.jpg', '.jpeg', '.pdf', '.map', '.csv', '.dat'}:
                if not source.is_relative_to(BASE):
                    report['source_inputs'][str(source)] = sha(source)

    correspondence = json.loads((BASE / 'source-correspondence.json').read_text())
    for row in correspondence:
        n = row['chapter']
        assert row['examples'] == row['solutions'] == COUNTS[n]
        assert row['source_sha256'] == sha(BOOK / f'generated/chapters/ch{n:02}.tex')
    ledger = json.loads((ROOT / 'build/audit-ch01-05-20260923/geometry/source-figure-ledger.json').read_text())
    mapping = json.loads((BOOK.parent / 'kinematics-supplement/data/question-figure-map.json').read_text())
    assert Counter(x['source_example'] for x in ledger['question_figures']) == Counter(x['source_example'] for x in mapping)
    assert Counter(x['source_example'] for x in mapping) == Counter(x for r in correspondence for x in r['source_question_figures'])
    for item in mapping:
        source = next(x for x in ledger['question_figures'] if x['source_example'] == item['source_example'])
        assert item['source_pages'] == source['source_physical_pages']
    report['questions'] = report['solutions'] = 171
    report['source_question_figure_groups'] = len(mapping)
    report['blank_question_template_groups'] = sum(x['source_blank_template'] for x in ledger['question_figures'])

    # Check every body page of volume 1 against the standalone PDF, including graphics.
    volume = fitz.open(BASE / 'volume1/volume1.pdf')
    offset = 2
    compared = []
    for n in range(1, 5):
        doc = fitz.open(BASE / f'ch{n:02}/ch{n:02}.pdf')
        for i in range(1, len(doc)):
            clip = fitz.Rect(30, 50, 565, 790)  # omit running header/footer only
            a, b = doc[i], volume[offset + i - 1]
            assert re.sub(r'\s', '', a.get_text(clip=clip)) == re.sub(r'\s', '', b.get_text(clip=clip)), (n, i)
            pa = a.get_pixmap(matrix=fitz.Matrix(1, 1), clip=clip, alpha=False)
            pb = b.get_pixmap(matrix=fitz.Matrix(1, 1), clip=clip, alpha=False)
            assert pa.samples == pb.samples, ('Body raster differs', n, i + 1)
            compared.append([n, i + 1, offset + i])
        offset += len(doc) - 1
    assert offset == len(volume)
    report['volume1_body_page_comparisons'] = compared
    report['volume1_body_text_and_pixels_identical'] = True
    # Review front matter separately; it is not covered by body comparisons.
    for i in range(2):
        volume[i].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(BASE / 'visual' / f'volume1-front-{i+1}.png')

    for name in ['geometry-review.md', 'semantic-review.md', 'text-review.md', 'layout-review.md',
                 'text-final-two-labels.md']:
        path = BASE / name
        assert path.exists() and ('复验' in path.read_text() or 'Recheck' in path.read_text())
        report['review_reports'][str(path)] = sha(path)
    report['note'] = ('The script checks structure and correspondence, not human review approval. '
                      'Publication additionally requires an explicit root-reviewed approval bound to these PDF hashes.')
    (BASE / 'release-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v['pages'] for k, v in report['artifacts'].items()}, ensure_ascii=False))
    print('149 body pages: volume text and raster match standalone chapters 1–4 exactly.')

def publish():
    verification = json.loads((BASE / 'release-verification.json').read_text())
    approval = json.loads((BASE / 'root-review-approval.json').read_text())
    assert approval['approved'] and approval['verification_sha256'] == sha(BASE / 'release-verification.json')
    for path, digest in verification['source_inputs'].items():
        assert sha(path) == digest, ('Source modified after verification', path)
    for path, digest in verification['review_reports'].items():
        assert sha(path) == digest, ('Review changed after verification', path)
    old = json.loads((ARCHIVE / 'manifest.json').read_text())['formal']
    for target, dst in targets().items():
        assert sha(BASE / target / (target + '.pdf')) == verification['artifacts'][target]['sha256']
        assert sha(dst) == old[str(dst)]
    record = {'published_at': datetime.datetime.now().astimezone().isoformat(),
              'archive': str(ARCHIVE), 'files': {}, 'shared_volume2_main': 'delegated to coordinated chapter7–10 task; not replaced here'}
    for target, dst in targets().items():
        src = BASE / target / (target + '.pdf')
        tmp = dst.with_suffix('.revision-tmp')
        assert not tmp.exists()
        shutil.copy2(src, tmp)
        assert sha(tmp) == sha(src)
        os.replace(tmp, dst)
        record['files'][str(dst)] = {'sha256': sha(dst), 'pages': verification['artifacts'][target]['pages'], 'source': str(src)}
    (BASE / 'publication.json').write_text(json.dumps(record, ensure_ascii=False, indent=2))
    print(json.dumps(record, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify()
    if args.publish:
        publish()
