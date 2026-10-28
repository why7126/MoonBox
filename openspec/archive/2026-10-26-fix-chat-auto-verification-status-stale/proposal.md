---
title: Chat 自动核验状态持续更新修复提案
created_at: '2026-10-26 18:50:07'
updated_at: '2026-10-26 18:50:07'
---

# Chat 自动核验状态持续更新修复提案

## 背景
来源：[缺陷说明](../../../issues/bugs/review/BUG-0066-chat-auto-verification-status-stale/bug.md) 与 [根因证据](../../../issues/bugs/review/BUG-0066-chat-auto-verification-status-stale/root-cause.md)。DirectCompletion 仅挂载时读取，执行终态后父组件也停止轮询，后台自动核验成功无法持续反映。隔离组件已复现；截图时序与人工点击历史不能倒推。

## 变更内容
独立跟踪核验生命周期，区分自动处理中、失败需处理与成功；增加有界刷新、去重退避、取消及旧响应保护，保留手动核验的权限与版本围栏。

## 能力影响
### 新增能力
无独立新能力。
### 修改能力
- governance-command-durable-recovery：补充本缺陷的行为约束与回归场景。

## 影响范围
DirectCompletion.tsx、TurnActivity.tsx、核验状态接口及生成类型、governanceRequest 请求链路和前后端回归。
纳入sprint-014，估算3人天；本命令仅生成方案，未开发或验收。

## 回滚方案
回退兼容应用版本，保留原始成果、队列和保护事实；详细边界见design.md。
