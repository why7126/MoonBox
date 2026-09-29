## 背景

REQ-0037 已纳入 `sprint-007`，父需求 REQ-0031 已在需求中心提供当前迭代容量条。当前缺口是：用户能看到 Sprint 容量压力，却不能从同一上下文进入收尾动作；同时前端新增入口不得绕过 Sprint archive 既有门禁。

现有事实源和约束：

- 当前迭代容量来自 Sprint scope 与 `scope_estimates[]`，不是前端卡片数量。
- Sprint archive 已有未归档 Change、验收报告 sign-off、权限和 Workflow Sync 门禁。
- REQ-0037 存在 `prototype/web/`，本 Change 必须承接 UI Contract、UI Skeleton、1440px 视觉证据、computed style、Mock/API 边界和最终一致性回填。
- 产品数据采集与链路观测适用：`usage_events`、`request_logs`、`task_traces`，实现阶段需确认是否复用现有 `task_trace_spans`。

## 目标与非目标

**Goals:**

- 在需求中心当前迭代容量区域或操作区提供安全的归档入口。
- 基于 Sprint archive readiness 汇总决定入口隐藏、禁用或可进入确认流程。
- 确认流程展示目标 Sprint、容量摘要、门禁状态、失败项和修复方向。
- 归档执行复用既有 Sprint archive 门禁，前端不直接写归档状态。
- 归档成功、失败或 Workflow Sync 刷新失败后，需求中心状态与事实源保持一致或明确提示过期。
- 完成 UI Skeleton、动作按钮矩阵、computed style 与 1440px/390px 验收设计。

**Non-Goals:**

- 不新增独立 Sprint archive 状态机。
- 不自动归档未完成 REQ、BUG、独立 Change 或 OpenSpec Change。
- 不自动补签 `acceptance-report.md`。
- 不改变 Sprint 容量、默认容量、估算人天和容量门禁规则。
- 不新增管理后台、移动端、微信小程序或桌面端入口。

## 设计决策

### D1. Readiness 是入口启用事实源

入口初始可见性必须同时满足当前迭代存在、`used_capacity > 0`，且 readiness 汇总允许进入确认流程。若 readiness 显示范围内存在未归档闭环的 REQ、BUG 或独立 Change，入口可隐藏或展示禁用态，但不得进入可执行确认路径。

拒绝方案：仅按 `used_capacity > 0` 展示可执行入口。原因是用户补充文案明确要求 UI 口径并入 readiness，且不能让用户误以为容量区域可绕过未闭环范围。

### D2. 前端只负责入口和确认，不负责最终裁判

前端展示 readiness 汇总和确认流程；最终归档仍由 Sprint archive 后端/脚本门禁裁判。客户端传入的 Sprint ID、权限状态、readiness 状态和行为链路字段都不能作为服务端授权依据。

失败项需要提供修复方向：未归档范围跳到关联卡片或 Change，验收 sign-off 跳到验收报告，Workflow Sync 失败提示重试或查看事实源，权限失败只展示安全摘要。

### D3. API / 数据边界

优先复用需求中心上下文聚合或既有 Sprint archive readiness API，建议安全摘要字段包含：

```yaml
current_iteration_archive:
  - sprint_id: sprint-007
    can_enter_confirmation: false
    display_mode: hidden | disabled | enabled
    reason_code: unarchived_scope | missing_signoff | permission_denied | workflow_sync_failed | capacity_zero | unknown
    safe_summary: "仍有范围未归档闭环"
    blockers:
      - type: requirement | bug | change | acceptance_report | workflow_sync | permission
        id: REQ-0037-current-iteration-archive-entry
        status: in_sprint
        visible: true
        action_hint: "继续完成并归档"
```

实现可按既有类型命名微调，但必须保留 display mode、can enter、reason code、安全摘要、阻塞类型和目标 Sprint 绑定。无权限或不可见资源不得泄露内部路径、不可见 Sprint、完整文档正文、堆栈、密钥、`.env`、Authorization 或 Cookie。

### D4. UI Contract

事实源优先级：

```text
prototype/web/prototype.html
> prototype/web/context.md
> acceptance.md
> requirement.md
> docs/standards/prototype-ui-acceptance.md
> rules/ui-design.md
> 现有 RequirementCenterPage 实现
> openspec/specs
```

页面与入口：

- 页面：前台需求中心现有入口。
- 入口：`CurrentIterationSummary` / 当前迭代容量条相邻操作或当前迭代操作区。
- 弹窗：`ArchiveSprintConfirmDialog` 或等价 action modal。
- 登录态：仅已登录且有授权项目时显示可用信息。
- 权限态：无归档权限时隐藏或禁用入口，错误摘要不泄露不可见资源。

信息架构：

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

视觉 token：

- 沿用需求中心现有 Ops token、细边框、近直角、紧凑信息密度。
- 入口视觉权重低于容量核心数值和异常提示，高于普通辅助链接。
- 禁用态、失败态和高风险状态不能只依赖颜色表达。
- 文本在长 Sprint ID、窄屏、多当前迭代、失败态下不得重叠。

交互状态：

- `hidden`: 无当前迭代、容量为 0、无权限或策略选择隐藏。
- `disabled`: readiness 未通过，展示安全摘要和 tooltip。
- `loading`: 门禁检查中，不清空容量区域。
- `failed`: 展示失败项、修复方向和重试/查看入口，无强制归档。
- `passed`: 主按钮可用，执行前仍需二次确认。
- `success`: 刷新当前迭代、容量、Scope 和卡片状态。
- `sync_failed`: 不伪装成功，提示状态可能过期。

Mock/API 边界：

- 原型和测试 fixture 可模拟 `sprint-007`、未归档 Change、sign-off 缺失、权限通过、Workflow Sync 通过/失败。
- 生产运行时必须来自真实需求中心上下文或 Sprint archive readiness API。
- Mock readiness 不得进入生产执行路径。

权限规则：

- 入口展示可以被权限过滤；归档执行必须服务端重新校验。
- 无权限用户只看到安全摘要或不看到入口，不返回不可见 Sprint、Change、验收报告或内部路径。

### D5. UI Skeleton

实现细节前必须完成 Skeleton，并留存 1440px 首轮证据：

- 稳定选择器：`data-testid="current-iteration-archive-action"`、`data-testid="archive-sprint-confirm-dialog"`、`data-testid="archive-gate-checklist"`。
- 状态容器：hidden、disabled、loading、failed、passed、success、sync_failed、permission_denied。
- 页面结构：容量条、入口、确认弹窗、门禁结果列表、footer 操作和 toast/inline status。
- 响应式：1440px、1024px、390px。
- 关键交互：点击入口、取消、主操作、失败项跳转、外部点击关闭和弹窗内 `stopPropagation` 不误关闭。

### D6. 动作按钮矩阵

| 动作按钮 | modal 类型 | 目标 selector | 状态 | 组件族 | 验收证据 |
|---|---|---|---|---|---|
| 归档当前迭代 | `confirm` / `action-modal` | `[data-testid="current-iteration-archive-action"]`、`[data-testid="archive-sprint-confirm-dialog"]` | hidden、disabled、loading、open、failed、passed、permission_denied | IconButton、Dialog、Toast、InlineStatus | 1440px/390px 截图、Playwright 状态断言、computed style；CapacityItem 桌面按左侧 sprint id + 状态 badge、中间容量数值 + 进度条、右侧无边框归档 icon button 呈现；readiness 长摘要进入 hover/title |
| 取消 | dialog footer | `[data-testid="archive-sprint-cancel"]` | default、hover、focus | Button、Dialog | 确认无事实源变更 |
| 门禁通过后归档 | dialog footer | `[data-testid="archive-sprint-confirm"]` | disabled、loading、enabled、error | Button、Dialog、Toast | 权限、readiness 和后端门禁断言 |
| 查看失败项 | inline action | `[data-testid="archive-gate-blocker-link"]` | visible、permission-hidden | Link/Button | 不泄露不可见资源，跳转或提示正确 |

### D7. Computed Style 采样清单

| selector | 视口 | 关键属性 | 期望 |
|---|---|---|---|
| `[data-testid="capacity-metric-item"]` / `[data-testid="current-iteration-capacity-status"]` / `[data-testid="current-iteration-archive-action"]` | 1440 / 390 | grid-template-columns、width、height、padding、border、background、aria-label、title | 桌面三列：左侧 sprint id + 状态 badge，badge hover/title 显示容量来源和说明；中间容量数值 + 进度条；右侧 34px 无边框 icon-only 归档按钮。390px 安全堆叠，readiness 长摘要只通过归档按钮 hover/title 暴露 |
| `.rc-column-body` / `.rc-column-body.empty::before` | 1440 | padding-top、inset-top、row-gap、gap | 看板列头与首张卡片或空列虚线框保持紧凑连续；列体顶部 padding 10px，空列虚线框 top inset 10px，避免列头下方出现大面积空带 |
| `[data-testid="archive-sprint-confirm-dialog"]` | 1440 / 390 | width、max-height、padding、z-index、overflow | 桌面居中、移动端可滚动、footer 不遮挡列表 |
| `[data-testid="archive-gate-checklist"]` | 1440 / 390 | display、gap、line-height、color、overflow | 失败项可扫描，长文案换行不重叠 |
| `[data-testid="archive-sprint-confirm"]` | 1440 / 390 | disabled 样式、focus ring、loading state | 禁用态不只靠颜色，可读且不可点击 |

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 当前迭代归档入口是 Web 端触发的高风险多步骤写操作，涉及按钮点击、确认取消、权限拒绝、readiness 门禁、归档执行请求、Sprint archive 节点和 Workflow Sync 结果刷新。
  validation: 实现阶段需验证入口点击、确认取消、权限拒绝、门禁失败、归档成功和 Workflow Sync 失败具备脱敏行为事件或等价摘要；归档执行请求具备服务端 request_id 与请求日志；若复用既有 Sprint archive Task Trace，需证明校验、归档、同步和失败节点可定位；不得记录完整文档正文、本机路径、Authorization、Cookie、密钥、真实 .env、完整请求体或未脱敏错误堆栈。
```

API / OpenAPI / Orval：如果新增 readiness 字段或归档执行接口，必须同步 OpenAPI 来源、前端生成类型、`docs/03-api-index.md` 和接口测试；若完全复用既有 API，需要在 trace 和验收中记录复用边界与不新增字段的原因。

DB：当前设计不要求新增表、字段、索引或迁移；如果实现发现需要持久化 readiness 或 sign-off 状态，必须补充 SQLite / MySQL schema、`docs/04-database-design.md` 和数据库测试后再关闭任务。

## 冲突处理

- `prototype.html` 与现有页面布局冲突时，保留现有需求中心 Shell 和容量条风格，仅新增相邻入口和弹窗。
- `used_capacity > 0` 与 readiness 冲突时，`used_capacity > 0` 只代表入口候选，readiness 决定是否隐藏、禁用或进入确认流程。
- 前端 readiness 与后端 Sprint archive 结果冲突时，以后端/治理命令最终门禁为准，并刷新或提示状态过期。
- 多当前迭代时，不默认选择编号最大、更新时间最新或容量最高的 Sprint；每个入口与确认流程必须绑定目标 Sprint。

## 风险与权衡

- Readiness 摘要过细可能泄露不可见资源 → 对无权限资源返回安全摘要、类型和数量，不返回不可见 ID 或路径。
- 前端误把 readiness 当最终裁判 → 服务端执行前重新校验，测试覆盖篡改 Sprint ID 和状态。
- 归档成功后刷新失败导致页面过期 → 保留失败提示，不移除当前迭代，提供刷新或查看事实源入口。
- 弹窗信息过重影响扫描 → 门禁项列表化，详情通过跳转或展开，不堆长段落。
- 现有 Sprint archive 缺少 API 化 readiness → 可先复用治理脚本/服务投影，但必须保留后端最终门禁。

## 迁移计划

1. 完成 UI Skeleton、readiness 字段契约和确认流程骨架。
2. 接入需求中心上下文或 Sprint archive readiness，输出安全摘要。
3. 复用 Sprint archive 执行路径并补齐权限、请求日志和 Task Trace 覆盖。
4. 覆盖入口展示/隐藏/禁用、确认取消、门禁失败、权限拒绝、成功刷新、Workflow Sync 失败、多当前迭代和响应式视觉验收。
5. 回填 Change trace、REQ acceptance、OpenAPI/API 文档和最终一致性证据。

回滚方式：隐藏或禁用归档入口，保留现有当前迭代容量展示；后端 readiness 字段若已发布，应兼容保留或标记不消费，不影响旧客户端。
