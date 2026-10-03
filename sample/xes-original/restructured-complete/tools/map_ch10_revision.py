"""Materialize a manually reviewed, page-by-page teaching-object map.

This is an evidence index, not an automated assertion of word-for-word equality.
Source figures are compared individually; newly added figures cannot offset one.
"""
from pathlib import Path
import hashlib,json,re
BOOK=Path(__file__).resolve().parent.parent
SRC=Path('/Users/dongxingxi/Downloads/学而思资料/二轮')
pages={
73:('foundations','振幅、平衡位置、相位与初相位|复物理量、复振幅及取实部|复表示的一阶、二阶导数|位移、速度和加速度关系'),
74:('foundations','状态反求相位与多值分支|连续相位和两状态历时|线性回复判据及证明|平方和判据及分段积分证明|实部平方不能当复数平方的实部'),
75:('foundations','稳定平衡条件|势能二阶展开|坐标相关等效惯量和小振动频率|单摆能量与周期|有限摆幅误差及10度换算'),
76:('damping','线性黏滞阻力模型|阻尼系数、衰减参数及固有频率|特征方程|欠阻尼通解'),
77:('damping','过阻尼双指数通解|临界阻尼通解及重根极限|最快回归说法的比较条件|衰减包络与弛豫时间|弱阻尼能量分析'),
78:('damping','品质因数与每周期损耗|阻尼螺旋相图|速度相位偏离与损耗角|归一化椭圆的交叉项及轴方向'),
79:('damping','自由暂态加受迫稳态|复振幅代入求解|振幅与相位|低中高频响应及分支'),
80:('damping','位移共振及其存在条件|速度与功率共振|输入功率的周期平均|洛伦兹型近峰曲线'),
81:('damping','高斯型与洛伦兹型线宽对比|半高全宽|峰高与线宽归一化|品质因数的谱线解释'),
82:('modes','多自由度平衡与二阶动能势能|惯性矩阵与弹性矩阵元素|混合偏导与矩阵对称性'),
83:('modes','耦合摆实际弹簧长度|耦合摆完整能量和二阶矩阵|双摆下球速度与动能交叉项|双摆势能和两矩阵对比'),
84:('modes','逐变量配方与对角化|动能正定和退化|冗余或奇异坐标|势能负方向、零方向和高阶稳定性'),
85:('modes','双摆配方后势能重新耦合|正逆坐标变换|二次型矩阵形式|合同变换|广义本征问题的物理意义'),
86:('modes','拉格朗日方程至矩阵运动方程|行列式为零|不同特征值质量正交证明|简并子空间正交化|模态矩阵给出两能量对角元'),
87:('modes','双摆二次特征方程|两个频率和振幅比|变换矩阵与逆变换|简正坐标'),
88:('modes','双摆变换后两能量|独立模态方程和通解|简正坐标、简正频率、简正模三概念|初始状态决定各模叠加|耦合摆对称模式方法'),
89:('modes','耦合摆同相反相频率|苯分子至六坐标模型的限制|环模型能量和动力学|循环指标'),
90:('modes','六重和两类二重轴操作|能量不变性与非对称交换的区别|方程对称性不保证任意初态对称|对称操作保频与简并'),
91:('modes','六次单位根投影与共同本征向量|二重轴正负本征值|单重态的符号分类|交替态与整体转动零模'),
92:('modes','两个二重简并代表态|零位移点的力抵消|各代表态牛顿方程|旋转产生伙伴|二次旋转的线性关系|六模完备列表'),
93:('modes','群与群表示的用途|12原子36坐标减6刚体自由度|20组30个内部振动模式|分子光谱、振动能级和光子频率|吸收需满足选择条件'),
94:('lattice','非线性摄动仅为源标题，现有扩展在nonlinear模块保留|原子实、晶格热运动与声波|耦合运动与传声传热|独立模式和声子|单原子链方程|平移算符本征态'),
95:('lattice','实指数空间解和截止|波矢与相位差|第一布里渊区及端点等价|最短波长|群速度与相速度|长波连续介质极限'),
96:('lattice','双原子晶胞和两个位移坐标|两条运动方程|复振幅及行列式|轻质量低频串联近似|高频根的近似'),
97:('lattice','两支色散端点|光学支胞内反向运动|声学支长波|两质量不同时的带隙|每个波矢的两个自由度'),
98:('lattice','声子模式的量子化和热学联系|电子能带和禁带的类比|电子与晶格相互作用|两种激发的动力学及统计区别'),
}
figures=[(76,'4.1',['damping-types']),(77,'4.2',['damping-envelope']),(78,'4.3',['damped-phase']),
(79,'4.4',['resonance']),(81,'4.5',['profiles']),(83,'4.6',['coupled-pendula']),
(83,'4.7',['double-pendulum']),(89,'4.8',['benzene-model']),(90,'4.9',['ring-symmetry']),
(92,'4.10',['ring-modes']),(93,'4.11',['benzene-modes-a','benzene-modes-b','benzene-modes-c','benzene-modes-d']),
(94,'4.12',['mono-chain']),(95,'4.13',['mono-dispersion']),(96,'4.14',['diatomic-chain']),(97,'4.15',['diatomic-dispersion'])]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
alltex='\n'.join(p.read_text() for p in (BOOK/'chapters/new').glob('ch10-*.tex'))
sources=[]
notes=SRC/'2020秋季高二物理竞赛学生版讲义.pdf'
objects=[]
for p,(module,names) in pages.items():
    for i,name in enumerate(names.split('|'),1):
        objects.append(dict(source_object_id=f'r2notes:p{p}:teaching:{i:02}',physical_page=p,printed_page=p-2,
          object_type='teaching_argument',description=name,target_file=f'chapters/new/ch10-{module}.tex',
          status='mapped',notes='按教学段、公式链与证明功能成组核对；不把文字改写后的字数当完整性证据。'))
for p,num,targets in figures:
    assert all(r'\label{ch10:fig:'+s+'}' in alltex for s in targets)
    objects.append(dict(source_object_id=f'r2notes:p{p}:fig:{num}',physical_page=p,printed_page=p-2,
      object_type='figure_group',source_number=num,target_ids=['ch10:fig:'+s for s in targets],status='mapped'))
modegroups=[(395,2),(599,2),(677,1),(700,1),(838,2),(954,2),(981,1),(994,1),(1014,1),(1048,2),
 (1137,1),(1162,2),(1332,1),(1376,1),(1477,2),(1612,2),(3080,1),(3092,2),(3110,2),(3121,1)]
for j,(nu,n) in enumerate(modegroups):
    group='a' if j<5 else 'b' if j<11 else 'c' if j<16 else 'd'
    for k in range(n):
        objects.append(dict(source_object_id=f'r2notes:p93:fig4.11:{nu}:{k+1}',physical_page=93,printed_page=91,
          object_type='figure_panel',source_number=f'4.11/{nu}/{k+1}',target_ids=[f'ch10:fig:benzene-modes-{group}'],
          status='mapped',notes='定性振型；保留频率组、平面内/外和简并结构，不把箭长当定量本征矢量。'))
sources.append(dict(source_id='r2-mechanics-notes',path=str(notes),sha256=sha(notes),physical_pages=[73,98],objects=objects))
ex=SRC/'2020秋季高二物理竞赛习题.pdf'
objects=[]
for i,(p,label) in enumerate([(36,'friction'),(36,'governor'),(37,'chain'),(37,'wedges'),(38,'charges'),(39,'spring-pendulum')],1):
    objects.append(dict(source_object_id=f'r2ex:p{p}:problem9.{i}',physical_page=p,printed_page=None,
      object_type='problem_with_subquestions',source_number=f'第九讲第{i}题',target_ids=[f'ch10:ex:{label}'],
      target_example=f'10.{i+3}',status='mapped',notes='题设、全部子问及解答；第5题恢复水分子自由度类比。'))
    if i<=4: objects.append(dict(source_object_id=f'r2ex:p{p}:fig9.{i}',physical_page=p,object_type='figure_group',
      source_number=f'第九讲第{i}题题图',target_ids=[f'ch10:fig:{label}'],status='mapped'))
sources.append(dict(source_id='r2-mechanics-exercises',path=str(ex),sha256=sha(ex),physical_pages=[36,39],objects=objects))
record=dict(chapter=10,date='2026-09-09',sources=sources,
 scope='本章26页讲义与4页习题的独有教学内容及19组来源图。逐组核对不等于字面逐字复制。',
 boundary={'physical_page':99,'belongs_to_chapter':11,'reason':'万有引力开始；不计入振动，不排除为非教学页。'},
 corrections=['相位反函数分支','10度为0.1745弧度','瞬时能量和弱阻尼平均能量区别','共振条件与相位象限',
 '本征值符号和稳定性','六环旋转关系符号','声学传播和有限热导率不等同','模式图中的入出面、成对方向及定性标度'],
 source_figures=19,source_molecular_panels=30,retained_examples=9,new_numbered_figure_groups=29,
 image_provenance={'asset':'assets/ch10/benzene-model.png','sha256':sha(BOOK/'assets/ch10/benzene-model.png'),
 'method':'内置图像生成工具','original_output':'/Users/dongxingxi/.codex/generated_images/019fe8f7-db8d-7383-b4b2-16a55baa634b/exec-ec5df910-95bc-467b-9805-a2290351bf7e.png',
 'prompt_summary':'白底斜视苯分子；六碳六氢，闭合平面六边形，每碳一氢；环上下淡蓝离域电子云；无文字。'})
path=BOOK/'audit/source-review/ch10-revision-ledger.json'
path.write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('Source objects:',sum(len(s['objects']) for s in sources),'source figure groups: 19; molecular subpanels: 30')
