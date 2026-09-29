---
requirement_id: REQ-0037-current-iteration-archive-entry
title: 当前迭代容量区域新增归档当前迭代入口
prototype_type: web
status: draft
created_at: 2026-09-14 23:35:53
updated_at: 2026-09-14 23:35:53
---

# Prototype Context

## 页面清单

| 页面 | 路由/入口 | 目标 |
|---|---|---|
| 需求中心当前迭代视图 | 前台需求中心，当前迭代默认范围 | 在当前迭代容量区域展示归档入口 |
| 归档确认弹窗 | 点击“归档当前迭代”后打开 | 展示目标 Sprint、门禁检查和执行确认 |
| 门禁失败状态 | 确认弹窗内 | 展示未归档 Change、验收 sign-off、权限或 Workflow Sync 失败项 |
| 无权限/不可用状态 | 容量区域或入口 tooltip | 阻止执行，同时说明安全摘要 |

## 关键区域

1. 当前迭代容量行：Sprint ID、容量比例、容量状态、已使用/总容量。
2. 归档入口：靠近容量条或当前迭代操作区，绑定目标 Sprint。
3. 确认弹窗：目标 Sprint 摘要、门禁检查列表、取消按钮、主操作按钮。
4. 门禁结果列表：状态图标、失败原因、修复入口或查看入口。
5. 反馈层：成功 toast、失败 toast、同步失败提示。

## 组件层级

```text
RequirementCenterPage
  CurrentIterationSummary
    CapacityItem
      CapacityBar
      CapacityMeta
      ArchiveSprintAction
  ArchiveSprintConfirmDialog
    SprintSummary
    ArchiveGateChecklist
    DialogFooter
      CancelButton
      ConfirmArchiveButton
  Toast / InlineStatus
```

## 状态矩阵

| 状态 | 容量区域 | 归档入口 | 确认流程 | 说明 |
|---|---|---|---|---|
| no-current-sprint | 空态或无当前迭代提示 | 不展示 | N/A | 不提供执行路径 |
| zero-capacity-used | `0 / total` | 隐藏或禁用 | N/A | 不可执行，需说明原因 |
| capacity-ready | `used > 0` | 可见 | 可打开 | 进入门禁检查 |
| multiple-current-sprints | 多个容量项 | 每项绑定 Sprint | 每次只确认一个 Sprint | 禁止默认归档任意 Sprint |
| permission-denied | 可展示安全摘要 | 禁用或隐藏 | 不可执行 | 后端权限为准 |
| gates-loading | 容量保持 | loading | 展示检查中 | 不清空页面 |
| gates-failed | 容量保持 | 可重试或查看 | 展示失败项 | 无强制归档 |
| gates-passed | 容量保持 | 可确认 | 主按钮可用 | 二次确认后执行 |
| archive-success | 刷新后移出当前迭代 | N/A | 关闭 | toast + 刷新 |
| archive-failed | 保留当前上下文 | 可重试 | 展示失败 | 不伪装成功 |

## 交互触发

- 点击归档入口：打开确认弹窗并触发门禁检查。
- 点击取消：关闭弹窗，不改变任何事实源。
- 点击主操作：仅在门禁通过且有权限时执行归档。
- 点击失败项修复入口：跳转到 Change、验收报告、Sprint 文档或同步入口。
- 点击外部区域：若设计声明支持关闭，必须覆盖内部 `stopPropagation` 不误关闭、外部点击仍关闭。
- 切换项目或刷新：重置目标 Sprint，避免迟到响应覆盖当前上下文。

## 数据依赖

| 数据 | 来源 | 用途 |
|---|---|---|
| 当前迭代列表 | 需求中心聚合事实源 | 判断入口所属 Sprint |
| `used_capacity` / total | Sprint 容量事实源 | 判断入口展示与容量摘要 |
| 当前用户权限 | 后端权限事实源 | 判断入口可执行性 |
| 门禁检查结果 | Sprint archive 既有门禁 | 确认流程状态 |
| Workflow Sync 结果 | Workflow Sync 脚本/服务投影 | 刷新 Sprint、Scope 和 Issue 状态 |

## 响应式断点

| 视口 | 要求 |
|---|---|
| 1440px 桌面 | 容量、入口和确认弹窗布局完整；门禁列表可扫描；无文本重叠 |
| 1024px 窄桌面 | 容量项可换行；入口仍绑定目标 Sprint；弹窗宽度不溢出 |
| 390px 移动宽度 | 入口可进入更多操作或换行；弹窗纵向滚动；主/取消按钮不重叠 |

## 1440px 验收焦点

- 容量条、Sprint ID、容量数值和归档入口对齐。
- 多当前迭代时每个入口能明确识别目标 Sprint。
- 确认弹窗居中且宽度、内边距、行高符合 Ops 视觉系统。
- 门禁失败列表能快速扫描，不被按钮 footer 遮挡。
- toast 或 inline status 不引起容量区域 layout shift。

## PNG/截图状态

当前阶段仅提供 HTML 结构原型，PNG 暂不要求。后续 `/opsx-apply` 必须基于实现结果补齐 1440px 和关键交互截图或等价视觉证据。
