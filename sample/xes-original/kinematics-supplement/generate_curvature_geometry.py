"""Deterministic C2 reconstruction of the folded curve in source physical p59.

The spline is a geometric realization of a qualitative drawing, not an inferred
physical law. Osculating circles use this exact spline and its derivatives.
"""
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline

ROOT=Path(__file__).resolve().parent
t=np.array([0,1,2,2.7,3,3.4,4,5,6.])
xy=np.array([[-2.8,1.4],[0,0],[1.45,1.55],[2.65,2.65],[3,2.65],
             [2.75,2.3],[2.52,1.3],[3.45,.4],[4.75,.3]])
s=CubicSpline(t,xy,bc_type='natural')
def point(p): return '('+','.join(f'{x:.8f}' for x in p)+')'
path=point(xy[0])
for i in range(len(t)-1):
    dt=t[i+1]-t[i]
    p1=s(t[i])+s(t[i],1)*dt/3
    p2=s(t[i+1])-s(t[i+1],1)*dt/3
    path+='\n ..controls '+point(p1)+' and '+point(p2)+'..'+point(xy[i+1])
records=[]
for number,time in enumerate([1,2,3,4],1):
    p=s(time);v=s(time,1);a=s(time,2)
    cross=float(v[0]*a[1]-v[1]*a[0])
    centre=p+np.dot(v,v)/cross*np.array([-v[1],v[0]])
    radius=np.linalg.norm(centre-p)
    assert abs(np.dot(centre-p,v))<1e-10
    records.append(dict(n=number,t=time,point=p.tolist(),derivative=v.tolist(),
                        centre=centre.tolist(),radius=float(radius),curvature=float(cross/np.linalg.norm(v)**3)))
header=r'''% Figure contract: source example 2.69, physical p59; simple geometry, mode C.
% Reading order: broad valley P1 -> ascending P2 -> sharp turn P3 -> P4 left-below P3.
% Preserve the folded topology, not a single-valued y(x) hill. No artistic smoothing of labels.
% Layout: full curve spans x=-2.8..4.75, y=0..2.8, 10cm final width; labels >=9pt.
% Question: only curve and P1..P4. Answer: circles derived from same C2 spline.
% Blue physical curve, thin grey circle arcs, white paper, all labels transparent.
% Expected collision: tiny circle P3 / label; label offset above-right; P4 left.
% No decorative panels. Circle arcs may intersect remote curve segments legitimately.
% Sketch:  \___P1__/P2__/P3
%                            /P4\___
'''
out=[header,r'\newcommand{\FoldedCurvePath}{'+path+'}\n',r'\newcommand{\FoldedCurvePoints}{%']
for r,pos in zip(records,['below left','above left','above right','left']):
    out.append(r'\node[point,label={[label distance=3pt]'+pos+':{$P_'+str(r['n'])+r'$}}] at '+point(r['point'])+' {};')
out += ['}\n',r'\newcommand{\FoldedCurveCircles}{%',r'\begin{scope}',r'\clip (-3.0,-1.1) rectangle (5,3.9);']
for r in records:
    out.append(r'\draw[TextGray,thin] '+point(r['centre'])+' circle ('+f"{r['radius']:.8f}"+');')
out += [r'\end{scope}','}\n']
zoom=records[2]
out += [r'\newcommand{\FoldedCurveTipZoom}{%',r'\begin{scope}[scale=10]',r'\clip (2.88,2.54) rectangle (3.08,2.78);',r'\draw[kcurve] \FoldedCurvePath;',r'\draw[TextGray,thin] '+point(zoom['centre'])+' circle ('+f"{zoom['radius']:.8f}"+');',r'\end{scope}','}\n']
(ROOT/'data/folded-curvature.tex').write_text('\n'.join(out))
(ROOT/'data/folded-curvature.json').write_text(json.dumps({'method':'C2 parametric cubic spline','knots':t.tolist(),'points':xy.tolist(),'circles':records,'checks':{'P4_left_of_P3':records[3]['point'][0]<records[2]['point'][0],'P4_below_P3':records[3]['point'][1]<records[2]['point'][1],'normal_dot_tangent_zero':True}},indent=2))
print(json.dumps(records,indent=2))
