"""Evidence and guarded publication for the thermal revision; no implicit release."""
import argparse, hashlib, json, os, re, shutil, subprocess
from datetime import datetime
from pathlib import Path
import fitz
import revise_volume3_20260927 as r

sha = r.common.sha
LATEST = r.ARCHIVE / 'latest-shared-before-thermal'

def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2))

def checkpoint():
    if (LATEST/'manifest.json').exists():
        return
    LATEST.mkdir(parents=True, exist_ok=True)
    records = {}
    for key, name in r.NAMES.items():
        p = r.common.FORMAL/name
        (LATEST/'pdf').mkdir(exist_ok=True)
        shutil.copy2(p, LATEST/'pdf'/name)
        records[key] = dict(sha256=sha(p), pages=len(fitz.open(p)))
    assert records['main']['sha256'] == '45c122151bcb90cda55b9fb814e92d221da7c11fcab6abef2f67cca1147df59e'
    # The preceding archive supplies the old thermal inputs. Preserve the
    # subsequently published chapter-six generation in this exact checkpoint.
    shutil.copytree(r.book.GENERATED, LATEST/'generated', dirs_exist_ok=True)
    for n in range(14,19):
        shutil.copy2(r.ARCHIVE/f'source/restructured-complete/generated/chapters/ch{n}.tex', LATEST/f'generated/chapters/ch{n}.tex')
    old_map=json.loads((r.ARCHIVE/'source/restructured-complete/generated/source-map.json').read_text())
    current=json.loads((LATEST/'generated/source-map.json').read_text())
    for i,c in enumerate(current['chapters']):
        if c['chapter'] in range(14,19):
            current['chapters'][i]=next(x for x in old_map['chapters'] if x['chapter']==c['chapter'])
    save(LATEST/'generated/source-map.json',current)
    protected={str(p):sha(p) for p in (r.book.GENERATED/'chapters').glob('*.tex') if p.stem not in r.NAMES}
    formal_protected={str(p):sha(p) for p in r.common.FORMAL.glob('*.pdf') if p.name not in r.NAMES.values()}
    save(LATEST/'manifest.json',dict(formal=records, protected=protected, formal_protected=formal_protected,
        source_note='Use archived original root configuration/assets with this generated snapshot; chapter six includes the 10:17 publication.'))

def structure(keys=None):
    rows={}
    for key in (keys or r.NAMES):
        p=r.BASE/key/f'{key}.pdf';doc=fitz.open(p)
        log=(p.with_suffix('.log')).read_text(errors='replace')
        warnings=re.findall(r'(?m)^.*(?:Overfull|Underfull|Missing character|undefined|multiply defined|Rerun to get).*(?:\n.*)?',log)
        inherited=[]
        if key=='main':
            prior=(LATEST/'main.log').read_text(errors='replace')
            previous=re.findall(r'(?m)^.*(?:Overfull|Underfull|Missing character|undefined|multiply defined|Rerun to get).*(?:\n.*)?',prior)
            if warnings==previous and len(warnings)==1 and 'Underfull \\hbox (badness 1253)' in warnings[0]:
                inherited=warnings
        q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
        fonts=subprocess.run(['pdffonts',str(p)],capture_output=True,text=True,check=True).stdout
        # pdffonts has variable-width type names; the trailing columns are stable.
        unembedded=[line for line in fonts.splitlines()[2:] if line.split()[-5] != 'yes']
        text='\n'.join(page.get_text() for page in doc)
        (r.BASE/key/'extracted.txt').write_text(text)
        row=dict(pages=len(doc),sha256=sha(p),warnings=warnings,inherited_unmodified_A4_warning=inherited,qpdf_code=q.returncode,
            qpdf=q.stdout+q.stderr,fonts=fonts,unembedded=unembedded,
            replacement_characters=text.count('\ufffd'),bookmarks=doc.get_toc(),text_per_page=[len(page.get_text()) for page in doc])
        assert (not warnings or warnings==inherited) and q.returncode==0 and not unembedded and not row['replacement_characters'],(key,row)
        assert row['bookmarks'] and all(1<=x[2]<=len(doc) for x in row['bookmarks'])
        frozen=json.loads((r.BASE/key/'frozen-build.json').read_text())
        assert frozen['passes']>=2 and frozen['pdf_sha256']==sha(p)
        # Earlier chapter builds recorded every staged chapter, even unused ones.
        # Only the own body/wrapper are actual chapter inputs.
        for path,h in frozen['chapter_hashes'].items():
            if key.startswith('ch') and Path(path).name not in [f'{key}.tex',f'{key}-body.tex']:
                continue
            assert sha(Path(path))==h,(key,path)
        rows[key]=row
    save(r.BASE/'structural-checks.json',rows)
    print([(k,v['pages']) for k,v in rows.items()])

def sources():
    mapping=json.loads((r.book.GENERATED/'source-map.json').read_text())
    rows=[]; source_objects=[]
    for n,expected in [(14,11),(15,11),(16,5),(17,6),(18,7)]:
        body=(r.book.GENERATED/f'chapters/ch{n}.tex').read_text()
        assert body==(r.BASE/f'staged/ch{n}-body.tex').read_text()
        q=re.findall(r'\\begin\{origexamplebox\}.*?\\end\{origexamplebox\}',body,re.S)
        sol=re.findall(r'\\begin\{xesolution\}.*?\\end\{xesolution\}',body,re.S)
        assert len(q)==len(sol)==expected
        labels=re.findall(r'\\label\{([^}]+)\}',body)
        assert len(labels)==len(set(labels))
        aux=(r.BASE/f'ch{n}/ch{n}.aux').read_text()
        c=next(c for c in mapping['chapters'] if c['chapter']==n)
        for unit in c['source_number_maps']:
            for obj in unit['objects']:
                if obj['source_kind'] in ['ex','fig']:
                    assert r'\newlabel{'+obj['new_label']+'}' in aux,obj
                    source_objects.append(dict(chapter=n,**obj))
        rows.append(dict(chapter=n,examples=len(q),solutions=len(sol),sections=re.findall(r'\\section\{([^}]+)\}',body),source_sha256=sha(r.book.GENERATED/f'chapters/ch{n}.tex')))
    question_figures=[]
    for n,question,page,macro in [(14,6,15,'exampleNineteenSixFaithful'),(14,7,16,'figureNineteenSevenFaithful'),(14,8,16,'figureNineteenEightFaithful'),(15,9,29,'cycleQuestionRedraw'),(15,10,29,'straightQuestionRedraw'),(15,11,30,'liftingPistonQuestionRedraw'),(17,4,50,'pressureCookerQuestionFigure')]:
        body=(r.book.GENERATED/f'chapters/ch{n}.tex').read_text()
        q=re.findall(r'\\begin\{origexamplebox\}.*?\\end\{origexamplebox\}',body,re.S)
        assert '\\'+macro in q[question-1]
        assert sum(('\\'+macro) in x for x in q)==1
        question_figures.append(dict(chapter=n,question=question,source_physical_page=page,macro=macro,status='in_question_box'))
    assert sum(x['source_kind']=='fig' for x in source_objects)==31
    save(r.BASE/'source-correspondence.json',dict(chapters=rows,source_objects=source_objects,
        question_figures=question_figures, source_numbered_figures=31,
        source_unnumbered_groups=[dict(page=15,target='14.6 apparatus and blank plotting grid'),dict(page=50,target='17.4 pressure cooker and saturation curve')],
        original_examples=33,statistics_bridge_examples=7,
        source_sha256={str(p):sha(p) for p in [r.HEAT,r.STATS]},
        limitation='Object correspondence and question/figure retention audited; not a character-by-character identity claim. Sources 14.9/14.10 have no visible diagram and remain explicitly reconstructed models.'))

def body_text(page):
    return re.sub(r'\s+','',page.get_text(clip=fitz.Rect(0,65,page.rect.width,page.rect.height-55)))

def page_ledger():
    """Rebind prior page-index clues to the newly checked generated targets."""
    audit=r.book.BOOK/'audit'
    old14=json.loads((audit/'source-review/ch13-ch14-revision-ledger-20260912.json').read_text())
    old1516=json.loads((audit/'source-review/ch15-ch16-revision-ledger-20260915.json').read_text())
    pages=[dict(x,chapter=14) for x in old14['pages'] if x.get('source')=='thermal']
    pages.extend(old1516['pages'])
    manual17=[
        (41,'物态、分子作用与相变','相图',[]),
        (42,'水相图、潜热、状态方程背景','相图',['fig:s31-22-1']),
        (43,'范德瓦耳斯方程及参数表','范德瓦耳斯方程',['tab:s31-22-1','eq:s31-22-1']),
        (44,'等温线、低密度展开、凝结','等温线',['fig:s31-22-2','eq:s31-22-2']),
        (45,'临界导数、参数、两类路径','临界点',['fig:s31-22-3','eq:s31-22-3']),
        (46,'临界实验、压缩率、约化、等面积图','低于临界温度的等温线',['fig:s31-22-4','fig:s31-22-5']),
        (47,'等面积推导、稳定与亚稳段、尾迹','过冷气体与过热液体',['fig:s31-22-6']),
        (48,'云室和气泡室、例22.1、例22.2开始','过冷气体与过热液体',['ex:s31-22-1','ex:s31-22-2']),
        (49,'例22.2续、例22.3三问、例22.4题干','综合例题',['ex:s31-22-2','ex:s31-22-3','ex:s31-22-4']),
        (50,'压力锅装置和饱和曲线、例22.5、例22.6开始','综合例题',['ex:s31-22-4','ex:s31-22-5','ex:s31-22-6']),
        (51,'例22.6六个子问','综合例题',['ex:s31-22-6']),
    ]
    for page,topics,heading,targets in manual17:
        pages.append(dict(id=f'thermal:page:{page}',source='thermal',physical_page=page,printed_page=page+274,chapter=17,teaching_topics=topics,target_heading=heading,targets=['ch17:'+x for x in targets],status='mapped'))
    stats=[
        (68,'事件空间、古典/几何概率、乘积空间','概率、随机变量与涨落'),
        (69,'概率公理、条件、密度、变量变换','概率、随机变量与涨落'),
        (70,'双根变量变换、均值、大数定律、方差、柯西分布','概率、随机变量与涨落'),
        (71,'信息对数形式、细分与条件熵','微观状态、宏观状态与熵'),
        (72,'链式关系、可加性、不等式、互信息、偏振模型','微观状态、宏观状态与熵'),
        (73,'补事件、球面测度、高斯最大熵','微观状态、宏观状态与熵'),
        (74,'边缘分布、随机性、衰变、系综、刘维尔、等概率','分子通量、压强与统计假设'),
        (75,'H定理、速度与速率分布、平均、通量及压强','分子通量、压强与统计假设'),
        (76,'平均场、连续正则积分、均分、功热及熵','从配分函数连接功、热与熵'),
    ]
    for page,topics,heading in stats:
        pages.append(dict(id=f'stats:page:{page}',source='stats',physical_page=page,printed_page=None,chapter=18,teaching_topics=topics,target_heading=heading,targets=[],status='mapped'))
    assert len(pages)==55
    for row in pages:
        n=row['chapter'];body=(r.book.GENERATED/f'chapters/ch{n}.tex').read_text();aux=(r.BASE/f'ch{n}/ch{n}.aux').read_text()
        row['source']=row.get('source','thermal')
        for label in row.get('targets',[]):assert r'\newlabel{'+label+'}' in aux,(row['id'],label)
        if row.get('target_heading'):assert row['target_heading'] in body,row
        row['target_pdf_sha256']=sha(r.BASE/f'ch{n}/ch{n}.pdf')
        row['verification_level']='Source overview and teaching-topic/object correspondence; detailed source-question checks recorded in semantic-review.md. Not character-level identity.'
    exclusions=[dict(source='thermal',physical_page=p,status='excluded',reason=reason) for ps,reason in [(range(1,5),'封面和目录'),([18,52,53],'空白'),([54],'广告')] for p in ps]
    exclusions.append(dict(source='stats',physical_page=77,status='excluded',reason='本章之后的空白页；本次未审该来源其他章节'))
    save(r.BASE/'page-ledger.json',dict(provenance='Prior page indexes used as clues, checked against the source overview and current object mappings; prior numbering is not treated as new verification evidence.',pages=pages,excluded=exclusions))

def volume_regression():
    vol=fitz.open(r.BASE/'volume3/volume3.pdf')
    starts=[x for x in vol.get_toc() if x[0]==1]
    rows=[]
    for n,start in zip(range(14,19),starts):
        chapter=fitz.open(r.BASE/f'ch{n}/ch{n}.pdf')
        pixels=[]
        for i in range(1,len(chapter)):
            a=chapter[i];b=vol[start[2]+i-2]
            assert body_text(a)==body_text(b),(n,i,'volume text')
            clip=fitz.Rect(0,65,a.rect.width,a.rect.height-55)
            ap=a.get_pixmap(dpi=100,clip=clip,alpha=False)
            bp=b.get_pixmap(dpi=100,clip=clip,alpha=False)
            if ap.samples!=bp.samples:pixels.append(i+1)
        rows.append(dict(chapter=n,body_pages=len(chapter)-1,body_text_equal=True,pixel_different_pages=pixels))
    save(r.BASE/'volume-regression.json',rows)
    print(rows)

def regression():
    old=fitz.open(LATEST/'pdf'/r.NAMES['main']);new=fitz.open(r.BASE/'main/main.pdf')
    a=[x for x in old.get_toc() if x[0]==1];b=[x for x in new.get_toc() if x[0]==1]
    assert [x[1] for x in a]==[x[1] for x in b]
    heat_titles={r.book.CHAPTERS[n]['title'] for n in range(14,19)}
    results=[]
    for i,(x,y) in enumerate(zip(a,b)):
        if x[1] in heat_titles:continue
        ap=list(range(x[2]-1,a[i+1][2]-1 if i+1<len(a) else len(old)))
        bp=list(range(y[2]-1,b[i+1][2]-1 if i+1<len(b) else len(new)))
        assert len(ap)==len(bp),(x,y,len(ap),len(bp))
        differences=[(p+1,q+1) for p,q in zip(ap,bp) if body_text(old[p])!=body_text(new[q])]
        assert not differences,(x[1],differences)
        raster_differences=[]
        for p,q in zip(ap,bp):
            clip=fitz.Rect(0,65,old[p].rect.width,old[p].rect.height-55)
            old_pixels=old[p].get_pixmap(dpi=90,clip=clip,alpha=False)
            new_pixels=new[q].get_pixmap(dpi=90,clip=clip,alpha=False)
            if old_pixels.samples!=new_pixels.samples:raster_differences.append((p+1,q+1))
        assert not raster_differences,(x[1],raster_differences)
        results.append(dict(title=x[1],pages=len(ap),body_text_equal=True,body_raster_equal=True))
    # The volume and standalone bodies should have exactly the same pagination.
    vol=fitz.open(r.BASE/'volume3/volume3.pdf');t=[x for x in vol.get_toc() if x[0]==1]
    thermal=[]
    for n,start in zip(range(14,19),t):
        chapter=fitz.open(r.BASE/f'ch{n}/ch{n}.pdf')
        mainstart=next(x[2] for x in b if x[1]==start[1])
        for i in range(1,len(chapter)):
            assert body_text(chapter[i])==body_text(vol[start[2]+i-2]),(n,i,'volume')
            assert body_text(chapter[i])==body_text(new[mainstart+i-2]),(n,i,'main')
        thermal.append(dict(chapter=n,body_pages=len(chapter)-1,volume_main_body_text_equal=True))
    save(r.BASE/'regression.json',dict(unmodified_units=results,thermal=thermal))

def publish():
    checks=json.loads((r.BASE/'structural-checks.json').read_text())
    visual=json.loads((r.BASE/'visual-reviewed.json').read_text())
    assert visual.get('independent_visual_gate_passed') is True
    assert len(set(visual.get('independent_reviewer_ids',[]))) == 4
    baseline=json.loads((LATEST/'manifest.json').read_text())
    assert (r.BASE/'regression.json').exists() and (r.BASE/'source-correspondence.json').exists()
    for group in ['protected','formal_protected']:
        assert all(sha(Path(p))==h for p,h in baseline[group].items()),group
    for key,name in r.NAMES.items():
        assert sha(r.common.FORMAL/name)==baseline['formal'][key]['sha256']
        assert sha(r.BASE/key/f'{key}.pdf')==checks[key]['sha256']==visual['pdfs'][key]
        frozen=json.loads((r.BASE/key/'frozen-build.json').read_text())
        for path,h in frozen['chapter_hashes'].items():
            if key.startswith('ch') and Path(path).name not in [f'{key}.tex',f'{key}-body.tex']:
                continue
            assert sha(Path(path))==h,(key,path)
    stage=r.BASE/'publish';stage.mkdir(exist_ok=True)
    for key,name in r.NAMES.items():shutil.copy2(r.BASE/key/f'{key}.pdf',stage/name)
    for key,name in r.NAMES.items():
        assert sha(stage/name)==checks[key]['sha256']
        os.replace(stage/name,r.common.FORMAL/name)
    save(r.BASE/'publication.json',dict(published_at=datetime.now().astimezone().isoformat(),
        files={name:dict(sha256=checks[key]['sha256'],pages=checks[key]['pages']) for key,name in r.NAMES.items()},archive=str(r.ARCHIVE)))
    print('Published seven verified thermal artifacts.')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['checkpoint','structure','sources','regression','publish']:p.add_argument('--'+name,action='store_true')
    a=p.parse_args()
    for name in ['checkpoint','structure','sources','regression','publish']:
        if getattr(a,name):globals()[name]()
