---
title: 独立 Change 创建时自动分级与卡片只读展示采集记录
status: done
priority: P2
requirement_id: REQ-0059-standalone-change-auto-classification
created_at: '2026-11-01 00:19:33'
updated_at: 2026-11-01 01:06:07
owner: 产品团队
source: 用户反馈与 explore 结论
lifecycle_stage: archive
parent_requirement: REQ-0057-standalone-change-priority
related_requirements:
- REQ-0057-standalone-change-priority
iteration: null
openspec_changes: []
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - governance
  reason: 涉及分级元数据投影、创建流程与原卡片编辑入口；本次仅采集需求，不修改运行态。暂无 DB、部署、对象存储变更，后续按实际方案复核。
  validation: 后续验证自动评估依据可追溯、分级投影一致、旧编辑入口及相关事件处理、来源 Issue 分级不被覆盖。
---

# 独立 Change 创建时自动分级与卡片只读展示采集记录

## 一句话
独立 Change 创建时由 Agent 自动评估分级：fix 评估严重性，其他类型评估优先级；卡片仅展示结果，移除设置入口。

## 原始描述
用户要求卡片不提供优先级设置，分级应在创建独立 Change 时自动评估；fix Change 评估严重性，非 fix Change 评估优先级。

## 范围与建议验收
- 独立 fix Change 评估 severity，沿用 blocker、critical、high、medium、low；其他独立 Change 评估 priority P0–P3。
- 自动评估结合影响范围、阻断程度、业务价值与紧迫性，保留简短依据，不统一填充默认值。
- 卡片按类型展示分级，移除设置优先级按钮及卡片编辑交互。
- 来源于 REQ/BUG 的 Change 继续引用来源分级，不重复评估或覆盖来源。
- 后续分级调整通过治理流程维护记录；历史缺失等级的补评范围及证据不足策略在需求设计时明确。

## 判重与用户确认
已检查 CHANGELOG 与注册表，发现已归档 REQ-0057 的分级能力直接相关。用户明确选择新建关联子需求，保留原交付历史，单独验收自动评估及移除设置入口。自动分级与只读展示属于同一分级交付闭环，保持单条需求。

## 初判优先级
P2：改善治理信息准确性与操作体验，暂无核心业务阻断证据。

## 待澄清
- fix 类型的权威识别字段与旧命名兼容方式。
- 历史独立 Change 补评范围及信息不足时的处理策略。

## 探索结论
已确认创建时自动分级、卡片只读、来源 Issue 分级继承；本次仅记录，不进入开发。
