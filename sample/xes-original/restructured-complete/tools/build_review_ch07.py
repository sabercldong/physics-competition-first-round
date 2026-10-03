"""Rebuild Chapter 7 and its two containing books; never publish automatically."""
import argparse, hashlib, json, os, subprocess, re
from pathlib import Path
import build_restructured as book
DEST=book.BOOK/'build/review-ch07-20260908'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def regenerate():
    protected={str(p):sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem!='ch07'}
    spec=book.CHAPTERS[7]
    parts=[f"\\chapter{{{spec['title']}}}\n"]; maps=[]
    for unit in spec['legacy']:
        body,objects=book.extract_legacy(unit,7)
        parts.append(body); maps.append({'source':unit.key,'objects':objects})
    text=book.normalize_visible_eponyms('\n'.join(parts))
    assert text.count(r'\begin{origexamplebox}')==36
    assert text.count(r'\begin{xesolution}')==36
    assert text.count(r'\label{ch07:fig:')==54
    assert 'sollabel/.style={font=\\scriptsize,fill=white' not in text
    text=book.apply_chapter_layout(7,text)
    (book.GENERATED/'chapters/ch07.tex').write_text(text)
    mp=book.GENERATED/'source-map.json'; mapping=json.loads(mp.read_text())
    next(c for c in mapping['chapters'] if c['chapter']==7)['source_number_maps']=maps
    mp.write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
    (book.GENERATED/'wrappers/chapters/ch07.tex').write_text(book._wrapper(f"第7章　{spec['title']}",[7],toc=False))
    (book.GENERATED/'wrappers/volumes/volume2.tex').write_text(book._wrapper('第2卷　力学',list(range(5,14)),toc=True))
    dp=book.GENERATED/'deliverables.json'; data=json.loads(dp.read_text())
    for item in data['chapters']:
        if item['chapter']==7: item['output']=item['output'].replace('_含解答与解图.pdf','.pdf')
    dp.write_text(json.dumps(data,ensure_ascii=False,indent=2))
    assert all(sha(Path(p))==h for p,h in protected.items())
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'protected-chapters.json').write_text(json.dumps(protected,indent=2))
    print('Regenerated Chapter 7: 36 examples, 36 solutions, 54 numbered figures.')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--regenerate',action='store_true')
    parser.add_argument('--target',choices=['ch07','volume2','main'])
    parser.add_argument('--verify-two-passes',action='store_true')
    args=parser.parse_args()
    if args.regenerate: regenerate()
    if args.target:
        os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
        target=args.target
        wrapper=(book.BOOK/'main.tex' if target=='main' else book.GENERATED/'wrappers/volumes/volume2.tex' if target=='volume2' else book.GENERATED/'wrappers/chapters/ch07.tex')
        book.compile_tex(wrapper,DEST/target)
        if args.verify_two_passes:
            env=os.environ.copy(); env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
            for n in (1,2):
                with (DEST/target/f'verify-pass-{n}.txt').open('w') as log:
                    subprocess.run(['xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error',
                      '-synctex=1','-recorder',f'-output-directory={DEST/target}',str(wrapper)],
                      cwd=book.BOOK,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
            subprocess.run(['xdvipdfmx','-q','-o',str(DEST/target/(wrapper.stem+'.pdf')),
                            str(DEST/target/(wrapper.stem+'.xdv'))],cwd=book.BOOK,env=env,check=True)
if __name__=='__main__': main()
