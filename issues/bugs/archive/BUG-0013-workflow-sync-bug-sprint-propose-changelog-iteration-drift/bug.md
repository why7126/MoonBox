---
bug_id: BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
title: Workflow Sync 对 BUG sprint.propose 的 CHANGELOG/iteration 派生刷新不完整
severity: medium
priority: P2
status: done
owner:
discovered_at: 2026-08-15 11:11:51
environment: local governance workflow
related_requirement:
related_change: fix-workflow-sync-bug-sprint-propose-drift
created_at: 2026-08-15 11:29:52
updated_at: 2026-08-15 12:29:48
---

# Workflow Sync 对 BUG sprint.propose 的 CHANGELOG/iteration 派生刷新不完整

## 现象

在 BUG 通过 `sprint.propose` 纳入 Sprint 的场景中，Workflow Sync 对 BUG 当前态看板和 iteration 相关派生字段的刷新覆盖不够完整。

可能表现为：

- `issues/bugs/CHANGELOG.md` 中对应 BUG 当前态行未完整刷新状态、阶段、关联 Sprint、最近更新时间、下一步或事实源路径。
- BUG `trace.md` 或 `issues/bugs/_registry.yaml` 中的 `iteration`、`status`、`lifecycle_stage` 与 Sprint 纳入结果存在漂移。
- Sprint 四件套已经包含 BUG，但 BUG 目录级看板或派生字段仍停留在旧状态。

## 复现步骤

1. 准备一个已评审通过、尚未纳入 Sprint 的 BUG。
2. 执行 `/sprint-propose --bug <BUG-full-id>` 或等价 Workflow Sync 链路。
3. 运行或观察：

```bash
python scripts/sync-workflow-status.py --event sprint.propose --bug <BUG-full-id> --sprint <sprint-id> --dry-run --output detail
```

4. 对比以下事实源是否同步：
   - BUG `trace.md`
   - `issues/bugs/_registry.yaml`
   - `issues/bugs/CHANGELOG.md`
   - `iterations/change/<sprint-id>/sprint.yaml`
   - `iterations/change/<sprint-id>/sprint.md`

## 期望结果

BUG 纳入 Sprint 后，Workflow Sync 应完整刷新：

- BUG `trace.md` 的 `status: in_sprint`、`iteration: sprint-xxx`、`lifecycle_stage: review` 或等价状态块。
- `issues/bugs/_registry.yaml` 对应 entry 的 `status`、`iteration`、`lifecycle_stage`、`path`。
- `issues/bugs/CHANGELOG.md` 对应 BUG 当前态行的状态、阶段、关联 Sprint、最近更新时间、下一步和事实源路径。
- Sprint 四件套中与该 BUG 相关的 scope、验收和发布摘要派生内容。

## 实际结果

当前观察到 `BUG sprint.propose` 场景下，CHANGELOG/iteration 派生刷新不够完整，可能导致事实源和当前态看板之间出现漂移。

## 影响范围

- BUG 纳入 Sprint 后的状态追踪。
- `issues/bugs/CHANGELOG.md` 当前态看板可信度。
- 后续 `/bug-opsx`、`/opsx-apply <BUG-full-id>` 的链路判断。
- Sprint 范围和 BUG 事实源的一致性复核。

## 严重等级说明

严重等级为 `medium`：该问题不直接影响业务运行时功能，但会影响治理链路的状态一致性和后续命令判断，可能造成重复排查或错误下一步建议。

## 证据状态

当前证据来自用户在近期 Workflow Sync 治理链路中的观察，以及相邻 `req.generate` CHANGELOG 派生覆盖问题的已修复经验。仍需在 `/bug-complete` 阶段补充 focused dry-run 报告或真实执行报告，确认具体缺口和根因。
