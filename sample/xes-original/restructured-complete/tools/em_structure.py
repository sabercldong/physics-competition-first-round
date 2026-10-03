"""Thematic EM sections; preserve every legacy example and its source labels.

Legacy sources stay intact. This assembly layer moves their complete theory and
question/solution blocks inside the same graphic/macro scope. Extra teaching
material lives in chapters/em-expansion. ch26's application source is integrated
here rather than appended as five disproportionate top-level sections.
"""
from pathlib import Path
import re
B=Path(__file__).resolve().parents[1]
# (section title, zero-based theory blocks, inclusive one-based example range)
PLANS={
's32': [('电荷、库仑定律与场的叠加',[0,1,2],[1,2,4,5]),('高斯定律与对称带电体',[3,4],[3,6,7])],
's33': [('电势与场势关系',[0,1,2],[1]),('电势应用与放电现象',[3,4],[4,5,6]),('静电能量与带电粒子运动',[5,6],[2,3,7,8,9])],
's34': [('导体平衡、屏蔽与电荷响应',[0,1,4],(1,3)),('唯一性定理与电像法',[2,3],(4,10))],
's35': [('电容的定义与导体组',[0,1,4],(1,3)),('电介质、极化与界面条件',[5,6],[4,6]),('电容网络、储能与充放电',[2,3],[5,7,8,9,10,11])],
's36': [('电流密度与微观输运',[0,3,4],(1,4)),('伏安特性、电阻与测量',[1,2],(5,6)),('电路守恒与节点方程',[5,6,7,8,9],(7,8))],
's37': [('等效电源、对称性与电桥',[0,1,2,3],(1,6)),('多端、无限与自相似网络',[4,5],(7,10))],
's38': [('洛伦兹力与回旋轨道',[0,1,5,9],(1,6)),('交叉场、漂移与载流子输运',[4,7],(7,12)),('缓变场、扰动与阻尼运动',[8,10],(13,16)),('磁矩、频移与加速装置',[6,3,2],(17,17))],
's39': [('电流元叠加与典型磁场',[3],(1,3)),('对称性、安培环路与磁通',[2,4],(4,4)),('安培力与载流回路的合力',[0],(5,6)),('磁矩、进动与磁场应用',[1],(7,9))],
's40': [('磁通法、楞次定律与发电机',[0,2],(1,2)),('动生电动势与机电耦合',[1],(3,9)),('感生电场、加速与电压测量',[3,4],(10,16)),('自感、互感与动态回路',[5,6],(17,21))],
's41': [('位移电流与麦克斯韦方程组',[0,1],(1,0)),('电磁波、能流与辐射压',[2,3],(1,0)),('辐射、散射与介质传播',[4,5],(1,0)),('超导磁响应与磁通量子化',[6,7,8],(1,0))],
}

def headings(text, pattern=r'(?m)^\\subsection\*?\{([^{}]+)\}'):
 matches=list(re.finditer(pattern,text));assert matches
 return text[:matches[0].start()],[(m[1],text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)])for i,m in enumerate(matches)]

def restructure(key,text):
 if key not in PLANS:return text
 first=text.find(r'\begin{origexamplebox}')
 theory=text if first<0 else text[:first]
 questions=[] if first<0 else re.split(r'(?=\\begin\{origexamplebox\})',text[first:])[1:]
 # split() gives an empty initial element because the first token is a box.
 assert all(q.count(r'\begin{origexamplebox}')==q.count(r'\begin{xesolution}')==1 for q in questions),(key,len(questions))
 prefix,topics=headings(theory)
 order=[i for _,idx,_ in PLANS[key]for i in idx];assert sorted(order)==list(range(len(topics))),(key,len(topics),order)
 extras=[]
 if key=='s41':
  _,extras=headings((B/'chapters/new/ch26-em-waves.tex').read_text(),r'(?m)^\\section\{([^{}]+)\}')
 out=[];used=[]
 for j,(title,idx,selection) in enumerate(PLANS[key],1):
  chosen=list(range(selection[0],selection[1]+1)) if isinstance(selection,tuple) else selection
  out.append(r'\section{'+title+'}\n')
  if key=='s34' and j==1:
   out.append(r'本节先用等势与电荷守恒确定导体的约束。后面的异号导体题还会用到静电势的最大值原理：无电荷区域的电势满足拉普拉斯方程，非恒定解不能在区域内部取得严格极大或极小值，极值由边界控制。这为判断导体电势与表面电荷符号提供工具；唯一性定理及电像构造将在下一节系统展开。'+'\n')
  if j==1:out.append(prefix)
  for i in idx:
   name,body=topics[i]
   if key=='s38' and i==10:
    assert r'\label{' not in body
    name='线性阻尼与小扰动的求解框架'
    body=(B/'chapters/em-expansion/s38-damping-core.tex').read_text()
   if key=='s39' and i==0:name='电流元受力与闭合回路'
   out.append(r'\subsection{'+name+'}\n'+body)
  if key=='s41':
   for i in {1:[0],2:[1,2],3:[3],4:[4]}[j]:
    name,body=extras[i];out.append(r'\subsection{'+name+'}\n'+body)
  p=B/f'chapters/em-expansion/{key}-{j}.tex'
  if p.exists():out.append(p.read_text())
  if chosen:
   out.append(r'\subsection{专题例题与方法应用}'+'\n')
   out.extend(questions[k-1] for k in chosen);used.extend(chosen)
 assert sorted(used)==list(range(1,len(questions)+1)),(key,used,len(questions))
 result='\n'.join(out)
 if key=='s38':result=result.replace('下一节绝热不变量中的','前面绝热不变量中的')
 if key=='s39':result=result.replace('上一讲从单个带电粒子','第22章从单个带电粒子').replace('本讲','本章')
 if key=='s40':result=result.replace('上一讲研究了稳恒电流与磁场','第23章研究了稳恒电流与磁场').replace('本讲','本章')
 if key=='s34':result=result.replace('前两讲分别从力和能量','第19章分别从力和能量')
 if key=='s39':result=result.replace('上一讲从单个带电粒子','第22章从单个带电粒子')
 if key=='s40':result=result.replace('上一讲研究了稳恒电流与磁场','第23章研究了稳恒电流与磁场')
 result=result.replace('本讲','本章')
 result=result.replace('上一讲从带电体受力','本章前文从带电体受力').replace('上一讲讨论导体静电平衡','前面两节讨论导体静电平衡').replace('上一讲含','本章前面含').replace('下一讲','本章后续内容').replace('上一讲','本章前文')
 result=result.replace('前面的电导模型给出', '线性碰撞模型给出（电导率的微观推导见第21章）')
 return result

def finish_chapter19(text):
 """Move multipole and particle examples after their prerequisites.
 Both legacy units use the chapter's local macro scope; source labels persist.
 """
 moved={}
 for src in ('s32-1-4','s32-1-5','s32-1-7'):
  label=r'\label{ch19:ex:'+src+'}'
  pos=text.index(label);start=text.rfind(r'\begin{origexamplebox}',0,pos)
  stop=text.index(r'\end{xesolution}',pos)+len(r'\end{xesolution}')
  moved[src]=text[start:stop];text=text[:start]+text[stop:]
 for title,keys in [('电势与场势关系',('s32-1-4','s32-1-5')),('静电能量与带电粒子运动',('s32-1-7',))]:
  start=text.index(r'\section{'+title+'}')
  pos=text.index(r'\begin{origexamplebox}',start)
  text=text[:pos]+'\n'.join(moved[k] for k in keys)+'\n'+text[pos:]
 return text
