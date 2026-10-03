"""Read-only source/PDF evidence generation for the Chapter 9 review."""
from pathlib import Path
import hashlib, json, re
import fitz
from PIL import Image, ImageDraw

BOOK=Path(__file__).resolve().parent.parent
ROOT=BOOK.parents[2]
OUT=BOOK/'build/review-ch09-20260909'
OUT.mkdir(parents=True,exist_ok=True)
FILES={
    'current':(ROOT/'output/pdf/高中物理竞赛一轮讲义_第09章_角动量与刚体动力学_含解答与解图.pdf',None),
    'source':(Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2019暑】兴趣一阶.pdf'),list(range(3,25)))
}
manifest={}
for key,(path,selection) in FILES.items():
    doc=fitz.open(path)
    pages=selection or list(range(1,len(doc)+1))
    dest=OUT/key;dest.mkdir(exist_ok=True)
    text=[]
    for n in pages:
        p=doc[n-1]
        p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(dest/f'page-{n:02}.png')
        text.append(f'\n===== PHYSICAL PAGE {n} =====\n'+p.get_text())
    (dest/'text.txt').write_text('\n'.join(text))
    for start in range(0,len(pages),6):
        batch=pages[start:start+6]
        sheet=Image.new('RGB',(1500,1470),'white'); draw=ImageDraw.Draw(sheet)
        for j,n in enumerate(batch):
            im=Image.open(dest/f'page-{n:02}.png');im.thumbnail((490,690))
            x=(j%3)*500;y=(j//3)*735
            draw.text((x+8,y+5),f'{key} physical page {n}',fill='black')
            sheet.paste(im,(x+(500-im.width)//2,y+25))
        sheet.save(dest/f'contact-{batch[0]:02}.jpg',quality=92)
    manifest[key]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                   'total_pages':len(doc),'review_pages':pages,'toc':doc.get_toc() if key=='current' else []}
tex=(BOOK/'generated/chapters/ch09.tex').read_text()
manifest['generated_source_sha256']=hashlib.sha256(tex.encode()).hexdigest()
manifest['examples']=len(re.findall(r'\\begin\{origexamplebox\}',tex))
manifest['solutions']=len(re.findall(r'\\begin\{xesolution\}',tex))
manifest['numbered_figures']=len(re.findall(r'\\label\{ch09:fig:',tex))
manifest['tikz_pictures']=len(re.findall(r'\\begin\{tikzpicture\}',tex))
manifest['white_fill_mentions']=len(re.findall(r'fill\s*=\s*white',tex))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k not in FILES},ensure_ascii=False,indent=2))
