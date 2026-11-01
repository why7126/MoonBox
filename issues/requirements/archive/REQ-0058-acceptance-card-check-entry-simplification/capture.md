---
requirement_id: REQ-0058-acceptance-card-check-entry-simplification
status: done
priority: P2
created_at: '2026-10-31 23:08:26'
updated_at: 2026-11-01 00:26:32
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 调整已交付检查入口的展示位置，保留检查能力，属于交互改进需求。
lifecycle_stage: archive
iteration: null
openspec_changes: []
related_requirement: REQ-0056-requirement-center-change-delivery-cards
related_bug: BUG-0071-change-summary-acceptance-check-entry-missing
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  reason: 涉及Web检查入口和既有API请求关联；DB、部署、对象存储无变更，保持既有权限。
  validation: AC-008验证行为与请求关联、权限与脱敏；产品运行验收待实现。
  standard_ref: docs/standards/product-data-collection-observability.md
title: 验收中卡片检查入口展示简化采集记录
---

# 验收中卡片检查入口展示简化采集记录

## 一句话
移除验收中卡片“检查验收条件 / 验收待检查”整行，将检查能力保留在操作流程内。

## 原始描述与范围
用户截图红框标出检查按钮和待检查状态整行；要求整体移除并收起空白。红框外失败提示不默认删除。不得移除实际验收校验、放宽归档门禁或自动归档。

## 建议验收
- 验收中卡片不再出现该整行及占位空白。
- 操作流程仍可检查、显示结果、失败重试，检查通过后归档仍独立确认。
- 覆盖 Issue 来源和独立 Change 卡片；入口位置及弹窗交互在需求完善阶段确定。

## 判重与授权
关联已归档 BUG-0071-change-summary-acceptance-check-entry-missing，其目标是补足检查入口；本项调整展示位置。用户明确选择新建关联项、保留历史交付，独立闭环。

## 证据
用户本会话标注截图；src/web/src/pages/catalog/RequirementCenterPage.tsx 中 acceptance-check 区块。截图未另存仓库，本次未新增运行态复验。

## 优先级依据
P2：界面信息简化，保留核心检查功能。
