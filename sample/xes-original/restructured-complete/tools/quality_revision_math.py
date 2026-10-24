"""Question and solution illustrations, with explicit mathematical connections."""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parent.parent
MARKER = "% MathQuality20261023"

TITLES = {
 5: "五类函数的差商极限", 6: "乘积法则与链式法则", 7: "从坐标函数求速度与加速度",
 8: "移动半圆柱与竖直杆的约束微分", 9: "透镜像点的有向速度", 10: "光程极值与折射定律",
 11: "两种热力学路径的温度极值", 12: "双星引力的最大值", 13: "抛体包络线与球顶的可达条件",
 14: "侧向弹簧的平衡", 15: "圆锥上环形弹簧的平衡", 16: "弹簧连接双杆的平衡及稳定性",
 17: "相对论能量的低速展开", 18: "恒力相对论位移的低速极限", 19: "射程对初速与角度的灵敏度",
 20: "均匀角分布与壁面接收密度", 22: "直线下的面积", 23: "抛物线下的面积", 24: "圆面积的三种分割",
 25: "圆锥体积的薄片积分", 26: "非均匀密度的质量元", 27: "变力功与气体过程功",
 28: "线性阻力下的减速", 29: "线性阻力下的自由下落", 30: "平方阻力下的速度衰减",
 31: "引力场中的径向自由落体", 32: "衰变的平均规律与半衰期", 33: "弧长元与曲线长度", 34: "光滑轨道上的下落时间",
}

# Body, caption. Existing reviewed geometries are retained and numbered in place.
QUESTION = {
 1: (r"\QMPendulum{0}", r"单摆的长度、质量和重力场；摆角由竖直方向量起。"),
 2: (r"\QMStokes", r"小球与静止流体的题设参数；释放时速度为零。"),
 3: (r"\QMTorque{0}", r"作用点位置与力方向；力对原点的力矩待求。"),
 4: (r"\QMSphere{0}", r"球对称密度只依赖距球心的距离，并在球面降为零。"),
 5: (r"\QMDerivatives{0}", r"五类函数的形状示例：取常数为1、幂指数为2；一般参数仍按题干保留。"),
 6: (r"\QMProduct{0}", r"正值函数的面积示意与复合函数的两级映射；求导法则本身不限于正值函数。"),
 7: (r"\QMMotion{0}", r"三类位置曲线的无量纲示例，横坐标各用本情形的时间尺度，不能比较实际时间数值。"),
 8: (r"\probdiagOneFour", r"半圆柱水平移动而杆的水平坐标固定；角度由竖直半径量起。"),
 9: (r"\QMLens{0}", r"物点向右接近薄凸透镜；图先示意实像分支 $u>f$。"),
 10: (r"\probdiagOneSix", r"跨平面界面的两段光路与可变折射点；高度及水平间距均固定。"),
 11: (r"\probdiagOneSeven", r"直线路径与无量纲圆路径；物理坐标中的后者一般是椭圆。"),
 12: (r"\probdiagOneEight", r"两个等质量天体与垂直平分线上的试探位置。"),
 13: (r"\QMSafety", r"左图为同速轨迹族及题给包络线；右图只示意一条可行命中轨迹，不预设最优。"),
 14: (r"\probdiagOneTen", r"弹簧原长为水平距离 $h$，重物沿竖直直线运动。"),
 15: (r"\probdiagOneEleven", r"母线与轴线夹角为 $\alpha$；环形弹簧位于距顶点竖直距离 $x$ 处。"),
 16: (r"\probdiagOneTwelve", r"两杆长度均为 $l$，底端弹簧原长为零，角度从地面量起。"),
 17: (r"\QMRelativityEnergy{0}", r"相对论总能量含静能，故零速度时图像的纵坐标为1。"),
 18: (r"\QMRelativityMotion{0}", r"恒力位移关系改写为无量纲形式，低速区对应横坐标远小于1。"),
 19: (r"\QMRange{0}", r"同一高度抛出、落地的理想抛体；虚线只示意发射参数发生微小改变。"),
 20: (r"\probdiagOneSixteen", r"壁上小区间与源处小角区间的对应；不能把两种均匀分布混为一谈。"),
 21: (r"\QMPendulum{0}", r"摆球处于极端摆位时 $\theta=\theta_0$；线性化以弧度小角为条件。"),
 22: (r"\areaLineDiagram", r"直线与横轴围成的积分区域；$a,k$ 均为正。"),
 23: (r"\areaParabolaDiagram", r"抛物线与横轴围成的积分区域；$a,k$ 均为正。"),
 24: (r"\circlePartitionsDiagram", r"扇形、薄环与竖直条带三种面积分割，外边界均为半径 $R$ 的圆。"),
 25: (r"\QMCone{0}", r"圆锥与同底等高圆柱的比较参数 $R,H$；坐标 $x$ 从锥顶向下。"),
 26: (r"\QMMassGeometry", r"左为随高度变半径的轴对称物体，右为密度只依赖半径的球体。"),
 27: (r"\QMForceCurves{0}", r"三种给定力函数的示意曲线；各自作正尺度归一化，只示意正位置分支。"),
 28: (r"\QMDragBody{0}", r"正方向沿初速度，线性阻力始终与当前速度反向。"),
 29: (r"\QMFallingDrag{0}", r"下落阶段的受力方向；初始瞬间阻力为零。"),
 30: (r"\QMDragBody{1}", r"本题取 $v_0>0$、$\beta>0$，图中阻力的平方形式只用于正速度分支。"),
 31: (r"\QMRadialInitial", r"试探质点由 $r_0$ 处静止释放；理想中心质点固定在原点。"),
 32: (r"\QMDecay{0}", r"样品中的单个衰变事件随机；微分方程描述未衰变数的期望。"),
 33: (r"\arcLengthDiagram", r"曲线上微小弦段与两个坐标投影；极限中弦长趋于弧长元。"),
 34: (r"\trackTimeDiagram", r"光滑轨道连接 $A(0,H)$ 与 $B(L,0)$，重力竖直向下。"),
 35: (r"\QMPhasorQuestion", r"两个同频量的相量振幅相同、初相差 $2\pi/3$；公共时间因子省略。"),
 36: (r"\QMCooling{0}", r"小物体与恒温环境交换热量；实际传热方向由温差符号决定。"),
}

ANSWER_BODY = {
 1:r"\QMPendulum{1}", 3:r"\QMTorque{1}", 4:r"\QMSphere{1}", 5:r"\QMDerivatives{1}",
 6:r"\QMProduct{1}",7:r"\QMMotion{1}",8:r"\soldiagOneFour",9:r"\QMLens{1}",
 10:r"\QMFermat",11:r"\QMPVExtrema",12:r"\QMGravityMaximum",13:r"\soldiagOneNine",
 14:r"\QMSpringForces",15:r"\QMConeEnergy",16:r"\QMDoubleRodEnergy",17:r"\QMRelativityEnergy{1}",
 18:r"\QMRelativityMotion{1}",19:r"\QMRange{1}",20:r"\soldiagOneSixteen",21:r"\QMSmallAngle",
 22:r"\QMStrip{1}",23:r"\QMStrip{2}",24:r"\circlePartitionsDiagram",25:r"\QMCone{1}",
 26:r"\massElementsDiagram",27:r"\QMForceCurves{1}\pvWorkDiagram",28:r"\QMLinearDrag",
 29:r"\QMFallingDrag{1}",30:r"\QMQuadraticDrag",31:r"\radialFallDiagram",32:r"\QMDecay{1}",
 33:r"\arcLengthDiagram",34:r"\trackTimeSolutionDiagram",36:r"\QMCooling{1}",
}

ANSWER_CAPTION = {
 1:r"长度与重力加速度组合成时间尺度，量纲不能确定右侧的纯数系数。",
 3:r"力的两个坐标分量都产生顺时针转动趋势；$\otimes$ 表示力矩指向纸内。",
 4:r"球壳法：同半径的体积元合并为厚度 $\dd r$ 的完整薄壳。",
 5:r"实线是五类函数的代表曲线，虚线是在同一横坐标处的切线。",
 6:r"乘积增量的两条边带与二阶角块；图示取正增量以便显示面积。",
 7:r"三种归一化运动的一阶导实线与二阶导虚线；图示取正尺度参数，定义见解答正文。",
 8:r"保持接触的杆—圆柱几何约束，位置关系随时间一起变化。",
 9:r"实像右移与虚像右移对应不同的空间含义；两幅图分别使用各自光路。",
 10:r"固定端点、移动折射点的光程变分；入射和折射角均从法线量起。",
 11:r"直线路径上的等温线相切与无量纲圆路径上的两个温度极值。",
 12:r"垂直平分线上的合力大小随距离变化，归一化后峰位与试探质量无关。",
 13:r"允许提前相切时的边界轨迹；相切点与球顶是两个不同的点。",
 14:r"竖直导轨上重物的受力分解：支持力水平，弹簧分量平衡重力。",
 15:r"环形弹簧势能的凸曲线；图取无量纲重力参数 $\eta=1/2$。",
 16:r"双杆系统的内点平衡位于势能极大处，图取 $mg/(kl)=2$。",
 17:r"相对论动能与经典动能比较，二者均已扣除静能。",
 18:r"精确恒力位移与低速抛物线近似；控制参数为 $Ft/(mc)$。",
 19:r"射程的角度响应在 $45^\circ$ 处切线水平，一阶角度灵敏度为零。",
 20:r"壁面区间与源处方向角的微小变化，一阶几何关系给出接收密度。",
 21:r"精确正弦恢复项与小角线性项，横轴统一使用弧度。",
 22:r"直线下的窄矩形条：宽度与取样高度共同组成面积元。",
 23:r"抛物线下的窄矩形条：曲线高度随积分位置改变。",
 24:r"同一个圆的角分割、薄环分割与条带分割，对应三种面积元。",
 25:r"圆锥横截面半径从锥顶线性增长，体积元按半径平方增长。",
 26:r"轴对称物体的薄片与球对称物体的薄壳分别构造质量元。",
 27:r"给定力函数的有向积分区间与气体过程路径；力—位置图面积具有正负号。",
 28:r"线性阻力的时间响应与速度—位置关系；空心点只在无限时间达到。",
 29:r"竖直下落速度单调接近终端值，初始斜率与自由落体加速度相符。",
 30:r"平方阻力的速度按倒数形式衰减，有限时间内保持原运动方向。",
 31:r"径向坐标向外而落体速度向内，时间积分必须处理相反的符号。",
 32:r"未衰变数的连续期望曲线及半高位置，不表示每个样品都按光滑曲线衰变。",
 33:r"局部弧长与两个坐标微元组成直角三角形，再沿整段曲线累加。",
 34:r"轨道下降高度决定速率，局部弧长决定行进距离，二者分工不同。",
 36:r"非零初始温差的统一弛豫曲线；初温等于环境温度时另取恒温解。",
}

EXPLANATIONS = {
 1:"图~\\ref{quality:01:a1}将几何长度与重力加速度合成时间尺度；摆角是无量纲量，量纲方法不能排除周期的振幅依赖，小角条件才将其收敛到常系数极限。",
 3:"图~\\ref{quality:01:a3}中 $F_y<0$ 与 $F_x>0$ 均使该作用点绕原点顺时针转动，故两项 $xF_y$ 与 $-yF_x$ 同为负，与叉积计算相符。",
 4:"图~\\ref{quality:01:a4}的薄壳包含所有同半径的位置，故质量元须乘整个球面面积，不能把径向线积分 $\\int\\rho(r)\\dd r$ 直接当质量。",
 5:"图~\\ref{quality:01:a5}用虚线切线检验差商极限的几何意义；常数曲线切线水平，指数函数的切线斜率随横坐标增大。图中的特定参数只用于展示，不能代替一般常数的极限推导。",
 6:"图~\\ref{quality:01:a6}的两条边带贡献 $g\\Delta f$ 与 $f\\Delta g$，角上的小块为 $\\Delta f\\Delta g$。可导时两增量均为 $O(\\Delta x)$，小块除以 $\\Delta x$ 后趋零；符号变化时仍按代数增量计算。",
 7:"图~\\ref{quality:01:a7}实线是位置对无量纲时间的一阶导，虚线是二阶导。图示取 $a,v_0,A,\\omega,\\beta,m>0$，三图分别取 $s=at/v_0$、$s=\\omega t$ 且 $\\beta/\\omega=1/4$、$s=\\beta t/m$；对应位置归一化为 $ax/v_0^2,x/A,\\beta x/(mv_0)$。零值或其他符号参数仍按正文的一般导数式处理。实际速度、加速度还要乘回各自尺度，不能从无量纲图漏掉链式法则因子。",
 8:"图~\\ref{quality:01:a8}的杆水平坐标固定，而圆柱中心的 $X$ 改变，所以先微分 $X+R\\sin\\theta=\\mathrm{const}$，再微分高度 $R\\cos\\theta$；不能把 $\\theta$ 误当作恒定角速度变量。",
 9:"图~\\ref{quality:01:a9}的两幅图分别表示实像与虚像：同一正号 $\\dot q>0$ 在右半轴表示远离透镜，在左半轴表示靠近透镜。有向坐标使两个分支使用同一公式。",
 10:"图~\\ref{quality:01:a10}中的 $\\delta x$ 只移动折射点而不移动 $A,B$。上段长度一阶变化为 $\\sin\\theta_1\\delta x$，下段为 $-\\sin\\theta_2\\delta x$；光程一阶变化相消便给出折射定律。两段长度的二阶导均为正，所以对这两个固定异侧端点，所得极值是唯一最小值。",
 11:"图~\\ref{quality:01:a11}中温度正比于 $pV$。左图等温双曲线与直线路径在中点相切；右图沿 $p/p_0=V/V_0$ 的两点分别给出最大、最小乘积，两个点都必须检查，不能只求一个驻点。",
 12:"图~\\ref{quality:01:a12}把试探质量记为 $m$，横坐标为题图中的距离 $x$。中心处两引力抵消，远处合力又趋零；在 $x/L=1/\\sqrt2$ 的内部峰值因此具有正确的两端行为。",
 13:"图~\\ref{quality:01:a13}中的球面相切点发生在到达球顶以前。因此该图对应允许提前相切的临界情形；严格不提前接触时，必须采用正文的抬高轨迹极限，不能直接把这幅等号轨迹当成可取的最小值。",
 14:"图~\\ref{quality:01:a14}中导轨支持力水平，不进入竖直平衡式；弹簧拉力的竖直分量为 $F_s x/\\ell$。令它等于 $mg$，与势能驻值条件完全等价，且说明了导轨约束怎样进入计算。",
 15:"图~\\ref{quality:01:a15}取 $\\eta=mg/(2\\pi kL_0\\tan\\alpha)=1/2$ 作形状示意。一般极小值为 $s=1+\\eta$，二阶导为正；图的具体参数不限制正文的一般解。",
 16:"图~\\ref{quality:01:a16}取 $mg/(kl)=2$，内点平衡为 $\\theta=30^\\circ$，对应势能峰顶。求出平衡角不等于证明稳定，正是图中峰与谷的区别。",
 17:"图~\\ref{quality:01:a17}比较的是扣除静能后的动能与经典抛物线。两曲线只在 $|v|/c\\ll1$ 时接近；把总能量直接与经典动能比较，会漏掉常数 $mc^2$。",
 18:"图~\\ref{quality:01:a18}中精确曲线与经典抛物线在 $s\\ll1$ 区域重合至主阶。这里控制展开的是无量纲组合 $Ft/(mc)$，不能单凭“时间短”而忽略力与质量的尺度。",
 19:"图~\\ref{quality:01:a19}的 $45^\\circ$ 处切线水平，所以纯角度误差的一阶贡献为零。若初速固定而 $\\theta=\\pi/4+\\delta\\theta$，则 $S/S_{\\max}=\\cos(2\\delta\\theta)=1-2(\\delta\\theta)^2+O((\\delta\\theta)^4)$，角度必须按弧度代入。",
 20:"图~\\ref{quality:01:a20}的扇形角宽与壁上区间宽度通过斜射几何联系；越偏离法向，相同 $\\Delta x$ 对应的角宽越小，这与接收密度随 $|x|$ 增大而减小的趋势相符。",
 21:"图~\\ref{quality:01:a21}比较精确恢复项与其切线近似。差从三次项开始，而恢复项本身是一阶，故相对修正是二阶；在零点用极限理解这个比值。",
 22:"图~\\ref{quality:01:a22}的窄条高为 $kx$、宽为 $\\dd x$，因此其一阶面积为 $kx\\dd x$。积分区间与题图右边界 $a$ 一致，结果还可由三角形面积直接复核。",
 23:"图~\\ref{quality:01:a23}中不同横坐标的窄条高度是 $kx^2$；累加面积不是用端点高度乘总宽度，因为中间各条的高度并不相同。",
 24:"图~\\ref{quality:01:a24}三种小区域分别对应角变量、半径变量与直角坐标变量。选哪个分割，就使用其自身的面积元与上下限，不能把三种变量的微元混在同一个积分中。",
 25:"图~\\ref{quality:01:a25}的坐标从锥顶向下，故薄片半径与 $x$ 成正比。若把坐标改从底部向上，半径应改为 $R(1-x/H)$，不能仅改积分上下限而保留旧半径式。",
 26:"图~\\ref{quality:01:a26}左图的薄片覆盖整个横截面，右图的薄壳覆盖整个球面；密度在这两种区域内分别近似相同，才可把密度提出对应的体积元。",
 27:"图~\\ref{quality:01:a27}的曲线以下、位置轴以上区域记正功，位于轴下方记负功；气体对外功则按 $p$—$V$ 图面积求取。力函数的符号已由题设给定，不应因“引力”或“分子力”的名称而再任意变号。",
 28:"图~\\ref{quality:01:a28}取 $\\tau=m/\\alpha$。右图的空心端点表示 $x\\to v_0\\tau,v\\to0$ 只在 $t\\to\\infty$ 达到，不能把直线外推到 $x>v_0\\tau$ 后解释为速度反向。",
 29:"图~\\ref{quality:01:a29}中 $\\tau=m/\\alpha$，速度单调接近 $v_\\infty=mg/\\alpha$。曲线初始斜率还原尺度后为 $g$，提供了初值与受力方向的独立检查。",
 30:"图~\\ref{quality:01:a30}在任意有限 $t\\ge0$ 均保持 $v>0$，因此正速度分支的积分自洽。倒数函数的尾部比指数衰减慢，与速度小时平方阻力更弱的物理含义一致。",
 31:"图~\\ref{quality:01:a31}的径向正方向向外，而速度向内，因此 $\\dot r=-v$。将时间积分的上下限翻转为 $0$ 到 $r_0$ 正是这个负号的结果；不能把速率 $v>0$ 直接写成 $\\dot r$。",
 32:"图~\\ref{quality:01:a32}的平滑曲线是期望值，虚线在 $\\lambda t=\\ln2$ 处截出一半高度。单个样品的实际数目为整数并有随机涨落，不能要求它逐点等于连续期望曲线。",
 33:"图~\\ref{quality:01:a33}的直角小三角形满足 $\\dd s^2=\\dd x^2+\\dd y^2$。对 $x_2>x_1$ 取正长度元并累加，才得到根号内含 $1+[y'(x)]^2$ 的弧长积分。",
 34:"图~\\ref{quality:01:a34}将局部弧长与下降高度分别用于 $\\dd s$ 和能量守恒；两种几何量不能用同一个水平位移代替。起点速率为零的奇点仍须按正文检查收敛性。",
 36:"图~\\ref{quality:01:a36}对 $T_0\\ne T_a$ 画出归一化温差，冷却与升温均对应同一正指数曲线；$T_0=T_a$ 时归一化分母为零，应直接使用恒温解而不画这条比值曲线。",
}


def frame(body, caption, label):
    return r"\QMathNamed{" + body + "}{" + caption + "}{" + label + "}"


def apply_chapter_revision(number, text):
    if number != 1 or MARKER in text:
        return text
    matches = list(re.finditer(r"\\begin\{origexamplebox\}", text))
    if len(matches) != 36:
        raise ValueError("chapter 1 example count changed; review ordinal mapping")
    chunks = [text[:matches[0].start()]]
    for no, match in enumerate(matches, 1):
        end = matches[no].start() if no < len(matches) else len(text)
        block = text[match.start():end]
        if no in TITLES:
            block = block.replace(r"\begin{origexamplebox}{}", r"\begin{origexamplebox}{" + TITLES[no] + "}", 1)
        if no == 15:
            block = block.replace("锥角为 $\\alpha$ 的光滑圆锥体", "母线与轴线夹角为 $\\alpha$ 的光滑圆锥体")
            block = block.replace("一段质量为 $m$、等效劲度系数为 $k$、原长为", "一个质量为 $m$、周长方向等效劲度系数为 $k$、原周长为")
            block = block.replace("的弹簧，弹簧始终保持水平。", "的闭合环形弹簧，弹簧始终保持水平。")
            block = block.replace("到锥体顶端的距离 $x$", "到锥体顶端的竖直距离 $x$")
        if no == 17:
            block = block.replace("证明当物体速度远小于光速时，相对论性能量与经典力学动能给出的结果一致。", "证明当物体速度远小于光速时，扣除静能 $mc^2$ 后的相对论动能趋于经典动能。")
        if no == 30:
            block = block.replace("初速度为 $v_0$。", "初速度为 $v_0>0$，取初速度方向为正，$\\beta>0$。", 1)
        if no == 7:
            block = block.replace("在本题给出的运动中 $v>0$ 而 $a<0$", "在 $v_0>0,m>0,\\beta>0$ 的减速分支中 $v>0$ 而 $a<0$")
        if no == 8:
            block = block.replace("求杆上任意一点的速度、加速度与图示角", "在图示 $0<\\theta<\\pi/2$、$v_0>0$ 且保持接触的阶段，求杆上任意一点的速度、加速度与图示角", 1)
        if no == 2:
            block = block.replace("静止流体中由静止释放，且", "静止流体中、远离边界处由静止释放。采用准稳阻力近似，忽略流体附加质量和历史力，且", 1)
        if no == 4:
            block = block.replace("半径为 $R$ 的球体密度", "半径为 $R>0$ 的球体密度", 1)
            block = block.replace("$\\rho(r)=\\rho_0(1-r/R)$。", "$\\rho(r)=\\rho_0(1-r/R)$，其中 $\\rho_0>0$。", 1)
        if no == 31:
            block = block.replace("求它们相撞的时间。", "把两者视为质点，以间距趋于零表示相撞，求这一理想极限的下落时间。", 1)
        if no == 27:
            block = block.replace("分子力 $F=", "给定径向模型力 $F=", 1)
        if no == 34:
            block = block.replace("一条光滑轨道 $y(x)$ 连接", "一条光滑轨道 $y(x)$ 连接", 1)
            block = block.replace("求物体由 $A$ 点从静止出发、沿该轨道下落到 $B$ 点所需的时间。", "设 $y(x)<H$（$0<x\\le L$）。写出物体由 $A$ 点从静止出发、沿该轨道到 $B$ 点的时间积分，并讨论起点切线对自行出发与积分收敛的影响。", 1)
        question, sep, after = block.partition(r"\end{origexamplebox}")
        body, caption = QUESTION[no]
        wrapped = frame(body, caption, f"quality:01:q{no}")
        if body.startswith("\\probdiag") or body in [r"\areaLineDiagram", r"\areaParabolaDiagram", r"\circlePartitionsDiagram", r"\arcLengthDiagram", r"\trackTimeDiagram"]:
            question = question.replace(body, wrapped, 1)
        else:
            question += "\n" + wrapped + "\n"
        # Keep the existing p-V question diagram; the new panels cover its other three subquestions.
        if no == 27:
            question = question.replace(r"\pvWorkDiagram", frame(r"\pvWorkDiagram", "气体过程功由给定路径下的面积计算，膨胀时体积积分方向为正。", "quality:01:q27-pv"), 1)
        sm = re.search(r"\\begin\{xesolution\}(.*?)\\end\{xesolution\}", after, re.S)
        if not sm:
            raise ValueError(f"missing solution {no}")
        answer = sm[1]
        if no in [2, 35]:
            answer = answer.replace(r"\begin{center}", r"\begin{qualityfigure}").replace(r"\end{center}", r"\end{qualityfigure}")
        else:
            body = ANSWER_BODY[no]
            caption = ANSWER_CAPTION[no]
            figure = frame(body, caption, f"quality:01:a{no}")
            if no in [8,13,20,26,31,34]:
                answer = answer.replace(body, figure, 1)
            else:
                answer += "\n" + figure + "\n"
            answer += "\n" + EXPLANATIONS[no] + "\n"
        after = after[:sm.start(1)] + answer + after[sm.end(1):]
        chunks.append(question + sep + after)
    revised = "".join(chunks)
    chapter = re.search(r"\\chapter\{[^\n]*\}", revised)
    revised = revised[:chapter.end()] + "\n\\input{chapters/quality-20261023/ch01-figures.tex}\n" + revised[chapter.end():]
    return MARKER + "\n" + revised


if __name__ == "__main__":
    import argparse
    import subprocess
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-head", action="store_true", help="Rebuild only this owned chapter from reviewed Git baseline")
    args = parser.parse_args()
    path = BOOK / "generated/chapters/ch01.tex"
    source = path.read_text()
    if args.from_head:
        relative = path.relative_to(BOOK.parents[2])
        source = subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=BOOK.parents[2]).decode()
        from quality_revision_20261023 import apply_quality_revision
        source = apply_quality_revision(1, source)
    path.write_text(apply_chapter_revision(1, source))
