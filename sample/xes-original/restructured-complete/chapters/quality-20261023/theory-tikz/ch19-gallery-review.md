# 第19章四幅理论图转换记录

交付文件：ch19-gallery.tex。只新增本文件和此记录，未改generated章节或公共覆盖模块。

| 原资源 | 替换宏 |
|---|---|
| field-gallery.pdf | ThTheoryFieldGallery |
| equipotentials.pdf | ThTheoryEquipotentials |
| zero-potential.pdf | ThTheoryZeroPotential |
| ionization.pdf | ThTheoryIonization |

四宏仅输出TikZ/PGFPlots图形，不包含center、figure、图注或label，供主审在原有图注容器中调用。

- 场线三联图：静电异号点电荷与四极分布直接采样点电荷场；动态一幅保留原图的实际Liénard–Wiechert模型，xq(t)=0.2sin(2.5t)、c=1、观察时刻t=0、最高速0.5c。以601×601网格计算场，流线坐标转换为可编辑TikZ折线，箭头按精确场方向定向。推迟时间方程最大残差8.9e-16。
- 等势线三联图：匀强场和正点电荷用解析路径，偶极势与场线第一积分用函数等值线取样。点电荷的四条等势圆对应相同电势差；偶极箭头从右侧正电荷指向左侧负电荷，与正文相符。两等值函数梯度数值正交检验的相对点积约1.2e-10（有限差分）。
- 零电势图：取+Q在(-3,0)、-q在(0,0)，Q=2q，零势圆中心(1,0)、半径2，P=(0,√3)。整圆距离比r+/r-=2的数值误差小于7e-16；r+、r-与P位置对应，球面包围较小负电荷。
- 电离能图：内嵌本地NIST CSV中108个中性原子的原始十进制电离能字符串，已逐字比较全部108值；没有依赖外部图像。保留10类元素、稀有气体He/Ne/Ar/Kr/Xe/Rn标记，以及原Prefix含理论/估计标识的10个空心点：Z=1、59、91、100、101、104—108。氢使用专门空心六边形，避免五线星形无法显示空心的歧义；类金属使用实心左三角形，与估计数据的空心标识区分。

单图册：build/quality-thermal/theory-ch19/atlas.pdf（4页）。XeLaTeX最终双遍成功，未检出Warning、Overfull、未定义引用或重复标签。四幅已逐幅放大检查，场线方向、r+/r-标签、数轴、图例和空心标记均已核对。

构图脚本、数值残差和页面预览位于build/quality-thermal/theory-ch19/；TeX交付文件内也保留采样模型、数据来源及空心类别说明。根统一负责替换原includegraphics与全书编译。
