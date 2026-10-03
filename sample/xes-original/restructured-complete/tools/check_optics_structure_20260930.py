"""Private chapter/volume checks. This does not publish or certify all sources."""
import re,json,hashlib,subprocess
from pathlib import Path
import fitz
from revise_optics_20260930 import BASE,ARCHIVE,FORMAL,book,sha,save,names

def image_hashes(doc):
    hashes=set()
    for xref in {v[0] for p in doc for v in p.get_images(full=True)}:
        pix=fitz.Pixmap(doc,xref)
        hashes.add((pix.width,pix.height,pix.n,hashlib.sha256(pix.samples).hexdigest()))
    return hashes

def check():
    rows={};filename=names()
    for key in ['ch27','ch28','ch29','ch30','volume5']:
        pdf=BASE/key/f'{key}.pdf';doc=fitz.open(pdf)
        q=subprocess.run(['qpdf','--check',str(pdf)],capture_output=True,text=True)
        font=subprocess.run(['pdffonts',str(pdf)],capture_output=True,text=True,check=True)
        unembedded=[x for x in font.stdout.splitlines()[2:] if x.strip() and x.split()[-5]!='yes']
        log=pdf.with_suffix('.log').read_text(errors='replace')
        problems=re.findall(r'^.*(?:Overfull|Underfull|undefined|Missing character|multiply defined|^!).*$',log,re.M)
        assert q.returncode==0 and not unembedded and not problems,(key,unembedded,problems)
        assert all(0<x[2]<=len(doc) for x in doc.get_toc())
        rows[key]={'pages':len(doc),'sha256':sha(pdf),'qpdf':q.stdout,'unembedded_fonts':unembedded,'log_problems':problems,'bookmarks':doc.get_toc(),'copyable_text_characters':sum(len(p.get_text()) for p in doc)}
        if key!='volume5':
            old=fitz.open(ARCHIVE/'pdf'/filename[key])
            a,b=image_hashes(old),image_hashes(doc)
            assert a==b,(key,'raster illustration assets changed')
            rows[key]['existing_distinct_raster_assets_retained']=len(a)
    volume=fitz.open(BASE/'volume5/volume5.pdf')
    starts=[t[2]-1 for t in volume.get_toc() if t[0]==1]
    assert len(starts)==4
    comparison=[]
    for n,start in zip(range(27,31),starts):
        chapter=fitz.open(BASE/f'ch{n}/ch{n}.pdf')
        changed=[]
        for j in range(1,len(chapter)):
            a,b=chapter[j],volume[start+j-1]
            clip=fitz.Rect(40,52,a.rect.width-40,a.rect.height-52)
            text_same=a.get_text(clip=clip)==b.get_text(clip=clip)
            pixel_same=a.get_pixmap(dpi=100,clip=clip).samples==b.get_pixmap(dpi=100,clip=clip).samples
            if not(text_same and pixel_same):changed.append({'chapter_pdf_page':j+1,'volume_pdf_page':start+j,'text_same':text_same,'pixels_same':pixel_same})
        comparison.append({'chapter':n,'body_pages':len(chapter)-1,'differences':changed})
        assert not changed,(n,changed)
    ledger=json.loads((book.BOOK/'audit/source-review/optics-additions-20260930.json').read_text())
    source_hashes={x['source_pdf']:sha(Path(x['source_pdf'])) for x in ledger['objects']}
    baseline=json.loads((ARCHIVE/'manifest.json').read_text())
    protected={name:sha(FORMAL/name)==baseline['formal'][name]['sha256'] for key,name in filename.items() if key!='main'}
    assert all(protected.values()),protected
    save(BASE/'structure-and-regression.json',{'pdfs':rows,'chapter_volume_comparison':comparison,'new_question_source_hashes':source_hashes,'formal_optics_still_unchanged':protected,'not_checked':['Full original-source completeness','All pre-existing figures geometry','Full-book rebuild and regression','User visual acceptance']})
    print(json.dumps({'pages':{k:v['pages'] for k,v in rows.items()},'volume_regression':comparison,'formal_optics_unchanged':all(protected.values())},ensure_ascii=False,indent=2))

if __name__=='__main__':check()
