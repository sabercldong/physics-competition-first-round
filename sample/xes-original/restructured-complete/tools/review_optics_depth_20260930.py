"""Render private review artifacts and record checks without publishing PDFs."""
import argparse,json,re,hashlib,subprocess,os
from pathlib import Path
from PIL import Image,ImageDraw
import fitz
from revise_optics_20260930 import BASE,book,save,sha

def render(n):
    pdf=BASE/f'ch{n}/ch{n}.pdf';d=fitz.open(pdf);out=BASE/f'render/ch{n}';out.mkdir(parents=True,exist_ok=True)
    for i,p in enumerate(d):p.get_pixmap(dpi=130).save(out/f'p{i+1:03}.png')
    for start in range(0,len(d),8):
        sheet=Image.new('RGB',(1600,1180),'#ddd');draw=ImageDraw.Draw(sheet)
        for j,i in enumerate(range(start,min(start+8,len(d)))):
            im=Image.open(out/f'p{i+1:03}.png');im.thumbnail((390,550));x=j%4*400;y=j//4*590
            sheet.paste(im,(x,y+25));draw.text((x+5,y+5),f'ch{n} PDF p{i+1}',fill='black')
        sheet.save(out/f'overview-{start+1:03}.jpg',quality=92)
    terms={28:'图取',29:'均匀非相干线光源',30:'蓝线为电矢量'}
    if n in terms:
        for i,p in enumerate(d):
            if terms[n] in p.get_text():
                p.get_pixmap(dpi=240).save(out/f'new-figure-p{i+1:03}.png')
    print(n,len(d),flush=True)

def audit():
    rows={}
    for n in range(27,31):
        p=BASE/f'ch{n}/ch{n}.pdf';d=fitz.open(p);log=(p.parent/f'ch{n}.log').read_text(errors='replace')
        text=(BASE/f'staged/ch{n}-body.tex').read_text()
        labels=re.findall(r'\\label\{([^}]+)\}',text)
        refs=re.findall(r'\\(?:eqref|ref|autoref)\{([^}]+)\}',text)
        qpdf=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
        rows[n]={'pages':len(d),'sha256':sha(p),'examples':text.count(r'\begin{origexamplebox}'),'solutions':text.count(r'\begin{xesolution}'),
          'duplicate_labels':[x for x in set(labels) if labels.count(x)>1],
          'unresolved_local_refs':[x for x in set(refs)-set(labels) if x.startswith(f'ch{n}:')],
          'log_findings':re.findall(r'^.*(?:Overfull|Underfull|undefined|Missing character|multiply defined|^!).*$',log,re.M),
          'qpdf_exit':qpdf.returncode,'text_characters':sum(len(p.get_text()) for p in d),
          'visual_review_status':'not_complete','source_object_review_status':'not_complete'}
    save(BASE/'mechanical-checks.json',rows);print(json.dumps(rows,ensure_ascii=False,indent=2))

def new_figures():
    out=BASE/'new-figure-review';out.mkdir(exist_ok=True)
    checker=Path('/Users/dongxingxi/.codex/skills/thesis-figure-skill/references/pdf-overlap-checker.py')
    specs=[(28,'图取',150,455,181.5,5.5),(29,'均匀非相干线光源',175,460,121,1),(30,'蓝线为电矢量',130,470,145,10)]
    for n,term,x0,x1,above,gap in specs:
        src=fitz.open(BASE/f'ch{n}/ch{n}.pdf')
        hits=[(i,b) for i,p in enumerate(src) for b in p.get_text('blocks') if term in b[4] and b[4].startswith('图')]
        assert len(hits)==1,(n,hits)
        index,block=hits[0];pno=index+1;rect=fitz.Rect(x0,block[1]-above,x1,block[1]-gap)
        doc=fitz.open();p=doc.new_page(width=rect.width,height=rect.height)
        p.show_pdf_page(p.rect,src,pno-1,clip=rect)
        pdf=out/f'ch{n}-new-figure.pdf';doc.save(pdf)
        p.get_pixmap(dpi=300).save(out/f'ch{n}-new-figure.png')
        # A clipped Form XObject retains off-clip page text that pdfplumber
        # mistakenly reports. Recompile the exact TikZ block alone for checking;
        # the user-visible PNG above still comes from the actual chapter page.
        source=(book.BOOK/f'chapters/new/optics-depth/ch{n}.tex').read_text()
        drawings=re.findall(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',source,re.S)
        assert len(drawings)==1
        tex=out/f'ch{n}-diagram-only.tex'
        tex.write_text(r'\documentclass[UTF8,zihao=-4]{ctexbook}'+'\n'+r'\input{style.tex}\pagestyle{empty}\begin{document}\begin{center}'+'\n'+drawings[0]+'\n'+r'\end{center}\end{document}')
        env=os.environ.copy();env['TEXINPUTS']=str(book.BOOK)+'//:'+env.get('TEXINPUTS','')
        for passno in (1,2):
            with (out/f'ch{n}-diagram-only-pass{passno}.txt').open('w') as log:
                subprocess.run(['/Library/TeX/texbin/xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={out}',str(tex)],cwd=book.BOOK,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        checked=out/f'ch{n}-diagram-only.pdf'
        run=subprocess.run([str(BASE/'checker-venv/bin/python'),str(checker),str(checked),'--json'],capture_output=True,text=True)
        result=run.stdout[run.stdout.find('{'):]
        json.loads(result)
        (out/f'ch{n}-overlap.json').write_text(result)
        save(out/f'ch{n}-evidence.json',{'source_pdf_sha256':sha(BASE/f'ch{n}/ch{n}.pdf'),'page':pno,'clip':list(rect),'png_sha256':sha(out/f'ch{n}-new-figure.png'),'checker_exit':run.returncode,'checker_stderr':run.stderr})
        print(n,run.returncode,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--chapter',type=int);p.add_argument('--audit',action='store_true');p.add_argument('--new-figures',action='store_true');a=p.parse_args()
    if a.chapter:render(a.chapter)
    if a.audit:audit()
    if a.new_figures:new_figures()
