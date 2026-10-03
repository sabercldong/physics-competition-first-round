# 本轮人工审阅证据

自动编译、渲染、OCR、标签计数都不能生成 `verified` 结论。

最终记录文件名为构建目录名，例如 `chapter-01.json`、`volume-mechanics.json`、`complete-main.json`。必须具有：

- `status: "verified"`；
- `pdf_sha256` 和 `inputs`，对应当前 `build/<构建名>/artifact.json`；
- `checks` 中的 `page_layout`、`figures`、`physics`、`source_completeness`、`pdf_structure` 各含 `status: "passed"`、非空 `evidence` 文件列表，以及记录每个证据文件SHA-256的 `evidence_sha256` 字典；
- `unresolved_findings: []`。

证据文件路径相对本工程，须真实存在且哈希一致；更换核对表或审查记录会使验收失效。人工记录应说明查看过的页码、逐图关系、解答核算、来源对象清单，以及页序/书签/目录检查，不以“已检查”一句话替代。

只完成部分检查时，记录在带日期的 Markdown 工作记录中，不提前创建通过记录。修改任何纳入构建的章节源、样式、资源或构建入口后，旧构建/旧审阅记录自动失效。

`source_inventory/` 下的清单是独立来源对象枚举。它仅说明原件中有哪些对象、对应现稿何处，不等于其解答和图形已正确。源页不能因OCR完成或旧台账已有行就被批量标为已核对。
