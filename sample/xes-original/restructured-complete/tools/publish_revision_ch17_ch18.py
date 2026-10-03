"""Publish only the four verified chapter-17/18 revision artifacts."""
import json,shutil,hashlib
from pathlib import Path
import build_review_ch17_ch18 as r
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=json.loads((r.BASE/'release-checks.json').read_text())
visual=json.loads((r.BASE/'visual-review.json').read_text())
archive=json.loads((r.ARCHIVE/'manifest.json').read_text())
assert checks['protected_chapters']==30
assert all(sha(Path(p))==h for p,h in archive['old_formal'].items())
names=dict(r.OLD_NAMES)
for ch in ['ch17','ch18']:names[ch]=names[ch].replace('_含解答与解图','')
for key,name in names.items():
 p=r.BASE/key/f'{key}.pdf'
 assert sha(p)==checks['pdfs'][key]['sha256']==visual['pdfs'][key]['sha256']
 frozen=json.loads((r.BASE/key/'frozen-build.json').read_text())
 assert all(sha(Path(p))==h for p,h in frozen['source_hashes'].items())
 target=r.common.FORMAL/name
 if key in ['ch17','ch18']:assert not target.exists(),target
published={}
for key,name in names.items():
 src=r.BASE/key/f'{key}.pdf';target=r.common.FORMAL/name
 shutil.copy2(src,target);assert sha(src)==sha(target)
 published[str(target)]=sha(target)
 # Retire old suffixed filenames only after the verified replacement exists.
 if key in ['ch17','ch18']:
  old=r.common.FORMAL/r.OLD_NAMES[key]
  retired=r.ARCHIVE/'superseded-filenames';retired.mkdir(exist_ok=True)
  shutil.move(str(old),retired/old.name)
(r.BASE/'published.json').write_text(json.dumps(published,ensure_ascii=False,indent=2))
print(json.dumps(published,ensure_ascii=False,indent=2))
