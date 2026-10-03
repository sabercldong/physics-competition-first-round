"""Read-only document inspection; only write internal review artifacts."""
import fitz, hashlib, json, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[4]
BOOK=Path(__file__).resolve().parents[1]
OUT=BOOK/'build/review-ch27-ch28-20260923'
SOURCE=Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020寒】兴趣一阶-光学.pdf')

def render(key,path,pages):
    d=fitz.open(path); folder=OUT/key;folder.mkdir(parents=True,exist_ok=True)
    thumbs=[]
    for i in pages:
        pix=d[i].get_pixmap(dpi=145,alpha=False)
        dest=folder/f'page-{i+1:03}.png';pix.save(dest)
        im=Image.open(dest);im.thumbnail((450,635)); tile=Image.new('RGB',(470,665),'white')
        tile.paste(im,((470-im.width)//2,24));ImageDraw.Draw(tile).text((12,6),f'{key} PDF {i+1}',fill='black')
        thumbs.append(tile)
    for start in range(0,len(thumbs),6):
        canvas=Image.new('RGB',(940,1995),'#dddddd')
        for j,tile in enumerate(thumbs[start:start+6]):canvas.paste(tile,((j%2)*470,(j//2)*665))
        canvas.save(folder/f'contact-{start//6+1}.jpg')
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(d),'rendered_pages':[i+1 for i in pages]}

def main():
    result={}
    for n in (27,28):
        p=next((ROOT/'output/pdf').glob(f'*第{n}章*pdf'));d=fitz.open(p)
        result[f'ch{n}']=render(f'ch{n}',p,range(len(d)))
        txt='\n'.join(f'PDF PAGE {i+1}\n'+pg.get_text() for i,pg in enumerate(d))
        (OUT/f'ch{n}/text.txt').write_text(txt)
        q=subprocess.run(['qpdf','--check',str(p)],capture_output=True,text=True)
        (OUT/f'ch{n}/qpdf.txt').write_text(q.stdout+q.stderr)
        src=(BOOK/f'generated/chapters/ch{n}.tex').read_text()
        result[f'ch{n}'].update(examples=src.count(r'\begin{origexamplebox}'),solutions=src.count(r'\begin{xesolution}'),qpdf=q.returncode,replacement_chars=txt.count('\ufffd'))
    result['source27']=render('source27',SOURCE,range(4,16))
    result['source28']=render('source28',SOURCE,range(17,31))
    crops={
      27:[(3,.30,.82),(4,.66,.88),(5,.75,.95),(6,.73,.96),(7,.61,.88),(8,.70,.91),(9,.28,.52),(10,.12,.35),(12,.32,.57),(13,.42,.72),(14,.42,.70),(16,.02,.37)],
      28:[(3,.72,.94),(4,.025,.20),(4,.72,.93),(5,.76,.95),(6,.72,.96),(7,.035,.24),(8,.025,.20),(9,.03,.33),(11,.71,.93),(12,.68,.90),(14,.61,.79),(15,.04,.28),(16,.36,.73)]}
    for n,entries in crops.items():
        d=fitz.open(result[f'ch{n}']['path'])
        for j,(p,top,bottom) in enumerate(entries,1):
            pg=d[p-1];clip=fitz.Rect(30,pg.rect.height*top,pg.rect.width-25,pg.rect.height*bottom)
            pg.get_pixmap(dpi=230,clip=clip,alpha=False).save(OUT/f'ch{n}'/f'detail-{j:02}.png')
    (OUT/'inspection-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
