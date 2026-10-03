"""Publish the four reviewed artifacts only; retain recoverable predecessors."""
import json
import shutil
from pathlib import Path
import build_review_ch29_ch30 as r

sha = r.common.sha
checks = json.loads((r.BASE / 'release-checks.json').read_text())
visual = json.loads((r.BASE / 'visual-review.json').read_text())
archive = json.loads((r.ARCHIVE / 'manifest.json').read_text())
physics = json.loads((r.BASE / 'physics-checks.json').read_text())
sources = json.loads((r.BASE / 'source-figure-map.json').read_text())
assert physics and all(value is True for value in physics.values())
assert all(sha(Path(s['path'])) == s['sha256'] for s in sources['sources'].values())
assert not (r.BASE / 'published.json').exists(), 'Already published; do not republish blindly.'
assert checks['protected_chapters'] == 30
assert all(sha(Path(p)) == h for p, h in archive['old_formal'].items())
assert all(sha(Path(p)) == h for p, h in archive['protected_generated_chapters'].items())
names = {k: v.replace('_含解答与解图', '') for k, v in r.OLD_NAMES.items()}
for key, name in names.items():
    p = r.BASE / key / f'{key}.pdf'
    c = checks['pdfs'][key]
    v = visual['pdfs'][key]
    assert sha(p) == c['sha256'] == v['sha256']
    assert v['review_complete']
    if key in ('volume5', 'main'):
        pixel = json.loads((r.BASE / f'{key}-pixel-regression.json').read_text())
        assert pixel['pdf_sha256'] == sha(p)
        assert all(not x.get('pixel_differences', []) for x in pixel['records'])
        assert sum(x.get('status') == 'matches_independent_chapter' for x in pixel['records']) == 2
    else:
        assert v['reviewed_pages'] == c['pages']
        assert v['reviewed_figures'] == {'ch29': 19, 'ch30': 23}[key]
    assert c['qpdf'] == 0 and c['all_fonts_embedded']
    assert not c['new_warnings'] and not c['replacement_chars']
    assert c['bookmark_destinations_valid'] and c['copies_text'] > 1000
    frozen = json.loads((p.parent / 'frozen-build.json').read_text())
    assert frozen['passes'] >= 2 and frozen['pdf_sha256'] == sha(p)
    assert all(sha(Path(src)) == h for src, h in frozen['source_hashes'].items())
    if key.startswith('ch'):
        assert not (r.common.FORMAL / name).exists()

published = {}
for key, name in names.items():
    src = r.BASE / key / f'{key}.pdf'
    target = r.common.FORMAL / name
    shutil.copy2(src, target)
    assert sha(src) == sha(target)
    published[str(target)] = sha(target)
    if name != r.OLD_NAMES[key]:
        old = r.common.FORMAL / r.OLD_NAMES[key]
        retired = r.ARCHIVE / 'superseded-filenames'
        retired.mkdir(exist_ok=True)
        assert not (retired / old.name).exists()
        shutil.move(str(old), retired / old.name)

manifest_path = r.book.GENERATED / 'deliverables.json'
manifest = json.loads(manifest_path.read_text())
for item in manifest['chapters']:
    if item['chapter'] in (29, 30):
        item['output'] = names[f"ch{item['chapter']}"]
for item in manifest['volumes']:
    if item['volume'] == 5:
        item['output'] = names['volume5']
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
(r.BASE / 'published.json').write_text(json.dumps(published, ensure_ascii=False, indent=2))
print(json.dumps(published, ensure_ascii=False, indent=2))
