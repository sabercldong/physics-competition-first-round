"""Private optics revision, immutable published baseline, no automatic release."""
import argparse,hashlib,json,re,shutil,os,subprocess,fcntl
from pathlib import Path
from collections import Counter
import fitz
import build_restructured as book

BASE=book.BOOK/'build/revision-optics-20260930'
ARCHIVE=book.PROJECT/'archive/20260930-optics-before-teaching-restructure'
FORMAL=book.PROJECT/'output/pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def names():
    return {**{f'ch{n}':f'高中物理竞赛一轮讲义_第{n}章_{book.CHAPTERS[n]["title"]}.pdf' for n in range(27,31)},'volume5':'高中物理竞赛一轮讲义_第5卷_光学.pdf','main':'高中物理竞赛一轮讲义.pdf'}
def backup():
    BASE.mkdir(parents=True,exist_ok=True)
    if (ARCHIVE/'manifest.json').exists():
        print('Existing immutable baseline retained.');return
    assert not ARCHIVE.exists(),'Inspect incomplete archive before resuming'
    (ARCHIVE/'pdf').mkdir(parents=True)
    for name in names().values():shutil.copy2(FORMAL/name,ARCHIVE/'pdf'/name)
    shutil.copytree(book.BOOK,ARCHIVE/'source',ignore=shutil.ignore_patterns('build','__pycache__','.git'))
    for folder in ['forty-second-section','forty-third-section','forty-fourth-section','forty-fifth-section']:
        shutil.copytree(book.LEGACY/folder,ARCHIVE/'legacy'/folder,ignore=shutil.ignore_patterns('build','__pycache__','.git'))
    save(ARCHIVE/'manifest.json',{'formal':{p.name:{'sha256':sha(p),'pages':len(fitz.open(p))} for p in FORMAL.glob('*.pdf')},'generated':{str(p.relative_to(book.BOOK)):sha(p) for p in (book.GENERATED/'chapters').glob('*.tex')},'main':sha(book.BOOK/'main.tex'),'style':sha(book.BOOK/'style.tex')})
    print('Archived four chapters, volume, main and their source baselines.')
def inventory():
    rows={}
    for n in range(27,31):
        s=(ARCHIVE/f'source/generated/chapters/ch{n}.tex').read_text()
        row={'sections':re.findall(r'\\section\{([^}\n]+)\}',s),'examples':[],'figure_labels':re.findall(r'\\label\{(ch\d+:fig:[^}]+)\}',s)}
        for i,x in enumerate(re.finditer(r'\\begin\{origexamplebox\}(.*?)\\end\{xesolution\}',s,re.S),1):
            labels=re.findall(r'\\label\{([^}]+)\}',x[0]);row['examples'].append({'old_number':f'{n}.{i}','labels':labels,'sha256':hashlib.sha256(x[0].encode()).hexdigest()})
        row['solution_count']=s.count(r'\begin{xesolution}');row['tikz_count']=s.count(r'\begin{tikzpicture}')
        assert len(row['examples'])==row['solution_count']
        rows[str(n)]=row
    save(BASE/'baseline-inventory.json',rows)
    print({k:{'examples':len(v['examples']),'sections':len(v['sections']),'tikz':v['tikz_count']} for k,v in rows.items()})
def stage():
    from optics_teaching_layout import reviewed_presentation,refine,correct,CORRECTIONS
    from optics_solution_review import strip_additions,INSERTIONS
    from optics_figure_completion import undo as undo_figures,CHANGES
    staged=BASE/'staged';staged.mkdir(exist_ok=True);evidence={}
    for n in range(27,31):
        # Assemble raw source independently of the public layout hook so a
        # later normal rebuild cannot accidentally apply optics refinement twice.
        spec=book.CHAPTERS[n];parts=[f'\\chapter{{{spec["title"]}}}\n']
        for unit in spec['legacy']:
            body,_=book.extract_legacy(unit,n);parts.append(body)
        for name in spec['new']:
            p=book.BOOK/'chapters/new'/name
            parts.append(book._qualify_existing_labels(book.flatten_inputs(p.read_text(),p.parent,set()),n))
        raw=book.normalize_visible_eponyms('\n'.join(parts))
        old=(ARCHIVE/f'source/generated/chapters/ch{n}.tex').read_text()
        assert reviewed_presentation(n,raw)==old,('Baseline changed',n)
        new=refine(n,raw)
        retained=strip_additions(undo_figures(n,new))
        corrected_old=correct(n,old)
        for env in ['origexamplebox','xesolution','tikzpicture']:
            pattern=r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}'
            a=Counter(re.findall(pattern,corrected_old,re.S));b=Counter(re.findall(pattern,retained,re.S))
            assert not a-b,(n,env,'missing original object')
        def prose_lines(value):
            value=re.sub(r'\\Needspace\{\d+\\baselineskip\}',lambda _:r'\Needspace{N\baselineskip}',value)
            return Counter(x.strip() for x in value.splitlines() if x.strip() and not x.strip().startswith(r'\section{') and x.strip() not in ['{','}'])
        oldlines=prose_lines(corrected_old);newlines=prose_lines(retained)
        assert not oldlines-newlines,(n,oldlines-newlines)
        (staged/f'ch{n}-body.tex').write_text(new)
        wrapper=book._wrapper(f'第{n}章　{book.CHAPTERS[n]["title"]}',[n],toc=False)
        (staged/f'ch{n}.tex').write_text(wrapper.replace(f'generated/chapters/ch{n}.tex',str(staged/f'ch{n}-body.tex')))
        evidence[n]={'old_examples':old.count(r'\begin{origexamplebox}'),'new_examples':new.count(r'\begin{origexamplebox}'),'original_prose_lines_retained_except_documented_corrections':True,'corrections':CORRECTIONS.get(n,[]),'original_question_solution_diagram_blocks_retained':True}
        evidence[n]['solution_additions']=[{'label':x[0],'addition_id':x[3]} for x in INSERTIONS.get(n,[])]
        evidence[n]['figure_transformations']=CHANGES.get(n,[])
        evidence[n]['retention_method']='Remove only reversible named additions; compare complete original blocks after explicitly listed corrections.'
    save(BASE/'retention.json',evidence)
    for key,path in [('volume5',book.GENERATED/'wrappers/volumes/volume5.tex'),('main',book.BOOK/'main.tex')]:
        text=path.read_text()
        for n in range(27,31):text=text.replace(f'generated/chapters/ch{n}.tex',str(staged/f'ch{n}-body.tex'))
        (staged/f'{key}.tex').write_text(text)
    print('Private staged bodies generated with retention assertions.')
def build(key):
    out=BASE/key;out.mkdir(exist_ok=True);wrapper=BASE/f'staged/{key}.tex'
    lock=(out/'build.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    inputs={str(p):sha(p) for p in (BASE/'staged').glob('*.tex')}
    inputs[str(book.BOOK/'style.tex')]=sha(book.BOOK/'style.tex')
    env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','');env['TEXFONTMAPS']=str(book.BOOK)+':'+env.get('TEXFONTMAPS','')
    for i in range(1,4):
        with (out/f'pass-{i}.txt').open('w') as f:
            subprocess.run(['/Library/TeX/texbin/xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={out}',str(wrapper)],cwd=book.BOOK,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    subprocess.run(['/Library/TeX/texbin/xdvipdfmx','-q','-o',str(out/f'{key}.pdf'),str(out/f'{key}.xdv')],cwd=book.BOOK,env=env,check=True)
    assert all(sha(Path(p))==h for p,h in inputs.items()),'Inputs changed during build'
    save(out/'build-evidence.json',{'inputs':inputs,'passes':3,'pdf_sha256':sha(out/f'{key}.pdf'),'pages':len(fitz.open(out/f'{key}.pdf'))})
    print(key,len(fitz.open(out/f'{key}.pdf')),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backup',action='store_true');p.add_argument('--inventory',action='store_true');p.add_argument('--stage',action='store_true');p.add_argument('--target');a=p.parse_args()
    if a.backup:backup()
    if a.inventory:inventory()
    if a.stage:stage()
    if a.target:build(a.target)
