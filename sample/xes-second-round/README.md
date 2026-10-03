# 学而思物理竞赛二轮独立工程

本工程与一轮讲义完全分离。正文、分卷和总册共用 `chapters/`、`style.tex` 和 `book.json`，不使用 `\includepdf` 拼接正文。

本轮范围为四份原件的547个物理页、第1—28章及五个分卷，不含221页独立高阶讲义和H1—H6。来源目录仍保留历史元数据，但 `--scope main` 不依赖高阶单元。

构建命令：

```bash
python3 tools/build.py --chapter 1
python3 tools/build.py --volume mechanics
python3 tools/build.py --all --scope main
python3 tools/build.py --all --scope main --list
```

所有构建默认仅生成 `build/<构建名>/main.pdf`。编译两遍、通过 `qpdf` 并记录源文件和PDF哈希后，状态仍是 `built_not_reviewed`，不会复制到正式目录。未完成的章节不会用占位PDF代替；分卷或总册缺源文件时明确停止。

来源准备与审查：

```bash
python3 tools/prepare_sources.py --workers 2
python3 tools/audit.py --chapter 1
python3 tools/audit.py --all --scope main --sources --require-review
python3 tools/render_review.py --artifact chapter-01 --dpi 300
python3 -m unittest discover -s tests -v
```

`prepare_sources.py` 生成工作文本、中文OCR及源页预览，不会将机器识别标成已审阅。

- `page_inventory.jsonl`：547页独立清单，未审阅页明确保持 `unreviewed`。
- `source_inventory.jsonl`：从原件独立枚举的教学对象，不由旧台账反推。
- `source_ledger.jsonl`：源对象到正文的落点；无 `source_object_id` 的历史粗粒度条目不作为本轮完整性证据。
- `reviews/source_inventory/*.json`：人工逐页查看后录入的对象清单，可用 `tools/import_inventory.py` 合并。导入只验证对象落点，不升级章节验收。
- `reviews/<构建名>.json`：最终人工审阅记录，必须绑定当前源文件、PDF哈希和证据文件。见 `reviews/README.md`。

统一发布（默认只检查）：

```bash
python3 tools/release.py --scope main
python3 tools/release.py --scope main --publish
```

发布要求28章、五卷和总册共34份全部通过。缺任何内容、人工证据或来源映射时，正式目录不动。发布成功前将旧目录及构建源归档，再一次性替换，不生成 `final2`。

## 本轮状态

2026-09-04开始全面复核。已有第1—8章底稿，第9—28章尚未编写。`chapter_status.json` 的 `chapters` 记录本轮真实进度；旧第1—7章的 `verified_locked` 已移入 `historical_chapters` 保留，不代表本轮已通过。当前工作详见 `reviews/2026-09-04-progress.md`。不依据“有PDF”“总图数相等”或自动检查通过宣称内容零遗漏。
