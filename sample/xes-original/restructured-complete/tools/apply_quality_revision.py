#!/usr/bin/env python3
"""Apply reviewed overlays to current source; never rebuild legacy input."""
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
STAGES=[("quality_revision_20261023.py",[]),("quality_revision_appendix.py",[]),
        ("quality_revision_advanced_mechanics.py",[]),("quality_revision_thermal.py",["--advanced"]),
        ("quality_revision_advanced_em.py",[]),("quality_revision_advanced_optics.py",[]),
        ("apply_final_review.py",[])]
for stage,options in STAGES:
    path=HERE/stage
    if not path.exists():raise SystemExit(f"Missing reviewed stage: {stage}")
    subprocess.run([sys.executable,str(path)]+options,cwd=HERE.parent,check=True)
