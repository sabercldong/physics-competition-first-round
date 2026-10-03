#!/usr/bin/env python3
"""Narrow, non-publishing rebuild for the September 7 review of chapters 1–3."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import build_restructured as book

DEST = book.BOOK / 'build/review-ch01-03-20260907'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def regenerate():
    protected = {str(p): digest(p) for p in (book.GENERATED/'chapters').glob('ch*.tex')
                 if p.stem not in ('ch01','ch02','ch03')}
    mapping_path = book.GENERATED/'source-map.json'
    mapping = json.loads(mapping_path.read_text())
    for n, count in ((1,36),(2,21),(3,51)):
        spec = book.CHAPTERS[n]
        parts = [f"\\chapter{{{spec.get('display_title', spec['title'])}}}\n"]
        rendered, maps = {}, []
        for unit in spec['legacy']:
            rendered[unit.key], objects = book.extract_legacy(unit,n)
            maps.append({'source':unit.key,'objects':objects})
        if n == 1:
            source = (book.BOOK/'chapters/new/ch01-math-foundations.tex').read_text()
            tmark, pmark = r'\section{泰勒展开与近似的阶}', r'\section{复数相量}'
            basics, rest = source.split(tmark,1)
            taylor, tail = rest.split(pmark,1)
            parts.extend([book._qualify_existing_labels(basics,n),rendered['s14'],
                          book._qualify_existing_labels(tmark+taylor,n),rendered['s15'],
                          book._qualify_existing_labels(pmark+tail,n)])
        else:
            parts.extend(rendered.values())
        content = book.normalize_visible_eponyms('\n'.join(parts))
        assert content.count(r'\begin{origexamplebox}') == count, (n,'examples')
        assert content.count(r'\begin{xesolution}') == count, (n,'solutions')
        (book.GENERATED/f'chapters/ch{n:02}.tex').write_text(content)
        record = next(x for x in mapping['chapters'] if x['chapter']==n)
        record['source_number_maps'] = maps
        wrapper = book._wrapper(f"第{n}章　{spec.get('display_title',spec['title'])}",[n],toc=False)
        (book.GENERATED/f'wrappers/chapters/ch{n:02}.tex').write_text(wrapper)
    mapping_path.write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
    deliverables_path = book.GENERATED/'deliverables.json'
    deliverables = json.loads(deliverables_path.read_text())
    for entry in deliverables['chapters']:
        if entry['chapter'] in (1,2,3):
            entry['output'] = entry['output'].replace('_含解答与解图.pdf','.pdf')
    for entry in deliverables['volumes']:
        if entry['volume'] == 1:
            entry['output'] = entry['output'].replace('_含解答与解图.pdf','.pdf')
    deliverables_path.write_text(json.dumps(deliverables,ensure_ascii=False,indent=2))
    (book.GENERATED/'wrappers/volumes/volume1.tex').write_text(
        book._wrapper('第1卷　数学工具与运动学',list(range(1,5)),toc=True))
    assert all(digest(Path(p))==h for p,h in protected.items())
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'protected-chapters.json').write_text(json.dumps(protected,indent=2))
    print('Regenerated only chapters 1–3; counts 36/21/51 unchanged. Chapters 4–32 unchanged.')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--regenerate',action='store_true')
    parser.add_argument('--target',choices=['ch01','ch02','ch03','volume1','main'])
    args=parser.parse_args()
    if args.regenerate:
        regenerate()
    if args.target:
        os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
        t=args.target
        wrapper=(book.BOOK/'main.tex' if t=='main' else
                 book.GENERATED/f'wrappers/volumes/{t}.tex' if t=='volume1' else
                 book.GENERATED/f'wrappers/chapters/{t}.tex')
        book.compile_tex(wrapper,DEST/t)

if __name__=='__main__':
    main()
