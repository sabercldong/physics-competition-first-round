#!/usr/bin/env python3
"""Narrow chapter-six rebuild. Never publishes or regenerates other chapters."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
import build_restructured as book

DEST = book.BOOK / 'build/review-ch06-20260908'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def regenerate():
    protected = {str(p): digest(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem != 'ch06'}
    spec = book.CHAPTERS[6]
    parts, maps = [f"\\chapter{{{spec['title']}}}\n"], []
    for unit in spec['legacy']:
        body, objects = book.extract_legacy(unit, 6)
        parts.append(body)
        maps.append({'source': unit.key, 'objects': objects})
    text = book.normalize_visible_eponyms('\n'.join(parts))
    assert text.count(r'\begin{origexamplebox}') == 31
    assert text.count(r'\begin{xesolution}') == 31
    # The short prompts fit a page. Locally change the default of the existing
    # breakable key; the shared environment and all other chapters stay intact.
    text = '\\begingroup\n\\tcbset{breakable/.default=false}\n' + text + '\n\\endgroup\n'
    text = text.replace(r'\begin{xesolution}', r'\Needspace{6\baselineskip}\begin{xesolution}')
    (book.GENERATED/'chapters/ch06.tex').write_text(text)
    mapping_path = book.GENERATED/'source-map.json'
    mapping = json.loads(mapping_path.read_text())
    next(c for c in mapping['chapters'] if c['chapter'] == 6)['source_number_maps'] = maps
    mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    (book.GENERATED/'wrappers/chapters/ch06.tex').write_text(book._wrapper(f"第6章　{spec['title']}", [6], toc=False))
    (book.GENERATED/'wrappers/volumes/volume2.tex').write_text(book._wrapper('第2卷　力学', list(range(5,14)), toc=True))
    dpath = book.GENERATED/'deliverables.json'
    d = json.loads(dpath.read_text())
    for entry in d['chapters']:
        if entry['chapter'] == 6:
            entry['output'] = entry['output'].replace('_含解答与解图.pdf', '.pdf')
    for entry in d['volumes']:
        if entry['volume'] == 2:
            entry['output'] = entry['output'].replace('_含解答与解图.pdf', '.pdf')
    dpath.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    assert all(digest(Path(p)) == h for p,h in protected.items())
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST/'protected-chapters.json').write_text(json.dumps(protected, indent=2))
    print('Only chapter 6 regenerated: 31 examples / 31 solutions; 31 other chapters unchanged.')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--regenerate', action='store_true')
    p.add_argument('--target', choices=['ch06','volume2','main'])
    p.add_argument('--verify-two-passes', action='store_true', help='Two recorded XeLaTeX passes on the frozen source, then PDF conversion.')
    args = p.parse_args()
    if args.regenerate:
        regenerate()
    if args.target:
        os.environ['TEXINPUTS'] = str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
        t = args.target
        wrapper = (book.BOOK/'main.tex' if t=='main' else book.GENERATED/'wrappers/volumes/volume2.tex' if t=='volume2' else book.GENERATED/'wrappers/chapters/ch06.tex')
        book.compile_tex(wrapper, DEST/t)
        if args.verify_two_passes:
            env=os.environ.copy()
            env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
            for n in (1,2):
                with (DEST/t/f'verify-pass-{n}.txt').open('w') as log:
                    subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error',
                                    '-synctex=1','-recorder',f'-output-directory={DEST/t}',str(wrapper)],
                                   cwd=book.BOOK,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
            subprocess.run(['xdvipdfmx','-q','-o',str(DEST/t/(wrapper.stem+'.pdf')),
                            str(DEST/t/(wrapper.stem+'.xdv'))],cwd=book.BOOK,env=env,check=True)

if __name__ == '__main__':
    main()
