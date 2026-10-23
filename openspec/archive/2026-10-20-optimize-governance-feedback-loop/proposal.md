---
title: 治理执行量化与分级优化闭环
created_at: 2026-10-20 18:18:42
updated_at: 2026-10-20 18:18:42
---

# 治理执行量化与分级优化闭环

## 背景
现有 AI Usage 记录模型消耗，执行复盘仅提供建议，缺少运行边界、量化归因、优化预算和修复收益判定。用户授权在治理范围内自动优化规范、技能和脚本，保留 Change、Sprint 和验证门禁。

## 变更内容
- 新增标准库治理运行台账与 CLI，记录真实耗时、Token 可用性、质量、版本与优化自身成本。
- 统一分级决策、去重、预算、防递归、授权范围与前置门禁；Agent 按决策执行治理修复，脚本不执行会话代码。
- 对可比样本计算净收益，区分交付通过、待观察、收益确认和退化。
- 接入 AI Usage 完成 Hook 与中央技能契约，采集失败非阻断并提供修复路径。

## 能力影响
### 新增能力
- `governance-feedback-loop`：治理调用指标、受控优化与效果评估。
### 修改能力
无正式规格直接修改。

## 影响范围
仅 AGENTS、rules、docs、skills、scripts、治理测试及当前 Change/Sprint。无业务 src、API、DB、UI、部署和客户端生成变化。纯治理 Change 无 REQ/BUG 来源，仍纳入 Sprint。

## 数据采集声明
product_data_collection_observability: applicable

affected_layers: [agent_workflow_governance]

validation: 本地脱敏台账、幂等、缺失用量、预算、范围、收益与失败降级测试。usage_events/request_logs/产品 task_traces、对象存储、OpenAPI/Orval 为 N/A：不改产品运行态，仅治理 CLI 采集。
