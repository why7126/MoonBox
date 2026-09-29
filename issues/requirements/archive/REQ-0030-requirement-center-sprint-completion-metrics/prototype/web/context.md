---
requirement_id: REQ-0030-requirement-center-sprint-completion-metrics
title: 需求中心指标卡 Sprint 数量原型上下文
owner: product
created_at: 2026-09-14 14:50:18
updated_at: 2026-09-14 18:26:44
prototype_status: decomposed
png_required: false
---

# 原型上下文

## 页面清单

| 页面 | 路由/入口 | 说明 |
|---|---|---|
| 需求中心 | `/catalog/requirements` 或现有需求中心入口 | 在既有需求中心顶部指标区新增 Sprint 已完成与总体数量指标，并统一指标说明 tooltip |

## 关键区域

```text
需求中心页面
  |
  +-- Sidebar / 品牌区 / 用户菜单（沿用父 REQ）
  |
  +-- 页面标题与操作区（沿用父 REQ）
  |
  +-- 指标区
  |     |
  |     +-- 既有对象统计卡片
  |     +-- 新增 Sprint 卡片：已完成 / 总体
  |
  +-- 筛选区
  |
  +-- 9 阶段看板
```

## 组件层级

| 组件 | selector 种子 | 说明 |
|---|---|---|
| 指标区容器 | `[data-testid="requirement-center-metrics"]` | 保持既有统计区布局与密度 |
| 指标说明图标 | `.rc-stat-info` | 指标名后的统一说明入口，hover/focus 展示浮层 tooltip |
| Sprint 数量卡 | `[data-testid="sprint-completion-metric"]` | 新增指标卡，标题为 Sprint，展示已完成与总体数量 |
| 已完成数量 | `[data-testid="sprint-completion-metric-completed"]` | 主数字之一 |
| 总体数量 | `[data-testid="sprint-completion-metric-total"]` | 主数字之一 |
| 口径说明 | `.rc-stat-info[data-tooltip]` | 简短说明，避免误解为筛选结果；Sprint 卡片不再使用底部说明文案 |
| 加载状态 | `[data-state="loading"]` | 骨架或保留上一值 |
| 错误状态 | `[data-state="error"]` | 轻量错误提示与重试入口 |
| 空状态 | `[data-state="empty"]` | `0 / 0` |

## 状态矩阵

| 状态 | 已完成 | 累计 | 展示要求 |
|---|---:|---:|---|
| 无 Sprint | 0 | 0 | 展示 `0 / 0`，不隐藏卡片 |
| 仅规划中 Sprint | 0 | N | 已完成为 0，累计为 N |
| 有归档 Sprint | M | N | M 小于或等于 N |
| completed 未归档兼容 | M | N | 按实现阶段固定口径处理并去重 |
| 加载中 | 上一值或骨架 | 上一值或骨架 | 不引起布局跳动 |
| 请求失败 | 上一值或错误占位 | 上一值或错误占位 | 错误文案脱敏，可重试 |
| 权限不足 | 不展示敏感细节 | 不展示敏感细节 | 页面其他区域保持可用 |

## 交互触发

- 首次进入需求中心：请求聚合接口并展示 Sprint 指标。
- 手动刷新：重新请求聚合接口，刷新 Sprint 指标。
- 切换空间：按当前空间上下文刷新 Sprint 指标。
- 搜索或筛选：不改变 Sprint 指标数字，只影响卡片列表和现有局部统计。
- 重试：错误态中触发重新请求，不清空其他可用区域。

## 数据依赖

- `sprint_metrics.completed_count`：已完成 Sprint 数。
- `sprint_metrics.total_count`：累计 Sprint 数。
- `sprint_metrics.source`：口径来源或版本，可用于调试但不得直接暴露内部路径。
- `sprint_metrics.warning`：脱敏口径 warning，例如状态冲突或兼容状态。
- `loading`、`error`、`last_successful_value`：前端展示状态。

## 响应式断点

| 视口 | 要求 |
|---|---|
| 1440px | 指标区与筛选区、9 阶段看板同屏层级清晰；新增卡片不挤压既有卡片文本 |
| 1024px | 指标卡可换行或按既有网格收缩，数字与 tooltip 图标不溢出 |
| 390px | 指标区纵向排列或横向滚动，`已完成 / 总体` 数字不遮挡筛选控件 |

## 1440px 验收焦点

- 深色主题和浅色主题下，新增指标卡与既有指标卡的背景、边框、字号、圆角、间距一致。
- 主数字层级清晰，口径说明通过 tooltip 呈现，不抢占页面标题和筛选区注意力。
- 指标区高度稳定，加载、空态、错误态不会导致看板列头错位。
- 筛选条件变化后，新增指标数字保持项目级总览。
- 错误态文案不展示本机绝对路径、内部异常堆栈或原始治理文档。

## Mock/API 边界

原型 HTML 只表达布局、状态和口径说明，不代表真实 API 已完成。实现阶段必须通过需求中心聚合接口或明确的测试 fixture 提供 `sprint_metrics`，生产默认路径不得使用原型中的静态数字。

## PNG 说明

当前阶段 `prototype.html` 与本 `context.md` 已完成原型拆解；PNG 暂不要求。实现阶段需要在 Change 证据中补 1440px 深浅主题截图和关键响应式截图。
