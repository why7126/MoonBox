---
purpose: Workflow Sync Issue 输出与 next 推导治理优化
content: 记录子文档 apply 输出明细和 req.opsx/bug.opsx 当前态看板 next 推导修复
created_at: 2026-08-27 08:02:44
updated_at: 2026-08-27 08:02:44
owner: MoonBox 产品团队
---

# Workflow Sync Issue 输出与 next 推导治理优化

## 迭代目标

- 让 `sync-workflow-status.py --apply-issue-subdocuments` 的 summary 输出更明确，能直接看到正文状态块和验收块的 apply 结果。
- 修复 `req.opsx` / `bug.opsx` 后当前态看板 `下一步` 字段仍基于旧派生态推导的问题。

## 变更摘要

- `SyncReport.format_summary()` 增加 Issue 子文档 apply 明细：更新文件数、字段数、验收状态和安全同步项。
- `SyncEngine.run()` 在 `req.opsx` / `bug.opsx` 回填新 Change 后，同步刷新聚焦 Issue 的派生态，确保 CHANGELOG `下一步` 进入 `/opsx-apply <REQ-full-id>` 或 `/opsx-apply <BUG-full-id>`。
- 新增聚焦单元测试覆盖 req.opsx next 推导和子文档 summary 输出。

## 影响范围

- 影响治理脚本：`scripts/workflow_sync/engine.py`。
- 影响测试：`tests/unit/test_workflow_sync_engine.py`。
- 影响 OpenSpec：`openspec/changes/optimize-workflow-sync-issue-output-next/`。
- 不影响 API、DB、Web、客户端、管理端、Orval 或 Docker Compose。

## 更新文件

- `scripts/workflow_sync/engine.py`
- `tests/unit/test_workflow_sync_engine.py`
- `openspec/changes/optimize-workflow-sync-issue-output-next/`
- `iterations/change/sprint-003/sprint.yaml`
- `docs/spec-logs/20260827080244-governance-workflow-sync-issue-output-next.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `pytest tests/unit/test_workflow_sync_engine.py tests/unit/test_workflow_sync_patch.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate optimize-workflow-sync-issue-output-next`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-workflow-sync-issue-output-next --sprint auto`：通过，解析到 `sprint-003`。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-workflow-sync-issue-output-next --sprint sprint-003 --json`：通过，`usage_mode: actual`。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：不适用。
- DB：不适用。
- Web：不适用。
- 客户端：不适用。
- 管理端：不适用。
- Orval：不适用。
- Docker Compose：不适用。

## 后续建议

无。
