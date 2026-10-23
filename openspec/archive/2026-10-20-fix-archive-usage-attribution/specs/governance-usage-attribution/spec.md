---
title: 治理用量归属
created_at: "2026-10-20 19:40:57"
updated_at: "2026-10-20 19:40:57"
---

# 治理用量归属

## ADDED Requirements

### Requirement: 归档用量采用同源 Sprint 归属与桌面消息解析
归档用量 MUST 采用 Workflow Sync 的 Change 范围解析 Sprint，采集器 MUST 支持字符串及文本块数组，不重复统计同一调用的旁路用量事件，不持久化原始会话。

#### Scenario: 已归档 Change 仅声明 iteration
- **WHEN** Change 已在 Sprint 范围内且 trace 使用 iteration
- **THEN** 钩子使用同一 Sprint，保留 BUG 链路

#### Scenario: 桌面用户消息内容数组
- **WHEN** 用户消息包含 input_text 与非文本块，且存在 token_count
- **THEN** 解析命令并按 token_count 记录实测数值，忽略非文本与重复旁路事件

#### Scenario: 证据缺失
- **WHEN** 会话、用户消息或 Token 证据缺失
- **THEN** 输出可区分的脱敏诊断，不伪造 Token 或收益
