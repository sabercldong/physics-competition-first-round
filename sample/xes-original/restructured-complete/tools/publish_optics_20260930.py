"""Narrow, hash-gated publication: four optics chapters and volume 5 only.

The full book is owned by a concurrent review. Never publish main.pdf here.
The private revision builder remains the reproducible optics source entry.
"""
import json,os,shutil,tempfile
from datetime import datetime
from pathlib import Path
from revise_optics_20260930 import BASE,ARCHIVE,FORMAL,book,sha,save,names

def publish():
    import build_review_ch15_ch16 as common
    from optics_teaching_layout import update_source_maps
    review=json.loads((BASE/'final-human-review.json').read_text())
    assert review['release_decision']=='approved_for_optics_only'
    structure=json.loads((BASE/'structure-and-regression.json').read_text())
    mechanics=json.loads((BASE/'mechanical-checks.json').read_text())
    keys=['ch27','ch28','ch29','ch30','volume5']
    changed_generated={book.GENERATED/f'chapters/ch{n}.tex' for n in range(27,31)}
    protected_sources={str(p):sha(p) for root in (book.GENERATED,book.BOOK/'advanced')
       for p in root.rglob('*.tex') if p not in changed_generated}
    protected_sources[str(book.BOOK/'style.tex')]=sha(book.BOOK/'style.tex')
    protected_sources[str(book.BOOK/'main.tex')]=sha(book.BOOK/'main.tex')
    normal={}
    for n in range(27,31):
        body,maps=common.chapter_text(n)
        assert body==(BASE/f'staged/ch{n}-body.tex').read_text(),('Normal build differs',n)
        update_source_maps(n,maps);normal[n]=(body,maps)
    before={p.name:sha(p) for p in FORMAL.glob('*.pdf')}
    for key in keys:
        pdf=BASE/key/f'{key}.pdf';h=sha(pdf)
        assert h==review['pdfs'][key]==structure['pdfs'][key]['sha256']
        build=json.loads((pdf.parent/'build-evidence.json').read_text())
        assert build['passes']>=2 and build['pdf_sha256']==h
        assert all(sha(Path(p))==v for p,v in build['inputs'].items())
        if key!='volume5':
            row=mechanics[key[2:]]
            assert row['sha256']==h and row['examples']==row['solutions']
            assert not any(row[x] for x in ('duplicate_labels','unresolved_local_refs','log_findings','qpdf_exit'))
            render=json.loads((BASE/f'final-render/{key}/evidence.json').read_text())
            assert render['pdf_sha256']==h and render['dpi']>=300
    # Retain the exact old formal PDFs, not an assumed older main-book baseline.
    # The task's client date is authoritative; a host clock may be stale.
    backup=book.PROJECT/'archive'/('20261003-'+datetime.now().strftime('%H%M%S')+'-optics-release')
    (backup/'previous-pdf').mkdir(parents=True)
    for key in keys:
        name=names()[key];shutil.copy2(FORMAL/name,backup/'previous-pdf'/name)
    # Snapshot our final source and evidence without copying mutable advanced units.
    for directory in ('staged','final-figure-checks'):
        shutil.copytree(BASE/directory,backup/directory)
    shutil.copytree(book.BOOK/'chapters/new/optics-depth',backup/'optics-depth')
    (backup/'tools').mkdir()
    for p in (book.BOOK/'tools').glob('*optics*.py'):shutil.copy2(p,backup/'tools'/p.name)
    shutil.copy2(book.BOOK/'tools/build_restructured.py',backup/'tools/build_restructured.py')
    shutil.copy2(BASE/'build_restructured-before-optics-hook.py',backup/'tools/build_restructured-before-optics-hook.py')
    for p in BASE.glob('*.json'):shutil.copy2(p,backup/p.name)
    shutil.copy2(book.BOOK/'style.tex',backup/'style.tex')
    dependencies={}
    for key in keys:
        for line in (BASE/key/f'{key}.fls').read_text().splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=(book.BOOK/p).resolve() if not p.is_absolute() else p.resolve()
            if not p.is_file() or p.suffix.lower() not in {'.tex','.sty','.png','.jpg','.jpeg','.pdf'}:continue
            try:rel=p.relative_to(book.PROJECT)
            except ValueError:continue
            dest=backup/'project-dependencies'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():shutil.copy2(p,dest)
            dependencies[str(rel)]=sha(p)
    save(backup/'project-dependencies.json',dependencies)
    save(backup/'previous-formal-manifest.json',before)
    (backup/'previous-generated').mkdir()
    mapping_path=book.GENERATED/'source-map.json'
    shutil.copy2(mapping_path,backup/'previous-generated/source-map.json')
    mapping=json.loads(mapping_path.read_text())
    for n,(body,maps) in normal.items():
        p=book.GENERATED/f'chapters/ch{n}.tex'
        shutil.copy2(p,backup/'previous-generated'/p.name)
        # Mechanically generated output; the editable implementation is the hook.
        p.write_text(body)
        entry=next(x for x in mapping['chapters'] if x['chapter']==n)
        entry['source_number_maps']=maps
        entry['optics_review']='audit/source-review/optics-final-figure-map-20260930.md'
        entry['additional_question_sources']='audit/source-review/optics-additions-20260930.json'
    save(mapping_path,mapping)
    # Each replacement is atomic; the release manifest is written after all five.
    for key in keys:
        src=BASE/key/f'{key}.pdf';dest=FORMAL/names()[key]
        with tempfile.NamedTemporaryFile(dir=FORMAL,prefix='.optics-',suffix='.pdf',delete=False) as f:
            temp=Path(f.name)
        shutil.copy2(src,temp);assert sha(temp)==review['pdfs'][key]
        os.replace(temp,dest)
    after={p.name:sha(p) for p in FORMAL.glob('*.pdf')}
    assert all(sha(Path(p))==h for p,h in protected_sources.items()),'Non-optics source changed concurrently'
    unrelated=[name for name,h in before.items() if name not in {names()[k] for k in keys} and after.get(name)!=h]
    result={'published':{names()[k]:after[names()[k]] for k in keys},'archive':str(backup),
      'full_book_published':False,'concurrent_unrelated_changes':unrelated,
      'source_entry':'tools/revise_optics_20260930.py --stage --target volume5',
      'generated_updated':[27,28,29,30],'main_and_non_optics_generated_untouched':True,
      'normal_build_hook_matches_reviewed_source':True}
    result['protected_non_optics_source_count']=len(protected_sources)
    save(BASE/'publication.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':publish()
