---
bug_id: BUG-0029-chat-workbench-nonempty-page-scroll
title: Chat 工作台非空白对话出现页面级滚动条及底部布局异常追溯记录
status: done
created_at: 2026-10-05 22:31:19
updated_at: 2026-10-12 23:01:32
owner: 产品团队
source: 用户截图反馈
lifecycle_stage: archive
captured_via: capture
classification_rationale: 已有 Chat 工作台在非空白对话场景出现页面级滚动和布局异常，属于现有界面行为偏差。
iteration: sprint-008
related_requirement: REQ-0025-chat-workbench
related_bug: BUG-0027-page-scroll-bottom-light-background-exposed
related_change: fix-chat-workbench-nonempty-page-scroll
openspec_changes:
  - change_id: fix-chat-workbench-nonempty-page-scroll
    type: fix
    status: archived
lifecycle:
  reviewed: 2026-10-06 00:45:16
  approved: 2026-10-06 00:45:16
  captured: 2026-10-05 22:31:19
  generated: 2026-10-05 23:17:21
  completed: 2026-10-06 00:32:39
severity: medium
---

# Chat 工作台非空白对话出现页面级滚动条及底部布局异常追溯记录

## 当前摘要

用户反馈 Chat 工作台非空白对话出现页面级垂直滚动条，向下滚动后页面布局异常。已关联归档的 BUG-0027，按用户选择作为独立缺陷跟踪。Firefox 实际复现并完成样式因果对照，根因已确认；修复与验收尚未执行。

## 重复/相似检查

| 候选 | 当前状态 | 相似原因 | 处理方式 |
|---|---|---|---|
| 2026-10-06 00:45:16 | /bug-review | approved | 根因证据校验通过，确认修复，验收未开始。 |
| BUG-0027-page-scroll-bottom-light-background-exposed | done / archive | 同属页面滚动边界问题，但本条有非空白对话触发条件及页面级滚动条的独立验收目标 | 用户确认新建关联 BUG |

## 证据摘要

| 证据 | 结论 |
|---|---|
| capture 中记录的用户截图反馈摘要 | 用户报告非空白对话页面级滚动和底部布局异常；原图未复制到仓库 |
| Firefox `/chat` 长对话，1419×832 视口 | `body.scrollHeight=2021`，页面可滚动 1189 px；消息区内部也可滚动 |
| DevTools 临时样式对照 | 10 个消息角色标签绝对定位到 BODY；将标签设为 static 或给消息卡片设 relative，页面高度降至 832；恢复后回到 2021 |

## 待补证项

| 证据名称 | 需要内容 |
|---|---|
| 修复后回归 | 空白、短/长对话在桌面视口的页面与消息区滚动；输入区可见性 |
| 跨浏览器影响 | Chromium 等浏览器是否同样产生页面外层溢出 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-12 23:01:32 | /opsx-archive | Change `fix-chat-workbench-nonempty-page-scroll` 已归档，状态同步完成。 |
| 2026-10-12 22:57:30 | /opsx-accept | Change `fix-chat-workbench-nonempty-page-scroll` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-10-07 18:22:57 | /opsx-apply | Change `fix-chat-workbench-nonempty-page-scroll` apply 完成，待 archive。 |
| 2026-10-07 13:37:20 | /opsx-apply | Change `fix-chat-workbench-nonempty-page-scroll` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-07 13:23:54 | /opsx-apply | Change `fix-chat-workbench-nonempty-page-scroll` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-06 00:38:02 | /bug-complete | pending_review | BUG-0029-chat-workbench-nonempty-page-scroll 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-05 23:17:21 | /bug-generate | draft | BUG-0029-chat-workbench-nonempty-page-scroll 已生成 bug.md，状态同步为 draft。 |
| 2026-10-05 22:31:19 | capture | captured | 用户确认独立创建关联缺陷，记录页面级滚动条与底部布局异常。 |
| 2026-10-05 23:22:51 | /bug-complete 草稿保存 | enriching | 根因 unknown；保存根因、规避与验收草稿，补证待执行；不推进待评审，不写完成时间。 |
| 2026-10-05 23:59:51 | /bug-complete 草稿复核 | enriching | 保留既有补证清单与验收草稿，修正材料已保存及截图引用表述；无新增直接证据，完成时间保持原值。 |
| 2026-10-06 00:17:20 | /bug-complete 连续补证 | enriching | 回填布局静态线索及端口访问拒绝证据；未确认根因，保留完成时间与待执行验收。 |

## 本轮治理草稿与门禁

主状态 approved；根因 [confirmed](root-cause.md)，规避方案未验证，验收 pending。既有截图条目是 capture 阶段反馈引用，本轮未将原图或会话正文落盘。

本轮更新目标缺陷文档并运行完成态 Workflow Sync；iteration 与 openspec_changes 保留原值。未修改业务代码或 OpenSpec。
- 阶段迁移：plan → review（/bug-review --approve）

## 评审同步范围

标准 Workflow Sync dry-run 会更新父需求关联缺陷索引，超出本轮授权，因此未执行标准全量写入；按预演结论仅同步目标 BUG 主文档、trace、注册表条目与索引行。目录完整迁入 review，既有其他子文档保留；后端应用结果尚未确认。
- 2026-10-12 23:01:32 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-chat-workbench-nonempty-page-scroll
