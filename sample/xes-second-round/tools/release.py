#!/usr/bin/env python3
"""Release all 34 main-syllabus PDFs together, never a partial batch."""
from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import fitz
from build import BOOK, BUILD, OUTPUT, WORKSPACE, load_book, main_jobs
from quality import load_json, review_errors, source_inventory_errors, sha256, write_json


def pdf_errors(path: Path, with_toc: bool) -> list[str]:
    errors = []
    if not path.exists():
        return [f"缺PDF：{path}"]
    proc = subprocess.run(["qpdf", "--check", str(path)], capture_output=True, text=True)
    if proc.returncode:
        errors.append(f"PDF结构检查失败：{path}")
    fonts = subprocess.check_output(["pdffonts", str(path)], text=True).splitlines()[2:]
    if not fonts or any(not re.search(r"\byes\s+(?:yes|no)\s+yes\s+\d+\s+\d+\s*$", f) for f in fonts):
        errors.append(f"存在未嵌入或无Unicode映射字体：{path}")
    with fitz.open(path) as doc:
        if not doc.get_toc() or any(not 1 <= row[2] <= len(doc) for row in doc.get_toc()):
            errors.append(f"书签缺失或目标页异常：{path}")
        if any(len(page.get_text().strip()) < 10 for page in doc):
            errors.append(f"存在需核查的空白页或不可复制文字页面：{path}")
        if with_toc and not any("目录" in page.get_text().replace(" ", "") for page in doc):
            errors.append(f"合订本缺目录：{path}")
    return errors


def preflight() -> list[str]:
    errors = source_inventory_errors()
    jobs = main_jobs(load_book())
    if len(jobs) != 34 or len({j['output_name'] for j in jobs}) != 34:
        errors.append("交付契约必须为28章、5卷、1总册，共34个唯一文件")
    for job in jobs:
        work = BUILD / job["tag"]
        errors.extend(review_errors(work))
        if not (work / "artifact.json").exists():
            continue
        artifact = load_json(work / "artifact.json")
        if artifact.get("output_name") != job["output_name"] or artifact.get("items") != job["chapters"]:
            errors.append(f"{job['tag']}：构建内容或正式文件名与交付契约不一致")
        if artifact.get("status") != "built_not_reviewed":
            errors.append(f"{job['tag']}：未完成有效构建")
        log = work / "main.log"
        if not log.exists() or re.search(r"Warning:|Overfull|Missing character|undefined|multiply defined",
                                         log.read_text(encoding="utf-8", errors="ignore")):
            errors.append(f"{job['tag']}：缺有效日志或仍有编译警告")
        errors.extend(pdf_errors(work / "main.pdf", job["include_toc"]))
    check = subprocess.run(["python3", str(BOOK / "tools/audit.py"), "--all", "--scope", "main"],
                           capture_output=True, text=True, cwd=BOOK)
    if check.returncode:
        errors.append("章节/引用自动审查未通过：\n" + check.stdout + check.stderr)
    return errors


def publish() -> Path:
    jobs = main_jobs(load_book())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".r2-release-", dir=OUTPUT.parent) as temporary:
        stage = Path(temporary) / "二轮"
        stage.mkdir()
        # Preserve unrelated user files in the same directory. Superseded
        # lecture PDFs move to the recoverable archive during the final swap.
        if OUTPUT.exists():
            for item in OUTPUT.iterdir():
                if item.name.startswith("高中物理竞赛二轮讲义") and item.suffix == ".pdf":
                    continue
                if item.is_dir():
                    shutil.copytree(item, stage / item.name)
                else:
                    shutil.copy2(item, stage / item.name)
        hashes = {}
        for job in jobs:
            source = BUILD / job["tag"] / "main.pdf"
            destination = stage / job["output_name"]
            shutil.copy2(source, destination)
            hashes[job["output_name"]] = sha256(destination)
            if hashes[job["output_name"]] != load_json(BUILD / job["tag"] / "artifact.json")["pdf_sha256"]:
                raise RuntimeError("复制后的PDF哈希不一致，停止发布")
        errors = preflight()
        if errors:
            raise RuntimeError("发布前状态已变化：\n" + "\n".join(errors))
        archive = WORKSPACE / "archive" / (datetime.now().strftime("%Y-%m-%d-%H%M%S") + "-r2-main-release")
        archive.mkdir(parents=True, exist_ok=False)
        shutil.copytree(BOOK, archive / "source", ignore=shutil.ignore_patterns("build", "__pycache__"))
        write_json(archive / "release.json", {"scope": "main", "artifacts": hashes})
        previous = archive / "pdf"
        had_previous = OUTPUT.exists()
        if had_previous:
            os.replace(OUTPUT, previous)
        try:
            os.replace(stage, OUTPUT)
        except BaseException:
            if had_previous and previous.exists() and not OUTPUT.exists():
                os.replace(previous, OUTPUT)
            raise
    return archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("main",), default="main")
    parser.add_argument("--publish", action="store_true", help="全部通过后才归档旧稿并统一发布")
    args = parser.parse_args()
    errors = preflight()
    if errors:
        print("发布门未通过；正式目录保持不动。")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    if not args.publish:
        print("34份成品及来源、人工审阅证据全部通过；本次仅检查，没有发布。")
        return
    print("发布完成，旧稿及源文件归档于：", publish())


if __name__ == "__main__":
    main()
