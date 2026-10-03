#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from quality import artifact_errors, review_errors, source_inventory_errors

BOOK = Path(__file__).resolve().parents[1]
BUILD = BOOK / "build"
ALLOWED_STATUS = {"mapped", "merged", "excluded"}
BANNED_STUDENT_TERMS = ("原扫描", "截图", "OCR", "标校说明", "重新创作", "原讲义", "重绘")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def without_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def load_ledger(errors: list[str]) -> list[dict]:
    rows: list[dict] = []
    path = BOOK / "source_ledger.jsonl"
    source_catalog = json.loads((BOOK / "sources.json").read_text(encoding="utf-8"))
    allowed_source_ids = {item["source_id"] for item in source_catalog["sources"]}
    allowed_source_ids.add("authorial_expansion")
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"来源台账第{number}行不是合法JSON：{exc}", errors)
            continue
        missing = {
            "source_id", "physical_page", "printed_page", "object_type",
            "source_number", "target_id", "status", "exclusion_reason", "notes",
        } - set(row)
        if missing:
            fail(f"来源台账第{number}行缺字段：{sorted(missing)}", errors)
        if row.get("status") not in ALLOWED_STATUS:
            fail(f"来源台账第{number}行状态非法：{row.get('status')!r}", errors)
        if row.get("status") == "excluded" and not row.get("exclusion_reason"):
            fail(f"来源台账第{number}行排除对象没有理由", errors)
        if row.get("status") != "excluded" and not row.get("target_id"):
            fail(f"来源台账第{number}行已映射对象没有target_id", errors)
        if row.get("source_id") not in allowed_source_ids:
            fail(f"来源台账第{number}行source_id不在来源目录中：{row.get('source_id')!r}", errors)
        rows.append(row)
    return rows


def question_errors(text: str) -> list[str]:
    errors = []
    questions = []
    for token in re.finditer(r"\\begin\{(examplebox|practicebox|solution)\}", text):
        kind = token.group(1)
        if kind != "solution":
            questions.append([kind, 0])
        elif not questions:
            errors.append("存在不属于任何题目的解答")
        else:
            questions[-1][1] += 1
    for n, (kind, solutions) in enumerate(questions, 1):
        if solutions != 1:
            errors.append(f"第{n}个{kind}有{solutions}个解答，应为1个")
    return errors


def tex_typo_errors(text: str) -> list[str]:
    """Catch silent rendering failures, not just fatal TeX syntax errors."""
    errors = []
    for match in re.finditer(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text):
        errors.append(f"正文含不可见控制字符U+{ord(match.group()):04X}")
    for match in re.finditer(r"(?<![\\A-Za-z])(?:sum|prod|frac|sqrt|partial)(?=[_^{])", text):
        line = text.count("\n", 0, match.start()) + 1
        errors.append(f"合并正文第{line}行疑似数学命令缺反斜杠：{match.group()}")
    # These names are harmless ordinary letters to TeX when their leading
    # backslash is lost, so compilation succeeds while the printed formula is
    # visibly wrong.  Keep this list deliberately restricted to control words
    # that do not occur as Chinese/English prose in this project.
    silent_controls = (
        "qquad", "quad", "Longrightarrow", "Rightarrow", "Leftarrow",
        "rightarrow", "leftarrow", "simeq", "geq", "leq", "neq",
        "infty", "cdots", "ldots",
    )
    pattern = r"(?<![\\A-Za-z])(?:" + "|".join(silent_controls) + r")(?![A-Za-z])"
    for match in re.finditer(pattern, text):
        line = text.count("\n", 0, match.start()) + 1
        errors.append(f"合并正文第{line}行疑似数学命令缺反斜杠：{match.group()}")
    for match in re.finditer(r"\^\{,", text):
        line = text.count("\n", 0, match.start()) + 1
        errors.append(f"合并正文第{line}行疑似间距命令误成上下标逗号：{match.group()}")
    return errors


def chapter_audit(chapter: int, require_review: bool = False) -> int:
    errors: list[str] = []
    chapter_id = f"r2ch{chapter:02d}:"
    paths = sorted((BOOK / "chapters").glob(f"ch{chapter:02d}*.tex"))
    if not paths:
        raise SystemExit(f"未找到第{chapter}章源文件")
    text = "\n".join(without_comments(path.read_text(encoding="utf-8")) for path in paths)
    errors.extend(tex_typo_errors(text))

    labels = re.findall(r"\\label\{([^}]+)\}", text)
    duplicates = [label for label, count in Counter(labels).items() if count > 1]
    if duplicates:
        fail("重复标签：" + "、".join(duplicates), errors)

    rows = load_ledger(errors)
    relevant = [row for row in rows if (row.get("target_id") or "").startswith(chapter_id)]
    for row in relevant:
        target = row["target_id"]
        if target not in labels:
            fail(f"台账目标不存在：{target}", errors)

    practice_count = len(re.findall(r"\\begin\{practicebox\}", text))
    example_count = len(re.findall(r"\\begin\{examplebox\}", text))
    solution_count = len(re.findall(r"\\begin\{solution\}", text))
    practice_labels = [label for label in labels if label.startswith(chapter_id + "pr:")]
    example_labels = [label for label in labels if label.startswith(chapter_id + "ex:")]
    if not (practice_count == len(practice_labels) and example_count == len(example_labels)
            and solution_count == practice_count + example_count):
        fail(
            f"习题/解答/标签数不一致：{practice_count}/{solution_count}/{len(practice_labels)}",
            errors,
        )
    errors.extend(question_errors(text))
    all_text = "\n".join(without_comments(p.read_text(encoding="utf-8"))
                          for p in (BOOK / "chapters").glob("ch*.tex"))
    all_labels = set(re.findall(r"\\label\{([^}]+)\}", all_text))
    for group in re.findall(r"\\(?:ref|eqref|pageref|autoref|cref|Cref)\{([^}]+)\}", text):
        for reference in group.split(","):
            if reference.strip() not in all_labels:
                fail(f"引用目标不存在：{reference.strip()}", errors)

    figure_labels = [label for label in labels if label.startswith(chapter_id + "fig:")]
    for label in figure_labels:
        if not re.search(r"\\(?:ref|eqref)\{" + re.escape(label) + r"\}", text):
            fail(f"插图未被正文或解答引用：{label}", errors)

    equation_labels = [label for label in labels if label.startswith(chapter_id + "eq:")]
    ledger_equations = {
        row["target_id"] for row in relevant
        if row.get("object_type") == "formula" or row.get("target_object_type") == "formula"
    }
    missing_equations = sorted(set(equation_labels) - ledger_equations)
    if missing_equations:
        fail("已编号公式缺来源映射：" + "、".join(missing_equations), errors)

    diagram_text = without_comments((BOOK / "chapters" / f"ch{chapter:02d}-diagrams.tex").read_text(encoding="utf-8"))
    if re.search(r"fill\s*=\s*white|fill\s*=\s*\{white\}", diagram_text):
        fail("技术图中存在白色标签底框", errors)
    if "\\includepdf" in text:
        fail("章节源文件使用了includepdf", errors)
    for term in BANNED_STUDENT_TERMS:
        if term in text:
            fail(f"学生正文存在编辑痕迹：{term}", errors)

    pdf = BUILD / f"chapter-{chapter:02d}" / "main.pdf"
    log = BUILD / f"chapter-{chapter:02d}" / "main.log"
    aux = BUILD / f"chapter-{chapter:02d}" / "main.aux"
    errors.extend(artifact_errors(BUILD / f"chapter-{chapter:02d}"))
    if not pdf.exists():
        fail(f"尚未生成PDF：{pdf}", errors)
    else:
        check = subprocess.run(["qpdf", "--check", str(pdf)], text=True, capture_output=True)
        if check.returncode:
            fail("qpdf检查失败：" + check.stderr.strip(), errors)
    if log.exists():
        bad = re.findall(
            r"^(?:.*(?:LaTeX Warning|Package .* Warning|Overfull|Missing character|multiply defined|undefined).*)$",
            log.read_text(encoding="utf-8", errors="ignore"),
            flags=re.MULTILINE,
        )
        if bad:
            fail("编译日志存在警告：\n" + "\n".join(bad[:20]), errors)

    # TeX 标签名也承担来源台账接口，不能只看页面上自动生成的序号。
    # 从 aux 反查实际显示编号，防止“图面编号正确、内部标签却指向另一幅图”的隐蔽错位。
    numbered_labels = {
        label for label in labels
        if re.fullmatch(re.escape(chapter_id) + r"(?:eq|fig|pr|ex):\d{3}", label)
    }
    if not aux.exists():
        fail(f"尚未生成辅助文件：{aux}", errors)
    else:
        aux_text = aux.read_text(encoding="utf-8", errors="ignore")
        pattern = re.compile(
            r"\\newlabel\{" + re.escape(chapter_id)
            + r"(eq|fig|pr|ex):(\d{3})\}\{\{" + str(chapter) + r"\.(\d+)\}"
        )
        seen: set[str] = set()
        for kind, suffix, printed in pattern.findall(aux_text):
            label = f"{chapter_id}{kind}:{suffix}"
            seen.add(label)
            if int(suffix) != int(printed):
                fail(f"内部标签与显示编号错位：{label} 实际显示为 {chapter}.{printed}", errors)
        missing_aux = sorted(numbered_labels - seen)
        if missing_aux:
            fail("编号标签没有写入aux：" + "、".join(missing_aux), errors)

    if require_review:
        errors.extend(review_errors(BUILD / f"chapter-{chapter:02d}"))
    print(f"第{chapter:02d}章：例题{example_count}道，习题{practice_count}道，解答{solution_count}份，"
          f"图{len(figure_labels)}幅，编号公式{len(equation_labels)}组，台账对象{len(relevant)}项。")
    if errors:
        print("验收失败：")
        for item in errors:
            print("- " + item)
        return 1
    print("自动检查通过；不代表来源、解答及图形的人工验收通过。")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chapter", type=int)
    group.add_argument("--all", action="store_true")
    parser.add_argument("--scope", choices=("main",), default="main")
    parser.add_argument("--sources", action="store_true")
    parser.add_argument("--require-review", action="store_true")
    args = parser.parse_args()
    result = 0
    if args.all:
        for chapter in range(1, 29):
            if not (BOOK / "chapters" / f"ch{chapter:02d}.tex").exists():
                print(f"第{chapter:02d}章尚未编写")
                result = 1
                continue
            result |= chapter_audit(chapter, args.require_review)
        text = "\n".join(without_comments(p.read_text(encoding="utf-8"))
                          for p in (BOOK / "chapters").glob("ch*.tex"))
        for pattern, name in ((r"\\label\{([^}]+)\}", "标签"),
                              (r"\\(?:newcommand|DeclareRobustCommand)\{\\([^}]+)\}", "宏")):
            duplicates = [key for key, n in Counter(re.findall(pattern, text)).items() if n > 1]
            if duplicates:
                print(f"跨章重复{name}：{duplicates}")
                result = 1
    else:
        result = chapter_audit(args.chapter, args.require_review)
    if args.sources:
        errors = source_inventory_errors()
        for error in errors:
            print(error)
        result |= bool(errors)
    raise SystemExit(int(result))


if __name__ == "__main__":
    main()
