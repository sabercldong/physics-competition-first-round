"""Replace the remaining eleven external theory diagrams with editable TikZ."""
from pathlib import Path
import re

BOOK=Path(__file__).resolve().parent.parent
MARKER="% TheoryTikZQuality20261023"
REPLACEMENTS={
 19:{"field-gallery":"ThTheoryFieldGallery","equipotentials":"ThTheoryEquipotentials",
     "zero-potential":"ThTheoryZeroPotential","ionization":"ThTheoryIonization",
     "quadrupole":"MeTheoryQuadrupole"},
 20:{"conductor-pair":"EmTheoryConductorPair","capacitor-pair":"EmTheoryCapacitorPair",
     "plate-edges":"EmTheoryPlateEdges","dielectric-sphere":"EmTheoryDielectricSphere",
     "grounded-sphere":"MeTheoryGroundedSphere","two-cylinders":"MeTheoryTwoCylinders"},
}
INPUTS={19:["ch19-gallery.tex","field-geometries.tex"],20:["ch20-conductors.tex","field-geometries.tex"]}

def apply_chapter_revision(number,text):
    if number not in REPLACEMENTS or MARKER in text:return text
    for name,macro in REPLACEMENTS[number].items():
        pattern=r"\\includegraphics\[([^]]+)\]\{[^}]*revision-ch19-ch20/"+re.escape(name)+r"\.pdf\}"
        def replace(match):
            width=re.search(r"(?:^|,)\s*width=([^,]+)",match[1])
            if not width:raise ValueError(f"missing width for {name}")
            return r"\resizebox{"+width[1]+"}{!}{\\"+macro+"}"
        text,count=re.subn(pattern,replace,text)
        if count!=1:raise ValueError(f"expected one theory diagram {number}/{name}, got {count}")
    chapter=re.search(r"\\chapter\{[^\n]+\}",text)
    inputs="\n"+"\n".join(r"\input{chapters/quality-20261023/theory-tikz/"+name+"}" for name in INPUTS[number])+"\n"
    return MARKER+"\n"+text[:chapter.end()]+inputs+text[chapter.end():]

if __name__=="__main__":
    for number in REPLACEMENTS:
        p=BOOK/f"generated/chapters/ch{number}.tex";old=p.read_text();new=apply_chapter_revision(number,old)
        if new!=old:p.write_text(new)
