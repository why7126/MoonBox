---
title: Change 来源人力估算缺失验收清单
created_at: '2026-10-31 23:16:00'
bug_id: BUG-0073-change-source-issue-estimate-missing
acceptance_status: passed
updated_at: 2026-11-01 00:02:00
---

# Change 来源人力估算缺失验收清单

## 回归验收
- [x] AC-001 唯一来源与唯一交付的3人天记录正确展示，并可识别引用来源。
- [x] AC-002 存在Change自身合法估算时优先自身，不覆盖来源。
- [x] AC-003 一对多未分配估算不复制、不均分；明确归属的分项仅用于目标交付。
- [x] AC-004 多来源冲突、非法数值、缺失分别提示，零值是有效0而非缺失。
- [x] AC-005 刷新、阶段切换及归档展示一致；未授权来源信息不泄漏。
- [x] AC-006 Sprint总容量与已用量保持原事实源口径，无重复累计，无源文档写入。
- [x] AC-007 单元与真实浏览器证据分别记录；展示3人天不标为实际耗时。
- [x] AC-008 复用现有API请求日志与关联，不记录来源全文或凭证；无契约变化不生成客户端。

## 诊断与验收边界
根因机制confirmed；修复与逐项验证已执行，所有AC通过，最终状态由结构化验收同步。API投影与Web为适用层级；数据库、部署、对象存储无修改目标。观测依据docs/standards/product-data-collection-observability.md。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-11-01 00:02:00
accepted_by: workflow-sync
source_change: fix-change-source-issue-estimate
source_sprint: sprint-018
evidence: [openspec/archive/2026-10-31-fix-change-source-issue-estimate/evidence/acceptance/20261031235345727111-7cd273ef/summary.md]
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本轮逐项证据
AC-001/005/007：真实本地39002页面、1440/390截图与计算样式，见关联Change evidence/acceptance/visual-review.md；现有归档样本未重新归档。AC-002/003/004/006：test_change_source_estimate.py及test_delivery_cards.py覆盖优先级、分项、冲突、权限和源文件哈希。AC-008：完整/摘要API与既有请求观测回归。视觉与合成测试分开记录，未宣称真实Chat执行轮次。
