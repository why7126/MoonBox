---
bug_id: BUG-0048-chat-legacy-panel-cleanup-removes-conversation
severity: high
created_at: '2026-10-19 18:48:04'
updated_at: 2026-10-19 22:43:47
owner: 产品团队
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0047-review-recovery-operation-record-missing
title: 旧治理面板清理误删聊天会话区域
status: done
---

# 旧治理面板清理误删聊天会话区域

## 缺陷描述

旧面板清理遍历所有带 aria-label 的节点，正文命中“确认应用”等旧面板文字时误删 chat-main。影响历史会话阅读和发送，严重度 high。

## 复现

1. 在带 aria-label 的 chat-main 中渲染包含“确认应用”的普通消息。
2. 调用 removeLegacyGovernancePanels。
3. 主区域与消息被删除；预期保留，仅清理明确旧面板。

## 范围

修正 runtimeBuild.ts 清理候选选择，覆盖所有旧文案、正常 dialog、带标签容器和重复调用。保留真正旧面板清理。API、DB、权限和 UI 布局不变。
