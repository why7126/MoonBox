---
requirement_id: REQ-0031-requirement-center-current-iteration-capacity
title: 需求中心显示当前迭代容量已使用与总容量
prototype: web
status: draft
created_at: 2026-09-14 14:50:31
updated_at: 2026-09-14 14:50:31
---

# Prototype Context

## 页面清单

| 页面 | 路由 | 说明 |
|---|---|---|
| 需求中心 | `/requirements` 或现有需求中心入口 | 在既有需求中心统计/筛选区域增加当前迭代容量展示。 |

## 关键区域

1. 左侧导航与品牌区：沿用 REQ-0012，不在本需求修改。
2. 页面标题与工具栏：保留刷新、搜索和筛选能力。
3. 指标区：新增当前迭代容量项，靠近 Sprint 或当前迭代相关指标。
4. 看板区：9 阶段列、卡片和阶段动作保持既有结构。
5. 轻量反馈区：刷新失败、容量待核实或超量提示以非阻断方式展示。

## 组件层级

```text
RequirementCenterPage
  -> RequirementCenterHeader
  -> RequirementCenterToolbar
  -> CurrentIterationCapacityStrip
      -> CapacityMetricItem (single)
      -> CapacityMetricItem (second current sprint)
      -> CapacityStatusHint
  -> RequirementCenterStats
  -> RequirementKanbanBoard
```

`CurrentIterationCapacityStrip` 为建议组件名，实际实现可合并到现有统计组件，但必须保留稳定 selector 或 data-testid。

## 状态矩阵

| 状态 | 输入示例 | UI 期望 |
|---|---|---|
| 单当前迭代正常 | `sprint-006 18/30` | 展示一个容量项，状态正常。 |
| 单当前迭代接近上限 | `sprint-006 28/30` | 展示关注态，不阻断操作。 |
| 单当前迭代超量 | `sprint-006 32/30` | 展示超量风险提示，不自动阻止浏览。 |
| 双当前迭代 | `sprint-006 18/30`、`sprint-007 9/30` | 两个容量项并列或分组可见。 |
| 默认容量 | total 来自默认规则 | 展示默认来源提示。 |
| 待核实 | total 或 used 缺失/冲突 | 保留 Sprint ID，展示容量待核实。 |
| 刷新失败 | 请求失败但有旧数据 | 保留旧容量项，显示轻量失败反馈。 |
| 无权限 | 用户不可访问 Sprint | 不显示受限 Sprint 数值或名称。 |

## 交互触发

- 进入页面：加载当前项目稳定快照并展示容量。
- 手动刷新：重新请求容量和看板数据。
- 切换项目或空间：清理旧项目容量，加载新项目容量。
- Sprint 筛选变化：容量展示仍表达当前迭代全局信息；若后续设计改为随筛选变化，需在 Change 设计中明确。
- Hover 或 focus 容量提示：展示默认容量、超量或待核实说明。

## 数据依赖

建议容量项最小字段：

```yaml
current_iteration_capacity:
  - sprint_id: sprint-006
    used_capacity: 18
    total_capacity: 30
    capacity_unit: person_day
    capacity_source: explicit | default | unknown
    status: normal | near_limit | over_limit | unknown
    message: null
```

字段名称可在 OpenSpec 阶段调整，但语义必须覆盖已使用、总容量、单位、来源、状态和安全提示。

## 响应式断点

- 1440px：容量项与统计区在首屏可见，不挤压工具栏。
- 1024px：容量项允许换行，保持 Sprint ID 和数值同组。
- 390px：容量项可折叠或纵向排列，但至少显示当前 Sprint ID 和容量比例。

## 1440px 验收焦点

- 容量区域位置是否靠近当前迭代统计或筛选语义。
- 两个当前迭代是否同时可见。
- 深浅主题下正常、超量和待核实状态是否清晰。
- 容量项是否造成统计区、筛选区或看板列头跳动。
- 长 Sprint ID、默认容量提示和刷新失败提示是否遮挡其他内容。

## Mock/API 边界

本原型只描述结构和状态，不代表真实 API 已实现。后续 Change 必须声明哪些字段来自真实需求中心聚合接口，哪些数据仅用于测试 fixture，并禁止 Mock 容量进入生产运行路径。

## PNG 说明

当前 req-complete 阶段不要求导出 PNG；后续 `/req-opsx` 和 `/opsx-apply` 需要根据 UI Skeleton 与真实组件截图补齐 1440px 视觉证据。
