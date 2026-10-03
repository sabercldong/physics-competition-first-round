"""Optics-only structural editing. Stable object labels survive reordering."""
import re
from pathlib import Path

def update_source_maps(number, maps):
    """Preserve source identities after splitting a formerly shared panel."""
    targets={27:{'19.14':'ch27:fig:s42-19-14','19.16':'ch27:fig:s42-19-16'},
             28:{'20.10':'ch28:fig:s43-20-10'},
             29:{'21.4':'ch29:fig:coherence-contrast','21.8':'ch29:fig:moving-source'}}
    for group in maps:
        for obj in group['objects']:
            if obj['source_kind']=='fig' and obj['source_number'] in targets.get(number,{}):
                obj['new_label']=targets[number][obj['source_number']]

# Each replacement is a local correction, not a deletion of a source object.
CORRECTIONS={27:[
 ('它是波面法线在空间中的积分曲线。','在各向同性介质中，它是波面法线在空间中的积分曲线。','区分各向同性介质与晶体中的能流方向'),
 ('光能沿波面的法线方向传播。','在各向同性透明介质中，光能沿波面的法线方向传播。','补足能流与波法线平行的适用条件'),
 ('真实光路使传播时间相对于邻近光路取驻值。','单色光的真实光路使光程相对于邻近光路取驻值；在色散可忽略时，也可表述为传播时间取驻值。','费马原理不把有色散时的相速度当作群速度'),
 ('介质中一段几何路程 $\\dd s$ 的传播时间为 $\\dd t=n\\dd s/c$，因此定义光程','在色散可忽略的静止介质中，一段几何路程 $\\dd s$ 的传播时间为 $\\dd t=n\\dd s/c$。定义光程','限定传播时间公式的适用条件'),
 ('以平界面为例，物点与像点到界面的垂直距离分别为 $a,b$','以平界面为例，界面两侧固定起点与终点到界面的垂直距离分别为 $a,b$','费马变分固定的是两个端点，不预设平界面能严格点成像'),
 ('冲量参数（入射线到球心的距离）','入射高度（入射线到球心的垂直距离）','把容易误解成力学冲量的术语改为直接几何定义'),
 ('冲量参数小于','入射高度小于','与前述几何定义统一'),
 ('因而亮度最大。由','形成明亮的虹带。由','不把几何聚束直接等同实际强度的精确极大位置'),
],30:[
 ('会出现许多级，不利于谱线分离。','会出现许多级；宽波段观察时更需防止不同级次的光谱重叠。这与同一级内的分辨本领不是一回事。','不将级次重叠与单级分辨本领混为一谈'),
 ('但衍射极限是任何无源线性远场成像都不能靠打磨消除的波动下限。','但有限孔径的衍射不能仅靠改善表面打磨消除；这里采用瑞利判据，并不把它当成所有探测和参数估计方法的绝对信息极限。','与后文瑞利判据适用范围一致，避免绝对化'),
]}

def correct(number,text):
    for old,new,reason in CORRECTIONS.get(number,[]):
        assert text.count(old)==1,(number,old,text.count(old))
        text=text.replace(old,new)
    return text

def add_depth(number,text):
    path=Path(__file__).resolve().parents[1]/f'chapters/new/optics-depth/ch{number}.tex'
    before,sections=split_sections(text)
    additions=path.read_text()
    pattern=r'%<(block|append):([^>]+)>\n(.*?)%</\1>'
    remainder=re.sub(pattern,'',additions,flags=re.S)
    # Never silently drop teaching text outside a named insertion block.
    assert not re.sub(r'(?m)^%[^\n]*','',remainder).strip(),(number,'unclassified depth text')
    assert additions.count('%<block:')==additions.count('%</block>'),number
    assert additions.count('%<append:')==additions.count('%</append>'),number
    for mode,title,extra in re.findall(pattern,additions,re.S):
        assert title in sections,(number,title)
        body=sections[title]
        first=re.search(r'\\Needspace\{\d+\\baselineskip\}\\begin\{origexamplebox\}',body) if mode=='block' else None
        at=first.start() if first else len(body)
        # Keep any drawing calls immediately preceding a question next to it.
        prefix=body[:at]
        trailing=re.search(r'(?:\n\\[A-Z][A-Za-z]+\s*)+$',prefix)
        if first and trailing:at=trailing.start()
        sections[title]=body[:at]+'\n'+extra+'\n'+body[at:]
    return before+''.join(section(k,v) for k,v in sections.items())

def reviewed_presentation(number,text):
    text=text.replace(r'\subsection*{',r'\section{')
    for a,b in [('光线的性质','光的描述与光学发展'),('光的干涉','干涉现象与相干条件'),('光的衍射','衍射现象与波动模型')]:
        text=text.replace(r'\section{'+a+'}',r'\section{'+b+'}')
    text=re.sub(r'(\\historyfigure(?:\[[^\]]*\])?\{[^}]+\}\{[^\n]*?)\}\\label\{([^}]+)\}',lambda m:m[1]+r'\label{'+m[2]+'}}',text)
    text=text.replace(r'\begin{center}',r'\begin{center}\begin{minipage}{\linewidth}\centering').replace(r'\end{center}',r'\end{minipage}\end{center}')
    text=r'\begingroup\tcbset{breakable/.default=false}'+'\n'+text+'\n'+r'\endgroup'
    if number!=27:
        text=text.replace(r'\begin{starread}',r'\tcbset{breakable/.default=true}\begin{starread}').replace(r'\end{starread}',r'\end{starread}\tcbset{breakable/.default=false}')
    text=text.replace(r'\end{origexamplebox}',r'\end{origexamplebox}\par\nopagebreak[3]')
    reserve=8 if number in {28,29} else 7
    return text.replace(r'\begin{origexamplebox}',rf'\Needspace{{{reserve}\baselineskip}}\begin{{origexamplebox}}')

def split_sections(text):
    matches=list(re.finditer(r'\\section\{([^}\n]+)\}',text))
    assert len({m[1] for m in matches})==len(matches)
    return text[:matches[0].start()],{m[1]:text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)] for i,m in enumerate(matches)}

def section(title,body):return '\n'+r'\section{'+title+'}\n'+body

def flatten_legacy_group(text):
    from build_restructured import balanced_argument
    start=text.index('\n{\n\\graphicspath')+1
    inner,end=balanced_argument(text,start)
    return text[:start]+inner+text[end:]

def extract_examples(part,label_prefix):
    first=re.search(r'\\Needspace\{\d+\\baselineskip\}\\begin\{origexamplebox\}',part)
    assert first,label_prefix
    theory=part[:first.start()];tail=part[first.start():];q={};at=0
    for end in re.finditer(r'\\end\{xesolution\}',tail):
        block=tail[at:end.end()];at=end.end()
        label=re.search(r'\\label\{'+re.escape(label_prefix)+r'(\d+)\}',block)
        assert label,block[:120]
        q[int(label[1])]=block
    return theory,q,tail[at:]

def restructure_rays(text):
    before,s=split_sections(flatten_legacy_group(text))
    lead,q,tail=extract_examples(s['光路计算与费马原理的应用'],'ch27:ex:s42-19-')
    assert set(q)==set(range(1,14))
    assert not lead.strip() and not tail.strip(),(lead,tail)
    # The two-panel mirror drawing formerly sat immediately before the examples.
    mirror=r'\SphericalMirrorRotatingDiagram'
    s['费马原理（Fermat principle）与光程']=s['费马原理（Fermat principle）与光程'].replace(mirror,'')
    refraction,prism=s['折射'].split('对顶角为 $A$',1)
    return ''.join([before,
      section('光线模型、波面与光学发展',s['光的描述与光学发展']),
      section('反射定律与镜面光路',s['反射']+'\n'+mirror+'\n'+q[1]+q[2]),
      section('折射定律与多界面光路',refraction+q[3]+q[4]+q[9]),
      section('棱镜偏向、色散与彩虹','对顶角为 $A$'+prism+q[11]+q[12]+q[13]),
      section('全反射、临界条件与光纤',s['全反射与光纤']+q[10]),
      section('费马原理与非均匀介质中的光路',s['费马原理（Fermat principle）与光程']+q[6]+q[7]+q[5]+q[8]),
      section('界面上的电磁波与隐失场（选读）',r'\subsection{反射、透射与偏振分量}'+'\n'+s['波动观点下的反射与折射']+r'\subsection{全反射中的隐失场}'+'\n'+s['全反射中的隐失场']),
      section('程函与光线方程（选读）',s['程函方程、光线方程与费马原理'])])

def restructure_imaging(text):
    before,s=split_sections(flatten_legacy_group(text))
    lead,q,tail=extract_examples(s['成像条件与组合系统的计算'],'ch28:ex:s43-20-')
    assert set(q)==set(range(1,10))
    return ''.join([before,
      section('成像概念、光学器件与近轴条件',s['几何光学成像']),
      section('平面界面与视深',s['视深度']),
      section('球面折射与无球差点',s['球面折射']+q[1]+q[6]),
      section('球面镜、薄透镜与物像关系',s['球面镜与平面镜']+s['薄透镜']+q[3]),
      section('组合系统与逐次成像',s['元件组合']+lead+q[2]+q[7]+q[8]+q[9]+tail+r'\subsection{近轴矩阵方法}'+'\n'+s['近轴光线矩阵与理想成像']),
      section('眼睛、视角与放大镜',s['眼睛']+s['放大镜']+s['眼睛与角放大率']),
      section('显微镜与望远镜',r'\subsection{显微镜的中间像与调焦}'+'\n'+s['显微镜']+q[4]+r'\subsection{望远镜的无焦系统与有效倍率}'+'\n'+s['望远镜']+q[5]),
      section('仪器分辨本领与光能探测',s['光谱仪与分辨本领']+s['辐射度学、光度学与探测器'])])

def restructure_diffraction(text):
    before,s=split_sections(flatten_legacy_group(text))
    theory,q,tail=extract_examples(s['单缝、圆孔与分辨率'],'ch30:ex:s45-22-')
    assert set(q)==set(range(10))
    single,resolution=theory.split('任何点物经有限圆孔成像后都成为艾里斑。',1)
    return ''.join([before,
      section('衍射现象与波动模型',s['衍射现象与波动模型']),
      section('单缝衍射与圆孔图样',single+q[0]),
      section('孔径、分辨率与成像限制','任何点物经有限圆孔成像后都成为艾里斑。'+resolution+''.join(q[i] for i in range(1,8))),
      section('多缝干涉与光栅衍射',s['光栅衍射']+q[8]+q[9]+tail),
      section('晶体衍射与布拉格定律',s["周期晶体与布拉格定律（Bragg's law）"]),
      section('偏振态、偏振片与强度',s['线偏振、圆偏振与椭圆偏振']+s['偏振片与马吕斯定律']),
      section('波片与相位延迟',s['波片与相位延迟']+s['快轴、慢轴与波片计算'].removesuffix('\n\\endgroup')),
      section('单轴晶体与双折射',s['单轴晶体与双折射']),
      section('衍射积分与部分相干光（选读）',r'\subsection{衍射积分与傅里叶光学}'+'\n'+s['衍射积分与傅里叶光学图像']+r'\subsection{相干矩阵与部分偏振}'+'\n'+s['相干矩阵与部分偏振'])+'\n'+r'\endgroup'])

def restructure_interference(text):
    # Remove only the legacy unit's redundant enclosing group. The chapter
    # itself remains grouped, so its drawing macros are available after moves.
    text=flatten_legacy_group(text)
    before,s=split_sections(text)
    title='迈克耳孙干涉仪';part=s[title]
    first=part.index(r'\Needspace{8\baselineskip}\begin{origexamplebox}')
    s[title]=part[:first]
    tail=part[first:];ends=list(re.finditer(r'\\end\{xesolution\}',tail));q={};at=0
    for end in ends:
        block=tail[at:end.end()];at=end.end()
        label=re.search(r'\\label\{ch29:ex:s44-21-(\d+)\}',block)
        assert label,block[:120]
        q[int(label[1])]=block
    assert set(q)=={1,3,4,5,6,7,8,9,10,11,12,13,14}
    s[title]+=tail[at:]
    chunks=[before,
      section('干涉现象与相干条件',s['干涉现象与相干条件']),
      section('电场叠加、光程差与干涉强度',s['两束光干涉的一般关系']+q[5]),
      section('杨氏双缝与条纹移动',s['杨氏双缝：分波阵面干涉']+q[1]+q[11]),
      section('虚光源干涉与公共照明区',q[3]+q[6]+q[7]+q[8]+q[9]),
      section('薄膜干涉与增透膜',s['分振幅干涉与薄膜']+q[12]+q[13]),
      section('劈尖与牛顿环',q[4]+q[14]),
      section('迈克耳孙干涉仪与测量',s[title]+q[10]),
      section('复振幅与相干性的定量描述（选读）',s['复振幅与相干性的定量描述'])]
    return ''.join(chunks)

def refine(number,text):
    from optics_solution_review import apply,strip_additions
    text=reviewed_presentation(number,text)
    text={27:restructure_rays,28:restructure_imaging,29:restructure_interference,30:restructure_diffraction}[number](text)
    text=add_depth(number,correct(number,text))
    reviewed=apply(number,text)
    assert strip_additions(reviewed)==text,(number,'solution additions are not reversible')
    from optics_figure_completion import apply as complete_figures,undo as undo_figures
    text=complete_figures(number,reviewed)
    assert undo_figures(number,text)==reviewed
    if number==29:
        # This answer begins with an unbreakable optical diagram. Reserve room
        # for the question and figure, not merely for the word 'solution'.
        # Locate by stable source label, independent of displayed title wording.
        pattern=r'\\Needspace\{8\\baselineskip\}(?=\\begin\{origexamplebox\}[^\n]*\\label\{ch29:ex:s44-21-9\})'
        text,count=re.subn(pattern,lambda _:r'\Needspace{20\baselineskip}',text)
        assert count==1,count
    return text.replace(r'\end{xesolution}\subsection',r'\end{xesolution}'+'\n'+r'\subsection')
