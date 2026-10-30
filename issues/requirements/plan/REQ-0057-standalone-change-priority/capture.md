---
title: 独立 Change 优先级定义与卡片展示采集记录
status: captured
priority: P2
created_at: '2026-10-30 09:37:37'
updated_at: '2026-10-30 09:37:37'
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 无来源 Issue 的独立 Change 尚无分级能力，属于新增需求。
lifecycle_stage: plan
iteration: null
openspec_changes: []
requirement_id: REQ-0057-standalone-change-priority
parent_requirement: REQ-0056-requirement-center-change-delivery-cards
related_requirements:
- REQ-0056-requirement-center-change-delivery-cards
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - governance
  reason: 涉及卡片元数据来源与 API 投影；本次仅记录，不修改采集或请求契约。DB、部署、对象存储和安全权限无本次变更。
  validation: 复用探索中的页面与源码证据；后续检查字段来源、权限与日志脱敏，客户端生成依实际 API 差异确定。
---

# 独立 Change 优先级定义与卡片展示采集记录

## 原始描述与范围
用户要求按同会话探索结论记录独立 Change 缺少优先级的问题。面向产品经理，支持无 REQ/BUG 来源的独立 Change 定义、维护和展示优先级；严重度继续专属于 BUG。负责人字段与分级明确区分，缺负责人可显示“负责人未分配”。

## 探索证据
后端 src/backend/app/governance/change_index.py 的 cards 对独立 Change 固定写 priority 为空；现有 rules/document-governance.md 分级契约仅覆盖 REQ 与 BUG。截图的“未分配”对应 owner，不是优先级。

## 判重与用户决策
已检查需求 CHANGELOG 与注册表，并复核 REQ-0026、REQ-0056 的 capture。REQ-0026 为已归档可见性能力；REQ-0056 为待评审的交付卡模型。用户于本轮明确选择作为 REQ-0056 的关联子需求新建，独立定义优先级、单独验收，保留父需求现有状态。

## 建议验收与待澄清
- 独立 Change 优先级可持久化、刷新后正确显示；缺失与非法值不伪造默认等级。
- 明确字段事实源、维护入口、授权、筛选排序及旧 Change 兼容策略；具体设计在 req-generate 收敛。
- 不把 BUG severity 映射为优先级，不覆盖关联 Issue 原分级，不混淆负责人。
- 初判 P2：改善独立治理交付排序，不是当前归档阻断的修复。
