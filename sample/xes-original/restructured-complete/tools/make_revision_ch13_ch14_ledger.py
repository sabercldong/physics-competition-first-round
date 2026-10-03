"""Encode the independently inspected source-page/topic and object mapping."""
import json,hashlib
from pathlib import Path
BOOK=Path(__file__).resolve().parent.parent
audit=BOOK/'audit/source-review'
baseline=json.loads((BOOK/'build/review-ch13-ch14-20260912/manifest.json').read_text())
def target(ch,kind,slug):return f'ch{ch}:{kind}:{slug}'
pages=[]
def page(src,n,printed,topic,*targets):
 pages.append(dict(id=f'{src}:page:{n}',source=src,physical_page=n,printed_page=printed,
  teaching_topics=topic,targets=list(targets),status='mapped'))
for n,topic in [(78,'流体、定常流、速度场、可压缩性'),(79,'流线性质、流线管、体积流率、例2.97'),
 (80,'等截面稳定流、下落水束、质量连续性'),(81,'可压缩连续性、等截面自由落体液柱')]:
 page('kinematics',n,None,topic,target(13,'sec','flow-intro'))
for n,topic,slugs in [
 (123,'质元映射与欧拉速度场、流线微分方程、流线管、不可压缩条件',['material','flow-intro']),
 (124,'随体连续性、热流耦合、速度梯度的平动/转动/形变分解',['material','bernoulli']),
 (125,'应力、压强各向同性、压力合力、浮力积分、静力平衡及偏应力',['statics','surface']),
 (126,'欧拉方程、压力做功图、沿流线导出伯努利方程',['bernoulli']),
 (127,'内能与焓、可压缩伯努利条件、牛顿黏滞与两种黏度',['bernoulli','viscosity']),
 (128,'应力对称性、黏性应力散度、纳维—斯托克斯方程及讨论',['surface'])]:
 page('notes',n,n-2,topic,*[target(13,'sec',s) for s in slugs])
for n,topic,slugs in [
 (53,'两液柱振动；竖直同轴圆筒流三问',['coupled-hg','couette']),
 (54,'半圆柱机库风力、速度势及压力积分',['hangar']),
 (55,'漏斗排液及黏性；浅水波岸坡与俯视轨迹',['funnel','shore']),
 (56,'直角水管稳定偏角',['hose'])]:
 page('exercises',n,None,topic,*[target(13,'ex',s) for s in slugs])
for n,topic,slugs in [
 (5,'热物理导言、历史、分子运动论与实验证据',['molecules']),
 (6,'分子成像、分子特征、热运动、温度',['molecules','temperature']),
 (7,'测温前后、温标、热平衡、熔点与沸点',['temperature']),
 (8,'热膨胀、非对称势阱、膨胀系数表',['expansion']),
 (9,'线膨胀、工程应用与因瓦合金、气体模型适用条件',['expansion','ideal-gas']),
 (10,'固定物质量状态关系、气体密度、分压、传统气压计',['ideal-gas','mixtures']),
 (11,'瑞利仪器叉形端面、误差控制、气体密度差推导',['mixtures']),
 (12,'氩气比例与性质、容器及碰壁、动量统计',['mixtures','pressure']),
 (13,'压强微观式、均分与常数关系；例19.1、19.2',['pressure'])]:
 page('thermal',n,n+274,topic,*[target(14,'sec',s) for s in slugs])
for n,nums,topic in [(14,[3,4,5],'润湿三问、温度计、托里拆利题上半'),
 (15,[5,6,7],'托里拆利末句、加热气体三问与双题图、砂粒题上半'),
 (16,[7,8,9],'砂粒题末半、汞柱溢出及题图、U形管题'),
 (17,[10,11],'L形管题、一维原子链')]:
 page('thermal',n,n+274,topic,*[target(14,'ex',f's28-19-{i}') for i in nums])
figs=[]
def fig(src,n,number,t,role,status='mapped'):
 figs.append(dict(id=f'{src}:figure:{number}',source=src,physical_page=n,source_number=number,
  target=t,status=status,physical_role=role))
for n,num,slug,role in [
 (79,'2.23','k10-2-23','球外流线不相交，局部相切'),
 (79,'2.24','k10-2-24','闭合截线、横截面、三维弯曲流线管'),
 (79,'ex2.97','k10-ex-2-97','扩张管面积与速度'),
 (80,'ex2.98','k10-ex-2-98','等截面直管'),
 (80,'ex2.99','k10-ex-2-99','同一高度的水束面积、速度及位移'),
 (81,'ex2.100','k10-ex-2-100','两截面密度、面积与速度')]:
 fig('kinematics',n,num,target(13,'fig',slug),role)
fig('notes',123,'8.1',target(13,'fig','k10-2-24'),'横截线与各点局部切向速度；与资料图2.24合并','merged')
fig('notes',126,'8.2',target(13,'fig','bernoulli'),'压力、面积、位移和共同高度基准')
fig('notes',127,'8.3',target(13,'fig','shear'),'流层间距、速度梯度和黏性力')
for n,num,slug,role in [(53,'q1','coupled-hg','两根连续水银柱、封闭气体、各段长度'),
 (54,'q3','hangar','来流、半圆柱、门口停滞点和积分角'),
 (55,'q4','funnel','漏斗水面与有限开口'),
 (55,'q5','shore','岸坡剖面与俯视射线两个子图'),
 (56,'q6','hose','等长正交管、转轴及水流')]:
 fig('exercises',n,num,target(13,'fig',slug),role)
for n,num,slug,role in [(6,'19.1','s28-19-1','两种分子成像外观；创作示意不充当实验证据'),
 (7,'19.2','s28-19-2','测温前后两场景；内置图像生成工具创作'),
 (8,'19.3','s28-19-3','非对称势阱及能量升高的转折点'),
 (10,'19.4','s28-19-4','传统气压计密封、连通与高度'),
 (11,'19.5','s28-19-5','瑞利仪器同形叉端、气路与汞路'),
 (12,'19.6','s28-19-6','立方容器和弹性反射两个子图'),
 (15,'ex19.6','heated-apparatus','两限位件及待解pV双子图'),
 (16,'19.7','s28-19-7','活塞卡环及铁砂接触'),
 (16,'19.8','s28-19-8','汞柱/封闭气体/管长比例')]:
 fig('thermal',n,num,target(14,'fig',slug),role)
questions=[]
def question(src,n,num,t,notes=''):
 questions.append(dict(id=f'{src}:example:{num}',source=src,physical_page=n,source_number=num,
  target=t,status='mapped',notes=notes))
for i,n in zip(range(97,102),[79,80,80,81,81]):
 question('kinematics',n,f'2.{i}',target(13,'ex',f'k10-2-{i}'))
for i,n,slug in [(1,53,'coupled-hg'),(2,53,'couette'),(3,54,'hangar'),(4,55,'funnel'),(5,55,'shore'),(6,56,'hose')]:
 question('exercises',n,str(i),target(13,'ex',slug),
  '竖直方向重力项和三问均保留' if i==2 else '源件“内径2 cm²”修正为截面积' if i==6 else '')
for i,n in enumerate([13,13,14,14,14,15,15,16,16,17,17],1):
 question('thermal',n,f'19.{i}',target(14,'ex',f's28-19-{i}'),
  '沿用此前用户明确授权的条件重构，非声称与含糊源题逐字一致' if i in [9,10] else
  '人体材料模型与实际生理现象分开；原问题保留并纠正解说' if i in [1,2] else
  '统计平均系数7/48；保留转折点中点估算并说明7/72不是统计平均' if i==11 else '')
result=dict(scope='第13、14章修订；源页教学主题+逐题+逐图对象核对，不是逐字逐句计数',
 sources={s:{k:baseline['files'][s][k] for k in ['path','sha256']} for s in ['kinematics','notes','exercises','thermal']},
 pages=pages,source_figures=figs,source_exercises=questions,
 boundary_exclusions=[dict(source='kinematics',physical_page=82,reason='下一单元'),
 dict(source='thermal',physical_page=18,reason='空白页'),dict(source='thermal',physical_page=19,reason='下一讲')],
 preserved_bridge_examples=[target(13,'ex',s) for s in ['outlet','jet-plate','settling']],
 source_absent_figures=[dict(source='thermal',physical_page=16,source_number='19.9',notes='题称如图，但本PDF无附图；新增封闭U管图'),
 dict(source='thermal',physical_page=17,source_number='19.10',notes='题称如图，但本PDF无附图；新增L管初态及四阶段图')],
 generated_sha256={f'ch{n}':hashlib.sha256((BOOK/f'generated/chapters/ch{n}.tex').read_bytes()).hexdigest() for n in [13,14]})
assert len(pages)==27 and len(figs)==23 and len(questions)==22
dest=audit/'ch13-ch14-revision-ledger-20260912.json'
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(dest)
