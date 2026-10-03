"""Emit a patch that attaches physical explanations to numbered figure refs."""
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[4]/'sample/xes-original'
def arg(t,i):
    assert t[i]=='{'
    start=i+1; depth=1; i+=1
    while depth:
        if t[i]=='{':depth+=1
        elif t[i]=='}':depth-=1
        i+=1
    return t[start:i-1],i
directory=sys.argv[1]; p=ROOT/directory/'content.tex'
old=p.read_text(); new=old
d=(ROOT/directory/'diagrams.tex').read_text()
for m in re.finditer(r'\\newcommand\{\\((?:probdiag|soldiag|rocketMicro)[A-Za-z]*)\}',d):
    name=m[1]; i=d.index('\\diagcaption{',m.end())+len('\\diagcaption')
    _,i=arg(d,i); cap,i=arg(d,i)
    reference='图~\\ref{ch07:fig:'+name+'}'
    generic=reference+('给出题设的几何关系。' if name.startswith('prob') else '中的关系与上述推导相对应。')
    assert generic in new,(p,name)
    pos=new.index(generic)
    preceding=new[max(0,pos-100):pos]
    if '见解图' in preceding:
        j=new.rfind('见解图',max(0,pos-100),pos)
        new=new[:j]+'见'+reference+new[j+3:pos]+new[pos:].replace(generic,'',1)
    else:
        new=new.replace(generic,reference+'中，'+cap,1)
print('*** Begin Patch\n*** Update File: '+str(p)+'\n@@\n'+
      ''.join('-'+l+'\n' for l in old.splitlines())+
      ''.join('+'+l+'\n' for l in new.splitlines())+'*** End Patch')
