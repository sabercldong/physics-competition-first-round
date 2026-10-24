"""Reproducible corrections and specific TikZ figures for the 15 A5 examples."""
from pathlib import Path
import re

BOOK=Path(__file__).resolve().parent.parent
MARKER="% AdvancedOpticsQuality20261023"
FILES=["A5-geometric.tex","A5-wave.tex","A5-source-interference.tex"]
QBODY={1:r"\QAOFermat{0}",2:r"\QAOBeachQuestion",3:r"\QAOFishQuestion",5:r"\QAOThickQuestion",6:r"\QAOPeriscopeQuestion",
       7:r"\QAOInterfaces{0}",8:r"\QAOStackQuestion",13:r"\QAOMichelsonQuestion",15:r"\QAOCylindersQuestion"}
QCAP={
 1:"变折射率介质中的固定端点与可变路径；虚线是折射率等值线。",
 2:r"水深随离岸距离增大；$\theta$ 从岸线法向量起。",
 3:"球对称折射率的构造问题；图只给物点和不同发射方向，不预设光线路径。",
 4:"圆柱坐标中的螺旋光线及其半径、螺距和切向；端面位于垂直轴线的平面。",
 5:"光从右向左传播；厚目镜两表面、刻线面与物镜孔径的位置及未知尺寸。",
 6:"潜望镜的两反射中心与五片透镜；两次景物实像分别位于两片指定镜面。",
 7:"两平行界面的传播通道及单程相位；幅度系数使用同一能流规范。",
 8:"无限周期双层结构；每一周期的两个折射率与厚度必须分别保留。",
 9:"单缝入射、双缝级联和末端中心；省略号仅省略中间面，不改变面数。",
 10:"狭缝、横移双棱镜组、透镜与屏的器件顺序；单元数仍待求。",
 11:"折射率台阶沿横向分布；每条带内部均匀，透镜用于后焦面观察。",
 12:"球心点源与同心半球薄膜；膜厚为放大的示意量。",
 13:"等倾干涉的两个等效镜面与同一视场内的吞环计数；虚线表示等效延长段。",
 14:r"球面反射点 $P$、平面观察点 $Q$ 与俯视方位角；只示几何，不给条纹公式。",
 15:"两个正交截面中不同的曲率；相切点为原点，箭头表示竖直入射光。",
}
ABODY={1:r"\QAOFermat{1}",2:r"\QAOBeachAnswer",3:r"\QAOFishAnswer",4:r"\QAOHelixAnswer",
       7:r"\QAOInterfaces{1}",8:r"\QAOStackAnswer",9:r"\QAOCascadeAnswer",10:r"\QAOBiprismAnswer",11:r"\QAOGratingAnswer"}
ACAP={
 1:"端点固定的邻近路径变分与局部切向；边界项为零来自端点条件。",
 2:"摆线的向岸分支，箭头指向水深减小的一端；岸边垂直入射为理想模型的极限。",
 3:r"鱼眼光线在同一子午面内的圆轨迹示例；物像满足 $z_i=-a^2/\bar z_0$。",
 4:r"比较出射族的无透镜轮廓与透镜后束腰；图取 $qf/r=1$，不要求 $q=1$。",
 7:"两条透射路径与第一次内部反射；每一新增往返都贡献相同的复数乘子。",
 8:r"定量示例：$n_1/n_2=2$、$n_1d_1=n_2d_2=\lambda_0/4$；阴影内矩阵迹超出传播区间。",
 9:"左为级联的谱选择，右为最终双缝的单色空间条纹；两个不同变量上的峰宽不能混同。",
 10:"四个平移相位单元的简化示意；各段抛物线相同，公共边界上相位连续。",
 11:r"取 $2N=8$：同相时向量相加，第一零点时向量闭合；每条带的公共包络另乘。",
}
EXPLANATIONS={
 1:r"图~\ref{quality:A5:a1}的两条路径共用 $A,B$，所以分部积分的边界项 $[n\vect\tau\cdot\delta\vect r]_A^B$ 消失。局部任意的 $\delta\vect r$ 才迫使积分内的 Euler--Lagrange 余项逐点为零；只比较端点光程不能代替变分。",
 2:r"图~\ref{quality:A5:a2}画的是向岸传播分支，其 $y$ 随传播减小、$x$ 增大，故 $\dd x/\dd y<0$；正文所积正号表达另一支，镜像或反向参数化即得到本图。若沿岸动量常数为零，另有直线 $x=\mathrm{const}$；有限 $y_m$ 的摆线式不覆盖该极限。非常靠近岸边时，破波、黏性及波长与水深变化尺度的比较会使浅水射线近似失效，垂直靠岸是理想模型的外推。",
 3:r"图~\ref{quality:A5:a3}在 $z_0/a=1/2$ 时给出像点 $z_i/a=-2$。所有曲线通过这两个点，是球面上同一对对跖点的大圆投影。这里的成像结论属于几何光学和紧致化的理想光学度量，并未证明真实波场在有限孔径下无衍射。",
 4:r"图~\ref{quality:A5:a4}中两条曲线都以 $\rho(0)=r$ 为起点；透镜增加径向斜率，保留原来的切向斜率，因此最窄处早于 $z=f$，一般也不缩为一点。图取 $qf/r=1$，可同时满足 $r/f\ll1$ 与 $q\ll1$，与近轴假设相容。",
 5:r"图~\ref{advA5:fig:eyepiece-source}中景物像位于右刻线面，而物镜孔径的像位于左出射面；前者给 $y=f_O$，后者给 $1/y+n/x=(n-1)/R'$。这两条不同的共轭关系分别约束成像与通光，不能用一条普通薄透镜关系代替。",
 6:r"图~\ref{advA5:fig:periscope-source}右侧将实际传播折线展开，$a,b$ 分别连接第一像、第二像与中继物镜，因而 $-b/a$ 是景物中继倍率。计算视场时同一光线的入口高度 $u$ 必须贯穿全部镜面约束，这正是式中各个 $h_i(u,\theta)$ 共用同一个 $u$ 的理由。",
 7:r"图~\ref{quality:A5:a7}中第一束在界面1直接反射，第二束先进入中间层，再经界面2反射并从界面1退出。因此第二束的系数同时含 $t_1,t'_1,r_2$ 和往返相位；后续往返再乘 $r'_1r_2\e^{2\ii\delta}$。能流归一化后透射率才可直接写为 $|t|^2$。",
 8:r"图~\ref{quality:A5:a8}的阴影由 $|\operatorname{tr}M/2|>1$ 确定，对应 Bloch 特征值一增一减。有限厚度的无吸收叠层仍可有隧穿透射，禁带不是吸收带；带边的重根也应单独看待，不能从 $K$ 实数就断言任意有限器件都完全透射。",
 9:r"图~\ref{quality:A5:a9}左图以某一谱峰附近的相位失谐为横坐标，展示高次幂选谱；右图固定波长，只剩末端双缝的 $\cos^2$ 空间因子。两者的自变量分别包含 $\lambda$ 和 $y$，因此窄谱峰不能直接当作窄空间条纹。题图~\ref{quality:A5:q9}中的2020个双缝面只有2019次双缝到双缝传播。",
 10:r"图~\ref{quality:A5:a10}中的棱脊 $b_j$ 是相位斜率的折点，而每个区段的中心是抛物线的极小点。公共孔径必须切出这些完整区段，才能将透射场写成相同单元的平移求和；仅把棱镜同轴堆放不会产生该图的多区段结构。",
 11:r"图~\ref{quality:A5:a11}用八条带说明结构因子：$\xi=0$ 时所有相量同向，$\xi=\pi/4$ 时围成闭合八边形。实际强度还要乘单条带的 $\sinc^2$ 包络，不能把相量合成的主峰位置直接当作全部花样的唯一最大值。$\alpha=0$ 时各条带首尾相接且同相，实际退化为总宽 $2Na$ 的单个矩形孔径，而非缝间含不透光间隔的光栅。",
 12:r"图~\ref{advA5:fig:source-ar}中球心到每个界面交点的连线都沿法线，才可把平面膜正入射公式逐点用于半球面。膜厚须远小于球半径，使局部平面膜近似成立；偏离设计波长或把点源移离球心后，零反射条件一般不再同时成立。",
 13:r"图~\ref{advA5:fig:source-michelson}中的固定视场边界决定环数的取整。镜移使中心级次连续改变，吞入20环只给出级次变化，严格唯一的整数答案还需要初末中心亮、视场边界亮等附加约定。大于40度的结果必须使用余弦精确关系。",
 14:r"图~\ref{advA5:fig:source-bump}的 $P\to Q$ 方向决定径向波矢 $k\sin2\theta$，它与入射波在平面内的零切向波矢之差，给出局部条纹间距。俯视图中的 $\phi$ 只改变偏振投影；扩束引起的强度比仍由相同 $\rho$ 的环带面积比计算。",
 15:r"图~\ref{advA5:fig:source-cylinders}的两个正交截面中，曲率分别来自不同表面；膜厚是上表面减下表面，故两项都为正。椭圆长轴沿半径较大的一侧，半轴平方随级次等差，提供了图形方向和系数的直接核对。",
}

def frame(body,caption,label):
    return r"\QAOFrame{"+body+"}{"+caption+"}{"+label+"}"

def apply_file(name,text):
    if MARKER in text:return text
    if name=="A5.tex":
        text=text.replace(r"\AdvancedUnit{5}{光学}",r"\AdvancedUnit{5}{光学}"+"\n\\input{chapters/quality-20261023/advanced-optics/figures.tex}")
    elif name in FILES:
        offset={FILES[0]:0,FILES[1]:6,FILES[2]:11}[name]
        starts=list(re.finditer(r"\\begin\{advexamplebox\}",text));chunks=[text[:starts[0].start()]]
        for local,m in enumerate(starts,1):
            no=offset+local;block=text[m.start():starts[local].start() if local<len(starts) else len(text)]
            q,sep,after=block.partition(r"\end{advexamplebox}")
            sm=re.search(r"\\begin\{advsolution\}(.*?)\\end\{advsolution\}",after,re.S);a=sm[1]
            if no==2:q=q.replace("水深 $H(y)=ay$，$y>0$", "水深 $H(y)=ay$，$a>0,y>0$")
            if no==3:
                q=q.replace("构造一个球对称折射率场，使任一点发出的全部光线在另一点重新会聚。", "在几何光学理想模型中，容许把无穷远补为一个点，构造球对称折射率场，使任意非原点发出的光线在另一点重新会聚，并说明边界与极限。")
                a=a.replace("$n\\to0$，这说明理想分布需要有限边界或镜面截断才能工程实现。", "$n\\to0$。原点的像位于补入的无穷远点；非原点的径向外射线也须按经过该补点的极限理解。实际有限边界或镜面截断会改变部分传播路径和物像关系，必须另解边界问题，不能直接沿用全空间的像点式。")
            if no==4:
                q=q.replace("该层折射率为 $n$。", "该层折射率为 $n$，$r,h>0$。取这条光线绕轴旋转所得的光线族，端面垂直于 $z$ 轴。")
                q=q.replace("所有出射线构成的包络曲面", "这族出射线所在的曲面")
                a=a.replace("右端不超过 $1$", "右端严格小于 $1$")
                a=a.replace("否则发生全反射，题设的出射不成立。", "等号对应临界掠射，不能形成向 $z>0$ 传播的这族光线；大于 $1$ 时发生全反射。")
                a=a.replace(r"q\equiv\tan\theta_t",r"q\equiv|\tan\theta_t|")
            if no==7:q+="\n各介质中的通道均为传播波，选定同一偏振并按单位能流归一化，排除全反射的倏逝通道情形。\n"
            if no==5:
                a=a.replace("原图的“将右侧凸透镜成像至左侧单球面透镜”是\\textbf{物镜孔径的瞳成像}，与景物成像同时发生。不能把它读成目镜右表面向左表面成像。", "本题同时要求\\textbf{物镜孔径的瞳成像}与景物成像。目镜右表面是景物第一像面，左表面是出瞳面，必须分别建立两组共轭关系。")
            if no==10:a=a.replace("原扫描确为 $30^\\circ$，与“全程傍轴”的高精度使用并不相容。", "题给 $30^\\circ$ 与全程傍轴的高精度使用并不相容。")
            if no==8:q+="\n介质均匀、无吸收、非磁且折射率为正，先讨论无限周期结构的 Bloch 模式。\n"
            if no==12:q+="\n球半径远大于膜厚和波长，采用局部平面膜近似。\n"
            if no==13:
                q=q.replace("（原文“一臂透镜”按调节光程差的反射镜理解。）", "")
                q+="\n分别讨论视场边界恰落亮环与仅给定视场内环数两种计数含义。\n"
            if no==15:
                a=a.replace("原资料写作“反射与入射光发生干涉”，但没有给出两束在观察面重合的光路。本题明确采用两相向表面反射形成的空气膜等厚干涉模型；这是对模型的补充限定。", "按题设比较两相向表面的反射光，采用空气膜等厚干涉模型；两束反射光必须在同一观察区域叠加。")
            if no in QBODY:
                q+="\n"+frame(QBODY[no],QCAP[no],f"quality:A5:q{no}")+"\n"
            else:
                # Existing question geometries are correct; retain their editable
                # TikZ, give them a caption in the same scope as the new label.
                source=q if no in [4,9,10,11] else a
                tm=re.search(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",source,re.S)
                if not tm:raise ValueError(f"missing source geometry for A5.{no}")
                cap=QCAP[no]
                if no==9:cap+=r"\label{advA5:fig:cascade-source}"
                framed=frame(tm[0],cap,f"quality:A5:q{no}")
                if source is q:
                    cm=re.search(r"\\begin\{center\}.*?\\end\{center\}",q,re.S)
                    q=q[:cm.start()]+framed+q[cm.end():]
                else:q+="\n"+framed+"\n"
            if no==2:
                cm=re.search(r"\\begin\{center\}.*?\\end\{center\}",a,re.S)
                a=a[:cm.start()]+frame(ABODY[no],ACAP[no],f"quality:A5:a{no}")+a[cm.end():]
            elif no in ABODY:
                a+="\n"+frame(ABODY[no],ACAP[no],f"quality:A5:a{no}")+"\n"
            a+="\n"+EXPLANATIONS[no]+"\n"
            if no==11:
                a=a.replace("可恢复普通 $2N$ 缝光栅", "可恢复 $2N$ 个相邻同相条带，即总宽 $2Na$ 的矩形孔径")
                a+=r"对 $2N\ge2$，上述对称条件也是必要的。令 $M=2N$、$\varphi=kd\alpha a$，结构因子展开为 $G(\xi)=M+2\sum_{j=1}^{M-1}(M-j)\cos(j\xi)$。要求 $G(\varphi-u)=G(\varphi+u)$ 对所有 $u$ 成立，正弦级数的每个系数必须为零；其中 $j=1$ 的系数非零，便有 $\sin\varphi=0$，即 $\varphi=\pi\ell$。公共包络仅在离散点为零，不改变这一整体对称条件。"+"\n"
            after=after[:sm.start(1)]+a+after[sm.end(1):];chunks.append(q+sep+after)
        text="".join(chunks)
        if name=="A5-wave.tex":
            text=text.replace("真空或线性无源介质中的标势、矢势以及电磁场各分量都可归入这一标量框架，", "在均匀、各向同性、线性无源介质中，电磁场各分量满足相应标量 Helmholtz 方程，势函数还须选用相容规范；非均匀介质不能无条件逐分量套用同一标量方程，")
            text=text.replace(r"\e^{\ii k(\theta_xx+\theta_yy)},",r"\e^{\ii k(\theta_xx+\theta_yy)-\ii kz(\theta_x^2+\theta_y^2)/2},")
            anchor=r"\end{advtheorem}"+"\n\n\\noindent\\textit{证明。}\n对 $\\e^{\\ii(\\vect k\\cdot\\vect r-\\omega t)}$"
            note=r"\end{advtheorem}"+"\n\n"+r"上述分式须先乘去分母再按连续极限解释。相速度的完整多项式为 $\sum_i p_i^2\prod_{j\ne i}(v_p^2-v_j^2)=0$；沿主轴或出现相等本征值时，不能在分式形式中直接约去零因子而丢失偏振支。单轴情形可因式分解为 $[v_p^2-v_o^2][v_p^2-v_o^2\cos^2\theta-v_e^2\sin^2\theta]=0$，两支都须保留。射线速度的对偶分式亦须作相同处理。"+"\n\n\\noindent\\textit{证明。}\n对 $\\e^{\\ii(\\vect k\\cdot\\vect r-\\omega t)}$"
            if anchor not in text:raise ValueError("crystal theorem anchor changed")
            text=text.replace(anchor,note,1)
    else:return text
    return MARKER+"\n"+text

def main():
    import argparse,subprocess
    parser=argparse.ArgumentParser();parser.add_argument("--from-head",action="store_true");args=parser.parse_args()
    for name in ["A5.tex"]+FILES:
        p=BOOK/"advanced"/name;old=p.read_text()
        source=subprocess.check_output(["git","show",f"HEAD:{p.relative_to(BOOK.parents[2])}"],cwd=BOOK.parents[2]).decode() if args.from_head else old
        new=apply_file(name,source)
        if new!=old:p.write_text(new)

if __name__=="__main__":main()
