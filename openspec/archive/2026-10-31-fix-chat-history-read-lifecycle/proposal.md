---
title: 聊天历史读取生命周期修复提案
created_at: "2026-10-31 08:19:14"
updated_at: "2026-10-31 08:19:14"
---

# 聊天历史读取生命周期修复提案

## 背景

来源：[BUG-0058](../../../issues/bugs/review/BUG-0058-chat-history-status-replay-request-amplification/bug.md)，已批准并纳入 sprint-017。历史正文已出现时状态仍重建，同轮事件首页实际读取三次；隐藏详情继续取数。

## 变更内容

统一轮次摘要与事件请求生命周期，终态展示不依赖完整事件回放；详情按需加载，恢复查询避免重叠。保留权限、成果核验和活跃任务状态更新。

## 能力影响

新增能力规格 chat-history-read-lifecycle，补充现有 web-catalog-chat-workbench 的读取约束，不替换其已有执行与权限要求。

## 影响范围

Web 聊天状态、页脚、执行详情与恢复面板。优先复用现有 API，不预设数据库或部署改动。若现有摘要不足则在本 Change 内明确契约并同步 OpenAPI、客户端与接口文档后实施。

## 回滚方案

回退本次读取层及消费者接入改动，恢复旧读取行为；不删除事件和历史会话，不修改业务事实。新增接口字段如需引入须保持兼容，回退前端不要求数据库恢复。

## 观测声明

product_data_collection_observability: applicable；affected_layers: Web、API、request_logs、Task Trace。validation: 复用已确认机制证据，修复后逐AC对照；现有请求关联透传保留，禁止缓存凭证和消息原文日志。DB、对象存储、部署、保留周期暂为N/A，因本方案不改变这些契约。
