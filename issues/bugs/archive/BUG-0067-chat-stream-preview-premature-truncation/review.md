---
bug_id: BUG-0067-chat-stream-preview-premature-truncation
title: Chat 流式正文预览过早截断修复评审
review_result: approved
created_at: '2026-10-26 21:58:48'
updated_at: '2026-10-26 21:58:48'
reviewed_at: '2026-10-26 21:58:48'
reviewer: 用户明确批准，Agent 核对证据
---

# Chat 流式正文预览过早截断修复评审

## 评审结论

根据用户本次明确 --approve 授权，评审通过，确认修复。根因证据门禁通过，6 条证据支持原样本的固定片段预览截断与误导提示机制。此结论表示允许后续规划，不表示已经修复或验收通过。

## 评审清单

| 项目 | 结论 | 依据 |
|---|---|---|
| 可复现或根因充分 | 通过 | 用户截图、只读片段统计、前 21 片段匹配及代码路径互相印证，详见 root-cause.md |
| 严重等级合理 | 保持 medium | 影响短正文阅读与执行可信度，未证实业务执行失败、存储内容丢失或安全事故 |
| 回归验收明确 | 通过 | acceptance.md 的 AC-001 至 AC-008 覆盖片段边界、字符预算、历史缺口、最终答案切换、权限与查询成本及真实视觉验证 |
| 是否需要 hotfix | 否 | 无阻断或数据损坏证据，按正常 Sprint 与 OpenSpec 流程交付 |

## 修复范围与约束

修复正文预览以片段数量代替正文体量的提前截断，准确区分正常生成、预览限制和真实缺口。保留有界读取、权限隔离、最终答案选择与去重，禁止以取消所有限制替代修复。

原样本最终答复出现后仍显示执行中的收尾问题不在本条范围。BUG-0056 为观察样本，与其性能根因无确认因果；关联历史 BUG-0030 只用于背景追溯。

## 实施前设计项

在 Change 设计中明确 AC-003/007 的正文预算、分页与查询上界，以及超限查看完整内容入口；如调整 API 原因字段，同步 API 文档、客户端和测试。此处为已识别的设计事项，不将待运行回归标记通过。

product_data_collection_observability: applicable；affected_layers: Web、API、DB 读取、Agent Workflow 输出链路。validation：根因证据门禁通过，既有 8 项验收标准保留。N/A：本次评审无业务代码、数据结构、部署、安全或客户端生成物变更。

## 后续链路

先执行 /sprint-propose --bug BUG-0067-chat-stream-preview-premature-truncation 纳入 Sprint；成功同步为 in_sprint 后才进入 bug-opsx。当前无 Sprint、无 Change，验收未开始。
