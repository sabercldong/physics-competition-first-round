"""Evidence generation, not an automatic content/geometry approval."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import fitz
from PIL import Image, ImageDraw

BOOK=Path(__file__).resolve().parents[1]
BASE=BOOK/'build/revision-ch01-05-20260923'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def structural(targets):
    report=[]
    for target in targets:
        path=BASE/target/(target+'.pdf')
        doc=fitz.open(path)
        text='\n'.join(p.get_text() for p in doc)
        (BASE/target/'extracted.txt').write_text(text)
        log=(BASE/target/(target+'.log')).read_text(errors='replace')
        q=subprocess.run(['qpdf','--check',str(path)],capture_output=True,text=True)
        fonts=subprocess.run(['pdffonts',str(path)],capture_output=True,text=True)
        row=dict(target=target,pages=len(doc),sha256=sha(path),qpdf_code=q.returncode,
            qpdf_output=q.stdout+q.stderr,fonts=fonts.stdout,
            warnings=re.findall(r'(?m)^.*(?:Overfull|Underfull|Missing character|undefined|multiply defined).*(?:\n.*)?',log),
            replacement_characters=text.count('\ufffd'),bookmarks=doc.get_toc(),
            text_per_page=[len(p.get_text()) for p in doc])
        report.append(row)
    (BASE/'structural-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print([(r['target'],r['pages'],r['qpdf_code'],len(r['warnings'])) for r in report])

def render(targets):
    dest=BASE/'visual';dest.mkdir(exist_ok=True)
    index=[]
    for target in targets:
        pdf=BASE/target/(target+'.pdf');doc=fitz.open(pdf)
        for i,page in enumerate(doc,1):
            page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(dest/f'{target}-p{i:03}.png')
            index.append(dict(target=target,page=i,text=page.get_text(),image=str(dest/f'{target}-p{i:03}.png')))
        for start in range(0,len(doc),8):
            sheet=Image.new('RGB',(1400,2050),'#dddddd');draw=ImageDraw.Draw(sheet)
            for i in range(start,min(start+8,len(doc))):
                pix=doc[i].get_pixmap(matrix=fitz.Matrix(.8,.8),alpha=False)
                im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((340,965))
                x=(i-start)%4*350+5;y=(i-start)//4*1025+25
                # Taller source pages fit naturally; avoid enlarging tiny previews.
                im.thumbnail((340,970));sheet.paste(im,(x,y));draw.text((x,y-20),f'{target} physical {i+1}',fill='black')
            sheet=sheet.crop((0,0,1400,1050)) if len(doc)-start<=4 else sheet
            # Typical A4 thumbnails need only ~490 px height per row.
            compact=Image.new('RGB',(1400,1050),'#dddddd')
            compact.paste(sheet.crop((0,0,1400,520)),(0,0))
            compact.paste(sheet.crop((0,1025,1400,1545)),(0,525))
            compact.save(dest/f'{target}-overview-{start+1:03}.jpg',quality=92)
    (BASE/'page-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
    print('Rendered',len(index),'pages at 144 dpi; higher-resolution crops available from PDFs.')

def sources():
    mapping=json.loads((BOOK.parent/'kinematics-supplement/data/question-figure-map.json').read_text())
    rows=[]
    for ch,expected in [(1,36),(2,21),(3,51),(4,32),(5,31)]:
        p=BOOK/f'generated/chapters/ch{ch:02}.tex';text=p.read_text()
        questions=re.findall(r'\\begin\{origexamplebox\}.*?\\end\{origexamplebox\}',text,re.S)
        solutions=re.findall(r'\\begin\{xesolution\}.*?\\end\{xesolution\}',text,re.S)
        assert len(questions)==len(solutions)==expected,(ch,len(questions),len(solutions))
        matched=[]
        for row in mapping:
            calls=[q for q in questions if '\\'+row['macro'] in q]
            if calls:
                assert len(calls)==1
                matched.append(row['source_example'])
        rows.append(dict(chapter=ch,source_sha256=sha(p),examples=len(questions),solutions=len(solutions),source_question_figures=matched))
    assert sum(len(r['source_question_figures']) for r in rows)==58
    (BASE/'source-correspondence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print('171 questions, 171 solutions, 58 source question-figure groups in question environments.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--structure',action='store_true');p.add_argument('--sources',action='store_true');p.add_argument('--targets',nargs='+',default=[f'ch{n:02}' for n in range(1,6)])
    a=p.parse_args()
    if a.sources:sources()
    if a.structure:structural(a.targets)
    if a.render:render(a.targets)
