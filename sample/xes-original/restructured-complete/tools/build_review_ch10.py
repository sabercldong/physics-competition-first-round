"""Rebuild Chapter 10 and its two containing books; never publish automatically."""
import argparse, hashlib, json, os, subprocess, re
from pathlib import Path
import build_restructured as book
DEST=book.BOOK/'build/review-ch10-20260909'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def regenerate():
    protected={str(p):sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem!='ch10'}
    spec=book.CHAPTERS[10]
    parts=[f"\\chapter{{{spec['title']}}}\n"]; maps=[]
    for name in spec['new']:
        path=book.BOOK/'chapters/new'/name
        parts.append(book.flatten_inputs(path.read_text(),path.parent,set()))
    ledger=book.BOOK/'audit/source-review/ch10-revision-ledger.json'
    if ledger.exists(): maps=json.loads(ledger.read_text())['sources']
    text=book.normalize_visible_eponyms('\n'.join(parts))
    assert text.count(r'\begin{origexamplebox}')==9
    assert text.count(r'\begin{xesolution}')==9
    assert text.count(r'\label{ch10:fig:')==29
    assert 'sollabel/.style={font=\\scriptsize,fill=white' not in text
    text=book.apply_chapter_layout(10,text)
    (book.GENERATED/'chapters/ch10.tex').write_text(text)
    mp=book.GENERATED/'source-map.json'; mapping=json.loads(mp.read_text())
    next(c for c in mapping['chapters'] if c['chapter']==10)['source_number_maps']=maps
    mp.write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
    (book.GENERATED/'wrappers/chapters/ch10.tex').write_text(book._wrapper(f"第10章　{spec['title']}",[10],toc=False))
    (book.GENERATED/'wrappers/volumes/volume2.tex').write_text(book._wrapper('第2卷　力学',list(range(5,14)),toc=True))
    dp=book.GENERATED/'deliverables.json'; data=json.loads(dp.read_text())
    for item in data['chapters']:
        if item['chapter']==10: item['output']=item['output'].replace('_含解答与解图.pdf','.pdf')
    dp.write_text(json.dumps(data,ensure_ascii=False,indent=2))
    assert all(sha(Path(p))==h for p,h in protected.items())
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'protected-chapters.json').write_text(json.dumps(protected,indent=2))
    print('Regenerated Chapter 10: 9 examples, 9 solutions, 29 numbered figure groups.')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--regenerate',action='store_true')
    parser.add_argument('--target',choices=['ch10','volume2','main'])
    parser.add_argument('--verify-two-passes',action='store_true')
    parser.add_argument('--verify-only',action='store_true',help='Repeat two explicit passes using already converged auxiliary files.')
    args=parser.parse_args()
    if args.regenerate: regenerate()
    if args.target:
        os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
        target=args.target
        wrapper=(book.BOOK/'main.tex' if target=='main' else book.GENERATED/'wrappers/volumes/volume2.tex' if target=='volume2' else book.GENERATED/'wrappers/chapters/ch10.tex')
        if args.verify_only:
            assert args.verify_two_passes
            assert (DEST/target/(wrapper.stem+'.aux')).exists()
        else:
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
