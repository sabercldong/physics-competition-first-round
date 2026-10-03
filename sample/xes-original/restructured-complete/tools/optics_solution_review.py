"""Auditable additions inside existing solutions; never silently replace one."""
import re
from pathlib import Path

# Stable question label, literal insertion anchor, side, reviewed text block.
INSERTIONS={
27:[
 ('ch27:ex:s42-19-2',r'\begin{xesolution}','after','mirror-domain'),
 ('ch27:ex:s42-19-2','利用 $\\dot\\theta=\\omega$ 求导','before','mirror-simplify'),
 ('ch27:ex:s42-19-9',r'\begin{xesolution}','after','plate-reference'),
 ('ch27:ex:s42-19-12','大量邻近光线','before','rainbow-turns'),
 ('ch27:ex:s42-19-12','对水的可见光折射率代入','before','rainbow-angles'),
 ('ch27:ex:s42-19-5',r'\begin{xesolution}','after','gradient-geometry'),
 ('ch27:ex:s42-19-8',r'\begin{xesolution}','after','circular-ray-proof'),
 ('ch27:ex:s42-19-8',r'\end{xesolution}','before','circular-ray-domain'),
],
28:[
 ('ch28:ex:s43-20-1','小明到像的总距离化简为','before','ball-second-surface'),
 ('ch28:ex:s43-20-1',r'\end{xesolution}','before','ball-parallel-limit'),
 ('ch28:ex:s43-20-2','同一物点发出的不同倾角光必须','before','matrix-meaning'),
 ('ch28:ex:s43-20-7',r'\begin{xesolution}','after','cat-eye-reference'),
],
}

def additions(number):
    if number not in INSERTIONS:return {}
    p=Path(__file__).resolve().parents[1]/f'chapters/new/optics-depth/review-solutions-ch{number}.tex'
    text=p.read_text();pattern=r'%<addition:([^>]+)>\n(.*?)%</addition>'
    blocks=dict(re.findall(pattern,text,re.S))
    assert len(blocks)==text.count('%<addition:')
    assert not re.sub(r'(?m)^%[^\n]*','',re.sub(pattern,'',text,flags=re.S)).strip()
    assert set(blocks)=={x[3] for x in INSERTIONS[number]}
    return blocks

def apply(number,text):
    blocks=additions(number)
    for label,anchor,side,key in INSERTIONS.get(number,[]):
        start=text.index(r'\label{'+label+'}')
        end=text.index(r'\end{xesolution}',start)+len(r'\end{xesolution}')
        question=text[start:end]
        assert question.count(anchor)==1,(label,key,anchor)
        at=start+question.index(anchor)+(len(anchor) if side=='after' else 0)
        extra='\n%<optics-review:'+key+'>\n'+blocks[key]+'\n%</optics-review:'+key+'>\n'
        text=text[:at]+extra+text[at:]
    return text

def strip_additions(text):
    # Round trip is verified byte-for-byte by the staging gate. Added teaching
    # material can be excluded from retention tests without exempting old text.
    return re.sub(r'\n%<optics-review:([^>]+)>\n.*?\n%</optics-review:\1>\n','',text,flags=re.S)
