"""Source-page topics, individual source questions and complete figure groups."""
import json, hashlib
from pathlib import Path
import build_review_ch15_ch16 as revision
BOOK=revision.book.BOOK
SOURCE=Path('/Users/dongxingxi/Downloads/学而思资料/一轮/【2020寒】兴趣一阶-热学.pdf')
sha=revision.sha
def label(ch,kind,num):return f'ch{ch}:{kind}:s{29 if ch==15 else 30}-{20 if ch==15 else 21}-{num}'
page_data=[
 (19,15,'第一定律导言、三种永动机设想、内能与总能量区别','内能'),
 (20,15,'单/双原子内能、状态量、热交换、传导、对流、恒星内部对流层及表面细节','热交换：传导、对流与辐射'),
 (21,15,'对流、辐射、黑体、辐射常数、边界功','机械功与准静态过程'),
 (22,15,'活塞位移与面积功、准静态条件、第一定律','热力学第一定律'),
 (23,15,'循环净功、热容温度依赖、等容与等压过程','理想气体的等容、等压与等温过程'),
 (24,15,'等压热容、等温积分、绝热微分式与泊松关系','绝热过程'),
 (25,15,'泊松关系变形、密度式、重力场对流起始条件','重力场中形成对流的条件'),
 (26,15,'大气定量温压分层、温室吸收、对流判据及例20.1','重力场中形成对流的条件'),
 (27,15,'例20.2三循环、20.3变热容、20.4恒热容、20.5等温大气题干',None),
 (28,15,'例20.5续、20.6毛细、20.7泡膜两问、20.8温标两问',None),
 (29,15,'例20.9四问及题图、20.10直线过程及题图',None),
 (30,15,'例20.11提升气缸及题图',None),
 (31,16,'第二定律导言、循环净功与效率定义','热力学循环的效率'),
 (32,16,'五动作阶段与pV图、真实发动机与空气标准奥托模型','热力学循环的效率'),
 (33,16,'奥托效率、卡诺四过程、卡诺曲线及效率推导','卡诺循环'),
 (34,16,'四类热机/制冷机、开尔文与克劳修斯表述、中英文引述','热力学第二定律的早期陈述形式'),
 (35,16,'三位人物、可逆与不可逆、熵及状态函数','熵与热力学第二定律'),
 (36,16,'不可逆过程熵差、定热容系统、理想气体熵、替代可逆路径','具有简单物态方程系统的熵'),
 (37,16,'玻尔兹曼纪念碑、熵与可能数、左右分布组合计数','熵的微观解释'),
 (38,16,'花生示例辨析、明确热库模型、例21.1与21.2',None),
 (39,16,'例21.3五子问、例21.4三物体最高温度',None),
 (40,16,'例21.5表面能热机',None)]
questions=[]
for ch,source_pages in [(15,[26,27,27,27,27,28,28,28,29,29,30]),(16,[38,38,39,39,40])]:
 for n,p in enumerate(source_pages,1):
  questions.append(dict(id=f'thermal:p{p}:example:{20 if ch==15 else 21}.{n}',physical_page=p,
   source_number=f'{20 if ch==15 else 21}.{n}',target=label(ch,'ex',n),status='mapped'))
figures=[]
roles15=['三类永动机所有构件；共同坐标保证杆球连接', '手掌热对流羽流',
 '太阳和红巨星内部对流区域、辐射区、核心；保留表面细节扩展', '手部辐射强弱示意',
 '两个活塞密封状态、同长杆、位移与同一条P(V)曲线下面积',
 '三个热容平台、定量纵轴、诚实的对数横轴', '水平薄层厚度、重力与压强差',
 '高度/摄氏温度/压强数值、四层结构、地表与飞行器及极光情景',
 'abc三过程、同一等温双曲线、Pb=Pc=Pa/4', 'A到B直线且PB=PA/2',
 '初态及开口前最后密封位置、活塞接触与缸底通大气']
roles16=['五机械动作、气门、火花塞、同长连杆与曲柄；分开的奥托pV图',
 '四个状态及共同等温/绝热曲线', '四类热机/制冷机的热流、功和两个热库',
 '卡诺、开尔文、克劳修斯三位肖像', 'ABC等容/等温替代可逆路径',
 '玻尔兹曼碑、半身像与熵公式']
for ch,pages,roles in [(15,[19,20,20,21,22,23,25,26,29,29,30],roles15),
                        (16,[32,33,34,35,36,37],roles16)]:
 for n,(p,role) in enumerate(zip(pages,roles),1):
  figures.append(dict(id=f'thermal:p{p}:figure:{20 if ch==15 else 21}.{n}',physical_page=p,
   source_number=f'{20 if ch==15 else 21}.{n}',target=label(ch,'fig',n),physical_role=role,status='mapped'))
pages=[]
for p,ch,topic,heading in page_data:
 targets=[r['target'] for r in questions+figures if r['physical_page']==p]
 if p==24:targets+=[label(15,'eq',5),label(15,'eq',6),label(15,'eq',7)]
 if p==25:targets+=[label(15,'eq',n) for n in range(8,12)]
 if p==31:targets+=['ch16:fig:s30-21-1']
 pages.append(dict(id=f'thermal:page:{p}',physical_page=p,printed_page=p+274,chapter=ch,
  teaching_topics=topic,target_heading=heading,targets=targets,status='mapped'))
result=dict(scope='源页教学主题、逐题子问、逐组子图核对；不是逐字词或逐句OCR计数',
 source={'path':str(SOURCE),'sha256':sha(SOURCE)},pages=pages,source_questions=questions,source_figures=figures,
 exclusions=[dict(physical_page=18,reason='空白页，位于本次教学范围之前'),
             dict(physical_page=41,reason='已进入第22讲相变，属于下一章；仅排除在本次两章修订范围之外，并非非教学页')],
 source_absent_figures=[dict(physical_page=26,source_number='20.1',note='源题提及图，但留白处无图；保留并修正补充三循环图'),
                       dict(physical_page=27,source_number='20.2',note='源题提及图，但无实际附图；补充方程生成的标准循环图')],
 source_unnumbered_independent_teaching_figures_found=0,
 corrections_not_literal_reproduction={
 'thermal:p25':'源件将绝热常数与焓关联不准确，给出与熵的关系；原密度与强度量讨论保留',
 'thermal:p26':'代表性大气数据按标准模型重建；平均温度递减率不直接证明不稳定；极光机制纠正',
 'thermal:p38':'保留花生例作为模型辨析，不能由化学能求人体熵；另给明确热库模型',
 'thermal:p39':'保留五问并在题面明确辨析假命题及理想气体/稳定性条件；不证明错误命题'},
 generated_sha256={f'ch{n}':sha(BOOK/f'generated/chapters/ch{n}.tex') for n in (15,16)})
assert (len(pages),len(questions),len(figures))==(22,16,17)
dest=BOOK/'audit/source-review/ch15-ch16-revision-ledger-20260915.json'
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(dest)
