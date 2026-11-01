---
title: 独立 Change 自动分级与卡片只读展示提案
requirement: REQ-0059-standalone-change-auto-classification
iteration: sprint-018
created_at: 2026-11-01 00:32:30
updated_at: '2026-11-01 00:57:00'
---

# 独立 Change 自动分级与卡片只读展示提案

## 背景
当前独立 Change 统一维护优先级并在卡片提供编辑。用户要求创建时自动评估，fix 使用严重性，其他类型使用优先级，卡片只读。父需求 REQ-0057 已交付，本次演进其行为。

## 变更内容
- 新建独立 Change 自动识别类型、评估等级并记录依据，信息不足明确待补充。
- 卡片正确展示严重性或优先级，移除编辑入口，保留来源 Issue 分级。
- 兼容旧对象并保护历史，不批量补评归档。
- 旧 priority API 对 fix 拒绝写入，其他合法调用维持授权与并发控制；这是类型约束变化，旧客户端需兼容错误响应。

## 能力影响
### 新增能力
无独立新增能力。
### 修改能力
- standalone-change-priority：分级事实源、创建评估、卡片展示与旧接口约束。

## 影响范围
backend、web、api、治理创建技能及规则、OpenAPI/客户端生成和测试；无新增数据库表、部署服务或对象存储读写。Sprint估算M/3人天；容量30.5/30人天，无剩余缓冲。实施及验收结果见 trace.md 与自动验收报告。
