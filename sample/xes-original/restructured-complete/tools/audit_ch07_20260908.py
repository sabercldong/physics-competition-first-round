"""Read-only document audit: render formal chapter and original source pages."""
from pathlib import Path
import fitz, re, json, hashlib, subprocess
from PIL import Image, ImageDraw

BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
OUT=ROOT/'tmp/pdfs/ch07-audit-20260908'
OUT.mkdir(parents=True,exist_ok=True)
PDF=ROOT/'output/pdf/高中物理竞赛一轮讲义_第07章_动量、变质量系统与碰撞_含解答与解图.pdf'
SRC=Path('/Users/dongxingxi/Downloads/学而思资料/一轮/19春假兴趣1-力学.pdf')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def contact(files,prefix):
    for start in range(0,len(files),6):
        sheet=Image.new('RGB',(1500,1460),'white'); draw=ImageDraw.Draw(sheet)
        for k,fn in enumerate(files[start:start+6]):
            im=Image.open(fn);im.thumbnail((480,690))
            x,y=k%3*500,k//3*730
            sheet.paste(im,(x,y+28));draw.text((x+8,y+6),fn.stem,fill='black')
        sheet.save(OUT/f'{prefix}-{start+1:02}.jpg')
d=fitz.open(PDF); s=fitz.open(SRC)
manifest={'pdf':str(PDF),'sha256':sha(PDF),'pages':len(d),'toc':d.get_toc(),
          'source':str(SRC),'source_sha256':sha(SRC),'figures':[],'examples':{}}
files=[]
for i,p in enumerate(d):
    fn=OUT/f'current-{i+1:02}.png'; p.get_pixmap(matrix=fitz.Matrix(2,2)).save(fn);files.append(fn)
    for n in re.findall(r'例\s*7\.(\d+)\b',p.get_text()):
        manifest['examples'].setdefault(n,[]).append(i+1)
    bands=[]
    for v in p.get_drawings():
        r=v['rect']
        if r.width>p.rect.width*.76 or r.y0<48 or r.height>360: continue
        if r.width<.7 and r.height<.7: continue
        bands.append(r)
    clusters=[]
    for r in sorted(bands,key=lambda r:r.y0):
        if clusters and r.y0<clusters[-1].y1+45: clusters[-1]|=r
        else: clusters.append(fitz.Rect(r))
    for b in p.get_text('dict')['blocks']:
        for ln in b.get('lines',[]):
            text=''.join(x['text'] for x in ln['spans']).strip()
            if not re.match(r'^(题图|题意图|解图|示意图)[：:]',text): continue
            cap=fitz.Rect(ln['bbox'])
            candidates=[r for r in clusters if r.y1<=cap.y0+3 and cap.y0-r.y1<75]
            if not candidates:
                manifest['figures'].append({'page':i+1,'caption':text,'needs_full_page':True});continue
            r=max(candidates,key=lambda r:r.y1)
            clip=fitz.Rect(38,max(48,r.y0-26),p.rect.width-35,min(p.rect.height-38,cap.y1+8))
            name=f'figure-{len(manifest["figures"])+1:02}-p{i+1:02}.png'
            p.get_pixmap(matrix=fitz.Matrix(3.5,3.5),clip=clip).save(OUT/name)
            manifest['figures'].append({'page':i+1,'caption':text,'file':name,'rect':list(clip)})
contact(files,'current-contact')
files=[]
for n in range(47,min(91,len(s)+1)):
    fn=OUT/f'source-{n:02}.png'; s[n-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(fn);files.append(fn)
contact(files,'source-contact')
t=(BOOK/'generated/chapters/ch07.tex').read_text()
manifest['tex_sha256']=sha(BOOK/'generated/chapters/ch07.tex')
manifest['counts']={k:t.count(v) for k,v in {'examples':r'\begin{origexamplebox}',
   'solutions':r'\begin{xesolution}','tikz':r'\begin{tikzpicture}','white_label_styles':'sollabel/.style={font=\\scriptsize,fill=white'}.items()}
labels=re.findall(r'\\label\{([^}]+)\}',t); refs=re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}',t)
manifest['duplicate_labels']=sorted({x for x in labels if labels.count(x)>1})
manifest['unknown_refs']=sorted(set(refs)-set(labels))
for command in ('qpdf','pdffonts'):
    args=[command,'--check',str(PDF)] if command=='qpdf' else [command,str(PDF)]
    r=subprocess.run(args,capture_output=True,text=True)
    (OUT/f'{command}.txt').write_text(r.stdout+r.stderr)
    manifest[command+'_returncode']=r.returncode
(OUT/'text.txt').write_text('\n\n'.join(f'=== PDF {i+1} ===\n'+p.get_text() for i,p in enumerate(d)))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k!='figures'},ensure_ascii=False,indent=2))
print('Figure groups:',len(manifest['figures']))
