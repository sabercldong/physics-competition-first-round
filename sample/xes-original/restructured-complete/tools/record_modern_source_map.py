"""Record bounded source corrections without claiming whole-source acceptance."""
import json,re
from pathlib import Path
import build_review_ch31_ch32 as r
source=Path('/Users/dongxingxi/Downloads/学而思资料/二轮/兴趣二阶春季.pdf')
rows=[
 (115,'洛伦兹变换、间隔、四矢量与伪内积','ch31 §§31.1,31.5选读；A6-relativity 洛伦兹矩阵与四矢量','expanded_and_cross_reference'),
 (116,'固有时、尺缩、同时性、速度、四速度、四动量','ch31 §§31.1—31.5；A6-relativity 常见四矢量','expanded_and_cross_reference'),
 (117,'相对论力、功率、本征加速度、快度、碰撞、动量中心系','ch31 §31.5及选读；A6例 accelerating-rod','expanded_and_cross_reference'),
 (118,'反应能、阈能、四电流、四波矢','ch31 §31.4、31.5选读、例31.8；Q值另见ch32例32.11','expanded_and_cross_reference'),
 (119,'光行差、多普勒、四力密度','ch31 §31.4及31.5选读','expanded'),
 (120,'空白页','不进入学生正文','excluded_blank_confirmed'),
 (143,'热辐射、朗伯角分布、光电效应、康普顿、玻尔假设','ch32 §§32.1,32.2,32.4','expanded'),
 (144,'玻尔轨道及能级、精细结构常数、电子长度、物质波、概率与不确定性','ch32 §§32.3—32.5；A6-quantum-mechanics 平面波与概率解释','corrected_and_cross_reference'),
 (145,'静电场练1：同质量带电环/质点；练2a：扇形板；练2b：无限线电荷','撤销ch32归属；待后续静电场来源专项追踪','not_accepted_in_this_review'),
 (146,'静电场练3a—d：两倾斜电偶极子相互作用、力、力矩、平衡朝向','撤销ch32归属；待后续静电场来源专项追踪','not_accepted_in_this_review'),
]
data={'scope':'本轮只修订ch31/ch32；不把二轮静电场练习误计入近代物理验收，不宣称全书遗漏为零。',
 'sources':{'r2-spring':{'path':str(source),'sha256':r.common.sha(source)}},
 'pages':[{'source_id':'r2-spring','physical_page':p,'objects':o,'target':t,'status':s} for p,o,t,s in rows],
 'corrections':['120为确认空白，不是教学对象。','143—144属于量子论；145—146属于静电场习题。',
 '源144页电子长度比值有误，改为约化康普顿波长=alpha*a0、经典电子半径=alpha^2*a0。',
 '源115页“经典物理没有协变性”过于笼统：牛顿理论也可具有伽利略协变性，不能理解为没有任何协变性。'],
 'unresolved_out_of_scope':[{'pages':[145,146],'reason':'已检查图文并检索ch19/A4，未证实三题全部条件和子问具有新版落点；不自动改记mapped，也不称其为空白。'}],
 'figure_map':[]}
for n,total in [(31,6),(32,8)]:
 s=(r.book.GENERATED/f'chapters/ch{n}.tex').read_text()
 labels=re.findall(r'\\label\{(ch'+str(n)+r':fig:[^}]+)\}',s)
 assert len(labels)==total
 for i,label in enumerate(labels,1):
  data['figure_map'].append({'figure':f'{n}.{i}','label':label,'origin':'历史情景教学图（31.1）或扩展技术图；不冒充源页编号图',
   'body_reference_verified':bool(re.search(r'\\ref\{'+re.escape(label)+r'\}',s))})
assert all(x['body_reference_verified'] for x in data['figure_map'])
(r.BASE/'source-figure-map.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(r.book.BOOK/'audit/source-review/ch31-ch32-revision-ledger-20260923.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
print('Recorded ten page classifications and fourteen figure destinations; two external pages remain unaccepted.')
