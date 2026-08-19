---
bug_id: BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
acceptance_status: passed
created_at: 2026-08-15 11:31:53
updated_at: 2026-08-15 12:29:57
owner:
---

# 验收标准

## 回归验收

| AC | 描述 | 验收方式 |
|---|---|---|
| AC-BUG-001 | `sprint.propose --bug <BUG-full-id>` dry-run/detail 报告覆盖 `issues/bugs/CHANGELOG.md` 对应 BUG 行 | 运行 Workflow Sync dry-run，检查 Updated 或 Skipped 列表 |
| AC-BUG-002 | BUG 纳入 Sprint 后，`trace.md` frontmatter 与 yaml lifecycle 同步 `status: in_sprint`、`iteration: sprint-xxx` 和阶段信息 | 检查目标 BUG trace 片段 |
| AC-BUG-003 | `issues/bugs/_registry.yaml` 同步目标 BUG 的 `status`、`iteration`、`lifecycle_stage` 和 `path` | 检查 registry 目标 entry |
| AC-BUG-004 | `issues/bugs/CHANGELOG.md` 当前态行同步状态、阶段、关联 Sprint、最近更新时间、下一步和事实源路径 | 检查 CHANGELOG 目标行 |
| AC-BUG-005 | 修复后不破坏 REQ/BUG capture、generate、complete、opsx archive 等既有 Workflow Sync 派生刷新 | 运行上下文预算、目录结构、focused Workflow Sync dry-run 或相关测试 |

## 验收风险

- 若没有一个 approved 且尚未 in_sprint 的 BUG 样本，可使用临时测试 fixture 或 dry-run 构造样本验证。
- 验收不得依赖手工修改当前态看板；必须由 Workflow Sync 派生刷新。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-15 12:29:57
accepted_by: workflow-sync
source_change: fix-workflow-sync-bug-sprint-propose-drift
source_sprint: sprint-003
evidence: []
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

