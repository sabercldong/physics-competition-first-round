"""Targeted prose links to the quantities used by each existing figure."""
from build_review_ch19_ch20 import book
rows={
('thirty-second-section','examples.tex'):{
'dipoleFarFigure':r'图 1.7 左侧把场分解为径向和极角方向，右侧以同一偶极矩方向展示远场线族。',
'quadrupoleFarFigure':r'图 1.8 左侧的三个电荷共线，相邻间距为 $l$；观察角 $\theta$ 从这条轴量起，右侧场线由三个电荷共同产生。'},
('thirty-third-section','content.tex'):{
'zeroEquipotentialFigure':r'图 2.2 取 $Q=2q$；圆周上 $P$ 到正、负电荷的距离分别为 $r_+,r_-$，满足 $r_+=2r_-$，故两项电势正好相消。',
'acceleratorTunnelFigure':r'图 2.4 中的蓝色磁体沿隧道弯曲排列，束流在内部真空管中传播；磁场用于约束轨道，粒子的能量由加速电场提供。'},
('thirty-third-section','examples.tex'):{
'repellingSpheresFigure':r'图 2.6 中两段悬线位置均长 $L$，夹角为 $\theta$；$A,B$ 的连线决定电斥力方向，$h$ 是两球的高度差。'},
('thirty-fourth-section','content.tex'):{
'faradayCageFigure':r'图 3.3 的金属网构成连通屏蔽壳；在上述静电条件下，壳内无电荷的空腔与外界电场隔离。',
'discretePotentialFigure':r'图 3.4 中节点 $n$ 与两侧相邻节点均相距 $a$，所以其二阶差分恰由上式三项构成；$A,B$ 的电势不再作为未知量。',
'groundedSphereImageFigure':r'图 3.5 中 $C$ 是球心，$P$ 严格位于球面；$CP=R$，真实电荷与像电荷到 $C$ 的距离分别为 $L,l$。',
'ionosphereFigure':r'图 3.6 中橙色路径表示被电离层折回的通信波，蓝色路径穿过电离层到达卫星；两条路径对应不同的频率条件。'},
('thirty-fourth-section','examples.tex'):{
'cavityImageFigure':r'图 3.7 中真实电荷到球心距离为 $d<R$；像点距离为 $R^2/d>R$，因而不在要求电场的球腔内。',
'cornerImagesFigure':r'图 3.8 的真实求解域是第一象限，另三个点都是像点；逐块检查镜像的相反符号即可验证两板零电势。',
'hemisphereImagesFigure':r'图 3.9 中四个点都在对称轴上；关于平面成对反射使平面电势为零，关于球面的像变换使半球面电势为零。'},
('thirty-fifth-section','content.tex'):{
'capacitorFieldFigure':r'图 4.1 以两球为例，正球上的场线沿外法线发出，负球上的场线沿内法线进入；两球各自等势，但电势一般不同。',
'parallelPlateFigure':r'图 4.2 左侧标出面积 $A$ 和间距 $d$；右侧场线在板间中央近乎平行，只有边缘附近明显弯曲，因此下文匀强近似要求极板尺度远大于 $d$。',
'coaxialCapacitorFigure':r'图 4.3 的横截面中，积分面半径必须满足 $a<r<b$；沿径向从 $a$ 积到 $b$，才能得到两导体间的电势差。',
'capacitorParallelFigure':r'图 4.4 的两支路连接同一对节点，所以每个电容器的电压均为 $U$，而电源提供的电荷量等于各支路电荷量之和。',
'capacitorSeriesFigure':r'图 4.5 中两电容器之间的导线与两片内侧极板组成孤立中性导体，因此内侧两片极板的电荷等量异号。',
'greenSphereFigure':r'图 4.6 中距离 $r$ 从球心量到 $P$；交换球上电荷与 $P$ 处电荷时，球的位置和半径均保持不变。',
'greenTwoConductorFigure':r'图 4.7 将两导体的电荷与电势一一配对；倒易关系比较的是同一几何下的两个状态，而不是把两导体互换位置。',
'polarizationFigure':r'图 4.9 左侧每个偶极矩由负端指向正端，右侧由束缚面电荷产生的场则指向左，因而抵消一部分向右的外加场。'},
('thirty-fifth-section','examples.tex'):{
'exampleParallelFigure':r'图 4.10 的板间距为 $d$，板面边长为 $l$，故用来包围极板电荷的高斯面有效面积为 $S=l^2$。',
'exampleSphericalFigure':r'图 4.11 中场仅分布于 $R_1<r<R_2$；两导体之间的电压须沿半径方向积分。',
'touchingSpheresFigure':r'图 4.12 的接触点是两球的公共点；在计算电容时，两球应视为同一等势导体，而非两个独立电容器。',
'modifiedCapacitorFigure':r'图 4.14 左图的两部分共有相同板间电压；右图的两层沿电场方向依次排列，分别对应并联与串联。',
'dielectricInsertionFigure':r'图 4.15 中 $x$ 向右增加，表示介质插入更深；因此由能量求得的正 $F$ 指向右。',
'yCapacitorFigure':r'图 4.16 的三个内侧极板连接在同一节点上，电势均为 $V$；该节点与外界不导通，所以其总电荷保持为零。'}
}
for (section,file),items in rows.items():
 p=book.LEGACY/section/file;t=p.read_text()
 for macro,prose in items.items():
  if prose not in t:
   needle='\\'+macro+'\n';assert t.count(needle)==1,(section,macro)
   t=t.replace(needle,prose+'\n\n'+needle)
 p.write_text(t)
