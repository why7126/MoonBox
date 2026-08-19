---
change_id: fix-workflow-sync-bug-sprint-propose-drift
acceptance_status: not_started
created_at: 2026-08-15 11:45:27
updated_at: 2026-08-15 11:45:27
source_bug: BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
---

# 验收计划

## 验收标准

| AC | 描述 | 验收方式 |
|---|---|---|
| AC-001 | `sprint.propose --bug` dry-run/detail 报告覆盖 `issues/bugs/CHANGELOG.md` | 运行 focused dry-run 并检查报告 |
| AC-002 | BUG trace frontmatter 与 fenced yaml 同步 `status: in_sprint`、`iteration: sprint-xxx`、`lifecycle.stage: review` | 检查目标 BUG trace |
| AC-003 | `issues/bugs/_registry.yaml` 同步 `status`、`iteration`、`lifecycle_stage`、`path` | 检查目标 registry entry |
| AC-004 | `issues/bugs/CHANGELOG.md` 同步状态、阶段、Sprint、Change、下一步和事实源 | 检查当前态行 |
| AC-005 | 不破坏 REQ/BUG 其他 Workflow Sync 事件 | 运行 focused check 或相关测试 |

## 验收结果

```yaml
accepted_at: null
accepted_by: null
evidence: []
failed_items: []
```
