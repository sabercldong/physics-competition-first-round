"""Teaching modules: preserve all material while exposing meaningful hierarchy."""
import re

def promote(text,title,new=None):
    old='\\subsection{'+title+'}'
    assert text.count(old)==1,title
    return text.replace(old,'\\section{'+(new or title)+'}',1)

def refine(number,text):
    if number==5:
        for old,new in [('是否滑动？','摩擦约束与平衡临界条件'),('有质量绳的情况','有质量绳的平衡'),('平衡的稳定性','平衡的稳定性')]:
            text=promote(text,old,new)
    elif number==6:
        # A large application section is retained rather than inventing short sections.
        text=text.replace(r'\section{牛顿运动定律应用}',r'\section{牛顿定律的建模方法与典型应用}')
    elif number==7:
        text=promote(text,'质心参考系','质心系与动量分解')
        text=text.replace(r'\subsection{质量变化的情况}',r'\subsection{从封闭系统看质量交换}')
    elif number==8:
        text=promote(text,'不同参考系中的动能定理','功与动能的参考系依赖')
        # Virtual work remains a subsection of the method module, not a short new chapter.
        text=promote(text,'保守力、势能','保守力、势能与稳定性')
    elif number==9:
        text=text.replace(r'\section{角动量}',r'\section{角动量、力矩与参考点}')
        text=promote(text,'有心力、回归点与有效势','角动量守恒与有心力运动')
        text=promote(text,'转动惯量及两条移轴定理','转动惯量、移轴定理与进动')
        text=text.replace(r'\section{刚体动力学}',r'\section{刚体的运动描述}')
        text=promote(text,'刚体的动量与角动量','刚体动力学与纯滚动')
        text=promote(text,'动能、外力功率与转动功','刚体的功、能量与碰撞')
    elif number==12:
        # Work on raw text before chapter-local center/box wrappers are installed.
        a=text.index(r'\section{张紧薄膜的二维波动（选读）}')
        b=text.index(r'\section{流体中的声波与绝热声速}',a)
        advanced=text[a:b];text=text[:a]+text[b:]
        anchor=r'\section{弹性体与波动综合问题}'
        assert text.count(anchor)==1
        text=text.replace(anchor,advanced+'\n'+anchor,1)
        # Old sections become subtopics; existing detailed subsections remain third level.
        text=text.replace(r'\subsection{',r'\subsubsection{')
        text=text.replace(r'\section{',r'\subsection{')
        modules=[
            ('弹性体、物质坐标与小形变','弹性形变、应力与材料定律'),
            ('细杆纵波与弹性能','一维机械波的建立与传播'),
            ('流体中的声波与绝热声速','声波、拍频与多普勒效应'),
            ('声强与声强级','声能传播、声强与声强级'),
            ('波包、相速度与群速度','波包、色散与传播速度'),
            ('管中驻波','边界条件、驻波与反射透射'),
            ('张紧薄膜的二维波动（选读）','二维与三维弹性波（选读）'),
            ('弹性体与波动综合问题','弹性体与波动综合问题')]
        for first,title in modules:
            anchor='\\subsection{'+first+'}'
            if first==title:text=text.replace(anchor,'\\section{'+title+'}',1)
            else:text=text.replace(anchor,'\\section{'+title+'}\n'+anchor,1)
    elif number==13:
        text=text.replace(r'\section{流体运动学}',r'\section{流线、流管与质量流率}')
    return text
