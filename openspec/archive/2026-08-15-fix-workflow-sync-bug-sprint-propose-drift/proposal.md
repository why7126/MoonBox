---
change_id: fix-workflow-sync-bug-sprint-propose-drift
change_type: fix
status: applied
created_at: 2026-08-15 11:45:27
updated_at: 2026-08-15 12:29:13
source_bug: BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
source_sprint: sprint-003
related_specs:
  - agent-workflow-tooling
---

# 修复 Workflow Sync 的 BUG sprint.propose 派生刷新漂移

## 背景

`BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift` 已确认根因：`sprint.propose --bug` 链路在 BUG 纳入 Sprint 后，未完整刷新 `issues/bugs/CHANGELOG.md`、`issues/bugs/_registry.yaml`、BUG `trace.md` 的 iteration/lifecycle 字段，导致 Sprint 四件套与 BUG 事实源之间出现漂移。

本缺陷会影响后续 `/bug-opsx`、`/opsx-apply <BUG-full-id>` 的链路判断，也会让当前态看板给出错误下一步。

## 变更内容

- 扩展 Workflow Sync 在 `sprint.propose` 聚焦 BUG/REQ 时的 Issue 当前态看板刷新覆盖。
- 扩展 registry patch，使其同步 `status`、`iteration`、`lifecycle_stage`、`path` 和关联 Change。
- 扩展 trace patch，使其同步 frontmatter 与 fenced yaml 中的 `status`、`iteration`、`lifecycle.stage`、`related_change` 和 `openspec_changes`。
- 增加 focused 回归校验，覆盖 BUG sprint.propose 后的 CHANGELOG、trace、registry 与 Sprint scope 一致性。

## 非目标

- 不改业务 `src/`。
- 不改 API、数据库、UI、部署或客户端生成物。
- 不重写 Workflow Sync 整体架构。

## 回滚计划

如修复导致 Workflow Sync 其他事件误刷新：

1. 回退本 Change 对 `scripts/workflow_sync/**` 和相关测试的修改。
2. 保留已创建的 BUG/OpenSpec 文档事实源，不回退历史评审和 Sprint 纳入记录。
3. 使用 `python scripts/sync-workflow-status.py --event <event> --dry-run --output detail` 定位受影响事件，再按证据补充 BUG 或返修。

## 归档验证摘要

- 任务状态：`tasks.md` 6/6 完成。
- 规格同步：delta spec 修改 `agent-workflow-tooling` 的 `Issues 当前态看板索引` Requirement。
- 文档同步：已写入 `docs/spec-logs/20260815120052-governance-workflow-sync-bug-sprint-propose-drift.md` 并更新 `docs/spec-logs/CHANGELOG.md`。
- 验证结果：OpenSpec strict、中文语言、目录结构、focused pytest、Workflow Sync `sprint.propose --check` 和 `opsx.apply --check` 均通过。
