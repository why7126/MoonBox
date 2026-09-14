---
change_id: refresh-issue-index-after-archive-promotion
created_at: 2026-09-14 09:01:23
updated_at: 2026-09-14 09:01:23
---

## MODIFIED Requirements

### Requirement: Issues 当前态看板索引

MoonBox SHALL 在 `issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` 维护 REQ/BUG 目录级当前态看板索引。该索引 SHALL 每个 Issue 保留一行最新快照，用于快速定位当前状态、阶段、关联 Sprint、关联 Change、下一步和事实源路径；该索引 SHALL NOT 复制单条 Issue `trace.md` 的完整生命周期事件流水。

#### Scenario: Issue 归档迁移后刷新当前态路径

- **WHEN** `promote-issues-for-archive.py` 成功将 REQ 或 BUG 目录从 `review/` 迁入 `archive/`
- **THEN** 系统 SHALL 在同一次 promote 命令内刷新对应 `_registry.yaml` 条目的 `lifecycle_stage` 与 `path`
- **AND** 系统 SHALL 刷新对应 `CHANGELOG.md` 当前态行的阶段、事实源路径与下一步
- **AND** 成功路径不应要求额外运行第二次 Workflow Sync 才能消除 `review/` 路径残留
