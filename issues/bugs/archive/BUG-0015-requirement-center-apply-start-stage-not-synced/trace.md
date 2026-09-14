---
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
status: done
created_at: 2026-09-12 17:20:40
updated_at: 2026-09-14 09:00:13
title: 研发启动后需求中心卡片仍停留准备开发态，缺少 apply 启动状态同步
lifecycle_stage: archive
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0014-requirement-center-capture-not-persisted
iteration: sprint-005
openspec_changes:
  - change_id: fix-requirement-center-apply-lifecycle-sync
    type: fix
    status: archived
lifecycle:
  reviewed: 2026-09-12 17:49:30
  approved: 2026-09-12 17:49:30
  captured: 2026-09-12 17:20:40
  completed: 2026-09-12 17:46:16
  generated: 2026-09-12 17:28:58
related_change: fix-requirement-center-apply-lifecycle-sync
severity: medium
---

# BUG-0015-requirement-center-apply-start-stage-not-synced Trace

## 当前状态

已纳入 sprint-005，状态 迭代内，估算M=3人天；根因 confirmed（6条证据，门禁通过），严重度 medium，11项修复验收尚未执行。BUG-0014仅为复现案例；已创建修复Change fix-requirement-center-apply-lifecycle-sync，状态提议态，待实施。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-09-14 08:59:42 | /opsx-archive | Change `fix-requirement-center-apply-lifecycle-sync` 已归档，状态同步完成。 |
| 2026-09-12 21:30:31 | /opsx-apply | Change `fix-requirement-center-apply-lifecycle-sync` apply 完成，待 archive。 |
| 2026-09-12 21:28:53 | /opsx-apply | Change `fix-requirement-center-apply-lifecycle-sync` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-12 21:14:02 | /opsx-apply | Change `fix-requirement-center-apply-lifecycle-sync` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-12 17:20:40 | /bug-capture | captured | 承接 explore 的用户截图、文件状态与合成阶段判定证据，记录启动同步缺口及 0/N 回归范围。 |
| 2026-09-12 17:28:58 | /bug-generate | draft | 生成 bug.md，承接启动同步与状态判定分歧证据，保留真实部署补证边界。 |
| 2026-09-12 17:45:49 | /bug-complete | enriching | 补齐根因、规避、11项验收及合成复现证据，等待根因门禁。 |
| 2026-09-12 17:46:16 | /bug-complete | 评审中 | 根因门禁通过（6条证据），四组合成复现通过；待评审，真实修复验收未执行。 |
| 2026-09-12 17:49:30 | /bug-review | approved | 根因及11项验收范围评审通过；medium / P2，常规修复，待纳入Sprint。 |

- 阶段迁移：plan → review（/bug-review --approve）

## BUG-0015 修复反向追溯

fix-requirement-center-apply-lifecycle-sync 已实现启动事实同步与0/N阶段流转；验证见 openspec/archive/2026-09-14-fix-requirement-center-apply-lifecycle-sync/verification.md。父需求保持历史归档状态，本次交付由BUG-0015与sprint-005承接。
- 2026-09-14 08:59:42 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive BUG-0015-requirement-center-apply-start-stage-not-synced
