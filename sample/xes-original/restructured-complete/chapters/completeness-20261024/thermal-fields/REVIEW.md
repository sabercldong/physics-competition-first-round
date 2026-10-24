# 五处完整性补充（2026-10-24）

本目录保留全部可编辑 TeX 与 TikZ；通过 `tools/quality_completeness_thermal_fields.py`
在旧覆盖层之后接入，不修改公共样式、主入口或其他章节。

| 对应内容 | 独立源文件 | 实质补充 |
|---|---|---|
| 例 A2.25 费米气体低温热容 | `fermi-sommerfeld.tex` | 从阶跃差的奇对称性推导索末菲展开与 π²/6；分别展开 N、U，显式消去 δμ；补固定 N,V、光滑态密度与低温条件。 |
| 例 A3.23 连带 Legendre 函数 | `associated-definition.tex`、`associated-proof.tex` | 先用微分方程及独立端点首项定义负阶；从 Rodrigues–Leibniz 计算正阶端点系数，Wronskian 证唯一性，再比较归一化、证明宇称。 |
| 例 A2.15 末 GL 知识 | `gl-functional.tex` | 定义复序参量、对电荷/有效质量、密度与总泛函；给规范不变梯度项、电流、变分方程和可代回核验的 tanh 边界解；说明一级相变不能删去稳定六次项。 |
| 正则 Sturm–Liouville 谱定理 | `sl-spectrum-proof.tex` | 明确有限正则分离边界条件；Robin 迹估计、移位正定、Green 核与有限秩逼近、紧正自伴算子的逐次本征构造及完备性、Wronskian 单重性、变分最低态和 Prüfer 节点计数。 |
| 附录 E.6.2 有限间距等势双球 | `two-spheres-derivation.tex` | 两条镜像反演链的边界配对、像点和电量递推、双曲函数闭式、唯一性与总电荷、交错余项的一致界及相切极限。 |

共5幅新增或替换的 TikZ 解图/理论图；所有图均在对应推导内通过唯一图号引用。
原有例题标签、题序及知识层级保留。

接口：`apply_file_revision(name,text)` 接受含 `.tex` 的文件名或路径；
`apply_appendix_revision(text)` 处理附录。CLI只写本分区的4个正文源文件，`--check` 不写文件。
旧 `quality_final_review_thermal_fields.py` 仅为负阶旧段落增加精确兼容判定，其他旧修正仍执行。
已验证新层幂等、旧 final-review 层后重放新层不改变最终文本。

局部编译在工程根执行 XeLaTeX，输出独立位于 `PARENT/work/completeness-thermal-build/`：
`A2/A2.pdf`、`A3/A3.pdf`、`appendix-e/appendix-e.pdf`；未编译全书，未提交或推送。
最终局部PDF分别30、40、26页；最后一遍日志均无LaTeX/包警告、无Overfull/Underfull，
页面扫描无空白页或文字越过纸张边界，5幅新图已逐幅视觉检查。

独立数学核算在同一私有编译目录的 `verify_math.py` 和 `math-verification.json`：

- 直接费米积分固定 N=1，取 T/T_F=0.01、0.02、0.04，μ、U、C_V 的前导系数趋于推导值。
- 索末菲一阶矩数值为 1.6449340668482264，与 π²/6 一致。
- l=0…10、0≤m≤l 的66组 Legendre 端点导数和宇称完全符号核对。
- tanh 剖面代回无量纲 GL 方程，残差符号化简为零。
- L/R=2.001、2.01、2.2、3、10 的双链递推与闭式一致；球面41个采样点的等势误差最大约1.36×10⁻¹⁴。
- 3组参数直接微分与积分独立核对 Prüfer 参数导数，结果一致且为正。

谱证明另经其他分区代理只读交叉复核；据意见补清 H¹ 能量空间、Robin 自然边界、导数弱收敛与弱下半连续性，并在图注明确折线核的 κ=0 特例。
本记录仅覆盖所列5项，不构成其他章节或全书的质量认证。
