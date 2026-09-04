---
change_id: optimize-workflow-sync-issue-output-next
created_at: 2026-08-27 08:02:44
updated_at: 2026-08-27 08:02:44
---

# 技术设计

## 方案

- 在 `SyncReport.format_summary()` 中保留既有聚合输出，并追加每个 Issue 的子文档 apply 明细：`updated_files`、`updated_fields`、`acceptance_status` 和 safe finding 列表。
- 在 `SyncEngine.run()` 处理 `req.opsx` / `bug.opsx` 时，若本轮通过 `--change` 回填了新 Change，则同步修正聚焦 Issue 的 `DerivedIssue.linked_change` 与说明，确保后续 trace、registry 和 CHANGELOG 使用同一轮最新派生态。
- 维持 `--output detail` 的完整明细能力；summary 只展示安全同步项和 warning/blocker 计数，不输出完整日志或无变化文件列表。

## 风险与约束

- summary 会比原来多几行，但只在存在 `subdocument_results` 时输出。
- 不改变 `issue_subdocuments.py` 的安全分类规则，避免误改 `review.md`、`root-cause.md` 等语义不明字段。
- `/opsx-apply` 下一步继续使用完整 REQ/BUG ID，符合链路身份规范。
