"""Deterministic streamlines: sphere meridian and circular-cylinder potential flow."""
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'assets/ch13';OUT.mkdir(parents=True,exist_ok=True)
checks={}
for name,R,levels in [('sphere',1.2,[.35,.75,1.2,1.75]),('cylinder',2.2,[.25,.65,1.1,1.65])]:
 lines=[];maxerr=0;mingap=100
 previous=None
 for b in levels:
  coords=[]
  for j in range(181):
   x=-4+8*j/180
   lo=max(0,math.sqrt(max(0,R*R-x*x)));hi=6.
   def psi(y):
    r=math.hypot(x,y)
    return y*y*(1-R**3/r**3) if name=='sphere' else y*(1-R*R/(r*r))
   target=b*b if name=='sphere' else b
   for _ in range(65):
    mid=(lo+hi)/2
    if psi(mid)<target:lo=mid
    else:hi=mid
   y=(lo+hi)/2;coords.append((x,y));maxerr=max(maxerr,abs(psi(y)-target))
  if previous:mingap=min(mingap,min(p[1]-q[1] for p,q in zip(coords,previous)))
  previous=coords
  for sign in ([1,-1] if name=='sphere' else [1]):
   style='Blue,thick'
   lines.append('\\draw['+style+'] plot[smooth] coordinates {'+' '.join(f'({x:.6f},{sign*y:.6f})' for x,y in coords)+'};')
   j=148 if name=='sphere' else 32
   start,end=(coords[j-3],coords[j+3]) if name=='sphere' else (coords[j+3],coords[j-3])
   lines.append('\\draw[Blue,thick,->] '+f'({start[0]:.6f},{sign*start[1]:.6f})--({end[0]:.6f},{sign*end[1]:.6f});')
 (OUT/f'{name}-paths.tex').write_text('\n'.join(lines)+'\n')
 checks[name]={'streamfunction_max_error':maxerr,'minimum_adjacent_meridian_gap':mingap,'R':R,'levels':levels}
(OUT/'geometry.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
