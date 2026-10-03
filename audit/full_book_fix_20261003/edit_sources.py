from pathlib import Path
import re,json,hashlib
root=Path.cwd();book=root/'sample/xes-original/restructured-complete';changes=[]
def edit(p,fn):
 s=p.read_text();t=fn(s)
 if s!=t:
  changes.append(dict(path=str(p.relative_to(root)),before=hashlib.sha256(s.encode()).hexdigest(),after=hashlib.sha256(t.encode()).hexdigest()))
  p.write_text(t)
old='忽略它随高度的变化；气体上升过程近似为绝热过程。在这些假设下可证明'
new='''忽略它随高度的变化。凝结前采用静力平衡、恒定组成且比熵处处相同的干绝热大气柱模型；水蒸气含量很少，
对空气平均摩尔质量和绝热系数的影响可忽略。上升气团与周围压强近似相等，凝结前作可逆绝热变化。
以下温度递减率与压强分布只用于开始凝结以前；不得将干绝热关系直接用于凝结放热后的阶段。在这些假设下可证明'''
for p in [book/'generated/chapters/ch17.tex',root/'sample/xes-original/thirty-first-section/examples.tex']:
 assert old in p.read_text();edit(p,lambda s:s.replace(old,new))
old='所有电阻均忽略。棒初速为 $v_0$ 向右，电容初始不带电。描述 $t=0$ 后导体棒的运动。'
new=r'''并保留串联小电阻 $R_s>0$；忽略回路自感及其他电阻。在 $t=0$ 接通回路，棒初速为 $v_0$ 向右，电容初始不带电。
求充电暂态中的棒速和电荷、长时间后的终态，并讨论先等待暂态结束再取 $R_s\to0^+$ 的极限。'''
rail=r'\draw[Ink,very thick] (-3,1.4)--(3,1.4);'
newrail=r'''\draw[Ink,very thick] (-3,1.4)--(-1.9,1.4);
  \draw[Ink,thick] (-1.9,1.2) rectangle (-1.0,1.6);
  \node[above] at (-1.45,1.6) {$R_s$};
  \draw[Ink,very thick] (-1.0,1.4)--(3,1.4);'''
for p in [book/'generated/chapters/ch24.tex',root/'sample/xes-original/fortieth-section/examples-a.tex']:
 def change(s):
  assert old in s;s=s.replace(old,new)
  s=s.replace('零电阻与“初始电容不带电、棒却有非零速度”不能在普通时间尺度上同时满足；闭合回路后会出现一个极短的充电暂态。','接通回路后先经历充电暂态。先求长时间极限，再解出完整的时间变化。')
  s=s.replace('设暂态后电容带电量为 $q$、棒速为 $v$，则回路方程和棒的冲量方程分别为','设长时间后电容带电量为 $q$、棒速为 $v$。此时电流趋于零，回路方程与暂态全过程的冲量方程分别为')
  s=s.replace('上述状态是忽略自感、先保留微小电阻 $R_s>0$ 并等待暂态结束后的终态，随后电流为零，棒匀速运动。',r'上述 $q,v$ 分别记作 $q_\infty,v_\infty$；这是题设 $R_s>0$ 时的长时间极限，电流渐近趋零，棒速渐近趋于常量。')
  # Only alter this example's question circuit, not every rod diagram.
  pos=s.index('【小棒加电容】');end=s.index(r'\end{origexamplebox}',pos)
  s=s[:pos]+s[pos:end].replace(rail,newrail)+s[end:]
  s=s.replace('导体棒与初始未充电电容器相连。','导体棒通过小电阻与初始未充电的电容器相连，图示接通后的回路。')
  s=s.replace('机械等效电容与真实电容的电荷重分配','电容充电时的回路与棒的冲量关系')
  return s
 edit(p,change)
# The solution circuit also shows the retained resistor and instantaneous speed.
for p in [book/'generated/chapters/ch24.tex',root/'sample/xes-original/fortieth-section/diagrams.tex']:
 def diagram(s):
  pos=s.index(r'\newcommand{\rodCapacitorDiagram}');end=s.index(r'\newcommand',pos+12)
  part=s[pos:end].replace(rail,newrail).replace('{$v_0$}','{$v(t)$}')
  return s[:pos]+part+s[end:]
 edit(p,diagram)
for n,name in [(31,'ch31-relativity.tex'),(32,'ch32-modern.tex')]:
 for p in [book/f'generated/chapters/ch{n}.tex',book/'chapters/new'/name]:
  edit(p,lambda s:re.sub(r'\\setcounter\{bookexample\}\{\d+\}\s*\n','',s))
for p in [book/'generated/chapters/ch11.tex',book/'chapters/new/ch11-gravity.tex',book/'chapters/new/ch11-time-teaching.tex']:
 edit(p,lambda s:s.replace('比耐方程','比内方程'))
for p in [book/'generated/chapters/ch11.tex',book/'chapters/new/ch11-gravity.tex']:
 def intro(s):
  pos=s.index(r'\section{');return s[:pos]+'第9章已建立角动量守恒、有效势与有心力轨道的基本方法。本章先作必要回顾，再重点讨论轨道初始条件、二体运动及天体运动中的具体应用。\n\n'+s[pos:]
 edit(p,intro)
p=book/'main.tex'
def notes(s):
 s=s.replace('符号与常数索引','记号说明')
 s=s.replace('本书统一采用国际单位制。矢量以粗体表示，微分记号写作 $\\dd$，虚数单位记作 $\\ii$。',r'''除题目另有说明外，本书采用国际单位制。数值计算所用物理常数和近似值以题目或所在节的说明为准。

矢量通常以粗体表示，部分图示与推导使用箭头记号；两者均表示具有大小和方向的量。微分记号写作 $\dd$，虚数单位写作 $\ii$。
同一字母在不同专题中可能表示不同物理量，应结合本节定义及单位辨认；例如 $I$ 可表示电流、转动惯量或光强，$L$ 可表示长度、角动量大小或电感。

除专门说明角度单位的题目外，微积分与小角展开中的角度以弧度计。对数的底、正方向及参考系均以局部定义为准。
''')
 return s
edit(p,notes)
# Keep the current release manifest and QA expectation consistent.
p=book/'generated/deliverables.json'
def manifest(s):
 d=json.loads(s)
 for c in d['chapters']:
  if c['chapter']==19:c['output']='高中物理竞赛一轮讲义_第19章_静电场与电势.pdf'
 return json.dumps(d,ensure_ascii=False,indent=2)+'\n'
edit(p,manifest)
p=book/'tools/qa_release_staging.py';edit(p,lambda s:s.replace('符号与常数索引','记号说明'))
(root/'audit/full_book_fix_20261003/source_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
print('Edited',len(changes),'source/manifest files')
