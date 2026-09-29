---
requirement_id: REQ-0034-requirement-center-default-current-iteration-cards
title: 需求中心默认只显示当前迭代卡片
prototype: web
prototype_status: draft
owner: product
source: requirement.md
created_at: 2026-09-14 14:56:26
updated_at: 2026-09-14 23:55:00
---

# Prototype Context

## 页面清单

| 页面 | 入口 | 目标 |
|---|---|---|
| 需求中心默认视图 | 前台需求中心 | 默认展示当前迭代和未纳入 Sprint 卡片，并在既有 Sprint 多选中直接选中这些范围 |
| 当前迭代空态 | 前台需求中心 | 无当前迭代或当前迭代无卡片时，默认保留未纳入 Sprint 对象，并允许清空 Sprint 多选查看全部 |
| 多当前迭代状态 | 前台需求中心 | 默认选中多个当前 Sprint 和未纳入 Sprint，并允许进一步取消或筛选单个 Sprint |
| 非当前范围状态 | 前台需求中心 | 用户通过清空 Sprint 多选、选择历史 Sprint 或归档 Sprint 查看非当前对象 |

## 关键区域

1. 页面标题区：保留需求中心标题、摘要和手动刷新入口。
2. 指标区：保持既有指标卡，不因默认范围文案挤压卡片。
3. 筛选工具栏：复用 Sprint 多选状态，默认选中当前 Sprint 和未纳入 Sprint；保留搜索、对象类型、负责人、优先级等既有筛选。
4. Sprint 多选区：通过下拉选中状态表达当前迭代、多当前迭代或非当前范围，不新增筛选模块下方提示。
5. 看板区：九阶段列和卡片组件保持既有密度、sticky 表头和横向滚动。
6. 空态/错误态：当前迭代无卡片、无当前迭代、解析失败时提供查看全部或重试入口。

## 组件层级

```text
RequirementCenterPage
  -> PageHeader
  -> MetricSummary
  -> FilterToolbar
      -> SearchInput
      -> TypeSegment
      -> SprintSelector
      -> Owner/Priority filters
      -> ResetButton
  -> KanbanBoard
      -> StageColumnHeader
      -> CardList
          -> RequirementCard / BugCard / ChangeCard
  -> EmptyState / ErrorState
```

## 状态矩阵

| 状态 | 触发 | UI 表现 | 数据边界 |
|---|---|---|---|
| single-current | 一个当前 Sprint | Sprint 多选默认选中该 Sprint 和未纳入 Sprint，展示两个范围卡片 | 当前 Sprint scope + no sprint |
| multi-current | 多个 planning/in_progress Sprint | Sprint 多选默认选中全部当前 Sprint 和未纳入 Sprint，触发器显示多选状态 | 多 Sprint scope 并集 + no sprint |
| no-current | 无当前 Sprint | Sprint 多选默认选中未纳入 Sprint，不伪装为当前 | no sprint |
| no-card | 有当前 Sprint 但无卡片 | 当前 Sprint 和未纳入 Sprint 选中但看板空态，用户可清空 Sprint 查看全部 | 当前 Sprint scope + no sprint 为空 |
| custom-sprint | 用户显式调整 Sprint 选择 | Sprint 多选显示用户选择，刷新保留选择 | 用户选择优先 |
| error | 接口或解析失败 | 脱敏错误态，保留可重试入口 | 不暴露路径、堆栈、密钥 |

## 交互触发

- 首次进入：自动选中当前 Sprint 集合和未纳入 Sprint。
- Sprint 切换：用户清空 Sprint、选择历史/归档 Sprint 或取消部分当前 Sprint 后，卡片集合更新。
- Sprint 细分：多当前迭代时，用户可进一步保留单个 Sprint。
- 重置筛选：恢复当前 Sprint + 未纳入 Sprint 默认选中状态。
- 手动刷新：保留用户当前显式 Sprint 选择。
- 空间/项目切换：重新计算新上下文的当前迭代。

## 数据依赖

- 真实需求中心稳定快照。
- Sprint lifecycle stage 与 status。
- Sprint scope 中的 requirements、bugs、changes。
- REQ/BUG trace 与 registry。
- OpenSpec Change trace 与归档路径。
- 权限、冻结空间、只读用户和项目绑定信息。

## 响应式断点

| 视口 | 验收焦点 |
|---|---|
| 1440px desktop | 标题、指标、工具栏、Sprint 多选、九阶段表头和首屏卡片稳定对齐 |
| 1024px tablet | 工具栏可换行，Sprint 多选状态不遮挡刷新和筛选按钮 |
| 390px mobile | 筛选与 Sprint 入口可触控，横向看板滚动正常，文本不重叠 |

## 1440px 验收焦点

- 默认当前 Sprint 和未纳入 Sprint 在 Sprint 多选中选中。
- 多当前 Sprint 多选状态不挤压指标区和看板列头。
- 当前迭代空态位于看板有效区域，不生成额外灰色空白。
- sticky 表头、横向滚动和卡片密度保持父需求基线。
- 深浅主题下 Sprint 多选、按钮、边框和文本对比清晰。

## Mock/API 边界

本原型为结构与状态说明，不代表真实 API 已接入。实现阶段若复用既有需求中心聚合接口，应在 Change 中记录接口字段来源；若新增字段，应同步 API 文档、OpenAPI/客户端类型和请求日志验收。

## PNG

本阶段不要求导出 PNG。`prototype.html` 作为结构原型和 UI Skeleton 输入；1440px 与关键交互截图在 `/req-opsx`、`/opsx-apply` 阶段产出。
