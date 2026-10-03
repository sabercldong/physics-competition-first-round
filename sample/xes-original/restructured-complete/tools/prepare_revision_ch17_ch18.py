"""Mechanical source cleanup and deterministic water saturation plotting data."""
from pathlib import Path
import re,json,math
import numpy as np
from scipy.optimize import brentq
BOOK=Path(__file__).resolve().parent.parent
S=BOOK.parent/'thirty-first-section'
def brace(s,i):
 depth=0
 for j in range(i,len(s)):
  if s[j]=='{' and (j==0 or s[j-1]!='\\'):depth+=1
  if s[j]=='}' and (j==0 or s[j-1]!='\\'):
   depth-=1
   if depth==0:return j+1
 raise ValueError('unbalanced')
p=S/'diagrams.tex';s=p.read_text();r=(S/'diagrams-revised.tex').read_text()
names=re.findall(r'\\renewcommand\{(\\\w+)\}',r)
for name in names:
 marker=r'\newcommand{'+name+'}'
 if marker not in s:continue
 start=s.index(marker);b=s.index('{',start+len(marker));end=brace(s,b)
 s=s[:start]+s[end:]
s=s.replace(r'\input{diagrams-revised.tex}','').rstrip()+'\n\n'+r'\input{diagrams-revised.tex}'+'\n'
p.write_text(s)
(S/'diagrams-revised.tex').write_text(r.replace(r'\renewcommand',r'\newcommand'))
for name in ['content.tex','examples.tex']:
 p=S/name;t=p.read_text().replace(',{}',r'\,{}')
 if name=='examples.tex':
  # Condensation temperature and cloud height are not critical-point symbols.
  head,tail=t.split(r'\textbf{6. 凝结条件。}',1)
  tail=tail.replace('T_c','T_d').replace('z_c','z_d')
  t=head+r'\textbf{6. 凝结条件。}'+tail
  t=t.replace(r'\twoVesselsFigure',r'\twoVesselsFigure'+'\n'+r'\diagramcaption{冷热容器通过开放管口连通。}\label{s31:fig:vessels}')
  t=t.replace('细管使两端分压相同','在忽略热扩散、细管温差效应并采用普通气体扩散平衡的模型中，细管使两端分压相同')
 p.write_text(t)
# IAPWS saturation-pressure correlation; output kPa, temperature in Celsius.
def ps(t):
 T=t+273.15;tau=1-T/647.096
 coeff=[-7.85951783,1.84408259,-11.7866497,22.6807411,-15.9618719,1.80122502]
 powers=[1,1.5,3,3.5,4,7.5]
 return 22064*math.exp(647.096/T*sum(a*tau**b for a,b in zip(coeff,powers)))
pa=lambda t:(101-ps(10))*(t+273.15)/283.15
threshold=ps(120);lift=brentq(lambda t:ps(t)+pa(t)-threshold,70,100)
folder=BOOK/'assets/ch17';folder.mkdir(exist_ok=True)
(folder/'saturation.dat').write_text('t ps pa total\n'+'\n'.join(f'{t:.6f} {ps(t):.9f} {pa(t):.9f} {ps(t)+pa(t):.9f}' for t in sorted(set(np.arange(1,131,.5).tolist()+[lift,120]))))
p=S/'diagrams-revised.tex';t=p.read_text().replace('198.665399',f'{threshold:.9f}').replace('89.728776',f'{lift:.9f}');p.write_text(t)
out=BOOK/'build/revision-ch17-ch18-20260920';out.mkdir(exist_ok=True)
(out/'water-data.json').write_text(json.dumps({'correlation':'IAPWS saturation pressure','p10_kPa':ps(10),'p120_kPa':threshold,'lift_C':lift},indent=2))
print(lift,threshold)
