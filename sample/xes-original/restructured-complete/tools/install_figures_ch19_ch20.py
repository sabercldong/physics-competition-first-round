"""Install reviewed vector/image assets; keep all old source figure positions."""
from pathlib import Path
import re,shutil,json
from build_review_ch19_ch20 import ARCHIVE,book
OUT=book.BOOK/'assets/revision-ch19-ch20';OUT.mkdir(parents=True,exist_ok=True)
IMG=Path('/Users/dongxingxi/.codex/generated_images/019fe8f7-db8d-7383-b4b2-16a55baa634b')
assets={
 'coulomb':('c28c5be9-d120-4ec6-b158-c2509fd0028e','Original historically plausible engraved bust of Charles-Augustin de Coulomb; 18th century hair and clothing; white background; no text.'),
 'gauss':('8baac323-9023-4a02-9357-e92eb033655f','Original engraved bust of Carl Friedrich Gauss in old age, dark cap, period clothing, white background, no text.'),
 'accelerator':('63b84230-9f44-44cb-a3c5-19d8f93374f0','Original realistic educational scene of LHC blue superconducting magnet cryostats, coherent gently curved underground tunnel, cables, pipes, walkway; no text or beam outside apparatus.'),
 'lightning':('02223503-1f36-4d8c-98a8-584d1e237a4b','Original realistic cloud-to-ground lightning with irregular branching under storm clouds and distant hills, no text.'),
 'dielectric-meter':('abea9e93-346f-46bc-9ba5-e7f41ec449d3','Original two-state isolated capacitor with high-impedance electrometer; air gap left, dielectric fully filling gap right. Targeted edit rotates RIGHT needle to 10 oclock, leaving LEFT at 2 oclock. No battery; no text.')}
for name,(key,prompt) in assets.items():shutil.copy2(IMG/f'exec-{key}.png',OUT/f'{name}.png')
(OUT/'imagegen-provenance.json').write_text(json.dumps({'tool':'built-in image_gen','assets':{n:{'original':str(IMG/f'exec-{k}.png'),'saved':str(OUT/f'{n}.png'),'prompt_summary':p} for n,(k,p) in assets.items()}},ensure_ascii=False,indent=2))
def graphic(name,width='.78',ext='pdf'):
 return '\\begin{center}\n\\includegraphics[width='+width+'\\linewidth]{'+str(OUT/(name+'.'+ext))+'}\n\\end{center}'
def replace_macro(t,name,body):
 m=re.search(r'\\newcommand\{\\'+name+r'\}\s*\{',t);assert m,name
 _,end=book.balanced_argument(t,m.end()-1)
 return t[:m.start()]+'\\newcommand{\\'+name+'}{%\n'+body+'}\n'+t[end:]
texts={s:(ARCHIVE/'source'/s/'diagrams.tex').read_text() for s in ['thirty-second-section','thirty-third-section','thirty-fourth-section','thirty-fifth-section']}
maps={
 'thirty-second-section':{'dipoleFarFigure':'dipole-far','unequalChargesFigure':'unequal','fieldLineGallery':'field-gallery'},
 'thirty-third-section':{'zeroEquipotentialFigure':'zero-potential','equipotentialGallery':'equipotentials','ionizationEnergyFigure':'ionization','twoLinesFamiliesFigure':'two-lines','finiteRodFamiliesFigure':'finite-rod','rutherfordFigure':'rutherford','apolloniusSphereFigure':'apollonius-example'},
 'thirty-fourth-section':{'groundedSphereImageFigure':'grounded-sphere','uniformFieldSphereFigure':'uniform-sphere','conductorFieldFigure':'conductor-pair'},
 'thirty-fifth-section':{'capacitorFieldFigure':'capacitor-pair','twoCylindersFigure':'two-cylinders','dielectricSphereFieldFigure':'dielectric-sphere'}}
for section,items in maps.items():
 for macro,asset in items.items():texts[section]=replace_macro(texts[section],macro,graphic(asset,'.95' if asset in ['equipotentials','dipole-far','ionization','field-gallery'] else '.76'))
for macro,asset in [('acceleratorTunnelFigure','accelerator'),('lightningFigure','lightning')]:
 texts['thirty-third-section']=replace_macro(texts['thirty-third-section'],macro,graphic(asset,'.76','png'))
texts['thirty-fifth-section']=replace_macro(texts['thirty-fifth-section'],'dielectricMeterFigure',graphic('dielectric-meter','.93','png'))

t=texts['thirty-second-section']
start=t.index(r'  \begin{scope}[shift={(8.55,1.25)}');end=t.index(r'  \end{scope}',start)+len(r'  \end{scope}')
t=t[:start]+r'  \node[inner sep=0pt] at (8.55,1.25) {\includegraphics[width=4.4cm]{'+str(OUT/'quadrupole.pdf')+r'}};'+t[end:]
t=t.replace(r'$\sim10^{-12}\,\mathrm{cm}$',r'$10^{-13}$--$10^{-12}\,\mathrm{cm}$')
t=replace_macro(t,'coulombHistoryFigure',r'''\begin{center}
\begin{minipage}{.21\linewidth}\centering
\includegraphics[width=\linewidth]{'''+str(OUT/'coulomb.png')+r'''}\par\small 库仑
\end{minipage}\hfill
\begin{minipage}{.76\linewidth}\centering
\begin{tikzpicture}[scale=.83]
 \draw[xesline] (-2,3.3)--(2,3.3);
 \draw[xesline] (0,3.3)--(0,.65);
 \draw[xesline] (-1.65,.65)--(1.65,.65);
 \fill[Ink] (-1.65,.65) circle (3pt);\fill[DeepBlue] (1.65,.65) circle (4pt);
 \fill[Gold] (2.3,.65) circle (4pt);\draw[xesline] (2.3,.65)--(2.3,-.5);
 \node[xessmall,above] at (1.65,.82) {$A$};\node[xessmall,above] at (-1.65,.82) {$D$};
 \node[xessmall,right] at (2.45,.65) {$B$};\node[xessmall,left] at (-.18,2.2) {悬丝};
 \node[xessmall,below] at (0,-.7) {侧视：两球同高};
 \begin{scope}[xshift=6.1cm]
  \coordinate(O) at (0,1);\coordinate(A) at (1.8,1.55);\coordinate(D) at (-1.8,.45);\coordinate(B) at (1.9,.6);
  \draw[RuleGray,dashed] (-2.1,1)--(2.1,1);
  \draw[xesline] (D)--(A);\fill[Ink] (O) circle (2pt);
  \fill[DeepBlue] (A) circle (4pt);\fill[Ink] (D) circle (3pt);\fill[Gold] (B) circle (4pt);
  \draw[xesarrow] (A)--($(A)+(-.1,.95)$);
  \draw[RuleGray,dotted] (B)--(A);
  \draw[RuleGray] (.7,1) arc[start angle=0,end angle=17,radius=.7];
  \node[xessmall] at (.96,1.13) {$\theta$};
  \node[xessmall,below] at (O) {$O$};\node[xessmall,left] at (D) {$D$};
  \node[xessmall,right] at ($(A)+(.1,.1)$) {$A$};\node[xessmall,right] at (B) {$B$};
  \node[xessmall,above] at (1.7,2.55) {$\boldsymbol F_{BA}$};
  \node[xessmall,below] at (0,-.7) {俯视：$O$ 为悬丝转轴};
 \end{scope}
\end{tikzpicture}\end{minipage}
\end{center}''')
# Retain all three Gauss teaching panels, replacing only the oversimplified portrait.
start=t.index('  % Gauss profile');end=t.index('  % local surface element',start)
t=t[:start]+r'''  \node[inner sep=0pt] at (1.1,2.05) {\includegraphics[height=2.7cm]{'''+str(OUT/'gauss.png')+r'''}};
  \node[xessmall] at (1.1,.38) {高斯};
'''+t[end:]
# The external point charge has radial straight field lines, not arbitrarily bowed rays.
t=t.replace(r'\draw[fieldline] (-1.58,.14)..controls(-.75,.55)and(.35,.62)..(1.25,.5);',r'\draw[fieldline] (-1.58,.114)--(1.25,.68);')
t=t.replace(r'\draw[fieldline] (-1.58,.1)..controls(-.55,.1)and(.35,.1)..(1.3,.1);',r'\draw[fieldline] (-1.58,.1)--(1.3,.1);')
t=t.replace(r'\draw[fieldline] (-1.58,.06)..controls(-.75,-.45)and(.35,-.55)..(1.25,-.48);',r'\draw[fieldline] (-1.58,.086)--(1.25,-.48);')
texts['thirty-second-section']=t

t=texts['thirty-second-section']
t=t.replace(r'\draw[RuleGray,line width=.75pt,rounded corners=3pt] (0,0) rectangle (11.2,4.1);','')
t=t.replace('at (0,-1.2) {(a) 面元与外法线}', 'at (0,-1.8) {(a) 面元与外法线}')
t=t.replace(r'at (.31,.45) {$\theta_i$}',r'at (.39,.74) {$\theta_i$}')
t=t.replace('at (0,-1.2) {(b) 电荷在闭面内}', 'at (0,-1.8) {(b) 电荷在闭面内}')
t=t.replace('at (0,-1.2) {(c) 电荷在闭面外}', 'at (0,-1.8) {(c) 电荷在闭面外}')
t=t.replace(r'    \fill[DeepBlue] (-.15,.06) circle (5.0pt);\node[xestiny,text=white] at (-.15,.06) {$+$};'+'\n','')
t=t.replace(r'    \node[xessmall] at (0,-1.8) {(b) 电荷在闭面内};',r'    \fill[DeepBlue] (-.15,.06) circle (5.0pt);\node[xestiny,text=white] at (-.15,.06) {$+$};'+'\n'+r'    \node[xessmall] at (0,-1.8) {(b) 电荷在闭面内};')
t=t.replace('at (1.45,1.5) {$\\rho d/\\varepsilon_0$}', 'at (1.55,1.94) {$\\rho d/\\varepsilon_0$}')
t=replace_macro(t,'cavityFigure',r'''\begin{center}
\begin{tikzpicture}[x=1cm,y=1cm]
 \fill[DeepBlue!8] (0,0) circle (2.5);\draw[xesline] (0,0) circle (2.5);
 \fill[white] (.9,.65) circle (1);\draw[xesblue] (.9,.65) circle (1);
 \coordinate(O) at (0,0);\coordinate(C) at (.9,.65);\coordinate(P) at (1.5,.05);
 \foreach \p in {O,C,P}{\fill[Ink] (\p) circle (1.5pt);}
 \node[xessmall] at (-.23,-.22) {$O$};\node[xessmall] at (.88,.93) {$C$};\node[xessmall] at (1.72,-.12) {$P$};
 \draw[xesarrow] (O)--(C);\draw[xesarrow] (O)--(P);\draw[xesarrow] (C)--(P);
 \node[xessmall] at (.25,.58) {$\boldsymbol a$};\node[xessmall] at (.7,-.22) {$\boldsymbol r$};\node[xessmall] at (1.62,.56) {$\boldsymbol r'$};
 \node[xessmall,align=left,anchor=west] at (4,1) {完整均匀球：$+\rho$\\叠加的负球：$-\rho$};
 \node[xessmall,align=left,anchor=west] at (4,-.55) {空腔内 $\boldsymbol r-\boldsymbol r'=\boldsymbol a$，\\因而叠加场为匀强场。};
\end{tikzpicture}
\end{center}''')
# The charge element is positive: its field at P points away from dq, not toward it.
t=t.replace(r'\draw[xesarrow] (P)--++(151.7:1.25);\node[xessmall,anchor=south] at ($(P)+(151.7:1.25)+(0,.12)$) {$\dd\boldsymbol E$};',r'\draw[xesarrow] (P)--++(1.2,-.315);\node[xessmall,anchor=north] at (5.05,-.55) {$\dd\boldsymbol E$};')
t=t.replace(r'(0,-.35)--(4,-.35);\node[xessmall,below] at (2,-.35)',r'(0,-2.6)--(4,-2.6);\node[xessmall,below] at (2,-2.6)')
t=replace_macro(t,'differentialCubeFigure',r'''\begin{center}
\begin{tikzpicture}[x=1cm,y=1cm]
 \coordinate(A) at (0,0);\coordinate(B) at (4,0);\coordinate(C) at (5.25,1.25);\coordinate(D) at (1.25,1.25);
 \coordinate(E) at (0,3.1);\coordinate(F) at (4,3.1);\coordinate(G) at (5.25,4.35);\coordinate(H) at (1.25,4.35);
 \fill[DeepBlue!5] (A)--(B)--(F)--(E)--cycle;
 \fill[DeepBlue!8] (B)--(C)--(G)--(F)--cycle;
 \fill[DeepBlue!11] (E)--(F)--(G)--(H)--cycle;
 \draw[xesline] (A)--(B)--(C)--(G)--(H)--(E)--cycle (B)--(F)--(G) (E)--(F);
 \draw[RuleGray,dashed] (A)--(D)--(C) (D)--(H);
 \node[xessmall] at (1,-.32) {$\Delta x$};
 \node[xessmall,rotate=45] at (4.9,.35) {$\Delta y$};
 \node[xessmall] at (-.4,1.0) {$\Delta z$};
 \draw[xesarrow,dashed] (.625,2.175)--(-1.35,2.175);
 \node[xessmall,anchor=east,align=right] at (-1.45,2.175) {面1\\$E_x(x)$};
 \draw[xesarrow] (4.625,2.175)--(6.15,2.175);
 \node[xessmall,anchor=west,align=left] at (6.25,2.175) {面2\\$E_x(x+\Delta x)$};
 \draw[xesarrow] (2,1.55)--(.8,.35);
 \node[xessmall,anchor=east,align=right] at (-.25,.25) {面3：$E_y(y)$};
 \draw[RuleGray] (-.1,.25)--(.67,.32);
 \draw[xesarrow,dashed] (3.25,2.8)--(4.45,4.0);
 \node[xessmall,anchor=west,align=left] at (5.45,4.2) {面4\\$E_y(y+\Delta y)$};
 \draw[RuleGray] (4.5,4.03)--(5.3,4.2);
 \draw[xesarrow,dashed] (2.625,.625)--(2.625,-.75);
 \node[xessmall,anchor=north] at (2.625,-.82) {面5：$E_z(z)$};
 \draw[xesarrow] (2.625,3.725)--(2.625,5.15);
 \node[xessmall,anchor=south] at (2.625,5.22) {面6：$E_z(z+\Delta z)$};
 \node[xessmall,anchor=east] at (-.35,-.62) {$(x,y,z)$};
 \draw[RuleGray] (-.3,-.5)--(A);
\end{tikzpicture}
\end{center}''')
texts['thirty-second-section']=t

t=texts['thirty-third-section']
t=t.replace(r'\coordinate (A) at (-2.25,.8);',r'\coordinate (A) at ({-3.5*sin(40)},{3.5*(1-cos(40))});')
t=t.replace(r'(.65,0)--(.65,.8)',r'(.65,0)--(.65,{3.5*(1-cos(40))})')
t=t.replace(r'\draw[RuleGray,densely dashed] (S)--(B);',r'''\draw[RuleGray,densely dashed] (S)--(B);
  \draw[RuleGray] (0,2.7) arc[start angle=270,end angle=230,radius=.8];
  \node[xessmall] at (-.4,2.47) {$\theta$};
  \node[xessmall,anchor=south east] at (-1.35,2.1) {$L$};''')
texts['thirty-third-section']=t

t=texts['thirty-fourth-section']
t=t.replace(r'\node[xeslabel] at (4.6,1.75)',r'\node[xeslabel] at (4.6,-.55)')
t=t.replace('(0.53,0)',r'({1.45*1.45/4},0)')
t=t.replace('(-3.93,0)',r'({-1.75*1.75/.78},0)').replace('(-3.93,-.55)',r'({-1.75*1.75/.78},-.55)')
t=t.replace('(0,.647)',r'(0,{1.45*1.45/3.25})').replace('(0,-.647)',r'(0,{-1.45*1.45/3.25})')
texts['thirty-fourth-section']=t

t=texts['thirty-fifth-section']
t=t.replace(r'\fill[DeepBlue!8] (0,0) circle (1.7);\fill[white] (0,0) circle (1.12);','')
t=t.replace(r'(0,0) circle (1.7) (0,0) circle (1.12)',r'(0,0) circle (1.7)')
t=t.replace(r'\node[xessmall] at (0,.65) {中间导体净电荷为零，故两电容电荷量均为 $Q$};',r'\node[xessmall,align=center] at (0,.55) {中间导体净电荷为零\\两电容电荷量均为 $Q$};')
t=t.replace(r'\node[xessmall] at (0,.12) {$U=Q/C_1+Q/C_2$};',r'\node[xessmall] at (0,-.45) {$U=Q/C_1+Q/C_2$};')
t=t.replace('两侧电荷序列都向接触点聚集；标记未加白底','两侧电荷序列都向接触点聚集')
t=t.replace(r'(0,-1.55) arc[start angle=180,end angle=360,x radius=1.45,y radius=.42]',r'(-1.45,-1.55) arc[start angle=180,end angle=360,x radius=1.45,y radius=.42]')
t=t.replace(r'\fill[white] (0,0) circle (.72);','')
t=t.replace(r'\draw[xesblue] (0,0) circle (1.65) (0,0) circle (.72);',r'\draw[xesblue] (0,0) circle (1.65);')
t=t.replace(r'\foreach \a in {0,30,...,330}',r'\foreach \a in {15,45,...,345}')
t=t.replace(r'\draw[Ink,line width=.55pt] (0,0)--(.56,0) node[xestiny,pos=.56,above] {$a$};',r'\draw[Ink,line width=.55pt] (0,0)--(-.56,0);\node[xestiny,above] at (-.28,.05) {$a$};')
t=t.replace(r'\draw[Ink,line width=.55pt] (0,0)--(1.65,0) node[xestiny,pos=.82,below] {$b$};',r'\draw[Ink,line width=.55pt] (0,0)--(1.65,0);\node[xestiny,below] at (1.12,-.04) {$b$};')
# Keep parameter geometry panel; put the independently solved edge field in the right panel.
start=t.index('  % field panel');end=t.index('\n\\end{tikzpicture}',start)
t=t[:start]+r'''  \node[inner sep=0pt] at (3,0) {\includegraphics[width=6.7cm]{'''+str(OUT/'plate-edges.pdf')+r'''}};
'''+t[end:]
texts['thirty-fifth-section']=t
for section,text in texts.items():(book.LEGACY/section/'diagrams.tex').write_text(text)

# Small figure-specific contextual additions in prose (idempotent).
def prose(section,file,old,new):
 p=book.LEGACY/section/file;t=p.read_text()
 if old in t and new not in t:p.write_text(t.replace(old,new))
prose('thirty-second-section','examples.tex','图右侧按这个方程画出典型场线；箭头从 $+q$ 指向 $-q$。','图右侧按这个方程画出理想点偶极子的场线，偶极矩集中于原点；对左侧有限间距的真实电荷，这个近似只用于 $r\\gg l$，不延伸至两电荷附近。')
prose('thirty-second-section','examples.tex','金色虚线是把“终止于 $-q$”与“通向无穷远”分开的分界线。虚线本身也通过零场点，但零场点处方向未定义，\n因此两支只表示同一分界结构的两侧极限。','场线由下文的第一积分计算。通向无穷远与终止于 $-q$ 的场线之间存在分界结构，它趋近零场点；零场点处方向未定义，不能把它当普通连接点。')
prose('thirty-third-section','examples.tex','图中实线等势圆与虚线场线圆处处正交。','图中 $+\\lambda$ 位于右侧，$-\\lambda$ 位于左侧，箭头从正电荷指向负电荷；实线等势圆与虚线场线圆处处正交。')
prose('thirty-third-section','examples.tex','椭圆与双曲线在每个交点正交。','图中粗黑线表示 $-a\\le x\\le a$ 的均匀带电导线（$\\lambda>0$）；实线是等势椭圆，虚线箭头从导线不同位置向外。椭圆与双曲线在每个交点正交。')
prose('thirty-third-section','examples.tex',r'\rutherfordFigure',r'''\rutherfordFigure
图中三条曲线使用同一 $\kappa/(2E_k)=0.7$ 和同一核位置，长度以同一个任意单位表示。
虚线是入射与出射渐近线，$b$ 是入射渐近线到核的垂距；蓝线的 $b$ 最小，因而偏转最大。
''')
prose('thirty-fifth-section','examples.tex','解图：电介质球使外部场线弯曲；球内场仍为匀强场，并弱于外场。','解图：$\\varepsilon_r=4$ 时的电介质球，$+z$ 沿外场。线表示场的方向，线密度不用于跨介质比较 $E$ 的大小；界面处切向 $E$、法向 $D$ 连续。')
prose('thirty-fifth-section','content.tex','右图同时画出中央匀强区和边缘场。','右图为无限延伸方向的截面模型：中央近似匀强，边缘场由同一电势边界求得。')
prose('thirty-fifth-section','content.tex','中央近似匀强，边缘场由同一电势边界求得。','上板带正电、下板带负电；中央近似匀强，边缘场由同一电势边界求得。')
prose('thirty-fourth-section','content.tex','电场线在导体表面垂直入射或出射。','以两球为例，实线为场线、虚线为等势线；电场线垂直球面，延伸到画框外的线并非在框边终止。')
prose('thirty-fifth-section','content.tex','由两个任意形状导体构成的电容器。','双极电容器的两球示例。')
print('All replacements installed; source crops not used.')
