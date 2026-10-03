"""Emit an apply_patch patch; this program never writes the teaching files."""
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[4]
LEGACY=ROOT/'sample/xes-original'
updates={}
def diagram(name,code): updates[name]=code.strip()

diagram('probdiagThreeOne',r'''
\begin{tikzpicture}[scale=.78]
 \draw[solbody] (-2.8,1.2)--(0,1.2)--(0,-1.2)--(3,-1.2);
 \draw[DeepBlue,line width=1pt] (-1.8,1.22)--(.9,1.22);
 \draw[solbody,fill=SoftGray] (-.82,1.24) rectangle (-.08,1.85);
 \node[sollabel] at (-.45,1.55) {铁块};
 \draw[solflow] (.3,1.65)--(1.5,1.65) node[midway,above=3pt,sollabel] {$v$：抽纸速度};
 \node[sollabel] at (1.4,.96) {纸条};
 \draw[solbody,fill=SoftGray] (1.65,-1.2) rectangle (2.35,-.62);
 \node[sollabel] at (2,-.35) {$P$};
\end{tikzpicture}''')
diagram('soldiagThreeOne',r'''
\begin{tikzpicture}[scale=.78]
 \draw[solbody] (-1.1,2.2)--(0,2.2)--(0,0);
 \draw[axis] (0,0)--(6.7,0) node[right,sollabel] {$x$};
 \draw[curve,domain=0:1,samples=60] plot ({3*\x},{2.2*(1-\x*\x)});
 \draw[TextGray,line width=.9pt,domain=0:1,samples=60] plot ({5.5*\x},{2.2*(1-\x*\x)});
 \draw[solflow] (0,2.2)--(1.3,2.2) node[midway,above=4pt,sollabel] {$v_x$};
 \node[sollabel,below=4pt] at (3,0) {$O$：抽速 $2v$};
 \node[sollabel,below=4pt] at (5.5,0) {$P$：抽速 $v$};
 \node[sollabel] at (3.1,3.05) {$I_f=f\tau$；接触时间较短，离桌速度较小};
\end{tikzpicture}''')
diagram('probdiagThreeFour',r'''
\begin{tikzpicture}[scale=.78]
 \begin{scope}[rotate=25]
  \draw[solbody] (-3,0)--(3.2,0);
  \draw[solbody,fill=SoftGray] (-2.2,0) rectangle (-1.25,.7);
  \draw[solbody,fill=SoftGray] (.35,0) rectangle (1.3,.7);
  \draw[DeepBlue] (-1.25,.35)--(.35,.35);
  \node[sollabel,rotate=0] at (-1.725,.35) {$A$};
  \node[sollabel,rotate=0] at (.825,.35) {$B$};
  \draw[solforce] (1.3,.35)--(2.8,.35) node[midway,above=4pt,sollabel] {$F$};
 \end{scope}
\end{tikzpicture}''')
diagram('soldiagThreeFour',r'''
\begin{tikzpicture}[x=1cm,y=.53cm]
 \draw[axis] (0,0)--(5.7,0) node[right,sollabel] {$t$};
 \draw[axis] (0,0)--(0,8) node[above,sollabel] {$v$};
 % Illustrative ratio m_A=m_B and t_2=t_1; all slopes share these parameters.
 \draw[curve] (0,0)--(2,2);
 \draw[curve] (2,2)--(4,0);
 \draw[TextGray,line width=.9pt] (2,2)--(4,8);
 \draw[solgeom] (0,2)--(2,2)--(2,0) (4,0)--(4,8);
 \node[sollabel,left=4pt] at (0,2) {$at_1$};
 \node[sollabel,below=4pt] at (2,0) {$t_1$};
 \node[sollabel,below=4pt] at (4,0) {$t_1+t_2$};
 \node[sollabel,anchor=west] at (4.15,7.3) {$B$：$a_B>a$};
 \node[sollabel,anchor=west] at (4.15,1.2) {$A$：减速至零};
\end{tikzpicture}''')
diagram('soldiagThreeFive',r'''
\begin{tikzpicture}[scale=.8]
 \node[solpanel] at (-2.4,1.6) {碰前};
 \node[solpanel] at (2.4,1.6) {碰后};
 \draw[solbody,fill=SoftGray] (-3.5,-.35) rectangle (-2.6,.35);
 \draw[solbody,fill=SoftGray] (-1.8,-.35) rectangle (-.9,.35);
 \node[sollabel] at (-3.05,0) {$A$}; \node[sollabel] at (-1.35,0) {$B$};
 \draw[solbody,fill=SoftGray] (1,-.35) rectangle (1.9,.35);
 \draw[solbody,fill=SoftGray] (2.6,-.35) rectangle (3.5,.35);
 \node[sollabel] at (1.45,0) {$A$}; \node[sollabel] at (3.05,0) {$B$};
 \draw[solimpulse] (-3.5,.85)--(-.9,.85) node[midway,above=3pt,sollabel] {$P_i=m_Av_0$};
 \draw[solimpulse] (1,.85)--(3.6,.85) node[midway,above=3pt,sollabel] {$P_f=P_i$};
 \node[sollabel] at (0,-1.05) {以上箭头表示系统总动量；$I_x^{\rm ext}=0$};
\end{tikzpicture}''')
diagram('probdiagThreeSix',r'''
\begin{tikzpicture}[scale=.85]
 \coordinate (A) at (-2.4,.8); \coordinate (B) at (0,.8);
 \coordinate (C) at ($(B)+(-60:2.4)$);
 \draw[solbody] (A)--(B)--(C); \draw[solgeom] (B)--++(1.8,0);
 \draw[TextGray] ($(B)+(0:.65)$) arc (0:-60:.65);
 \draw[TextGray] ($(B)+(180:.5)$) arc (180:300:.5);
 \foreach \p in {A,B,C}{\fill[Ink] (\p) circle (2.5pt);}
 \node[sollabel,above=7pt] at (A) {$A$}; \node[sollabel,above=7pt] at (B) {$B$};
 \node[sollabel,below=6pt] at (C) {$C$};
 \node[sollabel] at (.95,.34) {$60^\circ$}; \node[sollabel] at (-.8,.05) {$120^\circ$};
 \draw[solimpulse] (A)--++(-1.1,0) node[midway,above=4pt,sollabel] {$I$};
\end{tikzpicture}''')
diagram('soldiagThreeSix',r'''
\begin{tikzpicture}[scale=.85]
 \coordinate (A) at (-2.7,1); \coordinate (B) at (0,1);
 \coordinate (C) at ($(B)+(-60:2.7)$);
 \draw[solgeom] (A)--(B)--(C);
 \foreach \p in {A,B,C}{\fill[Ink] (\p) circle (2.4pt);}
 \node[sollabel,below=8pt] at (A) {$A$}; \node[sollabel,above=7pt] at (B) {$B$};
 \node[sollabel,below=7pt] at (C) {$C$};
 \draw[solimpulse] (A)--++(-1.05,0) node[midway,above=4pt,sollabel] {$I$};
 \draw[solimpulse] (A)--++(.95,0) node[midway,above=4pt,sollabel] {$J_1$};
 \draw[solimpulse] (B)--++(-.95,0) node[midway,above=4pt,sollabel] {$J_1$};
 \draw[solimpulse] (B)--++(-60:1) node[midway,right=5pt,sollabel] {$J_2$};
 \draw[solimpulse] (C)--++(120:1) node[midway,right=5pt,sollabel] {$J_2$};
 \draw[solflow] (2.4,.7)--++(-60:.85) node[right=4pt,sollabel] {$\hat{\boldsymbol u}$};
 \draw[solflow] (2.4,.7)--++(.95,0) node[right=3pt,sollabel] {$+x$};
\end{tikzpicture}''')
diagram('soldiagThreeSeven',r'''
\begin{tikzpicture}[scale=.82]
 % g=1, v0=2, theta=45 degrees, wall at s0=2.5 in drawing units.
 \coordinate (Q) at (2.5,.9375);
 \draw[solbody] (-.3,0)--(2.5,0)--(2.5,2.8);
 \draw[curve,domain=0:2.5,samples=60] plot ({\x},{\x-\x*\x/4});
 \draw[solflow] (0,0)--(45:1.1) node[above left=3pt,sollabel] {$v_0$};
 \draw[TextGray] (.5,0) arc (0:45:.5); \node[sollabel] at (.85,.22) {$\theta$};
 \draw[<->,TextGray] (0,-.45)--(2.5,-.45) node[midway,below=3pt,sollabel] {$s_0$};
 \fill[Ink] (Q) circle (2pt) node[below left=5pt,sollabel] {$Q$};
 \draw[solflow] (2.5,1.05)--(2.5,2.3);
 \node[sollabel,anchor=west] at (2.7,2.25) {蹬后竖直上升};
 \begin{scope}[shift={(5.2,1.2)}]
  \fill[Ink] (0,0) circle (2.5pt);
  \draw[solimpulse] (0,0)--(-1.1,0) node[midway,below=4pt,sollabel] {$J_N$};
  \draw[solimpulse] (0,0)--(0,1.2) node[right=4pt,sollabel] {$J_f$};
  \node[sollabel] at (0,-.65) {接触冲量，单独画出};
 \end{scope}
\end{tikzpicture}''')
diagram('probdiagThreeEight',r'''
\begin{tikzpicture}[scale=.8]
 \coordinate (O) at (-.5,1.4); \coordinate (S) at (-2,-.4);
 \coordinate (A) at ({-.5+2.8*1.5/1.8},-1.4);
 \coordinate (B) at ({-.5+2.8*1.5/1.8+.7},-1.4);
 \draw[solbody] (-3,1.4)--(3.1,1.4) (-3,-1.4)--(3.1,-1.4);
 \draw[TextGray,line width=.8pt] (S)--(O)--(A);
 \draw[curve] (O)--(B);
 \draw[solflow] (S)--($(S)!.45!(O)$) node[midway,above left=3pt,sollabel] {$\vec v$};
 \draw[solgeom] (O)--(-.5,-1.4);
 \foreach \p in {O,S,A,B}{\fill[Ink] (\p) circle (2pt);}
 \node[sollabel,above=5pt] at (O) {$O$}; \node[sollabel,left=5pt] at (S) {$S$};
 \node[sollabel,below=5pt] at (A) {$A$}; \node[sollabel,below=5pt] at (B) {$B$};
 \draw[<->,TextGray] (-3.35,-1.4)--(-3.35,1.4) node[midway,left=4pt,sollabel] {$d$};
 \node[sollabel] at (0,2.05) {俯视；本图取摩擦冲量向右};
\end{tikzpicture}''')
diagram('soldiagThreeEight',r'''
\begin{tikzpicture}[scale=.8]
 \coordinate (O) at (-1,1.2); \coordinate (A) at (.2,-1.2); \coordinate (B) at (1.4,-1.2);
 \draw[solbody] (-2,1.2)--(2,1.2) (-2,-1.2)--(2,-1.2);
 \draw[TextGray] (O)--(A); \draw[curve] (O)--(B);
 \node[sollabel,above=5pt] at (O) {$O$};
 \node[sollabel,below=3pt] at (A) {$A$}; \node[sollabel,below=3pt] at (B) {$B$};
 \draw[solgeom] (A)--(.2,-1.9) (B)--(1.4,-1.9);
 \draw[<->,DeepBlue] (.2,-1.8)--(1.4,-1.8) node[midway,below=4pt,sollabel] {$AB=|\Delta v_t|d/v_n$};
 \begin{scope}[shift={(4,0)}]
  \fill[Ink] (0,.6) circle (2pt);
  \draw[solimpulse] (0,.6)--(0,-.55) node[midway,left=4pt,sollabel] {$J_N$};
  \draw[solimpulse] (0,.6)--(1.2,.6) node[midway,above=4pt,sollabel] {$J_t$};
  \node[sollabel,align=center] at (.35,-1.25) {持续滑动时\\$J_t=\mu J_N$};
 \end{scope}
\end{tikzpicture}''')
diagram('soldiagThreeNine',r'''
\begin{tikzpicture}[scale=.82]
 \draw[solbody,fill=SoftGray] (1.2,-1.1) rectangle (1.9,1.1);
 \draw[solflow] (-2.5,.5)--(1.2,.5) node[pos=.35,above=4pt,sollabel] {$v_{\rm in}=v$};
 \draw[solflow] (1.2,-.5)--(-2.5,-.5) node[pos=.65,below=4pt,sollabel] {$v_{\rm out}=-v$};
 \node[sollabel] at (-.1,1.75) {飞船系：碰前、碰后路线分行示意};
 \draw[solforce] (1.6,-1.6)--(3,-1.6) node[midway,below=4pt,sollabel] {$F=2\rho Sv^2$};
 \node[sollabel] at (2.55,.45) {迎流面};
\end{tikzpicture}''')
diagram('soldiagThreeTen',r'''
\begin{tikzpicture}[scale=.8]
 \coordinate (T) at (-1,0);
 \fill[SoftGray] (-4,1.2)--(T)--(-4,-1.2)--cycle;
 \draw[solgeom] (-4,-1.2) arc (-90:90:.25 and 1.2);
 \draw[solbody] (-4,1.2) arc (90:270:.25 and 1.2);
 \draw[solbody] (-4,1.2)--(T)--(-4,-1.2);
 \draw[solgeom] (-4.4,0)--(-.65,0);
 \foreach \y in {-.7,.7}{\draw[solflow] (-.1,\y)--({-1-abs(\y)/.4},\y);}
 \draw[<->,TextGray] (-4,-1.65)--(-1,-1.65) node[midway,below=4pt,sollabel] {$L$};
 \draw[<->,TextGray] (-4.55,0)--(-4.55,1.2) node[midway,left=3pt,sollabel] {$R$};
 \node[solpanel] at (-2.5,2.6) {空间外形：平行来流};
 \begin{scope}[shift={(1.4,0)}]
  \pgfmathsetmacro{\ang}{atan(.4)}
  \coordinate (P) at (3,0); \coordinate (Q) at (1.2,.72);
  \draw[solbody] (0,1.2)--(P)--(0,-1.2);
  \draw[solgeom] (-.2,0)--(3.5,0);
  \draw[solflow] (3.3,.72)--(Q) node[pos=.35,above=4pt,sollabel] {$\vec v_{\rm in}$};
  \draw[solflow] (Q)--++({180-2*\ang}:1.4) node[above left=3pt,sollabel] {$\vec v_{\rm out}$};
  \draw[solgeom,->] (Q)--++({90-\ang}:1.15) node[above right=3pt,sollabel] {$\hat{\boldsymbol n}$};
  \draw[TextGray] (2.35,0) arc (180:{180-\ang}:.65);
  \node[sollabel] at (2.15,.15) {$\alpha$};
  \node[sollabel] at (1.5,-1.7) {$R=L\tan\alpha$};
 \end{scope}
 \node[solpanel] at (2.9,2.6) {轴截面：法向分量反向};
\end{tikzpicture}''')
diagram('soldiagThreeTwelve',r'''
\begin{tikzpicture}[scale=.8]
 \coordinate (O) at (-1.4,0); \coordinate (S) at (1.4,0);
 \draw[solgeom] (O) circle (2.8);
 \draw[solbody,fill=SoftGray] (O) circle (.45);
 \node[sollabel] at (-1.4,0) {太阳};
 \foreach \a in {-18,0,18}{\draw[solflow] ($(O)+(\a:.5)$)--($(O)+(\a:2.8)$);}
 \draw[solbody,line width=1.3pt] (1.4,-.4)--(1.4,.4);
 \draw[solforce] (1.4,0)--(2.65,0) node[midway,above=4pt,sollabel] {$F$};
 \node[sollabel,anchor=west] at (1.65,-.7) {小接收面 $S$，正入射};
 \draw[solgeom] (-1.4,-.5)--(-1.4,-1.4) (1.4,-.4)--(1.4,-1.4);
 \draw[<->,TextGray] (-1.4,-1.35)--(1.4,-1.35) node[midway,below=4pt,sollabel] {$r$：球心到接收面中心};
 \node[sollabel] at (-1.3,3.3) {虚线球面的面积 $4\pi r^2$};
\end{tikzpicture}''')

diagram('soldiagThreeFourteen',r'''
\begin{tikzpicture}[scale=.8]
 \draw[solbody] (-3.2,0)--(3.2,0);
 \foreach \x/\m in {-2.25/1,-.75/2,.75/3,2.25/4}{
  \draw[solbody,fill=SoftGray] (\x,.25) circle (.25);
  \node[sollabel] at (\x,.85) {$m_{\m}$};}
 \node[sollabel] at (0,1.6) {$\sum_i m_i\dot x_i=0\ \Longrightarrow\ \dot x_C=0$};
 \node[sollabel] at (0,-.45) {各球仅在水平面内运动};
\end{tikzpicture}''')
for name in ['probdiagThreeFifteen','soldiagThreeFifteen']:
 diagram(name,r'''
\begin{tikzpicture}[scale=.85]
 \pgfmathsetmacro{\ell}{3} \pgfmathsetmacro{\half}{40}
 \pgfmathsetmacro{\span}{2*\ell*sin(\half)}
 \pgfmathsetmacro{\xL}{-3*\span/8} \pgfmathsetmacro{\xH}{\span/8}
 \pgfmathsetmacro{\xR}{5*\span/8} \pgfmathsetmacro{\yH}{\ell*cos(\half)}
 \coordinate (L) at (\xL,0); \coordinate (H) at (\xH,\yH); \coordinate (R) at (\xR,0);
 \draw[axis] (-2.1,0)--(3.15,0) node[right,sollabel] {$x$};
 \draw[solbody] (L)--(H)--(R);
 \foreach \p in {L,H,R}{\fill[Ink] (\p) circle (2.5pt);}
 \node[sollabel,below=6pt] at (L) {$L,2m$}; \node[sollabel,below=6pt] at (R) {$R,m$};
 \node[sollabel,above=6pt] at (H) {$H,m$};
 \node[sollabel,left=7pt] at ($(L)!.5!(H)$) {$l$};
 \node[sollabel,right=7pt] at ($(R)!.5!(H)$) {$l$};
 \draw[solgeom] (H)--(\xH,0);
 \draw[TextGray] ($(H)+(-130:.65)$) arc (-130:-50:.65);
 \node[sollabel] at (\xH,{\yH-1}) {$\theta$};
 \fill[DeepBlue] (0,{\yH/4}) circle (2pt) node[left=7pt,sollabel] {$C$};
 \draw[solgeom] (0,0)--(0,{\yH/4});
 \node[sollabel,below=6pt] at (0,0) {$O$};
 \draw[solgeom] (L)--(\xL,-.9) (R)--(\xR,-.9);
 \draw[<->,TextGray] (\xL,-.85)--(\xR,-.85) node[midway,below=4pt,sollabel] {$2l\sin(\theta/2)$};
 \node[sollabel] at (.5,-1.6) {$x_C=0$；$C$ 的高度随杆张开而改变};
\end{tikzpicture}''')
diagram('soldiagThreeSixteen',r'''
\begin{tikzpicture}[scale=.8]
 \node[solpanel] at (-2.5,3) {碰前动量};
 \fill[Ink] (-2.3,1.6) circle (2.5pt);
 \draw[solimpulse] (-3.8,1.6)--(-2.3,1.6) node[midway,above=5pt,sollabel] {$mv$};
 \draw[solimpulse] (-2.3,1.6)--(-2.3,.35) node[midway,left=5pt,sollabel] {$Mu$};
 \node[solpanel] at (2.4,3) {碰后：$V_x>0,\ V_y>0$（向下）};
 \coordinate (Q) at (.3,2.2);
 \draw[curve,domain=0:1,samples=70] plot ({.3+2.8*\x},{2.2-.9*\x-1.3*\x*\x});
 \draw[solflow] (Q)--(1.42,2.2) node[midway,above=5pt,sollabel] {$V_x$};
 \draw[solflow] (Q)--(.3,1.84) node[left=6pt,sollabel] {$V_y$};
 \draw[solgeom] (Q)--(.3,0);
 \draw[solbody] (-.1,0)--(3.7,0);
 \draw[<->,DeepBlue] (.3,-.45)--(3.1,-.45) node[midway,below=4pt,sollabel] {$l=V_xT$};
 \fill[Ink] (3.1,0) circle (2pt);
\end{tikzpicture}''')
diagram('soldiagThreeSeventeen',r'''
\begin{tikzpicture}[scale=.82]
 \coordinate (C) at (.5,0);
 \draw[decorate,decoration={coil,segment length=5pt,amplitude=3pt},line width=.8pt] (-2.5,0)--(2.5,0);
 \fill[Ink] (-2.5,0) circle (2.5pt); \fill[Ink] (2.5,0) circle (2.5pt);
 \node[sollabel] at (-2.5,.7) {$m_1$}; \node[sollabel] at (2.5,.7) {$m_2$};
 \draw[solgeom] (C)--(.5,.6); \node[sollabel] at (.5,1) {$C$：固定材料点};
 \draw[solgeom] (-2.5,-.2)--(-2.5,-.8) (C)--(.5,-.8) (2.5,-.2)--(2.5,-.8);
 \draw[<->,TextGray] (-2.5,-.65)--(.5,-.65) node[midway,below=4pt,sollabel] {$L_1$};
 \draw[<->,TextGray] (.5,-.65)--(2.5,-.65) node[midway,below=4pt,sollabel] {$L_2$};
 \node[sollabel] at (0,-1.4) {$m_1L_1=m_2L_2$};
\end{tikzpicture}''')
diagram('soldiagThreeEighteen',r'''
\begin{tikzpicture}[scale=.92]
 % Example mass ratio M=m. Circle and trajectory share R, theta and X.
 \pgfmathsetmacro{\rad}{2} \pgfmathsetmacro{\ang}{35}
 \pgfmathsetmacro{\X}{\rad/2*(1-sin(\ang))}
 \coordinate (C) at (\X,\rad);
 \coordinate (A) at ({\X+\rad*sin(\ang)},{\rad*(1-cos(\ang))});
 \draw[axis] (-2.4,0)--(3.1,0) node[right,sollabel] {$x$};
 \draw[axis] (0,-.45)--(0,3.1) node[above,sollabel] {$y$};
 \draw[solgeom] (-2,2) arc (180:360:2);
 \draw[solbody] ({\X-2},2) arc (180:360:2);
 \draw[curve,domain=90:35,samples=70] plot ({1+sin(\x)},{2*(1-cos(\x))});
 \draw[solgeom] (C)--(A) (C)--(\X,0);
 \draw[TextGray] ($(C)+(-90:.5)$) arc (-90:-55:.5);
 \node[sollabel] at ({\X+.25},1.25) {$\theta$};
 \node[sollabel,right=6pt] at ($(C)!.65!(A)$) {$R$};
 \fill[Ink] (A) circle (2.5pt) node[right=7pt,sollabel] {$A$};
 \fill[Ink] (2,2) circle (2pt) node[above right=5pt,sollabel] {$A_0$};
 \node[sollabel,below left=5pt] at (0,0) {$O$};
 \draw[solgeom] (0,2)--(0,2.6) (C)--(\X,2.6);
 \draw[<->,TextGray] (0,2.5)--(\X,2.5) node[midway,above=4pt,sollabel] {$X$};
 \node[sollabel] at (.2,-.9) {虚线为初始碗；实线为当前碗；蓝线为对地轨迹};
\end{tikzpicture}''')

common={'soldiagThreeNineteen':'momentumRain','soldiagThreeTwentyFour':'momentumRain',
 'soldiagThreeTwenty':'momentumPickup','soldiagThreeTwentyFive':'momentumPickup',
 'probdiagThreeTwentyOne':'momentumFallingRope','probdiagThreeTwentySix':'momentumFallingRope',
 'soldiagThreeTwentyOne':'momentumRopeLoad','soldiagThreeTwentySix':'momentumRopeLoad',
 'soldiagThreeTwentyTwo':'momentumAccretion','soldiagThreeTwentySeven':'momentumAccretion',
 'soldiagThreeTwentyThree':'momentumDroplet','soldiagThreeTwentyEight':'momentumDroplet'}
for key,value in common.items(): updates[key]='\\'+value

diagram('rocketMicroDiagram',r'''
\begin{tikzpicture}[scale=.77]
 \node[solpanel] at (-2.8,1.5) {喷气前}; \node[solpanel] at (2.6,1.5) {喷气后};
 \draw[solbody,fill=SoftGray] (-4,-.35) rectangle (-2,.35);
 \node[sollabel] at (-3,0) {$M$};
 \draw[solflow] (-2,0)--(-.7,0) node[midway,above=4pt,sollabel] {$v$};
 \draw[solbody,fill=SoftGray] (1.4,-.35) rectangle (3.4,.35);
 \node[sollabel] at (2.4,0) {$M+\Delta M$};
 \draw[solflow] (3.4,0)--(4.7,0) node[midway,above=4pt,sollabel] {$v+\Delta v$};
 \foreach \x in {-.2,.2,.6}{\fill[TextGray] (\x,0) circle (2pt);}
 \node[sollabel] at (.2,.75) {燃气 $-\Delta M$};
 \draw[solflow] (.65,-.95)--(-.65,-.95) node[midway,below=4pt,sollabel] {$-u$：相对火箭};
 \node[sollabel] at (.2,-1.8) {燃气对地速度为 $v-u$，可以向左、为零或向右};
\end{tikzpicture}''')
diagram('soldiagThreeTwentyNine',r'''
\begin{tikzpicture}[scale=.82]
 \draw[axis] (0,0)--(5.2,0) node[right,sollabel] {$\mathcal M$};
 \draw[axis] (0,0)--(0,3.7) node[above,sollabel] {$V$};
 \draw[curve,domain=.6:4.4,samples=80] plot ({\x},{1+ln(4.4/\x)});
 \draw[curve,-{Latex[length=2mm]},domain=3.4:2.4,samples=20] plot ({\x},{1+ln(4.4/\x)});
 \draw[solgeom] (0,1)--(4.4,1)--(4.4,0);
 \node[sollabel,left=4pt] at (0,1) {$v$}; \node[sollabel,below=4pt] at (4.4,0) {$M$};
 \node[sollabel,anchor=west] at (2.5,3.2) {$V=v+u\ln(M/\mathcal M)$};
 \node[sollabel,anchor=west] at (2.5,2.6) {燃烧方向：沿曲线向左上方};
\end{tikzpicture}''')
diagram('soldiagThreeThirty',r'''
\begin{tikzpicture}[scale=.82]
 \draw[axis] (0,0)--(5.8,0) node[right,sollabel] {$\mathcal M$};
 \draw[axis] (0,0)--(0,3.8) node[above,sollabel] {$u/\mathcal M$};
 \path[fill=Blue!12] (1.5,0)--plot[domain=1.5:4.6,samples=50] (\x,{2.1/\x})--(4.6,0)--cycle;
 \draw[curve,domain=.6:5.1,samples=80] plot (\x,{2.1/\x});
 \draw[solgeom] (1.5,0)--(1.5,1.4) (4.6,0)--(4.6,{2.1/4.6});
 \node[sollabel,below=4pt] at (1.5,0) {$M$}; \node[sollabel,below=4pt] at (4.6,0) {$M_0$};
 \node[sollabel] (L) at (3.8,2.5) {阴影面积 $u\ln(M_0/M)$};
 \draw[TextGray] (L.south)--(3,.4);
 \draw[solflow] (4.6,-.65)--(1.5,-.65) node[midway,below=4pt,sollabel] {质量减少的方向};
\end{tikzpicture}''')
diagram('soldiagFourFifteen',r'''
\begin{tikzpicture}[scale=.85]
 \draw[axis] (0,0)--(6.6,0) node[right,sollabel] {$r$};
 \draw[axis] (0,0)--(0,2.7) node[above,sollabel] {能量};
 \draw[curve,domain=.6:5.4,samples=80] plot ({\x},{.35*(\x-3)^2});
 \draw[TextGray,line width=.8pt] (.45,1.12)--(5.75,1.12);
 \draw[solgeom] (1.21115,0)--(1.21115,1.12) (4.78885,0)--(4.78885,1.12);
 \node[sollabel,above=4pt] at (5.7,1.12) {$E_{\rm rel}$};
 \node[sollabel] at (3,2.45) {$U(r)=\frac12k(r-l_0)^2$};
 \node[sollabel,below=4pt] at (1.21115,0) {$r_{\min}$};
 \node[sollabel,below=4pt] at (3,0) {$l_0$};
 \node[sollabel,below=4pt] at (4.78885,0) {$r_{\max}$};
\end{tikzpicture}''')
diagram('soldiagFourSixteen',r'''
\begin{tikzpicture}[scale=.8]
 \node[solpanel] at (0,2.6) {下物块 $B$ 的临界受力图};
 \draw[solbody,fill=SoftGray] (-.4,-.35) rectangle (.4,.35);
 \draw[solbody] (-1.2,-.35)--(1.2,-.35);
 \draw[solforce] (0,0)--(0,1.7) node[above=4pt,sollabel] {$T=k(x-l_0)$};
 \draw[solforce] (0,0)--(0,-1.7) node[below=4pt,sollabel] {$m_2g$};
 \node[sollabel,right=5pt] at (.4,0) {$B$};
 \node[sollabel,anchor=west,align=left] at (2,1)
   {临界时 $N=0$\\$T=m_2g$\\$x_{\rm c}=l_0+m_2g/k$};
\end{tikzpicture}''')
diagram('probdiagFourEighteen',r'''
\begin{tikzpicture}[scale=.9]
 \coordinate (A) at (0,0); \coordinate (B) at (.64,.48);
 \draw[solgeom] (-2.4,0)--(1.9,0);
 \draw[solbody,fill=SoftGray] (A) circle (.4);
 \draw[solbody,fill=SoftGray] (B) circle (.4);
 \draw[solgeom] (A)--(B);
 \node[sollabel,below=15pt] at (A) {$A$}; \node[sollabel,above=15pt] at (B) {$B$};
 \draw[solflow] (-2.1,0)--(-.5,0) node[midway,above=5pt,sollabel] {$\vec v_0$};
 \node[sollabel] at (.2,1.6) {俯视：接触瞬间；圆心连线为法线};
\end{tikzpicture}''')
diagram('soldiagFourEighteen',r'''
\begin{tikzpicture}[scale=.85]
 \coordinate (O) at (0,0); \coordinate (A) at (3,0); \coordinate (B) at (3,2);
 \draw[solforce] (O)--(A) node[midway,below=5pt,sollabel] {$\vec v_A$};
 \draw[solforce] (A)--(B) node[midway,right=7pt,sollabel] {$\vec v_B$};
 \draw[solforce] (O)--(B) node[midway,above left=4pt,sollabel] {$\vec v_0$};
 \draw[TextGray] (2.72,0)--(2.72,.28)--(3,.28);
 \node[sollabel,anchor=west,align=left] at (4.2,1)
  {动量：首尾相接\\动能：交叉项为零\\两非零速度互相垂直};
\end{tikzpicture}''')
diagram('probdiagFourNineteen',r'''
\begin{tikzpicture}[scale=.8]
 \begin{scope}[rotate=20]
  \draw[solbody] (-3,0)--(3,0);
  \draw[solbody,fill=SoftGray] (1.1,0) rectangle (2,.65);
  \draw[solgeom] (-2.2,0) rectangle (-1.3,.65);
  \draw[solgeom] (-1.75,.8)--(-1.75,1.55) (1.55,.8)--(1.55,1.55);
  \draw[<->,TextGray] (-1.75,1.45)--(1.55,1.45) node[midway,above=4pt,sollabel] {$L$};
  \draw[solforce] (1.55,.325)--(2.85,.325) node[above right=5pt,sollabel] {$f$};
  \draw[solflow] (.8,.75)--(-.4,.75) node[midway,above=4pt,sollabel] {下滑};
 \end{scope}
 \coordinate (Q) at ({-3*cos(20)},{-3*sin(20)});
 \draw[TextGray] (Q)--++(1.1,0);
 \draw[TextGray] ($(Q)+(.7,0)$) arc (0:20:.7);
 \node[sollabel] at ($(Q)+(1.1,.23)$) {$\theta$};
\end{tikzpicture}''')
diagram('probdiagFourTwenty',r'''
\begin{tikzpicture}[scale=.78]
 \draw[solbody] (-3.8,0)--(3.8,0) (-3.6,0)--(-3.6,1.4);
 \draw[solgeom] (-.45,0) rectangle (.45,.8);
 \draw[decorate,decoration={coil,segment length=5pt,amplitude=3pt}] (-3.6,.4)--(1.55,.4);
 \draw[solbody,fill=SoftGray] (1.55,0) rectangle (2.45,.8);
 \draw[solgeom] (0,-.65)--(0,1.15) (2,-.65)--(2,1.15);
 \draw[<->,TextGray] (0,-.5)--(2,-.5) node[midway,below=4pt,sollabel] {$a$};
 \node[sollabel,above=4pt] at (0,1.15) {$O$：自然长度时的中心};
 \draw[solflow] (2,1.3)--(.9,1.3) node[above=4pt,sollabel] {释放后向左};
\end{tikzpicture}''')

def argument(text,start):
    assert text[start]=='{'
    level=1; i=start+1
    while level:
        if text[i]=='{': level+=1
        elif text[i]=='}': level-=1
        i+=1
    return text[start+1:i-1],i

directory=sys.argv[1]
path=LEGACY/directory/'diagrams.tex'
old=path.read_text()
assert r'\label{ch07:fig:' not in old, 'Already converted; do not reapply.'
matches=list(re.finditer(r'\\newcommand\{\\((?:probdiag|soldiag|rocketMicro)[A-Za-z]*)\}\{',old))
new=old[:matches[0].start()]
new=new.replace('fill=white,inner sep=1pt','fill=none,inner sep=1pt')
cap_start=new.index(r'\newcommand{\diagcaption}')
new=new[:cap_start]+r'''\newcommand{\diagcaption}[2]{%
 \refstepcounter{figure}\par\nopagebreak[4]\smallskip
 {\centering\scriptsize\color{TextGray}图~\thefigure\quad #2\par}\smallskip}
'''
if directory in ('eighth-section','ninth-section'):
    new+=r'\input{../momentum-common-diagrams.tex}'+'\n'
calls={}
captions={
 'soldiagThreeFour':r'断线后 $B$ 的斜率增大；图取 $m_A=m_B,\ t_2=t_1$ 显示相同定性关系。',
 'soldiagThreeNine':r'飞船系中的入射与原路反弹分别列示；飞船所受反作用力沿来流方向。',
 'soldiagThreeEight':r'左右两部分分别表示落点偏移和接触冲量，不能把冲量箭头当作轨迹。',
 'soldiagThreeTwelve':r'距离从太阳中心量起，接收面中心落在半径 $r$ 的球面上。',
 'soldiagThreeEighteen':r'圆心、接触点和轨迹使用同一组参数；图取 $M=m$，一般关系见推导。',
 'soldiagFourSixteen':r'离地瞬间只保留弹力和重力；支持力降为零。',
}
for j,m in enumerate(matches):
    name=m.group(1)
    block=old[m.end():matches[j+1].start() if j+1<len(matches) else len(old)]
    p=block.index(r'\diagcaption')+len(r'\diagcaption')
    kind,p=argument(block,p); cap,p=argument(block,p)
    cap=captions.get(name,cap)
    if name in updates: code=updates[name]
    else:
        start=block.index(r'\begin{tikzpicture}')
        end=block.index(r'\end{tikzpicture}')+len(r'\end{tikzpicture}')
        code=block[start:end]
    label='ch07:fig:'+name
    new+='\n'+'\\newcommand{\\'+name+'}{%\n'+r'\begin{center}\begin{minipage}{.97\linewidth}\centering'+'\n'+code+'\n'
    new+=r'\diagcaption{'+kind+'}{'+cap+'}'+r'\label{'+label+r'}\end{minipage}\end{center}}'+'\n'
    calls[name]=(label,cap)

# A numbered reference directly precedes each figure invocation, with the
# physical relation stated in the caption instead of a free-standing decoration.
content=LEGACY/directory/'content.tex'
before=content.read_text(); after=before
for name,(label,cap) in calls.items():
    call='\\'+name
    assert re.search(r'^'+re.escape(call)+r'\s*$',after,re.M), name
    sentence='图~\\ref{'+label+'}'+('给出题设的几何关系。' if name.startswith('prob') else '中的关系与上述推导相对应。')
    # Prefer replacing an existing nearby figure-introduction sentence.
    after=re.sub(r'(?m)^'+re.escape(call)+r'\s*$',lambda _:sentence+'\n'+call,after)

patch='*** Begin Patch\n'
for p,a,b in [(path,old,new),(content,before,after)]:
    patch+='*** Update File: '+str(p)+'\n@@\n'
    patch+=''.join('-'+line+'\n' for line in a.splitlines())
    patch+=''.join('+'+line+'\n' for line in b.splitlines())
patch+='*** End Patch\n'
print(patch)
