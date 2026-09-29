## 背景

REQ-0030 要求在需求中心指标卡新增 Sprint 已完成与累计数量。需求已生成、补齐、评审通过，并通过 `/sprint-propose` 纳入 `sprint-006`。本设计将该需求转换为可实现的 OpenSpec 方案，范围集中在需求中心 Web 页面和真实数据聚合接口。

## 需求就绪报告

| 项 | 结论 | 证据 |
|---|---|---|
| REQ 状态 | Ready | `status: in_sprint`，`iteration: sprint-006` |
| 文档完整性 | Ready | requirement、user-stories、business-flow、acceptance、trace、prototype/web 已存在 |
| 评审状态 | Approved | `review.md` 已创建，REQ 已迁移至 `issues/requirements/review/` |
| Sprint 状态 | In Sprint | `iterations/archive/sprint-006/sprint.yaml` 已包含 REQ-0030 |
| 原型门禁 | Pass for propose | 已有 context 与 prototype.html；实现阶段需补视觉证据 |
| Knowledge-base | N/A | 未命中后台横切标签；已参考 sprint-005 复盘 |

## 变更分类

```yaml
change_id: add-requirement-center-sprint-completion-metrics
source_requirement: REQ-0030-requirement-center-sprint-completion-metrics
change_type: add
capabilities:
  modified:
    - web-catalog-requirement-center
    - web-catalog-requirement-center-real-data
impact:
  backend: true
  web: true
  api: true
  database: false
  storage: false
  admin: false
  miniapp: false
```

## 冲突处理

优先级：`prototype.html` > `context.md` > `acceptance.md` > `requirement.md` > `rules/ui-design.md` > 既有 OpenSpec 规格。

| 冲突点 | 处置 |
|---|---|
| 既有需求中心统计与卡片范围遵循同一筛选条件 | Sprint 数量指标明确为项目级总览，是新增例外；看板卡片和既有局部统计仍可随筛选变化 |
| 原型 HTML 中的数字为静态展示 | 生产路径必须使用聚合接口或明确测试 fixture，不得沿用 Mock 数字 |
| 已完成 Sprint 可能存在 archive 与 `status: completed` 两类来源 | 以 Sprint ID 去重；归档 Sprint 计入已完成，未归档 completed 作为兼容状态计入但不得重复 |
| 错误原因可能来自本地治理文件解析 | 对外只暴露脱敏 warning/error code，不展示本机路径、系统用户名、堆栈或原始文档 |

## UI 契约

| 区域 | Contract |
|---|---|
| 页面入口 | 复用现有需求中心入口 `/catalog/requirements` 或当前项目实际路由 |
| 指标区容器 | 保持 `[data-testid="requirement-center-metrics"]`，新增卡片不得破坏既有指标布局 |
| 指标卡高度 | 指标卡采用更紧凑高度，减少顶部统计区纵向占位，但不得压缩主数字可读性 |
| 指标说明 | 所有指标名后提供统一信息图标与浮层 tooltip，说明统计口径 |
| 需求 / Bug / 独立 Change 指标 | 展示“已完成 / 总体”，继续跟随当前筛选条件变化 |
| Sprint 指标卡 | 新增 `[data-testid="sprint-completion-metric"]`，标题文案为 `Sprint`，展示已完成数、总体数，不再在卡片底部展示辅助说明 |
| 数字 selector | `[data-testid="sprint-completion-metric-completed"]`、`[data-testid="sprint-completion-metric-total"]` |
| 口径说明 | Sprint 项目级总览说明进入标题旁 tooltip，不随筛选变化 |
| 状态 | 支持 loading、empty、error、last-successful-value；错误态提供重试入口 |
| 主题 | 复用需求中心既有深浅主题 token、间距、边框和字体层级 |
| 响应式 | 1440px 与筛选区同屏清晰；1024px 可换行；390px 不溢出、不遮挡筛选控件 |

指标卡不得使用过长说明挤占主数字。若需要解释口径，优先使用 tooltip 或短辅助文案。
验收返修后，指标卡统一采用 tooltip 承载说明文案；Sprint 卡片删除底部辅助说明，避免额外撑高指标区。

## UI 骨架

实现阶段先交付可截图确认的骨架，再进入接口细节和视觉 polish。

```text
RequirementCenterPage
  RequirementCenterHeader
  RequirementCenterMetrics
    ExistingMetricCards
    SprintCompletionMetricCard
      MetricTitle
      CompletedCount
      DividerOrSlash
      TotalCount
      ScopeHint
      LoadingEmptyErrorState
  RequirementCenterFilters
  RequirementCenterBoard
    StageColumns
    Cards
```

骨架首轮验收聚焦：1440px 深浅主题、指标区高度稳定、筛选区不被挤压、看板列头对齐、数字与文案无溢出。确认后再接入真实数据、重试、筛选解耦和状态处理。

## 数据与 API 设计

需求中心上下文接口建议在现有响应中增加 `sprint_metrics`：

```yaml
sprint_metrics:
  completed_count: number
  total_count: number
  source: sprint_lifecycle
  warning: string | null
  refreshed_at: string | null
```

聚合口径：

- 扫描当前项目可见的 `iterations/archive/` 与 `iterations/change/` Sprint 元数据。
- `total_count` 统计所有有效 `sprint-xxx`，按 Sprint ID 去重。
- `completed_count` 默认统计 `iterations/archive/` 下有效 Sprint。
- 若 `iterations/change/` 中存在 `status: completed` 但尚未归档的兼容状态，可计入已完成，但必须按 Sprint ID 与 archive 去重。
- 解析失败或权限不足时返回脱敏 warning 或接口错误，不暴露内部路径和文档全文。

如后端响应 schema 变化，需要同步 OpenAPI 来源、`docs/03-api-index.md`、前端类型和客户端生成物。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
    - usage_events
  task_traces: N/A
  task_trace_spans: N/A
  reason: 本需求只扩展需求中心同步上下文请求和页面交互事件，不新增长耗时任务、异步任务或对象存储链路。
  validation:
    - request_logs 只记录接口、状态码、耗时和脱敏统计摘要
    - usage_events 只记录页面加载、手动刷新、空间切换等稳定事件
    - 不记录原始治理文档、本机绝对路径、内部堆栈、密钥、token 或 .env 内容
```

## 测试策略

- 后端：覆盖无 Sprint、仅 planning、仅 archive、archive + completed 未归档兼容、重复 ID 去重、解析失败脱敏。
- API：覆盖 `sprint_metrics` schema、OpenAPI 示例、错误响应和权限边界。
- 前端：覆盖渲染、loading、empty、error、手动刷新、空间切换、筛选不改变指标。
- 视觉：覆盖 1440px 深浅主题、1024px、390px 截图与文本溢出检查。
- 治理：运行 OpenSpec validate、中文优先校验、Sprint scope 校验、workflow sync。

## 风险

| 风险 | 缓解 |
|---|---|
| Sprint 生命周期文件口径与历史数据不一致 | 在聚合层集中去重并固定 completed 未归档兼容规则 |
| 用户误以为指标跟随当前筛选 | 卡片短文案标注项目级总览，并在测试中固定筛选不变行为 |
| 错误态泄漏本地路径或治理文档内容 | API 与前端均只展示脱敏 warning/error code |
| 新字段遗漏客户端类型同步 | tasks 中明确 OpenAPI、Orval/客户端类型和 API 文档同步门禁 |
