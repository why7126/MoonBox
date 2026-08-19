---
bug_id: BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
title: Workflow Sync 对 BUG sprint.propose 的 CHANGELOG/iteration 派生刷新不完整
status: done
severity: medium
priority: P2
lifecycle_stage: plan
reporter: user
owner:
related_requirement:
related_bug:
related_change:
captured_via: capture
classification_rationale: 已有 Workflow Sync 治理能力在 BUG 纳入 Sprint 场景下派生刷新不完整，属于既有流程行为偏差，归类为 BUG。
created_at: 2026-08-15 11:11:51
updated_at: 2026-08-15 12:29:53
---

# 缺陷收集

## 原始描述

这次发现 Workflow Sync 对 BUG sprint.propose 的 CHANGELOG/iteration 派生刷新不够完整。

## 分类结果

- 类型：BUG
- 严重等级：medium
- 优先级：P2
- 影响范围：Workflow Sync、BUG Sprint 纳入流程、`issues/bugs/CHANGELOG.md` 当前态看板、BUG trace / registry 的 iteration 派生刷新。

## 现象

当 BUG 通过 `sprint.propose` 纳入 Sprint 时，Workflow Sync 对 BUG 当前态看板和 iteration 相关派生字段的刷新覆盖不够完整，可能导致事实源与目录级看板或派生字段出现漂移。

## 期望

`python scripts/sync-workflow-status.py --event sprint.propose --bug <BUG-full-id> --sprint <sprint-id|auto>` 或等价链路应完整刷新：

- BUG `trace.md` 中的 `status`、`iteration`、`lifecycle_stage` 或相关状态块。
- `issues/bugs/_registry.yaml` 中对应 BUG 的 `status`、`iteration`、`lifecycle_stage`。
- `issues/bugs/CHANGELOG.md` 中对应 BUG 当前态行的状态、阶段、关联 Sprint、最近更新时间、下一步和事实源路径。

## 初步证据

- 用户在执行近期治理链路后观察到 BUG `sprint.propose` 场景存在 CHANGELOG/iteration 派生刷新不完整。
- 已有相邻治理刚补过 `req.generate` 对 `issues/requirements/CHANGELOG.md` 的派生刷新覆盖，说明当前态看板刷新需要由 Workflow Sync 显式覆盖并验证。

## 待补证

- 选择一个已 approved、尚未 in_sprint 的 BUG 作为样本。
- 运行 `python scripts/sync-workflow-status.py --event sprint.propose --bug <BUG-full-id> --sprint <sprint-id> --dry-run --output detail`。
- 返回报告中 `Updated` / `Skipped` 涉及的 `trace.md`、`_registry.yaml`、`issues/bugs/CHANGELOG.md` 和 Sprint 四件套条目。

## 下一步建议

`/bug-generate BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift`
