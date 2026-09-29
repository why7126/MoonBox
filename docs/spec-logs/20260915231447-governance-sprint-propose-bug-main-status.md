---
purpose: 治理迭代日志
content: Workflow Sync sprint.propose 聚焦 BUG 主文档状态同步优化记录
created_at: 2026-09-15 23:14:47
updated_at: 2026-09-15 23:24:10
owner: MoonBox 产品团队
---

# Workflow Sync sprint.propose BUG 主状态同步

## 迭代目标

减少 `/sprint-propose --bug <BUG-full-id>` 后的人工聚焦修正：当 BUG 被正式纳入 Sprint 并由 Workflow Sync 派生为 `in_sprint` 时，已存在的 `bug.md` Frontmatter `status` 也应自动同步为同一主状态。

## 变更摘要

- 在 Workflow Sync 子文档同步判定中补齐 `sprint.propose` 聚焦 REQ/BUG 分支。
- 保持同步范围限定为当前命令传入的 `--req` 或 `--bug`。
- 增加聚焦单元测试，验证 `sprint.propose --bug` 会触发主文档同步并传递 `in_sprint` 派生态。

## 影响范围

- Workflow Sync 治理脚本：影响 `sprint.propose` 聚焦 Issue 的子文档状态镜像。
- REQ/BUG 文档：只自动更新聚焦 Issue 的主文档状态；不批量重写历史文档。
- API/DB/Web/客户端/管理端/Orval/Docker Compose：不适用，本次不触达业务运行时、接口、数据库、前端、客户端生成或部署编排。

## 更新文件

- `scripts/workflow_sync/engine.py`
- `tests/unit/test_workflow_sync_engine.py`
- `openspec/changes/sync-sprint-propose-bug-main-status/`
- `iterations/change/sprint-007/sprint.yaml`
- `docs/spec-logs/20260915231447-governance-sprint-propose-bug-main-status.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `python -m py_compile scripts/workflow_sync/engine.py`：通过。
- `python -m pytest tests/unit/test_workflow_sync_engine.py -k sprint_propose_syncs_focused_bug_primary_document`：通过，1 passed。
- `python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0023-requirement-center-acceptance-progress-task-classification --sprint sprint-007 --dry-run`：通过，报告子文档 `checked=7`、`updated=1`，验证聚焦 BUG 主文档进入同步路径；dry-run 未写入该 BUG。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py --change sync-sprint-propose-bug-main-status --residual-report`：通过，未发现非当前 Change 中文残留。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate sync-sprint-propose-bug-main-status --strict`：通过。
- `python scripts/validate-sprint-scope.py sprint-007 --item sync-sprint-propose-bug-main-status`：通过。
- `python scripts/sync-workflow-status.py --sprint auto --check`：通过，updated=0，skipped=17。
- `python scripts/sync-workflow-status.py --event opsx.apply --change sync-sprint-propose-bug-main-status --sprint auto`：通过，updated=3。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change sync-sprint-propose-bug-main-status --sprint sprint-007 --json`：warning，usage_mode unavailable，未发现可归因 command-run token 事件；不阻断本次治理变更。

## 后续建议

无。
