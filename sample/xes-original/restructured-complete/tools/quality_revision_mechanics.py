"""Mechanics editorial overlay (2026-10-23), with editable per-problem TikZ.

apply_chapter_revision is deliberately independent of the main generator.  The
CLI applies only this module's owned chapters and is idempotent.  Existing
question/solution drawings are retained unless an explicit correction says so.
"""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parent.parent
MARKER = "% MechanicsQualityRevision20261023-v1"
REFERENCE_MARKER = "% MechanicsNumberedSolutionFigures20261023-v1"
BLOCK = re.compile(r"(\\begin\{origexamplebox\}\{[^\n]*?\})(.*?)(\\end\{origexamplebox\}.*?\\begin\{xesolution\})(.*?)(\\end\{xesolution\})", re.S)


def figure(label, caption, body):
    return "\n\\begin{qualityfigure}\n\\begin{tikzpicture}[>=Latex,font=\\small]\n" + body.replace("Accent", "Gold") + "\n\\end{tikzpicture}\n\\figcap{" + caption + "}\\label{" + label + "}\n\\end{qualityfigure}\n"


# The drawings below describe the actual geometry, coordinates, boundaries and
# stages of their individual problems.  Q never contains the requested result.
def _scene(kind, answer=False):
    a = answer
    if kind == "oscillation":
        return r"""\draw[->] (0,0)--(7,0) node[right]{$t$};
\draw[->] (0,-1.1)--(0,1.35) node[above]{$x$};
\draw[DeepBlue,thick,domain=0:6.5,samples=130] plot(\x,{cos(180*\x)});
\draw[<->] (.2,1.15)--(2.2,1.15) node[midway,above]{$T$};
\draw[dashed] (0,1)--(6.5,1);
\node[left] at (0,1){$A$};
\draw[Accent,thick] (.65,-1)--(1.35,-1) node[right]{$v=0$};"""
    if kind == "samples":
        b = r"""\draw[->] (0,0)--(6.6,0) node[right]{$t/\mathrm s$};
\draw[->] (0,-2.2)--(0,1) node[above]{$x$};
\draw[DeepBlue,thick,domain=0:6,samples=70] plot(\x,{(20*\x-5*\x*\x)/30});
\foreach \t in {0,.5,...,6} {\fill (\t,{(20*\t-5*\t*\t)/30}) circle(1.2pt);}
\draw[dashed] (2,0)--(2,.667) node[above]{$t=2$};"""
        return b + (r"\draw[Accent,very thick] (3,.5)--(3.5,.292);\draw[<->] (3,-.3)--(3.5,-.3) node[midway,below]{$\Delta t$};\node[above right] at (3,.5){$\Delta x<0$};" if a else "")
    if kind == "headon":
        b = r"""\draw[->] (-.5,0)--(7,0) node[right]{$x$};
\fill (0,0) circle(2pt) node[below]{$A_0:-5\,\mathrm m$};
\fill (6,0) circle(2pt) node[below]{$B_0:10\,\mathrm m$};
\draw[->,thick,DeepBlue] (0,.4)--(1.8,.4) node[midway,above]{$1.5\,\mathrm{m/s}$};
\draw[->,thick,Accent] (6,.4)--(5,.4) node[midway,above]{$0.5\,\mathrm{m/s}$};"""
        return b + (r"\fill (4.5,0) circle(2pt) node[above=12pt]{$P$};\draw[<->] (0,-.9)--(4.5,-.9) node[midway,below]{$1.5t$};\draw[<->] (4.5,-.9)--(6,-.9) node[midway,below]{$0.5t$};" if a else "")
    if kind in ("vtarea", "notime"):
        b = r"""\draw[->] (0,0)--(5,0) node[right]{$t$};
\draw[->] (0,0)--(0,3) node[above]{$v$};
\draw[DeepBlue,thick] (0,.9)--(4,2.5);
\node[left] at (0,.9){$v_0$};\draw[dashed] (4,0) node[below]{$t$}--(4,2.5) node[above]{$v$};"""
        if kind == "notime":
            b = b.replace("$v_0$", "$v_1$").replace("node[below]{$t$}", "node[below]{$\\Delta t$}").replace("(4,2.5) node[above]{$v$}", "(4,2.5) node[above]{$v_2$}")
        return (r"\fill[PaleBlue] (0,0)--(4,0)--(4,2.5)--(0,.9)--cycle;" if a else "") + b + (r"\draw[dashed] (0,.9)--(4,.9);\node at (2,.45){$v_0t$};\node at (2.9,1.4){$\frac12at^2$};" if a and kind == "vtarea" else (r"\node at (2,.7){$x_2-x_1$};" if a else ""))
    if kind == "train":
        b = r"""\draw[->] (-1,0)--(7,0) node[right]{$x$};
\draw[thick,fill=PaleBlue] (0,.25) rectangle (5,.85);
\node at (.5,.55){尾};\node at (2.5,.55){中};\node at (4.5,.55){头};
\draw[->] (5.3,.55)--(6.5,.55) node[midway,above]{$v$};
\draw[<->] (0,1.25)--(5,1.25) node[midway,above]{$L$};
\fill (5,0) circle(2pt) node[below]{$O$};"""
        return b + (r"\draw[<->,Accent] (0,-.65)--(2.5,-.65) node[midway,below]{$L/2$};\draw[<->,Accent] (2.5,-.65)--(5,-.65) node[midway,below]{$L/2$};\node[align=center] at (2.5,-1.6){同一标志点依次前移 $0,L/2,L$\\对应速率 $v_1,v,v_2$};" if a else "")
    if kind == "junction":
        b = r"""\draw[thick] (-.3,0)--(6.7,0);\draw[very thick] (6,-.6)--(6,1);
\node[above] at (6,1){路口};\draw[fill=PaleBlue] (0,.1) rectangle (1,.65);
\draw[->] (1.2,.4)--(2.5,.4) node[midway,above]{$v_0$};
\draw[<->] (.5,-.55)--(6,-.55) node[midway,below]{$60\,\mathrm m$};
\node at (3.5,1.2){倒计时 $2\,\mathrm s$};"""
        return b + (r"\draw[->,DeepBlue] (1.3,1.6)--(2.8,1.6) node[right]{$a_{\rm pass}$};\draw[->,Accent] (2.8,2.25)--(1.3,2.25) node[left]{$a_{\rm stop}$};" if a else "")
    if kind in ("rearend", "pursuit"):
        b = r"""\draw[->] (-.3,0)--(7,0) node[right]{$x$};
\fill (0,0) circle(2pt) node[below]{$A$};\fill (3,0) circle(2pt) node[below]{$B$};
\draw[->,DeepBlue,thick] (0,.4)--(1.5,.4) node[above]{$v_A$};
\draw[->,Accent,thick] (3,.4)--(4,.4) node[above]{$v_B$};
\draw[<->] (0,-.6)--(3,-.6) node[midway,below]{$d$};"""
        if kind == "rearend":
            b = b.replace("$v_A$", "$20$").replace("$v_B$", "$10$").replace("{$d$}", "{$100\\,\\mathrm m$}")
            return b + (r"\draw[->,Accent] (1.5,1.2)--(0,1.2) node[midway,above]{$a$};\node[align=center] at (4.5,1.6){间距最小时\\$v_A=v_B$};" if a else "")
        return b + r"\draw[very thick] (6,-.3)--(6,.8) node[above]{$x=L$};" + (r"\node[align=center] at (3,1.5){$r=x_B-x_A$\\$r(t_*)=0$};\draw[->] (2.2,1.1)--(2.2,.1);" if a else "")
    if kind == "vertical":
        b = r"""\foreach \x/\v/\name in {0/0/静放,2.8/+10/上抛,5.6/-10/下抛}{
\draw[->] (\x,-1.8)--(\x,1.7) node[above]{$x$};
\fill (\x,0) circle(2pt) node[left]{$O$};
\node[below] at (\x,-2){\name};\node[right] at (\x,.2){$v_0=\v$};}
\draw[->,DeepBlue] (3.2,.5)--(3.2,1.3);
\draw[->,DeepBlue] (6,.5)--(6,-.5);
\draw[->,Accent] (7,1.3)--(7,.3) node[midway,right]{$g$};"""
        return b + (r"\node[align=center] at (2.8,-3.3){同一坐标约定：$a=-g$\\$x=v_0t-gt^2/2$};" if a else "")
    if kind == "heights":
        b = r"""\draw[->] (0,0)--(5.6,0) node[right]{$t$};
\draw[->] (0,-1.3)--(0,2) node[above]{$x$};
\draw[DeepBlue,thick,domain=0:5,samples=70] plot(\x,{(20*\x-5*\x*\x)/15});
\foreach \yy/\lab in {1/15,1.333/20,1.667/25,-1.667/-25}{\draw[dashed] (0,\yy)--(5,\yy);\node[left] at (0,\yy){$\lab$};}"""
        return b + (r"\foreach \t in {1,3}{\fill (\t,1) circle(2pt);\draw[dashed] (\t,0)--(\t,1);}\draw[dashed] (2,0)--(2,1.333);\node[below] at (2,0){$2$};\node[above right] at (3,1){同一高度的两次通过};" if a else "")
    if kind == "superman":
        b = r"""\draw[thick] (-.5,2)--(2.5,2);\node[left] at (-.5,2){楼顶 $O$};
\draw[thick] (-.5,-1.5)--(6,-1.5) node[right]{地面};
\draw[->] (0,2)--(0,-1.8) node[below]{$y$};
\draw[<->] (-.8,2)--(-.8,-1.5) node[midway,left]{$H$};
\fill (1,1) circle(2pt) node[right]{女子（先出发 $T$）};
\fill (1,2) circle(2pt);\draw[->,DeepBlue] (1.4,1.9)--(1.4,1.3) node[right]{$v_0$};"""
        return b + (r"\draw[<->,Accent] (4,2)--(4,1) node[midway,right]{$gT^2/2$};\node[align=center] at (3.5,-.7){剩余时间 $t_f-T$\\相对加速度为零};" if a else "")
    if kind == "return":
        b = r"""\draw[very thick] (0,-.5)--(0,1.8) node[above]{固定板};
\draw[->] (0,0)--(6.2,0) node[right]{$x$};
\fill (1.5,.35) circle(2pt);\draw[->,DeepBlue] (1.5,.35)--(2.7,.35) node[right]{$v_0$};
\draw[->,Accent] (2.7,1.1)--(1.5,1.1) node[midway,above]{$a_n$};"""
        return b + (r"\fill (4.5,0) circle(2pt) node[above]{$v=0$};\draw[<->] (0,-.6)--(4.5,-.6) node[midway,below]{$x_{\max,n}$};\draw[->,DeepBlue] (4.3,-1.2)--(.3,-1.2) node[midway,below]{返回路程与去程相同};" if a else "")
    if kind == "strobe":
        return r"""\draw[thick] (0,3)--(0,0)--(2,0)--(2,3);
\draw[dashed] (0,2.7)--(2,2.7);\fill (1,2.7) circle(2pt) node[right]{$H$};
\fill[DeepBlue] (1,1.1) circle(2pt);\draw[<->] (2.4,0)--(2.4,1.1) node[midway,right]{$h$};
\draw[->] (.65,2.2)--(.65,1.5);\draw[->] (1.35,.4)--(1.35,1.2);
\node[align=left] at (5,1.8){拍摄时刻 $t_0+nT$\\同一高度可对应上行、下行};"""
    if kind in ("displacement", "subtract"):
        b=r"""\coordinate (A) at (0,0);\coordinate (B) at (2.5,2);\coordinate (C) at (5,.5);
\foreach \p/\t in {A/A(t_1),B/B(t_2),C/C(t_3)}{\fill (\p) circle(2pt) node[above]{$\t$};}
\draw[dashed] (A)..controls(.5,2.5)and(1.5,3)..(B)..controls(4,3)and(3,-.5)..(C);"""
        if kind=="subtract":
            b+=r"\draw[->,DeepBlue,thick] (A)--(B) node[midway,above left]{$\vect D_1$};\draw[->,DeepBlue,thick] (A)--(C) node[midway,below]{$\vect D_2$};"
        return b+(r"\draw[->,Gold,thick] (B)--(C) node[midway,above right]{$\vect D_{23}$};" if a else "")
    if kind=="coordinates":
        b=r"""\draw[->] (0,0)--(4.3,0) node[right]{$x$};\draw[->] (0,0)--(0,5) node[above]{$y$};
\coordinate (A) at (1.2,1.8);\coordinate (B) at (3.6,4.8);
\fill (A) circle(2pt) node[left]{$A(2,3)$};
\draw[->,DeepBlue,thick] (A)--(B) node[midway,right]{$\Delta\vect r=(4,5)\,\mathrm m$};
\node[below left] at (0,0){$O$};"""
        return b+(r"\fill (B) circle(2pt) node[above]{$B(6,8)$};\draw[->,Gold] (0,0)--(A) node[midway,left]{$\vect r_1$};\draw[->,Gold] (0,0)--(B) node[pos=.70,above left=10pt]{$\vect r_2$};\draw[dashed] (B)--(3.6,0) node[below]{$6$};\draw[dashed] (B)--(0,4.8) node[left]{$8$};" if a else r"\fill (B) circle(2pt) node[above]{$B$};")
    if kind=="airplane":
        b=r"""\draw[->] (0,0)--(6,0) node[right]{东 $x$};\draw[->] (0,0)--(0,3.8) node[above]{北 $y$};
\coordinate (P) at (3.2,2.4);\coordinate (B) at (5,0);
\fill (0,0) circle(2pt) node[below left]{$O$};\fill (P) circle(2pt) node[above]{$P$};\fill (B) circle(2pt) node[below]{$B$};
\draw[->,DeepBlue,thick] (0,0)--(P) node[midway,above left]{$800\,\mathrm{km}$};
\draw (0,.8) arc(90:36.87:.8) node[midway,above]{$53^\circ$};
\draw[<->] (0,-.7)--(5,-.7) node[midway,below]{$1000\,\mathrm{km}$};"""
        return b+(r"\draw[->,Gold,thick] (P)--(B) node[midway,right]{$\Delta\vect r$};\draw[dashed] (P)--(3.2,0) node[below]{$640$};\node[left] at (0,2.4){$480$};\draw[dashed] (0,2.4)--(P);" if a else r"\draw[dashed] (P)--(B) node[midway,right]{改航};")
    if kind in ("shotput","bomb"):
        b=r"""\draw[thick] (-.5,-1)--(6,-1) node[right]{地面};
\coordinate (O) at (0,1);\coordinate (P) at (5,-1);
\fill (O) circle(2pt) node[left]{$O$};\fill (P) circle(2pt) node[below]{$P$};
\draw[<->] (-.4,-1)--(-.4,1) node[midway,left]{$H$};
\draw[dashed] (O)--(5,1);"""
        if kind=="bomb":
            b+=r"\draw[->,DeepBlue,thick] (O)--(1.7,1) node[above]{$v$};\draw[dashed] (O)--(P);\draw[dashed] (O)--(0,-1);\draw (0,.3) arc(-90:-21.8:.7) node[midway,below right]{$\phi$};"
            return b+(r"\draw[Gold,thick,domain=0:5,samples=50] plot(\x,{1-2*\x*\x/25});\draw[<->] (0,-1.6)--(5,-1.6) node[midway,below]{$D=vt$};" if a else "")
        b+=r"\draw[->,DeepBlue,thick] (O)--(1.3,2) node[right]{$v_0$};\draw (1,1) arc(0:37.57:1) node[midway,right]{$\theta$};\draw[DeepBlue,domain=0:5,samples=60] plot(\x,{1+.8*\x-.24*\x*\x});"
        return b+(r"\draw[<->,Gold] (0,-1.6)--(5,-1.6) node[midway,below]{$R$};\draw[->] (0,1)--(0,2.7) node[above]{$y$};\node[above right] at (5,-1){$(R,-H)$};" if a else "")
    if kind=="bouncearea":
        b=r"""\draw[thick](-.5,0)--(6.4,0);\fill(0,1)circle(2pt);\draw[<->](-.4,0)--(-.4,1)node[midway,left]{$h$};
\draw[->,DeepBlue](0,1)--(1.2,1)node[right]{$\sqrt{2gh}$};
\draw[DeepBlue,domain=0:2,samples=40]plot(\x,{1-\x*\x/4});
\draw[DeepBlue,domain=2:4.4,samples=40]plot(\x,{.25*(\x-2)*(4.4-\x)});
\draw[DeepBlue,domain=4.4:5.84,samples=40]plot(\x,{.25*(\x-4.4)*(5.84-\x)});"""
        shade=r"\fill[PaleBlue,domain=2:4.4,samples=40](2,0)--plot(\x,{.25*(\x-2)*(4.4-\x)})--cycle;" if a else ""
        extra=r"\draw[<->,Gold](2,-.3)--(4.4,-.3)node[midway,below]{$S_n$};\draw[<->,Gold](3.2,0)--(3.2,.36)node[midway,right]{$H_n$};\node at(3.2,.85){$A_n=\frac23H_nS_n$};" if a else ""
        return r"\begin{scope}[y=2cm]"+shade+b+extra+r"\end{scope}"
    if kind in ("circle", "electron", "centripetal", "kepler", "sameperiod", "sound"):
        b=r"""\draw[DeepBlue,thick] (0,0) circle(1.5);\fill (0,0) circle(2pt) node[below left]{$O$};
\fill (1.5,0) circle(2pt) node[below right]{$P$};\draw[thin] (0,0)--(1.5,0) node[midway,below]{$R$};
\draw[->,DeepBlue,thick] (1.5,.1)--(1.5,1.3) node[right]{$v$};"""
        if kind=="circle":b=b.replace("$R$","$r$")+r"\node[align=center] at (0,-2.2){$r=10\,\mathrm{cm}$\\每分钟 $30$ 圈};"
        if kind=="electron":b+=r"\draw[->,Gold] (-.5,1.65) arc(105:40:1.72);\node at (3,.3){$R=r_e$};\node at (3,-.5){$\omega R^2\simeq10^{-5}$};"
        if kind in ("kepler","sameperiod"):
            b=b.replace("$R$","$R_1$").replace("{$P$}","{$P_1$}")
            b+=r"\draw[dashed] (0,0) circle(2.2);\draw (0,0)--(-1.8,1.265) node[midway,above]{$R_2$};\fill (-1.8,1.265) circle(2pt) node[above left]{$P_2$};"
            b+=(r"\node[align=left] at (4,.2){$T_1^2/R_1^3=C$\\$T_2^2/R_2^3=C$};" if kind=="kepler" else r"\node[align=left] at (4,.2){$T_1=T_2=T$\\半径不同，周期相同};")
        if kind=="sound":b+=r"\draw[->,Gold] (-.5,1.7) arc(105:40:1.8);\node at (3,-.5){$\omega_0=0,\ \beta>0$};"
        if not a:return b
        if kind=="sound":return b+r"\draw[->,Gold,very thick](2,0)--(2,1)node[right]{$a_t$};\node at(3,-1.5){$a_t=R\beta$};"
        if kind in ("circle","electron"):return b+r"\node at(3,-1.5){$v=\omega R$};".replace("$v=\\omega R$","$v=\\omega r$" if kind=="circle" else "$v=\\omega R$")
        return b+r"\draw[->,Gold,very thick] (1.4,0)--(.4,0) node[midway,above]{$a_r$};\node at (3,-1.5){$v=\omega R$};"
    if kind=="logspiral":
        b=r"""\draw[->] (-.2,0)--(4,0) node[right]{$x$};\draw[->] (0,-.2)--(0,3.3) node[above]{$y$};
\draw[DeepBlue,thick,domain=-1:1.1,samples=80] plot({exp(\x)*cos(\x*180/pi)},{exp(\x)*sin(\x*180/pi)});
\coordinate (P) at (1.55,1.36);\fill (P) circle(2pt) node[left]{$P$};
\draw[dashed] (0,0)--(P) node[midway,above left]{$r$};\node[below left] at (0,0){$O$};"""
        return b+(r"\draw[->,Gold] (P)--(2.68,2.35) node[right]{$v_r$};\draw[->,Gold] (P)--(.56,2.49) node[left]{$v_\theta$};\draw[->,DeepBlue,very thick] (P)--(1.69,3.48) node[above]{$\vect v$};\node at (3.3,3){$v_r=v_\theta$};" if a else r"\draw[->,DeepBlue] (P)--(1.64,2.73) node[right]{$\vect v$};")
    if kind in ("linearresistance","quadraticresistance"):
        b=r"""\draw[->] (0,0)--(6.2,0) node[right]{$x$};\fill (1,0) circle(2pt) node[below]{$P$};
\draw[->,DeepBlue,thick] (1,.5)--(2.6,.5) node[right]{$v>0$};
\draw[->,Gold,thick] (2.6,1.3)--(1,1.3) node[midway,above]{$a<0$};"""
        if a:
            b+=r"\begin{scope}[xshift=3.8cm,yshift=.8cm,x=.55cm,y=.9cm]\draw[->] (0,0)--(4,0) node[right]{$t$};\draw[->] (0,0)--(0,1.5) node[above]{$v/v_0$};"
            b+=(r"\draw[DeepBlue,thick,domain=0:3.5,samples=50] plot(\x,{exp(-\x)});" if kind=="linearresistance" else r"\draw[DeepBlue,thick,domain=0:3.5,samples=50] plot(\x,{1/(1+\x)});")
            b+=r"\end{scope}"
        return b
    if kind in ("frame", "centervelocity", "centerframe", "centeracceleration"):
        b=r"""\draw[->] (-.5,0)--(6.5,0) node[right]{$x$};\node[below left] at (0,0){$O$};
\fill (1,0) circle(2pt) node[below]{$m_1$};\fill (4,0) circle(2pt) node[below]{$m_2$};
\draw[->,DeepBlue,thick] (1,.4)--(2.3,.4) node[above]{$v_1$};
\draw[->,DeepBlue,thick] (4,.4)--(5,.4) node[above]{$v_2$};"""
        if kind=="frame":
            b=b.replace("$m_1$","$A$").replace("$m_2$","$B$").replace("$v_1$","$v$")
            b=b.replace(r"\draw[->,DeepBlue,thick] (4,.4)--(5,.4) node[above]{$v_2$};",r"\node at (4,.7){$v_B=0$};")
            b+=r"\draw[->,Gold] (.4,-1)--(2,-1) node[right]{$S':u$};"
            return b+(r"\node[align=left] at (4,-1.4){每个速度均减去 $u$\\相对速度仍为 $v$};" if a else "")
        if kind=="centeracceleration":b=b.replace("$v_1$","$a_1$").replace("$v_2$","$a_2$")
        b+=r"\fill[Gold] (2.5,0) circle(2pt) node[below]{$C$};"
        if a:
            b+=(r"\draw[->,Gold] (2.5,1.2)--(3.7,1.2) node[right]{$V_C$};\node at (3,-1.2){$m_1v_1'+m_2v_2'=0$};" if kind=="centerframe" else r"\node at (3,-1.2){对 $Mx_C=m_1x_1+m_2x_2$ 求导};")
        return b
    if kind=="trainrunner":
        b=r"""\draw[thick,fill=PaleBlue] (0,0) rectangle (6,1.8);\draw[thick] (-.4,-.4)--(6.6,-.4);
\fill (2,.8) circle(2pt) node[below]{人};\draw[->,DeepBlue] (2,1.1)--(3.6,1.1) node[above]{$v_2,a_2$（对车）};
\draw[->,Gold] (4,-.9)--(5.6,-.9) node[right]{$a_1$（对地）};\node[left] at (0,0){$O'$};\node[left] at (0,-.4){$O$};"""
        return b+(r"\draw[<->] (0,-1.6)--(2,-1.6) node[midway,below]{$x_{\rm 人/车}$};\node at (3,2.5){$x=x_{\rm 车}+x_{\rm 人/车}$};" if a else "")
    if kind=="fallingsphere":
        b=r"""\fill (0,2) circle(2pt) node[above left]{$O$};\draw[->,Gold] (0,1.9)--(0,.8) node[midway,left]{$\vect g$};
\draw[DeepBlue] (0,0) circle(1.5);\draw[dashed] (-1.5,0) arc(180:360:1.5 and .35);\draw (-1.5,0) arc(180:0:1.5 and .35);
\fill (0,0) circle(2pt) node[below left]{$C$};\fill (1.06,1.06) circle(2pt) node[right]{$P$};"""
        return b+(r"\draw[->,DeepBlue,thick] (0,0)--(1.06,1.06) node[midway,below right=4pt]{$v_0t$};\draw[->] (0,2)--(0,0) node[pos=.65,left=14pt]{$\frac12\vect g t^2$};\draw[->,Gold] (0,2)--(1.06,1.06) node[midway,above right=6pt]{$\vect r$};" if a else r"\draw[dashed] (0,0)--(1.06,1.06) node[midway,below right]{$R(t)$};")
    if kind in ("wind", "equalwind", "smoke"):
        b=r"""\draw[->] (0,0)--(4,0) node[right]{东};\draw[->] (0,0)--(0,3.4) node[above]{北};"""
        if kind=="wind":return b+r"\draw[->,DeepBlue,thick] (0,0)--(2.8,0) node[midway,below]{$\vect v_{\rm 机/气}$};\draw[->,Gold,thick] (2.8,0)--(2.8,2) node[midway,right]{$\vect v_{\rm 气/地}$};"
        if kind=="equalwind":return b+r"\draw[->,DeepBlue,thick] (0,0)--(0,2.5) node[midway,left]{$\vect v_{\rm 机/地}$};\node[align=left] at (3,2){地速 $60$\\空速 $60$\\风速 $30$};"
        return b+r"\draw[->,Gold] (1.5,0)--(1.5,-1.3) node[below]{$\vect v_{\rm 船}$};\draw[->,DeepBlue] (0,1)--(2.4,1) node[right]{第一次烟对船};\draw[->,DeepBlue] (0,1.8)--(1.6,3.4) node[right]{第二次烟对船};"
    if kind=="intercept":
        return r"""\draw[thick] (-3,0)--(4,0);\fill (0,0) circle(2pt) node[below]{目标};
\fill (-2,2.5) circle(2pt) node[left]{投弹点};\draw[->,DeepBlue] (-2,2.5)--(-.5,2.5) node[right]{$v_1$};
\fill (2.5,0) circle(2pt) node[below]{炮位 $s=D$};\fill (-2.5,0) circle(2pt) node[below]{炮位 $s=-D$};
\draw[<->] (3.2,0)--(3.2,2.5) node[midway,right]{$H$};
\draw[<->] (0,-.8)--(2.5,-.8) node[midway,below]{$D$};"""
    if kind=="missile":
        return r"""\draw[thick] (-.5,0)--(6,0);\fill (0,0) circle(2pt) node[below]{$A$};
\fill (0,2.8) circle(2pt) node[left]{飞机};\draw[->,DeepBlue] (0,2.8)--(2,2.8) node[above]{$v_0$};
\draw[dashed] (0,0)--(0,2.8);\draw[<->] (-.6,0)--(-.6,2.8) node[midway,left]{$H$};
\draw[->,Gold] (0,0)--(0,1.3) node[right]{$v_1$（初始）};
\draw[DeepBlue,->] (0,.2)..controls(.5,2)and(2,2.4)..(4,2.8);
\node[right] at (1.7,1){速度始终沿视线};"""
    if kind=="semicylinder":
        return r"""\draw[thick] (-2,0) arc(180:0:2);\draw[thick] (-2,0)--(2,0);\fill (0,0) circle(2pt) node[below]{$C(X,0)$};
\coordinate (P) at (1,1.732);\draw[very thick] (P)--(1,3.5);\fill (P) circle(2pt) node[right]{$P$};
\draw[dashed] (0,0)--(0,2.3) (0,0)--(P) node[midway,right]{$R$};
\draw (.0,.8) arc(90:60:.8) node[midway,above]{$\theta$};
\draw[->,DeepBlue] (-1,-.7)--(.5,-.7) node[right]{$v_0$};\draw[->,Gold] (1.4,2.5)--(1.4,3.3) node[right]{$v_y$};
\node[align=left] at (4,1.7){杆的横坐标固定为 $x_0$\\$x_0-X=R\sin\theta$\\$y=R\cos\theta$};"""
    if kind=="lighttiming":
        return r"""\fill (0,0) circle(2pt) node[below]{$A$（起点）};\fill (5,0) circle(2pt) node[below]{$B$（终点）};\draw[->,thick] (0,0)--(5,0);
\fill (1.5,2.7) circle(2pt) node[above]{观察者 $O$};\draw[dashed] (0,0)--(1.5,2.7) node[midway,left]{$r_A$};\draw[dashed] (5,0)--(1.5,2.7) node[midway,right]{$r_B$};"""
    if kind=="solarday":
        b=r"""\fill (0,0) circle(3pt) node[below]{太阳};\draw[DeepBlue] (0,0) circle(2);
\fill (2,0) circle(2pt) node[right]{$E_1$};\fill (1.532,1.286) circle(2pt) node[above right]{$E_2$};
\draw[dashed] (0,0)--(2,0) (0,0)--(1.532,1.286);\draw[->,Gold] (1.5,0) arc(0:40:1.5) node[midway,right]{$\Omega D$};
\draw[->] (2,-.5) arc(-90:170:.5);\node at (4,-.2){自转与公转同向};"""
        return b+(r"\node[align=center] at (0,-3){一天内自转角 $2\pi+\Omega D$\\相对日地连线转角为 $2\pi$};" if a else "")
    if kind=="roemer":
        return r"""\draw[DeepBlue] (0,0) circle(1.7);\fill (0,0) circle(3pt) node[below]{太阳};
\fill (.578,1.5987) circle(2pt) node[above]{$E$};\fill (5,0) circle(3pt) node[right]{木星};
\draw[dashed] (.578,1.5987)--(5,0) node[midway,above]{视线};\draw[->,Gold] (.578,1.5987)--(1.7,1.193) node[below]{$\vect v_E$};
\draw[thin] (5,0) circle(.45);\node at (5,-.8){木卫I轨道};\node at (1,-2.5){距离变化使相邻信号的传播时间不同};"""
    if kind=="interpolation":
        b=r"""\draw[->] (0,0)--(5,0) node[right]{$\theta$};\draw[->] (0,-1.7)--(0,1.7) node[above]{落点误差};
\fill (1,-1.2) circle(2pt) node[left]{$-30\,\mathrm m$};\fill (4,0.8) circle(2pt) node[right]{$+20\,\mathrm m$};
\draw[dashed] (1,0) node[above]{$29^\circ$}--(1,-1.2);\draw[dashed] (4,0) node[below]{$30^\circ$}--(4,.8);"""
        return b+(r"\draw[DeepBlue,thick] (1,-1.2)--(4,.8);\fill[Gold] (2.8,0) circle(2pt) node[above left]{$\theta_*$};" if a else "")
    if kind=="rifle":
        b=r"""\fill (0,0) circle(2pt) node[below]{$O$（枪口）};\fill (6,0) circle(2pt) node[below]{$P$（目标）};
\draw[dashed] (0,0)--(6,0) node[midway,below]{水平瞄准线};
\draw[->,very thick,DeepBlue] (0,0)--(2,1) node[above]{$v_0$（枪管方向）};\draw (.8,0) arc(0:26.565:.8) node[midway,right]{$\alpha$};
\draw[<->] (0,-.7)--(6,-.7) node[midway,below]{$L$};"""
        return b+(r"\draw[Gold,thick,domain=0:6,samples=60] plot(\x,{.5*\x-\x*\x/12});" if a else "")
    if kind=="aimwall":
        return r"""\draw[fill=PaleBlue] (1,-.5)--(6,-.5)--(6,3.7)--(1,3.7)--cycle;
\draw[thick,DeepBlue] (1,1.3)--(6,1.3) node[right]{目标线 $z=h$};
\fill (-1,0) circle(2pt) node[left]{$O(z_0)$};\fill (4,1.3) circle(2pt) node[below right]{$P$};\fill (4,2.8) circle(2pt) node[above right]{$Q$};
\draw[dashed] (-1,0)--(4,2.8);\draw[<->] (-1,-1)--(1,-1) node[midway,below]{$L$};\node at (3.5,3.35){墙面};"""
    if kind=="rodscenter":
        return r"""\coordinate(C)at(0,0);\coordinate(A)at(4.2,0);\coordinate(B)at(0,2.6);
\draw[very thick] (B)--(C)--(A)--cycle;\draw (0,.3)--(.3,.3)--(.3,0);
\node[below left]at(C){$C=O$};\node[right]at(A){$A$};\node[above]at(B){$B$};
\foreach\x/\y/\t in {0/1.3/a,2.1/0/b,2.1/1.3/c}{\fill[DeepBlue](\x,\y)circle(2pt)node[above right]{$M_\t$};}
\draw[->] (0,0)--(4.8,0) node[right]{$x$};\draw[->] (0,0)--(0,3.2)node[above]{$y$};
\node at(2.5,-1.1){$m_a=\lambda_a a,\ m_b=\lambda_b b,\ m_c=\lambda_c c$};"""
    if kind=="cup":
        return r"""\draw[very thick] (0,3)--(0,0)--(2.5,0)--(2.5,3);
\fill[PaleBlue] (.05,.05)rectangle(2.45,1.3);\draw[DeepBlue,thick](0,1.3)--(2.5,1.3);
\draw[<->](-.5,0)--(-.5,1.3)node[midway,left]{$h$};
\draw[<->](3,0)--(3,2.2)node[midway,right]{$H$};\draw[dashed](0,2.2)--(2.5,2.2);
\draw[->](1.25,-.2)--(1.25,3.5)node[above]{$z$};\node at(1.25,-.6){底面积 $S$};
\node[align=left]at(5,1.5){空杯质量 $M$\\水密度 $\rho$\\$0\le h\le h_{\max}$};"""
    if kind=="capshell":
        return r"""\draw[thick](0,0)circle(1.5);\draw[DeepBlue,very thick](-1.118,1)arc(138.19:41.81:1.5);
\draw[dashed](-1.118,1)--(1.118,1);\draw[<->](-1.8,1)--(-1.8,1.5)node[midway,left]{$h$};
\fill(0,0)circle(2pt)node[left]{$O$};\draw[->](0,-1.7)--(0,2)node[above]{$z$};
\draw[->,Gold](2.1,.4)--(3.2,.4)node[midway,above]{下移};
\draw[thick](3.682,1)arc(138.19:401.81:1.5);\draw[dashed](3.682,1)arc(138.19:41.81:1.5);
\draw[DeepBlue,very thick](3.682,-2)arc(138.19:41.81:1.5);
\draw[dashed](3.682,-2)--(5.918,-2);\node[below]at(4.8,-2.3){保持朝向，顶点粘在原最低点};"""
    if kind=="springs":
        b=r"""\draw[very thick](0,-.6)--(0,.6);\draw[thick](0,0)--(.4,0);
\draw[decorate,decoration={coil,aspect=.5,segment length=5pt,amplitude=3pt}] (.4,0)--(2.5,0)node[midway,above=6pt]{$k_1$};
\draw[thick](2.5,0)--(2.9,0);\draw[decorate,decoration={coil,aspect=.5,segment length=5pt,amplitude=3pt}](2.9,0)--(5,0)node[midway,above=6pt]{$k_2$};
\draw[->,DeepBlue,thick](5,0)--(6.5,0)node[right]{$F$};"""
        return b+(r"\draw[<->](.4,-.8)--(2.5,-.8)node[midway,below]{$x_1$};\draw[<->](2.9,-.8)--(5,-.8)node[midway,below]{$x_2$};\node at(3,-1.8){总伸长 $x=x_1+x_2$，同一张力通过各弹簧};" if a else "")
    if kind=="hexforces":
        return r"""\coordinate(O)at(0,0);\draw[dashed](0,0)--(1,1.732)--(3,1.732)--(4,0)--(3,-1.732)--(1,-1.732)--cycle;
\foreach\x/\y/\t in {1/1.732/1,3/1.732/2,4/0/3,3/-1.732/4,1/-1.732/5}{\draw[->,DeepBlue](0,0)--(\x,\y)node[right]{$F_\t$};}
\draw[->,Gold,thick](0,-2.4)--(1,-2.4)node[right]{$\vec F_1+\vec F_5$};
\draw[->,Gold,thick](0,-3.1)--(3,-3.1)node[right]{$\vec F_2+\vec F_4$};
\node[below left]at(O){$O$};\node at(2,2.5){关于水平轴对称的竖直分量相消};"""
    if kind=="harmonic":
        return r"""\draw[->](-3,0)--(3.2,0)node[right]{$x$};\fill(0,0)circle(2pt)node[below]{$O$};
\fill(2.2,0)circle(2pt)node[below]{$A$};\fill(1.2,0)circle(2pt)node[above]{$P(x)$};\node at(2.2,.9){$t=0:\ x=A$};
\draw[dashed](-2.2,-.4)--(-2.2,.4)node[above]{$-A$};\draw[<->](-2.2,-.8)--(2.2,-.8)node[midway,below]{$x=A\cos\omega t$};"""
    if kind=="planarorbit":
        return scene("centripetal",False).replace("$R$","$A$")
    if kind=="helixforce":
        return r"""\draw[->](0,-.2)--(0,4)node[above]{$z$};\draw[->](0,0)--(3,-.7)node[right]{$x$};\draw[->](0,0)--(-1.2,-.7)node[left]{$y$};
\draw[dashed](0,0)ellipse(1.3 and .35);\draw[DeepBlue,thick,domain=0:720,samples=140]plot({1.3*cos(\x)},{.0042*\x+.35*sin(\x)});
\node[align=left]at(4,2.4){$x=A\cos\omega t$\\$y=A\sin\omega t$\\$z=q(t)$};
\node[below]at(1.3,0){$A$};\node at(4,.8){螺旋线示意对应 $q(t)=ut$};"""
    if kind=="constantforce":
        return r"""\draw[->](0,0)--(6.5,0)node[right]{$x$};\fill(0,0)circle(2pt)node[below]{$O$};
\fill(1,0)circle(2pt)node[below]{$m$};\draw[->,DeepBlue,thick](1,.4)--(2.4,.4)node[right]{$v_0$};\draw[->,Gold,thick](1,1.1)--(2.8,1.1)node[right]{$F$};
\fill(5,0)circle(2pt)node[below]{末态};\draw[->,DeepBlue](5,.4)--(6.4,.4)node[above]{$v_1$};"""
    if kind=="forceparabola":
        return r"""\draw[->](-.2,0)--(4,0)node[right]{$x$};\draw[->](0,-.2)--(0,3.4)node[above]{$y$};
\fill(0,0)circle(2pt)node[below left]{$O$};\draw[->,DeepBlue,thick](0,0)--(2,1)node[right]{$\vect v_0$};
\draw[->,Gold,thick](2.7,1.2)--(2.7,2.8)node[right]{$\vect F$};\draw[dashed](2,1)--(2,0)node[below]{$u$};\node[left]at(0,1){$w$};\draw[dashed](0,1)--(2,1);"""
    if kind=="rightforce":
        return r"""\fill(0,0)circle(2pt)node[below left]{$m$};\draw[->,DeepBlue,very thick](0,0)--(3,0)node[right]{$\vect v$};
\draw[->,Gold,very thick](0,0)--(0,-2)node[below]{$\vect F$（前进方向右侧）};\draw(.3,0)--(.3,-.3)--(0,-.3);"""
    if kind=="moon":
        return r"""\draw[fill=PaleBlue](0,0)circle(.65);\node at(0,.95){地球};\fill(0,0)circle(1.5pt)node[below left]{$O$};
\draw[DeepBlue](0,0)circle(2.4);\fill(2.4,0)circle(2.5pt)node[right]{月球};
\draw[dashed](0,0)--(2.4,0)node[midway,above]{$r$};\draw(0,0)--(-.46,.46)node[above left=6pt]{$R_E$};
\node[align=left]at(5,1.1){$r=3.8\times10^5\,\mathrm{km}$\\$T=27.3$ 天};\node at(1,-3){示意不按实际比例绘制};"""
    if kind=="twostageblock":
        return r"""\draw[thick](-.5,0)--(6.8,0);\draw[fill=PaleBlue](.2,0)rectangle(1.2,.65);\draw[->,DeepBlue](1.3,.3)--(2.3,.3)node[above]{$F$};
\fill(.7,0)circle(1pt)node[below]{$A$};\fill(3.2,0)circle(2pt)node[below]{撤力点 $C$};\fill(6.3,0)circle(2pt)node[above]{$B$（停止）};
\draw[<->](.7,-.7)--(6.3,-.7)node[midway,below]{$x=5.0\,\mathrm m$};\node at(4.8,1){撤力后滑行 $2.0\,\mathrm s$};\node at(3,-1.6){全过程接触面粗糙，$\mu=0.20$};"""
    if kind=="disc":
        return r"""\draw[fill=PaleBlue](0,0)circle(2);\fill(0,0)circle(2pt)node[below left]{$O$};\fill(1.4,0)circle(3pt)node[right]{$m$};
\draw[dashed](0,0)--(1.4,0)node[midway,below]{$r$};\draw[->,Gold](0,1.4)arc(90:170:1.4)node[midway,left]{$\omega$};
\node at(0,-2.6){俯视图；最大静摩擦因数 $\mu$};"""
    if kind=="pulleyperson":
        return r"""\draw[thick](0,2.6)circle(.5);\draw[thick](0,3.1)--(0,3.6);\draw[thick](-.5,2.6)--(-.5,0)(.5,2.6)--(.5,-.6);
\draw[fill=PaleBlue](-.9,-.7)rectangle(-.1,0);\node at(-.5,-.35){$m_1$};\fill(.9,.8)circle(.16);\draw(.9,.64)--(.9,-.15)(.9,.3)--(.5,.7)(.9,-.15)--(.6,-.7)(.9,-.15)--(1.2,-.7);\node[right]at(1,.3){$m_2$};
\draw[->,Gold](1.8,-.4)--(1.8,1.2)node[midway,right]{$a$（相对绳）};\node at(-2.1,1){轻绳、轻滑轮};"""
    if kind=="centrifuge":
        return r"""\draw[dashed](0,0)circle(2.3);\draw[very thick](0,0)--(2.3,0)node[midway,below]{$r=7\,\mathrm m$};\fill(0,0)circle(2pt)node[below left]{$O$};\fill(2.3,0)circle(4pt)node[right]{实验对象};
\draw[->,Gold](.5,1.9)arc(75:150:2)node[midway,above]{$\omega$};\node at(1,-2.8){水平向心加速度要求 $5g$};"""
    if kind=="forceimpulse":
        return r"""\draw[->](0,0)--(6.8,0)node[right]{$t/\mathrm s$};\draw[->](0,0)--(0,2.8)node[above]{$F/\mathrm N$};
\draw[DeepBlue,very thick](0,2.4)--(2,2.4)--(2,1.5)--(3.6,1.5)--(3.6,0)--(6,0);
\foreach\x/\t in {0/0,2/5,3.6/9,6/15}{\draw(\x,.08)--(\x,-.08)node[below]{$\t$};}
\node[left]at(0,2.4){$8$};\node[left]at(0,1.5){$5$};\node at(4.8,1.4){末速度为零};"""
    if kind=="wallkick":
        return r"""\draw[thick](-.2,0)--(5,0);\draw[very thick](4,0)--(4,3.6)node[above]{竖直墙};
\fill(0,0)circle(2pt)node[below]{$O$};\draw[->,DeepBlue,thick](0,0)--(1.7,1.2)node[above]{$v_0$};\draw(.8,0)arc(0:35:.8)node[midway,right]{$\theta$};
\draw[<->](0,-.7)--(4,-.7)node[midway,below]{$s_0$};\fill(4,1.7)circle(2pt)node[left]{$P$};\draw[->,Gold](3.6,1.7)--(3.6,3)node[left]{$J_f$};\draw[->,Gold](4,1.7)--(2.8,1.7)node[below]{$J_N$};"""
    if kind in ("reflectship","conicalship"):
        b=r"""\draw[->](-1,-1.5)--(6,-1.5)node[right]{$x$};\draw[->,Gold](.2,2.2)--(1.8,2.2)node[right]{$v$（飞船）};
\foreach\yy in {-.7,0,.7}{\fill(5,\yy)circle(1.5pt);\draw[->,DeepBlue](4.6,\yy)--(3.6,\yy);}
\node[align=center]at(4.4,1.6){船体系入射粒子\\相对速度 $-v$};"""
        if kind=="reflectship":b+=r"\draw[very thick](.2,-1)--(.2,1);\node[right]at(.2,0){迎风面积 $S$};"
        else:b+=r"\draw[very thick](2,0)--(0,1)--(0,-1)--cycle;\draw[dashed](0,0)--(2,0);\draw(1.2,0)arc(180:153.435:.8)node[midway,left]{$\alpha$};\draw[<->](0,-2.2)--(2,-2.2)node[midway,below]{$L$};"
        return b
    if kind=="sail":
        return r"""\draw[thick](-.5,0)--(6,0);\draw[thick](1,.4)--(3,.4)--(2.6,0)--(1.4,0)--cycle;\draw[very thick](2,.4)--(2,2.6);
\draw[->,DeepBlue](0,1.6)--(1.5,1.6)node[midway,above]{$v_0$};\draw[->,Gold](3.2,.5)--(4.8,.5)node[above]{$v$};\node at(3.7,2.2){帆面垂直来风};\node at(2,-.7){静水；风与船同向};"""
    if kind=="radiation":
        return r"""\draw[DeepBlue](0,0)circle(3.5);\fill(0,0)circle(4pt)node[below left]{太阳 $P_S$};
\draw[dashed](0,0)--(3.5,0)node[midway,below]{$r$};\draw[very thick](3.5,-.8)--(3.5,.8)node[right]{接收面 $S$};
\draw[->,Gold](.4,.12)--(3.3,.12);\draw[->,Gold](.3,.4)--(2.6,1.2);\draw[->,Gold](.3,-.4)--(2.6,-1.2);\node at(2,-2.2){各向同性辐射；接收面与入射光垂直};"""
    if kind=="earthjump":
        return r"""\draw[thick](-2,0)..controls(-1,.3)and(1,.3)..(2,0);\node at(0,-.8){地球 $M_E$};
\fill(0,1.5)circle(.15);\draw(0,1.35)--(0,.7)(0,1.1)--(-.3,.9)(0,1.1)--(.3,.9)(0,.7)--(-.3,.4)(0,.7)--(.3,.4);\node[right]at(.6,1.3){人 $m$};
\draw[->,Gold](1.5,.7)--(1.5,1.9)node[right]{$v$};\draw[dashed](-2.5,-1.2)rectangle(2.5,2.3);\node at(0,2.7){研究系统：人和地球};"""
    if kind in ("horizontalcenter","springmasses"):
        b=r"""\draw[thick](-.5,0)--(6,0);\fill(1,.15)circle(3pt)node[above]{$m_1$};\fill(4.5,.15)circle(3pt)node[above]{$m_2$};\node at(2.7,-.7){水平面光滑};"""
        if kind=="springmasses":b+=r"\draw[decorate,decoration={coil,aspect=.5,segment length=5pt,amplitude=3pt}](1.1,.15)--(4.4,.15)node[midway,above=7pt]{$k,l_0$};\draw[<->](1,-1.3)--(4.5,-1.3)node[midway,below]{$l>l_0$（初始静止）};"
        else:b+=r"\draw[->,Gold](1,.7)--(2.3,.7)node[above]{$\vec F_{12}$};\draw[->,Gold](4.5,.7)--(3.2,.7)node[above]{$\vec F_{21}$};\node at(3,1.7){所有初速度为零；仅有水平内力};"
        return b
    if kind in ("rain","rainwind"):
        b=r"""\draw[thick](0,1.8)--(0,0)--(3,0)--(3,1.8);\fill[PaleBlue](.05,.05)rectangle(2.95,.8);\draw[thick](-.5,-.2)--(6,-.2);
\foreach\x in {.4,1.2,2,2.8}{\draw[->,DeepBlue](\x,3)--(\x,2);}
\draw[->,Gold](3.2,.8)--(4.7,.8)node[right]{$F$};\node at(1.5,1.2){$M,S$};\node at(1.5,3.5){雨水密度 $\rho$};"""
        if kind=="rainwind":b=b.replace(r"(\x,3)--(\x,2)",r"(\x,3)--({\x+.6},2)")+r"\draw[->,Gold](3.5,2.7)--(5,2.7)node[right]{$u$（雨水水平速度）};"
        return b+(r"\node[align=left]at(5,-1){质量流率 $q$\\带入水平动量流率 $qu$};" if a and kind=="rainwind" else "")
    if kind in ("pickuprope","gradedrope"):
        b=r"""\draw[thick](-1,0)--(5,0);\draw[very thick](0,2.8)--(0,.2)..controls(.1,0)and(.3,0)..(.5,0)--(3.5,0);
\draw[->,DeepBlue](.4,2)--(.4,3.1)node[right]{$v$};\draw[<->](-.5,0)--(-.5,2.8)node[midway,left]{$x$};\node at(2,1){桌上绳段原来静止};"""
        if kind=="gradedrope":b+=r"\node[align=left]at(3.5,2.4){材料坐标 $s$ 从手端起\\$\lambda(s)=\lambda_0(1+s/l)$};"
        return b+(r"\draw[->,Gold](4.5,.2)--(4.5,1.1)node[right]{$\dot m=\lambda(x)v$};\node at(2,-.8){运动段质量 $m_x=\int_0^x\lambda(s)\,\dd s$};" if a else "")
    if kind in ("absorb","gradientabsorb","droplet","efficiencydrop"):
        drop=kind in ("droplet","efficiencydrop")
        b=r"""\foreach\x/\y in {-1/1,1/1.5,2.5/.5,-.5/-1.2,2/-1.7,3/1.5}{\fill[DeepBlue](\x,\y)circle(1.4pt);}
\draw[->,Gold](3.7,1.4)--(3.7,-1.4)node[below]{$y,v$（向下）};"""
        b+=(r"\draw[thick,fill=PaleBlue](1,0)circle(.65);\draw(1,0)--(1.65,0)node[midway,above]{$r$};" if drop else r"\draw[thick,fill=PaleBlue](0,-.5)rectangle(2,.5);\node at(1,0){$m$};\node at(1,-.9){截面积 $S$};")
        b+=r"\node at(1,2.2){介质粒子在地面系静止};"
        if kind=="gradientabsorb":b+=r"\node at(1,-2.4){$\rho(y)=\rho_0(1+y/L)$};"
        if kind=="efficiencydrop":b+=r"\node at(1,-2.4){捕获比例 $\eta(r)=r_*/r$};"
        return b+(r"\node at(1,3){$\dot m=\rho(y)Sv$，入流初动量为零};" if a and not drop else (r"\node at(1,3){$\dot m=\eta(r)\rho_f\pi r^2v$};" if a else ""))
    if kind=="rocket":
        return r"""\draw[thick,fill=PaleBlue](0,-.5)--(2,-.5)--(2.8,0)--(2,.5)--(0,.5)--cycle;\node at(1,0){$M(t)$};
\draw[->,DeepBlue](2.8,0)--(4.2,0)node[right]{$v$};\draw[->,Gold](0,0)--(-1.7,0)node[left]{$u$（相对火箭）};
\node[align=center]at(1,-1.5){燃烧前 $M_0$，燃尽后 $M$\\无重力和其他外力};"""
    if kind=="inclinework":
        return r"""\coordinate(A)at(0,2.6);\coordinate(B)at(5,0);\draw[very thick](A)--(B);\draw[dashed](0,0)--(B);
\fill(A)circle(2pt)node[above]{$A$};\fill(B)circle(2pt)node[right]{$B$};\draw[<->](-.3,2.2)--(4.7,-.4)node[midway,below]{$L$};
\draw[<->](-.8,0)--(-.8,2.6)node[midway,left]{$L\sin\theta$};\draw(4.1,0)arc(180:152.526:.9)node[midway,left]{$\theta$};
\draw[->,DeepBlue,thick](2,1.56)--(2.9,1.09)node[right]{$mg\sin\theta$};\draw[->,Gold,thick](2,1.56)--(1.1,2.03)node[left]{$f_k$};"""
    raise ValueError(kind)


def scene(kind,answer=False):
    body=_scene(kind,answer)
    # Chinese labels in math subscripts require text mode, otherwise XeTeX
    # silently drops the CJK glyphs from the Latin math roman font.
    return re.sub(r"_\{\\rm ([^}]+)\}",lambda m:r"_{\text{"+m[1]+"}}",body)


CH02 = {
    3: ("oscillation", False, True, "恒幅运动的周期、振幅与极值点切线", "图中的 $T$ 由相邻同向相位给出，$A$ 是极值到 $x=0$ 的距离；极值处的水平切线给出 $v=0$。"),
    4: ("samples", True, True, "相邻采样点与区间内的运动", "图中突出的一小段以 $\Delta t$ 为横向间隔、$\Delta x$ 为纵向变化；本题给定连续匀加速模型后，每个采样区间内均不换向。"),
    5: ("headon", True, True, "两质点相向运动与闭合距离", "图中 $A_0P$ 和 $B_0P$ 分别是两质点到相遇点 $P$ 的路程，两段之和等于初始间距 $15\,\mathrm m$。"),
    9: ("vtarea", True, True, "速度图下的梯形与有向位移", "图中阴影拆为矩形 $v_0t$ 与三角形 $at^2/2$；它们相加得到位置变化 $x-x_0$。图示取 $v_0,a>0$，一般情形仍按有向面积相加。"),
    10: ("notime", True, True, "首末速度与时间间隔对应的位移面积", "图中阴影的有向面积为 $x_2-x_1$，梯形上下底为 $v_1,v_2$，横向宽度为 $\Delta t$，所以可用梯形面积消去时间。"),
    11: ("train", True, True, "列车通过固定点时的三个平移状态", "图中每个半车长均为 $L/2$；车头、中部、车尾依次通过 $O$ 时，对同一列车标志点而言累计位移分别为 $0,L/2,L$。"),
    12: ("junction", True, True, "路口边界与加速、制动的方向", "图中的路口竖线是位移边界 $x=60\,\mathrm m$；加速通过对应限定时间，制动停车对应该边界处的末速度条件。"),
    13: ("rearend", True, True, "前后车的间距与后车制动方向", "图中前车 $B$ 的位置减去后车 $A$ 的位置得到间距；制动箭头向后，故后车加速度为 $-a$。间距极小必须与两车速度相等同时成立。"),
    14: ("pursuit", True, True, "追及问题的初始间距和直道终点", "图中终点竖线 $x=L$ 限定允许追及的位置；$r=x_B-x_A$ 的正根给出首次相遇，必须再检查相遇点严格在这条边界之前。"),
    15: ("vertical", True, True, "三种竖直运动使用同一个向上正方向", "图中三个原点均在各自抛出点，重力箭头向下，故 $a=-g$；上抛和下抛的差别进入 $v_0$ 的正负号。"),
    16: ("heights", True, True, "高度水平线与位置曲线的交点", "图中 $x=15\,\mathrm m$ 水平线与曲线有两个交点，$x=20\,\mathrm m$ 在顶点相切，$x=25\,\mathrm m$ 没有交点；负时间分支不属于实际运动。"),
    18: ("superman", True, True, "延迟出发、初始领先距离和地面边界", "图中在超人出发时女子已下降 $gT^2/2$；两人以相同加速度下落，能消除这段领先的仅是相对速度 $v_0-gT$，可用时间为 $t_f-T$。"),
    20: ("return", True, True, "第 n 次离板、转向和返回的循环", "图中从板到转向点的距离为 $x_{\max,n}$；去、回两段路程相等，而 $a_n$ 始终指向板，故每个循环要单独代入负的坐标加速度。"),
    21: ("strobe", True, False, "频闪拍摄的高度和运动方向", ""),
}

CH03 = {
    24: ("displacement",True,False,"三个时刻的位置与真实路径",r""),
    25: ("subtract",True,True,"累计位移共用起点，分段位移连接终点",r"$A$ 是两个累计位移的共同起点；从 $B$ 指向 $C$ 才是待求分段位移，因此应作矢量差 $\vect D_2-\vect D_1$。"),
    26: ("coordinates",True,True,"初始位置、位移与最终位置",r"$O\!A$ 是初始位置矢量，$A\!B$ 是随后位移，二者首尾相接得到 $O\!B$；横、纵坐标须分别相加。"),
    27: ("airplane",True,True,"改航前后的端点与东西、南北分量",r"$P$ 是改航点，$B$ 是目标；$\overrightarrow{PB}$ 的东向分量是 $1000-640$，北向分量是 $0-480$。不能把从 $O$ 到 $B$ 的总位移除以最后半小时。"),
    38: ("shotput",True,True,"从高于地面的出手点射向落点",r"以出手点 $O$ 为坐标原点，地面是 $y=-H$，落点 $P$ 的坐标为 $(R,-H)$。把这一边界代入轨迹方程，才可对出手角优化。"),
    42: ("bomb",True,True,"投弹点、竖直线与目标视线",r"$OP$ 是投弹瞬间的瞄准线，$H$ 是竖直落差，$D$ 是水平超前距离；夹角 $\phi$ 从竖直线量起，因此用 $\tan\phi=D/H$。"),
    44: ("bouncearea",True,True,"反弹后的抛物线弓形面积",r"阴影从某次反弹点起、到下一次落地点止，对应高度 $H_n$ 与射程 $S_n$；题目从第一次反弹开始计面积，故级数下标从 $n=1$ 起。"),
    46: ("circle",True,True,"圆轨道半径、转动周期和切向速度",r"半径 $OP=r$，速度沿 $P$ 点切线；一周路程为 $2\pi r$，每秒转数是 $f$，故 $v=2\pi rf$、$|\omega|=2\pi f$。"),
    53: ("electron",True,True,"经典自转模型中表面点的速度",r"表面点 $P$ 到轴心的距离为 $R=r_e$，故切向速率是 $\omega R$；把题给 $\omega R^2$ 除以同一个 $R$ 后再与光速比较。"),
    54: ("centripetal",True,True,"切向速度与指向圆心的加速度",r"$OP=R$，$\vect v$ 与半径垂直，向心加速度沿 $PO$ 指向圆心。匀速只说明速率不变，速度方向仍在改变，所以 $a_r=v^2/R=\omega^2R$。"),
    55: ("kepler",True,True,"同心轨道满足同一个周期律常量",r"两个轨道均以 $O$ 为圆心，但各自的周期随半径变化。对任一轨道先写 $a_r=(2\pi/T)^2R$，再把该轨道的 $T^2=CR^3$ 代入。"),
    56: ("sameperiod",True,True,"半径不同而周期相同的同心轨道",r"两个轨道在同一周期内各转一周，故角速度大小均为 $2\pi/T$；向心加速度箭头指向 $O$，其大小由 $\omega^2R$ 决定。"),
    58: ("sound",True,True,"角加速度引起边缘切向速率增长",r"点 $P$ 的速率沿切线，$v=R\omega$；题给的 $\beta$ 控制角速度变化，先求 $\omega=\beta t$，再由线速度达到声速确定时间。"),
    67: ("logspiral",True,True,"对数螺线上径向与横向速度分解",r"$\vect v_r$ 沿向外径向，$\vect v_\theta$ 垂直于径向且沿逆时针方向；两分量相等，合速度位于两者之间，由直角速度三角形确定夹角。"),
    71: ("linearresistance",True,True,"一次阻力下的速度方向和衰减曲线",r"正向速度与负向加速度反向，右侧衰减曲线在任意有限时间都位于时间轴上方；总路程要由曲线下的无穷区间面积判断。"),
    72: ("quadraticresistance",True,True,"平方阻力下的正速度与长时尾部",r"速度始终沿正向，加速度反向；右侧曲线的 $1/t$ 尾部与指数尾部不同，不能仅凭速度趋零便断言总路程有限。"),
}

CH04 = {
    75:("frame",True,True,"地面系与向正方向平移的参考系",r"参考系 $S'$ 相对地面沿正向运动，必须从两个地面速度中扣除同一个 $u$。两点速度之差在这种平移中保持不变。"),
    76:("trainrunner",True,True,"人、车和地面三个位置的相加",r"人的坐标先相对车内原点 $O'$ 给出，再加 $O'$ 相对地面原点 $O$ 的位置。两次求导须针对同一个地面时间。"),
    77:("fallingsphere",True,True,"自由下落的球心与各向扩展的球面",r"$O$ 是共同抛出点，$C$ 是自由下落的球心，任意球 $P$ 相对 $C$ 的矢量正是 $\vect v_0t$，其长度只由初速率决定。"),
    78:("centervelocity",True,True,"质量加权位置及质心的平移",r"两点示意质量加权坐标的构造，多质点时对所有点求和。各质量不变时先求导位置加权和，才能得到速度加权和；常速度的加权和仍是常量。"),
    79:("centerframe",True,True,"地面速度与随质心平移的速度",r"$C$ 随系统质心平移，质心系中每个速度均减去 $V_C$。解出的相对速度方向相反，且质量加权和应为零。"),
    80:("centeracceleration",True,True,"两质点加速度的质量加权",r"$C$ 的位置由两端质量加权；对同一时间连续求导两次，便把权重原样带入加速度关系。质心匀速时，加权加速度总和为零。"),
    81:("wind",True,False,"机头正东、空气向北的给定速度",r""),
    83:("equalwind",True,False,"正北地速与给定空速、风速",r""),
    84:("smoke",True,False,"船向南航行时的两次相对烟迹",r""),
    86:("intercept",True,False,"轰炸机、地面目标与两种炮位",r""),
    88:("missile",True,False,"恒速导弹的初始视线与飞机高度",r""),
    92:("semicylinder",False,True,"圆面接触点的几何约束和杆的竖直速度",r"杆沿固定竖直线运动，而圆心 $C$ 的横坐标为 $X$；$CP=R$ 将接触点 $P$ 的纵坐标与圆心位移联系起来。对约束求导时不能把 $\theta$ 误当作常量。"),
    102:("lighttiming",True,False,"观察者到起点和终点的不同光程",r""),
    104:("solarday",True,True,"地球自转与日地连线的相对转角",r"$E_1,E_2$ 表示相邻太阳日同一时刻的地球位置。日地连线也在公转中转过 $\Omega D$，因此地球自转必须额外多转这段角度。图中角度为辨认而放大。"),
    106:("roemer",True,False,"地球轨道切向速度和木星视线",r""),
    107:("interpolation",True,True,"两次试射误差与零误差角度",r"两个实测点分别位于零误差轴的两侧；连接两点后的横轴交点给出线性插值角度，横向距离按误差的 $30:20$ 分配。"),
    108:("rifle",True,True,"枪管方向、水平准线和同高落点",r"$OP$ 为水平瞄准线，初速度沿枪管与它夹角为 $\alpha$。命中点 $P$ 与枪口等高，应在抛体轨迹中使用同高射程条件，并取实际步枪所对应的小角分支。"),
    109:("aimwall",True,False,"墙面上的实际命中点与准线延长交点",r""),
}

CH05 = {
    2:("rodscenter",False,True,"把三根杆的质量集中到各自中点",r"$M_a,M_b,M_c$ 分别是三根均匀杆的中点；杆的质量应由各自线密度乘长度得到，再以这些中点坐标作质量加权。"),
    4:("cup",True,False,"注水状态、杯底原点和允许水深",r""),
    5:("capshell",True,False,"球冠切下后不翻转地移至底部",r""),
    6:("springs",True,True,"串联弹簧的共同张力和伸长相加",r"中间连接点视为无质量，所以两侧弹力大小相等；总伸长是每根弹簧伸长之和。结论以至少两根、均具有正劲度的理想轻弹簧为前提。"),
    8:("hexforces",False,True,"正六边形力矢量按对称对相加",r"$F_1$ 与 $F_5$、$F_2$ 与 $F_4$ 分别关于 $F_3$ 方向对称，竖直分量两两抵消；只需比较它们沿水平轴的投影。"),
}

CH06 = {
    1:("harmonic",True,False,"沿 x 轴的余弦位置函数与振幅边界",r"$O$ 是平衡位置，$P$ 的坐标为有符号的 $x$。以下求二阶导数时沿这个固定坐标轴投影，再判断力的符号与 $x$ 的关系。"),
    2:("planarorbit",True,False,"给定参数方程在平面中的圆周",r"$OP=A$ 是到原点的距离；由参数方程可知初始点在正 $x$ 轴上且速度向上。以下分别求 $x,y$ 的二阶导数，检查合力是否指向 $O$。"),
    3:("helixforce",True,False,"水平圆投影和独立给定的竖直位置",r"水平投影半径为 $A$，而竖直坐标由 $q(t)$ 独立给定。图中螺旋线仅示意 $q(t)=ut$ 的特例，不能据此在一般情形中令 $q''(t)=0$。"),
    4:("linearresistance",True,False,"正向减速运动的速度与加速度方向",r"质点仍沿 $+x$ 运动，给定关系 $v=v_0-\alpha x$ 对应 $0\le x<v_0/\alpha$ 的运动阶段。要由它求力，须使用 $a=v\,\dd v/\dd x$，而非把 $\dd v/\dd x$ 直接当成加速度。"),
    5:("constantforce",True,False,"恒力作用下的初末速度与位移方向",r"正方向沿恒力选取，初末速度应理解为该方向的有符号分量。时间由速度变化决定，位移则由初末速度平方之差决定。"),
    6:("forceparabola",True,False,"沿恒力与垂直恒力的坐标分解",r"$y$ 轴沿恒力，$x$ 轴垂直于恒力；初速度的水平分量 $u$ 非零时，$x=ut$ 才能用来消去时间。"),
    7:("rightforce",True,False,"初始速度及始终指向前进方向右侧的力",r"垂直标记表示合力没有切向分量；“右侧”是随瞬时前进方向改变的方向。先由此确定速率不变，再分析法向曲率。"),
    11:("moon",True,False,"地表重力尺度与月球轨道尺度",r"$r$ 从地心 $O$ 量到月球，$R_E$ 是地球半径；比较平方反比规律时应使用这两个到地心的距离，而非月球离地表的高度。"),
    15:("twostageblock",True,False,"受恒力段与撤力后的滑行段",r"撤力点 $C$ 把总位移 $AB$ 分成两段，$CB$ 段的已知停车时间可先确定 $C$ 点速度，随后再倒推 $AC$ 段。"),
    19:("disc",True,False,"圆盘俯视中的物体半径和角速度",r"$r$ 是物体到轴心 $O$ 的距离；相对圆盘静止并不表示对地静止，所需水平向心力必须由静摩擦承担。"),
    20:("pulleyperson",True,False,"重物、同学及相对绳的加速度",r"$a$ 的箭头表示同学相对他这一侧绳的加速度，而非相对地面的加速度。绷紧轻绳两侧的加速度反向，所以应先建立相对加速度约束再列动力学方程。"),
    31:("centrifuge",True,False,"离心机的水平杆、轴心和实验对象",r"半径从转轴 $O$ 量到实验对象；$5g$ 明确指水平向心加速度，故直接用 $\omega^2r=5g$，不把竖直重力混入这一给定分量。"),
}

CH07 = {
    "ch07:ex:s07-3-2":("forceimpulse",True,False,"两段推力和撤力阶段的时间边界",r"横轴把全过程分成 $5,4,6\,\mathrm s$ 三段。摩擦力在三个运动阶段都作负冲量，外加推力则仅在前两段存在。"),
    "ch07:ex:s07-3-7":("wallkick",True,False,"到墙前的飞行与蹬墙冲量方向",r"从 $O$ 到墙上接触点 $P$ 的水平距离为 $s_0$；墙的法向冲量向左消除水平速度，向上的切向冲量增加竖直速度。"),
    "ch07:ex:s07-3-9":("reflectship",True,False,"飞船参考系中粒子迎面入射平面",r"粒子的入射方向相对飞船向后，图中箭头表示船体系中的速度；弹性原路反弹后应先变回介质原来静止的参考系，再求每粒子的动量变化。"),
    "ch07:ex:s07-3-10":("conicalship",True,False,"圆锥的轴向长度与半顶角",r"$L$ 沿轴线量取，半顶角 $\alpha$ 在母线与轴线之间。粒子在光滑锥面作镜面反射，动量改变量先沿局部法线计算，再投影到轴向。"),
    "ch07:ex:s07-3-11":("sail",True,False,"同向的风速、船速与帆面",r"风和船同向，碰帆前的相对速率应为 $v_0-v$，而传给船的地面系功率是推力乘船速 $v$。两种速度不可混用。"),
    "ch07:ex:s07-3-12":("radiation",True,False,"各向同性辐射球面与法向接收面",r"同一总功率通过半径 $r$ 的球面分摊，接收面 $S$ 与径向入射垂直；吸收与反射的区别进入光子沿该法线的动量改变量。"),
    "ch07:ex:s08-3-13":("earthjump",True,False,"人和地球的系统边界",r"虚线把人和地球同时包括在系统内。地面给人的支持力在单独研究人时是外力，在这个完整系统内则属于内力。"),
    "ch07:ex:s08-3-14":("horizontalcenter",True,False,"光滑平面内仅有系统内力的质点组",r"相互作用箭头成对出现，水平方向的总外力为零；所有初速度为零使初始总动量也为零，二者共同决定质心运动。"),
    "ch07:ex:s08-3-17":("springmasses",True,False,"两端质量、弹簧原长与初始伸长",r"两端质量决定质心在瞬时弹簧长度上的分点比例；在均匀理想弹簧作仿射伸缩的模型中，同一材料分点才可始终对应这处固定空间位置。"),
    "ch07:ex:s08-3-19":("rain",True,False,"竖直入雨的容器与水平推力",r"雨滴进入前没有水平速度，因此它们没有带入水平动量；容器内水量却不断增加，左侧必须对整个 $m(t)v(t)$ 求导。"),
    "ch07:ex:s08-3-20":("pickuprope",True,False,"以恒速上提时绳元由静止进入运动段",r"桌面上的静止绳元依次从底部进入竖直运动段；手的提力既要托住这段绳的重量，又要提供新绳元的向上动量流率。"),
    "ch07:ex:s08-3-22":("absorb",True,False,"定截面下落物体对静止介质的扫掠",r"扫掠厚度在 $\dd t$ 内为 $v\dd t$，迎风面积为 $S$，故质量流率是 $\rho Sv$；介质入流的初始动量为零。"),
    "ch07:ex:s08-3-23":("droplet",True,False,"球形水滴吸附静止雾滴的迎风截面",r"增长中的球半径为 $r$，迎风面积是 $\pi r^2$，质量却与 $r^3$ 成正比。质量流率与半径增长率须由这两个不同几何量联系。"),
    "ch07:ex:s09-3-24":("rainwind",True,True,"横向有风的雨水携带入流动量",r"雨水在地面系中带有水平速度 $u$，所以每秒不仅带入质量 $q$，还带入动量 $qu$。这是本变式与竖直入雨前例的关键差别。"),
    "ch07:ex:s09-3-25":("gradedrope",True,True,"线密度沿材料坐标增大的绳",r"材料坐标从手端起算，当前进入运动段的绳元位于 $s=x$，其线密度为 $\lambda(x)$；已运动部分的质量则是从 $0$ 到 $x$ 的积分。"),
    "ch07:ex:s09-3-27":("gradientabsorb",True,True,"介质密度随下落深度线性增加",r"越深处介质越密，瞬时质量流率由当前位置的 $\rho(y)$ 决定，不能继续把 $\rho S$ 当作常量。图中 $y$ 从释放点向下量取。"),
    "ch07:ex:s09-3-28":("efficiencydrop",True,True,"捕获效率随水滴半径减小",r"迎风截面仍为 $\pi r^2$，但只有比例 $\eta(r)=r_*/r$ 被吸附。这个效率因子改变质量通量，随后也改变动量方程中的稀释项。"),
    "ch07:ex:s09-3-30":("rocket",True,False,"火箭减质量与相对喷气速度",r"喷气速率 $u$ 是相对火箭的速率，方向与火箭速度相反。火箭质量递减，所以质量微元 $\dd M<0$，积分时必须保持这一符号约定。"),
    "ch07:ex:s12-4-19":("inclinework",False,True,"粗糙斜面上的位移、高度差和功的符号",r"$A\to B$ 沿斜面向下，重力切向分量同向、摩擦力反向；高度差为 $L\sin\theta$，据此分别计算重力势能变化与摩擦功。"),
}

VARIANTS = {
    "ch07:ex:s09-3-24": ("横向来雨的入流动量",r"""
一个初始质量为 $M$、水平开口面积为 $S$ 的容器，从静止开始受恒定水平力 $F>0$ 推动。
地面光滑，雨水以恒定的向下速度落入开口，且在地面系中还具有与 $F$ 同向的恒定水平速度 $u\ge0$。
雨水完全留在容器内；稳定质量流率记为 $q=\rho S\Delta h/\tau>0$，其中静止同样容器在
$\tau$ 时间内水位上升 $\Delta h$。忽略侧面撞雨及溢出。求 $t=3\tau$ 时的速度，并讨论长时间极限。
""",r"""
取推力方向为正。容器与已收集的水构成变质量系统，$m(t)=M+qt$。
在 $\dd t$ 内进入的雨水质量为 $q\dd t$，它在进入前已有水平动量 $qu\dd t$。
将这部分带入动量和外力冲量同时计入，得
\[
 \frac{\dd}{\dd t}[(M+qt)v]=F+qu.
\]
初始动量为零，积分为 $(M+qt)v=(F+qu)t$，所以
\[
 \boxed{v(3\tau)=\frac{3\tau(F+qu)}{M+3q\tau}},\qquad
 \boxed{\lim_{t\to\infty}v=u+\frac Fq}.
\]
展开式也可写成 $(M+qt)\dot v=F+q(u-v)$：入流相对容器的速度差产生 $q(u-v)$ 项。
当容器超过雨水的水平速度时，该项反而使它减速，但恒力仍可使速度继续增加并渐近上述极限。
检查 $u=0$ 恢复竖直来雨前例；$q\to0$ 的有限时间极限恢复 $v=Ft/M$。
$qu$ 与 $F$ 同为力，分母为质量，所得速度量纲正确。极限仅在持续稳定入雨且容器不溢出的模型内成立。
"""),
    "ch07:ex:s09-3-25": ("线密度不均匀的提绳",r"""
长度为 $l$、总质量为 $m$ 的柔软绳放在水平桌面上。用手捏住一端，以恒定速度 $v>0$ 竖直提起。
从手持端沿绳的材料坐标记为 $s$，线密度为 $\lambda(s)=\lambda_0(1+s/l)$，$0\le s\le l$。
当手端高度为 $0<x<l$ 时，已提起的绳竖直，余绳仍静止，忽略弯折区长度和弹性。
求 $\lambda_0$、运动绳段质量与手的提力。新进入运动段的绳元按瞬时拾取模型处理。
""",r"""
先用总质量归一化线密度：
\[
 m=\int_0^l\lambda_0(1+s/l)\,\dd s=\frac32\lambda_0l,
 \qquad \boxed{\lambda_0=\frac{2m}{3l}}.
\]
已运动的材料是 $0\le s\le x$，故运动段质量为
\[
 \boxed{m_x=\lambda_0\left(x+\frac{x^2}{2l}\right)}.
\]
拾取点对应 $s=x$，每秒进入的绳长为 $v$，因此
$\dot m_x=\lambda(x)v=\lambda_0(1+x/l)v$。
新绳元从零速度变为向上速度 $v$；运动段自身保持恒速，手力与重力的差供给这股动量流率：
\[
 F-m_xg=v\dot m_x=\lambda_0(1+x/l)v^2.
\]
于是
\[
 \boxed{F=\frac{2m}{3l}\left[g\left(x+\frac{x^2}{2l}\right)
 +(1+x/l)v^2\right]},\qquad 0<x<l.
\]
重力项包含运动段线密度的积分，拾取项使用当前位置的局部线密度，不能用同一个平均值替代二者。
若将分布改回常量 $\lambda=m/l$，立即恢复 $F=\lambda gx+\lambda v^2$。
两项量纲均为力；$x\to l^-$ 仍有拾取项，但最后一段完全离桌后质量流率变为零，恒速手力随之变为 $mg$。
"""),
    "ch07:ex:s09-3-27": ("介质密度随深度增加的吸附下落",r"""
初始质量为 $m_0$、固定迎风面积为 $S$ 的物体从静止释放，竖直向下的深度记为 $y\ge0$。
介质粒子在地面系中静止，质量密度为 $\rho(y)=\rho_0(1+y/L)$，其中 $\rho_0,L>0$。
物体吸附所有遇到的粒子，重力加速度为常量 $g$，忽略其他作用。求质量 $m(y)$，写出并积分
速度平方的方程，比较深处运动与均匀介质前例的差别。
""",r"""
以题图向下的 $y$ 为正。扫掠厚度为 $\dd y$ 时，吸附质量为
\[
 \dd m=\rho(y)S\,\dd y.
\]
令 $k=\rho_0S$，由 $m(0)=m_0$ 得
\[
 \boxed{m(y)=m_0+k\left(y+\frac{y^2}{2L}\right)},\qquad
 \dot m=k(1+y/L)v.
\]
入流粒子原本静止，故 $\dd(mv)/\dd t=mg$，即
$\dot v=g-(m'(y)/m)v^2$。在开始下落后令 $w=v^2$，用 $\dot v=v\,\dd v/\dd y$ 得
\[
 w'+2\frac{m'}m w=2g,\qquad (m^2w)'=2gm^2.
\]
结合 $w(0)=0$，得到含有完整初值的结果
\[
 \boxed{v^2(y)=\frac{2g}{m(y)^2}\int_0^y m(\xi)^2\,\dd\xi}.
\]
本题积分可直接展开为
\[
 \int_0^y m(\xi)^2\dd\xi
 =m_0^2y+m_0ky^2+\frac{k^2+m_0k/L}{3}y^3
 +\frac{k^2}{4L}y^4+\frac{k^2}{20L^2}y^5.
\]
在 $y\to0$ 时 $v^2\sim2gy$，恢复刚释放时的自由落体起步。
深处 $m\sim ky^2/(2L)$，所以 $v^2\sim2gy/5$，于是 $a=\tfrac12\dd(v^2)/\dd y\to g/5$。
这与均匀介质的 $g/3$ 不同，差别来自密度增长使质量随深度按平方增长。
令 $L\to\infty$ 可恢复均匀介质；积分量纲是质量平方乘长度，乘 $g/m^2$ 后为速度平方。
"""),
    "ch07:ex:s09-3-28": ("捕获效率随半径变化的水滴",r"""
液态密度为 $\rho_w$ 的球形水滴在静止均匀雾中由静止下落，雾的质量密度为 $\rho_f$。
初始半径为 $r_0$，重力加速度为 $g$。与全部吸附的前例不同，水滴只捕获迎面雾滴的比例
$\eta(r)=r_*/r$，其中 $0<r_*\le r_0$，未捕获粒子直接穿过且不交换动量。
忽略空气阻力和蒸发，水滴始终为球形。列出运动方程，求 $v^2(r)$ 及长时间加速度的极限。
""",r"""
令 $b=\rho_fr_*/(4\rho_w)$，它的量纲是长度。球形质量关系不变，但吸附率含效率因子：
\[
 m=\frac43\pi\rho_wr^3,\qquad
 \dot m=\eta(r)\rho_f\pi r^2v=\rho_f\pi r_*rv.
\]
由质量式求导，得 $\dot r=bv/r$。被捕获雾滴入流前动量为零，所以
\[
 \frac{\dd(mv)}{\dd t}=mg,\qquad
 \boxed{\dot v=g-\frac{3b}{r^2}v^2},\qquad
 \boxed{\dot r=\frac br v}.
\]
在 $v>0$ 阶段令 $w=v^2$，消去时间：
\[
 \frac{\dd w}{\dd r}=\frac{2gr}{b}-\frac{6w}{r},
 \qquad \frac{\dd}{\dd r}(r^6w)=\frac{2g}{b}r^7.
\]
从 $(r_0,0)$ 积分，得到
\[
 \boxed{v^2(r)=\frac{g}{4b}\left(r^2-\frac{r_0^8}{r^6}\right)}.
\]
代回速度方程：
\[
 \boxed{a=\frac g4+\frac{3g}{4}\left(\frac{r_0}{r}\right)^8},
 \qquad \boxed{a\longrightarrow g/4}.
\]
初始 $r=r_0$ 时 $v=0,a=g$，之后半径增大、加速度下降但始终为正。
$r\ge r_0\ge r_*$ 保证 $0<\eta\le1$，因此捕获比例的模型自洽。
长时 $v^2\sim gr^2/(4b)$，从而 $\dot r\to\sqrt{gb}/2$、$v\sim gt/4$。
这里的 $g/4$ 与全捕获模型的 $g/7$ 不同，差别由半径相关效率改变了质量通量。
"""),
}


def add_missing_figures(text, number, specs):
    def revise(m):
        lab=re.search(r"\\label\{(ch"+f"{number:02d}"+r":ex:[^}]+)\}",m[2])
        if not lab:return m[0]
        k=int(lab[1].rsplit("-",1)[1])
        key=lab[1] if lab[1] in specs else k
        if key not in specs:return m[0]
        kind,q,a,caption,link=specs[key]
        if number==7 and lab[1].startswith("ch07:ex:s12"):k=100+k
        question,answer=m[2],m[4]
        if q:question+=figure(f"mech:{number:02d}:{k}:q",caption,scene(kind))
        if a:
            answer=figure(f"mech:{number:02d}:{k}:a",caption+"（解答用辅助图）",scene(kind,True))+"图~\\ref{mech:"+f"{number:02d}"+":"+str(k)+":a}中，"+link+"\n"+answer
        elif q and link:
            answer="题图~\\ref{mech:"+f"{number:02d}"+":"+str(k)+":q}中，"+link+"\n"+answer
        return m[1]+question+m[3]+answer+m[5]
    return BLOCK.sub(revise,text)


def macro_definitions(text):
    """Resolve real TeX macro bodies, including optional argument defaults."""
    result={}
    pattern=r"\\(?:newcommand|renewcommand|providecommand)\*?\{(\\[A-Za-z]+)\}(?:\[[^\]]*\])*\s*\{"
    for m in re.finditer(pattern,text):
        start=m.end();i=start;depth=1
        while depth and i<len(text):
            if text[i] in "{}" and (i==0 or text[i-1]!="\\"):
                depth+=1 if text[i]=="{" else -1
            i+=1
        result[m[1]]=(text[start:i-1],start,i-1)
    for m in re.finditer(r"\\registerfaithful\{([^}]+)\}\s*\{",text):
        start=m.end();i=start;depth=1
        while depth and i<len(text):
            if text[i] in "{}" and (i==0 or text[i-1]!="\\"):
                depth+=1 if text[i]=="{" else -1
            i+=1
        result["faithful@"+m[1]]=(text[start:i-1],start,i-1)
    return result


def has_tikz(text, definitions, seen=None):
    if r"\begin{tikzpicture}" in text:return True
    # Faithful redraw dispatch is parameterized by an old image filename. Its
    # body is TikZ, not a raster include; never count this as an absent picture.
    for m in re.finditer(r"\\sourcefigure(?:trim)?(?:\[[^\]]*\])?\{([^}]+)\}",text):
        registered=definitions.get("faithful@"+m[1])
        if registered and r"\begin{tikzpicture}" in registered[0]:return True
    seen=set() if seen is None else seen
    for command in re.findall(r"\\[A-Za-z]+",text):
        if command in definitions and command not in seen:
            seen.add(command)
            if has_tikz(definitions[command][0],definitions,seen):return True
    return False


def number_solution_figures(number,text):
    """Give legacy unnumbered solution drawings stable numbers and references.

    Existing physical discussion remains adjacent to its actual diagram. No
    synthetic process charts or answer-bearing question clones are introduced.
    """
    # Merged chapters contain separate brace-scoped definitions with the same
    # helper name. Promote every local definition, not just the final one.
    helper_pattern=r"\\(?:newcommand|renewcommand|providecommand)\*?\{(\\(?:soldiagcaption|diagcaption))\}(?:\[[^\]]*\])*\s*\{"
    for helper in reversed(list(re.finditer(helper_pattern,text))):
        start=helper.end();i=start;depth=1
        while depth and i<len(text):
            if text[i] in "{}" and (i==0 or text[i-1]!="\\"):depth+=1 if text[i]=="{" else -1
            i+=1
        body=text[start:i-1]
        if not any(s in body for s in (r"\figcap",r"\bookcaption",r"\refstepcounter")):
            replacement=r"\figcap{#1}" if helper[1]==r"\soldiagcaption" else r"\figcap{#1：#2}"
            text=text[:start]+replacement+text[i-1:]
    if REFERENCE_MARKER in text:
        return re.sub(r"(\\end\{qualityfigure\})\s*\\\\(?:\[[^\]]*\])?",r"\1\\par",text)
    definitions=macro_definitions(text)
    for command in (r"\soldiagcaption",r"\diagcaption"):
        if command in definitions:
            body,start,end=definitions[command]
            if not any(s in body for s in (r"\figcap",r"\bookcaption",r"\refstepcounter")):
                replacement=r"\figcap{#1}" if command==r"\soldiagcaption" else r"\figcap{#1：#2}"
                text=text[:start]+replacement+text[end:]
                definitions=macro_definitions(text)
    def revise(m):
        answer=m[4]
        if re.search(r"\\ref\{(?:[^}]*fig[^}]*|mech:[^}]+)\}",answer):return m[0]
        label=re.search(r"\\label\{([^}]+)\}",m[2])[1]
        unique="mech:legacy:"+label.replace(":ex:",":")
        # A direct picture belongs to the solution itself.
        direct=re.search(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",answer,re.S)
        used_label=None
        if direct:
            tail=answer[direct.end():]
            lm=re.search(r"^\s*(?:\\(?:figcap|diagramcaption)\{[^\n]*\})?\s*\\label\{([^}]+)\}",tail)
            if lm:used_label=lm[1]
            else:
                # Keep a new caption attached to the existing editable picture.
                numbered="\\begin{qualityfigure}\n"+direct[0]+"\n\\figcap{本题解答中的位置、分量与辅助量。}\\label{"+unique+"}\n\\end{qualityfigure}"
                answer=answer[:direct.start()]+numbered+answer[direct.end():]
                used_label=unique
        else:
            for call in re.finditer(r"\\[A-Za-z]+",answer):
                cmd=call[0]
                if cmd not in definitions or not has_tikz(definitions[cmd][0],definitions):continue
                body=definitions[cmd][0]
                lm=re.search(r"\\label\{([^}]+)\}",body)
                if lm:used_label=lm[1]
                else:
                    numbered=cmd
                    if not re.search(r"\\(?:figcap|bookcaption|soldiagcaption|diagcaption)\b",body):
                        numbered+=r"\figcap{本题解答中的几何、方向与辅助量。}"
                    numbered+=r"\label{"+unique+"}"
                    answer=answer[:call.start()]+numbered+answer[call.end():]
                    used_label=unique
                break
        if used_label:
            answer="\n以下推导所用的解图为图~\\ref{"+used_label+"}。\n"+answer
        return m[1]+m[2]+m[3]+answer+m[5]
    return REFERENCE_MARKER+"\n"+re.sub(r"(\\end\{qualityfigure\})\s*\\\\(?:\[[^\]]*\])?",r"\1\\par",BLOCK.sub(revise,text))


def refresh_new_diagrams(number,text):
    specs={2:CH02,3:CH03,4:CH04,5:CH05,6:CH06,7:CH07}[number]
    kinds={}
    for key,value in specs.items():
        k=key if isinstance(key,int) else int(key.rsplit("-",1)[1])
        if isinstance(key,str) and key.startswith("ch07:ex:s12"):k+=100
        kinds[k]=value[0]
    pattern=r"\\begin\{qualityfigure\}\s*\\begin\{tikzpicture\}\[>=Latex,font=\\small\]\n.*?\\end\{tikzpicture\}\s*\\figcap\{(.*?)\}\\label\{(mech:(\d+):(\d+):([qa]))\}\s*\\end\{qualityfigure\}"
    def refresh(m):
        if int(m[3])!=number or int(m[4]) not in kinds:return m[0]
        return figure(m[2],m[1],scene(kinds[int(m[4])],m[5]=="a")).strip()
    return re.sub(pattern,refresh,text,flags=re.S)


def repair_legacy_label_scopes(text):
    """Place labels in the same TeX group as their caption counter step."""
    calls=list(re.finditer(r"(\\[A-Za-z]+)\\label\{(mech:legacy:[^}]+)\}",text))
    for call in reversed(calls):
        command,label=call[1],call[2]
        definitions=macro_definitions(text)
        if command not in definitions:continue
        body,start,end=definitions[command]
        if r"\label{"+label+"}" not in body:
            pos=body.rfind(r"\end{minipage}")
            if pos<0:pos=body.rfind(r"\end{center}")
            if pos<0:pos=len(body)
            body=body[:pos]+r"\label{"+label+"}"+body[pos:]
            text=text[:start]+body+text[end:]
        text=text.replace(command+r"\label{"+label+"}",command)
    return text


def apply_chapter_revision(number, text):
    if MARKER in text:
        text=text.replace("Accent", "Gold").replace("$\nho$", r"$\rho$")
        # Repair the first draft's solid outline over the removed shell cap.
        text=text.replace(r"\draw[thick](4.8,0)circle(1.5);\draw[dashed](3.682,1)arc(138.19:41.81:1.5);",r"\draw[thick](3.682,1)arc(138.19:401.81:1.5);\draw[dashed](3.682,1)arc(138.19:41.81:1.5);")
        return repair_legacy_label_scopes(number_solution_figures(number,refresh_new_diagrams(number,text)))
    if number not in range(2, 8):
        return text
    if number == 2:
        # The original standalone endpoint data did not determine the travelled
        # distance.  Make the continuous model an explicit question condition.
        text = text.replace("求相邻两次测量之间的平均速率。", "已知这些数据来自同一匀加速直线运动，且采样时刻之间也服从该运动规律。求相邻两次测量之间的平均速率。")
        text = text.replace("求不相撞所需的最小 $a$。", "先求两车恰好接触的临界制动加速度，再给出保持正间距的条件。忽略车长，制动到停车后后车保持静止。")
        text = text.replace("不相撞要求最小间距非负：", "若把恰好接触也作为临界状态，要求最小间距非负：")
        def revise(m):
            lab = re.search(r"\\label\{ch02:ex:k02-2-(\d+)\}", m[2])
            if not lab or int(lab[1]) not in CH02:
                return m[0]
            k = int(lab[1]); kind,q,a,caption,link = CH02[k]
            question,answer=m[2],m[4]
            if q:
                question += figure(f"mech:02:{k}:q", caption, scene(kind))
            if a:
                answer = figure(f"mech:02:{k}:a", caption+"（解答用辅助图）", scene(kind,True)) + "图~\\ref{mech:02:"+str(k)+":a}中，" + link + "\n" + answer
            return m[1]+question+m[3]+answer+m[5]
        text=BLOCK.sub(revise,text)
    if number==3:
        # A single radius symbol must be used in the classical electron model.
        text=text.replace(r"半径 $r_e\simeq3\times10^{-15}\,\mathrm m$",r"半径 $R=r_e\simeq3\times10^{-15}\,\mathrm m$")
        text=text.replace("竖直速度反向且按固定比率 $e$ 减小。", "竖直速度反向且按固定比率 $e$ 减小，其中 $0<e<1$。")
        text=add_missing_figures(text,3,CH03)
    if number==4:
        text=text.replace("距墙 $L$ 的人以固定初速率 $v_0$ 投掷物体", "投掷点离地高度为 $z_0$、距墙 $L$，人以固定初速率 $v_0$ 投掷物体")
        text=text.replace("步枪中 $gL/v_0^2\\ll1$，故", "实数命中角要求 $gL/v_0^2\\le1$。射程方程通常还有高抛分支，本题步枪校准取接近水平的小角分支。步枪中 $gL/v_0^2\\ll1$，故")
        text=add_missing_figures(text,4,CH04)
    if number==5:
        text=text.replace("证明：串联弹簧的等效弹性系数", "设至少两根理想轻弹簧串联，各劲度系数均为正。证明：串联弹簧的等效弹性系数")
        text=text.replace("粘贴在圆球的最下面，形成一个“杯子”。", "保持球冠原朝向且不翻转，整体向下平移，使球冠顶点粘贴在原球壳最低点，形成一个“杯子”。")
        text=add_missing_figures(text,5,CH05)
    if number==6:
        text=add_missing_figures(text,6,CH06)
    if number==7:
        def variants(m):
            for label,(title,q,a) in VARIANTS.items():
                if r"\label{"+label+"}" in m[2]:
                    return r"\begin{origexamplebox}{变式："+title+"}"+r"\label{"+label+"}\n"+q+m[3]+a+m[5]
            return m[0]
        text=BLOCK.sub(variants,text)
        text=text.replace("条件与上面的模型相同，但介质粒子碰撞后以相同的相对速度反弹。", r"飞船以速率 $v$ 穿过在地面系静止、密度为 $\rho$ 的稀薄粒子介质，迎风平面面积为 $S$。粒子与飞船作正碰，碰后以相同的相对速率原路反弹，忽略单次碰撞对飞船速率的改变。")
        text=text.replace("且与介质粒子的碰撞为弹性碰撞，", r"在密度为 $\rho$ 的静止介质中以速率 $v$ 沿轴向前进，锥面光滑且粒子作弹性镜面反射，")
        text=add_missing_figures(text,7,CH07)
    return MARKER+"\n"+repair_legacy_label_scopes(number_solution_figures(number,text))


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("chapters",type=int,nargs="*",default=list(range(2,8)))
    parser.add_argument("--audit",action="store_true")
    parser.add_argument("--atlas",action="store_true")
    parser.add_argument("--render-atlas",action="store_true")
    parser.add_argument("--pdf-audit",action="store_true")
    args=parser.parse_args()
    for n in args.chapters:
        path=BOOK/f"generated/chapters/ch{n:02d}.tex"
        old=path.read_text();new=apply_chapter_revision(n,old)
        if old!=new:path.write_text(new);print(f"updated ch{n:02d}")
    if args.audit:
        import json
        rows=[]
        for n in range(2,8):
            source=(BOOK/f"generated/chapters/ch{n:02d}.tex").read_text()
            defs=macro_definitions(source)
            for m in BLOCK.finditer(source):
                label=re.search(r"\\label\{([^}]+)\}",m[2])[1]
                rows.append({"chapter":n,"label":label,"question_tikz":has_tikz(m[2],defs),"solution_tikz":has_tikz(m[4],defs),"numbered_figure_reference":bool(re.search(r"\\ref\{(?:[^}]*fig[^}]*|mech:[^}]+)\}",m[4]))})
        out=BOOK/"build/quality-mechanics/audit.json";out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
        print(f"audited {len(rows)} example pairs; {out}")
    if args.atlas:
        out=BOOK/"build/quality-mechanics/new-figures.tex"
        entries=[]
        for n,specs in ((2,CH02),(3,CH03),(4,CH04),(5,CH05),(6,CH06),(7,CH07)):
            for key,(kind,q,a,caption,link) in specs.items():
                for side,include in (("Q",q),("A",a)):
                    if not include:continue
                    entries.append((f"CH{n:02d} / {key} / {side}",caption,scene(kind,side=="A").replace("Accent","Gold")))
        preamble=r"""\documentclass[UTF8,zihao=-4,oneside,openany]{ctexbook}
\input{style.tex}
\geometry{a4paper,landscape,margin=12mm}
\pagestyle{plain}
\newsavebox{\reviewbox}
\newcommand{\ReviewPicture}[1]{\sbox{\reviewbox}{#1}%
\ifdim\wd\reviewbox>.92\linewidth\sbox{\reviewbox}{\resizebox{.92\linewidth}{!}{\usebox{\reviewbox}}}\fi
\ifdim\dimexpr\ht\reviewbox+\dp\reviewbox\relax>.31\textheight\resizebox*{!}{.31\textheight}{\usebox{\reviewbox}}\else\usebox{\reviewbox}\fi}
\begin{document}
"""
        chunks=[preamble]
        for i,(title,caption,body) in enumerate(entries):
            if i and i%4==0:chunks.append(r"\clearpage"+"\n")
            elif i%2==0 and i:chunks.append(r"\par\vspace{4mm}"+"\n")
            elif i%2:chunks.append(r"\hfill"+"\n")
            chunks.append(r"\noindent\begin{minipage}[t][.43\textheight][t]{.48\linewidth}\centering\small\textbf{"+title+"}\\\\[2mm]"+caption+r"\par\smallskip\ReviewPicture{\begin{tikzpicture}[>=Latex,font=\small]"+body+r"\end{tikzpicture}}\end{minipage}"+"\n")
        chunks.append(r"\end{document}"+"\n");out.parent.mkdir(parents=True,exist_ok=True);out.write_text("".join(chunks))
        print(f"atlas {len(entries)} drawings; {out}")
    if args.render_atlas:
        import fitz
        from PIL import Image,ImageDraw
        pdf=fitz.open(BOOK/"build/quality-mechanics/new-figures.pdf")
        for start in range(0,len(pdf),4):
            tiles=[]
            for page in list(pdf)[start:start+4]:
                pix=page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False)
                tiles.append(Image.frombytes("RGB",[pix.width,pix.height],pix.samples))
            w=max(im.width for im in tiles);h=max(im.height for im in tiles)
            sheet=Image.new("RGB",(2*w,2*h),"white")
            for i,im in enumerate(tiles):sheet.paste(im,((i%2)*w,(i//2)*h))
            out=BOOK/f"build/quality-mechanics/atlas-sheet-{start//4+1:02d}.png";sheet.save(out)
            print(out)
    if args.pdf_audit:
        import fitz,json
        report=[]
        for n in range(2,8):
            folder=BOOK/f"build/quality-mechanics/ch{n:02d}"
            doc=fitz.open(folder/f"ch{n:02d}.pdf")
            blank=[]
            for i,page in enumerate(doc):
                core=fitz.Rect(0,50,page.rect.width,page.rect.height-50)
                text=page.get_text(clip=core).strip()
                pix=page.get_pixmap(matrix=fitz.Matrix(.5,.5),clip=core,colorspace=fitz.csGRAY,alpha=False)
                ink=sum(v<245 for v in pix.samples)/len(pix.samples)
                if len(text)<5 and ink<.0003:blank.append(i+1)
            log=(folder/f"ch{n:02d}.log").read_text()
            aux=(folder/f"ch{n:02d}.aux").read_text()
            mismatch=[]
            for m in re.finditer(r"\\newlabel\{(mech:[^}]+)\}\{\{([^}]+)\}\{[^}]*\}\{.*?\}\{(figure\.[^}]+)\}",aux):
                if m[2]!=m[3].removeprefix("figure."):mismatch.append({"label":m[1],"printed":m[2],"anchor":m[3]})
            report.append({"chapter":n,"pages":len(doc),"blank_body_pages":blank,"overfull":log.count("Overfull"),"undefined":log.count("undefined"),"multiply_defined":log.count("multiply defined"),"missing_glyph":log.count("Missing character"),"figure_number_mismatches":mismatch})
        out=BOOK/"build/quality-mechanics/pdf-audit.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(out)


if __name__=="__main__":
    main()
