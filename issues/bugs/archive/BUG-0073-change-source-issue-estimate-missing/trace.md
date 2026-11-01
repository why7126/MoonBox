---
bug_id: BUG-0073-change-source-issue-estimate-missing
status: done
severity: medium
created_at: '2026-10-31 23:08:26'
updated_at: 2026-11-01 00:02:00
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 已有来源 Issue 估算未在交付卡片展示，属于数据展示偏差。
lifecycle_stage: archive
iteration: sprint-018
openspec_changes:
- change_id: fix-change-source-issue-estimate
  type: fix
  status: archived
related_requirement: REQ-0056-requirement-center-change-delivery-cards
related_bug: BUG-0070-standalone-change-updated-time-missing
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  reason: 涉及检查入口或估算投影；本次仅采集。DB、部署、对象存储不涉及；不改变安全授权。
  validation: 后续验证现有请求关联与检查门禁；API及客户端生成依契约差异决定。本次仅文档校验。
title: Change 卡片未展示来源 Issue 已有人力估算追溯记录
lifecycle:
  captured: '2026-10-31 23:08:26'
  generated: '2026-10-31 23:13:54'
  completed: '2026-10-31 23:16:00'
  reviewed: '2026-10-31 23:19:08'
  approved: '2026-10-31 23:19:08'
root_cause_status: confirmed
related_change: fix-change-source-issue-estimate
---

# Change 卡片未展示来源 Issue 已有人力估算追溯记录

## 当前摘要
已评审并纳入sprint-018，修复已实现及验证，状态由Workflow Sync维护；证据见关联Change verification.md。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-11-01 00:02:00 | /opsx-archive | Change `fix-change-source-issue-estimate` 已归档，状态同步完成。 |
| 2026-10-31 23:54:35 | /opsx-accept | Change `fix-change-source-issue-estimate` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-10-31 23:53:25 | /opsx-apply | Change `fix-change-source-issue-estimate` apply 完成，待 archive。 |
| 2026-10-31 23:46:38 | /opsx-apply | Change `fix-change-source-issue-estimate` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-31 23:40:36 | /opsx-apply | Change `fix-change-source-issue-estimate` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-31 23:16:13 | /bug-complete | BUG-0073-change-source-issue-estimate-missing 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-31 23:14:09 | /bug-generate | BUG-0073-change-source-issue-estimate-missing 已生成 bug.md，状态同步为 draft。 |
| 2026-10-31 23:08:26 | capture | captured | 用户确认新建关联项，保留历史交付 |
| 2026-10-31 23:13:54 | bug.generate | draft | 生成缺陷文档，真实scope函数复现取值缺失 |
| 2026-10-31 23:16:00 | bug.complete | pending_review | 根因证据、临时建议及8条AC补齐，修复未实施 |
| 2026-10-31 23:19:08 | bug.review | approved | 根因机制证据充分，常规修复，不走hotfix |

- 阶段迁移：plan → review（/bug-review）
- 2026-11-01 00:02:00 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-change-source-issue-estimate
