"""Rebuild editable TikZ paths from exact electrostatic first integrals.

Contour vertices are retained as TikZ coordinates, not raster/PDF inclusions.
Analytic circles, ellipses and hyperbolas remain analytic TikZ plots.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FOLDER = Path(__file__).resolve().parent
CHECKS = {}


def simplify(points, tolerance=.006):
    """Ramer--Douglas--Peucker, preserving every segment endpoint."""
    if len(points) < 3:
        return points
    a, b = points[0], points[-1]
    delta = b-a
    if np.dot(delta, delta) < 1e-20:
        distances = np.linalg.norm(points-a, axis=1)
    else:
        fraction = np.clip((points-a)@delta/np.dot(delta, delta), 0, 1)
        distances = np.linalg.norm(points-a-fraction[:, None]*delta, axis=1)
    index = int(np.argmax(distances))
    if distances[index] <= tolerance:
        return points[[0, -1]]
    return np.vstack((simplify(points[:index+1], tolerance)[:-1],
                      simplify(points[index:], tolerance)))


def coords(points):
    return " ".join(f"({x:.5f},{y:.5f})" for x, y in points)


def contours(x, y, values, levels, style, field=None):
    figure, axes = plt.subplots()
    result = axes.contour(x, y, values, levels=levels)
    output = []
    for level, segments in zip(result.levels, result.allsegs):
        for segment in segments:
            if len(segment) < 12:
                continue
            output.append(r"\draw[" + style + "] plot coordinates{" + coords(simplify(segment)) + "};")
            if field is not None:
                i = int(.55*(len(segment)-1))
                first, last = segment[max(0, i-2)], segment[min(len(segment)-1, i+2)]
                direction = last-first
                if np.linalg.norm(direction) < 1e-6:
                    continue
                middle = (first+last)/2
                if np.dot(direction, field(*middle)) < 0:
                    direction = -direction
                direction = .10*direction/np.linalg.norm(direction)
                output.append(r"\draw[->,"+style+"] "+coords([middle-direction])+"--"+coords([middle+direction])+";")
    plt.close(figure)
    return "\n".join(output)


def unequal():
    # Q/q=4 gives x0=3 a0, visible on the same coordinate window.
    X,Y=np.meshgrid(np.linspace(-3.5,5.3,801), np.linspace(-2.8,2.8,601))
    rp=np.hypot(X+1,Y); rm=np.hypot(X-1,Y)
    flux=4*(X+1)/np.maximum(rp,1e-20)-(X-1)/np.maximum(rm,1e-20)
    mask=(rp<.10)|(rm<.10)
    def field(x,y):
        p=np.hypot(x+1,y);m=np.hypot(x-1,y)
        return np.array([4*(x+1)/p**3-(x-1)/m**3,4*y/p**3-y/m**3])
    body=contours(X,Y,np.ma.masked_where(mask,flux),[-2.6,-1.8,-1.,-.2,.6,1.4,2.2,2.8,3.25,3.7,4.15,4.6],"DeepBlue,line width=.65pt",field)
    CHECKS['unequal-zero-field-residual']=float(np.linalg.norm(field(3,0)))
    return r"""\newcommand{\ThUnequalAnalysisDrawing}{\begin{tikzpicture}[>=Latex,font=\small,x=.9cm,y=.9cm]
\begin{scope}\clip(-3.5,-2.8)rectangle(5.3,2.8);
"""+body+r"""
\draw[->,TextGray](-3.5,0)--(5.3,0);
\end{scope}
\fill[DeepBlue](-1,0)circle(3pt)node[below=4pt]{$+Q$};\fill(1,0)circle(3pt)node[below=4pt]{$-q$};
\fill[Gold](3,0)circle(2pt);\draw[Gold](3,.1)--(4.2,1.35)node[above,align=center]{$E=0$\\$x_0=3a_0$};
\draw[->,Gold](3.12,0)--(3.55,0);\draw[->,Gold](2.88,0)--(2.45,0);
\draw[->,Gold](3,.85)--(3,.4);\draw[->,Gold](3,-.85)--(3,-.4);
\node[below]at(.5,-3.05){图示 $Q=4q,\ a_0=1$；蓝线方向由 $+Q$ 出发，金色箭头示零场点的局部鞍形结构};
\end{tikzpicture}}
"""


def dipole():
    # In-plane polar axis along p, e_theta counterclockwise from +x.
    return r"""\newcommand{\ThDipoleAnalysisDrawing}{\begin{tikzpicture}[>=Latex,font=\small,x=.85cm,y=.85cm]
\draw[->](-.9,0)--(3.3,0)node[right]{$\vect p$};\fill(-.5,0)circle(2pt)node[below]{$-q$};\fill[DeepBlue](.5,0)circle(2pt)node[below]{$+q$};
\coordinate(P)at({2.5*cos(40)},{2.5*sin(40)});\draw[dashed](0,0)--(P)node[midway,above left]{$r$};\fill(P)circle(1.5pt)node[below right]{$P$};
\draw(.8,0)arc(0:40:.8)node[right]{$\theta$};
\draw[->,DeepBlue,thick](P)--++({cos(40)},{sin(40)})node[right]{$E_r$};
\draw[->,Gold,thick](P)--++({-.41955*sin(40)},{.41955*cos(40)})node[above left]{$E_\theta$};
\draw[->,thick](P)--++({cos(40)-.41955*sin(40)},{sin(40)+.41955*cos(40)})node[above]{$\vect E$};
\node[below]at(1.2,-.8){远场分解：$E_r/E_\theta=2\cot\theta$};
\begin{scope}[shift={(7,0)}]
\foreach\C in {1,2,3}{
 \draw[DeepBlue,thick,domain=1:179,samples=140]plot({\C*sin(\x)*sin(\x)*cos(\x)},{\C*sin(\x)*sin(\x)*sin(\x)});
 \draw[DeepBlue,thick,domain=359:181,samples=140]plot({\C*sin(\x)*sin(\x)*cos(\x)},{\C*sin(\x)*sin(\x)*sin(\x)});
 \draw[->,DeepBlue] (.12,\C)--(-.12,\C);\draw[->,DeepBlue](.12,-\C)--(-.12,-\C);
}
\fill(0,0)circle(2pt);\draw[->,thick](0,0)--(.7,0)node[right]{$\vect p$};
\node[above]at(0,3.4){点偶极子：$r=C\sin^2\theta$};
\end{scope}\end{tikzpicture}}
"""


def line_families():
    return r"""\newcommand{\ThTwoLinesAnalysisDrawing}{\begin{tikzpicture}[>=Latex,font=\small,x=1cm,y=1cm]
\begin{scope}\clip(-4,-2.7)rectangle(4,2.7);
\foreach\C in {1.4,2,3}{\pgfmathsetmacro{\c}{1.5*(\C*\C+1)/(\C*\C-1)}\pgfmathsetmacro{\R}{3*\C/(\C*\C-1)}\draw[DeepBlue](-\c,0)circle(\R);\draw[DeepBlue](\c,0)circle(\R);}
\draw[DeepBlue](0,-2.7)--(0,2.7);
\foreach\d in {-2,-.7,0,.7,2}{\pgfmathsetmacro{\R}{sqrt(2.25+\d*\d)}\draw[TextGray,dashed](0,\d)circle(\R);\draw[->,TextGray](.12,{\d+\R})--(-.12,{\d+\R});\draw[->,TextGray](.12,{\d-\R})--(-.12,{\d-\R});}
\draw[TextGray,dashed](-4,0)--(4,0);\draw[->,TextGray](.2,0)--(-.2,0);
\end{scope}
\fill(-1.5,0)circle(3pt)node[below=4pt]{$-\lambda$};\fill[DeepBlue](1.5,0)circle(3pt)node[below=4pt]{$+\lambda$};
\fill(0,1.5)circle(1.5pt)node[above right]{$P$};\draw(0,1.25)--(-.25,1.25)--(-.25,1.5);
\node[below,align=center]at(0,-3){实线：$r_-/r_+=C$；虚线：$x^2+(y-d)^2=a^2+d^2$\\电荷位置 $x=\pm a$；在 $P=(0,a)$ 可直接检验两族切向正交};
\end{tikzpicture}}
"""


def rod():
    a=1.5
    CHECKS['rod-ellipse-focus-residual']=max(abs(A*A-(np.sqrt(A*A-a*a))**2-a*a)for A in[1.75,2.2,2.9,3.7])
    return r"""\newcommand{\ThFiniteRodAnalysisDrawing}{\begin{tikzpicture}[>=Latex,font=\small,x=1cm,y=1cm]
\begin{scope}\clip(-4,-2.7)rectangle(4,2.7);
\foreach\A in {1.75,2.2,2.9,3.7}{\pgfmathsetmacro{\B}{sqrt(\A*\A-2.25)}\draw[DeepBlue](0,0)ellipse({\A} and {\B});}
\foreach\eta in {-.92,-.7,-.4,0,.4,.7,.92}{\foreach\sign in {-1,1}{
 \draw[TextGray,dashed,domain=1:3.5,samples=100]plot({1.5*\x*\eta},{\sign*1.5*sqrt((\x*\x-1)*(1-\eta*\eta))});
 \draw[->,TextGray]({1.5*1.3*\eta},{\sign*1.5*sqrt((1.3*1.3-1)*(1-\eta*\eta))})--({1.5*1.4*\eta},{\sign*1.5*sqrt((1.4*1.4-1)*(1-\eta*\eta))});
}}
\end{scope}\draw[very thick](-1.5,0)--(1.5,0);\fill(-1.5,0)circle(2pt)node[below=4pt]{$-a$};\fill(1.5,0)circle(2pt)node[below=4pt]{$a$};
\node[below,align=center]at(0,-3){实线：$r_++r_-=2a\xi$（椭圆）；虚线：$r_--r_+=2a\eta$（双曲线）\\$\lambda>0$ 时箭头沿增大的 $\xi$ 向外，两个端点是共同焦点};
\end{tikzpicture}}
"""


def scattering():
    output=[]
    errors=[]
    B0=.7
    for b,color in[(.65,'DeepBlue'),(1.4,'Gold'),(2.6,'TextGray')]:
        theta=2*np.arctan(B0/b); e=np.sqrt(1+(b/B0)**2); alpha=np.arccos(1/e);p=b*b/B0
        psi=np.linspace(alpha-.0001,-alpha+.0001,10000)
        r=p/(e*np.cos(psi)-1);angle=np.pi/2+theta/2+psi
        x=r*np.cos(angle);y=r*np.sin(angle)
        mask=(x>-7)&(x<6.3)&(y<6)&(y>-1)
        xy=np.column_stack((x[mask],y[mask]))
        output.append(r'\draw[thick,'+color+'] plot coordinates{'+coords(simplify(xy,.004))+'};')
        i=int(len(xy)*.72);v=xy[min(len(xy)-1,i+3)]-xy[max(0,i-3)];v=.16*v/np.linalg.norm(v)
        output.append(r'\draw[->,'+color+']'+coords([xy[i]-v])+'--'+coords([xy[i]+v])+';')
        tangent=np.array([np.cos(theta),np.sin(theta)]);normal=np.array([-np.sin(theta),np.cos(theta)])
        output.append(r'\draw[dashed,'+color+'](-7,'+str(b)+')--(-3.5,'+str(b)+');')
        outgoing=np.array([b*normal+u*tangent for u in[-1,9]])
        output.append(r'\draw[densely dotted,'+color+']'+coords(outgoing[:1])+'--'+coords(outgoing[1:])+';')
        q=np.linspace(-alpha*.98,alpha*.98,501);den=e*np.cos(q)-1;rr=p/den;dr=p*e*np.sin(q)/den**2
        angular=-b/rr**2;vr=dr*angular;vt=rr*angular
        errors.append(float(np.max(abs(.5*(vr*vr+vt*vt)+B0/rr-.5))))
    CHECKS['rutherford-energy-residual']=errors
    return r"""\newcommand{\ThRutherfordAnalysisDrawing}{\begin{tikzpicture}[>=Latex,font=\small,x=.65cm,y=.65cm]
\begin{scope}\clip(-7,-1)rectangle(6.3,6);
"""+'\n'.join(output)+r"""
\end{scope}\fill(0,0)circle(4pt)node[below right]{$+Ze$};
\draw[<->,Gold](-5.2,0)--node[left]{$b$}(-5.2,1.4);\draw[dashed](-5.4,0)--(0,0);
\draw[->,DeepBlue,thick](-6.5,-.7)--(-4.5,-.7)node[midway,below]{$\vect v_\infty$};
\begin{scope}[shift={(2,-1.7)}]\draw[->,Gold](0,0)--(2.5,0);\draw[->,Gold](0,0)--({2.5*cos(53.1301)},{2.5*sin(53.1301)});\draw[Gold](1,0)arc(0:53.1301:1)node[right]{$\Theta$};\end{scope}
\node[below]at(-4.5,-2.4){\textcolor{DeepBlue}{$b=0.65$}};\node[below]at(0,-2.4){\textcolor{Gold}{$b=1.4$}};\node[below]at(4.5,-2.4){\textcolor{TextGray}{$b=2.6$}};
\node[below]at(0,-3.1){同一 $B_0=\kappa/(2E_k)=0.7$；所有渐近线与各自双曲线使用同一尺度};
\end{tikzpicture}}
"""


def sphere():
    X,Y=np.meshgrid(np.linspace(-3.2,3.2,801),np.linspace(-2,2,601));r=np.maximum(np.hypot(X,Y),1e-20)
    potential=-X+X/r**3;flux=.5*Y**2*(1+2/r**3);mask=r<1.002
    def field(x,y):
        rr=np.hypot(x,y)
        return np.array([1+3*x*x/rr**5-1/rr**3,3*x*y/rr**5])
    body=contours(X,Y,np.ma.masked_where(mask,potential),[-2,-1.3,-.6,0,.6,1.3,2],"TextGray,dashed,line width=.55pt")
    body+='\n'+contours(X,Y,np.ma.masked_where(mask,flux),[.06,.18,.4,.7,1.,1.4,2.,2.6],"DeepBlue,line width=.7pt",field)
    angle=np.linspace(0,2*np.pi,1001);s=np.sin(angle);c=np.cos(angle)
    E=np.array([3*c*c,3*c*s]).T;tangent=np.array([-s,c]).T
    CHECKS['conducting-sphere-tangential-E-residual']=float(np.max(abs((E*tangent).sum(axis=1))))
    return r"""\newcommand{\ThUniformSphereAnalysisDrawing}{\begin{tikzpicture}[>=Latex,font=\small,x=1.15cm,y=1.15cm]
\begin{scope}\clip(-3.2,-2)rectangle(3.2,2);
"""+body+r"""
\end{scope}
\fill[DeepBlue!6](0,0)circle(1);\draw[thick](0,0)circle(1);\node at(0,0){$E=0$};
\foreach\ang in {-60,-30,0,30,60}{\node at({.88*cos(\ang)},{.88*sin(\ang)}){$+$};\node at({-.88*cos(\ang)},{.88*sin(\ang)}){$-$};}
\draw[->,DeepBlue,thick](-3,2.3)--(-1.9,2.3)node[midway,above]{$\vect E_0$};\draw[->](1.8,-2.35)--(3,-2.35)node[right]{$+z$};
\node[below,align=center]at(-.3,-2.25){$r=R$：$\varphi=0,\ E_\theta=0$\\$\sigma=3\varepsilon_0E_0\cos\theta$};
\node[above]at(.7,2.15){蓝实线为场线；灰虚线为等势线};
\end{tikzpicture}}
"""


if __name__ == '__main__':
    (FOLDER/'electrostatic-analysis-ch19.tex').write_text('% Deterministic editable paths; see make_electrostatic_tikz.py.\n'+unequal()+dipole()+line_families()+rod()+scattering())
    (FOLDER/'electrostatic-analysis-ch20.tex').write_text('% Deterministic editable paths; see make_electrostatic_tikz.py.\n'+sphere())
    (FOLDER/'electrostatic-tikz-checks.json').write_text(json.dumps(CHECKS,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(CHECKS,ensure_ascii=False,indent=2))
