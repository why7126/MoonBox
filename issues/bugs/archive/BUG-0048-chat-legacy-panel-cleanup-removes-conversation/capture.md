---
bug_id: BUG-0048-chat-legacy-panel-cleanup-removes-conversation
severity: high
created_at: '2026-10-19 18:48:04'
updated_at: 2026-10-19 22:43:48
owner: 产品团队
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0047-review-recovery-operation-record-missing
title: 旧治理面板清理误删聊天会话区域记录
status: done
---

# 旧治理面板清理误删聊天会话区域记录

## 现象与复现

已登录 Chat 打开含“后端确认应用后”正文的历史会话，加载后主区域消失，仅剩侧栏。刷新仍复现。预期聊天正文与轨迹、输入区始终保留。

## 判重

已检查 BUG 索引与注册表；BUG-0029 为滚动边界，BUG-0047 为后端恢复记录，均与本次 DOM 清理范围独立。本次仅一条缺陷。

## 证据

上一轮浏览器截图 logs/review-recovery-deployment/page-verification.jpg；实际 runtimeBuild 清理函数最小 DOM 调用返回 removed=2、chatMainRetained=false。
