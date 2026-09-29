---
requirement_id: REQ-0033-requirement-center-filter-multiselect-search
title: 需求中心筛选下拉框支持复选搜索多选与排序优化
prototype_type: web
status: decomposition_done
created_at: 2026-09-14 14:50:41
updated_at: 2026-09-14 14:50:41
---

# Prototype Context

## 页面清单

| 页面 | 入口 | 说明 |
|---|---|---|
| 需求中心 | 前台需求中心路由 | 在既有工具栏中替换或增强枚举类筛选下拉控件 |

## 关键区域

| 区域 | 说明 | 变化 |
|---|---|---|
| 标题与统计区 | 保持父需求现有结构 | 不变 |
| 工具栏 | 搜索、类型、状态、负责人、Sprint 等筛选控件 | 枚举类筛选下拉升级为可搜索多选 |
| 多选下拉浮层 | 搜索输入、候选列表、复选框、清空入口、空态 | 新增 |
| 看板列与卡片 | 9 阶段看板和卡片 | 数据受筛选条件影响，结构不变 |

## 组件层级

```text
RequirementCenterPage
  Toolbar
    GlobalSearchInput
    MultiSelectFilterTrigger
      SelectedSummary
      ClearDimensionButton
    MultiSelectFilterPopover
      FilterSearchInput
      OptionList
        OptionRow
          Checkbox
          Label
          Meta
      EmptyState
      FooterActions
  KanbanBoard
    StageColumn
      IssueCard
```

## 状态矩阵

| 组件 | 状态 | 期望 |
|---|---|---|
| Trigger | default | 显示默认占位和下拉指示 |
| Trigger | selected-small | 显示 1-2 个选项名称 |
| Trigger | selected-many | 显示已选数量摘要 |
| Trigger | focus | 可见 focus ring，不改变布局 |
| Popover | open | 面板覆盖工具栏下方，不推动页面布局 |
| Search | typing | 候选项即时过滤 |
| Search | empty-result | 显示轻量空态，已选项保持 |
| Option | checked | 复选框选中，行状态清晰 |
| Option | unchecked | 复选框未选，行可点击 |
| Option | disabled | 不可选且说明原因或禁用态明显 |
| Popover | click-outside | 外部点击关闭，内部点击不误关闭 |

## 交互触发

- 点击触发器打开下拉。
- 输入关键词过滤候选项。
- 点击候选项或复选框切换选择。
- 点击单维度清空按钮清空当前维度。
- 点击全局清空筛选恢复默认条件。
- 点击外部区域或按 Esc 关闭下拉。
- 手动刷新时保留当前筛选条件。

## 数据依赖

| 数据 | 来源 | 备注 |
|---|---|---|
| 候选项列表 | 需求中心上下文数据 | 只能包含当前用户有权访问的对象和枚举 |
| 当前用户 | 需求中心上下文数据 | 可用于负责人排序 |
| 当前 Sprint | Sprint scope 或需求中心上下文 | 可用于 Sprint 排序 |
| 卡片列表 | 已加载的需求中心对象 | 首版可前端过滤 |
| 权限态 | 后端授权与上下文字段 | 不由前端筛选推断 |

## 响应式断点

| 断点 | 期望 |
|---|---|
| 1440px | 工具栏可完整展示，浮层宽度稳定，候选列表可滚动 |
| 1024px | 筛选控件允许换行或收敛摘要，不遮挡刷新和全局搜索 |
| 390px | 触发器优先显示数量摘要；浮层宽度受视口约束；列表可触控滚动 |

## 1440px 验收焦点

- 工具栏控件间距、对齐、字号和边框符合 MoonBox Ops 视觉。
- 下拉浮层与触发器对齐，层级高于看板卡片。
- 搜索输入、复选框、候选项和清空入口不溢出。
- 搜索无结果和多选摘要不导致工具栏高度跳动。
- 深浅主题均具备可读对比。

## Mock/API 边界

本原型使用静态候选项展示结构和状态，不代表 API 已修改。后续实现若继续使用现有需求中心上下文数据，需在 Change 中声明为前端筛选；若新增 API 查询或 URL 持久化，需补齐 API、观测和安全验收。

## PNG 状态

PNG 暂不要求在 req-complete 阶段导出；后续 `/req-opsx` 和 `/opsx-apply` 以 UI Skeleton 与 1440px 截图作为视觉证据。
