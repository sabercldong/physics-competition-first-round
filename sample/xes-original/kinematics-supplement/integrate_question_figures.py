"""Idempotent mechanical insertion of the reviewed 58 question-only views."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
mapping=json.loads((ROOT/'data/question-figure-map.json').read_text())
pending={row['source_example']:row for row in mapping}
total=0
for path in sorted((ROOT/'units').glob('k*.tex')):
    text=path.read_text()
    def replace(m):
        global total
        number=m.group(1)
        if number not in pending:
            return m.group(0)
        row=pending.pop(number)
        total+=1
        call='\\'+row['macro']
        if call in m.group(0):
            return m.group(0)
        return m.group(0).replace(r'\end{origexamplebox}',
            '\\par 题图见图~\\ref{'+row['label']+'}。\n'+call+'\n'+r'\end{origexamplebox}')
    updated=re.sub(r'\\begin\{origexamplebox\}\{例(2\.\d+)\b.*?\\end\{origexamplebox\}',replace,text,flags=re.S)
    # Keep the solution heading with real reasoning. Move an initial diagram
    # after the first prose paragraph or displayed derivation, retaining all
    # content and geometry. This is an order-only, idempotent transformation.
    opening=re.compile(r'(\\begin\{xesolution\}\s*\n)(\\[A-Za-z]+(?:Diagram|Graphs))\s*\n')
    for match in reversed(list(opening.finditer(updated))):
        limit=updated.index(r'\end{xesolution}',match.end())
        tail=updated[match.end():limit]
        ends=[p for p in (tail.find('\n\n'),tail.find(r'\]')) if p>=0]
        if not ends:continue
        end=min(ends)+2
        # A paragraph break must not precede closing a displayed formula.
        first=tail[:end]
        if first.count(r'\[')!=first.count(r'\]'):continue
        updated=updated[:match.start()]+match[1]+first+'\n'+match[2]+'\n'+tail[end:]+updated[limit:]
    if updated!=text:
        path.write_text(updated)
assert total==58 and not pending,(total,pending)
print('58 question figure groups bound inside their own question environments.')
