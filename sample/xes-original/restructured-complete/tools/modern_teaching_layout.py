"""Keep modern-physics question boxes and drawings readable in every build."""
import re

def refine(number, text):
    if number not in {31, 32} or '% ModernLayout' in text:
        return text
    text = re.sub(r'\\Needspace\{\d+\\baselineskip\}', '', text)
    def label_solution(match):
        body = match.group(1).lstrip()
        if body.startswith(r'\begin{center}'):
            body = body.replace(r'\begin{center}', r'\begin{center}\raggedright\ModernAnswerLabel\par\smallskip\centering', 1)
        else:
            body = r'\ModernAnswerLabel\quad ' + body
        return r'\begin{xesolution}' + '\n' + body + r'\end{xesolution}'
    text = re.sub(r'\\begin\{xesolution\}(.*?)\\end\{xesolution\}', label_solution, text, flags=re.S)
    text = text.replace(r'\begin{center}', r'\begin{center}\begin{minipage}{\linewidth}\centering')
    text = text.replace(r'\end{center}', r'\end{minipage}\end{center}')
    local = r'''% ModernLayout
\begingroup
\hypersetup{bookmarksdepth=3}
\tcbset{breakable/.default=false,after={\par\nobreak\smallskip}}
\newcommand{\ModernAnswerLabel}{{\bfseries\color{DeepBlue}解答}}
\RenewDocumentEnvironment{xesolution}{+b}{%
  \par\nobreak\smallskip\nobreak\begingroup\small
  \clubpenalties 2 10000 10000\displaywidowpenalties 2 10000 10000\noindent
  #1\par\endgroup\smallskip
}{}
'''
    text = text.replace(r'\begin{starread}', r'\begingroup\tcbset{breakable/.default=true}\begin{starread}')
    text = text.replace(r'\end{starread}', r'\end{starread}\endgroup')
    return local + text + '\n\\hypersetup{bookmarksdepth=2}\n\\endgroup\n'
