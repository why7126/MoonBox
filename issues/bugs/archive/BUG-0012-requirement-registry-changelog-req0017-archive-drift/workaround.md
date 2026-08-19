---
bug_id: BUG-0012-requirement-registry-changelog-req0017-archive-drift
created_at: 2026-08-15 10:46:46
updated_at: 2026-08-15 10:46:46
---

# 临时规避方案

## 当前规避

在正式修复前，人工查阅 `REQ-0017-admin-space-management` 时以单条 REQ 事实源为准：

- `issues/requirements/archive/REQ-0017-admin-space-management/trace.md`
- `openspec/archive/2026-08-14-add-admin-space-management/`

不要依据 `issues/requirements/_registry.yaml` 或 `issues/requirements/CHANGELOG.md` 中的 `review/` 路径执行 `/opsx-apply REQ-0017-admin-space-management`。

## 风险与限制

- 该规避只适用于人工查阅和命令判断，不会修复目录级索引中的漂移。
- 如果脚本或自动化流程读取 `_registry.yaml` / `CHANGELOG.md` 的当前态快照，仍可能被旧路径或旧下一步误导。
- 不建议长期保留，应通过 BUG 修复链路同步两个目录级索引。

## 回滚策略

本 BUG 修复只涉及治理文档索引。如修复后发现状态不一致，应以 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` 与 OpenSpec archive 目录为事实源回滚或重新同步索引。
