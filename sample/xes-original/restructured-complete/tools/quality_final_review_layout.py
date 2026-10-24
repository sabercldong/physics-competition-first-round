"""Keep solution headings with their first paragraph, display or diagram."""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parents[1]
OLD = r"{\bfseries\color{DeepBlue}解答}\quad"
NEW = r"\LectureSolutionHeading"
DEFINITION = r"""
% FinalReviewSolutionHeading20261024
\makeatletter
\newcommand{\LectureSolutionHeading}{%
  \par\noindent{\bfseries\color{DeepBlue}解答}\par\nobreak
  \@afterindentfalse\@afterheading}
\makeatother
"""


def apply_chapter_revision(number, text):
    return apply_file_revision(f"ch{number:02d}.tex", text)


def apply_file_revision(name, text):
    text = text.replace(OLD, NEW)
    text = re.sub(r"(\\begin\{(?:xe|adv)solution\})\s*\\par\s*\\(?:pagebreak|clearpage|newpage)(?:\[[^]]*\])?", r"\1", text)
    # These long question boxes otherwise leave most of the preceding page empty.
    # Only the text may split; their diagram/caption minipages remain intact.
    split_questions = {
        "ch01.tex": ["变力功与气体过程功"],
        "ch04.tex": ["火星的顺行与逆行时间"],
        "ch14.tex": ["【托里拆利实验】", "【气体膨胀】"],
        "ch15.tex": ["【循环过程】"],
        "ch21.tex": ["【电离计数器】"],
        "ch23.tex": ["【电子显微镜】"],
    }
    for title in split_questions.get(name, []):
        marker = "% FinalReviewQuestionSplit20261024 " + title
        if marker not in text:
            pattern = (r"(?:\\Needspace\{[^\n]*?\}\s*)*"
                       + re.escape(r"\begin{origexamplebox}{" + title + "}")
                       + r".*?\\end\{origexamplebox\}")
            def split_box(match):
                box = re.sub(r"^(?:\\Needspace\{[^\n]*?\}\s*)+", "", match[0])
                return (marker + "\n" + r"\tcbset{breakable/.default=true}" + "\n"
                        + box + "\n" + r"\tcbset{breakable/.default=false}")
            text, count = re.subn(pattern, split_box, text, count=1, flags=re.S)
            if count != 1:
                raise ValueError(f"Missing final layout question: {name}: {title}")
        if name in {"ch21.tex", "ch23.tex"}:
            start = text.index(marker)
            end = text.index(r"\begin{xesolution}", start)
            block = text[start:end]
            if r"\pagebreak[0]" not in block:
                # Break between the complete question and answer if necessary;
                # LectureSolutionHeading still protects the first answer block.
                text = text[:end] + "\\par\\pagebreak[0]\n" + text[end:]
    if name == "ch21.tex":
        text = text.replace(r"\diagramcaption{题图：平行板电离室。", r"\diagramcaption{解图：平行板电离室。")
    if name == "ch17.tex":
        text = text.replace(
            r"\Needspace{18\baselineskip}" + "\n"
            + r"\par\noindent\begin{minipage}{\linewidth}" + "\n" + r"\criticalPointFigure",
            r"\par\noindent\begin{minipage}{\linewidth}" + "\n" + r"\criticalPointFigure")
    if name == "style.tex" and "FinalReviewSolutionHeading20261024" not in text:
        anchor = r"\NewDocumentEnvironment{xesolution}"
        text = text.replace(anchor, DEFINITION + "\n" + anchor, 1)
    return text


if __name__ == "__main__":
    paths = [BOOK / "style.tex", BOOK / "advanced/layout.tex"]
    paths += list((BOOK / "generated/chapters").glob("ch*.tex"))
    for path in paths:
        before = path.read_text()
        after = apply_file_revision(path.name, before)
        if before != after:
            path.write_text(after)
            print(f"final layout {path.relative_to(BOOK)}")
