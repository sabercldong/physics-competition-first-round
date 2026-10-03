"""Mechanical extraction replacement, restricted to seven named figures."""
from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'chapters/new/ch32-modern.tex'
s=p.read_text()
names=['blackbody','compton','bragg','hydrogen','binding','fusion','decay']
labels=['blackbody','compton','electron-diffraction','hydrogen-levels','binding-curve','fusion-q','decay-chain']
for name,label in zip(names,labels):
    pattern=r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}(?=\s*\\figcap\{[^\n]*?\\label\{ch32:fig:'+label+r'\})'
    # Tempered pattern must not consume earlier unrelated figures.
    pattern=pattern.replace('.*?',r'(?:(?!\\end\{tikzpicture\})[\s\S])*?')
    s,n=re.subn(pattern,lambda m:'\\input{../../assets/diagrams-modern/'+name+'.tex}',s)
    assert n==1,(name,n)
p.write_text(s)
