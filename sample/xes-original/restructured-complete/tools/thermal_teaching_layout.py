"""Add thermal teaching bridges after legacy headings have been normalized.

Existing paragraphs, examples, solutions and figures are left intact.  Each
insertion has one explicit anchor; missing/ambiguous anchors fail the build.
"""
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[1] / 'chapters/new'
INSERTIONS = {
    14: [
        ('section', '理想气体物态方程', 'ch14-expansion-teaching.tex'),
        ('section', '理想气体压强的微观推导', 'ch14-mixture-teaching.tex'),
    ],
    15: [
        ('section', '机械功与准静态过程', 'ch15-transfer-teaching.tex'),
        ('section', '重力场中形成对流的条件', 'ch15-path-teaching.tex'),
    ],
    16: [('section', '熵的微观解释', 'ch16-entropy-teaching.tex')],
    17: [('section', '范德瓦耳斯方程', 'ch17-coexistence-teaching.tex')],
    18: [
        ('section', '微观状态、宏观状态与熵', 'ch18-counting-teaching.tex'),
        ('section', '能量均分定理', 'ch18-population-teaching.tex'),
        ('subsection', '动力学与概率描述之间的条件', 'ch18-effusion-teaching.tex'),
    ],
}

def refine(number: int, text: str) -> str:
    for level, title, filename in INSERTIONS.get(number, []):
        anchor = '\\' + level + '{' + title + '}'
        assert text.count(anchor) == 1, (number, anchor)
        addition = (CONTENT / filename).read_text()
        addition = addition.replace('\\begin{origexamplebox}',
                                    '\\Needspace{180pt}\n\\begin{origexamplebox}')
        addition = addition.replace('\\begin{xesolution}',
                                    '\\Needspace{65pt}\n\\begin{xesolution}')
        text = text.replace(anchor, addition.rstrip() + '\n\n' + anchor)
    return text
