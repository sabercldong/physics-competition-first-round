"""Rebuild Chapter 9 and its two containing books; never publish automatically."""
import argparse, hashlib, json, os, subprocess, re
from pathlib import Path
import build_restructured as book
DEST=book.BOOK/'build/review-ch09-20260909'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def regenerate():
    protected={str(p):sha(p) for p in (book.GENERATED/'chapters').glob('ch*.tex') if p.stem!='ch09'}
    spec=book.CHAPTERS[9]
    parts=[f"\\chapter{{{spec['title']}}}\n"]; maps=[]
    for unit in spec['legacy']:
        body,objects=book.extract_legacy(unit,9)
        figure_rows={
            's16':[(3,'14.1','cross'),(4,'14.2','particle'),(6,'14.3','kepler'),
              (8,'14.4','inertia'),(10,'14.5','cosmic'),(11,'14.6','gyro'),
              (12,'14.7','area'),(13,'14.8','conical'),(13,'14.9','dumbbell-ground'),
              (13,'14.10','dumbbell-collision'),(14,'14.11','seesaw'),(14,'14.12','funnel')],
            's17':[(16,'15.1','euler'),(17,'15.2','rolling'),(18,None,'nonparallel'),
              (19,'15.3','incline'),(21,'15.4','brake'),(21,'15.5','two-wheels'),
              (22,'15.6','billiard'),(22,'15.7','balls'),(22,'15.8','bounce'),
              (23,'15.9','egg'),(23,'15.10','pulley'),(23,'15.11','torque-work'),
              (24,'15.12','percussion'),(24,'15.13','rod'),(24,'15.14','chimney')]
        }
        for page,old,label in figure_rows[unit.key]:
            objects.append({'source_kind':'fig','source_number':old,
               'physical_page':page,'printed_page':page+138,
               'source_pdf':'【2019暑】兴趣一阶.pdf','new_label':'ch09:fig:'+label,
               'status':'mapped','notes':'Unnumbered source model restored' if old is None else ''})
        parts.append(body); maps.append({'source':unit.key,'objects':objects})
    text=book.normalize_visible_eponyms('\n'.join(parts))
    assert text.count(r'\begin{origexamplebox}')==19
    assert text.count(r'\begin{xesolution}')==19
    assert text.count(r'\label{ch09:fig:')==29
    assert 'sollabel/.style={font=\\scriptsize,fill=white' not in text
    text=book.apply_chapter_layout(9,text)
    (book.GENERATED/'chapters/ch09.tex').write_text(text)
    mp=book.GENERATED/'source-map.json'; mapping=json.loads(mp.read_text())
    next(c for c in mapping['chapters'] if c['chapter']==9)['source_number_maps']=maps
    mp.write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
    (book.GENERATED/'wrappers/chapters/ch09.tex').write_text(book._wrapper(f"第9章　{spec['title']}",[9],toc=False))
    (book.GENERATED/'wrappers/volumes/volume2.tex').write_text(book._wrapper('第2卷　力学',list(range(5,14)),toc=True))
    dp=book.GENERATED/'deliverables.json'; data=json.loads(dp.read_text())
    for item in data['chapters']:
        if item['chapter']==9: item['output']=item['output'].replace('_含解答与解图.pdf','.pdf')
    dp.write_text(json.dumps(data,ensure_ascii=False,indent=2))
    assert all(sha(Path(p))==h for p,h in protected.items())
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'protected-chapters.json').write_text(json.dumps(protected,indent=2))
    print('Regenerated Chapter 9: 19 examples, 19 solutions, 29 numbered figures.')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--regenerate',action='store_true')
    parser.add_argument('--target',choices=['ch09','volume2','main'])
    parser.add_argument('--verify-two-passes',action='store_true')
    args=parser.parse_args()
    if args.regenerate: regenerate()
    if args.target:
        os.environ['TEXINPUTS']=str(book.BOOK)+'//:'+os.environ.get('TEXINPUTS','')
        target=args.target
        wrapper=(book.BOOK/'main.tex' if target=='main' else book.GENERATED/'wrappers/volumes/volume2.tex' if target=='volume2' else book.GENERATED/'wrappers/chapters/ch09.tex')
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
