# 高中物理竞赛一轮讲义

面向高中物理竞赛一轮教学与系统学习的竞赛讲义，包含知识讲解、例题推导、题图与解答图、可编辑 TikZ 和 LaTeX 源码。另保留二轮讲义及测试资料。

## 最新讲义

全书含32章、附录E及高阶A1—A6，共765道例题。每题均有题图和解答内部的可编辑TikZ配图，解答结合图中的变量、方向、区域或边界展开推导。封面署名董兴习、合肥一六八中学、19719272621，不印日期。

- [下载讲义PDF](https://github.com/sabercldong/physics-competition-first-round/releases/download/v2026.10.24-complete/physics-competition-first-round.pdf)
- [下载可编辑源码与TikZ](https://github.com/sabercldong/physics-competition-first-round/releases/download/v2026.10.24-complete/physics-competition-first-round-sources-tikz.zip)
- [查看发布版本与附件](https://github.com/sabercldong/physics-competition-first-round/releases/tag/v2026.10.24-complete)
- [修订与验收报告](audit/completeness_20261024/修订与验收报告.md) · [编译说明](audit/completeness_20261024/编译与修订说明.md)

本次继续处理只读检查报告中的提纲式知识段、解答跳步与内容过少的尾页，新增27个教学片段、29幅可编辑TikZ，补齐证明、条件、计算过程和图文衔接。全书结构检查、重点数学核算、编译及分页检查的结果和范围见验收报告。

## 主要内容

- `output/pdf/高中物理竞赛一轮讲义.pdf`：最新合订本；本目录的历史分卷、分章版本见[发布说明](output/pdf/发布说明.md)。`二轮/` 保存二轮讲义。
- `sample/xes-original/restructured-complete/`：一轮书稿主项目。
  - `main.tex`、`style.tex`：合订本入口及公共排版设置。
  - `generated/chapters/`、`generated/appendices/`：当前成书使用的章节及附录。
  - `advanced/`：高阶选读书稿。
  - `chapters/`、`appendices/`、`assets/`：专题源稿与配图素材。
  - `tools/`：生成、审校和发布脚本。
  - `audit/`：审校记录及来源台账。
- `sample/xes-original/`：分节源稿与历史整理稿。
- `sample/xes-second-round/`：二轮讲义源稿。
- `audit/completeness_20261024/`：本次处理报告、分区审校记录及机器核验数据；此前审校记录继续保留。
- `output/tests/`：测试资料；`output/论文修改/`：论文修改文件。

## 获取文件

PDF、图片、字体和 Word 文档通过 Git LFS 保存。克隆前安装 Git LFS，再执行：

```sh
git lfs install
git clone https://github.com/sabercldong/physics-competition-first-round.git
cd physics-competition-first-round
git lfs pull
```

## 编译说明

主书稿采用 XeLaTeX，依赖完整的中文、TikZ、PGFPlots、tcolorbox 等宏包，活动素材使用随源码提供的相对路径。可直接阅读合订PDF，也可在主项目目录编译：

```sh
cd sample/xes-original/restructured-complete
mkdir -p build/local
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -recorder -output-directory=build/local main.tex
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -recorder -output-directory=build/local main.tex
```

如日志仍提示交叉引用发生变化，再编译一次。输出为`build/local/main.pdf`。直接编辑当前已审校的TeX即可，无需重新运行历史讲次生成器。覆盖规则及复核方法见[编译与修订说明](audit/completeness_20261024/编译与修订说明.md)。

仓库保留当前书稿与正式输出，不包含本机构建缓存、临时 OCR 文件、虚拟环境及备份目录。

## 历史修订（2026-10-03）

当时修正了题干条件、例号顺序、术语和书末记号说明，并同步分册与组合文件；该历史合订本为1106页。记录见`audit/全书复查问题_修订完成记录_20261003.md`，历史49份一轮PDF清单见`output/pdf/发布清单_20261003.json`。当前完整内容请使用上方最新讲义。
