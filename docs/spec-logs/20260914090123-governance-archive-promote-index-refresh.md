---
purpose: 治理迭代日志
content: Issue archive promote 后自动刷新 registry 与当前态看板
created_at: 2026-09-14 09:01:23
updated_at: 2026-09-14 09:06:20
owner: MoonBox 产品团队
---

# Issue 归档迁移后索引刷新治理优化

## 迭代目标

优化 `promote-issues-for-archive.py`，使 REQ/BUG 迁入 `archive/` 后自动刷新 registry 与当前态看板，避免归档命令需要额外运行第二次 Workflow Sync 才消除旧路径。

## 变更摘要

- promote 成功后重新加载已迁移 Issue。
- 复用 Workflow Sync 的派生与 patch 函数刷新 `_registry.yaml` 和 `CHANGELOG.md`。
- 增加单元测试覆盖 archive 路径刷新。

## 影响范围

- 治理脚本：`scripts/promote-issues-for-archive.py`
- 测试：`tests/unit/test_promote_issues_for_archive.py`
- OpenSpec Change：`openspec/changes/refresh-issue-index-after-archive-promotion/`

## 更新文件

- `scripts/promote-issues-for-archive.py`
- `tests/unit/test_promote_issues_for_archive.py`
- `openspec/changes/refresh-issue-index-after-archive-promotion/*`
- `docs/spec-logs/20260914090123-governance-archive-promote-index-refresh.md`

## 验证结果

- `uv run --with pytest --with pyyaml pytest tests/unit/test_promote_issues_for_archive.py tests/unit/test_workflow_sync_patch.py -q`：2 passed。
- `uv run --with pytest --with pyyaml pytest tests/unit/test_promote_issues_for_archive.py tests/unit/test_workflow_sync_patch.py tests/unit/test_workflow_sync_collect.py -q`：4 passed。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate refresh-issue-index-after-archive-promotion`：valid。
- `python scripts/validate-sprint-scope.py sprint-005 --item refresh-issue-index-after-archive-promotion`：pass。
- Workflow Sync `opsx.apply`：Updated=2，Errors=0。
- AI Usage Hook：warning/unavailable，未发现可归因 token_count 事件。
- 归档后补验：纯治理 Change 的 proposal 正文提到 BUG 编号时，不再被误判为关联 Issue；sprint-005 changes 表已回到 `—`。

## 边界说明

API、DB、Web、客户端、管理端、Orval、Docker Compose 均不适用；本次不修改业务运行时代码，不新增数据采集或链路观测字段。

## 后续建议

归档技能可继续保留 promote 后的路径复核，但成功路径不应要求手工二次同步。
