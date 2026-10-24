# 静态图号扫描的两处非活动候选

合订源文件的静态扫描包括已加载文件中的宏定义，因此发现两处不存在于实际排版中的旧引用：

| 旧引用 | 所在未使用宏 | 实际解答 |
|---|---|---|
| `advA2:quality:fermi-c-a` | `chapters/quality-20261023/thermal/A2-statistics.tex` 的 `\AAFermiCapacity`，宏体103—112行 | `advanced/A2-statistics.tex` 直接输入 `fermi-sommerfeld.tex`，实际图号为 `advA2:complete:sommerfeld` |
| `advA3:quality:assoc-a` | `chapters/quality-20261023/thermal/A3-pde.tex` 的 `\AAAssociatedLegendre`，宏体155—166行 | `advanced/A3-pde.tex` 直接输入 `associated-proof.tex`，实际图号为 `advA3:complete:associated` |

排除build目录，对全工程TeX搜索 `FermiCapacity|AssociatedLegendre`，两个 `AA` 宏各只出现于自己的定义，没有调用。仍在正文调用的是 `AQ` 题图宏。主入口依次加载A2/A3及其统计/PDE章节，再输入上述新解答。

因此保留 `figure-reference-review.json` 原始的两条静态候选，不伪造缺失标签或清空扫描结果；实际排版中的未定义引用以最终XeLaTeX日志检查为准。新图的引用、实际图号计数器和锚点亦接受相同检查。
