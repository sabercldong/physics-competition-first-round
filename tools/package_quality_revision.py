#!/usr/bin/env python3
"""Package the final PDF plus editable sources and recorded local media closure."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

parser=argparse.ArgumentParser()
parser.add_argument("--repo",type=Path,required=True)
parser.add_argument("--output",type=Path,required=True)
parser.add_argument("--date",default="20261024")
parser.add_argument("--report",type=Path,default=Path("audit/final_review_20261024"))
args=parser.parse_args()
repo=args.repo.resolve()
book=repo/"sample/xes-original/restructured-complete"
build=book/"build/quality-main"
report=repo/args.report
args.output.mkdir(parents=True,exist_ok=True)
files=set()
suffixes={".tex",".sty",".cls",".py",".bib",".dat",".csv",".json",".md"}
for p in (repo/"sample/xes-original").rglob("*"):
    if p.is_file() and p.suffix in suffixes and not {"build","__pycache__",".git"}.intersection(p.relative_to(repo).parts):
        files.add(p)
for name in ["review_lecture_quality.py","render_quality_pages.py","verify_revision_physics.py","package_quality_revision.py","verify_book_release.py"]:
    files.add(repo/"tools"/name)
for report_folder in [repo/"audit/quality_revision_20261023",report]:
    files.update(p for p in report_folder.rglob("*") if p.is_file() and p.suffix in {".json",".md"} and "intermediate-pass3" not in p.parts)

# -recorder output includes assets actually opened by TeX; include those even
# when their names do not have the normal text-source extensions.
for line in (build/"main.fls").read_text().splitlines():
    if not line.startswith("INPUT "):continue
    p=Path(line[6:])
    if not p.is_absolute():p=book/p
    p=p.resolve()
    if p.is_file() and p.is_relative_to(repo) and not {"build","__pycache__",".git"}.intersection(p.relative_to(repo).parts):
        files.add(p)

for p in files:
    if p.read_bytes()[:100].startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise SystemExit(f"Unrestored LFS asset: {p.relative_to(repo)}")

pdf=args.output/f"高中物理竞赛一轮讲义_终审版_{args.date}.pdf"
shutil.copy2(build/"main.pdf",pdf)
archive=args.output/f"一轮讲义_可编辑源码与TikZ_终审版_{args.date}.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):
        z.write(p,Path("physics-competition-first-round")/p.relative_to(repo))
    z.write(args.output/"编译与修订说明.md","physics-competition-first-round/README-精修版.md")
    z.write(args.output/"修订与验收报告.md","physics-competition-first-round/修订与验收报告.md")
    for name in ["source-review.json","figure-reference-review.json","pdf-review.json","physics-checks.json","compile-and-portability.json"]:
        z.write(report/name,"physics-competition-first-round/"+name)

for name in ["source-review.json","figure-reference-review.json","pdf-review.json","physics-checks.json","compile-and-portability.json"]:
    shutil.copy2(report/name,args.output/name)
manifest={"version":args.date,"source_files":len(files),"source_uncompressed_bytes":sum(p.stat().st_size for p in files),"deliverables":[]}
for p in [pdf,archive,args.output/"编译与修订说明.md",args.output/"修订与验收报告.md",
          *[args.output/name for name in ["source-review.json","figure-reference-review.json","pdf-review.json","physics-checks.json","compile-and-portability.json"]]]:
    manifest["deliverables"].append({"file":p.name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
(args.output/"交付清单.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({"source_files":len(files),"pdf_bytes":pdf.stat().st_size,"zip_bytes":archive.stat().st_size},ensure_ascii=False))
