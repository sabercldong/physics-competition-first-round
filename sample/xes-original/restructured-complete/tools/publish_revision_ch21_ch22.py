"""Publish only four reviewed artifacts, preserving recoverable predecessors."""
import json, shutil, hashlib
from pathlib import Path
import build_review_ch21_ch22 as r
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=json.loads((r.BASE/'release-checks.json').read_text())
visual=json.loads((r.BASE/'visual-review.json').read_text())
archive=json.loads((r.ARCHIVE/'manifest.json').read_text())
assert checks['protected_chapters']==30
assert all(sha(Path(p))==h for p,h in archive['old_formal'].items())
assert all(sha(Path(p))==h for p,h in archive['protected_generated_chapters'].items())
names={k:v.replace('_含解答与解图','') for k,v in r.OLD_NAMES.items()}
for key,name in names.items():
 p=r.BASE/key/f'{key}.pdf';c=checks['pdfs'][key]
 assert sha(p)==c['sha256']==visual['pdfs'][key]['sha256']
 if key in ('volume4','main'):
  pixel=json.loads((r.BASE/('volume-pixel-regression.json' if key=='volume4' else 'main-pixel-regression.json')).read_text())
  assert pixel['pdf_sha256']==sha(p) and all(not x['pixel_differences'] for x in pixel['records'])
 assert c['qpdf']==0 and c['all_fonts_embedded'] and not c['new_warnings'] and not c['replacement_chars']
 frozen=json.loads((r.BASE/key/'frozen-build.json').read_text())
 assert frozen['passes']>=2 and frozen['pdf_sha256']==sha(p)
 assert all(sha(Path(p))==h for p,h in frozen['source_hashes'].items() if not key.startswith('ch') or Path(p).stem==key)
 if key.startswith('ch'):assert not (r.common.FORMAL/name).exists()
published={}
for key,name in names.items():
 src=r.BASE/key/f'{key}.pdf';target=r.common.FORMAL/name
 shutil.copy2(src,target);assert sha(src)==sha(target)
 published[str(target)]=sha(target)
 if name!=r.OLD_NAMES[key]:
  old=r.common.FORMAL/r.OLD_NAMES[key]
  retired=r.ARCHIVE/'superseded-filenames';retired.mkdir(exist_ok=True)
  shutil.move(str(old),retired/old.name)
(r.BASE/'published.json').write_text(json.dumps(published,ensure_ascii=False,indent=2))
manifest_path=r.book.GENERATED/'deliverables.json'
manifest=json.loads(manifest_path.read_text())
for item in manifest['chapters']:
 if item['chapter'] in (21,22):item['output']=names[f"ch{item['chapter']}"]
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(published,ensure_ascii=False,indent=2))
