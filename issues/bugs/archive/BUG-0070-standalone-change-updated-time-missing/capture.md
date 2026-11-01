---
title: 独立 Change 卡片更新时间缺失采集记录
status: done
severity: medium
created_at: '2026-10-30 09:37:37'
updated_at: 2026-10-31 23:01:58
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 已有卡片更新时间展示因事实源字段缺失退化，属于缺陷。
lifecycle_stage: archive
iteration: null
openspec_changes: []
bug_id: BUG-0070-standalone-change-updated-time-missing
related_requirement: null
related_bug: null
environment: local
root_cause_status: confirmed
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

# 独立 Change 卡片更新时间缺失采集记录

## 现象与复现
2026-10-30 同会话 Firefox 已登录的本地 /requirements 页面，刷新至 09:33:58 后，fix-archive-finalization-consistency 卡片仍显示“更新时间未知”。该对象来源 sprint-016，研发任务 7/7；来源迭代不等于本 BUG 已纳入该迭代。

1. 打开需求中心，定位上述独立 Change。
2. 刷新看板，观察卡片底部更新时间。
3. 对照 Change trace 元数据与卡片投影。

## 期望与实际
期望：有效业务更新时间可显示且来源可追溯，旧数据兼容不虚构更新时间。实际：Change trace 无 created_at、updated_at，虽有 execution.started_at/completed_at，卡片仅读取前两个字段，最终显示未知。

## 已确认的证据与边界
- 用户附件截图和本轮前一探索中的 Firefox 刷新观察一致；复用会话观察，不声称本次再次浏览或已保存截图附件。
- openspec/changes/fix-archive-finalization-consistency/trace.md 缺少上述两个字段。
- src/backend/app/governance/change_index.py 的 cards 只以 trace.updated_at 或 created_at 投影 updated_at。
- src/web/src/pages/catalog/RequirementCenterPage.tsx 的 rc-updated 对无有效格式显示“更新时间未知”。
- 显示链路根因 confirmed；具体哪个创建/同步入口遗漏维护字段仍需后续追溯，不能将执行完成时间直接当作最后更新时间。

## 判重与拆分
已检查 BUG CHANGELOG 与注册表。用户管理时间展示问题属于其他模块；BUG-0039 为 Sprint 归属误报、BUG-0018 为验收来源识别，均非本时间字段链路。与归档按钮检查入口故障修复面不同，独立记录。

## 建议验收
覆盖新建、apply、modify、归档后的时间维护及历史缺字段兼容；刷新后显示与事实源一致；不得把文件复制时间或当前查询时间冒充业务更新时间。初判 medium：影响进度判断但无数据丢失或执行阻断证据。
