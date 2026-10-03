"""Run figure-skill source checks; preserve warnings rather than declaring visual PASS."""
import json,subprocess
from pathlib import Path
BOOK=Path(__file__).resolve().parents[1]
BASE=BOOK/'build/modern-source-revision-20260923'
REF=Path('/Users/dongxingxi/.codex/skills/thesis-figure-skill/references')
NAMES=['particle-lifetime','photoelectric-apparatus','hydrogen-two-processes',
 'accelerator-source','elliptic-current-source','threshold-frames','velocity-two-frames',
 'closed-clock-source','recoil-resonance-source','photon-scattering-source',
 'photon-wavevector-locus','rutherford-recoil-source','neutron-interferometer-source',
 'rod-telescope-source','pursuit-source']
rows=[]
for name in NAMES:
    p=BOOK/f'assets/diagrams-modern/{name}.tex'
    row={'asset':str(p.relative_to(BOOK)),'checks':{}}
    for kind,args in [('syntax',['tikz-validator.py']),('design',['tikz-design-linter.py'])]:
        cmd=['python3',str(REF/args[0]),str(p)]
        if kind=='design':cmd+=['--type','simple']
        result=subprocess.run(cmd,capture_output=True,text=True)
        row['checks'][kind]={'returncode':result.returncode,'output':result.stdout+result.stderr}
    rows.append(row)
(BASE/'drawing-source-checks.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps([{'asset':r['asset'],'returncodes':{k:v['returncode'] for k,v in r['checks'].items()}} for r in rows],ensure_ascii=False))
