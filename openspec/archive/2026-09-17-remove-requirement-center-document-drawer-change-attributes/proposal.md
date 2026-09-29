---
change_id: remove-requirement-center-document-drawer-change-attributes
title: 需求中心文档抽屉移除 Change 属性模块
type: update
status: proposed
created_at: 2026-09-15 23:32:00
updated_at: 2026-09-16 08:45:49
source_requirement: REQ-0036-requirement-center-document-drawer-simplification
source_sprint: sprint-007
---

# 需求中心文档抽屉移除 Change 属性模块

## 背景

需求中心右侧文档抽屉当前在正文前展示“Change 追溯属性”模块，混合 Change 状态、任务进度、关联文档和告警。用户阅读文档时更需要稳定的“文档属性 + 正文”结构；独立 Change 仅显示任务进度时价值有限，多 Change 场景又容易混淆 Issue trace 与 Change trace。

REQ-0036 已明确要求直接删除整个 Change 属性模块，不把它迁移为抽屉内的新折叠区，同时保留底层关联 Change 数据和文档可达性。

## 变更内容

- 删除 REQ、BUG 和独立 Change Markdown 文档抽屉中的“Change 追溯属性”模块。
- 文档抽屉加载完成后只保留标题区、文档属性区和正文阅读区；删除后不得留下空白占位、残留边框、贴边文本或重复分隔线。
- 保留 `current_change`、`related_changes`、`task_progress`、`warnings`、`drift_warnings` 和 `document_entries` 等底层事实供抽屉外入口使用。
- 保留单 Change、多 Change、独立 Change 的文档可达入口；入口位于抽屉外的卡片、详情或既有文档分组中，不在抽屉内重建同类模块；卡片侧关联 Change 文档入口保持紧凑，不展开完整 Change ID。
- 回归现有文档读取权限、只读策略、草稿保护、缺失文档提示、筛选、搜索、刷新和阶段按钮。

## 能力影响

### 新增能力

无。本变更不引入新的业务能力。

### 修改能力

- `web-catalog-requirement-center`：修改需求中心 Markdown 文档抽屉和卡片文档查看约束，要求文档抽屉移除 Change 属性模块并保持抽屉外 Change 文档入口可达。

## 影响范围

- Web：`src/web/src/pages/catalog/RequirementCenterPage.tsx` 和需求中心相关样式、前端测试。
- API：预期不修改 API、OpenAPI、Orval 或请求封装；若实现中必须新增入口字段，需先补充设计和观测声明。
- DB：无 schema、索引、迁移或保留周期变化。
- 权限与安全：复用现有项目、空间成员、对象读取授权和文档 URL 约束，不放宽访问边界。
- UI 验收：需要 1440px 与窄视口截图、深浅主题、长标题/长 ID/长正文，以及文档属性区 computed style 证据。
