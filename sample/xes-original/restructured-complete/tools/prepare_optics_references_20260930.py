"""Read-only source discovery; generated page images/OCR live in private build."""
import argparse,json,subprocess,re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import fitz
from PIL import Image,ImageDraw
from revise_optics_20260930 import BASE,book,save
SOURCES={
 'xes':Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020寒】兴趣一阶-光学.pdf'),
 'cheng':Path('/Users/dongxingxi/Downloads/程书/热学、光学、近代物理学篇（程稼夫系列后续）.pdf'),
 'black':Path('/Users/dongxingxi/Downloads/黑白皮/新编物理 奥赛实用题典（462）.pdf'),
 'white':Path('/Users/dongxingxi/Downloads/黑白皮/新编物理 奥赛指导（470）.pdf')}
def prepare(key,pages):
    out=BASE/'sources'/key;out.mkdir(parents=True,exist_ok=True);d=fitz.open(SOURCES[key])
    binary=BASE/'vision_ocr'
    if not binary.exists():subprocess.run(['swiftc',str(book.PROJECT/'tools/vision_ocr.swift'),'-o',str(binary)],check=True)
    for n in pages:
        image=out/f'p{n:03}.png'
        if not image.exists():d[n-1].get_pixmap(dpi=180).save(image)
    def ocr(n):
        p=out/f'p{n:03}.txt'
        if not p.exists():subprocess.run([str(binary),str(out/f'p{n:03}.png'),str(p)],check=True,capture_output=True)
    with ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(ocr,pages))
    for start in range(0,len(pages),8):
        sheet=Image.new('RGB',(1600,1180),'#ddd');draw=ImageDraw.Draw(sheet)
        for j,n in enumerate(pages[start:start+8]):
            im=Image.open(out/f'p{n:03}.png');im.thumbnail((390,550));x=j%4*400;y=j//4*590
            sheet.paste(im,(x,y+25));draw.text((x+5,y+5),f'{key} physical p{n}',fill='black')
        sheet.save(out/f'overview-{pages[start]:03}.jpg',quality=92)
    print(key,pages,flush=True)
def cai():
    folder=Path('/Users/dongxingxi/Downloads/2026.6.22/竞赛/蔡题集萃/蔡题集萃_整理版');rows=[]
    for path in sorted(folder.glob('蔡题*/试卷.pdf')):
        d=fitz.open(path)
        for i,p in enumerate(d):
            text=p.get_text();terms=[w for w in ['光程','折射率','透镜','干涉','衍射','偏振','光栅','波片'] if w in text]
            if len(terms)>=1:
                snippets=[]
                for line in text.splitlines():
                    if any(w in line for w in terms):snippets.append(line)
                rows.append({'source':str(path),'physical_page':i+1,'terms':terms,'snippets':snippets})
    save(BASE/'cai-optics-candidates.json',rows);print('Cai candidate pages',len(rows))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--key',choices=SOURCES);p.add_argument('--pages');p.add_argument('--cai',action='store_true');a=p.parse_args()
    if a.key:
        pages=[]
        for block in a.pages.split(','):
            if '-' in block:
                lo,hi=map(int,block.split('-'));pages.extend(range(lo,hi+1))
            else:pages.append(int(block))
        prepare(a.key,pages)
    if a.cai:cai()
