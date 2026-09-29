---
bug_id: BUG-0021-requirement-center-bug-card-severity-display
title: 需求中心 BUG 卡片显示优先级 P 值而非严重性
status: done
created_at: '2026-09-14 13:13:50'
updated_at: 2026-09-14 14:45:11
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0020-req-complete-status-projection-drift
owner: 产品团队
source: /explore 截图反馈
lifecycle_stage: archive
iteration: sprint-006
openspec_changes:
  - change_id: fix-requirement-center-bug-card-severity-display
    type: fix
    status: archived
lifecycle:
  captured: '2026-09-14 13:13:50'
  generated: 2026-09-14 13:59:47
  completed: 2026-09-14 14:01:07
  reviewed: 2026-09-14 14:03:55
  approved: 2026-09-14 14:03:55
related_change: fix-requirement-center-bug-card-severity-display
severity: medium
---

# BUG-0021-requirement-center-bug-card-severity-display Trace

## 来源与范围

用户通过 `/bug-capture` 记录：BUG 类型需求中心卡片不应显示优先级 P 值，而应显示严重性 `severity`。样本为 BUG-0020 卡片显示 `P2`，但事实源为 `severity: medium`。

本次仅记录缺陷，不修改需求中心代码、API schema、测试或 OpenSpec。初步范围为需求中心 REQ/BUG 卡片分级展示契约、API 响应字段和相关测试 fixture。

## 证据入口

- capture.md：用户报告现象、期望与建议验收。
- 用户截图：BUG-0020 卡片分级标签显示 `P2`。
- `rules/document-governance.md`：Issue 分级元数据要求 REQ 使用 `priority`、BUG 使用 `severity`。
- `issues/bugs/archive/BUG-0020-req-complete-status-projection-drift/trace.md`：BUG-0020 当前分级事实源为 `severity: medium`。
- `issues/bugs/archive/BUG-0020-req-complete-status-projection-drift/bug.md`：BUG-0020 主文档镜像为 `severity: medium`。
- `issues/bugs/_registry.yaml`：BUG-0020 注册表分级为 `severity: medium`。
- 只读探索定位到需求中心卡片模型和前端渲染路径仍围绕 `priority` 展示分级标签。
- bug.md：缺陷主文档。
- root-cause.md：confirmed 根因、七条证据、排除假设与修复方向。
- workaround.md：正式修复前以 BUG `severity` 事实源为准的人工规避。
- acceptance.md：六项回归验收标准。
- review.md：评审通过结论、hotfix 判断和后续 Sprint 门禁。
- `openspec/archive/2026-09-14-fix-requirement-center-bug-card-severity-display/`：BUG 来源修复 Change 归档包。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 14:44:34 | /opsx-archive | Change `fix-requirement-center-bug-card-severity-display` 已归档，状态同步完成。 |
| 2026-09-14 14:40:39 | /opsx-modify | Change `fix-requirement-center-bug-card-severity-display` 验收返修已同步，已完成复验并归档。 |
| 2026-09-14 14:25:25 | /opsx-apply | Change `fix-requirement-center-bug-card-severity-display` apply 完成，已归档。 |
| 2026-09-14 14:16:56 | /opsx-apply | Change `fix-requirement-center-bug-card-severity-display` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 14:12:36 | /bug-opsx | 创建 OpenSpec Change `fix-requirement-center-bug-card-severity-display`，已完成归档。 |
| 2026-09-14 14:03:55 | /bug-review | 评审通过，根因证据门禁已过，严重等级 medium，下一步纳入 Sprint。 |
| 2026-09-14 14:02:07 | /bug-complete | BUG-0021-requirement-center-bug-card-severity-display 已完成文档补齐，状态曾同步为待评审，后续已完成归档。 |
| 2026-09-14 14:01:07 | /bug-complete | 根因门禁通过：confirmed，7 条证据；补齐 root-cause、workaround、acceptance，状态推进 pending_review。 |
| 2026-09-14 13:59:47 | /bug-generate | BUG-0021-requirement-center-bug-card-severity-display 已生成 bug.md，状态同步为 draft。 |
| 2026-09-14 13:13:50 | /bug-capture | 创建单条采集记录，严重度 medium，关联需求中心分级展示契约与 BUG-0020 截图样本。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-14 14:44:34 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-requirement-center-bug-card-severity-display
