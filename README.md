# 高中物理竞赛一轮讲义

高中物理竞赛一轮讲义的 LaTeX 书稿、配图、审校记录、生成脚本与正式 PDF，另含二轮讲义及测试资料。

## 主要内容

- `output/pdf/`：正式合订本、分卷、分章、高阶选读及附录；`二轮/` 保存二轮讲义。
- `sample/xes-original/restructured-complete/`：一轮书稿主项目。
  - `main.tex`、`style.tex`：合订本入口及公共排版设置。
  - `generated/chapters/`、`generated/appendices/`：当前成书使用的章节及附录。
  - `advanced/`：高阶选读书稿。
  - `chapters/`、`appendices/`、`assets/`：专题源稿与配图素材。
  - `tools/`：生成、审校和发布脚本。
  - `audit/`：审校记录及来源台账。
- `sample/xes-original/`：分节源稿与历史整理稿。
- `sample/xes-second-round/`：二轮讲义源稿。
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

主书稿采用 XeLaTeX，依赖 `ctexbook`、TikZ、tcolorbox 及书稿配置的字体。正式 PDF 可直接阅读。

部分书稿和历史脚本使用本机绝对路径；在其他电脑重新编译前，需要调整素材路径、字体和运行环境。涉及原始资料比对的审校脚本还需对应的本地原始资料。

仓库保留当前书稿与正式输出，不包含本机构建缓存、临时 OCR 文件、虚拟环境及备份目录。

## 当前本机工作副本

为避免 iCloud 将 Git 对象转为占位文件，本机 `.git` 文件指向用户主目录下的 `.local/share/git/physics-competition-first-round.git`。原有 Git 元数据保存在本地 `archive/20261003-git-before-github/`。从 GitHub 克隆的新工作副本使用常规 Git 目录，无需上述本机路径。

## 本次全书修订（2026-10-03）

已修正复查中定位的题干条件、例号顺序、术语和书末记号说明，并同步正式分册及组合文件。合订本仍为1106页。修订记录见 `audit/全书复查问题_修订完成记录_20261003.md`；当前49份正式一轮PDF的校验清单见 `output/pdf/发布清单_20261003.json`。
