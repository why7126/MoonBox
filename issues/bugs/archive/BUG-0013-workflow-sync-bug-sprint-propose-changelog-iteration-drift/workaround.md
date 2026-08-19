---
bug_id: BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
workaround_status: documented
created_at: 2026-08-15 11:31:53
updated_at: 2026-08-15 11:31:53
owner:
---

# 临时规避

## 可用 workaround

在正式修复 Workflow Sync 前，执行 BUG `sprint.propose` 后必须补跑 focused 检查：

```bash
python scripts/sync-workflow-status.py --event sprint.propose --bug <BUG-full-id> --sprint <sprint-id> --dry-run --output detail
```

人工确认以下文件是否覆盖目标 BUG：

- `issues/bugs/CHANGELOG.md`
- 目标 BUG `trace.md`
- `issues/bugs/_registry.yaml`
- `iterations/change/<sprint-id>/sprint.yaml`
- `iterations/change/<sprint-id>/sprint.md`

如报告未覆盖 `issues/bugs/CHANGELOG.md` 或 iteration / lifecycle 字段，应暂缓后续 `/bug-opsx`，先通过 `/spec-opt` 修复 Workflow Sync 派生刷新。

## 不建议操作

- 不建议手工批量修改 `sprint.md` workflow-sync marker 块。
- 不建议直接跳过 `CHANGELOG.md` 当前态行刷新。
- 不建议在 trace/registry/CHANGELOG 不一致时继续 `/bug-opsx`。
