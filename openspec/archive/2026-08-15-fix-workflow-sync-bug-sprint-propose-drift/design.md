---
change_id: fix-workflow-sync-bug-sprint-propose-drift
created_at: 2026-08-15 11:45:27
updated_at: 2026-08-15 11:45:27
---

# 技术设计

## 根因

BUG-0013 的证据链确认两类缺口：

- `scripts/workflow_sync/engine.py` 调用 `patch_issue_changelog_index` 的条件未覆盖 `sprint.propose`，导致 BUG 纳入 Sprint 后 `issues/bugs/CHANGELOG.md` 没有被纳入派生刷新报告。
- `scripts/workflow_sync/patch.py` 的 registry 与 trace patch 只同步部分状态字段，未覆盖 Sprint 纳入所需的 `iteration`、`lifecycle_stage`、`path` 和 fenced yaml lifecycle 字段。

## 修复方案

1. 在 Workflow Sync 的 issue focused 路径中，把 `sprint.propose` 纳入 Issue 当前态看板 patch 条件。
2. 让 registry patch 基于已解析的 Issue 目录和 Sprint/Change 上下文派生：
   - `status`
   - `iteration`
   - `lifecycle_stage`
   - `path`
   - `related_change`
3. 让 trace patch 在 `sprint.propose`、`bug.opsx`、`req.opsx` 等链路同步 frontmatter 与 fenced yaml 的一致字段。
4. 保持 `sprint.md` marker block 仍由 Workflow Sync 统一生成，不手工改 marker。

## 测试策略

- focused dry-run：`python scripts/sync-workflow-status.py --event sprint.propose --bug <BUG-full-id> --sprint <sprint-id> --dry-run --output detail`
- focused check：`python scripts/sync-workflow-status.py --event sprint.propose --bug <BUG-full-id> --sprint <sprint-id> --check`
- 回归覆盖：`req.generate` CHANGELOG 刷新、`bug.opsx` Change 回填、目录结构校验、根因证据校验。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance_scripts: true
  governance_docs: true
```
