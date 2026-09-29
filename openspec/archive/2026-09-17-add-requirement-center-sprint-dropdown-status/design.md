## 背景与现状

REQ-0032 已通过评审并纳入 sprint-006，目标是让需求中心 Sprint 筛选下拉展示 Sprint 状态。当前需求中心已有 `Sprint 筛选`、卡片 `sprintId` 标签、加入迭代弹窗中的 Sprint 状态/容量模型，以及 `web-catalog-requirement-center` 正式规格中的筛选与搜索能力。

本 Change 只建立设计与实现任务，不直接修改 `src/`。后续 `/opsx-apply` 需要先核实现有后端响应是否已包含可用状态字段，再决定是复用字段还是扩展 API。

## 目标与非目标

**目标：**

- Sprint 筛选选项展示 Sprint ID/名称和状态。
- 状态来自可追溯事实源，未知或冲突时稳定降级。
- 保持现有筛选、刷新、项目切换、统计和权限行为。
- 对齐加入迭代弹窗已有 Sprint 状态口径，避免两个入口状态不一致。
- 覆盖 UI Contract、Skeleton、观测、OpenAPI/Orval 条件和测试验收。

**非目标：**

- 不新增 Sprint 创建、编辑、启动、完成或归档能力。
- 不实现按状态分组、多选 Sprint、高级搜索或当前迭代置顶。
- 不自动修复 Sprint 状态漂移。
- 不新增 DB、对象存储、部署拓扑或 Agent Workflow 执行链路。

## 设计决策

### D1. Change 分类

类型：`update`。本 Change 修改已有 `web-catalog-requirement-center` 能力的筛选展示契约，不创建新能力，也不是针对已实现缺陷的 fix。

### D2. Sprint 状态事实源

优先复用需求中心稳定快照中的结构化 Sprint 状态；若当前 API 只有字符串列表，则由后端聚合 `iterations/change|archive/<sprint-id>/sprint.yaml` 的状态和阶段目录派生结构化字段。前端只负责展示和异常降级，不根据 ID、排序或当前选中项推断状态。

状态映射：

| 事实 | 展示 |
|---|---|
| `planning` | 规划中 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `archive` 目录事实 | 已归档 |
| 缺失、非法、冲突 | 状态待核实 |

### D3. UI Contract

事实源优先级：

1. REQ prototype `prototype/web/prototype.html`
2. REQ prototype `prototype/web/context.md`
3. REQ acceptance AC
4. `rules/ui-design.md`
5. 现有 `RequirementCenterPage` 与 `web-catalog-requirement-center` spec

页面入口：`/requirements` 需求中心工具栏 Sprint 筛选。

组件与 selector 候选：

| 区域 | 目标 selector / 入口 | 验收关注 |
|---|---|---|
| 筛选工具栏 | `.rc-toolbar` | 与类型、负责人、优先级筛选对齐 |
| Sprint 筛选字段 | `aria-label="Sprint 筛选"` 或后续 combobox 根节点 | 展示选中 Sprint 状态，保持可达 |
| Sprint 选项 | 选项行 / listbox option | ID/名称与状态同屏可读 |
| 状态标签 | `.rc-sprint-status-pill` 或新增等价类 | 字号、颜色、边框、深浅主题 |
| 卡片区 | 现有阶段列和卡片 selector | 筛选结果和统计不回退 |

视觉 token：沿用 MoonBox Ops 低噪音、近直角、细边框、Inter/Noto Sans SC、JetBrains Mono ID。状态色只作辅助，不作为唯一识别方式。

交互状态：default、open、hover、focus、selected、disabled、loading、error、empty、unknown、long-text、mobile。

权限规则：复用需求中心现有项目绑定和读取授权；无权 Sprint 不进入选项，异常详情不得泄漏内部路径、日志或无权对象。

Mock/API 边界：REQ 原型是静态 Mock，仅表达布局和状态矩阵；生产实现必须使用真实 API 或后端派生字段。若临时使用 Mock，不能进入完成态。

Computed style 验收点：`font-family`、`font-size`、`line-height`、`width`、`padding`、`gap`、`border`、`background-color`、`color`、`overflow`、`z-index`、focus ring。

### D4. UI Skeleton

Skeleton 先行任务必须产出：

```text
RequirementCenterPage
  -> toolbar filters
      -> Sprint filter trigger/select
          -> selected Sprint id/name
          -> selected Sprint status
          -> option list
              -> 全部 Sprint without status
              -> concrete Sprint with status
              -> unknown status fallback
  -> filtered board/cards
```

Skeleton 验收：

- 1440px 下筛选行、下拉打开态和卡片区无重叠。
- 390px 下筛选字段纵向或受控换行。
- 长 Sprint ID/名称受控换行或省略。
- loading/error/empty 状态不闪现旧项目数据。

### D5. 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: Sprint 筛选下拉展示和选择会影响前端行为事件、需求中心上下文请求和异常降级排障；如果扩展 API 字段，还需要请求日志和 OpenAPI/客户端类型验证。
  validation: 实现阶段验证 Sprint 下拉打开、选择、项目切换、状态缺失和授权失败的行为事件安全摘要、request_id、错误脱敏和客户端类型一致性；不得记录完整响应体、本机路径、密钥或无权对象内容。
```

本 Change 不预期新增 DB 表、索引、迁移、对象存储、Task Trace、Task Trace Span 或部署配置。若实现中引入批量状态修复、异步同步或后台任务，需重新评估 Task Trace。

## 风险与取舍

| 风险 | 处置 |
|---|---|
| 现有 `sprintOptions` 可能只有字符串 | 先核实 API；若缺字段，扩展后端 schema、OpenAPI 和前端类型。 |
| 原生 `<select>` 难以展示复杂标签 | 优先评估产品需要；若切换 combobox，必须保留键盘可达和 click outside 行为。 |
| Sprint 状态来源冲突 | 降级为“状态待核实”，不隐藏选项、不伪造正常状态。 |
| 与加入迭代弹窗状态口径分裂 | 抽取或复用同一映射函数/类型，测试覆盖两个入口。 |

## 迁移与回滚计划

1. 核实现有需求中心上下文和 Sprint 列表字段。
2. 如需扩展 API，先更新后端 schema/service、OpenAPI 和 Orval 生成类型。
3. 实现前端 Sprint 筛选状态展示和状态映射。
4. 补齐测试、视觉证据、computed style 和文档同步。

Rollback：保留原 Sprint 字符串筛选行为；若状态字段不可用，前端降级为不显示具体状态或显示“状态待核实”，不得影响筛选选择。

## 冲突处理

| 输入 | 结论 |
|---|---|
| REQ 原型要求状态标签/文本 | 作为目标视觉方向，生产实现可用原生 select 文案增强或 combobox，但必须满足状态可读。 |
| 现有工具栏使用原生 select | 可保留原生 select 并在 option 文案中拼接状态；若产品体验不足，再切换受控 combobox。 |
| 加入迭代弹窗已有状态/容量模型 | 不回退；状态映射需统一。 |
| Sprint-005 复盘“事实源优先” | 状态必须由后端或稳定快照提供，前端不凭位置推断。 |
| 验收反馈要求删除“已完成 / 归档”筛选 | 该 checkbox 与 Sprint 状态展示无关，且与需求中心范围/归档语义重复；返修中从筛选面板删除，不作为本 Change 的归档能力。 |
