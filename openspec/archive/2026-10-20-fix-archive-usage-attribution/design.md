---
title: 用量归属修复设计
created_at: "2026-10-20 19:40:57"
updated_at: "2026-10-20 19:40:57"
---

# 用量归属修复设计

## 根因证据
归档 trace 使用 iteration: sprint-011；wrapper 只读取 sprint。实际桌面会话发现 269 条 token_count、0 条可识别用户消息和 0 条命令记录；用户 content 为 input_text 数组。仅保存结构计数，不转存原始会话。

## 方案
归档入口使用 Workflow Sync 相同的 resolve_sprint_id，不能用任意当前 Sprint 代替 Change 范围。用户消息支持字符串和白名单文本块，忽略图片。仅 token_count 计量，token_usage_record 不重复计数。钩子输出 warnings，令缺少会话、消息、Token 可区分。

## 验证与成本
合成回归验证兼容、隔离与精确数值；真实会话仅记录聚合计数。分析、修复、验收成本统一归属；当前明确单次授权允许 Token 不可得时继续，不能冒充自动预算门禁通过。净收益待观察。

## 数据采集影响
product_data_collection_observability: applicable
affected_layers: governance_usage
validation: 脱敏、归属、重复事件回归及真实采集验证。产品 API/DB/审计/客户端 N/A：未修改业务采集链路。