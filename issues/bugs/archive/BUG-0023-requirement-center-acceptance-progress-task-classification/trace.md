---
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
title: 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务
status: done
created_at: '2026-09-15 22:32:37'
updated_at: 2026-09-17 10:24:34
related_requirement: REQ-0012-frontend-requirement-center
related_bug: null
owner: 产品团队
source: /bug-capture
lifecycle_stage: archive
iteration: sprint-007
openspec_changes:
  - change_id: fix-requirement-center-acceptance-progress-task-classification
    type: fix
    status: archived
lifecycle:
  captured: '2026-09-15 22:32:37'
  generated: 2026-09-15 22:40:01
  completed: 2026-09-15 22:47:41
  reviewed: 2026-09-15 22:57:14
  approved: 2026-09-15 22:57:14
related_change: fix-requirement-center-acceptance-progress-task-classification
severity: medium
---

# BUG-0023-requirement-center-acceptance-progress-task-classification Trace

## 来源与范围

用户通过 `/bug-capture` 授权记录缺陷。范围为需求中心验收中卡片的研发、测试、人工验收进度口径，以及 `/opsx-modify` 返修任务是否纳入统计。当前已纳入 `sprint-007`，并已创建修复 Change `fix-requirement-center-acceptance-progress-task-classification`。

## 证据入口

- capture.md：现象、复现步骤、期望与实际、建议验收要点。
- bug.md：正式缺陷描述、附件截图摘要、影响范围和严重等级说明。
- root-cause.md：confirmed 根因、证据链、已排除假设、修复方向和验证闭环。
- workaround.md：正式修复前的人工核对规避。
- acceptance.md：修复回归验收标准。
- 用户附件 Image #1：验收中卡片展示研发、测试、人工验收满格或完成态的截图证据摘要。
- 代码证据：需求中心后端进度聚合、前端人工验收推导、前端卡片渲染和现有测试 fixture。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 10:24:34 | /opsx-archive | Change `fix-requirement-center-acceptance-progress-task-classification` 已归档，状态同步完成。 |
| 2026-09-15 23:33:10 | /opsx-apply | Change `fix-requirement-center-acceptance-progress-task-classification` apply 完成，后续已完成归档。 |
| 2026-09-15 23:17:53 | /opsx-apply | Change `fix-requirement-center-acceptance-progress-task-classification` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-15 23:10:51 | /bug-opsx | 创建 OpenSpec Change `fix-requirement-center-acceptance-progress-task-classification`；下一步执行 /opsx-apply。 |
| 2026-09-15 23:04:03 | /sprint-propose | 纳入 sprint-007；后续已执行 /bug-opsx 创建修复 Change。 |
| 2026-09-15 22:57:14 | /bug-review | 评审通过，确认按常规 Sprint 纳入修复；下一步先执行 /sprint-propose。 |
| 2026-09-15 22:50:06 | /bug-complete | BUG-0023-requirement-center-acceptance-progress-task-classification 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-15 22:47:41 | /bug-complete | 根因门禁通过：confirmed，8 条证据；补齐 root-cause、workaround、acceptance，状态推进 pending_review。 |
| 2026-09-15 22:40:01 | /bug-generate | BUG-0023-requirement-center-acceptance-progress-task-classification 已生成 bug.md，状态同步为 draft。 |
| 2026-09-15 22:32:37 | /bug-capture | 创建单条 BUG，严重度 medium，关联 REQ-0012，记录验收中进度口径未按 `tasks.md` 分类统计且未纳入返修任务。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-17 10:24:34 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive BUG-0023-requirement-center-acceptance-progress-task-classification
