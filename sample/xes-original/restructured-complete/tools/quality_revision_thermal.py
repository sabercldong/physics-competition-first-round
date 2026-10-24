"""Idempotent reviewed revisions for chapters 8--17, 19--20 and advanced A2/A3.

This overlay never edits another chapter and does not regenerate legacy sources.
The editable TikZ definitions live beside the teaching prose under thermal/.
"""
from pathlib import Path
import re

BOOK = Path(__file__).resolve().parent.parent
FOLDER = "chapters/quality-20261023/thermal"
MARKER = "% ThermalQualityRevision20261023-v1"
OWNED = tuple(range(8, 18)) + (19, 20)
ILLUSTRATIONS = {
    8: {5: ("SlidingBoard", None), 6: ("Train", None),
        7: ("AcceleratingTrain", None), 8: ("InverseForce", None),
        9: ("InverseSquareForce", None), 13: ("Conservative", None),
        15: ("Stopping", "Stopping"), 16: (None, "RoughSpring"),
        17: ("Bullet", "Bullet")},
    9: {1: ("Vectors", "Vectors"), 2: ("Area", None), 3: ("Inertias", None),
        4: ("ConePendulum", None), 5: ("Dumbbell", None),
        6: ("Dumbbells", None), 7: ("Seesaws", None), 8: ("ConeBead", None),
        9: ("BrakingWheel", None), 10: ("Wheels", None),
        11: ("Billiard", None), 12: ("Billiards", None),
        14: ("Eggs", None), 15: ("Pulley", None),
        16: ("RodWork", None), 17: ("Percussion", None), 19: ("Chimney", None)},
    10: {1: ("VerticalSpring", None), 2: ("PhysicalPendulum", None),
         3: ("Bandwidth", "Bandwidth"), 4: ("Hardening", "Hardening"),
         9: ("SphereCharges", None), 10: ("SpringPendulum", None)},
    11: {1: ("RadialFall", "RadialFall"), 2: ("Orbit", "Orbit"),
         3: ("Apsides", None), 4: ("Transfer", "Transfer"),
         6: ("MassLoss", "MassLoss"), 7: ("LRL", "LRL"),
         8: ("Dust", None), 9: ("Precession", "Precession"),
         10: ("OrbitDrag", "OrbitDrag")},
    12: {1: ("SelfWeight", None), 2: ("StringFrequency", "StringFrequency"),
         3: ("Pulse", "Pulse"), 4: ("Beats", "Beats"),
         5: ("Doppler", "Doppler"), 6: ("SoundSources", "SoundSources"),
         7: ("SoundDistance", "SoundDistance"), 8: ("DeepWave", "DeepWave"),
         9: ("Cutoff", "Cutoff"), 10: ("ClosedPipe", "ClosedPipe"),
         11: ("ResonanceLength", "ResonanceLength"),
         12: ("StringInterface", "StringInterface"), 15: ("Membrane", None)},
    13: {1: (None, "FlowVolume"), 2: (None, "UniformFlow"),
         3: (None, "FallingFlow"), 4: (None, "FlowMass"),
         5: ("DilutingColumn", "DilutingColumn"),
         6: ("Layers", "Layers"), 7: ("Float", "Float"),
         8: ("Outlet", None), 9: ("Jet", None),
         10: ("MovingPlate", "MovingPlate"), 11: ("Settling", None),
         12: ("Droplets", "Droplets"), 13: (None, "CoupledMercury"),
         14: (None, "Couette"), 15: (None, "Hangar"),
         16: (None, "Funnel"), 17: (None, "Shore"), 18: (None, "Hose")},
    14: {1: ("Composite", "Composite"), 2: ("Mixture", "Mixture"),
         3: ("Expansion", "Expansion"), 4: ("Sensation", None),
         5: ("Meniscus", None), 6: ("GasThermometer", None),
         7: ("Barometer", None), 11: (None, "UTube"),
         13: ("Chain", None)},
    15: {1: ("Conduction", "Conduction"), 2: ("Radiation", "Radiation"),
         3: ("Polytropic", "Polytropic"), 4: (None, "Cycles"),
         5: (None, "HeatCylinder"), 6: ("VariableCapacity", None),
         7: ("ConstantCapacity", "ConstantCapacity"),
         8: ("Atmosphere", None), 9: ("Capillary", None),
         10: ("Bubble", None), 11: ("Fahrenheit", "Fahrenheit")},
    16: {1: ("TwoPaths", "TwoPaths"), 2: ("FiniteWork", "FiniteWork"),
         3: ("Cooling", "Cooling"), 4: ("Carnot", None),
         5: ("SecondLaw", None), 6: ("Irreversibility", None),
         7: ("ThreeBodies", None), 8: ("SurfaceEngine", None)},
    17: {1: ("Condensation", "Condensation"), 2: ("Boiling", "Boiling"),
         3: ("Mercury", None), 4: ("Vaporization", "Vaporization"),
         5: ("WetExpansion", None), 7: ("TwoVessels", None),
         8: ("Cloud", None)},
    19: {1: ("ElectroSystems", None), 2: ("UnequalCharges", None),
         3: ("Cavity", None), 7: ("Potential", None),
         8: ("ZeroPotential", None), 9: ("TwoLines", None),
         10: ("FiniteLine", None), 11: ("ElectronLens", None),
         12: ("SphereEnergy", None), 13: ("Assembly", None),
         15: ("Bohr", None), 16: ("Rutherford", None)},
    20: {1: ("OppositeConductors", None), 2: ("PositiveConductors", "PositiveConductors"),
         3: ("NeutralConductors", "NeutralConductors"), 4: ("LikeAttraction", None),
         6: ("ImageEnergy", "ImageEnergy"), 9: ("PlaneEnergy", None),
         10: ("ConductingSphere", None), 11: (None, "Capacitors"),
         13: (None, "Cylinders"), 14: (None, "ModifiedCapacitor"),
         15: ("DielectricSphere", "DielectricSphere"),
         16: (None, "Insertion"), 17: ("PolarizationEnergy", "PolarizationEnergy"),
         18: ("Charging", "Charging"), 19: (None, "FloatingNode"),
         20: ("CapNetworks", "CapNetworks"), 21: ("EarthCapacitor", "EarthCapacitor")},
}

# Existing analysis figures had no counter or label.  Give each a real figure
# identity and explain the particular geometric element used by its derivation.
ANALYSIS_CAPTIONS = {
    19: {
        2: ("unequalChargesFigure", "异号不等量电荷的场线、零场点及远场。", "两电荷附近必须分别保留各自的距离；远处才可用净电荷 $Q-q$ 判断主导项。零场点处场线切向不再由零矢量唯一指定。"),
        3: ("cavityFigure", "用一个完整正密度球与一个负密度小球表示偏心空腔。", "图中 $O,C,P$ 满足 $\\vect r=\\vect a+\\vect r'$，所以两球内部线性场相减后只剩与观察点无关的 $\\vect a$。金属空腔不能沿用固定体电荷叠加模型。"),
        4: ("chargedSlabFigure", "厚板内外的分段场及负电荷的往复运动。", "边界 $x=\\pm d$ 将运动分成板内线性回复力段和板外恒力段。应先比较板内简谐振幅与 $d$，再决定周期是否需要拼接板外时间。"),
        7: ("potentialMethodFigure", "有限带电体与两种无限体系的电势零点选择。", "有限体系可从无穷远积分，而无限直线和平面的同类积分不收敛；图中的有限参考位置说明应先求电势差，再取梯度，不能把发散的常数当成零。"),
        8: ("apolloniusSphereFigure", "零等势面的距离比与球面截线；等量情形退化为中垂面。", "观察点到两个电荷的距离应分别写成 $r_+,r_-$，零势条件约束的是二者之比。配方时除以 $\\mu^2-1$ 会排除等量情形，因此 $Q=q$ 须回到原式单独讨论。"),
        9: ("twoLinesFamiliesFigure", "两平行异号线电荷的等势线与场线族。", "此截面垂直两根导线，场不含 $z$ 分量。等势线由到两导线的距离比确定，场线在非零场处与其正交；不能将等势圆同时当成场线。"),
        10: ("finiteRodFamiliesFigure", "有限直线电荷的等势线与场线，以两个端点为焦点。", "图中的两个端点距离都随观察点移动。求势时沿整根导线积分，求场线时再利用局部场方向；有限线段不能套用无限导线的纯径向对称。"),
        11: ("electronLensFigure", "弱偏转电子在带电细线附近的冲量近似。", "瞄准参数 $b$ 是未偏转入射直线与细线的垂距。弱场条件允许沿这条近似直线计算横向冲量，再除以初始动量求小角度；它不意味着电子沿真实轨道始终匀速。"),
        12: ("chargedSphereEnergyFigure", "表面电荷球壳与体电荷实心球的场能分布。", "两种分布在 $r>R$ 有相同外场，差别来自球内。场能积分的体积元为 $4\\pi r^2\\dd r$，须在 $r=R$ 分段，不能把球壳内部零场用于绝缘实心球。"),
        13: ("chargeAssemblyFigure", "逐个搬入十个点电荷时相互作用对的计数。", "图中的 $r_{ij}$ 属于一对不同电荷。按搬入次序求和时每对只出现一次；若改为 $\\sum_iQ_i\\varphi_i$，同一对会出现两次，因此总式前须有 $1/2$，且排除点电荷自身发散的势。"),
        15: ("bohrAtomFigure", "玻尔模型中的圆周受力、速度与能量零点。", "向心力箭头沿半径指向原子核，而速度沿切向。圆周条件把库仑势能写成 $-mv^2$，再与正的动能相加，所以相对无穷远静止自由电子的能量为负。"),
        16: ("rutherfordFigure", "固定排斥中心的散射轨道及渐近入射、出射方向。", "冲量参数 $b$ 从入射渐近线量起，散射角则比较两条远处速度方向。把半径 $b$、宽度 $\\dd b$ 的入射环映射到立体角环 $2\\pi\\sin\\theta\\dd\\theta$，即可建立截面变换。"),
    },
    20: {
        1: ("twoConductorPatchFigure", "异号净电荷导体的表面电荷与局部感应。", "$A$ 为最高电势导体时，离开其表面的电势不增，外法向电场因而非负。$B$ 的净电荷只约束表面电荷积分，不能据此禁止图中远侧的局部正电荷斑块。"),
        4: ("chargedIsolatedSphereImageFigure", "孤立同号球的两个辅助像电荷及竞争的吸、斥作用。", "偏心负像电荷满足等势球面条件，球心正像电荷则用来恢复指定净电荷。两个像电荷都只用于球外场；真实点电荷受力应将它们的场相加，而不能把球面感应电荷当作均匀分布。"),
        9: ("planeEnergyFigure", "真实电荷移动时的平面感应分布与有限相互作用能。", "准静态移动时感应分布随真实电荷连续调整；理想化瞬移的初始分布尚对应旧位置。因此比较两过程必须先明确哪些电荷分布被冻结，不能同时对两者套用同一组静电平衡边界条件。"),
        10: ("uniformFieldSphereFigure", "匀强外场中的中性导体球、等势面与表面感应电荷。", "导体球面 $r=R$ 必为等势，内部 $E=0$；球外须同时满足这一边界和远处的 $E_0\\hat{\\vect z}$。先确定偶极项系数，再取径向导数计算表面电荷，才能保证边界条件一致。"),
        12: ("touchingSphereImagesFigure", "相切等势双球的逐次电像构造。", "每次新增像电荷用来修复上一轮在另一球面上破坏的等势条件。两球连接为一个导体，求电容时分母是共同电势，分子必须计入两个球的总电荷。"),
    },
}

MOVE_QUESTION_ANALYSIS = {
    9: {2: "areaVelocityDiagram", 4: "conicalPendulumDiagram",
        5: "dumbbellGroundDiagram", 6: "dumbbellCollisionDiagram",
        7: "seesawDiagram", 8: "funnelDiagram", 9: "brakeWheelDiagram",
        10: "twoWheelsDiagram", 11: "billiardRollingDiagram",
        12: "ballsCollisionDiagram", 14: "eggRollingDiagram",
        15: "massivePulleyDiagram", 16: "torqueWorkDiagram",
        17: "percussionDiagram", 19: "chimneyDiagram"},
}
ANALYSIS_DRAWING_OVERRIDES = {(19, 8): "ThZeroPotentialAnalysisDrawing"}
LEGACY_ANALYSIS_DRAWINGS = {
    19: {"unequalChargesFigure": "ThUnequalAnalysisDrawing",
         "dipoleFarFigure": "ThDipoleAnalysisDrawing",
         "twoLinesFamiliesFigure": "ThTwoLinesAnalysisDrawing",
         "finiteRodFamiliesFigure": "ThFiniteRodAnalysisDrawing",
         "rutherfordFigure": "ThRutherfordAnalysisDrawing"},
    20: {"uniformFieldSphereFigure": "ThUniformSphereAnalysisDrawing"},
}

ADVANCED_ILLUSTRATIONS = {
    "A2": ("A2-thermo.tex", [
        ("EntropyVolume", True), ("GibbsHelmholtz", True), ("SurfaceThermo", True),
        ("GravityHeat", False), ("Superconductivity", True), ("WeissCritical", True),
        ("WeissCurve", False), ("CurieWeiss", True), ("Landau", True),
        ("Homogeneous", True), ("Sackur", True), ("GibbsDuhem", True),
        ("Response", True), ("Compressibilities", True), ("HeatDifference", True)]),
    "A2-statistics": ("A2-statistics.tex", [
        ("Microcanonical", True), ("Grand", True), ("DensityStates", True),
        ("FreePartition", True), ("ClassicalEntropy", True), ("Oscillators", True),
        ("Rotors", True), ("DipoleStatistics", True), ("QuantumDistributions", True),
        ("FermiCapacity", True), ("BoseCapacity", True), ("QuantumVirial", True)]),
    "A3-vector": ("A3-vector.tex", [
        ("Epsilon", True), ("Jacobi", True), ("Derivations", True),
        ("Sensors", True), ("Exterior", True), ("Hodge", True),
        ("RadialHessian", True), ("Green", True)]),
    "A3-pde": ("A3-pde.tex", [
        ("Orthogonal", True), ("SelfAdjoint", True), ("Bessel", True),
        ("Chebyshev", True), ("LegendreRecurrence", True), ("LegendreNorm", True),
        ("DipoleMatrix", True), ("PDETypes", True), ("Dirichlet", True),
        ("Parseval", True), ("GaussianFourier", True), ("BoundaryLift", True),
        ("ForcedWave", True), ("HeatKernel", True), ("AssociatedLegendre", True)]),
}
ADVANCED_MARKER = "% AdvancedThermalQuality20261023-v1"


def move_detached_analysis(text: str) -> str:
    """Legacy captions marked '解图' belong inside the answer, after its heading."""
    pair = re.compile(r"(\\end\{origexamplebox\})(.*?)(\\begin\{xesolution\})", re.S)
    figure = re.compile(r"\\par\\noindent\\begin\{minipage\}\{\\linewidth\}.*?\\end\{minipage\}\\par\\medskip", re.S)

    def move(match: re.Match) -> str:
        end_question, middle, begin_answer = match.groups()
        moved = []

        def detach(block: re.Match) -> str:
            if "解图" in block.group():
                moved.append(block.group())
                return ""
            return block.group()

        middle = figure.sub(detach, middle)
        return end_question + middle + begin_answer + ("\n" + "\n".join(moved) if moved else "")

    return pair.sub(move, text)


def apply_advanced_revision(identifier: str, text: str) -> str:
    """Illustrate and strengthen the owned advanced source fragment."""
    if identifier == "A2-statistics":
        text = text.replace("自由粒子单态配分函数", "自由粒子单粒子配分函数").replace("自由粒子的单态配分函数", "自由粒子的单粒子配分函数")
        text = text.replace(r"""\[
 \boxed{\mu=kT\left[\ln x+\eta\frac{x}{2^{3/2}}\right]},
\]
\[
 \boxed{p=nkT\left[1+\eta\frac{x}{2^{5/2}}\right]},
 \qquad
 \boxed{U=\frac32pV}.
\]
与 $p=nkT-an^2$ 比较，
\[
 \boxed{a(T)=-\eta\frac{kT\lambda_T^3}{2^{5/2}g}}.
\]
费米统计""", r"""\[
 \begin{aligned}
 \mu&=kT\left[\ln x+\eta\frac{x}{2^{3/2}}\right],\\
 p&=nkT\left[1+\eta\frac{x}{2^{5/2}}\right],\qquad U=\frac32pV.
 \end{aligned}
\]
与 $p=nkT-an^2$ 比较，得到 $a(T)=-\eta kT\lambda_T^3/(2^{5/2}g)$。
费米统计""")
    if identifier == "A3-pde":
        text = text.replace(r"-h_{tt}equiv F", r"-h_{tt}\equiv F")
        text = text.replace("求解思路：", "对下列初边值问题建立模态解：")
        text = text.replace("只有特殊退化参数可能偶然化简，不能构成完整多项式族。", "实际上，对本题所给方程，最高次项检查排除了所有非零有限次多项式解。")
    if identifier not in ADVANCED_ILLUSTRATIONS or ADVANCED_MARKER in text:
        return text
    filename, specifications = ADVANCED_ILLUSTRATIONS[identifier]
    text = "\\input{" + FOLDER + "/" + filename + "}\n" + text
    pattern = re.compile(r"(\\begin\{advexamplebox\}.*?)(\\end\{advexamplebox\}.*?\\begin\{advsolution\})(.*?)(\\end\{advsolution\})", re.S)
    index = 0

    def revise(match: re.Match) -> str:
        nonlocal index
        index += 1
        question, separator, answer, end = match.groups()
        name, add_answer = specifications[index - 1]
        if identifier == "A2-statistics" and index == 11:
            answer = re.sub(r"\\begin\{center\}.*?\\end\{center\}", "", answer, flags=re.S)
            answer += "\n图~\\ref{advA2:quality:bose-c-a}的两支在临界点相接；基态在本模型中不贡献激发能，低温热容来自激发态占据随温度改变。\n"
        question += "\n\\AQ" + name + "\n"
        if add_answer:
            answer = "\n\\AA" + name + "\n" + answer
        if identifier == "A2" and index == 7:
            answer += "\n图~\\ref{advA2:fig:weiss-curve}中的纵轴为归一化磁化，临界点左侧由正值连续降至零；平方根律只描述这一邻域，不能外推到全温区。零外场还存在符号相反但能量相同的负磁化支。\n"
        if identifier == "A2-statistics" and index == 2:
            answer = answer.replace(r"由 $\Omega=-kT\ln\Xi=-pV$，", r"由 $\Omega=-kT\ln\Xi$ 及 $p=-(\partial\Omega/\partial V)_{T,\mu}$，")
            answer = answer.replace(r"\boxed{p=\frac{kT}{V}\ln\Xi}", r"\boxed{p=kT\left(\frac{\partial\ln\Xi}{\partial V}\right)_{T,\mu}}")
        if identifier == "A2-statistics" and index == 9:
            answer = answer.replace("玻色式要求 $\\mu$ 不超过基态能量", "有限系统的玻色巨配分级数严格要求 $\\mu$ 低于基态能量（凝聚热力学极限另行处理）")
        return question + separator + answer + end

    text = pattern.sub(revise, text)
    if index != len(specifications):
        raise ValueError(f"{identifier}: expected {len(specifications)} examples, found {index}")
    return ADVANCED_MARKER + "\n" + text


def apply_chapter_revision(number: int, text: str) -> str:
    """Apply only reviewed changes; a repeated application is byte-identical."""
    if number in OWNED:
        text = move_detached_analysis(text)
    if number not in OWNED:
        return text
    if MARKER in text:
        return replace_external_analysis(number, text)
    rules = ILLUSTRATIONS.get(number, {})
    if not rules:
        return text
    heading = re.search(r"\\chapter\{[^\n]*\}", text)
    if heading is None:
        raise ValueError(f"missing chapter heading: {number}")
    text = text[:heading.end()] + f"\n\\input{{{FOLDER}/ch{number:02d}.tex}}\n" + text[heading.end():]
    pattern = re.compile(r"(\\begin\{origexamplebox\}.*?)(\\end\{origexamplebox\}.*?\\begin\{xesolution\})(.*?)(\\end\{xesolution\})", re.S)
    index = 0

    def revise(match: re.Match) -> str:
        nonlocal index
        index += 1
        question, separator, answer, end = match.groups()
        move = MOVE_QUESTION_ANALYSIS.get(number, {}).get(index)
        if move:
            call = "\\" + move
            if call not in question:
                raise ValueError(f"chapter {number}, example {index}: missing {call}")
            question = question.replace(call, "", 1)
            answer = "\n" + call + "\n" + answer
        question_name, answer_name = rules.get(index, (None, None))
        if question_name:
            question += f"\n\\ThQ{question_name}\n"
        if answer_name:
            answer = f"\n\\ThA{answer_name}\n" + answer
        caption_rule = ANALYSIS_CAPTIONS.get(number, {}).get(index)
        if caption_rule:
            macro, caption, explanation = caption_rule
            call = "\\" + macro
            if call not in answer:
                raise ValueError(f"chapter {number}, example {index}: missing {call}")
            label = f"ch{number:02d}:quality:analysis-{index:02d}"
            drawing_call = "\\" + ANALYSIS_DRAWING_OVERRIDES.get((number, index), macro)
            replacement = ("\\begin{qualityfigure}\n" + drawing_call + "\n\\figcap{" + caption +
                           "}\\label{" + label + "}\n\\end{qualityfigure}\n图~\\ref{" + label + "}中，" + explanation)
            answer = answer.replace(call, replacement, 1)
        return question + separator + answer + end

    text = pattern.sub(revise, text)
    missing = set(rules).difference(range(1, index + 1))
    if missing:
        raise ValueError(f"chapter {number}: missing examples {missing}")
    return replace_external_analysis(number, MARKER + "\n" + text)


def replace_external_analysis(number: int, text: str) -> str:
    """Replace six external-PDF answer drawings by their editable TikZ geometry."""
    replacements = LEGACY_ANALYSIS_DRAWINGS.get(number, {})
    def revise_answer(match: re.Match) -> str:
        answer = match.group()
        for old, new in replacements.items():
            answer = answer.replace("\\" + old, "\\" + new)
        return answer
    text = re.sub(r"\\begin\{xesolution\}.*?\\end\{xesolution\}", revise_answer, text, flags=re.S)
    if number == 20:
        text = re.sub(
            r"\\par\\noindent\\begin\{minipage\}\{\\linewidth\}\s*"
            r"(\\begin\{qualityfigure\}.*?\\label\{ch20:quality:analysis-10\}.*?\\end\{qualityfigure\}.*?)"
            r"\\diagramcaption\{匀强电场中的中性导体球。[^\n]*\}\s*\\end\{minipage\}\\par\\medskip",
            lambda match: match.group(1), text, flags=re.S)
    return text.replace("图~\\ref{ch19:quality:analysis-10}中，图中的", "图~\\ref{ch19:quality:analysis-10}中，")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapters", nargs="*", type=int, default=OWNED)
    parser.add_argument("--advanced", action="store_true", help="also revise owned advanced fragments")
    args = parser.parse_args()
    for number in args.chapters:
        if number not in OWNED:
            raise ValueError(f"chapter {number} is outside this overlay")
        path = BOOK / f"generated/chapters/ch{number:02d}.tex"
        old = path.read_text()
        new = apply_chapter_revision(number, old)
        if new != old:
            path.write_text(new)
            print(f"revised ch{number:02d}")
    if args.advanced:
        for identifier in ADVANCED_ILLUSTRATIONS:
            path = BOOK / "advanced" / (identifier + ".tex")
            old = path.read_text()
            new = apply_advanced_revision(identifier, old)
            if new != old:
                path.write_text(new)
                print(f"revised {identifier}")


if __name__ == "__main__":
    main()
