"""Narrow regression and guarded publication for the mechanics expansion."""
import argparse, json, re, shutil, os
from pathlib import Path
from datetime import datetime
import fitz
import enrich_mechanics_20260927 as m

def save(name, value):
    (m.BASE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))

def body(p):
    return re.sub(r'\s+','',p.get_text(clip=fitz.Rect(0,65,p.rect.width,p.rect.height-55)))

def pixels(p):
    return p.get_pixmap(dpi=90,clip=fitz.Rect(0,65,p.rect.width,p.rect.height-55),alpha=False).samples

def regression():
    old=fitz.open(m.ARCHIVE/'pdf'/m.names()['main'])
    new=fitz.open(m.BASE/'main/main.pdf')
    vol=fitz.open(m.BASE/'volume2/volume2.pdf')
    a=[x for x in old.get_toc() if x[0]==1]
    b=[x for x in new.get_toc() if x[0]==1]
    assert [x[1] for x in a]==[x[1] for x in b]
    changed={m.book.CHAPTERS[n]['title'] for n in range(5,14)}
    protected=[]
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
    for n in range(5,14):
        key=f'ch{n:02}';d=fitz.open(m.BASE/key/f'{key}.pdf');title=m.book.CHAPTERS[n]['title']
        vs=next(x[2] for x in vol.get_toc() if x[0]==1 and x[1]==title)
        ms=next(x[2] for x in b if x[1]==title)
        for i in range(1,len(d)):
            for dest,page in [('volume',vol[vs+i-2]),('main',new[ms+i-2])]:
                assert body(d[i])==body(page),(key,i,dest,'text')
                assert pixels(d[i])==pixels(page),(key,i,dest,'raster')
        rows.append({'chapter':n,'body_pages':len(d)-1,'text_and_raster_equal':True})
    save('regression.json',{'protected_units':protected,'mechanics':rows,
         'pdf_hashes':{k:m.sha(m.BASE/k/f'{k}.pdf') for k in m.names()}})
    print('Regression passed:',len(protected),'protected units,',len(rows),'mechanics chapters',flush=True)

def publish():
    baseline=json.loads((m.ARCHIVE/'manifest.json').read_text())
    checks=json.loads((m.BASE/'structure.json').read_text())
    visual=json.loads((m.BASE/'visual-reviewed.json').read_text())
    reg=json.loads((m.BASE/'regression.json').read_text())
    for p,h in json.loads((m.BASE/'main-frozen-inputs.json').read_text()).items():
        assert m.sha(Path(p))==h,('frozen input',p)
    for k,name in m.names().items():
        assert m.sha(m.common.FORMAL/name)==baseline[name]['sha256'],('formal changed',name)
        h=m.sha(m.BASE/k/f'{k}.pdf')
        assert h==checks[k]['sha256']==visual['pdf_hashes'][k]==reg['pdf_hashes'][k]
        assert checks[k]['qpdf_returncode']==0 and not checks[k]['errors']
    assert visual['all_mechanics_pages_overview_reviewed'] and visual['new_teaching_pages_reviewed']
    for n in range(5,14):
        current,_=m.common.chapter_text(n)
        assert current==(m.BASE/f'staged/ch{n:02}-body.tex').read_text(),('maintenance source changed',n)
    for k in m.names():
        for line in checks[k]['font_report'].splitlines()[2:]:
            assert line.split()[-5]=='yes',('font not embedded',k,line)
    for name,row in baseline.items():
        if name not in m.names().values():assert m.sha(m.common.FORMAL/name)==row['sha256'],name
    for n in range(5,14):
        shutil.copy2(m.BASE/f'staged/ch{n:02}-body.tex',m.book.GENERATED/f'chapters/ch{n:02}.tex')
    stage=m.BASE/'publish';stage.mkdir(exist_ok=True)
    for k,name in m.names().items():shutil.copy2(m.BASE/k/f'{k}.pdf',stage/name)
    for k,name in m.names().items():os.replace(stage/name,m.common.FORMAL/name)
    save('publication.json',{'published_at':datetime.now().astimezone().isoformat(),'archive':str(m.ARCHIVE),
         'files':{name:{'sha256':checks[k]['sha256'],'pages':checks[k]['pages']} for k,name in m.names().items()}})
    print('Published 9 chapters, mechanics volume, and main.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--regression',action='store_true');p.add_argument('--publish',action='store_true');a=p.parse_args()
    if a.regression:regression()
    if a.publish:publish()
