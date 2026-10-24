"""Reproducible editorial overlay, applied after legacy layout transformations.

Existing reviewed generated chapters are preserved. All inserted text and TikZ
remain in chapters/quality-20261023; repeated application is a no-op.
"""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parent.parent
MARKER = "% QualityRevision20261023"

STAT_EXAMPLES = [
    ("体积比为四比一的两区域粒子数", "Asymmetric"),
    ("二项分布与最概然宏观态", "Binomial"),
    ("二能级系统的平均能量与热容", "TwoLevels"),
    ("等间隔能级的配分函数", "Ladder"),
    ("简并度能否抵消较高能量的不利因素", "Degeneracy"),
    ("氮分子的方均根速率", "Speeds"),
    ("麦克斯韦分布中的越阈概率", "Tail"),
    ("两种等量理想气体的混合熵", "Mixing"),
    ("能量相对涨落的粒子数标度", "Fluctuation"),
    ("小孔逸出为何使绝热容器中的气体冷却", "Effusion"),
]


def example_illustrations(text: str, title: str, name: str, prefix: str = "Stat") -> str:
    start = text.index(r"\begin{origexamplebox}{" + title + "}")
    question_end = text.index(r"\end{origexamplebox}", start)
    text = text[:question_end] + "\n\\" + prefix + "Q" + name + "\n" + text[question_end:]
    answer_start = text.index(r"\begin{xesolution}", question_end)
    answer_end = text.index(r"\end{xesolution}", answer_start)
    return text[:answer_end] + "\n\\" + prefix + "A" + name + "\n" + text[answer_end:]


def apply_base_revision(number: int, text: str) -> str:
    if MARKER in text:
        return text
    original = text
    text = text.replace("/Users/dongxingxi/Documents/物理竞赛一轮资料/", "../../../")
    changed = text != original
    if number == 18:
        chapter = re.search(r"\\chapter\{[^\n]*\}\s*", text)
        if chapter is None:
            raise ValueError("chapter 18 heading missing")
        text = text[:chapter.end()] + "\n\\tcbset{breakable/.default=false}\n\\input{chapters/quality-20261023/ch18-figures.tex}\n" + text[chapter.end():]
        for title, name in STAT_EXAMPLES:
            text = example_illustrations(text, title, name)
        text = text.replace(r"\subsection{信息量、条件熵与相关性}", r"\subsection{选读：信息量、条件熵与相关性}")
        text = text.replace(r"\subsection{连续分布与最大熵的条件}", r"\subsection{选读：连续分布与最大熵的条件}")
        text = text.replace(
            "而总量的平均值正比于 $N$，所以相对涨落通常按 $N^{-1/2}$ 衰减。",
            "若单个变量的均值非零且方差有限，总量平均值正比于 $N$，相对标准差才按 $N^{-1/2}$ 衰减；均值为零时不能用它作分母。")
        changed = True
    theory = {
        7: ("动量的分量守恒", "ch07-components.tex"),
        8: ("变力作功", "ch08-work.tex"),
        12: ("声强与声强级", "ch12-sound.tex"),
        14: ("分压按分子数分配，不按质量分配", "ch14-mixture.tex"),
        26: ("能量、动量与辐射压", "ch26-radiation.tex"),
        31: ("从谱线频移反求速度", "ch31-redshift.tex"),
    }
    if number in theory:
        title, filename = theory[number]
        start = text.index(r"\subsection{" + title + "}")
        next_section = re.search(r"\\(?:subsection|section)\*?\{|\\Needspace|\\begin\{origexamplebox\}", text[start + len(title) + 15:])
        if next_section is None:
            raise ValueError(f"section boundary missing in chapter {number}")
        pos = start + len(title) + 15 + next_section.start()
        text = text[:pos] + "\n\\input{chapters/quality-20261023/" + filename + "}\n\n" + text[pos:]
        changed = True
    supplements = {21: "ch21-conduction-devices.tex", 25: "ch25-power-applications.tex", 32: "ch32-laser.tex"}
    if number in supplements:
        end = text.index(r"\section{原子核、结合能与核反应}") if number == 32 else text.rfind(r"\endgroup")
        if end < 0:
            end = len(text)
        text = text[:end] + "\n\\begingroup\\tcbset{breakable/.default=false}\n\\input{chapters/quality-20261023/" + supplements[number] + "}\n\\endgroup\n" + text[end:]
        changed = True
    return MARKER + "\n" + text if changed else text


def apply_quality_revision(number: int, text: str) -> str:
    """Keep every reviewed stage when the legacy generator is run again."""
    from quality_revision_math import apply_chapter_revision as mathematics
    from quality_revision_mechanics import apply_chapter_revision as mechanics
    from quality_revision_thermal import apply_chapter_revision as thermal
    from quality_revision_em_optics import apply_chapter_revision as electromagnetism
    from quality_revision_theory_tikz import apply_chapter_revision as theory_tikz
    from quality_final_review_mechanics import apply_chapter_revision as final_mechanics
    from quality_final_review_thermal_fields import apply_chapter_revision as final_thermal
    from quality_final_review_em_optics import apply_chapter_revision as final_electromagnetism
    from quality_final_review_layout import apply_chapter_revision as final_layout
    text = apply_base_revision(number, text)
    for revise in [mathematics, mechanics, thermal, electromagnetism, theory_tikz,
                   final_mechanics, final_thermal, final_electromagnetism, final_layout]:
        text = revise(number, text)
    # Whole question boxes already decide whether they fit. A second reserve of
    # 30–43% of the page unnecessarily pushed short examples onto another page.
    return re.sub(r"\\Needspace\{0\.\d+\\textheight\}",
                  lambda _: r"\Needspace{8\baselineskip}", text)


def main() -> None:
    for number in range(1, 33):
        path = BOOK / f"generated/chapters/ch{number:02d}.tex"
        old = path.read_text()
        new = apply_quality_revision(number, old)
        if new != old:
            path.write_text(new)
            print(f"updated ch{number:02d}")


if __name__ == "__main__":
    main()
