"""Reviewed appendix E corrections and editable question/solution figures."""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parent.parent
MARKER = "% AppendixQuality20261023"

QUESTION = {
 1:r"\QAESources",2:r"\unequalChargeDiagram",3:r"\cavityDiagram",4:r"\dipoleDiagram",
 5:r"\QAESources",6:r"\QAECapacitors{0}",7:r"\QAESplitQuestion",8:r"\QAEInsertQuestion",
 9:r"\QAERCQuestion",10:r"\QAEEarthQuestion",11:r"\QAEVacuumQuestion",12:r"\QAEIonQuestion",
 13:r"\QAERingQuestion",14:r"\QAECube",15:r"\QAELadder{0}",16:r"\QAEThreeRail{0}",17:r"\QAESierpinski",
}
QUESTION_CAPTION = {
 1:"直线、平面、条带与圆盘的题设几何；场点与电荷均不重合，距离为正。",
 2:r"不等量异号电荷位于同一轴线上，$Q>q>0$；场线数仅表示通量比例。",
 3:r"均匀带电绝缘球中的偏心球形空腔；空腔完全处于大球内。",
 4:r"两个等量异号点电荷与远场位置；偶极矩方向由负电荷指向正电荷。",
 5:"有限带电体与无限分布的比较；先确定几何和有限参考点，再求电势差。",
 6:"平行板、同心球与同轴圆柱三种电容器的尺寸；后两图均为中心横截面。",
 7:"半面积填充与半厚度填充；蓝色表示介质，白色表示真空。",
 8:r"介质沿 $+x$ 方向进入，插入长度 $0<x<a$；图中尚未给出受力。",
 9:"初始未充电的电容器与串联电阻、电源；讨论闭合后的过程。",
 10:"地表与等效大气外壳的同心球模型；图中的大气层厚度已放大。",
 11:"阴极、阳极、电势边界与电子运动方向；约定电流大小为正。",
 12:"平行板电离室中电子与离子的两段漂移距离及读出电极。",
 13:"圆环的两个电源接点；接点间不另接短路导线。",
 14:"正方体的十二条电阻棱与八个节点；三种待求端口共用该编号。",
 15:"连接完整的二端梯形网络；横接电阻位于每一节两只串联电阻之后。",
 16:"连接完整的三端无限条带；左端三个端口之间没有直接的竖直电阻。",
 17:"谢尔宾斯基网络的有限阶构造；各阶均采用相同的单位长度电阻。",
}
ANSWER = {
 2:(r"\QAEZeroField","零场点两侧的轴向场与垂直扰动方向；只画零场点邻域的线性结构。"),
 3:(r"\QAECavityVectors",r"带正、负密度的两个完整球叠加；$\vect r=\vect d+\vect r'$。"),
 4:(r"\QAEDipoleComponents","远场中的径向、极角方向及电场分量；图示第一象限。"),
 5:(r"\QAEPotentialPlot",r"正电荷密度时的电势形状；两图的纵向正尺度分别为 $\lambda/(2\pi\varepsilon_0)$、$\sigma/(2\varepsilon_0)$。"),
 6:(r"\QAECapacitors{1}","积分路径沿两极间的场线；同心球与同轴柱使用不同的高斯面积。"),
 7:(r"\splitDielectricDiagram",r"两区域等电压形成并联，两层等法向电位移形成串联；$\varepsilon=\varepsilon_r\varepsilon_0$。"),
 8:(r"\dielectricPullDiagram",r"吸引力指向插入深度增加方向；固定电压时须连同电源功计算。"),
 9:(r"\chargingDiagram","有限电阻充电的三项能量账；先积分，再取电阻趋零极限。"),
 10:(r"\QAEEarthQuestion",r"同一球壳面积 $4\pi r^2$ 分别进入场、电容和漏电电阻，形成几何因子的抵消。"),
 11:(r"\vacuumDiodeDiagram","电子向高电势端加速；电势为非线性分布，电场指向阴极。"),
 12:(r"\ionChamberDiagram","电子与正离子的漂移分别形成快、慢脉冲分量；输出取负电压脉冲的正幅值。"),
 13:(r"\ringResistanceDiagram",r"两段圆弧是同端口并联支路；优化变量满足 $R_1+R_2=R$。"),
 14:(r"\QAECube","按图中节点写基尔霍夫电流定律；表中的电势依次对应三组端口。"),
 15:(r"\QAELadder{1}",r"虚线尾部与原网络相同；第一节之后的横接 $R$ 与尾部 $X$ 并联。"),
 16:(r"\QAEThreeRail{1}\par\QAEThreeReduction",r"三端尾部及其等效三角形；$p/R,q/R$ 均为电导，不能误当电阻。"),
 17:(r"\QAESierpinski","三个半尺度副本组成下一阶；相同单位长度电阻意味着每个副本电阻同时缩小一半。"),
}
EXPLANATION = {
 2:r"图~\ref{quality:appE:a2}中较小负电荷距 $x_0$ 更近，才能与较大的正电荷抵消。令 $A=\partial E_x/\partial x|_{x_0}>0$，无源邻域的轴对称性和 $\nabla\cdot\vect E=0$ 给出横向线性系数 $-A/2$，从而得到图示鞍形方向。电荷之间并不存在这样的零场点。",
 3:r"图~\ref{quality:appE:a3}的两条位置矢量都终止于同一 $P$，相减后只剩与 $P$ 无关的 $\vect d$，这正是空腔内场均匀的原因。若 $\rho<0$，方向随密度符号反转；万有引力对应 $\vect g=-4\pi G\rho_m\vect d/3$。",
 4:r"图~\ref{quality:appE:a4}中 $\theta$ 沿从正极轴转向 $P$ 的方向增大，故 $E_\theta$ 的正方向是逆时针的局部切向。把 $E_r,E_\theta$ 按这两条正交基矢合成，才能得到空间方向。$r=C\sin^2\theta$ 只在理想偶极或远场有效，曲线向 $r\sim l$ 延伸的部分不再代表实际两电荷的近场。",
 5:r"图~\ref{quality:appE:a5}中对数和绝对值曲线在远处均不趋于有限常数，所以不能给它们硬加“无穷远零电势”。求导会消去有限参考点带来的常数，电场不随零点选择而变。平面 $z=0$ 处电势连续、法向导数跳变，与面电荷边界相符。",
 6:r"图~\ref{quality:appE:a6}内外电极之间分别使用平面、球面和柱面对称性。球面面积随 $r^2$ 增长，柱面面积随 $r$ 增长，因而径向积分一个给倒数差、一个给对数；不能仅凭外形把两式套换。",
 7:r"图~\ref{quality:appE:a7}左图沿面积切开，两块介质都连接同一对电极；右图沿厚度切开，中间界面没有自由面电荷，故两层法向 $D$ 相同。这些边界条件分别决定并联和串联，而不是按介质块数判断。",
 8:r"图~\ref{quality:appE:a8}的箭头沿介质右端向电容器内部，即 $x$ 增大方向。力来自插入前缘附近的非均匀边缘场；忽略边缘场对总电容的高阶修正，并不意味着可以在微观受力分析中删去边缘场。虚功法用 $C'(x)$ 保留了该作用的整体效果。",
 9:r"图~\ref{quality:appE:a9}将电源功拆成电场储能与焦耳热。初始未充电是两项各占一半的前提；若电容预先有电压，必须重新计算搬运的电荷和初末储能，不能仍套用这个数值。",
 10:r"图~\ref{quality:appE:a10}中的径向薄壳具有面积 $4\pi r^2$。电阻积分类似串联薄层，电势积分也沿相同半径进行，故 $R_{\rm el}C=\rho\varepsilon_0$ 与球壳的两端半径无关；这要求电阻率在整个壳层内均匀。",
 11:r"图~\ref{quality:appE:a11}中电子速率沿 $+x$ 增大，电势也随 $x$ 增大，但 $E_x=-\varphi'<0$，负电荷所受电力仍沿 $+x$。必须区分电场方向、电子速度方向和电流的大小。",
 12:r"图~\ref{quality:appE:a12}中电子向阳极、正离子向阴极的漂移对负电压脉冲幅值均作正贡献。只有两类载流子全部到达后，路径长度之和才为 $D$，于是开路总幅值与 $x_0$ 无关；有限负载下较早形成的分量已泄放，峰值通常重新依赖位置。",
 13:r"图~\ref{quality:appE:a13}中的两个支路共用 $a,b$，即使两支路沿不同圆弧也仍是并联。恒流和恒压分别约束电源的不同量，所以同一个 $R_{\rm eq}$ 的极大值在两种优化中具有相反的作用。",
 14:r"图~\ref{quality:appE:a14}的八节点在每种端口选择下均满足相同邻接关系。令 $V_{\rm out}=0$、注入电流为 $I_0$，以 $I_0R$ 归一化电势 $u_i=V_i/(I_0R)$；流入端满足 $3u_A-\sum_{j\sim A}u_j=1$，其余非流出节点满足 $3u_i-\sum_{j\sim i}u_j=0$。例如 $AB$ 端口有 $3u_A-u_B-u_D-u_E=1$、$3u_C-u_B-u_D-u_G=0$。解该七元线性方程组得到：\par\begin{center}\begin{tabular}{c|cccccccc}端口 & $u_A$ & $u_B$ & $u_C$ & $u_D$ & $u_E$ & $u_F$ & $u_G$ & $u_H$\\\hline $AB$ & $7/12$&$0$&$5/24$&$3/8$&$3/8$&$5/24$&$1/4$&$1/3$\\ $AC$ & $3/4$&$3/8$&$0$&$3/8$&$1/2$&$3/8$&$1/4$&$3/8$\\ $AG$ & $5/6$&$1/2$&$1/3$&$1/2$&$1/2$&$1/3$&$0$&$1/3$\end{tabular}\end{center}注入端的 $u_A$ 就是 $R_{\rm eq}/R$；逐行代回节点式，可独立复核三个答案。",
 15:r"图~\ref{quality:appE:a15}的虚线框从第一只横接电阻之后开始，故它与该横接电阻是并联关系，端口最前面的两只 $R$ 才是串联。有限节开路截断从 $X_1=3R$ 出发，以 $X_{n+1}=2R+RX_n/(R+X_n)$ 递推，单调下降且有下界 $2R$，所以极限存在并选择正文的正根。",
 16:r"图~\ref{quality:appE:a16}保留尾部的三个端口。还可把三端电导矩阵按上下反射分解：反对称电势型 $(1,0,-1)$ 的特征电导为 $\lambda_1=p+2q$，对称型 $(1,-2,1)$ 的为 $\lambda_2=3p$。一节的两根竖直电阻分别给两模增加 $1,3$，三根水平电阻再各串联单位电阻，故 $\lambda_1=(\lambda_1+1)/(\lambda_1+2)$、$\lambda_2=(\lambda_2+3)/(\lambda_2+4)$。取正根可得 $\lambda_1=(\sqrt5-1)/2$、$\lambda_2=(\sqrt{21}-3)/2$，以及 $p=(\sqrt{21}-3)/6$、$q=(3\sqrt5-\sqrt{21})/12$。端口电流分解到两模后，$R_{AC}/R=2/\lambda_1$，$R_{AB}/R=1/(2\lambda_1)+3/(2\lambda_2)$，从而得到上述两个根式。",
 17:r"图~\ref{quality:appE:a17}每一步都把三个半尺度副本连接成新网络。若小段电阻不随尺度缩短，同样拓扑的递推因子会是 $5/3$；本题固定单位长度电阻，另有长度因子 $1/2$，乘积才为 $5/6$。结论描述这一特定导线模型，不能推广到不同电阻缩放规则的分形材料。",
}

def frame(body, caption, label):
    return r"\QAENamed{" + body + "}{" + caption + "}{" + label + "}"

def apply_revision(text):
    if MARKER in text:
        return text
    text = text.replace("/Users/dongxingxi/Documents/物理竞赛一轮资料/", "../../../")
    text = text.replace(r"(0.55,0)--(-1.1,0)",r"(0.55,0)--(2.2,0)")
    text = text.replace("开尔文的大气球形电容器模型", "理想化的大气球形电容器模型")
    chapter = re.search(r"\\chapter\{[^\n]+\}",text)
    text = text[:chapter.end()]+"\n\\input{chapters/quality-20261023/appendix-e-figures.tex}\n"+text[chapter.end():]
    starts=list(re.finditer(r"\\begin\{origexamplebox\}",text))
    if len(starts)!=17:
        raise ValueError("appendix example mapping changed")
    chunks=[text[:starts[0].start()]]
    for i,m in enumerate(starts,1):
        block=text[m.start():starts[i].start() if i<len(starts) else len(text)]
        q,sep,after=block.partition(r"\end{origexamplebox}")
        if i==1:
            q=q.replace("有限长直导线中垂线外距中点 $a$ 处", "有限长直导线所在直线外、距垂足 $a$ 处（垂足在线段内）")
            q=q.replace("两端对中垂线所张角", "两端相对过垂足法线的张角")
            q=q.replace("仅一个方向无限延伸的均匀带电条带外距条带 $a$ 处", "仅一个方向无限延伸的均匀带电条带所在平面外距平面 $a$ 处（垂足在条带内）")
        if i==6:q=q.replace(r"$l\gg b-a$",r"$l\gg b$")
        if i in [7,8]:q=q.replace(r"$\varepsilon_r$",r"$\varepsilon_r>1$",1)+"\n忽略边缘效应对总电容的修正，介质为均匀线性电介质。\n"
        if i==9:q=q.replace("给电容 $C$ 充电", "给初始未充电的电容 $C$ 充电")
        if i==10:q=q.replace("物理学家开尔文最先把地球和大气层构造为一个电容器模型", "考虑地球与大气的理想化电容器模型")
        if i==12:q+="\n采用小信号近似，阳极初始电势为零，脉冲幅值 $\\Delta U=-\\delta V_{\\rm anode}$；要求 $|\\delta V_{\\rm anode}|\\ll U_0$，从而可将漂移速率视为常量。\n"
        if i in [15,16]:q=re.sub(r"图~\\ref\{[^}]+\}",lambda _:r"图~\ref{quality:appE:q"+str(i)+"}",q,count=1)
        oldq={1:r"\finiteLineDiagram",2:r"\unequalChargeDiagram",3:r"\cavityDiagram",4:r"\dipoleDiagram"}.get(i)
        figure=frame(QUESTION[i],QUESTION_CAPTION[i],f"quality:appE:q{i}")
        q=q.replace(oldq,figure,1) if oldq else q+"\n"+figure+"\n"
        sm=re.search(r"\\begin\{xesolution\}(.*?)\\end\{xesolution\}",after,re.S)
        a=sm[1]
        if i==1:
            a=a.replace("中垂线指向场点", "过垂足指向场点的法线")
            a=a.replace("若线段关于中垂线对称", "若线段关于过垂足的法线对称")
            a=a.replace(r"\lineFieldDiagram",frame(r"\lineFieldDiagram","同轴高斯面只在侧面产生通量。","quality:appE:a1-line"),1)
            a=a.replace(r"\diskFieldDiagram",frame(r"\diskFieldDiagram","圆盘分割为同心圆环，各环横向分量相消。","quality:appE:a1-disk"),1)
            a+="\n"+frame(r"\QAEStrip","条带的线元分割与无限平面的双端面高斯面。","quality:appE:a1")+"\n图~\\ref{quality:appE:a1}左图用 $x=a\\tan\\theta$ 将条带线元换成角度；每条线元的水平场沿场点到线元方向的反向，因此积分后水平分量含对数而非角度和。右图两个端面都要计入通量。图~\\ref{quality:appE:a1-line}与图~\\ref{quality:appE:a1-disk}分别对应同轴高斯法和同心环积分法。\n"
        else:
            body,caption=ANSWER[i]
            old={7:r"\splitDielectricDiagram",8:r"\dielectricPullDiagram",9:r"\chargingDiagram",10:r"\atmosphereCapacitorDiagram",11:r"\vacuumDiodeDiagram",12:r"\ionChamberDiagram",13:r"\ringResistanceDiagram",14:r"\cubeDiagram",15:r"\ladderDiagram",16:r"\threeRailDiagram",17:r"\sierpinskiDiagram"}.get(i)
            aframe=frame(body,caption,f"quality:appE:a{i}")
            if old:a=re.sub(re.escape(old)+r"(?:\\label\{[^}]+\})?",lambda _:aframe,a,count=1)
            else:a+="\n"+aframe+"\n"
            a=re.sub(r"图~\\ref\{appE:fig:[^}]+\}",lambda _:"图~\\ref{quality:appE:a"+str(i)+"}",a)
            a+="\n"+EXPLANATION[i]+"\n"
        if i==3:a=a.replace("方向由大球球心指向空腔球心", "当 $\\rho>0$ 时方向由大球球心指向空腔球心")
        if i==10:a=a.replace(r"r^2}approx",r"r^2}\approx").replace(r"R^2}approx",r"R^2}\approx")
        if i==11:a=a.replace(r"$E=\varphi'$",r"$E_x=-\varphi'$、$|\vect E|=\varphi'$")
        if i==12:a=a.replace("通常 $v^-\\gg v^+$", "当电离位置不紧靠阴极且 $t_-\\ll t_+$ 时")
        if i==14:a=a.replace("以包含两端点的面对角平面作对称，四个中间节点成两个等势组。", "交换端点 $A,C$ 的垂直平分镜面使电势变为 $V_A-V$；$B,D,F,H$ 均位于该镜面上，故都为 $V_A/2$，而 $E,G$ 分别保留。")
        if i==16:a=a.replace("三只纵向电阻和三只\n横向电阻", "三只水平电阻和两只\n竖直电阻")
        if i==17:a=a.replace("网络总导电\n能力则因并联通道数的增长快于单段电阻因缩短而产生的变化，最终等效电阻趋零", "网络电阻的递推则由拓扑因子与长度缩放共同决定，本题每步乘 $5/6$，最终等效电阻趋零")
        after=after[:sm.start(1)]+a+after[sm.end(1):]
        chunks.append(q+sep+after)
    revised=re.sub(r"\\Needspace\{0\.\d+\\textheight\}",lambda _:r"\Needspace{8\baselineskip}","".join(chunks))
    return MARKER+"\n\\begingroup\\tcbset{breakable/.default=false}\n"+revised+"\n\\endgroup\n"

if __name__=="__main__":
    import argparse,subprocess
    ap=argparse.ArgumentParser();ap.add_argument("--from-head",action="store_true");args=ap.parse_args()
    p=BOOK/"generated/appendices/appendix-e.tex";text=p.read_text()
    if args.from_head:
        text=subprocess.check_output(["git","show",f"HEAD:{p.relative_to(BOOK.parents[2])}"],cwd=BOOK.parents[2]).decode()
    p.write_text(apply_revision(text))
