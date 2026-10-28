---
title: Chat 最终回答去重与历史投影修复提案
created_at: '2026-10-26 18:50:07'
updated_at: '2026-10-26 18:50:07'
---

# Chat 最终回答去重与历史投影修复提案

## 背景
来源：[缺陷说明](../../../issues/bugs/review/BUG-0065-chat-final-answer-duplicate-concatenation/bug.md) 与 [根因证据](../../../issues/bugs/review/BUG-0065-chat-final-answer-duplicate-concatenation/root-cause.md)。同一最终答案经正常完成与恢复路径使用不同来源前缀落库，读取端拼接全部 final，形成完整回答重复。机制已经隔离复现；历史样本原始 item ID 未留存，不扩张为每次重复的唯一上游原因。

## 变更内容
统一逻辑答案身份与分片幂等，定义完整最终版本选择；消息预览、历史全文分页和复制使用一致投影。兼容旧记录且不批量删除原数据、不重放业务。

## 能力影响
### 新增能力
无独立新能力。
### 修改能力
- codex-session-execution：补充本缺陷的行为约束与回归场景。

## 影响范围
execution.py、content_store.py、assistant_output.py、结果分页读取及相关 Web 展示测试；涉及数据库持久化语义与 SQLite/MySQL 回归。
纳入sprint-014，估算3人天；本命令仅生成方案，未开发或验收。

## 回滚方案
回退兼容应用版本，保留原始成果、队列和保护事实；详细边界见design.md。
