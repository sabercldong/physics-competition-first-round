#!/usr/bin/env python3
"""Generate the unified 32-chapter TeX tree from the reviewed legacy sources.

Generated files live below restructured-complete/generated and are build artifacts.
No PDF pages are embedded; all retained material is compiled as TeX/TikZ source.
"""
from __future__ import annotations

import argparse
import os
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
PROJECT = BOOK.parents[2]
LEGACY = PROJECT / "sample" / "xes-original"
GENERATED = BOOK / "generated"
OUTPUT = PROJECT / "output" / "pdf"

VOLUMES = (
    (1, "数学工具与运动学", 1, 4),
    (2, "力学", 5, 13),
    (3, "热学与统计物理", 14, 18),
    (4, "电磁学", 19, 26),
    (5, "光学", 27, 30),
    (6, "近代物理", 31, 32),
)

ADVANCED_UNITS = (
    ("A1", "力学"),
    ("A2", "热学"),
    ("A3", "数学工具"),
    ("A4", "电磁学"),
    ("A5", "光学"),
    ("A6", "近代物理"),
)


@dataclass(frozen=True)
class LegacyUnit:
    key: str
    directory: str
    title: str
    unit_file: str | None = None
    preload: tuple[str, ...] = ()


CHAPTERS: dict[int, dict] = {
    1: {"title": "数学工具：量纲、矢量、坐标、导数和积分",
        "display_title": "数学工具：量纲、矢量、坐标与微积分", "legacy": [
        LegacyUnit("s14", "fourteenth-section", "导数及其应用"),
        LegacyUnit("s15", "fifteenth-section", "积分及其应用")],
        "new": ["ch01-math-foundations.tex"]},
    2: {"title": "质点运动的描述", "legacy": [
        LegacyUnit("k01", "kinematics-supplement", "理想物理模型：质点", "units/k01.tex", ("figures.tex",)),
        LegacyUnit("k02", "kinematics-supplement", "时间、位移、速度与加速度", "units/k02.tex", ("figures.tex",))], "new": []},
    3: {"title": "合运动、抛体、圆周与一般曲线运动", "legacy": [
        LegacyUnit("k03", "kinematics-supplement", "运动的合成与分解", "units/k03.tex", ("figures.tex",)),
        LegacyUnit("k04", "kinematics-supplement", "抛体运动", "units/k04.tex", ("figures.tex",)),
        LegacyUnit("k05", "kinematics-supplement", "圆周运动", "units/k05.tex", ("figures.tex",)),
        LegacyUnit("k06", "kinematics-supplement", "平面内的一般曲线运动", "units/k06.tex", ("figures.tex",))], "new": []},
    4: {"title": "相对运动、约束和刚体运动学", "legacy": [
        LegacyUnit("k07", "kinematics-supplement", "相对运动与参考系", "units/k07.tex", ("figures.tex",)),
        LegacyUnit("k08", "kinematics-supplement", "受约束的运动", "units/k08.tex", ("figures.tex",)),
        LegacyUnit("k09", "kinematics-supplement", "刚体运动学", "units/k09.tex", ("figures.tex",)),
        LegacyUnit("k11", "kinematics-supplement", "运动学综合", "units/k11.tex", ("figures.tex",))], "new": []},
    5: {"title": "力、受力分析与静力平衡", "legacy": [
        LegacyUnit("s01", "first-section", "力的基本性质"),
        LegacyUnit("s02", "second-section", "受力分析"),
        LegacyUnit("s03", "third-section", "质点与刚体的静力平衡")], "new": []},
    6: {"title": "牛顿定律、非惯性系及其应用", "legacy": [
        LegacyUnit("s04", "fourth-section", "牛顿运动定律"),
        LegacyUnit("s05", "fifth-section", "牛顿运动定律应用"),
        LegacyUnit("s06", "sixth-section", "非惯性系与惯性力")], "new": []},
    7: {"title": "动量、变质量系统与碰撞", "legacy": [
        LegacyUnit("s07", "seventh-section", "动量定理"),
        LegacyUnit("s08", "eighth-section", "动量守恒"),
        LegacyUnit("s09", "ninth-section", "变质量系统"),
        LegacyUnit("s12", "twelfth-section", "碰撞")], "new": []},
    8: {"title": "功、能量和守恒定律", "legacy": [
        LegacyUnit("s10", "tenth-section", "功、功率与动能定理"),
        LegacyUnit("s11", "eleventh-section", "势能与机械能守恒"),
        LegacyUnit("s13", "thirteenth-section", "能量的转化与守恒")], "new": []},
    9: {"title": "角动量与刚体动力学", "legacy": [
        LegacyUnit("s16", "sixteenth-section", "角动量"),
        LegacyUnit("s17", "seventeenth-section", "刚体动力学")], "new": []},
    10: {"title": "简谐振动、阻尼、受迫振动和共振", "legacy": [], "new": ["ch10-oscillation.tex", "ch10-source-exercises.tex"]},
    11: {"title": "有心力、万有引力与天体运动", "legacy": [], "new": ["ch11-gravity.tex", "ch11-source-exercises.tex"]},
    12: {"title": "弹性体与机械波", "legacy": [], "new": [
        "ch12-elastic-waves.tex", "ch12-wave-extensions.tex", "ch12-source-exercises.tex"]},
    13: {"title": "流体静力学与动力学", "legacy": [
        LegacyUnit("k10", "kinematics-supplement", "流体运动学", "units/k10.tex", ("figures.tex",))],
        "new": ["ch13-fluid.tex", "ch13-source-exercises.tex"]},
    14: {"title": "温度、物态、理想气体与分子模型", "legacy": [LegacyUnit("s28", "twenty-eighth-section", "温度、物态与分子模型")], "new": []},
    15: {"title": "热力学第一定律", "legacy": [LegacyUnit("s29", "twenty-ninth-section", "热力学第一定律")], "new": []},
    16: {"title": "热力学第二定律", "legacy": [LegacyUnit("s30", "thirtieth-section", "热力学第二定律")], "new": []},
    17: {"title": "相变与表面现象", "legacy": [LegacyUnit("s31", "thirty-first-section", "相变与临界现象")], "new": []},
    18: {"title": "统计物理基础", "legacy": [], "new": ["ch18-statistical.tex"]},
    19: {"title": "静电场与电势", "legacy": [
        LegacyUnit("s32", "thirty-second-section", "电场的基本性质"),
        LegacyUnit("s33", "thirty-third-section", "电势能与电势")], "new": []},
    20: {"title": "导体、电介质与电容器", "legacy": [
        LegacyUnit("s34", "thirty-fourth-section", "静电平衡"),
        LegacyUnit("s35", "thirty-fifth-section", "电介质与电容器")], "new": []},
    21: {"title": "恒定电流与复杂电路", "legacy": [
        LegacyUnit("s36", "thirty-sixth-section", "恒定电流"),
        LegacyUnit("s37", "thirty-seventh-section", "复杂电阻网络")], "new": []},
    22: {"title": "洛伦兹力与带电粒子运动", "legacy": [LegacyUnit("s38", "thirty-eighth-section", "洛伦兹力")], "new": []},
    23: {"title": "磁场、安培力与安培定律", "legacy": [LegacyUnit("s39", "thirty-ninth-section", "安培力与安培定律")], "new": []},
    24: {"title": "电磁感应", "legacy": [LegacyUnit("s40", "fortieth-section", "电磁感应")], "new": []},
    25: {"title": "交流电、相量与RLC电路", "legacy": [], "new": ["ch25-ac.tex"]},
    26: {"title": "电磁场、电磁波与超导体", "legacy": [LegacyUnit("s41", "forty-first-section", "电磁场与超导体")], "new": []},
    27: {"title": "几何光学：光线、反射和折射", "legacy": [LegacyUnit("s42", "forty-second-section", "光线的性质")],
        "new": ["ch27-wave-ray.tex"]},
    28: {"title": "成像与光学仪器", "legacy": [LegacyUnit("s43", "forty-third-section", "几何光学成像")], "new": ["ch28-instruments.tex"]},
    29: {"title": "光的干涉", "legacy": [LegacyUnit("s44", "forty-fourth-section", "光的干涉")], "new": ["ch29-wave-coherence.tex"]},
    30: {"title": "衍射、偏振与晶体光学", "legacy": [LegacyUnit("s45", "forty-fifth-section", "光的衍射")], "new": ["ch30-diffraction-theory.tex", "ch30-polarization.tex"]},
    31: {"title": "狭义相对论", "legacy": [], "new": ["ch31-relativity.tex"]},
    32: {"title": "量子现象、原子与原子核物理", "legacy": [], "new": ["ch32-modern.tex"]},
}


EDITORIAL_REPLACEMENTS = (
    ("示意示意", "示意"),
    ("普通Euclid角度", "普通欧氏几何角度"),
    ("原扫描页写有“如图”，但对应图未出现在扫描件中；下图按题意重建三种标准循环。",
     "三种循环的状态点和过程方向如图所示。"),
    ("原扫描页同样没有显示题干所引用的图，", ""),
    ("题目页写有“如图”，但对应图未出现在扫描件中；下图按题意重建三种标准循环。",
     "三种循环的状态点和过程方向如图所示。"),
    ("题目页同样没有显示题干所引用的图，", ""),
    ("下图分别重建相应的", "下图依次给出"),
    ("服饰、年龄特征和排列关系依照原图保留", "三位人物的服饰和年龄特征清晰可辨"),
    ("依照原图示意的玻尔兹曼纪念碑式构图", "玻尔兹曼纪念碑的式样"),
    ("下面严格沿用原图给定的", "以下取题图给定的"),
    ("依据原讲义重新绘制的", ""), ("依照原讲义重新绘制的", ""),
    ("依照原资料中的", ""), ("原讲义中的", ""), ("原资料中的", ""),
    ("提供的原始扫描页", "现有题干"), ("原始扫描", "题目"), ("原扫描", "题目"),
    ("重新创作", "绘制"), ("重新绘制", "绘制"), ("原创", ""), ("重绘", "示意"),
    ("新绘的", ""), ("新绘", ""), ("题源说明", ""),
    ("原图", "题图"), ("原题", "题目"),
)


VISIBLE_EPONYM_REPLACEMENTS = (
    ("Fabry--P\\'erot", "法布里--珀罗"),
    ("Clausius--Mossotti", "克劳修斯--莫索蒂"),
    ("Clausius--Clapeyron", "克劳修斯--克拉珀龙"),
    ("Lennard--Jones", "莱纳德--琼斯"),
    ("Van der Waals", "范德瓦耳斯"),
    ("Sadi Carnot", "萨迪·卡诺"),
    ("Lord Kelvin", "开尔文勋爵"),
    ("Rudolf Clausius", "鲁道夫·克劳修斯"),
    ("Georg Simon Ohm", "格奥尔格·西蒙·欧姆"),
    ("William Thomson", "威廉·汤姆孙"),
    ("Hans Geiger", "汉斯·盖革"),
    ("Ernest Marsden", "恩斯特·马斯登"),
    ("Ernest Rutherford", "恩斯特·卢瑟福"),
    ("Child--Langmuir", "查尔德--朗缪尔"),
    ("Kamerlingh Onnes", "卡末林·昂内斯"),
    ("Biot--Savart", "毕奥--萨伐尔"),
    ("Ampere--Maxwell", "安培--麦克斯韦"),
    ("Faraday--Kirchhoff", "法拉第--基尔霍夫"),
    ("Faraday--Lenz", "法拉第--楞次"),
    ("Von Laue", "冯·劳厄"),
    ("Lorentz", "洛伦兹"),
    ("Ampere", "安培"),
    ("Faraday", "法拉第"),
    ("Lenz", "楞次"),
    ("Maxwell", "麦克斯韦"),
    ("Coulomb", "库仑"),
    ("Gauss", "高斯"),
    ("Biot", "毕奥"),
    ("Savart", "萨伐尔"),
    ("Helmholtz", "亥姆霍兹"),
    ("Poynting", "坡印廷"),
    ("Larmor", "拉莫尔"),
    ("Thomson", "汤姆孙"),
    ("Meissner", "迈斯纳"),
    ("Ochsenfeld", "奥森菲尔德"),
    ("Onnes", "昂内斯"),
    ("Young", "杨氏"),
    ("Fresnel", "菲涅耳"),
    ("Newton", "牛顿"),
    ("Michelson", "迈克耳孙"),
    ("Nobel", "诺贝尔"),
    ("Bohr", "玻尔"),
    ("Boltzmann", "玻尔兹曼"),
    ("Compton", "康普顿"),
    ("Zeeman", "塞曼"),
    ("Lawrence", "劳伦斯"),
    ("Glaser", "格拉泽"),
    ("Corbino", "科尔比诺"),
    ("Hall", "霍尔"),
    ("Joule", "焦耳"),
    ("Kirchhoff", "基尔霍夫"),
    ("Rayleigh", "瑞利"),
    ("Ramsay", "拉姆齐"),
    ("Airy", "艾里"),
    ("Lloyd", "劳埃德"),
    ("Boyle", "波义耳"),
    ("Snell", "斯涅尔"),
    ("Bragg", "布拉格"),
    ("Meslin", "梅斯林"),
    ("Carnot", "卡诺"),
    ("Otto", "奥托"),
    ("Brayton", "布雷顿"),
    ("Poisson", "泊松"),
    ("Laplace", "拉普拉斯"),
    ("Kepler", "开普勒"),
    ("Fermat", "费马"),
    ("Dirac", "狄拉克"),
    ("Fraunhofer", "夫琅禾费"),
    ("Nyquist", "奈奎斯特"),
    ("Stokes", "斯托克斯"),
    ("Galileo", "伽利略"),
    ("Galilean", "伽利略"),
    ("Rutherford", "卢瑟福"),
    ("Geiger", "盖革"),
    ("Marsden", "马斯登"),
    ("Green", "格林"),
    ("Neumann", "诺依曼"),
    ("Clausius", "克劳修斯"),
    ("Kelvin", "开尔文"),
    ("Clapeyron", "克拉珀龙"),
    ("Drude", "德鲁德"),
    ("Ohmic", "欧姆"),
    ("Ohm", "欧姆"),
    ("Eulerian", "欧拉"),
    ("Euler", "欧拉"),
    ("Lagrangian", "拉格朗日"),
    ("Lagrange", "拉格朗日"),
    ("Gibbs", "吉布斯"),
    ("Liouville", "刘维尔"),
    ("Gaussian", "高斯"),
    ("Bose", "玻色"),
    ("Fermi", "费米"),
    ("Pauli", "泡利"),
    ("Jones", "琼斯"),
    ("Malus", "马吕斯"),
    ("Mueller", "穆勒"),
    ("Thevenin", "戴维南"),
    ("Norton", "诺顿"),
    ("Bernoulli", "伯努利"),
    ("Reynolds", "雷诺"),
    ("Navier", "纳维"),
    ("Cauchy", "柯西"),
    ("Hagen", "哈根"),
    ("Poiseuille", "泊肃叶"),
    ("Couette", "库埃特"),
    ("Dalton", "道尔顿"),
    ("Cavendish", "卡文迪许"),
    ("Perrin", "佩兰"),
    ("Billet", "比耶"),
    ("Einstein", "爱因斯坦"),
    ("Planck", "普朗克"),
    ("Stefan", "斯蒂芬"),
    ("Mayer", "迈耶"),
    ("London", "伦敦"),
    ("Rabi", "拉比"),
    ("Tolman", "托尔曼"),
    ("Stewart", "斯图尔特"),
    ("Child", "查尔德"),
    ("Langmuir", "朗缪尔"),
    ("Binet", "比内"),
    ("Dirichlet", "狄利克雷"),
    ("Mossotti", "莫索蒂"),
    ("Runge", "龙格"),
    ("Duffing", "杜芬"),
    ("Brillouin", "布里渊"),
    ("Hessian", "海森"),
    ("Hankel", "汉克尔"),
    ("Hamiltonian", "哈密顿量"),
    ("Hamilton", "哈密顿"),
)


def normalize_visible_eponyms(text: str) -> str:
    """Use Chinese names in student-facing prose while preserving bilingual glosses.

    Full-width parenthetical glosses such as ``麦克斯韦（Maxwell speed
    distribution）`` are protected.  The boundary rule also leaves command names such
    as ``\\MichelsonDiagram`` and source labels untouched.
    """
    protected: list[str] = []

    def hold(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"@@BILINGUAL-{len(protected) - 1}@@"

    # Mathematical identifiers such as ``\eta_{\rm Carnot}`` are labels, not
    # student-facing prose.  Translating them would corrupt the symbolic name.
    text = re.sub(r"\\rm[ \t]+[A-Za-z][A-Za-z-]*", hold, text)
    text = re.sub(r"\\(?:mathrm|operatorname)\{[^{}]*[A-Za-z][^{}]*\}", hold, text)
    text = re.sub(r"\\(?:label|ref|eqref|pageref|autoref)\{[^{}]+\}", hold, text)

    # A bilingual gloss contains Latin text but no Han characters.  Parentheses
    # such as “（后来获封 Kelvin 勋爵）” are ordinary prose and must
    # still be normalized, so they are deliberately not protected here.
    text = re.sub(r"（(?=[^（）]*[A-Za-z])[^（）\u3400-\u9fff]*）", hold, text)
    for english, chinese in VISIBLE_EPONYM_REPLACEMENTS:
        text = re.sub(
            rf"(?<![\\A-Za-z]){re.escape(english)}(?![A-Za-z])",
            lambda _match, value=chinese: value,
            text,
        )
    # Later protected parentheticals may contain an earlier math placeholder.
    # Expand in reverse nesting order so no temporary token reaches the PDF.
    for index in reversed(range(len(protected))):
        value = protected[index]
        text = text.replace(f"@@BILINGUAL-{index}@@", value)
    assert '@@BILINGUAL-' not in text, 'Unexpanded bilingual placeholder'
    # Legacy sources often surrounded an English eponym with spaces.  Once the
    # name is Chinese those spaces become visible gaps such as “杨氏 双缝”.
    text = re.sub(r"(?<=[\u3400-\u9fff])[ \t]+(?=[\u3400-\u9fff])", "", text)
    return text


def balanced_argument(text: str, start: int) -> tuple[str, int]:
    if start >= len(text) or text[start] != "{":
        raise ValueError("expected braced argument")
    depth = 0
    for pos in range(start, len(text)):
        if text[pos] == "{" and (pos == 0 or text[pos - 1] != "\\"):
            depth += 1
        elif text[pos] == "}" and (pos == 0 or text[pos - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start + 1:pos], pos + 1
    raise ValueError("unbalanced braces")


def replace_macro_argument(text: str, macro: str, transform) -> str:
    needle = "\\" + macro
    out, pos = [], 0
    while True:
        idx = text.find(needle, pos)
        if idx < 0:
            out.append(text[pos:])
            return "".join(out)
        out.append(text[pos:idx])
        brace = idx + len(needle)
        while brace < len(text) and text[brace].isspace():
            brace += 1
        if brace >= len(text) or text[brace] != "{":
            out.append(text[idx:brace])
            pos = brace
            continue
        arg, end = balanced_argument(text, brace)
        out.append(text[idx:brace + 1] + transform(arg) + "}")
        pos = end


def strip_command_definition(text: str, macro: str) -> str:
    """Remove a local \newcommand/\renewcommand definition for a shared macro."""
    pattern = re.compile(
        r"\\(?:re)?newcommand\s*\{\\" + re.escape(macro) + r"\}\s*(?:\[[^\]]*\]\s*)?"
    )
    while True:
        match = pattern.search(text)
        if not match:
            return text
        brace = match.end()
        while brace < len(text) and text[brace].isspace():
            brace += 1
        if brace >= len(text) or text[brace] != "{":
            text = text[:match.start()] + text[match.end():]
            continue
        _, end = balanced_argument(text, brace)
        text = text[:match.start()] + text[end:]


def strip_source_prefix(value: str) -> str:
    value = re.sub(r"^\s*(?:图|例(?:题)?)\s*[Kk0-9]+(?:\.[0-9]+)+(?:\s*[—-]\s*[Kk0-9]+(?:\.[0-9]+)+)?\s*[：:]\s*", "", value)
    value = re.sub(r"^\s*例(?:题)?\s*[Kk0-9]+(?:\.[0-9]+)+\s*(?:\\quad\s*)?", "", value)
    return value.strip()


def _source_slug(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z]+", "-", value).strip("-").lower()


def _skip_tex_space(text: str, position: int) -> int:
    """Skip whitespace and TeX comments between adjacent macro arguments."""
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        if text[position] == "%":
            newline = text.find("\n", position + 1)
            return len(text) if newline < 0 else _skip_tex_space(text, newline + 1)
        break
    return position


def _number_label(chapter: int, kind: str, unit_key: str, source_number: str) -> str:
    return f"ch{chapter:02d}:{kind}:{unit_key}-{_source_slug(source_number)}"


def _qualify_existing_labels(text: str, chapter: int) -> str:
    labels = set(re.findall(r"\\label\{([^}]+)\}", text))
    replacements: dict[str, str] = {}
    for old in labels:
        if re.fullmatch(r"ch\d{2}:[a-z]+:[A-Za-z0-9:-]+", old):
            continue
        head, _, tail = old.partition(":")
        kind = head if head in {"eq", "fig", "tab", "ex"} else "ref"
        slug = _source_slug(tail if tail else old)
        replacements[old] = f"ch{chapter:02d}:{kind}:{slug}"
    for old, new in replacements.items():
        text = text.replace(f"\\label{{{old}}}", f"\\label{{{new}}}")
        for macro in ("ref", "eqref", "pageref", "autoref"):
            text = text.replace(f"\\{macro}{{{old}}}", f"\\{macro}{{{new}}}")
    return text


def migrate_source_numbering(text: str, chapter: int, unit_key: str) -> tuple[str, list[dict[str, str]]]:
    """Attach stable labels to legacy numbered objects and rewrite prose refs."""
    mappings: dict[tuple[str, str], str] = {}
    object_counts: dict[tuple[str, str], int] = {}

    def register(kind: str, number: str) -> str:
        number = re.sub(r"\s+", "", number)
        key = (kind, number)
        mappings.setdefault(key, _number_label(chapter, kind, unit_key, number))
        return mappings[key]

    def register_object(kind: str, number: str) -> str:
        number = re.sub(r"\s+", "", number)
        key = (kind, number)
        base = _number_label(chapter, kind, unit_key, number)
        mappings.setdefault(key, base)
        object_counts[key] = object_counts.get(key, 0) + 1
        return base if object_counts[key] == 1 else f"{base}-dup{object_counts[key]}"

    # Preserve old manual equation numbers as labels before removing \tag.
    # Legacy sources use both a standalone ``\tag{...}`` line and an inline
    # ``... \tag{...}`` form.  Handling only the former silently removed the
    # visible number while leaving prose such as “由式(2)、(3)” behind.
    def tag_repl(match: re.Match[str]) -> str:
        number = match.group(1).strip()
        return f"\\label{{{register_object('eq', number)}}}"
    text = re.sub(r"\\tag\s*\{([^}]+)\}", tag_repl, text)

    # Caption macros used by the legacy figures.
    caption_prefix = re.compile(
        r"^\s*(?:图|Fig\.?|例(?:题)?)[ \t]*([Kk]?\d+(?:\.\d+)+)"
        r"(?:\s*(?:--|[—–-]|与)\s*(?:图\s*)?([Kk]?\d+(?:\.\d+)+))?"
        r"\s*(?:[：:]|\\quad)?\s*",
        re.IGNORECASE,
    )
    for macro in ("diagramcaption", "figcap", "origcaption"):
        needle = "\\" + macro
        out: list[str] = []
        pos = 0
        while True:
            idx = text.find(needle, pos)
            if idx < 0:
                out.append(text[pos:])
                text = "".join(out)
                break
            out.append(text[pos:idx])
            brace = idx + len(needle)
            while brace < len(text) and text[brace].isspace():
                brace += 1
            if brace >= len(text) or text[brace] != "{":
                out.append(text[idx:brace])
                pos = brace
                continue
            arg, end = balanced_argument(text, brace)
            match = caption_prefix.match(arg)
            if match:
                is_example_figure = bool(re.match(r"^\s*例", arg))
                source_number = match.group(1)
                object_number = f"ex-{source_number}" if is_example_figure else source_number
                label = register_object("fig", object_number)
                if is_example_figure:
                    mappings.setdefault(("fig", source_number), label)
                else:
                    mappings[("fig", source_number)] = label
                if match.group(2):
                    if is_example_figure:
                        mappings.setdefault(("fig", match.group(2)), label)
                    else:
                        mappings[("fig", match.group(2))] = label
                clean = arg[match.end():].strip()
                out.append(text[idx:brace + 1] + clean + f"}}\\label{{{label}}}")
            else:
                out.append(text[idx:end])
            pos = end

    # Older mechanics chapters use \diagcaption{old number}{description}.
    needle = "\\diagcaption"
    out, pos = [], 0
    while True:
        idx = text.find(needle, pos)
        if idx < 0:
            out.append(text[pos:])
            text = "".join(out)
            break
        out.append(text[pos:idx])
        first = idx + len(needle)
        while first < len(text) and text[first].isspace():
            first += 1
        if first >= len(text) or text[first] != "{":
            out.append(text[idx:first])
            pos = first
            continue
        title, after_title = balanced_argument(text, first)
        second = after_title
        while second < len(text) and text[second].isspace():
            second += 1
        if second >= len(text) or text[second] != "{":
            out.append(text[idx:after_title])
            pos = after_title
            continue
        description, end = balanced_argument(text, second)
        match = caption_prefix.match(title)
        if match:
            label = register_object("fig", match.group(1))
            if match.group(2):
                mappings.setdefault(("fig", match.group(2)), label)
            out.append(f"\\bookcaption{{{description}}}\\label{{{label}}}")
        else:
            out.append(text[idx:end])
        pos = end

    # Historical/real-scene images carry their caption in the second mandatory
    # argument, after an optional width and the image filename.
    for macro in ("historyfigure", "sourceimage"):
        needle = "\\" + macro
        out, pos = [], 0
        while True:
            idx = text.find(needle, pos)
            if idx < 0:
                out.append(text[pos:])
                text = "".join(out)
                break
            out.append(text[pos:idx])
            cursor = _skip_tex_space(text, idx + len(needle))
            if cursor < len(text) and text[cursor] == "[":
                close = text.find("]", cursor + 1)
                if close < 0:
                    out.append(text[idx:cursor + 1])
                    pos = cursor + 1
                    continue
                cursor = _skip_tex_space(text, close + 1)
            if cursor >= len(text) or text[cursor] != "{":
                out.append(text[idx:cursor])
                pos = cursor
                continue
            _, after_file = balanced_argument(text, cursor)
            caption = _skip_tex_space(text, after_file)
            if caption >= len(text) or text[caption] != "{":
                out.append(text[idx:after_file])
                pos = after_file
                continue
            arg, end = balanced_argument(text, caption)
            match = caption_prefix.match(arg)
            if match:
                label = register_object("fig", match.group(1))
                if match.group(2):
                    mappings.setdefault(("fig", match.group(2)), label)
                clean = arg[match.end():].strip()
                out.append(text[idx:caption + 1] + clean + f"}}\\label{{{label}}}")
            else:
                out.append(text[idx:end])
            pos = end

    # Standard table captions.
    needle = "\\caption"
    out, pos = [], 0
    table_prefix = re.compile(r"^\s*表\s*([Kk]?\d+(?:\.\d+)+)\s*(?:[：:]\s*)?")
    while True:
        idx = text.find(needle, pos)
        if idx < 0:
            out.append(text[pos:])
            text = "".join(out)
            break
        out.append(text[pos:idx])
        brace = idx + len(needle)
        while brace < len(text) and text[brace].isspace():
            brace += 1
        if brace >= len(text) or text[brace] != "{":
            out.append(text[idx:brace])
            pos = brace
            continue
        arg, end = balanced_argument(text, brace)
        match = table_prefix.match(arg)
        if match:
            label = register_object("tab", match.group(1))
            clean = arg[match.end():].strip()
            out.append(text[idx:brace + 1] + clean + f"}}\\label{{{label}}}")
        else:
            out.append(text[idx:end])
        pos = end

    # Non-floating tables in the kinematics supplement use the shared compact
    # table-caption macro rather than LaTeX's floating \caption command.
    needle = "\\booktablecaption"
    out, pos = [], 0
    while True:
        idx = text.find(needle, pos)
        if idx < 0:
            out.append(text[pos:])
            text = "".join(out)
            break
        out.append(text[pos:idx])
        brace = idx + len(needle)
        while brace < len(text) and text[brace].isspace():
            brace += 1
        if brace >= len(text) or text[brace] != "{":
            out.append(text[idx:brace])
            pos = brace
            continue
        arg, end = balanced_argument(text, brace)
        match = table_prefix.match(arg)
        if match:
            label = register_object("tab", match.group(1))
            clean = arg[match.end():].strip()
            out.append(text[idx:brace + 1] + clean + f"}}\\label{{{label}}}")
        else:
            out.append(text[idx:end])
        pos = end

    # Numbered example titles: the box increments the example counter before
    # this label is read, so the reference resolves to the new chapter number.
    begin = "\\begin{origexamplebox}"
    out, pos = [], 0
    example_prefix = re.compile(r"^\s*例(?:题)?\s*([Kk]?\d+(?:\.\d+)+)\s*(?:\\quad\s*)?")
    while True:
        idx = text.find(begin, pos)
        if idx < 0:
            out.append(text[pos:])
            text = "".join(out)
            break
        out.append(text[pos:idx])
        brace = idx + len(begin)
        while brace < len(text) and text[brace].isspace():
            brace += 1
        if brace >= len(text) or text[brace] != "{":
            out.append(text[idx:brace])
            pos = brace
            continue
        arg, end = balanced_argument(text, brace)
        match = example_prefix.match(arg)
        if match:
            label = register_object("ex", match.group(1))
            clean = arg[match.end():].strip()
            out.append(text[idx:brace + 1] + clean + f"}}\\label{{{label}}}")
        else:
            out.append(text[idx:end])
        pos = end

    # A frequent one-line caption form sits directly below a TikZ picture.
    def inline_caption_repl(match: re.Match[str]) -> str:
        label = register_object("fig", match.group(1))
        if match.group(2):
            mappings.setdefault(("fig", match.group(2)), label)
        return "\\figcap{" + match.group(3).strip() + f"}}\\label{{{label}}}"
    text = re.sub(
        r"(?:\\par\\smallskip\s*)?\{\\small\\color\{TextGray\}\s*(?:图|Fig\.?)\s*([Kk]?\d+(?:\.\d+)+)"
        r"(?:\s*(?:--|[—–-])\s*(?:图\s*)?([Kk]?\d+(?:\.\d+)+))?\s*(?:[：:]|\\quad)\s*"
        r"([^{}\n]*(?:\$[^$]*\$[^{}\n]*)*)\}",
        inline_caption_repl,
        text,
        flags=re.IGNORECASE,
    )

    # Replace prose references after caption prefixes have been removed.
    for (kind, number), label in sorted(mappings.items(), key=lambda item: -len(item[0][1])):
        escaped = re.escape(number)
        if kind == "fig":
            text = re.sub(rf"图\s*{escaped}(?![0-9.])", rf"图~\\ref{{{label}}}", text)
        elif kind == "tab":
            text = re.sub(rf"表\s*{escaped}(?![0-9.])", rf"表~\\ref{{{label}}}", text)
        elif kind == "ex":
            text = re.sub(rf"例(?:题)?\s*{escaped}(?![0-9.])", rf"例~\\ref{{{label}}}", text)
        elif kind == "eq":
            text = re.sub(rf"式\s*[（(]?\s*{escaped}\s*[）)]?", rf"式~(\\ref{{{label}}})", text)

    text = _qualify_existing_labels(text, chapter)
    # ``ex-<number>`` is an internal slug used to keep an example's embedded
    # figure label distinct from an ordinary numbered figure.  The matching
    # plain number is also registered so prose such as “见图 2.17” can be
    # rewritten.  They are two aliases for one source object, not two figures;
    # omit the synthetic alias from the source-object ledger when the plain
    # source number already points to the same label.
    audit = []
    for (kind, number), label in sorted(mappings.items()):
        if (
            kind == "fig"
            and number.startswith("ex-")
            and mappings.get((kind, number[3:])) == label
        ):
            continue
        audit.append(
            {"source_kind": kind, "source_number": number, "new_label": label}
        )
    return text, audit


def flatten_inputs(text: str, base: Path, seen: set[Path] | None = None) -> str:
    seen = set() if seen is None else seen
    pattern = re.compile(r"\\input\s*\{([^}]+)\}")
    while True:
        match = pattern.search(text)
        if not match:
            return text
        raw = match.group(1)
        candidate = (base / raw).resolve()
        if candidate.suffix == "":
            candidate = candidate.with_suffix(".tex")
        if not candidate.exists() or candidate.name in {"common-style.tex", "style.tex"}:
            text = text[:match.start()] + text[match.end():]
            continue
        if candidate in seen:
            replacement = ""
        else:
            seen.add(candidate)
            replacement = flatten_inputs(candidate.read_text(encoding="utf-8"), candidate.parent, seen)
        text = text[:match.start()] + replacement + text[match.end():]


def select_used_command_definitions(text: str, body: str) -> str:
    """Keep only preload macros that the current unit actually invokes.

    The kinematics source stores every figure in one shared file.  Injecting
    that whole file into each K unit made the source ledger claim that the
    same figure belonged to several chapters.  This routine follows macro
    dependencies and emits only definitions reachable from the unit body.
    """
    pattern = re.compile(r"\\(?:re)?newcommand\s*\{\\([A-Za-z@]+)\}")
    definitions: dict[str, str] = {}
    order: list[str] = []
    position = 0
    while True:
        match = pattern.search(text, position)
        if not match:
            break
        cursor = match.end()
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        for _ in range(2):
            if cursor < len(text) and text[cursor] == "[":
                close = text.find("]", cursor + 1)
                if close < 0:
                    break
                cursor = close + 1
                while cursor < len(text) and text[cursor].isspace():
                    cursor += 1
        if cursor >= len(text) or text[cursor] != "{":
            position = match.end()
            continue
        _, end = balanced_argument(text, cursor)
        name = match.group(1)
        definitions[name] = text[match.start():end]
        order.append(name)
        position = end

    used = set(re.findall(r"\\([A-Za-z@]+)", body)) & set(definitions)
    changed = True
    while changed:
        changed = False
        for name in tuple(used):
            dependencies = set(re.findall(r"\\([A-Za-z@]+)", definitions[name])) & set(definitions)
            before = len(used)
            used.update(dependencies)
            changed = changed or len(used) != before
    return "\n\n".join(definitions[name] for name in order if name in used)


def extract_legacy(unit: LegacyUnit, chapter: int) -> tuple[str, list[dict[str, str]]]:
    directory = LEGACY / unit.directory
    if unit.unit_file:
        body = flatten_inputs((directory / unit.unit_file).read_text(encoding="utf-8"), (directory / unit.unit_file).parent)
        preloads = []
        for item in unit.preload:
            preload = flatten_inputs((directory / item).read_text(encoding="utf-8"), directory)
            preloads.append(select_used_command_definitions(preload, body))
        pre = "\n".join(preloads)
    else:
        main = (directory / "main.tex").read_text(encoding="utf-8")
        marker = "\\begin{document}"
        if marker not in main:
            raise RuntimeError(f"No document body in {directory / 'main.tex'}")
        preamble, body = main.split(marker, 1)
        body = body.rsplit("\\end{document}", 1)[0]
        local_inputs = []
        for raw in re.findall(r"\\input\s*\{([^}]+)\}", preamble):
            candidate = (directory / raw).resolve()
            if candidate.suffix == "":
                candidate = candidate.with_suffix(".tex")
            if candidate.exists() and candidate.parent == directory and candidate.name not in {"style.tex"}:
                local_inputs.append(flatten_inputs(candidate.read_text(encoding="utf-8"), directory))
        pre = "\n".join(local_inputs)
        body = flatten_inputs(body, directory)

    text = pre + "\n" + body
    text = re.sub(r"\\pagenumbering\s*\{[^}]+\}", "", text)
    text = re.sub(r"\\setcounter\s*\{(?:page|chapter|section|subsection|equation|figure|table)\}\s*\{[^}]+\}", "", text)
    text = re.sub(r"\\renewcommand\s*\{\\theequation\}\s*\{[^{}]*\}", "", text)
    text, source_number_map = migrate_source_numbering(text, chapter, unit.key)
    # Remove legacy manual tags together with an otherwise empty line.  Leaving
    # a blank paragraph inside an equation environment makes TeX leave math
    # mode and later report a misleading ``Missing $'' error.
    text = re.sub(r"^[ \t]*\\tag\s*\{[^}]+\}[ \t]*\n?", "", text, flags=re.MULTILINE)
    text = re.sub(r"\\tag\s*\{[^}]+\}", "", text)
    text = re.sub(r"\\chapter\*?\s*\{[^{}]*\}", "", text, count=1)
    text = re.sub(r"\\section\*?\s*\{[^{}]*\}", "", text, count=1)
    text = re.sub(r"\\unitheading\s*\{[^{}]*\}\s*\{[^{}]*\}", "", text, count=1)
    # A legacy K-unit used a manual chapter-level TOC entry even though it is
    # now a section inside one of the 32 canonical chapters.  Keeping that
    # command would create false top-level bookmarks (K1--K11) in volumes and
    # in the complete book.
    text = re.sub(
        r"\\addcontentsline\s*\{toc\}\s*\{chapter\}\s*\{[^{}]*\}",
        "",
        text,
    )
    text = strip_command_definition(text, "diagramcaption")
    text = replace_macro_argument(text, "diagramcaption", strip_source_prefix)
    text = replace_macro_argument(text, "figcap", strip_source_prefix)
    text = replace_macro_argument(text, "origcaption", strip_source_prefix)

    begin = "\\begin{origexamplebox}"
    pos = 0
    while True:
        idx = text.find(begin, pos)
        if idx < 0:
            break
        brace = idx + len(begin)
        while brace < len(text) and text[brace].isspace():
            brace += 1
        if brace < len(text) and text[brace] == "{":
            arg, end = balanced_argument(text, brace)
            cleaned = strip_source_prefix(arg)
            text = text[:brace + 1] + cleaned + "}" + text[end:]
            pos = brace + len(cleaned) + 2
        else:
            pos = brace

    # Convert the common one-line legacy caption form into the automatic caption macro.
    text = re.sub(
        r"\\par\\smallskip\s*\{\\small\\color\{TextGray\}\s*(?:图|例(?:题)?)\s*[Kk0-9.]+\s*[：:]\s*([^{}\n]*(?:\$[^$]*\$[^{}\n]*)*)\}",
        lambda m: "\\figcap{" + m.group(1).strip() + "}", text)
    for old, new in EDITORIAL_REPLACEMENTS:
        text = text.replace(old, new)
    text = text.replace("示意示意", "示意")
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    asset_dir = directory / "assets"
    graphic_dirs = [directory.as_posix() + "/"]
    if asset_dir.exists():
        graphic_dirs.append(asset_dir.as_posix() + "/")
    graphicspath = "\\graphicspath{" + "".join("{" + path + "}" for path in graphic_dirs) + "}\n"
    from em_structure import PLANS as EM_PLANS, restructure as restructure_em
    if unit.key in EM_PLANS:
        text = restructure_em(unit.key, text)
        heading = ""
    else:
        heading = f"\\section{{{unit.title}}}\n"
    rendered = (graphicspath + heading + text.strip() + "\n") if chapter == 19 else ("{\n" + graphicspath + heading + text.strip() + "\n}\n")
    return rendered, source_number_map


def apply_chapter_layout(number: int, text: str) -> str:
    if number == 19:
        from em_structure import finish_chapter19
        text = finish_chapter19(text)
    if 5 <= number <= 13:
        from mechanics_teaching_layout import refine
        text = refine(number, text)
    if number in {1, 2, 3, 4, 5}:
        # The reviewed questions fit on one page, including the longest Mars
        # question. Keep givens, question drawings and captions together.
        # This is chapter-local; other reviewed chapters keep their policies.
        text = "\\begingroup\n\\tcbset{breakable/.default=false}\n" + text + "\n\\endgroup\n"
        text = text.replace(r"\begin{xesolution}", r"\Needspace{6\baselineskip}\begin{xesolution}")
        if number in {2, 3, 4}:
            # Legacy fixed reservations were tuned before question figures
            # were restored; they now create near-empty continuation pages.
            text = re.sub(r"\\KinematicKeepSpace\{[^{}]+\}", "", text)
            text = re.sub(r"\\ifdefined\\Needspace\\Needspace\{[^{}]+\}\\fi", "", text)
    if number in {19, 20, 21, 22}:
        # Chapter-local scope: never change pagination policies of reviewed chapters.
        text = "\\begingroup\n\\tcbset{breakable/.default=false}\n" + text + "\n\\endgroup\n"
        text = text.replace(r"\subsection*{", r"\subsection{")
        text = re.sub(r"\\Needspace\{\d+\\baselineskip\}", "", text)
        if number in {21,22}:
            text = re.sub(r"\\Needspace\{[0-9.]+\\textheight\}", "", text)
            text = re.sub(r"第\s*\d+\s*题[。：]?", "", text)
        text = text.replace(r"\begin{origexamplebox}",r"\Needspace{12\baselineskip}\begin{origexamplebox}")
        if number in {21,22}:
            text = text.replace(r"\Needspace{12\baselineskip}",r"\Needspace{6\baselineskip}")
        text = text.replace(r"\end{origexamplebox}",r"\end{origexamplebox}\par\nopagebreak[4]")
        pattern = re.compile(r"(?m)^\\[A-Za-z]+\s*\n\\(?:diagramcaption|figcap)\{")
        edits=[]
        for m in pattern.finditer(text):
            _,end=balanced_argument(text,m.end()-1)
            while text[end:end+7]==r"\label{": _,end=balanced_argument(text,end+6)
            edits.append((m.start(),end))
        for start,end in reversed(edits):
            text=text[:start]+r"\par\noindent\begin{minipage}{\linewidth}"+'\n'+text[start:end]+'\n'+r"\end{minipage}\par\medskip"+text[end:]
    if number in {17, 18}:
        text = "\\begingroup\n" + text + "\n\\endgroup\n"
    if number == 17:
        text = text.replace(r"\subsection*{", r"\subsection{")
    if number in {15, 16}:
        text = text.replace(r"\subsection*{", r"\subsection{")
        # One reservation before each question; a negative break penalty right
        # before its answer used to strand even short answers on the next page.
        text = re.sub(r"\\Needspace\{\d+\\baselineskip\}", "", text)
        question_reserve = 12 if number == 16 else 16
        text = text.replace(r"\begin{origexamplebox}", rf"\Needspace{{{question_reserve}\baselineskip}}\begin{{origexamplebox}}")
        # Bind figure call, caption and its labels as one unbreakable unit.
        # Do not modify other chapters or turn whole solutions into boxes.
        pattern = re.compile(r"(?m)^\\(?:redrawimage(?:\[[^\]]+\])?\{[^}]+\}|[A-Za-z]+)\s*\n\\(?:diagramcaption|figcap)\{")
        edits = []
        for match in pattern.finditer(text):
            _, end = balanced_argument(text, match.end()-1)
            while text[end:end+7] == r"\label{":
                _, end = balanced_argument(text, end+6)
            edits.append((match.start(), end))
        for start, end in reversed(edits):
            text = text[:start] + r"\par\noindent\begin{minipage}{\linewidth}" + '\n' + text[start:end] + '\n' + r"\end{minipage}\par\medskip" + text[end:]
        # Suppress break after an uncaptioned drawing's center environment.
        text = text.replace(r"\end{center}", r"\end{center}\nopagebreak[2]")
    if number in {11, 12, 13, 14}:
        text = text.replace(r"\begin{origexamplebox}", r"\Needspace{16\baselineskip}\begin{origexamplebox}")
        text = text.replace(r"\begin{center}", r"\begin{center}\begin{minipage}{\linewidth}\centering")
        text = text.replace(r"\end{center}", r"\end{minipage}\end{center}")
    """Keep reviewed chapter-local pagination in both full and narrow builds."""
    if number in {6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}:
        text = "\\begingroup\n\\tcbset{breakable/.default=false}\n" + text + "\n\\endgroup\n"
        text = text.replace(r"\begin{xesolution}", r"\Needspace{6\baselineskip}\begin{xesolution}")
        if number in {15, 16}:
            text = text.replace(r"\Needspace{6\baselineskip}\begin{xesolution}", r"\par\nopagebreak[4]\begin{xesolution}")
            text = text.replace(r"\end{origexamplebox}", r"\end{origexamplebox}\par\nopagebreak[4]")
    if number in {11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22}:
        # Elastic reservations participate in TeX's page builder. The old
        # pagegoal/pagetotal test could emit an almost empty page after a split.
        reserve = r"""\renewcommand{\Needspace}[1]{\par\begingroup
\dimen0=#1\relax\vskip0pt plus\dimen0\penalty-100
\vskip0pt plus-\dimen0\vskip\dimen0\penalty9999\vskip-\dimen0
\vskip0pt\endgroup}
"""
        text = text.replace("\\begingroup\n", "\\begingroup\n" + reserve, 1)
        text = text.replace(r"\begin{starread}", r"\begingroup\tcbset{breakable/.default=true}\begin{starread}")
        text = text.replace(r"\end{starread}", r"\end{starread}\endgroup")
    if number in {9, 10, 11, 12, 13, 14, 15, 16, 17, 18}:
        text = '\\hypersetup{bookmarksdepth=3}\n' + text + '\n\\hypersetup{bookmarksdepth=2}\n'
    if 19 <= number <= 26:
        from em_teaching_layout import refine as refine_em_layout
        text = refine_em_layout(number, text)
    text = refine_thermal_layout(number, text)
    if 14 <= number <= 18:
        from thermal_teaching_layout import refine as refine_thermal_teaching
        text = refine_thermal_teaching(number, text)
    if number in {31, 32}:
        from modern_teaching_layout import refine as refine_modern_layout
        text = refine_modern_layout(number, text)
    if 27 <= number <= 30:
        from optics_teaching_layout import refine as refine_optics_layout
        text = refine_optics_layout(number, text)
    return text


def refine_thermal_layout(number: int, text: str) -> str:
    """Thermal modules are actual sections; drawings stay with their captions."""
    if number in {14, 15, 16, 17}:
        outer = rf'\section{{{CHAPTERS[number]["legacy"][0].title}}}'
        assert text.count(outer) == 1
        text = text.replace(outer, '', 1)
        text = text.replace(r'\subsection*{', r'\section{').replace(r'\subsection{', r'\section{')
        text = text.replace(r'\subsubsection*{', r'\subsection{')
        first = text.index(r'\begin{origexamplebox}')
        text = text[:first] + r'\section{综合例题}' + '\n' + text[first:]
    if number == 17:
        pattern = re.compile(r'(?m)^\\[A-Za-z]+\s*\n\\(?:diagramcaption|figcap)\{')
        edits = []
        for match in pattern.finditer(text):
            _, end = balanced_argument(text, match.end()-1)
            while text[end:end+7] == r'\label{':
                _, end = balanced_argument(text, end+6)
            edits.append((match.start(), end))
        for start, end in reversed(edits):
            text = text[:start] + r'\par\noindent\begin{minipage}{\linewidth}' + '\n' + text[start:end] + '\n' + r'\end{minipage}\par\medskip' + text[end:]
    if number in {17, 18}:
        text = text.replace(r'\begin{center}', r'\begin{center}\begin{minipage}{\linewidth}\centering')
        text = text.replace(r'\end{center}', r'\end{minipage}\end{center}')
    return text


def generate() -> dict:
    if GENERATED.exists():
        shutil.rmtree(GENERATED)
    (GENERATED / "chapters").mkdir(parents=True)
    mapping = {"chapters": []}
    new_dir = BOOK / "chapters" / "new"
    for number, spec in CHAPTERS.items():
        parts = [f"\\chapter{{{spec.get('display_title', spec['title'])}}}\n"]
        source_units = []
        source_number_maps = []
        if number == 1:
            # Chapter 1 is prerequisite-driven rather than source-volume-driven:
            # dimensions/vectors/coordinates must precede calculus, Taylor
            # follows differentiation, and phasors/ODEs close the chapter.
            # Keep one authoritative foundations file, but place its sections
            # around the two fully restored legacy units in this logical order.
            foundation_name = spec["new"][0]
            foundation_path = new_dir / foundation_name
            foundation = foundation_path.read_text(encoding="utf-8")
            taylor_marker = "\\section{泰勒展开与近似的阶}"
            phasor_marker = "\\section{复数相量}"
            if taylor_marker not in foundation or phasor_marker not in foundation:
                raise RuntimeError("Chapter 1 foundation section markers are missing")
            basics, remainder = foundation.split(taylor_marker, 1)
            taylor_body, tail = remainder.split(phasor_marker, 1)
            taylor = taylor_marker + taylor_body
            phasor_and_ode = phasor_marker + tail

            rendered_legacy: dict[str, str] = {}
            for unit in spec["legacy"]:
                rendered, unit_map = extract_legacy(unit, number)
                rendered_legacy[unit.key] = rendered
                source_number_maps.append({"source": unit.key, "objects": unit_map})

            parts.extend([
                _qualify_existing_labels(basics, number),
                rendered_legacy["s14"],
                _qualify_existing_labels(taylor, number),
                rendered_legacy["s15"],
                _qualify_existing_labels(phasor_and_ode, number),
            ])
            source_units.extend([foundation_name, "s14", "s15"])
        else:
            for unit in spec["legacy"]:
                rendered, unit_map = extract_legacy(unit, number)
                parts.append(rendered)
                source_units.append(unit.key)
                source_number_maps.append({"source": unit.key, "objects": unit_map})
            for name in spec["new"]:
                path = new_dir / name
                if not path.exists():
                    raise FileNotFoundError(path)
                new_text = path.read_text(encoding="utf-8")
                if number in {10, 11, 12, 13}:
                    new_text = flatten_inputs(new_text, path.parent, set())
                parts.append(_qualify_existing_labels(new_text, number))
                source_units.append(name)
        target = GENERATED / "chapters" / f"ch{number:02d}.tex"
        target.write_text(apply_chapter_layout(number, normalize_visible_eponyms("\n".join(parts))), encoding="utf-8")
        if 27 <= number <= 30:
            from optics_teaching_layout import update_source_maps
            update_source_maps(number, source_number_maps)
        mapping["chapters"].append({
            "chapter": number,
            "title": spec["title"],
            "sources": source_units,
            "source_number_maps": source_number_maps,
        })
    (GENERATED / "source-map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(HERE / "audit_electromagnetism.py")], cwd=BOOK, check=True)
    subprocess.run([sys.executable, str(HERE / "build_appendix_e.py")], cwd=BOOK, check=True)
    generate_wrappers(mapping)
    return mapping


def _wrapper(title: str, chapters: list[int], *, toc: bool, after: str = "") -> str:
    first = min(chapters)
    inputs = "\n".join(f"\\input{{generated/chapters/ch{number:02d}.tex}}" for number in chapters)
    toc_tex = "\\tableofcontents\n" if toc else ""
    if toc and chapters == list(range(5, 14)):
        # Local directory spacing prevents a lone final entry on a third TOC page.
        toc_tex = "\\begingroup\n\\setlength{\\parskip}{0pt}\n\\tableofcontents\n\\clearpage\n\\endgroup\n"
    return f"""% Generated by tools/build_restructured.py; do not edit directly.
\\documentclass[UTF8,zihao=-4,oneside,openany]{{ctexbook}}
\\input{{style.tex}}
\\hypersetup{{
  pdftitle={{高中物理竞赛一轮讲义：{title}}},
  pdfsubject={{高中物理竞赛一轮讲义：{title}}}
}}
\\begin{{document}}
\\frontmatter
\\hypersetup{{pageanchor=false}}
\\begin{{titlepage}}
  \\centering
  \\vspace*{{0.26\\textheight}}
  {{\\Huge\\bfseries 高中物理竞赛一轮讲义\\par}}
  \\vspace{{1.2em}}
  {{\\Large {title}\\par}}
  \\vfill
\\end{{titlepage}}
\\hypersetup{{pageanchor=true}}
{toc_tex}\\mainmatter
\\setcounter{{chapter}}{{{first - 1}}}
{inputs}
{after}
\\end{{document}}
"""


def generate_wrappers(mapping: dict) -> None:
    wrappers = GENERATED / "wrappers"
    chapter_dir = wrappers / "chapters"
    volume_dir = wrappers / "volumes"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    volume_dir.mkdir(parents=True, exist_ok=True)
    appendix_input = """\\appendix
\\setcounter{chapter}{4}
\\input{generated/appendices/appendix-e.tex}"""
    deliverables = {"chapters": [], "advanced": [], "volumes": [], "appendices": []}
    title_by_number = {item["chapter"]: item["title"] for item in mapping["chapters"]}
    for number in range(1, 33):
        title = title_by_number[number]
        wrapper = chapter_dir / f"ch{number:02d}.tex"
        wrapper.write_text(_wrapper(f"第{number}章　{title}", [number], toc=False), encoding="utf-8")
        deliverables["chapters"].append({
            "chapter": number,
            "wrapper": str(wrapper.relative_to(BOOK)),
            "output": f"高中物理竞赛一轮讲义_第{number:02d}章_{title}.pdf",
        })
    for volume, title, start, end in VOLUMES:
        wrapper = volume_dir / f"volume{volume}.tex"
        wrapper.write_text(
            _wrapper(
                f"第{volume}卷　{title}", list(range(start, end + 1)), toc=True,
                after=appendix_input if volume == 4 else "",
            ),
            encoding="utf-8",
        )
        deliverables["volumes"].append({
            "volume": volume, "title": title, "chapters": [start, end],
            "wrapper": str(wrapper.relative_to(BOOK)),
            "output": f"高中物理竞赛一轮讲义_第{volume}卷_{title}.pdf",
        })
    advanced_inputs = "\n".join(f"\\input{{advanced/{unit}.tex}}" for unit, _ in ADVANCED_UNITS)
    volume7_wrapper = volume_dir / "volume7.tex"
    volume7_wrapper.write_text(
        f"""% Generated by tools/build_restructured.py; do not edit directly.
\\documentclass[UTF8,zihao=-4,oneside,openany]{{ctexbook}}
\\input{{style.tex}}
\\hypersetup{{pdftitle={{高中物理竞赛一轮讲义：第7卷 高阶选读}}}}
\\begin{{document}}
\\frontmatter
\\hypersetup{{pageanchor=false}}
\\begin{{titlepage}}
  \\centering
  \\vspace*{{0.26\\textheight}}
  {{\\Huge\\bfseries 高中物理竞赛一轮讲义\\par}}
  \\vspace{{1.2em}}
  {{\\Large 第7卷　高阶选读\\par}}
  \\vfill
  {{\\color{{TextGray}}含完整证明、解答与解图\\par}}
\\end{{titlepage}}
\\hypersetup{{pageanchor=true}}
\\tableofcontents
\\mainmatter
{advanced_inputs}
\\end{{document}}
""",
        encoding="utf-8",
    )
    deliverables["volumes"].append({
        "volume": 7,
        "title": "高阶选读",
        "advanced_units": [unit for unit, _ in ADVANCED_UNITS],
        "wrapper": str(volume7_wrapper.relative_to(BOOK)),
        "output": "高中物理竞赛一轮讲义_第7卷_高阶选读_含解答与解图.pdf",
    })
    for unit, title in ADVANCED_UNITS:
        wrapper = BOOK / "advanced" / f"{unit}-standalone.tex"
        if not wrapper.exists():
            raise FileNotFoundError(wrapper)
        deliverables["advanced"].append({
            "unit": unit,
            "title": title,
            "wrapper": str(wrapper.relative_to(BOOK)),
            "output": f"高中物理竞赛一轮讲义_高阶选读_{unit}_{title}_含解答与解图.pdf",
        })
    appendix_wrapper = wrappers / "appendix-e.tex"
    appendix_wrapper.write_text(
        """% Generated by tools/build_restructured.py; do not edit directly.
\\documentclass[UTF8,zihao=-4,oneside,openany]{ctexbook}
\\input{style.tex}
\\begin{document}
\\frontmatter
\\hypersetup{pageanchor=false}
\\begin{titlepage}
  \\centering
  \\vspace*{0.26\\textheight}
  {\\Huge\\bfseries 高中物理竞赛一轮讲义\\par}
  \\vspace{1.2em}
  {\\Large 附录E　电磁学补充专题\\par}
  \\vfill
  {\\color{TextGray}含完整解答与解图\\par}
\\end{titlepage}
\\hypersetup{pageanchor=true}
\\mainmatter
\\appendix
\\setcounter{chapter}{4}
\\input{generated/appendices/appendix-e.tex}
\\end{document}
""",
        encoding="utf-8",
    )
    deliverables["appendices"].append({
        "appendix": "E",
        "wrapper": str(appendix_wrapper.relative_to(BOOK)),
        "output": "高中物理竞赛一轮讲义_附录E_电磁学补充专题_含解答与解图.pdf",
    })
    deliverables["complete"] = {
        "wrapper": "main.tex",
        "output": "高中物理竞赛一轮讲义.pdf",
    }
    (GENERATED / "deliverables.json").write_text(
        json.dumps(deliverables, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def compile_tex(main: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    plugin = Path("/Users/dongxingxi/.codex/plugins/cache/openai-bundled/latex/0.2.6")
    cmd = ["python3", str(plugin / "scripts/compile_latex.py"), str(main),
           "--compiler", "texlive", "--engine", "xelatex", "--output-directory", str(out_dir)]
    env = os.environ.copy()
    # Project-local glyph list supplements Computer Modern's missing Unicode
    # names without changing fonts, glyph outlines, or page layout.
    env['TEXFONTMAPS'] = str(BOOK) + ':' + env.get('TEXFONTMAPS', '')
    subprocess.run(cmd, cwd=BOOK, env=env, check=True)
    glyphs = BOOK / 'texglyphlist.txt'
    pdf, xdv = out_dir / (main.stem + '.pdf'), out_dir / (main.stem + '.xdv')
    # latexmk does not track AGL files, so refresh only the PDF conversion when
    # the local mapping changed after the most recent successful build.
    if glyphs.exists() and xdv.exists() and pdf.exists() and glyphs.stat().st_mtime > pdf.stat().st_mtime:
        subprocess.run(['xdvipdfmx', '-o', str(pdf), str(xdv)], cwd=BOOK, env=env, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile", action="store_true")
    args = parser.parse_args()
    mapping = generate()
    print(f"generated {len(mapping['chapters'])} chapters")
    if args.compile:
        compile_tex(BOOK / "main.tex", BOOK / "build" / "complete")


if __name__ == "__main__":
    main()
