---
bug_id: BUG-0035-requirement-center-acceptance-readiness-projection
title: 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失追溯记录
status: done
created_at: 2026-10-09 22:32:00
updated_at: 2026-10-13 08:26:09
owner: 产品团队
source: 用户截图反馈与只读代码定位
lifecycle_stage: archive
iteration: sprint-009
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0023-requirement-center-acceptance-progress-task-classification
related_change: fix-requirement-center-acceptance-readiness-projection
openspec_changes:
  - change_id: fix-requirement-center-acceptance-readiness-projection
    type: fix
    status: archived
lifecycle:
  captured: 2026-10-09 22:32:00
  generated: 2026-10-09 22:38:20
  completed: 2026-10-09 22:42:33
  reviewed: 2026-10-09 22:47:00
  approved: 2026-10-09 22:47:00
severity: medium
---

# 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失追溯记录

## 当前摘要

已补齐需求中心卡片任务满格但验收未完成、归档提示与实际门禁不一致，以及已生成治理 MD 在后续阶段入口消失的证据与验收标准。BUG-0025 为复现实例；BUG-0023 为已归档的相关任务分类缺陷。卡片展示路径的根因已确认，产品修复和验收尚未执行。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-13 08:26:09 | /opsx-archive | Change `fix-requirement-center-acceptance-readiness-projection` 已归档，状态同步完成。 |
| 2026-10-12 18:08:17 | /bug-capture 补充 | in_sprint | 用户确认将验收中卡片“Change 文档已显示却提示缺少”的截图与前端判断路径关联到现有 BUG-0035；保留原 Sprint、Change 和验收状态，待后续返修验证。 |
| 2026-10-12 15:51:04 | /opsx-accept | Change `fix-requirement-center-acceptance-readiness-projection` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-10-10 07:29:18 | /opsx-modify | Change `fix-requirement-center-acceptance-readiness-projection` 验收返修已同步，待复验或 archive。 |
| 2026-10-10 03:48:43 | /opsx-apply | Change `fix-requirement-center-acceptance-readiness-projection` apply 完成，待 archive。 |
| 2026-10-10 00:04:27 | /opsx-apply | Change `fix-requirement-center-acceptance-readiness-projection` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-09 23:05:16 | /opsx-apply | Change `fix-requirement-center-acceptance-readiness-projection` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-09 22:47:00 | /bug-review | approved | 根因与验收标准通过评审，按常规 Sprint 纳入修复；不代表已完成开发或验收。 |
| 2026-10-09 22:42:33 | /bug-complete | BUG-0035-requirement-center-acceptance-readiness-projection 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-09 22:38:20 | /bug-generate | BUG-0035-requirement-center-acceptance-readiness-projection 已生成 bug.md，状态同步为 draft。 |
| 2026-10-09 22:32:00 | bug.capture | captured | 查重并经用户选择，创建独立关联 BUG；严重度初判 medium。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-10-13 08:26:09 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-requirement-center-acceptance-readiness-projection
