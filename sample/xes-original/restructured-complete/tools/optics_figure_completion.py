"""Explicit, reversible relocation of physical panels; no resampling of rays."""
import re
from pathlib import Path

CHANGES = {}

def replace(text, old, new, reason, changes):
    assert text.count(old) == 1, (reason, text.count(old), old[:100])
    changes.append({'reason': reason, 'before': old, 'after': new})
    return text.replace(old, new, 1)

def split_panel(text, macro, names, captions, labels, destination, changes):
    from build_restructured import balanced_argument
    start = text.index('\\newcommand{\\'+macro+'}')
    body_start=start+len('\\newcommand{\\'+macro+'}')
    _,end=balanced_argument(text,body_start)
    old = text[start:end]
    picture = re.search(r'\\begin\{tikzpicture\}(\[[^\n]+\])\n(.*?)\\end\{tikzpicture\}', old, re.S)
    assert picture
    body = picture[2]
    scopes=[]; depth=0; begin=0
    for token in re.finditer(r'\\(begin|end)\{scope\}(?:\[[^\n]*\])?', body):
        if token[1]=='begin':
            if depth==0: begin=token.end()
            depth+=1
        else:
            depth-=1
            if depth==0: scopes.append(body[begin:token.start()])
    assert len(scopes)==2 and depth==0
    new='\n\n'.join(
        '\\newcommand{\\'+name+'}{%\n'
        '% Independent panel: original physical paths and local coordinates retained.\n'
        '\\begin{center}\\begin{minipage}{\\linewidth}\\centering\n'
        '\\begin{tikzpicture}'+picture[1]+scope+'\\end{tikzpicture}\n'
        '\\figcap{'+cap+'}\\label{'+lab+'}\n\\end{minipage}\\end{center}\n}'
        for name,cap,lab,scope in zip(names,captions,labels,scopes))
    text=replace(text,old,new,'split '+macro+'; retain both complete physical scopes',changes)
    text=replace(text,'\n\\'+macro+'\n','\n\\'+names[0]+'\n','first panel call '+macro,changes)
    # Place the second panel immediately inside its own solution, after the题框.
    p=text.index('\\label{'+destination+'}')
    q=text.index('\\begin{xesolution}',p)+len('\\begin{xesolution}')
    anchor=text[p:q]
    text=replace(text,anchor,anchor+'\n\\'+names[1]+'\n','second panel at '+destination,changes)
    first_targets={
      'ShellAndGradientDiagram':'ch27:ex:s42-19-4',
      'FisherPlateDiagram':'ch27:ex:s42-19-6',
      'SpecialAndCatEyePanel':'ch28:ex:s43-20-6',
      'SilveredAndTrainPanel':'ch28:ex:s43-20-8',
    }
    if macro in first_targets:
        text=replace(text,'\n\\'+names[0]+'\n','\n% Relocated '+names[0]+' to its own solution.\n','avoid first panel stranded before its question: '+macro,changes)
        p=text.index('\\label{'+first_targets[macro]+'}')
        q=text.index('\\begin{xesolution}',p)+len('\\begin{xesolution}')
        anchor=text[p:q]
        text=replace(text,anchor,anchor+'\n\\'+names[0]+'\n','first panel inside '+first_targets[macro],changes)
    return text

def apply(number,text):
    changes=[]
    # Chapter-local elastic reservation, already used elsewhere in this book.
    # The global pagegoal/pagetotal test can see an unshipped full page and
    # force a second break after only a paragraph continuation.
    anchor=r'\begingroup\tcbset{breakable/.default=false}'
    reserve=r'''\renewcommand{\Needspace}[1]{\par\begingroup
\dimen0=#1\relax\vskip0pt plus\dimen0\penalty-100
\vskip0pt plus-\dimen0\vskip\dimen0\penalty9999\vskip-\dimen0
\vskip0pt\endgroup}'''
    text=replace(text,anchor,anchor+'\n'+reserve,'chapter-local elastic page reservation; no shared style edit',changes)
    if number==27:
        text=split_panel(text,'ShellAndGradientDiagram',('AbsorbingShellDiagram','GradientCircleDiagram'),
          ('临界折射线在 $T$ 与半径为 $a$ 的吸收层相切，外球半径为 $b$。',
           '光线从原点水平入射，沿圆心为 $C$ 的圆弧向上弯曲；圆弧切线确定传播方向。'),
          ('ch27:fig:s42-19-13','ch27:fig:s42-19-14'),'ch27:ex:s42-19-5',changes)
        text=replace(text,r'对图~\ref{ch27:fig:s42-19-13} 的圆弧',r'对图~\ref{ch27:fig:s42-19-14} 的圆弧','gradient reference',changes)
        text=split_panel(text,'FisherPlateDiagram',('FisherBayDiagram','ParallelPlateDiagram'),
          (r'湖湾顶角为完整的 $\alpha$，$A,B$ 在陆地；$P,Q$ 为步行与划船的转换点。',
           '玻璃板的入出射方向平行，视像 $I$ 在末段反向延长线上；$S,D,L$ 是三段轴向长度。'),
          ('ch27:fig:s42-19-15','ch27:fig:s42-19-16'),'ch27:ex:s42-19-9',changes)
        text=replace(text,r'参看图~\ref{ch27:fig:s42-19-15} 右侧',r'参看图~\ref{ch27:fig:s42-19-16}','plate reference',changes)
    if number==28:
        text=split_panel(text,'SpecialAndCatEyePanel',('AplanaticLensPanel','CatEyePanel'),
          ('无球差透镜的 $Q$ 为虚像；虚线是出射光反向延长线，$C_1,C_2$ 是两球面曲率中心。',
           '猫眼的两透镜装在同一贯通门孔中；正向观察时光从室外凹透镜传向室内凸透镜。'),
          ('ch28:fig:s43-20-9','ch28:fig:s43-20-10'),'ch28:ex:s43-20-7',changes)
        text=replace(text,r'图~\ref{ch28:fig:s43-20-9} 右侧标出了',r'图~\ref{ch28:fig:s43-20-10} 标出了','cat eye reference',changes)
        text=replace(text,
          r'\node[above,fill=none,inner sep=2pt] at (-1.3333333,0.0000000) {$C_1$};',
          r'\draw[gray,thin](-1.3333333,.04)--(-1.3333333,.52);\node[above,fill=none,inner sep=2pt] at (-1.3333333,.56) {$C_1$};',
          'C1 label outside virtual-ray fan, transparent leader',changes)
        text=split_panel(text,'SilveredAndTrainPanel',('SilveredLensPanel','PrismTrainPanel'),
          ('镀银薄透镜的等效折返光路，实像倒立，像高为物高的三分之一。',
           '累次成像的光轴在棱镜斜面上转过直角；物体 $AB$ 位于棱镜上方。'),
          ('ch28:fig:s43-20-11','ch28:fig:prism-train'),'ch28:ex:s43-20-9',changes)
        text=replace(text,r'图~\ref{ch28:fig:s43-20-11} 右图',r'图~\ref{ch28:fig:prism-train}','prism train reference after split',changes)
        text=replace(text,r'图~\ref{ch28:fig:s43-20-11} 左图',r'图~\ref{ch28:fig:s43-20-11}','silvered lens reference after split',changes)
        text=replace(text,r'\fill(-1.5,0)circle(1.4pt)node[below]{$S=F$};',
          r'\fill(-1.5,0)circle(1.4pt);\node[above left=4pt]at(-1.5,0){$S=F$};',
          'S=F label moved away from lower incident ray',changes)
        extra=(Path(__file__).resolve().parents[1]/'chapters/new/optics-depth/lens-seven-states.tex').read_text()
        anchor=r'\section{组合系统与逐次成像}'
        text=replace(text,anchor,extra+'\n'+anchor,'restore source p22 seven thin-lens states',changes)
        old=r'\Needspace{8\baselineskip}\begin{origexamplebox}{【累次成像】}\label{ch28:ex:s43-20-9}'
        text=replace(text,old,old.replace('8\\baselineskip','22\\baselineskip'),
          'keep prism-train question, solution heading and first diagram together',changes)
    if number==29:
        extra=(Path(__file__).resolve().parents[1]/'chapters/new/optics-depth/coherence-contrast.tex').read_text()
        text=replace(text,'\n\\YoungPatternPanel\n','\n\\YoungPatternPanel\n'+extra+'\n','restore source21.4 laser/ordinary-source visibility distinction',changes)
        text=split_panel(text,'MovingLloydPanel',('MovingSourceDiagram','FiniteLloydDiagram'),
          ('光源上移使零光程差点下移，图中 $P_0$ 表示移动后的中央明纹位置。',
           '有限长劳埃德镜：只有粗线段是真实镜面；两端点反射的边界光线限定屏上的重叠区。'),
          ('ch29:fig:moving-source','ch29:fig:s44-21-8'),'ch29:ex:s44-21-3',changes)
        text=replace(text,'\n\\MovingSourceDiagram\n','\n% Moving-source panel relocated to its solution.\n','remove misplaced moving-source panel from Michelson section',changes)
        p=text.index(r'\label{ch29:ex:s44-21-1}')
        q=text.index(r'\begin{xesolution}',p)+len(r'\begin{xesolution}')
        anchor=text[p:q]
        text=replace(text,anchor,anchor+'\n\\MovingSourceDiagram\n','place moving-source figure in its own solution',changes)
        text=replace(text,'移源图上部画出这种向下补偿的方向',r'图~\ref{ch29:fig:moving-source} 画出这种向下补偿的方向','explicit moving-source reference',changes)
        text=replace(text,"\n\\FiniteLloydDiagram\n",'\n\\FiniteLloydDiagram\n'+r"图~\ref{ch29:fig:s44-21-8} 中的虚源 $S'$、有限镜段与屏上边界确定下面的不等式。"+'\n','explicit Lloyd reference',changes)
        text=replace(text,'\n\\BiprismDiagram\n','\n% Biprism panel relocated to its solution.\n','biprism belongs to its own question',changes)
        p=text.index(r'\label{ch29:ex:s44-21-6}')
        q=text.index(r'\begin{xesolution}',p)+len(r'\begin{xesolution}')
        anchor=text[p:q]
        text=replace(text,anchor,anchor+'\n\\BiprismDiagram\n','biprism inside solution',changes)
        old=r'\Needspace{8\baselineskip}\begin{origexamplebox}{【菲涅耳双棱镜】}'
        text=replace(text,old,old.replace('8\\baselineskip','22\\baselineskip'),'keep biprism solution heading with diagram',changes)
    if number==30:
        text=replace(text,r'\fill[Blue!20,opacity=.45](0,1,0)--(2,1,0)--(2,1,2)--(0,1,2)--cycle;',
          r'\filldraw[fill=Blue!16,draw=Blue!75!black,thin](0,1,0)--(2,1,0)--(2,1,2)--(0,1,2)--cycle;',
          'crystal plane100 readable fill and outline',changes)
        text=replace(text,r'\fill[Gold!30,opacity=.45](0,2,0)--(2,0,0)--(2,0,2)--(0,2,2)--cycle;',
          r'\filldraw[fill=Gold!22,draw=Gold!70!black,thin](0,2,0)--(2,0,0)--(2,0,2)--(0,2,2)--cycle;',
          'crystal plane110 readable fill and outline',changes)
        text=replace(text,
          r'\foreach \y in {-.75,0,.75,1.5,2.25}{\draw[very thick](0,\y-.25)--(0,\y-.08) (0,\y+.08)--(0,\y+.25);}',
          r'\draw[very thick](0,-1.15)--(0,-.08) (0,.08)--(0,1.42) (0,1.58)--(0,2.65);',
          'oblique grating: continuous opaque barrier; A and B are truly adjacent openings',changes)
        text=replace(text,r'\node[left]at(A){$A$};\node[left]at(B){$B$};',
          r'\node[above left=4pt]at(A){$A$};\node[above left=4pt]at(B){$B$};',
          'A and B labels clear incident rays and horizontal normals',changes)
    references={
      28:{'LensImagingDiagram':r'图~\ref{ch28:fig:s43-20-6} 的三条特征光线在同一像点会合；通过物方焦点的光线出射后平行于光轴，不能把它误画成继续通过像方焦点。',
          'SelfConjugateDiagram':r'图~\ref{ch28:fig:self-conjugate} 中 $S=F$ 表示物点恰在透镜的物方焦点；第一次出射为平行光束，折返后再由透镜会聚。'},
      29:{'InterferencePhenomenaPanel':r'图~\ref{ch29:fig:s44-21-2} 把薄膜颜色与连续光谱并列：某处显色来自不同波长的增强或削弱，而不是薄膜只反射一种固定颜色。',
          'PlaneWaveDiagram':r'图~\ref{ch29:fig:s44-21-9} 中两波矢的横向分量相反，因此沿屏移动时两波相位之差持续变化；条纹周期应由这个相位差的变化率求出。',
          'BiprismDiagram':r'图~\ref{ch29:fig:s44-21-10} 的两条反向延长线确定虚源；肥皂膜只覆盖其中一束，因而只给这一束增加光程。',
          'FilmPhenomenaPanel':r'图~\ref{ch29:fig:s44-21-5} 中的薄膜现象都需要比较上下表面反射的两束光；以下计算既计膜内传播，也计反射相变。',
          'NewtonRingsDiagram':r'图~\ref{ch29:fig:newton} 中透镜与平板之间的空气层厚度随离接触点的距离增大；等厚位置成圆，因而干涉条纹呈同心环。',
          'MichelsonDiagram':r'图~\ref{ch29:fig:s44-21-7} 的两臂都往返传播；反射镜沿臂移动距离 $x$，该臂的几何路程改变 $2x$，而不是 $x$。'},
      30:{'BasicDiffractionPanel':r'图~\ref{ch30:fig:s45-22-1} 中虚线只表示几何光学的阴影边界；边界附近的明暗变化需要开放波面上各部分的波相干叠加才能解释。',
          'ResolutionPanel':r'图~\ref{ch30:fig:s45-22-9} 的实线是两个不相干点源的强度之和；比较两峰与中间凹陷，就能看出点源间距改变时分辨程度的变化。',
          'ArrayDiagram':r'图~\ref{ch30:fig:s45-22-10} 中连接不同台站的基线给出相位比较的空间尺度；这些连接线不表示地面上存在连续的反射面。',
          'MolecularLimitDiagram':r'图~\ref{ch30:fig:s45-22-12} 对比分子过程的尺度与普通可见光显微镜的分辨尺度；下面讨论的是能否分开局部结构，不是能否检测到分子发出的光。',
          'GratingDiagram':r'图~\ref{ch30:fig:s45-22-2} 在共同出射波前 $BH$ 上比较两束光：投影段 $AH$ 给出相邻缝的程差，因而必须先确定角度的基准线。',
          'BraggDiagram':r'图~\ref{ch30:fig:s45-22-7} 的 $HB$ 与 $BK$ 是下层光路多出的两段；各为 $d\sin\theta$，相加才得到布拉格公式中的因子 $2$。',
          'ObliqueGratingDiagram':r'图~\ref{ch30:fig:s45-ex-22-9} 中 $A,B$ 是相邻透光缝；入射波到达两缝时已有相位差，不能只比较两缝到屏的传播路程。'}
    }
    for macro,prose in references.get(number,{}).items():
        call='\n\\'+macro+'\n'
        text=replace(text,call,call+prose+'\n','explicit physical use of '+macro,changes)
    for label,prose in {
      27:[('ch27:fig:s42-19-2',r'图~\ref{ch27:fig:s42-19-2} 将反射定律放到实验和装置中：潜望镜利用多次反射改变光路，月面反射器用于激光往返测距；逐个反射面都要以该面的法线量角。')],
      30:[('ch30:fig:s45-22-5',r'图~\ref{ch30:fig:s45-22-5} 的衍射斑点对应满足相位匹配的方向；劳厄实验利用这些离散方向揭示晶体内部的周期结构。')]
    }.get(number,[]):
        line=next(x for x in text.splitlines() if x.startswith(r'\historyfigure') and r'\label{'+label+'}' in x)
        text=replace(text,line,line+'\n'+prose,'reference existing scene '+label,changes)
    CHANGES[number]=changes
    return text

def undo(number,text):
    for change in reversed(CHANGES.get(number,[])):
        assert text.count(change['after'])==1,change['reason']
        text=text.replace(change['after'],change['before'],1)
    return text
