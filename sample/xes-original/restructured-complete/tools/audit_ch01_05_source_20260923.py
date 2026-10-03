"""Read-only PDF/source inventory for the chapter 1--5 review; not a release gate."""
from pathlib import Path
import hashlib,json,re,subprocess
import fitz

BOOK=Path(__file__).resolve().parents[1]
ROOT=BOOK.parents[2]
OUT=BOOK/'build/audit-ch01-05-20260923'
SOURCES=Path('/Users/dongxingxi/Downloads/学而思资料/一轮')

def inventory():
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    files=[(f'ch{n:02}',next((ROOT/'output/pdf').glob(f'*第{n:02}章_*.pdf'))) for n in range(1,6)]
    files += [('source-kinematics',SOURCES/'资料.pdf'),('source-math',SOURCES/'19春假兴趣2-微积分在物理学中的应用.pdf'),('source-statics',SOURCES/'19春假兴趣1-力学.pdf')]
    for key,path in files:
        doc=fitz.open(path)
        pages=[]
        for n,page in enumerate(doc,1):
            text=page.get_text(sort=True)
            pages.append(f'\n===== PHYSICAL PAGE {n} =====\n{text}')
        (OUT/f'{key}.txt').write_text(''.join(pages))
        records.append({'key':key,'path':str(path),'pages':len(doc),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bookmarks':len(doc.get_toc())})
    (OUT/'inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(json.dumps(records,ensure_ascii=False,indent=2))

def questions():
    rows=[]
    for ch in range(1,6):
        tex=(BOOK/f'generated/chapters/ch{ch:02}.tex').read_text()
        starts=list(re.finditer(r'\\begin\{origexamplebox\}',tex))
        for i,start in enumerate(starts):
            end=tex.index(r'\end{origexamplebox}',start.end())
            q=tex[start.end():end]
            after=tex[end:starts[i+1].start() if i+1<len(starts) else len(tex)]
            solutions=re.findall(r'\\begin\{xesolution\}([\s\S]*?)\\end\{xesolution\}',after)
            assert len(solutions)==1,(ch,i+1,len(solutions))
            label=re.search(r'\\label\{(ch\d+:ex:[^}]+)\}',q)
            source=re.search(r'-(\d+)-(\d+)$',label[1]) if label else None
            s=solutions[0]
            rows.append({'example':f'{ch}.{i+1}',
                'label':label[1] if label else None,
                'source_number':f'{source[1]}.{source[2]}' if source else None,
                'question_tex':q,'solution_tex':s,
                'solution_chinese_characters':len(re.findall('[\u4e00-\u9fff]',s)),
                'question_diagram_calls':re.findall(r'\\[A-Za-z]*(?:Diagram|Graphs)\b|\\begin\{tikzpicture\}|\\sourcefigure',q),
                'solution_diagram_calls':re.findall(r'\\[A-Za-z]*(?:Diagram|Graphs)\b|\\begin\{tikzpicture\}|\\sourcefigure',s),
                'note':'Presence inventory only; counts and answer length do not establish completeness or correctness.'})
    (OUT/'question-inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print({ch:sum(r['example'].startswith(f'{ch}.') for r in rows) for ch in range(1,6)})

def structure():
    results=[]
    for item in json.loads((OUT/'inventory.json').read_text())[:5]:
        p=item['path']
        q=subprocess.run(['qpdf','--check',p],capture_output=True,text=True)
        f=subprocess.run(['pdffonts',p],capture_output=True,text=True)
        results.append({'key':item['key'],'sha256':item['sha256'],'qpdf_returncode':q.returncode,
            'qpdf_output':q.stdout+q.stderr,'font_output':f.stdout+f.stderr})
    (OUT/'structural-checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print([(x['key'],x['qpdf_returncode']) for x in results])

def render_review():
    from PIL import Image,ImageDraw
    dest=OUT/'visual'
    dest.mkdir(exist_ok=True)
    for item in json.loads((OUT/'inventory.json').read_text())[:5]:
        doc=fitz.open(item['path'])
        for start in range(0,len(doc),9):
            sheet=Image.new('RGB',(1050,1575),'#dddddd')
            draw=ImageDraw.Draw(sheet)
            for i in range(start,min(start+9,len(doc))):
                pix=doc[i].get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False)
                im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
                im.thumbnail((340,495))
                x=((i-start)%3)*350+5;y=((i-start)//3)*525+25
                sheet.paste(im,(x,y))
                draw.text((x,y-19),f"{item['key']} physical {i+1}",fill='black')
            sheet.save(dest/f"{item['key']}-overview-{start+1:02}.jpg")
        selections={'ch01':[21], 'ch02':[6,7,10,11,12], 'ch03':[42], 'ch04':[20,21], 'ch05':[14,15,16]}
        for n in selections[item['key']]:
            doc[n-1].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(dest/f"{item['key']}-page-{n:02}.png")
    print(str(dest))

def findings():
    report=BOOK/'audit/第1—5章原题图与解答专项检查_20260923.md'
    body=report.read_text()
    entries=[]
    for match in re.finditer(r'^### (F\d+)｜([^：\n]+)：([^\n]+)',body,re.M):
        entries.append({'id':match[1],'priority':match[2],'title':match[3],
            'status':'open','source':'2026-09-23 read-only review',
            'report_line':body[:match.start()].count('\n')+1})
    snapshot=json.loads((OUT/'inventory.json').read_text())
    current=[]
    for item in snapshot[:5]:
        actual=hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()
        current.append({'key':item['key'],'path':item['path'],'unchanged':actual==item['sha256'],'sha256':actual})
    assert all(x['unchanged'] for x in current),'An audited formal PDF changed during review'
    result={'date':'2026-09-23','mode':'read-only','acceptance_passed':False,
        'teaching_content_modified':False,'formal_pdf_modified':False,
        'report':str(report),'formal_pdf_check':current,'source_snapshot':snapshot[5:],
        'findings':entries,'limit':'Presence counts, thumbnail screening and structural checks are not a proof of complete semantic or pixel-level correctness.'}
    path=BOOK/'audit/source-review/ch01-ch05-problem-figure-findings-20260923.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print({'findings':len(entries),'formal_pdfs_unchanged':True,'path':str(path)})

if __name__=='__main__':
    import sys
    if '--questions' in sys.argv:questions()
    elif '--structure' in sys.argv:structure()
    elif '--render-review' in sys.argv:render_review()
    elif '--findings' in sys.argv:findings()
    else:inventory()
