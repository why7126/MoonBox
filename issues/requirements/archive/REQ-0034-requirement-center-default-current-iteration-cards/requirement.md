---
requirement_id: REQ-0034-requirement-center-default-current-iteration-cards
title: 需求中心默认只显示当前迭代卡片
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0012-frontend-requirement-center
created_at: 2026-09-14 10:22:15
updated_at: 2026-09-17 08:27:21
priority: P1
---

# 需求中心默认只显示当前迭代卡片

## 背景

需求中心当前承载 REQ、BUG、Sprint 与 OpenSpec Change 的研发治理看板能力，卡片范围可能同时覆盖采集池、规划中、已评审、历史归档和非当前迭代对象。随着 Sprint 工作流成为团队日常入口，用户进入页面时更需要优先聚焦“当前正在推进的迭代范围”和尚未纳入 Sprint 的待规划对象，而不是被历史卡片或归档对象分散注意力。

用户本次反馈“默认只显示当前迭代卡片”，属于需求中心默认展示策略增强。该能力应调整首屏默认范围，同时保留查看非当前迭代卡片的显式入口，避免把历史追溯能力从需求中心移除。

## 目标用户

- 产品负责人：进入需求中心后需要优先查看当前 Sprint 范围内的需求、缺陷和变更。
- 项目负责人：需要快速识别当前迭代范围、阶段分布和阻塞对象，减少历史项干扰。
- 开发与测试协作者：需要从看板默认视图理解当前应该推进的卡片集合。

## 范围

### 包含

- 需求中心首次进入页面时，默认展示当前迭代相关卡片和未纳入 Sprint 的待规划卡片。
- 当前迭代卡片范围应覆盖已纳入当前 Sprint 的 REQ、BUG，以及与当前 Sprint 相关的独立 Change 卡片；未纳入 Sprint 的 REQ、BUG 和独立 Change 作为默认待规划范围一并展示。
- 当前迭代的判断应使用 Sprint 生命周期事实源，而不是仅依赖前端缓存、卡片标题、目录名或人工文案。
- 当存在一个当前迭代时，默认视图直接展示该迭代范围和未纳入 Sprint 范围。
- 当存在多个当前迭代或多个可视为当前的 Sprint 时，默认展示全部当前迭代范围和未纳入 Sprint 范围，并在筛选状态中明确多选范围，避免静默选中任意一个。
- 用户应能通过既有 Sprint 多选查看全部卡片、历史迭代、取消未纳入 Sprint 范围和归档卡片。
- 重置筛选或回到默认视图时，应恢复为当前 Sprint + 未纳入 Sprint 范围，而不是全量范围。
- 手动刷新、空间切换、项目切换和稳定快照更新后，应保持“默认当前迭代”语义一致。
- 覆盖无当前迭代、仅有历史迭代、多个当前迭代、当前迭代无卡片、接口失败或权限不足等状态。

### 不包含

- 不在本需求内新增 Sprint 创建、启动、归档、评审或容量规划流程。
- 不在本需求内改变 Sprint 生命周期、REQ/BUG 状态机或 OpenSpec Change 状态映射。
- 不在本需求内删除历史卡片、归档卡片或未纳入迭代卡片的查看能力。
- 不在本需求内新增移动端、微信小程序、桌面端或管理后台页面。
- 不在本需求内重做需求中心整体信息架构、九阶段看板或卡片组件视觉体系。

## 功能要求

### FR-001 默认当前迭代范围

用户首次进入需求中心或主动恢复默认视图时，卡片列表应默认展示当前迭代相关对象和未纳入 Sprint 的待规划对象。默认范围应作用于 REQ、BUG 和独立 Change，不应只过滤某一类对象。

默认范围的筛选状态应可被用户感知，在既有 Sprint 多选中体现当前 Sprint 和“未纳入 Sprint”的选中状态。系统不得让用户误以为当前只存在这些卡片。

### FR-002 当前迭代识别

系统应从 Sprint 生命周期事实源识别当前迭代。优先候选包括 `iterations/change/` 中处于 planning 或 in_progress 的有效 Sprint；若后续存在明确的当前 Sprint 标记或配置，应在实现设计中定义优先级并通过测试固定口径。

已进入 `iterations/archive/` 的 Sprint 默认不属于当前迭代。仅存在历史归档 Sprint 时，默认视图应保留未纳入 Sprint 范围；若仍无卡片，则展示空态，并提供通过清空 Sprint 或选择历史 Sprint 查看其他范围的入口。

### FR-003 多当前迭代处理

当存在多个当前迭代候选时，默认视图应展示全部当前迭代相关卡片和未纳入 Sprint 卡片，并在 Sprint 多选状态中表达多个选中项。系统不得无证据地只选择编号最大、更新时间最新或任意一个 Sprint。

若多个当前迭代导致卡片范围较大，用户仍应能进一步选择单个 Sprint。单个 Sprint 筛选属于用户显式操作，不改变后续默认视图的恢复规则。

### FR-004 非当前范围查看

需求中心应保留查看非当前迭代卡片的能力。默认视图选中当前 Sprint 和“未纳入 Sprint”；用户可以通过清空 Sprint 多选查看全部对象，通过取消“未纳入 Sprint”收窄到当前 Sprint，通过选择历史或归档 Sprint 查看对应范围；不得新增独立的 `当前迭代｜全部｜历史｜未纳入迭代｜归档` 范围筛选模块。

Sprint 选择切换不应破坏既有搜索、对象类型、负责人、优先级、归档可见性和文档阅读能力。用户查看非当前范围后，手动点击重置或返回默认视图时恢复当前 Sprint + 未纳入 Sprint 默认选中状态。

### FR-005 空态、异常态与失败恢复

当没有当前迭代或当前迭代没有卡片时，页面应默认保留未纳入 Sprint 对象；若默认范围仍无卡片，则展示稳定空态，并允许用户通过清空 Sprint 多选或选择历史 Sprint 查看非当前对象。

当 Sprint 事实源解析失败、权限不足或接口失败时，页面应保留最近一次可用数据或展示轻量错误态，不得静默退回全量卡片并伪装为当前迭代结果。错误提示不得暴露本机绝对路径、内部堆栈、未脱敏治理文档全文、密钥、token 或 `.env` 内容。

### FR-006 刷新与一致性

默认当前 Sprint + 未纳入 Sprint 选择应跟随需求中心首次加载、手动刷新、空间切换、项目切换和后端聚合结果刷新。迟到响应不得覆盖用户已经切换的项目或 Sprint 选择。

用户已经显式选择非默认 Sprint 集合时，普通刷新应保留用户选择；只有重置筛选、重新进入默认视图或项目/空间上下文发生必要重置时，才回到当前 Sprint + 未纳入 Sprint 默认选中状态。

### FR-007 测试与文档

实现阶段应覆盖当前迭代识别、多个当前迭代、当前 Sprint + 未纳入 Sprint 多选默认选中、无当前迭代、历史 Sprint 查看、重置恢复默认、筛选组合、权限差异、接口失败和刷新一致性的测试。

如后端聚合接口、响应字段、OpenAPI、客户端类型或前端请求封装发生变化，应同步 API 文档、客户端生成物和相关治理说明；如仅在前端复用既有字段完成默认筛选，也应在 Change 文档中说明无接口契约变化。

## UI 约束

- 当前迭代状态应通过既有 Sprint 多选、筛选器、工具栏和卡片区视觉表达，不新增割裂的说明卡片或筛选模块下方提示模块。
- 当前 Sprint 和未纳入 Sprint 选中状态应清晰但克制，避免遮挡卡片标题、阶段动作或文档入口。
- 多当前迭代、无当前迭代和解析失败状态应有稳定文案和布局，不引起看板列宽、高度或吸顶表头抖动。
- 深浅主题、窄屏、长 Sprint ID、长卡片标题和空态下，文本不得与筛选栏、指标卡或看板列头重叠。
- 查看全部或历史范围的入口应是 Sprint 多选中的显式操作，不能依赖隐藏快捷键或仅通过浏览器地址参数完成。

## 关联需求

- REQ-0012-frontend-requirement-center：本需求承接需求中心九阶段看板、卡片、筛选和刷新框架。
- REQ-0013-requirement-center-real-data-integration：本需求依赖真实数据聚合与稳定快照，避免使用 Mock 或局部前端推导。
- REQ-0026-requirement-center-standalone-change-cards：本需求的默认范围应覆盖独立 Change 卡片，并保持独立 Change 与关联 Issue 的去重规则。
- REQ-0030-requirement-center-sprint-completion-metrics：本需求与 Sprint 数量指标共享 Sprint 生命周期事实源口径，但一个关注默认卡片范围，一个关注顶部统计展示。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: 默认当前 Sprint + 未纳入 Sprint 范围会影响需求中心页面加载、筛选切换、重置筛选、手动刷新和空间/项目切换等行为；若后端聚合接口参与当前迭代识别，需要请求日志记录安全摘要。该需求不新增长耗时、多步骤或异步任务，因此 task_traces 与 task_trace_spans 暂不适用。
  validation: 实现阶段需验证当前 Sprint + 未纳入 Sprint 默认范围、Sprint 切换和刷新请求的行为事件只记录脱敏筛选上下文；请求日志不得保存治理文档全文、本机路径、完整请求/响应体、密钥或 token；若接口契约无变化，应在 Change 中记录 N/A 原因。
```

## 状态块

```yaml
status: done
generated_at: 2026-09-14 10:22:15
completed_at: 2026-09-14 14:56:26
reviewed_at: 2026-09-14 15:06:22
approved_at: 2026-09-14 15:06:22
source_material:
  - capture.md
  - rules/requirement-management.md
  - docs/standards/product-data-collection-observability.md
  - REQ-0012-frontend-requirement-center/requirement.md
  - REQ-0026-requirement-center-standalone-change-cards/requirement.md
  - REQ-0030-requirement-center-sprint-completion-metrics/requirement.md
next: /req-opsx REQ-0034-requirement-center-default-current-iteration-cards
iteration: sprint-006
openspec_change: null
```
