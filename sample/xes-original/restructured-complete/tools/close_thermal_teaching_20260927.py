"""Thermal-only regression and guarded publication; protects concurrent work."""
import argparse,json,re,shutil,os
from pathlib import Path
from datetime import datetime
import fitz
import enrich_thermal_20260927 as m

def save(name,value):
    (m.BASE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))
def body(p):
    return re.sub(r'\s+','',p.get_text(clip=fitz.Rect(0,65,p.rect.width,p.rect.height-55)))
def pixels(p):
    return p.get_pixmap(dpi=90,clip=fitz.Rect(0,65,p.rect.width,p.rect.height-55),alpha=False).samples

def volume_regression():
    v=fitz.open(m.BASE/'volume3/volume3.pdf');toc=v.get_toc();rows=[]
    for n in range(14,19):
        k=f'ch{n}';d=fitz.open(m.BASE/k/f'{k}.pdf')
        start=next(x[2] for x in toc if x[0]==1 and x[1]==m.book.CHAPTERS[n]['title'])
        for i in range(1,len(d)):
            assert body(d[i])==body(v[start+i-2]),(k,i,'text')
            assert pixels(d[i])==pixels(v[start+i-2]),(k,i,'raster')
        rows.append({'chapter':n,'body_pages':len(d)-1,'text_and_raster_equal':True})
    save('volume-regression.json',{'chapters':rows,'pdf_hashes':{k:m.sha(m.BASE/k/f'{k}.pdf') for k in m.names() if k!='main'}})
    print('Thermal volume body regression passed.',flush=True)

def regression():
    old=fitz.open(m.ARCHIVE/'latest-shared-before-publication/main.pdf')
    new=fitz.open(m.BASE/'main/main.pdf')
    a=[x for x in old.get_toc() if x[0]==1];b=[x for x in new.get_toc() if x[0]==1]
    assert [x[1] for x in a]==[x[1] for x in b]
    changed={m.book.CHAPTERS[n]['title'] for n in range(14,19)};protected=[]
    for i,(x,y) in enumerate(zip(a,b)):
        if x[1] in changed:continue
        ap=range(x[2]-1,a[i+1][2]-1 if i+1<len(a) else len(old))
        bp=range(y[2]-1,b[i+1][2]-1 if i+1<len(b) else len(new))
        assert len(ap)==len(bp),(x,y)
        for p,q in zip(ap,bp):
            assert body(old[p])==body(new[q]),(x[1],p,q,'text')
            assert pixels(old[p])==pixels(new[q]),(x[1],p,q,'raster')
        protected.append({'title':x[1],'pages':len(ap),'text_and_raster_equal':True})
    rows=[]
    for n in range(14,19):
        k=f'ch{n}';d=fitz.open(m.BASE/k/f'{k}.pdf')
        start=next(x[2] for x in b if x[1]==m.book.CHAPTERS[n]['title'])
        for i in range(1,len(d)):
            assert body(d[i])==body(new[start+i-2]),(k,i,'text')
            assert pixels(d[i])==pixels(new[start+i-2]),(k,i,'raster')
        rows.append({'chapter':n,'body_pages':len(d)-1,'text_and_raster_equal':True})
    save('regression.json',{'protected_units':protected,'thermal':rows,'pdf_hashes':{k:m.sha(m.BASE/k/f'{k}.pdf') for k in m.names()}})
    print('Main regression passed:',len(protected),'protected units.',flush=True)

def publish():
    baseline=json.loads((m.BASE/'publication-baseline.json').read_text())
    checks=json.loads((m.BASE/'structure.json').read_text())
    visual=json.loads((m.BASE/'visual-reviewed.json').read_text())
    reg=json.loads((m.BASE/'regression.json').read_text())
    vol=json.loads((m.BASE/'volume-regression.json').read_text())
    for p,h in json.loads((m.BASE/'frozen-shared.json').read_text()).items():
        assert m.sha(Path(p))==h,('shared source changed',p)
    for name,h in baseline.items():
        assert m.sha(m.common.FORMAL/name)==h,('formal changed',name)
    for k,name in m.names().items():
        h=m.sha(m.BASE/k/f'{k}.pdf')
        assert h==checks[k]['sha256']==visual['pdf_hashes'][k]==reg['pdf_hashes'][k]
        if k!='main':assert h==vol['pdf_hashes'][k]
        assert checks[k]['qpdf_returncode']==0 and not checks[k]['errors']
        for line in checks[k]['font_report'].splitlines()[2:]:
            assert line.split()[-5]=='yes',('font not embedded',k,line)
        for p,h0 in json.loads((m.BASE/k/'build-inputs.json').read_text()).items():
            assert m.sha(Path(p))==h0,('staged source changed',k,p)
    assert visual['all_thermal_pages_overview_reviewed'] and visual['new_teaching_pages_reviewed']
    for n in range(14,19):
        text,_=m.common.chapter_text(n)
        assert text==(m.BASE/f'staged/ch{n}-body.tex').read_text(),('maintenance changed',n)
    for n in range(14,19):
        shutil.copy2(m.BASE/f'staged/ch{n}-body.tex',m.book.GENERATED/f'chapters/ch{n}.tex')
    stage=m.BASE/'publish';stage.mkdir(exist_ok=True)
    for k,name in m.names().items():shutil.copy2(m.BASE/k/f'{k}.pdf',stage/name)
    for name in m.names().values():os.replace(stage/name,m.common.FORMAL/name)
    assert all(m.sha(m.common.FORMAL/name)==h for name,h in baseline.items() if name not in m.names().values())
    save('publication.json',{'published_at':datetime.now().astimezone().isoformat(),'archive':str(m.ARCHIVE),
         'files':{name:{'sha256':checks[k]['sha256'],'pages':checks[k]['pages']} for k,name in m.names().items()}})
    print('Published five thermal chapters, volume3 and main.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--volume-regression',action='store_true');p.add_argument('--regression',action='store_true');p.add_argument('--publish',action='store_true');a=p.parse_args()
    if a.volume_regression:volume_regression()
    if a.regression:regression()
    if a.publish:publish()
