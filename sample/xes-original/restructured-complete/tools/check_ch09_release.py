#!/usr/bin/env python3
"""Read-only checks of the chapter-nine candidate PDFs before publication."""
from pathlib import Path
import hashlib, json, re, subprocess
import fitz

BOOK=Path(__file__).resolve().parent.parent
BASE=BOOK/'build/review-ch09-20260909'
ROOT=BOOK.parents[2]
title='角动量与刚体动力学'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def body(page):
    # Exclude running header/footer, retaining the full typeset text block.
    return re.sub(r'\s+', '', page.get_text(clip=fitz.Rect(42,51,552,780)))
def chapter_range(doc,name):
    toc=[row for row in doc.get_toc() if row[0]==1]
    i=next(i for i,r in enumerate(toc) if r[1]==name)
    return toc[i][2]-1, toc[i+1][2]-1 if i+1<len(toc) else len(doc)

result={'pdfs':{},'scope':'Chapter 9 revision and compilation regression; not a new content audit of all chapters.'}
docs={}
for key,stem in [('ch09','ch09'),('volume2','volume2'),('main','main')]:
    path=BASE/key/f'{stem}.pdf'
    doc=fitz.open(path);docs[key]=doc
    checks={}
    for tool,args in [('qpdf',['qpdf','--check',str(path)]),('fonts',['pdffonts',str(path)])]:
        r=subprocess.run(args,capture_output=True,text=True)
        (BASE/key/f'{tool}-check.txt').write_text(r.stdout+r.stderr)
        assert r.returncode==0,(key,tool,r.stderr)
        checks[tool]=True
        if tool=='fonts':
            rows=r.stdout.splitlines()[2:]
            assert rows and all(re.search(r'\byes\s+yes\s+yes\s+\d+\s+\d+\s*$',row) for row in rows),r.stdout
            checks['embedded_unicode_fonts']=len(rows)
    log=(BASE/key/f'{stem}.log').read_text(errors='replace')
    findings=[line for line in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined|multiply defined',line)]
    checks['log_findings']=findings
    # Preserve and report two independently confirmed mild spacing warnings
    # outside this chapter; do not change unrelated chapter 32 or A4 to hide them.
    if key=='main':
        old_log=(BOOK/'build/review-ch08-20260909/main/main.log').read_text(errors='replace')
        old_findings=[line for line in old_log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|undefined|multiply defined',line)]
        allowed=[r'Underfull \hbox (badness 1152) in paragraph at lines 311--313',
                 r'Underfull \hbox (badness 1253) in paragraph at lines 26--26']
        assert findings==old_findings==allowed,(findings,old_findings)
        checks['inherited_mild_spacing_warnings']={'ch32.tex:311':1152,'A4-electrostatics.tex:26':1253}
        checks['new_log_findings']=[]
    else:
        assert not findings,(key,findings[:15])
    assert all(1<=r[2]<=len(doc) for r in doc.get_toc())
    if key!='ch09':
        toc_text=(BASE/key/f'{stem}.toc').read_text()
        chapter_pages=[(int(ch),pg) for pg,ch in re.findall(r'\\contentsline \{chapter\}.*\{(\d+)\}\{chapter\.(\d+)\}',toc_text)]
        top=[r for r in doc.get_toc() if r[0]==1]
        expected=list(range(5,14)) if key=='volume2' else list(range(1,33))
        selected=[(ch,pg) for ch,pg in chapter_pages if ch in expected][:len(expected)]
        assert [ch for ch,pg in selected]==expected
        for (_,printed),entry in zip(selected,top):
            assert printed==doc[entry[2]-1].get_label(),(key,printed,entry)
        checks['numbered_chapter_toc_pages_matched']=len(selected)
    assert '\ufffd' not in ''.join(p.get_text() for p in doc)
    result['pdfs'][key]={'sha256':digest(path),'pages':len(doc),'bookmarks':len(doc.get_toc()),**checks}

unit=[body(p) for p in docs['ch09']][1:]
for key in ['volume2','main']:
    start,end=chapter_range(docs[key],title)
    actual=[body(docs[key][i]) for i in range(start,end)]
    assert actual==unit,(key,len(actual),len(unit),[i+1 for i,(a,b) in enumerate(zip(actual,unit)) if a!=b])
    result['pdfs'][key]['chapter9_physical_pages']=[start+1,end]
    result['pdfs'][key]['chapter9_body_matches_standalone']=True
    raster_differences=[]
    for j in range(end-start):
        pa=docs['ch09'][j+1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=fitz.Rect(42,51,552,780),alpha=False)
        pb=docs[key][start+j].get_pixmap(matrix=fitz.Matrix(1.5,1.5),clip=fitz.Rect(42,51,552,780),alpha=False)
        if pa.samples!=pb.samples:raster_differences.append(j+1)
    assert not raster_differences,(key,raster_differences)
    result['pdfs'][key]['chapter9_body_raster_matches_standalone']=True

# Compare every unchanged body page to the archived official master.
old=fitz.open(ROOT/'archive/2026-09-09-ch09-revision/pdf/高中物理竞赛一轮讲义.pdf')
old_start,old_end=chapter_range(old,title)
new_start,new_end=chapter_range(docs['main'],title)
first_body=next(r[2] for r in old.get_toc() if r[0]==1)-1
old_pages=list(range(first_body,old_start))+list(range(old_end,len(old)))
new_first_body=next(r[2] for r in docs['main'].get_toc() if r[0]==1)-1
new_pages=list(range(new_first_body,new_start))+list(range(new_end,len(docs['main'])))
assert len(old_pages)==len(new_pages)
diff=[]
for a,b in zip(old_pages,new_pages):
    if body(old[a])!=body(docs['main'][b]):
        diff.append({'old_page':a+1,'new_page':b+1})
result['unchanged_main_pages_compared']=len(old_pages)
result['unchanged_main_body_text_differences']=diff
assert not diff,diff[:20]
# Low-resolution raster equality is a regression test of unchanged pages,
# not a substitute for the high-resolution visual review of changed figures.
pixel_diff=[]
clip=fitz.Rect(42,51,552,780)
for a,b in zip(old_pages,new_pages):
    pa=old[a].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False)
    pb=docs['main'][b].get_pixmap(matrix=fitz.Matrix(1,1),clip=clip,alpha=False)
    if hashlib.sha256(pa.samples).digest()!=hashlib.sha256(pb.samples).digest():
        pixel_diff.append({'old_page':a+1,'new_page':b+1})
result['unchanged_main_body_raster_differences']=pixel_diff
assert not pixel_diff,pixel_diff[:20]
baseline=ROOT/'archive/2026-09-09-ch09-revision/source/generated/chapters'
others=[p for p in (BOOK/'generated/chapters').glob('ch*.tex') if p.stem!='ch09']
assert all(digest(p)==digest(baseline/p.name) for p in others)
result['other_chapter_sources_unchanged']=len(others)
result['source_sha256']=digest(BOOK/'generated/chapters/ch09.tex')
for key in docs:
    for n in (1,2):
        log=(BASE/key/f'verify-pass-{n}.txt').read_text(errors='replace')
        assert 'Output written' in log and 'Fatal error' not in log
result['recorded_frozen_source_xelatex_passes_per_pdf']=2
(BASE/'release-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
