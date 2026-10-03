#!/usr/bin/env python3
"""Build chapter four only from maintained units; no automatic publication."""
import json
import os
import argparse
import subprocess
import sys
import build_restructured as book


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compile', action='store_true')
    args = parser.parse_args()
    subprocess.run([sys.executable, str(book.LEGACY / 'kinematics-supplement/generate_ch04_geometry.py')], check=True)
    spec = book.CHAPTERS[4]
    parts = [f"\\chapter{{{spec['title']}}}\n"]
    maps = []
    for unit in spec['legacy']:
        body, objects = book.extract_legacy(unit, 4)
        parts.append(body)
        maps.append({'source': unit.key, 'objects': objects})
    text = book.normalize_visible_eponyms('\n'.join(parts))
    assert text.count(r'\begin{origexamplebox}') == 32
    assert text.count(r'\begin{xesolution}') == 32
    (book.GENERATED / 'chapters/ch04.tex').write_text(text, encoding='utf-8')
    path = book.GENERATED / 'source-map.json'
    mapping = json.loads(path.read_text())
    next(c for c in mapping['chapters'] if c['chapter'] == 4)['source_number_maps'] = maps
    path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding='utf-8')
    wrapper = book.GENERATED / 'wrappers/chapters/ch04.tex'
    source = book._wrapper(f"第4章　{spec['title']}", [4], toc=False)
    source = source.replace('（含解答与解图）', '')
    source = source.replace(r'{\color{TextGray}含完整解答与解图\par}', '')
    wrapper.write_text(source, encoding='utf-8')
    print('Chapter 4 regenerated: 32 examples, 32 solutions.')
    if args.compile:
        os.environ['TEXINPUTS'] = str(book.BOOK) + '//:' + os.environ.get('TEXINPUTS', '')
        book.compile_tex(wrapper, book.BOOK / 'build/review-ch04-20260907')


if __name__ == '__main__':
    main()
