---
created_at: 2026-09-12 17:48:54
updated_at: 2026-09-12 17:48:54
---

# Workflow Sync 分级同步

字段规则与迁移边界见 [文档治理](../../rules/document-governance.md#issue-分级元数据)。

`classification.py` 解析 trace 优先的分级并同步已有 Frontmatter。`collect.py` 保留内部 priority 展示槽以兼容旧调用，但 BUG 槽内只放严重度；`engine.py` 在写入前对聚焦对象校验，`patch.py` 按类型更新注册表与 Sprint 表头。

使用 `sync-workflow-status.py` 的 `--req` / `--bug` / `--change` 聚焦条目，`--dry-run` 不写入，`--check` 检测漂移。Sprint 事件覆盖所选 Sprint 条目。非法或缺失分级先人工在 trace 确认，再重跑；不要把 P2 自动映射为 medium。

验证：`python -m pytest tests/unit/test_issue_classification.py tests/unit/test_workflow_sync_patch.py tests/unit/test_workflow_sync_engine.py -q`。
