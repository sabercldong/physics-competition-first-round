#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from quality import fingerprints, sha256, write_json

BOOK = Path(__file__).resolve().parents[1]
WORKSPACE = BOOK.parents[1]
OUTPUT = WORKSPACE / "output" / "pdf" / "二轮"
BUILD = BOOK / "build"

VOLUME_NAMES = {
    "mechanics": "第1卷_力学",
    "thermal": "第2卷_热学与统计物理",
    "electromagnetism": "第3卷_电磁学",
    "optics": "第4卷_光学",
    "modern": "第5卷_近代物理",
    "advanced": "第6卷_高阶深化",
}


def load_book() -> dict:
    return json.loads((BOOK / "book.json").read_text(encoding="utf-8"))


def source_for(number: int) -> Path:
    return BOOK / "chapters" / f"ch{number:02d}.tex"


def source_for_item(item: dict) -> Path:
    if item.get("kind") == "advanced":
        return BOOK / "advanced" / f"{item['id'].lower()}.tex"
    return source_for(item["number"])


def wrapper(title: str, chapters: list[dict], include_toc: bool) -> str:
    blocks = []
    for item in chapters:
        source = source_for_item(item).as_posix()
        if item.get("kind") == "advanced":
            blocks.append(f"\\input{{{source}}}")
        else:
            blocks.append(
                f"\\setcounter{{chapter}}{{{item['number'] - 1}}}\n"
                f"\\input{{{source}}}"
            )
    inputs = "\n".join(blocks)
    toc = "\\tableofcontents\\clearpage" if include_toc else ""
    metadata_title = title or "高中物理竞赛二轮讲义"
    return rf"""\documentclass[UTF8,zihao=-4,oneside,openany]{{ctexbook}}
\input{{{(BOOK / 'style.tex').as_posix()}}}
\hypersetup{{pdftitle={{{metadata_title}}},pdfsubject={{{metadata_title}}}}}
\begin{{document}}
\frontmatter
\hypersetup{{pageanchor=false}}
\begin{{titlepage}}
\centering\vspace*{{0.26\textheight}}
{{\Huge\bfseries 高中物理竞赛二轮讲义\par}}
\vspace{{1.2em}}{{\Large {title}\par}}
\vfill
\end{{titlepage}}
\hypersetup{{pageanchor=true}}
{toc}
\mainmatter
{inputs}
\end{{document}}
"""


def compile_pdf(tag: str, title: str, chapters: list[dict], output_name: str, include_toc: bool) -> Path:
    missing = [source_for_item(item) for item in chapters if not source_for_item(item).exists()]
    if missing:
        raise SystemExit("尚未完成的章节源文件：\n" + "\n".join(str(path) for path in missing))
    work = BUILD / tag
    work.mkdir(parents=True, exist_ok=True)
    tex = work / "main.tex"
    tex.write_text(wrapper(title, chapters, include_toc), encoding="utf-8")
    command = [
        str(Path.home() / ".local" / "bin" / "latexmk"), "-g", "-norc", "-xelatex",
        "-interaction=nonstopmode", "-halt-on-error", "-synctex=1",
        f"-outdir={work}", str(tex),
    ]
    # Clear old success evidence before compiling. A failed build must never
    # inherit the acceptance record of a previous PDF at the same path.
    record = work / "artifact.json"
    write_json(record, {"status": "building", "items": chapters,
                        "successful_compile_passes": 0})
    inputs_before = fingerprints(chapters)
    for pass_number in (1, 2):
        with (work / f"compile-pass-{pass_number}.log").open("w", encoding="utf-8") as stream:
            subprocess.run(command, cwd=BOOK, stdout=stream, stderr=subprocess.STDOUT, check=True)
        print(f"{tag}: XeLaTeX pass {pass_number}/2", flush=True)
    pdf = work / "main.pdf"
    subprocess.run(["qpdf", "--check", str(pdf)], check=True)
    inputs_after = fingerprints(chapters)
    if inputs_after != inputs_before:
        raise SystemExit("构建期间源文件发生变更；本次结果不具备发布资格")
    write_json(record, {"status": "built_not_reviewed", "items": chapters,
                        "output_name": output_name, "inputs": inputs_after,
                        "successful_compile_passes": 2, "pdf_sha256": sha256(pdf)})
    return pdf


def main_jobs(book: dict) -> list[dict]:
    """The 34-artifact main-syllabus delivery contract, excluding H1--H6."""
    chapters = book["chapters"]
    jobs = []
    for item in chapters:
        n, title = item["number"], item["title"]
        jobs.append(dict(tag=f"chapter-{n:02d}", title=f"第{n:02d}章　{title}",
                         chapters=[item], include_toc=False,
                         output_name=f"高中物理竞赛二轮讲义_第{n:02d}章_{title}.pdf"))
    for volume, name in VOLUME_NAMES.items():
        if volume == "advanced":
            continue
        jobs.append(dict(tag=f"volume-{volume}", title=name.replace("_", "　"),
                         chapters=[c for c in chapters if c["volume"] == volume],
                         include_toc=True, output_name=f"高中物理竞赛二轮讲义_{name}.pdf"))
    jobs.append(dict(tag="complete-main", title="", chapters=chapters,
                     include_toc=True, output_name="高中物理竞赛二轮讲义.pdf"))
    return jobs


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chapter", type=int)
    group.add_argument("--unit", choices=tuple(f"H{i}" for i in range(1, 7)))
    group.add_argument("--volume", choices=tuple(VOLUME_NAMES))
    group.add_argument("--all", action="store_true")
    parser.add_argument("--scope", choices=("main", "complete"), default="main")
    parser.add_argument("--list", action="store_true", help="仅列出本次构建计划，不生成文件")
    args = parser.parse_args()
    book = load_book()
    chapters = book["chapters"]
    advanced = book["advanced_units"]

    if args.all and args.scope == "main":
        jobs = main_jobs(book)
        if args.list:
            print(json.dumps(jobs, ensure_ascii=False, indent=2))
            return
        missing = [source_for(c["number"]) for c in chapters if not source_for(c["number"]).exists()]
        if missing:
            raise SystemExit("主线尚未完成，拒绝生成不完整总册：\n" + "\n".join(map(str, missing)))
        for job in jobs:
            print(compile_pdf(**job), flush=True)
        return
    if args.list:
        raise SystemExit("--list 目前用于 --all --scope main")

    if args.chapter is not None:
        selected = [item for item in chapters if item["number"] == args.chapter]
        if not selected:
            raise SystemExit(f"不存在第{args.chapter}章")
        item = selected[0]
        title = f"第{item['number']:02d}章　{item['title']}"
        output = f"高中物理竞赛二轮讲义_第{item['number']:02d}章_{item['title']}.pdf"
        target = compile_pdf(f"chapter-{item['number']:02d}", title, selected, output, False)
    elif args.unit:
        selected = [item for item in advanced if item["id"] == args.unit]
        item = selected[0]
        title = f"{item['id']}　{item['title']}"
        output = f"高中物理竞赛二轮讲义_{item['id']}_{item['title']}.pdf"
        target = compile_pdf(f"advanced-{item['id'].lower()}", title, selected, output, False)
    elif args.volume:
        pool = advanced if args.volume == "advanced" else chapters
        selected = [item for item in pool if item["volume"] == args.volume]
        title = VOLUME_NAMES[args.volume].replace("_", "　")
        target = compile_pdf(f"volume-{args.volume}", title, selected,
                             f"高中物理竞赛二轮讲义_{VOLUME_NAMES[args.volume]}.pdf", True)
    else:
        target = compile_pdf("complete", "主线与高阶深化", chapters + advanced,
                             "高中物理竞赛二轮讲义_主线与高阶深化.pdf", True)
    print(target)


if __name__ == "__main__":
    main()
