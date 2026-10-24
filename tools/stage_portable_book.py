#!/usr/bin/env python3
"""Stage the editable book and its recorded media in a fresh verification folder."""
import argparse
import json
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
repo = args.repo.resolve()
target = args.output.resolve()
book = repo / "sample/xes-original/restructured-complete"
if target.exists():
    raise SystemExit("Use a fresh output directory to preserve earlier verification files.")
files = set()
excluded = {"build", "__pycache__", ".git"}
for path in (repo / "sample/xes-original").rglob("*"):
    if (path.is_file() and path.suffix in {".tex", ".sty", ".cls", ".py", ".bib", ".dat", ".csv", ".json", ".md"}
            and not excluded.intersection(path.relative_to(repo).parts)):
        files.add(path)
for line in (book / "build/quality-main/main.fls").read_text().splitlines():
    if not line.startswith("INPUT "):
        continue
    path = Path(line[6:])
    if not path.is_absolute():
        path = book / path
    path = path.resolve()
    if path.is_file() and path.is_relative_to(repo) and not excluded.intersection(path.relative_to(repo).parts):
        files.add(path)
for path in files:
    if path.read_bytes()[:100].startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise SystemExit(f"Unrestored LFS asset: {path.relative_to(repo)}")
for path in sorted(files):
    destination = target / path.relative_to(repo)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
print(json.dumps({"staged_files": len(files), "output": str(target)}, ensure_ascii=False))
