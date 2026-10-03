"""Final optics-only evidence. Never promotes files and never edits other volumes."""
import argparse,inspect,json,math,re,subprocess,os
from pathlib import Path
import fitz
from PIL import Image,ImageDraw,ImageChops
from revise_optics_20260930 import BASE,book,sha,save

def render(number):
    pdf=BASE/f'ch{number}/ch{number}.pdf';doc=fitz.open(pdf)
    out=BASE/f'final-render/ch{number}';out.mkdir(parents=True,exist_ok=True)
    for i,page in enumerate(doc):
        page.get_pixmap(dpi=300,alpha=False).save(out/f'p{i+1:03}.png')
    for start in range(0,len(doc),8):
        sheet=Image.new('RGB',(1600,1180),'#ddd');draw=ImageDraw.Draw(sheet)
        for j,i in enumerate(range(start,min(start+8,len(doc)))):
            im=Image.open(out/f'p{i+1:03}.png');im.thumbnail((390,550))
            x=j%4*400;y=j//4*590;sheet.paste(im,(x,y+25))
            draw.text((x+5,y+5),f'ch{number} PDF p{i+1}',fill='black')
        sheet.save(out/f'overview-{start+1:03}.jpg',quality=92)
    save(out/'evidence.json',{'pdf_sha256':sha(pdf),'pages':len(doc),'dpi':300,
      'rendered_pages':[sha(out/f'p{i+1:03}.png') for i in range(len(doc))]})
    print('rendered',number,len(doc),flush=True)

def crop_proofs():
    # Inspection derivatives only; delivery PDFs and figure source stay intact.
    out=BASE/'final-figure-checks'
    for p in out.glob('[0-9][0-9]-*.png'):
        im=Image.open(p).convert('RGB')
        box=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
        if box:
            x0,y0,x1,y1=box
            im.crop((max(0,x0-35),max(0,y0-35),min(im.width,x1+35),min(im.height,y1+35))).save(p.with_suffix('.jpg'),quality=95)

def physics():
    # Rerun old independent analytic tests, excluding their historical geometry
    # JSON and publication checks: neither is evidence for this new layout.
    import check_revision_ch27_ch28 as old
    source=inspect.getsource(old.physics)
    source=source[:source.index(' geom=')]+' return tests\n'
    exec(source,old.__dict__)
    result={'inherited_analytic_tests_rerun':old.physics()}
    f=1.2;cases=[]
    for u in (math.inf,3.6,2.4,1.8,1.2,.9,.55):
        residual=[];intercepts=[]
        for y in (-.32,-.16,.16,.32):
            incoming=0 if math.isinf(u) else y/u
            outgoing=incoming-y/f
            if u==f:
                assert abs(outgoing)<1e-12
            else:
                v=-y/outgoing
                expected=f if math.isinf(u) else f*u/(u-f)
                residual.append(abs(v-expected));intercepts.append(v)
                assert abs(v-expected)<1e-12
        cases.append({'u_over_f':None if math.isinf(u) else u/f,
          'v_over_f':None if u==f else intercepts[0]/f,'max_residual':max(residual,default=0)})
    result['seven_lens_bundles_independent_intercepts']=cases
    src=(BASE/'staged/ch30-body.tex').read_text()
    macro=src[src.index(r'\newcommand{\ObliqueGratingDiagram}'):src.index('衍射是光的波动性')]
    assert r'{-.75,0,.75,1.5,2.25}' not in macro
    assert '(0,-1.15)--(0,-.08) (0,.08)--(0,1.42) (0,1.58)--(0,2.65)' in macro
    opaque=[(-1.15,-.08),(.08,1.42),(1.58,2.65)]
    assert all(any(a<y<b for a,b in opaque) for y in (.3,.75,1.2))
    assert all(not any(a<y<b for a,b in opaque) for y in (0,1.5))
    result['grating_A_B_adjacent_slits']=True
    result['source_hashes']={str(p):sha(p) for p in (BASE/'staged').glob('ch*-body.tex')}
    save(BASE/'final-physics-checks.json',result)
    print('final physics checks passed')

def diagram_checks():
    refs=Path('/Users/dongxingxi/.codex/skills/thesis-figure-skill/references')
    out=BASE/'final-figure-checks';out.mkdir(exist_ok=True)
    rows={}
    for name in ('lens-seven-states','coherence-contrast'):
        tex=book.BOOK/f'chapters/new/optics-depth/{name}.tex'
        rows[name]={}
        for tool,args in [('tikz-validator.py',[]),('tikz-design-linter.py',['--type','simple','--json'])]:
            r=subprocess.run(['/opt/homebrew/bin/python3',str(refs/tool),str(tex),*args],capture_output=True,text=True)
            (out/f'{name}-{tool}.txt').write_text(r.stdout+r.stderr)
            rows[name][tool]={'exit':r.returncode,'output':r.stdout+r.stderr}
    save(out/'linter-results.json',rows)
    print(json.dumps(rows,ensure_ascii=False,indent=2))

def figures():
    """Compile the exact changed vector figures alone for bbox triage."""
    out=BASE/'final-figure-checks';out.mkdir(exist_ok=True)
    specs={27:['AbsorbingShellDiagram','GradientCircleDiagram','FisherBayDiagram','ParallelPlateDiagram'],
      28:['AplanaticLensPanel','CatEyePanel','SilveredLensPanel','PrismTrainPanel','SelfConjugateDiagram'],
      29:['MovingSourceDiagram','FiniteLloydDiagram'],30:['ObliqueGratingDiagram']}
    def definition(s,name):
        at=s.index('\\newcommand{\\'+name+'}')
        body=at+len('\\newcommand{\\'+name+'}')
        if s[body]=='[':body=s.index(']',body)+1
        _,end=book.balanced_argument(s,body)
        return s[at:end]
    pages=[]
    for n,macros in specs.items():
        s=(BASE/f'staged/ch{n}-body.tex').read_text()
        for name in macros:pages.append((name,definition(s,name)+'\n\\'+name))
    s=(book.BOOK/'chapters/new/optics-depth/lens-seven-states.tex').read_text()
    for j,drawing in enumerate(re.findall(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',s,re.S)):
        pages.append((f'lens-states-{j+1}',definition(s,'LensStateRow')+'\n'+drawing))
    s=(book.BOOK/'chapters/new/optics-depth/coherence-contrast.tex').read_text()
    pages.append(('coherence-contrast',re.search(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',s,re.S)[0]))
    s=(BASE/'staged/ch30-body.tex').read_text();label=s.index(r'\label{ch30:fig:nacl}')
    start=s.rfind(r'\begin{tikzpicture}',0,label);end=s.index(r'\end{tikzpicture}',start)+len(r'\end{tikzpicture}')
    pages.append(('crystal-planes',s[start:end]))
    text=r'\documentclass[UTF8,zihao=-4,oneside]{ctexbook}'+'\n'+r'\input{style.tex}\pagestyle{empty}\begin{document}'+'\n'
    text+='\n\\clearpage\n'.join('\\begingroup\n'+drawing+'\n\\endgroup' for name,drawing in pages)
    text+='\n\\end{document}\n';tex=out/'changed-diagrams.tex';tex.write_text(text)
    env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','')
    for i in (1,2):
        with (out/f'proof-pass{i}.txt').open('w') as log:
            subprocess.run(['/Library/TeX/texbin/xelatex','-no-pdf','-interaction=nonstopmode','-halt-on-error',f'-output-directory={out}',str(tex)],cwd=book.BOOK,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    pdf=out/'changed-diagrams.pdf'
    subprocess.run(['/Library/TeX/texbin/xdvipdfmx','-q','-o',str(pdf),str(tex.with_suffix('.xdv'))],check=True,cwd=book.BOOK,env=env)
    doc=fitz.open(pdf);assert len(doc)==len(pages)
    for i,(name,_) in enumerate(pages):doc[i].get_pixmap(dpi=300).save(out/f'{i+1:02}-{name}.png')
    checker=Path('/Users/dongxingxi/.codex/skills/thesis-figure-skill/references/pdf-overlap-checker.py')
    # The checker reads only page 0. Check one-page PDFs, never mistake a
    # multi-page invocation for sixteen independent diagram inspections.
    checks={}
    for i,(name,_) in enumerate(pages):
        single=fitz.open();single.insert_pdf(doc,from_page=i,to_page=i)
        one=out/f'{i+1:02}-{name}.pdf';single.save(one);single.close()
        result=subprocess.run([str(BASE/'checker-venv/bin/python'),str(checker),str(one),'--json'],capture_output=True,text=True)
        checks[name]={'exit':result.returncode,'report':json.loads(result.stdout[result.stdout.index('{'):])}
    save(out/'overlap.json',checks)
    save(out/'proof-manifest.json',{'pdf_sha256':sha(pdf),'pages':[{'page':i+1,'name':name} for i,(name,_) in enumerate(pages)],'checked_pages':len(checks)})
    crop_proofs()
    print('changed diagram proof and individually checked pages',len(checks))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render',type=int);p.add_argument('--physics',action='store_true');p.add_argument('--diagram-checks',action='store_true');p.add_argument('--figures',action='store_true');a=p.parse_args()
    if a.render:render(a.render)
    if a.physics:physics()
    if a.diagram_checks:diagram_checks()
    if a.figures:figures()
