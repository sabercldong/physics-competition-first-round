# 第19—20章三幅理论图转 TikZ 记录

仅新增 `field-geometries.tex`，未改 `generated/`、公共样式或覆盖模块。源文件定义三个独占宏，不调用 `includegraphics`，无 PDF、PNG、字体文件或数据文件依赖。曲线均为可直接编辑的 TikZ 坐标折线。

| 原媒体 | 替代宏 | 核对的正文与生成器 |
|---|---|---|
| `assets/revision-ch19-ch20/grounded-sphere.pdf` | `\MeTheoryGroundedSphere` | ch20 接地球像电荷构造；`figures_revision_ch19_ch20.py:image_sphere` |
| `assets/revision-ch19-ch20/two-cylinders.pdf` | `\MeTheoryTwoCylinders` | ch20 两个圆柱的双极坐标解；同脚本 `cylinders` |
| `assets/revision-ch19-ch20/quadrupole.pdf` | `\MeTheoryQuadrupole` | ch19 直线电四极子的右侧三电荷精确场线面板；同脚本 `point_panels` |

## 几何与方向

- 接地球：沿用原图的球心、半径、真实电荷距离；由 `l=R²/L` 计算像位置，由极角 2.05 rad 计算球面点 P。`r₁,r₂,R,L,l,C,+Q,−q` 均保留，补零电势和接地符号。数值验证 `CP=R`、`Ll=R²`、`Q/r₁=q/r₂`。
- 双圆柱：`d=1.7,R=.85,a=√(d²−R²),ξ₀=arcosh(d/R)`；场线按固定 η 的精确双极坐标式采样，等势线为固定 ξ 的解析圆，内部曲线被圆柱白底遮去。箭头沿 ξ 递减，由正柱指向负柱；外轴线也按真实电场定向。金色点标出 `x=±a`，半径 R 从真实圆心起画。
- 四极图：电荷位于 `x=−1,0,1`，电荷量依次 `−1,2,−1`。由精确三点电荷库仑场积分，保留原图“真实三电荷场”的语义；未把远场近似曲线延伸到点电荷近旁。采用归一化场方向的 RK4，步长不大于 `.006l` 及 `.055r_min`，随后以 `.00045l` 容差简化；第一象限 397 个坐标顶点，通过镜面对称得到四瓣。正电荷发出、负电荷接收的箭头均核验。

## 验证

专属构建目录：`build/quality-mechanics/theory-field-geometries/`。

- `atlas.tex`、`atlas.pdf`：3页图册，前两图实际使用 `.76\linewidth`，四极图分别以 **4.4 cm** 和 8.8 cm 呈现，均逐幅视觉检查；4.4 cm 下电荷标签仍可辨认，已减少过密箭头。
- XeLaTeX 在工程根目录连续两遍成功；最后日志无 Warning、Overfull、缺字或未定义引用。
- `numeric-checks.json`：双圆柱采样端点的圆面残差低于 `7×10⁻¹⁶`；四极原积分路径的通量函数 `F=Σqᵢ(x−xᵢ)/rᵢ` 最大漂移 `7.1×10⁻⁹`（坐标简化误差另受上述容差限制）。
- 导出坐标中全部显式场线箭头均与精确电场同向；最小方向余弦：双圆柱 `0.999995`，四极 `0.9999998`，其余通过镜面对称生成。
- 临时采样器 `make_field_geometries.py` 留在专属构建目录，供复算；编译交付的 TikZ 不依赖该脚本。

根代理负责替换原调用、保持原图号/图注并进行章节及全书集成。本记录只覆盖这三幅图。
