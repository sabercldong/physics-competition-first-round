"""Mechanical repairs and explicit adjacent references for the reviewed figures."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[2]
L23=ROOT/'thirty-ninth-section';L24=ROOT/'fortieth-section'
def edit(p,old,new):
 s=p.read_text();assert old in s,(p,old);p.write_text(s.replace(old,new))
def prep():
 p=L24/'diagrams.tex';s=p.read_text()
 s=re.sub(r'to\[decorate,decoration=\{([^}]+)\}\]\s*(\([^)]*\))',r'decorate[decoration={\1}] {-- \2}',s)
 s=s.replace('(0,-0.35);','(0,-0.30);').replace('(0,0.35)--(0,1.55)','(0,0.30)--(0,1.55)')
 s=s.replace('左移后扩张','近中部左移后收缩').replace('{收缩};','{极外近轴：收缩};').replace('{扩张};','{极外近轴：扩张};')
 s=s.replace('(-2.15,-1.25)--(2.15,-1.25)','({-sqrt(2.5*2.5-1.25*1.25)},-1.25)--({sqrt(2.5*2.5-1.25*1.25)},-1.25)')
 s=s.replace('(-2.19,-1.2)','({-sqrt(2.5*2.5-1.2*1.2)},-1.2)').replace('(2.19,-1.2)','({sqrt(2.5*2.5-1.2*1.2)},-1.2)')
 # Complete circular electric-field lines and make the sign convention explicit.
 s=s.replace('end angle=145,radius=\\r','end angle=180,radius=\\r')
 s=s.replace('感生电场线闭合，不是静电场','图示 $\\dot B>0$ 向纸内；$\\varphi$ 正向为顺时针\\\\感生电场沿逆时针')
 p.write_text(s)
 p=L23/'diagrams.tex';s=p.read_text().replace('(P)--++(0,1.15) node[right] {$B_y$}','(P)--++(0,-1.15) node[right] {$B_y$}')
 p.write_text(s)
 edit(L23/'content.tex','横向无限宽时 $\\theta_1=\\theta_2=\\pi/2$，故','取以垂足为中心、左右等宽同时扩展的无限面极限，先由对称性得 $B_y=0$，再令 $\\theta_1=\\theta_2\\to\\pi/2$，故')
 for p in [L23/'content.tex',L24/'content.tex',L24/'examples-a.tex',L24/'examples-b.tex']:
  s=p.read_text();s=re.sub(r'\\Needspace\{[0-9.]+\\textheight\}',r'\\Needspace{6\\baselineskip}',s)
  s=s.replace('电源极性使 Ampere 力向右','图示正电流沿棒向下，对应 Ampere 力向右')
  p.write_text(s)

FIGS={
23:{
'ampereForceDiagram':('载流子与电流元受力','正载流子的漂移方向向右，磁场向纸内，磁力向上；三者方向用于确定电流元的受力。'),
'bentWireResultDiagram':('弯曲导线合力的端点等效','端点位移 $\\vect L_{ab}$ 从a指向b；只有匀强场中才可把共同的磁场移到积分号外。'),
'loopTorqueDiagram':('矩形线框的力偶与力臂','A、C两侧导线平行转轴，其力不共线；右侧视图的距离 $a\\sin\\theta$ 直接给出力矩。'),
'motorStagesDiagram':('直流电动机的四个转动阶段','阶段2到3之间电流换向，导线电流的点、叉和受力箭头随之同时改变。'),
'ampereLawDiagram':('有向安培环路及穿面电流','环路正向决定纸外电流为正；外部电流虽改变局部场，却不计入所穿净电流。'),
'wireSolenoidDiagram':('直电流与理想螺线管的磁场','右图矩形环路的下边在管内、上边在管外，内部场线没有越出管体；左图虚线表示圆周后半段。'),
'biotSavartDiagram':('源点、切线和磁场叉积方向','源点Q位于导线上，线元取Q处切线；从Q到P的矢量与线元叉乘指向纸外。'),
'loopAxisDiagram':('圆电流对径线元的轴向叠加','Q与对径点 $Q\prime$ 同在圆环上，到P距离相同；两个场的横向分量相消，轴向分量相加。'),
'helmholtzDiagram':('亥姆霍兹线圈间距与三条轴场曲线','两圆心分别在 $\\pm D$；三条曲线均由同一个轴场表达式计算，$D=0.5R$ 的中心二阶曲率为零。'),
'magneticGaussDiagram':('磁体内部与外部的磁感线','内部场从S指向N，外部场回到S；闭合面有穿入也有穿出，不是面上处处无场。'),
'fluxPatchDiagram':('面积微元与局部法向','小面元面积为 $\\dd S$，向量 $\\dd\\vect S$ 沿局部法向，与B的夹角进入 $B\\dd S\\cos\\theta$。'),
'chargeMonopoleComparison':('电荷场与假想磁荷场的比较','上排给出电荷场，下排只是假设磁荷时的类比；两种源汇结构的差别对应两条Gauss定律的右端。'),
'finiteWireDiagram':('有限直电流的两端角度','两个端点角以垂线为基准；场点P在电流右侧，右手规则给出纸内磁场。'),
'currentSheetDiagram':('有限宽电流带的分量积分','左侧宽于右侧，因此积分的法向分量向下；水平分量由各窄条同向叠加。'),
'idealHelixDiagram':('圆环叠加近似与有轴向推进的绕线','左侧仅含方位电流，右侧绕线还沿轴推进；后者的轴向电流决定附加方位场。'),
'resistorGridForceDiagram':('电流网络合力的端点等效','入口和出口位移决定总合力，内部结点的流入流出项成对抵消。'),
'currentElementsDiagram':('两电流元的相互作用力','位置矢量从2指向1，两力分别由各自的双重叉积计算，均垂直于本地电流元。'),
'magneticLensDiagram':('近轴磁透镜的斜率变化','高度为 $\\xi$ 的射线前后斜率为 $\\xi/u$ 与 $-\\xi/v$；图在拉莫尔随动平面内表示聚焦。'),
'spinPrecessionDiagram':('进动与随动系中的自旋翻转','右图B1垂直纸面，转动发生在yz平面，整个过程中 $s_x=0$，不会转成平行B1。')},
24:{
'fluxOrientationDiagram':('回路正向与磁通法向','环路正向和法向按右手规则绑定，负号相对于这套共同约定解释。'),
'motionalRodDiagram':('运动导体棒与闭合电阻回路','棒向右、B向纸内，正电荷磁力沿棒向上，因此环流逆时针，棒受到向左的阻力。'),
'movingLoopDiagram':('匀强场中闭合回路的刚性平移','图示各点速度相同，面积与法向不变，正负的局部动生贡献沿全回路相消。'),
'vortexFieldDiagram':('柱形变磁场内外的涡旋电场','磁场向纸内增强时，电场逆时针；半径R是内外电场公式的分界，不是电场消失的位置。'),
'selfFieldLinesDiagram':('单环与有限螺线管的自生场','单环和多匝线圈都有内部场与外部回流场，同向绕组的内场贡献相加。'),
'selfInductanceDiagram':('螺线管的自生磁链','内部磁场穿过每一匝，磁链要将各匝通量相加，才得到 $\\Lambda=LI$。'),
'mutualInductanceDiagram':('两个同轴回路的互感','两个同向电流的正法向一致，回路1的场穿过回路2，反向激励时交换源和受体。'),
'concentricLoopsDiagram':('同心大小圆环的感应方向','所激励环的顺时针电流增加时，另一环的感应电流为逆时针；交换激励环仍须重算所穿磁通。'),
'magnetThreeLoopsDiagram':('磁铁左移时的三个圆环','轴向箭头描述对相对运动的阻碍；径向标记只适用于图示近轴极外和近中部的局部场条件。'),
'rodResistorDiagram':('导体棒经电阻耗散动能','棒横跨上下导轨，左侧R闭合回路；速度减小导致电流和阻力同时减小。'),
'twoRodDiagram':('同一导轨上的两根导体棒','两个运动边界的电动势相减，驱动量取决于 $v_2-v_1$，不是任一棒的绝对速度。'),
'unequalRodDiagram':('不等宽导轨之间的闭合连接','上下两根过渡导线分别连通；右棒正电流向上、左棒向下，故两棒的安培力方向相反。'),
'rodCapacitorDiagram':('机械等效电容与真实电容的电荷重分配','电容最终电压等于棒的动生电动势；暂态需按文中微小电阻模型理解。'),
'rodInductorDiagram':('导体棒与电感的能量交换','线圈接入回路后，电感电流和棒速度连续变化，动能与磁能相互转化。'),
'rodSourceDiagram':('电源驱动的导体棒','按所标电源极性，正电流在棒中向下；当动生电动势大于电源时，电流可反向。'),
'equivalentCircuitDiagram':('运动导体棒的电学端口等效','机械端口电压 $U_m=BLv$ 与电流关系相当于电容，图中R与该电容串联。'),
'chargedRingDiagram':('小环的角向和径向符号约定','顺时针为角坐标正向，径向向外为正；两个力的代数值按同一径向约定相加。'),
'chordParticleDiagram':('弦上粒子的约束与磁场边界','轨道在圆心下方h处，端点由同一个圆与直线的交点确定；粒子位移不能越过弦端。'),
'chordEmfDiagram':('跨越磁场边界的直导线','A、C为圆与导线的交点，D向右延伸到无穷远；圆外仍需积分涡旋电场。'),
'circularVoltmetersDiagram':('圆形电阻线与三种测量路径','V1、V2的引线分别紧贴两段弧，V3沿两条半径；不同闭合路径对应不同包围面积。'),
'squareVoltmetersDiagram':('四只电压表的真实连接点','所有引线都接到顶点，表与被测边的间距仅为辨认而放大，计算取其所围附加面积趋零。'),
'gridCurrentDiagram':('田字格的外周环流','向纸内磁场增强时，外周逆时针电流产生向纸外的反抗磁场，内部支路电流为零。'),
'solenoidSplitDiagram':('同向串联的两段线圈','分界只是对同一线圈的划分；保持位置时总自感还包括两段互感的两倍。'),
'mutualLoopsProofDiagram':('互感双重积分的源点和场点','两个线元落在各自回路上并取切向，交换下标不改变点积及两点距离。'),
'rlcDiagram':('RLC回路及初始电压参考极性','图示开关已闭合，C为等长双极板，R、L使用独立元件符号；电流正向与初始电压极性共同决定方程。'),
'travelingFieldTrainDiagram':('行波磁场与绝缘机械支承','点、叉区表示某一时刻磁场的相反方向，虚线为零场位置，场图样以相速移动。')}}

def references():
 records=[]
 for n,root,files in [(23,L23,['content.tex']),(24,L24,['content.tex','examples-a.tex','examples-b.tex'])]:
  counts={}
  for name in files:
   p=root/name;s=p.read_text()
   def sub(m):
    macro=m.group(1);args=m.group(2) or ''
    if macro not in FIGS[n]:return m.group(0)
    counts[macro]=counts.get(macro,0)+1
    key=f'ch{n}:fig:review-{macro.lower()}-{counts[macro]}'
    title,desc=FIGS[n][macro]
    records.append({'chapter':n,'macro':macro,'occurrence':counts[macro],'label':key,'caption':title,'adjacent_explanation':desc,'source_file':str(p)})
    return f'图~\\ref{{{key}}}中，{desc}\n\\par\\noindent\\begin{{minipage}}{{\\linewidth}}\n\\{macro}{args}\n\\figcap{{{title}}}\\label{{{key}}}\n\\end{{minipage}}\\par\\medskip'
   s=re.sub(r'(?m)^\\([A-Za-z]+)(\{[01]\})?[ \t]*$',sub,s)
   p.write_text(s)
 out=ROOT/'restructured-complete/build/revision-ch23-ch24-20260922/figure-references.json'
 out.write_text(json.dumps(records,ensure_ascii=False,indent=2))
if __name__=='__main__':prep();references()
