---
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
title: 需求中心 Sprint 下拉列表新增状态展示原型上下文
status: pending_review
created_at: 2026-09-14 14:50:40
updated_at: 2026-09-14 14:50:40
---

# 原型上下文

## 1. 页面清单

| 页面 | 入口 | 说明 |
|---|---|---|
| 需求中心 | `/requirements` | 工具栏 Sprint 筛选下拉显示 Sprint 状态。 |

## 2. 关键区域

| 区域 | 说明 |
|---|---|
| 顶部说明区 | 显示需求中心标题、项目状态和刷新入口，原型仅保留上下文。 |
| 统计区 | 显示需求、缺陷、阻塞和漂移指标，验证 Sprint 筛选不会改变统计口径定义。 |
| 筛选工具栏 | 类型、搜索、负责人、优先级、Sprint 筛选；本需求只改 Sprint 筛选。 |
| Sprint 下拉列表 | 展示“全部 Sprint”和具体 Sprint 选项；具体 Sprint 包含状态。 |
| 卡片区 | 验证选择 Sprint 后卡片列表与统计刷新，不在本需求中改卡片布局。 |

## 3. 组件层级

```text
RequirementCenterPage
  -> rc-toolbar
      -> rc-filter-row
          -> type select
          -> search input
          -> owner select
          -> priority select
          -> sprint filter combobox/select
              -> all option
              -> sprint option
                  -> sprint id/name
                  -> status label/text
  -> rc-board / cards
```

## 4. 状态矩阵

| 状态 | 原型表现 | 验收关注 |
|---|---|---|
| all | “全部 Sprint”聚合选项，无状态标签 | 不伪装成单个状态 |
| planning | 规划中 | 低噪音标签，可读 |
| in_progress | 进行中 | 当前迭代可识别，不改变默认行为 |
| completed | 已完成 | 历史迭代可辨认 |
| archived | 已归档 | 与归档目录事实一致 |
| unknown | 状态待核实 | 不阻断选择，异常安全 |
| loading | 下拉禁用或显示加载态 | 不闪现旧项目状态 |
| error | 沿用需求中心错误反馈 | 不暴露内部路径 |
| disabled | 权限或上下文不可用 | focus 和 disabled 可区分 |

## 5. 交互触发

- 点击或键盘打开 Sprint 筛选下拉。
- 浏览不同状态的 Sprint 选项。
- 选择一个具体 Sprint，刷新卡片列表和统计。
- 选择“全部 Sprint”，恢复聚合结果。
- 项目切换或刷新后，重新加载当前项目的 Sprint 状态。
- 状态异常项仍可选择，但展示“状态待核实”。

## 6. 数据依赖

| 数据 | 来源 | 说明 |
|---|---|---|
| sprint id/name | 需求中心上下文或 Sprint 列表接口 | 现有筛选值来源。 |
| sprint status | Sprint 稳定快照、`sprint.yaml`、Workflow Sync 派生或接口结构化字段 | 不由前端自造状态。 |
| issue sprintId | 卡片模型 `visibleSprintId(issue)` 等价事实 | 用于筛选卡片。 |
| permission/context error | 需求中心现有授权与加载错误 | 复用错误反馈。 |

## 7. 响应式断点

| 视口 | 要求 |
|---|---|
| 1440px desktop | 筛选行完整展示，下拉打开态不遮挡关键操作，状态标签不挤压主名称。 |
| 390px mobile | 筛选控件纵向排列或受控换行；下拉选项长文本不溢出。 |
| 矮视口 | 下拉列表可滚动，底部选项可访问。 |

## 8. 1440px 验收焦点

- Sprint 筛选字段与相邻优先级/刷新按钮对齐。
- 下拉打开后，五类状态和异常项视觉层级清晰。
- 长 Sprint ID 不改变工具栏高度或卡片区起始位置。
- 深浅主题下标签颜色与文字对比度可读。
- 键盘 focus ring 不被裁切。

## 9. Mock/API 边界

本原型使用静态 Mock 数据，仅表达布局和状态矩阵，不代表真实 API 已接入。后续 Change 需要确认当前 `RequirementCenterPage` 的 `sprintOptions`、`visibleSprintId(issue)` 和 Sprint 列表/上下文 API 是否已提供结构化状态字段；若没有，应在 OpenSpec 中明确接口扩展或后端派生策略。

## 10. 原型文件

- `prototype.html`：静态布局原型，用于表达筛选下拉状态展示。
- PNG 截图：暂不要求在 `/req-complete` 生成；后续 `/req-opsx` 和 `/opsx-apply` 阶段根据 UI Skeleton 与真实实现补证。

