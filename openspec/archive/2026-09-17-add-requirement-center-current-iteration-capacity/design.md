## 背景

REQ-0031 已通过评审并纳入 sprint-006，目标是在前台需求中心展示当前迭代容量，支持 2 个当前迭代并存。现有需求中心能力包括真实上下文聚合、9 阶段映射、筛选搜索、手动刷新、权限过滤、错误脱敏和当前 Sprint 标签展示；Sprint 容量治理已有 `capacity_person_days`、`scope_estimates[]`、`estimated_person_days` 和容量门禁。

本 Change 不改变 Sprint 容量事实源，只把当前迭代容量以安全摘要形式纳入需求中心上下文，并在 Web 统计区域展示。

## 目标与非目标

**目标：**

- 在需求中心上下文中返回当前迭代容量摘要。
- 支持 1 个或 2 个当前迭代容量项同时展示。
- 使用 Sprint 机器事实源计算 `used_capacity / total_capacity`。
- 覆盖默认容量、显式容量、接近上限、超量、待核实、刷新失败和无权限状态。
- 同步 API、OpenAPI/客户端类型、请求日志、行为事件和测试验收。
- 按 prototype gate 完成 UI Contract、UI Skeleton、1440px 视觉验收和最终一致性回填。

**非目标：**

- 不新增 Sprint 容量编辑入口。
- 不修改 `scripts/add-sprint-scope-item.py --capacity-person-days` 的事实源职责。
- 不引入自动排期、资源预测或容量分配算法。
- 不因容量超量自动阻止用户浏览、筛选或打开文档。
- 不新增 DB 表、对象存储、部署拓扑或后台异步任务。

## 设计决策

### D1. 容量事实源

使用 Sprint 四件套中的 `sprint.yaml` 作为容量事实源：

- `used_capacity` 来源于 `scope_estimates[].estimated_person_days` 合计。
- `total_capacity` 来源于 `capacity_person_days`。
- `capacity_source` 根据是否存在有效显式容量或默认容量写入 `explicit | default | unknown`。
- `capacity_status` 使用 `normal | near_limit | over_limit | unknown`。

理由：Sprint 容量治理已经使用这些字段驱动门禁和 Workflow Sync，需求中心不得用卡片数量、前端筛选结果或旧快照推断容量。

备选方案：前端按卡片数量估算容量。拒绝原因是无法反映 M/L/XL 等估算差异，也会与 Sprint 事实源断裂。

### D2. 当前迭代识别

首版复用需求中心已有当前迭代或 Sprint 筛选上下文识别逻辑，并以后端稳定快照输出为准。返回容量项时保持分项列表，不把 2 个当前迭代静默合并。

超过 2 个当前迭代时作为异常或待核实状态处理，不任意截断为前两个；可返回折叠列表或诊断提示。

### D3. API 字段边界

建议上下文 payload 新增安全摘要字段：

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

字段名可在实现中按既有前端类型风格微调，但语义必须覆盖 Sprint ID、已使用、总容量、单位、来源、状态和提示。响应不得包含本机路径、内部目录、Markdown 全文、Authorization、Cookie、`.env` 内容或原始堆栈。

### D4. UI 合同

事实源优先级：

```text
prototype/web/prototype.html
> prototype/web/context.md
> acceptance.md
> requirement.md
> rules/ui-design.md
> 现有 RequirementCenterPage 实现
> openspec/specs
```

页面与入口：

- 页面：前台需求中心 `/requirements` 或现有需求中心入口。
- 入口：首屏统计/筛选区域附近新增当前迭代容量区域。
- 登录态：仅已登录且有授权项目/空间时展示。
- 权限态：无权 Sprint 不显示数值或名称。

信息架构：

- `RequirementCenterPage`
- `RequirementCenterHeader`
- `RequirementCenterToolbar`
- `CurrentIterationCapacityStrip`
- `CapacityMetricItem`
- `CapacityStatusHint`
- `RequirementCenterStats`
- `RequirementKanbanBoard`

视觉 token：

- 沿用 MoonBox Ops 深浅主题、近直角、细边框、高信息密度。
- 容量项使用紧凑指标，不进入每张卡片。
- 状态色应与现有状态 token 协调，不引入蓝紫渐变、发光或大圆角装饰。
- 验收返修后容量条采用附件 HTML `.capacity` 模块的局部一致模式：紧凑横向容器、左侧 Sprint ID/来源标签、中间容量数值和细进度轨、右侧状态点；不展示额外可见标题“当前迭代容量”，仅保留 `aria-label` 语义。

交互状态：

- `normal`：常规展示。
- `near_limit`：轻量关注态。
- `over_limit`：风险提示，不阻断操作。
- `unknown`：待核实提示，保留 Sprint ID。
- `loading`：与上下文刷新状态一致。
- `refresh_failed`：保留上次成功数据并展示轻量失败提示。
- `mobile`：允许换行或折叠，但保留 Sprint ID 和容量比例。

Mock/API 边界：

- 原型和测试 fixture 可使用示例 `sprint-006 18/30`、`sprint-007 32/30`。
- 生产运行时必须来自真实需求中心上下文聚合接口。
- Mock 容量不得进入生产数据路径。

权限规则：

- 当前用户不可访问的项目或 Sprint 不得出现在容量项、搜索提示、统计或异常详情中。
- 只读用户可查看有权访问容量，但不得获得写入或编辑能力。

一致性参照：

- 需求中心既有统计区、筛选区、刷新按钮、错误态和 9 阶段看板。
- 管理后台/前台 Ops token、细线、近直角、字体层级和 toast 行为。

## UI 骨架

首轮 Skeleton 必须先于细节实现落地，覆盖：

- 页面壳：沿用现有需求中心 Shell，不调整侧边栏和看板基本结构。
- 容量区域：`data-testid="current-iteration-capacity"` 或等价稳定选择器。
- 容量项：`data-testid="capacity-metric-item"`，每项包含 Sprint ID、容量比例、状态和提示。
- 状态容器：normal、near_limit、over_limit、unknown、loading、refresh_failed、permission-hidden。
- 数据依赖：当前项目上下文、当前迭代列表、Sprint scope、capacity_person_days、scope_estimates。
- 1440px 验收：首屏可见、两个当前迭代同时可见、统计区不跳动、看板列头不被遮挡。
- 窄屏验收：390px 下保留 Sprint ID 与容量比例。

## UI Reference Replication Contract（验收返修）

| 组件 | 参考 selector / 文本锚点 | 目标 selector | 实现入口 | 状态 | 处置结论 |
|---|---|---|---|---|---|
| 当前迭代容量条 | `.capacity`、`.capacity-id`、`.capacity-track`、`.capacity-nums`、`.track-fill`、`.status-dot` | `[data-testid="current-iteration-capacity"]`、`.rc-current-capacity-items`、`.rc-capacity-item`、`.rc-capacity-bar`、`.rc-capacity-status` | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/styles/globals.css` | normal、over_limit、loading、refresh_failed、mobile | 局部一致；迁移紧凑横向条、5px 进度轨和状态点，不复刻页面其他模块。 |
| 可见标题 | 参考模块内部使用小标签承载来源，不需要外部标题 | `aria-label="当前迭代容量"` | `CurrentIterationCapacityStrip` | default、refresh_failed | 移除可见文案“当前迭代容量”，保留无障碍语义；刷新失败提示仍可见。 |

Computed style 采样清单：

| selector | 期望 | 证据 |
|---|---|---|
| `.rc-current-capacity-items` | `display:flex`、可换行、细边框、`var(--rc-panel)` 背景、`var(--ops-radius-md)` 圆角、紧凑 padding | `openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-modify-computed-style.json` |
| `.rc-capacity-bar` | 高度约 5px、圆角轨道、状态色 fill | `openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-modify-computed-style.json` |
| `.rc-capacity-status` | 右侧状态点 + 文案，不使用阻断式弹窗或遮罩 | `openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-modify-1440.png` |

## 冲突处理

- 若 `prototype.html` 与现有需求中心布局冲突，以不破坏现有需求中心 Shell、统计区和看板交互为先，容量区域采用局部一致扩展。
- 若 `context.md` 字段建议与后端已有类型命名冲突，可以调整字段名，但必须保留语义和验收项。
- 若 Sprint 默认容量和显式容量判断与 Sprint 容量治理脚本冲突，以 `sprint.yaml` 与 `sprint-capacity-default` spec 为准。
- 若当前迭代识别与 REQ-0030、REQ-0032、REQ-0034 出现口径差异，后续实现必须统一当前迭代定义，避免同一页面内多套判断。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: 当前迭代容量展示涉及需求中心 Web 展示、刷新/筛选行为，以及后端上下文聚合响应字段和请求日志摘要。
  validation: 实现阶段需验证行为事件采集失败不阻断主流程、容量聚合请求写入脱敏请求日志、错误摘要不含敏感内容、OpenAPI/客户端类型同步；普通查询不新增 Task Trace，若改为异步或批量计算则重新评估 task_traces 与 task_trace_spans。
```

## 风险与权衡

- 当前迭代定义与其他 Sprint 体验需求不一致 → 在实现前统一 REQ-0030、REQ-0032、REQ-0034 的当前迭代口径。
- 容量来源被误写为卡片数量 → 后端测试覆盖 `scope_estimates[]` 合计，前端只消费 API 字段。
- 超量提示过重干扰看板 → 使用非阻断状态提示，不弹出强制确认。
- 多 active Sprint 或超过 2 个当前迭代 → 显示待核实或折叠诊断，不任意选取前两个。
- 请求日志或行为事件泄露路径 → 只记录脱敏摘要和结果码，敏感字段测试覆盖。

## 迁移计划

1. 扩展后端上下文聚合字段与类型。
2. 同步 OpenAPI、客户端类型与 API 文档。
3. 增加前端 UI Skeleton 和状态组件。
4. 接入真实字段并覆盖状态组合。
5. 运行后端、前端、TypeScript、OpenSpec 与 1440px/390px 视觉验收。

无需数据库迁移、对象存储迁移或部署拓扑调整。回滚方式为隐藏容量区域并恢复上下文字段消费，保留后端字段兼容不影响旧客户端。

## 待确认问题

- `near_limit` 阈值使用 80%、90% 还是跟随 Sprint capacity gate 派生阈值，需要实现前统一。
- 当前迭代识别是否严格等于 active Sprint，还是与当前 Sprint 筛选默认值共享更细规则，需要与 REQ-0034 对齐。
