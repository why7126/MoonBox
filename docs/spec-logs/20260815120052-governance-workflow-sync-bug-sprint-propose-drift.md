---
title: 修复 BUG sprint.propose 派生刷新漂移
purpose: 记录 Workflow Sync 对 BUG sprint.propose 的 CHANGELOG、trace、registry 派生刷新修复
content: 治理脚本、OpenSpec Change、回归测试和验证结果
source: /opsx-apply BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
owner: MoonBox 产品团队
created_at: 2026-08-15 12:00:52
updated_at: 2026-08-15 12:00:52
---

# 修复 BUG sprint.propose 派生刷新漂移

## 背景

BUG-0013 的证据链显示，Workflow Sync 在 `sprint.propose --bug` 场景下未完整刷新 BUG 当前态看板、registry 和 trace 的 iteration/lifecycle 字段，导致 Sprint 四件套与 BUG 事实源之间出现漂移。

## 更新内容

- 扩展 `scripts/workflow_sync/engine.py`，让 focused `sprint.propose` 纳入 Issue 当前态看板刷新。
- 扩展 `scripts/workflow_sync/patch.py`，让 registry 同步 `status`、`iteration`、`lifecycle_stage`、`path` 和 `related_change`。
- 扩展 BUG/REQ trace patch，写入 frontmatter 与 fenced yaml 中的 `iteration`、`lifecycle.status`、`lifecycle.stage`、`lifecycle.iteration` 和关联 Change。
- 修复 CHANGELOG 当前态行的 check 幂等性，避免只因更新时间重新生成而持续 drift。
- 增加 `tests/unit/test_workflow_sync_patch.py` 覆盖 BUG sprint.propose 派生刷新与幂等行为。

## 验证结果

- `python -m py_compile scripts/workflow_sync/engine.py scripts/workflow_sync/patch.py`：通过。
- `pytest tests/unit/test_workflow_sync_patch.py`：1 passed。
- `python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift --sprint sprint-003 --dry-run --output detail`：`issues/bugs/CHANGELOG.md` 出现在 Skipped 列表。
- `python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift --sprint sprint-003 --check`：`Updated: 0`，`Errors: 0`。

## 影响与边界

本次只触达 Workflow Sync 治理脚本、OpenSpec/BUG/Sprint 文档和测试，不涉及 API、数据库、UI、部署、安全策略或客户端生成。

## 后续建议

无。
