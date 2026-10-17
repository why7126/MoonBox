---
bug_id: BUG-0028-requirement-center-card-owner-raw-user-id
title: 需求中心 Capture 卡片直接显示内部用户标识追溯记录
status: approved
created_at: 2026-10-05 22:23:03
updated_at: 2026-10-09 23:21:33
owner: 产品团队
source: 用户截图反馈
lifecycle_stage: review
captured_via: capture
classification_rationale: 已有的需求中心卡片展示将内部用户标识直接呈现给用户，属于现有界面的体验偏差。
iteration:
related_requirement: REQ-0012-frontend-requirement-center
related_bug:
related_change:
openspec_changes: []
lifecycle:
  captured: 2026-10-05 22:23:03
  generated: 2026-10-07 22:23:48
  completed: 2026-10-09 23:17:08
severity: medium
---

# 需求中心 Capture 卡片直接显示内部用户标识追溯记录

## 当前摘要

评审通过，状态为 approved。根因 confirmed：Firefox 刷新后在 REQ-0038 卡片复现截断内部标识，同条目治理 owner、后端原样映射及前端直接渲染形成证据闭环。按正常 Sprint 流程推进；其他部署和 BUG 卡片范围留待修复验收。结论见 review.md。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-09 23:21:33 | /bug-review | approved | 根因、严重度与 AC-001 至 AC-008 评审通过；不走热修，待纳入 Sprint。 |
| 2026-10-09 23:17:08 | /bug-complete | BUG-0028-requirement-center-card-owner-raw-user-id 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-09 23:16:26 | /bug-complete 根因确认 | pending_review | Firefox 刷新后复现 REQ-0038 标签，完成同条目治理值与代码链路核对；根因证据校验通过，待 Workflow Sync。 |
| 2026-10-09 | /bug-complete 运行态补证尝试 | enriching | 浏览器控制调用超时，本机 Web/API 入口连接失败；复核映射及渲染路径，仍缺原环境同条目响应与标签证据，根因保持 probable。 |
| 2026-10-08 22:57:52 | /bug-complete 草稿复核 | enriching | 保留既有成果，补充可复核隔离命令并纠正主文档代码行号；断言 3/3 通过，运行态缺口未消除，completed 保持原值。 |
| 2026-10-08 17:53:55 | /bug-complete 草稿保存 | enriching | 根因 probable；重新核查代码，隔离断言 3/3 通过；运行态缺证，不触发完成态同步。 |
| 2026-10-07 22:23:48 | /bug-generate | draft | BUG-0028-requirement-center-card-owner-raw-user-id 已生成 bug.md，状态同步为 draft。 |
| 2026-10-05 22:23:03 | capture | captured | 根据用户截图记录单一用户信息展示缺陷；严重度暂定 medium。 |

## 完成门禁与关联边界

根因状态：confirmed。Firefox 直接复现、同条目治理值与代码路径构成可复核证据，根因证据校验通过；缺陷包可进入评审。修复后验收场景仍为 pending，不把补齐缺陷包等同于修复完成。仅聚焦同步本 BUG 与工作流派生索引。
- 阶段迁移：plan → review（/bug-review --approve）
