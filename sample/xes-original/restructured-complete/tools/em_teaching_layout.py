"""Chapter-local pagination for the reviewed electromagnetism volume."""
import re


def refine(number, text):
    if not 19 <= number <= 26:
        return text
    # Fixed reservations accumulate with the question box's own page builder.
    # The box knows its actual height; avoid reserving an additional 6–12 lines.
    text = re.sub(r"\\Needspace\{(?:[0-9.]+\\textheight|\d+\\baselineskip)\}", "", text)
    if number == 22:
        # Size the oscillator frame from its label; keep feed wires on its top edge.
        text = text.replace(r"\draw (-.8,-2.9) rectangle(.8,-3.5);\node at(0,-3.2){高频振荡器};",
                            r"\node[draw,inner xsep=6pt,minimum height=.6cm,anchor=north] at(0,-2.9){高频振荡器};")
    if number == 21:
        # The large ion-chamber question must not drag its following analysis
        # drawing onto the same page; allow a normal break after this frame.
        text = re.sub(r"(\\begin\{origexamplebox\}\{[^}]*电离计数器[^}]*\}.*?\\end\{origexamplebox\})\\par\\nopagebreak\[4\]",
                      lambda m: m[1] + r"\par\pagebreak[1]", text, flags=re.S)
    # All reviewed question blocks fit on a page, including their givens-only
    # drawing. Keep the statement whole; the worked answer may still split.
    local = r"""\begingroup
\tcbset{breakable/.default=false,after={\par\nobreak\smallskip}}
\RenewDocumentEnvironment{xesolution}{+b}{%
  \par\nobreak\smallskip\nobreak\begingroup\small
  \clubpenalties 2 10000 10000\displaywidowpenalties 2 10000 10000\noindent
  {\bfseries\color{DeepBlue}解答}\quad #1\par\endgroup\smallskip
}{}
"""
    return local + text + "\n\\endgroup\n"
