---
req_id: REQ-0036-requirement-center-document-drawer-simplification
title: 需求中心文档抽屉简化与 Change 属性模块移除
status: done
created_at: '2026-09-14 10:26:42'
updated_at: 2026-09-17 08:35:51
recorded_by: product
source: 用户反馈
parent_requirement: REQ-0026-requirement-center-standalone-change-cards
priority: P2
---

# 需求中心文档抽屉简化与 Change 属性模块移除

## 一句话
移除需求中心文档抽屉的 Change 追溯属性模块，保留文档属性与正文，确保多 Change 关联及其文档仍有可达入口。

## 原始描述
简化需求中心文档抽屉：移除 Change 追溯属性模块，保留文档属性与正文，并确保多 Change 关联及文档仍有可达入口。

## 背景与范围
- 来源：本会话两轮 /explore 与用户截图反馈，用户明确选择界面简化方案。
- 独立 Change 抽屉中追溯面板仅显示任务进度时信息有限，占用正文阅读空间；截图还呈现文字贴边和空告警分隔符。
- 当前实现位于 src/web/src/pages/catalog/RequirementCenterPage.tsx，追溯面板同时承担关联 Change 的进度展示与文档导航，不能仅删除后造成多 Change 入口丢失。
- 同一交付单元覆盖面板移除及导航承接，不拆分；作为已交付父需求的体验 refinement 单独记录，不改写父需求交付状态。
- 初判 P2：阅读体验与信息架构优化，暂无核心业务阻断证据。
- 适用于 REQ、BUG 和独立 Change 的文档抽屉；保留文档属性、正文及原有文档操作和权限边界。
- 保留底层关联关系与 trace.md；不删除 Change 数据、不改变阶段映射或任务完成语义。

## 待澄清
- [ ] 多 Change 入口承接在卡片还是详情；先核对可复用入口，再确定最小调整方案。
- [ ] 关联 Change 的进度与异常提示需要在哪个现有位置保留，避免有效信息丢失。

## 建议验收方向
- 各类文档抽屉均不再显示 Change 追溯属性模块，无空白占位；文档属性展开/收起与正文阅读正常。
- 单个和多个关联 Change 均能辨识并打开对应文档，包括 trace.md，不串读其他 Change。
- 独立 Change 文档入口、只读/编辑权限和现有文档操作不回归。
- 后续在 1440px 和窄视口验证间距、滚动、展开状态与文档导航；补充截图及 computed style 证据。

## 探索结论
用户已确认移除模块并保留关联文档可达性的方向；导航承接位置留待需求细化，不预设新增独立页面。

## 影响层与观测
- product_data_collection_observability: N/A（当前采集范围）
- affected_layers: [web]
- reason: 本次仅记录界面展示与导航调整，计划复用现有文档读取及权限链路，不新增 API、DB、请求日志、行为事件、Task Trace 或请求封装；若后续入口方案改变请求或埋点，重新评估适用性。
- validation: 已基于截图和前轮代码阅读识别现状；实现阶段验证文档可达性、权限及交互回归。参考 docs/standards/product-data-collection-observability.md。
