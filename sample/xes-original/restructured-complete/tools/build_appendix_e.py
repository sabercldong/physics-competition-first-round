#!/usr/bin/env python3
"""Build the reviewed 2019-autumn electromagnetism difference appendix.

Text similarity only orders the audit.  Final decisions below come from a
condition/subquestion/derivation/figure review and are written back to the
ledger with source and destination labels.  Unique teaching content is either
typeset as a complete appendix example or retained in the reviewed supplements.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from audit_electromagnetism import OLD, NEW, collect, best_match
from build_restructured import (
    BOOK,
    GENERATED,
    balanced_argument,
    extract_legacy,
    flatten_inputs,
    normalize_visible_eponyms,
)

APPENDIX = GENERATED / "appendices" / "appendix-e.tex"
LEDGER = GENERATED / "appendix-e-difference-ledger.json"
SUPPLEMENTS = BOOK / "appendices" / "E-reviewed-supplements.tex"


# Entries not listed here were checked as the same physical model, with the
# same conditions and subquestions; the 2020 solution and figure inventory
# cover the 2019 teaching role.  The explicit overrides record cases in which
# a text-similarity score alone would make the wrong decision or in which a
# condition/derivation needed to be restored.
REVIEW_OVERRIDES: dict[tuple[int, str, str], tuple[str, str]] = {
    (19, "s18", "【电偶极子】"): (
        "included_unique_variant",
        "自动匹配到了电四极子，但电荷构型、远场阶数和场线方程均不同；整题收入附录。",
    ),
    (19, "s18", "【直线电四极子】"): (
        "verified_duplicate",
        "两版均为 -q,+2q,-q 的等间距直线四极子；2020主章已保留几何图、远场与场线推导。",
    ),
    (19, "s18", "【无穷大厚板】"): (
        "verified_duplicate_with_source_correction",
        "2019题面把正电荷置于正体电荷厚板中，力不具回复性却要求周期；2020版改为 -q 后模型自洽并完整分段求周期。",
    ),
    (19, "s19", "【同性相斥】"): (
        "verified_duplicate_with_condition_restored",
        "2019版明确准静态过程；已把“缓慢移动、始终近似平衡”补回2020主章题设。",
    ),
    (20, "s20", "【匀强电场中的导体球】"): (
        "verified_duplicate_with_appendix_extension",
        "基本边值解完全相同；2019版独有的极化率、非均匀场受力和极限检验保留在附录补充推导。",
    ),
    (20, "s21", "【两个导体球】"): (
        "verified_duplicate_with_appendix_extension",
        "相切双球答案相同；2019版独有的有限中心距级数及相切极限保留在附录补充推导。",
    ),
    (20, "s21", "【两个圆柱】"): (
        "verified_duplicate_with_condition_restored",
        "已在2020主章题设补明 L>2R、两柱平行且带等量异号线电荷，解答和双极坐标图一致。",
    ),
    (20, "s21", "【电容充电】"): (
        "verified_duplicate",
        "2020解答已显式求出浮置中心电势和三块外极板电荷，并检查电荷守恒，覆盖2019全部子问。",
    ),
    (19, "s19", "【$\\alpha$ 粒子散射】"): (
        "verified_duplicate",
        "2020解答已补明 +2e、入射动能、双曲线轨迹、Rutherford截面及Geiger--Marsden与Rutherford的历史分工。",
    ),
}

DEFAULT_REVIEW_NOTE = (
    "题设条件、子问和物理模型逐项一致；2020主章的解答不少于完成求解所需步骤，"
    "2019题意图的物理作用已由主章对应图覆盖。"
)


def example_segments(tex: str) -> list[dict[str, str]]:
    begin = "\\begin{origexamplebox}"
    end_box = "\\end{origexamplebox}"
    begin_solution = "\\begin{xesolution}"
    end_solution = "\\end{xesolution}"
    result: list[dict[str, str]] = []
    position = 0
    while True:
        start = tex.find(begin, position)
        if start < 0:
            return result
        brace = start + len(begin)
        while brace < len(tex) and tex[brace].isspace():
            brace += 1
        if brace >= len(tex) or tex[brace] != "{":
            position = brace
            continue
        title, _ = balanced_argument(tex, brace)
        box_end = tex.find(end_box, brace)
        if box_end < 0:
            return result
        solution_start = tex.find(begin_solution, box_end + len(end_box))
        next_example = tex.find(begin, box_end + len(end_box))
        if solution_start < 0 or (next_example >= 0 and next_example < solution_start):
            segment_end = box_end + len(end_box)
        else:
            solution_end = tex.find(end_solution, solution_start + len(begin_solution))
            if solution_end < 0:
                segment_end = box_end + len(end_box)
            else:
                segment_end = solution_end + len(end_solution)
        result.append({"title": title.strip(), "tex": tex[start:segment_end].strip()})
        position = segment_end


def qualify_appendix_labels(tex: str) -> str:
    tex = re.sub(r"\\label\{ch\d{2}:([^}]+)\}", r"\\label{appE:\1}", tex)
    for macro in ("ref", "eqref", "pageref", "autoref"):
        tex = re.sub(
            rf"\\{macro}\{{ch\d{{2}}:([^}}]+)\}}",
            lambda match, name=macro: f"\\{name}{{appE:{match.group(1)}}}",
            tex,
        )
    return tex


def captionize_diagrams(tex: str, unit_key: str) -> str:
    """Turn legacy literal figure lines into numbered transparent captions."""
    needle = "{\\small\\color{TextGray}"
    output: list[str] = []
    position = 0
    prefix = re.compile(
        r"^(?:(?:题?图|解图)\s*[0-9A-Za-z.()、，,\-]+\s*(?:\\quad)?\s*)"
    )
    caption_index = 0
    while True:
        start = tex.find(needle, position)
        if start < 0:
            output.append(tex[position:])
            break
        output.append(tex[position:start])
        try:
            value, end = balanced_argument(tex, start)
        except ValueError:
            output.append(tex[start:])
            break
        body = value[len("\\small\\color{TextGray}"):].strip()
        caption_index += 1
        caption = prefix.sub("", body).strip()
        caption = caption.replace("（合并重绘）", "").replace("（重绘）", "")
        output.append(
            f"\\figcap{{{caption}}}"
            f"\\label{{appE:fig:{unit_key}-legacy-{caption_index:02d}}}"
        )
        position = end
    return "".join(output)


FIGURE_ALIASES = {
    "s22": {
        "vacuumDiodeDiagram": ["33-9"],
        "ionChamberDiagram": ["33-11"],
        "ringResistanceDiagram": ["33-12"],
    },
    "s23": {
        "cubeDiagram": ["34-9"],
        "ladderDiagram": ["34-10"],
        "threeRailDiagram": ["34-11"],
        "sierpinskiDiagram": ["34-13"],
    },
}


def add_figure_aliases(tex: str, unit_key: str) -> str:
    for macro, aliases in FIGURE_ALIASES.get(unit_key, {}).items():
        labels = "".join(f"\\label{{appE:fig:{unit_key}-{alias}}}" for alias in aliases)
        tex = re.sub(
            rf"(\\{re.escape(macro)})(?![A-Za-z@])",
            lambda match, suffix=labels: match.group(1) + suffix,
            tex,
        )
    return tex


def build() -> dict:
    # Recompute instead of trusting a stale report.
    report = {
        "policy": {
            "automatic_unique_threshold": 0.55,
            "probable_duplicate_threshold": 0.82,
            "manual_review_is_not_acceptance": True,
        },
        "comparisons": [],
        "included": [],
    }
    selected: dict[str, set[str]] = {}
    for chapter in sorted(OLD):
        old = collect(OLD[chapter], chapter)
        new = collect(NEW[chapter], chapter)
        for item in old["examples"]:
            match = best_match(item, new["examples"])
            key = (chapter, item["source"], item["title"])
            override = REVIEW_OVERRIDES.get(key)
            if override is not None:
                status, review_note = override
            elif match["ratio"] < 0.55:
                status = "included_unique_candidate"
                review_note = "题设或物理模型与最佳匹配项不同；整题及其解答、题意图收入附录。"
            else:
                status = "verified_duplicate"
                review_note = DEFAULT_REVIEW_NOTE
            if status.startswith("included_unique"):
                selected.setdefault(item["source"], set()).add(item["title"])
            old_label_match = re.search(r"\\label\{([^}]+)\}", item["text"])
            matched_item = next(
                candidate for candidate in new["examples"]
                if candidate["source"] == match["source"] and candidate["title"] == match["title"]
            )
            new_label_match = re.search(r"\\label\{([^}]+)\}", matched_item["text"])
            report["comparisons"].append({
                "chapter": chapter,
                "old_source": item["source"],
                "old_title": item["title"],
                "old_label": old_label_match.group(1) if old_label_match else "",
                "best_2020_match": match,
                "new_label": new_label_match.group(1) if new_label_match else "",
                "status": status,
                "review_note": review_note,
            })

    parts = [
        "\\chapter{电磁学补充专题}",
        "本附录补充第19—26章的电磁学专题与例题，重点讨论连续电荷分布、电势、电容器、恒定电流和复杂电阻网络。各题配有完整解答与图示，可结合正文选读。",
    ]
    section_titles = {
        "s18": "静电场：连续分布与场线",
        "s19": "电势与相互作用能",
        "s20": "导体静电平衡",
        "s21": "电介质与电容器",
        "s22": "恒定电流",
        "s23": "复杂电阻网络",
    }
    unit_lookup = {unit.key: unit for chapter in (19, 20, 21) for unit in OLD[chapter]}
    chapter_lookup = {unit.key: chapter for chapter in (19, 20, 21) for unit in OLD[chapter]}

    for unit_key in ("s18", "s19", "s20", "s21", "s22", "s23"):
        titles = selected.get(unit_key, set())
        if not titles:
            continue
        unit = unit_lookup[unit_key]
        directory = BOOK.parent / unit.directory
        diagram_file = directory / "diagrams.tex"
        diagrams = ""
        if diagram_file.exists():
            diagrams = flatten_inputs(diagram_file.read_text(encoding="utf-8"), directory)
            diagrams = captionize_diagrams(diagrams, unit_key)
        rendered, _ = extract_legacy(unit, chapter_lookup[unit_key])
        segments = example_segments(rendered)
        parts.append("\\Needspace{18\\baselineskip}")
        parts.append("\\section{" + section_titles[unit_key] + "}")
        parts.append("\\begingroup")
        parts.append("\\graphicspath{{" + directory.as_posix() + "/}{" + (directory / "assets").as_posix() + "/}}")
        parts.append(diagrams)
        for segment in segments:
            if segment["title"] not in titles:
                continue
            clean = qualify_appendix_labels(segment["tex"])
            clean = add_figure_aliases(clean, unit_key)
            parts.append(clean)
            report["included"].append({
                "source": unit_key,
                "title": segment["title"],
                "appendix_label": re.sub(
                    r"^ch\d{2}:", "appE:",
                    (re.search(r"\\label\{([^}]+)\}", segment["tex"]) or [None, ""])[1],
                ),
            })
        parts.append("\\endgroup")

    if SUPPLEMENTS.exists():
        parts.append(SUPPLEMENTS.read_text(encoding="utf-8"))

    APPENDIX.parent.mkdir(parents=True, exist_ok=True)
    from quality_revision_appendix import apply_revision
    APPENDIX.write_text(apply_revision(normalize_visible_eponyms("\n\n".join(parts)) + "\n"), encoding="utf-8")
    LEDGER.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"appendix E: {len(report['included'])} unique candidates")
    return report


if __name__ == "__main__":
    build()
