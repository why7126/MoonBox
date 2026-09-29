## 背景

REQ-0035 来源于用户对 Chat 工作台输入区的执行配置增强要求：聊天框需要新增 Agent 选择，当前只有 Codex；还需要新增模型和推理程序选择，体验参考 Codex 聊天框。该 REQ 已完成 `/req-complete`、`/req-review` 和 `/sprint-propose`，当前 `trace.md` 状态为 `in_sprint`，迭代为 `sprint-006`。

现有 `web-catalog-chat-workbench` 已覆盖 `/chat` 入口、个人会话、真实执行、对话与轨迹双视图、首次输入延迟创建、输入状态提示和原型验收契约。本 Change 不重做会话生命周期，而是在既有 Chat 工作台上扩展执行配置选择、服务端能力发现、发送链路追溯和观测边界。

## 需求就绪报告

| 项 | 结论 | 证据 |
|---|---|---|
| 状态门禁 | ready | `trace.md` 为 `status: in_sprint`，`iteration: sprint-006`。 |
| 文档包 | ready | `requirement.md`、`user-stories.md`、`business-flow.md`、`acceptance.md`、`trace.md`、`prototype/web/context.md`、`prototype/web/prototype.html` 已存在。 |
| Prototype Gate | pass | `prototype_refs`、`prototype_gate`、`AC-PROTOTYPE-*` 均已记录。 |
| Knowledge Gate | pass | 已引用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`。 |
| 观测声明 | pass | REQ 已声明 Web 请求封装、API、DB、usage_events、request_logs、task_traces、task_trace_spans 适用。 |

## 影响分析

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: true
  storage: false
  api: true
capabilities:
  new: []
  modified:
    - web-catalog-chat-workbench
    - codex-session-execution
change_type: add
```

## 目标与非目标

**Goals:**

- 在 Chat 输入区展示 Agent、模型和推理配置，当前 Agent 唯一值为 Codex。
- 由服务端返回可用 Agent、模型、推理配置、默认值、可用状态和禁用原因。
- 发送时提交请求配置，并由后端重验权限、可用性和会话状态。
- 轮次事实源记录请求配置、实际生效配置和降级原因摘要，历史轮次可追溯。
- 运行中、停止中、未知、归档、加载失败和窄屏状态下保持输入区语义清晰。
- 将配置选择和执行结果纳入脱敏行为事件、请求日志、Task Trace 和流程节点。

**Non-Goals:**

- 不新增 Codex 以外的真实 Agent 接入。
- 不新增后台 Agent/模型配置管理页面。
- 不新增用户自定义模型、外部模型供应商绑定或个人 API Key 管理。
- 不改变 Chat 工作台既有会话权限、空间权限、仓库授权、执行隔离、停止、重试和历史管理规则。
- 不允许通过模型或推理选项绕过 REQ/BUG 评审、Sprint 纳入、OpenSpec Change 或正式开发授权。

## 设计决策

### D1. UI Strategy: MoonBox Ops DS + Codex 聊天框局部交互参考

采用现有 MoonBox Ops 设计系统和 `web-catalog-chat-workbench` 输入区结构，参考 Codex 聊天框的紧凑配置选择交互，但不复刻 Codex 品牌视觉。配置控件靠近输入框，视觉权重低于文本输入和发送动作，使用近直角、细边框、深浅主题和金色强调。

替代方案：

- CSS Port：适合完全移植外部 HTML/CSS，但本 REQ 只有局部交互参考，会与 MoonBox Ops token 产生冲突。
- 独立大配置面板：可承载更多说明，但会破坏 Chat 输入区密度，也不符合用户要求的聊天框内选择体验。

### D2. 服务端能力配置作为唯一可用性事实源

前端加载 Chat 工作台时请求执行配置能力，返回 Agent、模型、推理配置、默认值、可用状态和禁用原因。前端可以缓存上一次成功结果用于布局稳定，但发送时后端仍以当前服务端策略重新校验。

### D3. 请求配置与实际生效配置分离

发送请求记录 `requested_config`，执行端实际使用结果记录 `effective_config`。服务端拒绝或降级时保留脱敏 `fallback_reason` 或错误码。历史轮次展示实际生效配置，不用当前选择覆盖过去事实。

### D4. 运行中配置不改变当前执行

首版默认在同会话运行中、停止中或状态未知时禁用 Agent、模型和推理配置修改。若后续允许预设下一轮配置，必须在 UI 上区分当前运行配置和下一轮配置，本 Change 不要求首版支持预设。

### D5. 观测只保存脱敏配置摘要

行为事件记录配置选择、配置加载和发送结果；请求日志记录脱敏配置标识、状态码、错误码和耗时；Task Trace 记录实际生效配置、降级节点和错误摘要。任何 metadata 不保存完整 Prompt、完整回复、完整 Diff、Authorization、Cookie、Token、密钥、本机绝对路径、完整内部配置或真实客户敏感数据。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web_request_wrapper
    - api
    - db
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: Chat 输入区新增执行配置选择，会影响前端请求封装、配置能力 API、发送 API 字段、轮次持久化、配置选择行为事件、请求日志和 Codex 执行 Task Trace。
  validation: 实现阶段必须验证配置选择、发送和历史追溯只记录脱敏 Agent/model/reasoning 标识、实际生效配置摘要、错误码和降级原因；请求日志与 Task Trace 不保存完整 Prompt、完整回复、完整 Diff、密钥、凭证、本机绝对路径或内部配置全文；观测失败不阻断主流程但保留脱敏降级摘要。
```

API contract 影响：需要同步配置能力查询、Chat 发送、历史轮次读取的 OpenAPI、客户端生成、错误码、API 文档和接口测试。DB 影响：若新增轮次配置字段或 JSON 快照，需要同步 SQLite/MySQL schema、迁移、`docs/04-database-design.md` 和兼容测试。

## 冲突报告

事实源优先级：

1. `prototype/web/prototype.html`
2. `prototype/web/context.md`
3. `acceptance.md`
4. `rules/ui-design.md`
5. 现有 `openspec/specs/web-catalog-chat-workbench/spec.md`
6. 现有 `openspec/specs/codex-session-execution/spec.md`

冲突处理：

| 冲突点 | 处理 |
|---|---|
| `requirement.md` 人类入口状态仍显示 approved/plan | 以 `trace.md`、CHANGELOG 和 Sprint 投影为事实源；本 Change 完成后由 Workflow Sync 修正投影。 |
| prototype 使用静态模型名 | 仅作为结构示例；最终模型和推理选项必须由服务端能力配置驱动。 |
| Codex 聊天框交互参考与 MoonBox 视觉体系 | 采用局部一致交互，不复刻外部品牌视觉；视觉 token 以 MoonBox Ops 为准。 |
| 当前只有一个 Agent | 展示 Codex 执行主体，但使用低权重只读、禁用下拉或单项选择器，避免暗示多 Agent 已可用。 |
| 同一会话是否允许切换配置 | 首版默认切换只影响后续消息；若执行端要求固定会话配置，UI 禁用切换或引导新建会话。 |

## UI 合同

| 项 | 契约 |
|---|---|
| 页面与入口 | `/chat` 或等价 Chat 工作台入口；保持个人会话、历史、轨迹、Diff 和停止控制。 |
| 事实源优先级 | `prototype.html`、`context.md`、`acceptance.md`、`ui-design.md`、既有 Chat 工作台。 |
| 页面壳 | 共享侧边栏和空间菜单保留；主工作区为对话滚动区、输入 Composer、轨迹入口或详情面板。 |
| 输入区 | 在 PromptComposer 中新增 ExecutionConfigBar，包含 AgentSelector、ModelSelector、ReasoningSelector，靠近输入框并不遮挡发送/停止动作。 |
| 配置菜单 | 模型和推理菜单展示显示名、稳定值、可用状态、禁用原因；长文本截断并可通过菜单详情或 tooltip 识别。 |
| 轮次元信息 | ExecutionDetailPanel 或 TurnMetadata 展示本轮实际生效 Agent、模型、推理配置和脱敏降级原因。 |
| 视觉 token | 使用 MoonBox Ops 字体、近直角、细边框、金色强调、深浅主题；避免蓝紫渐变、大圆角卡片和低密度说明卡片。 |
| 交互状态 | loading、ready、single-agent、unavailable-option、running、stopping、unknown、archived、narrow、error。 |
| 浮层退出 | 模型/推理菜单支持选择后关闭、点击外部关闭或 Esc 关闭；外部点击需要覆盖 capture 阶段，不被内部 `stopPropagation` 破坏。 |
| 权限规则 | 配置能力查询、发送、历史读取和实际生效配置展示均重验本人、空间、会话和执行端能力权限。 |
| Mock/API 边界 | Change 实现阶段可先用 Mock 完成 Skeleton，但最终验收必须声明真实 API 覆盖范围；Mock 不得冒充生产接入。 |

## UI 骨架

```text
ChatWorkbench
  ConversationPane
  PromptComposer [data-testid="chat-composer"]
    ExecutionConfigBar [data-testid="chat-execution-config-bar"]
      AgentSelector [data-testid="chat-agent-selector"]
      ModelSelector [data-testid="chat-model-selector"]
      ReasoningSelector [data-testid="chat-reasoning-selector"]
    ExecutionConfigMenu [data-testid="chat-execution-config-menu"]
    PromptInput [data-testid="chat-prompt"]
    ComposerActions [data-testid="chat-send-actions"]
      SendButton
      StopButton
  ExecutionDetailPanel [data-testid="chat-execution-detail"]
    TurnMetadata
      EffectiveExecutionConfig [data-testid="chat-effective-config"]
```

1440px 验收焦点：

- Agent、模型和推理控件同排展示，输入框仍为主视觉。
- Agent 单项状态清晰，不让用户误以为存在其他可用 Agent。
- 长模型名截断后不挤压输入框、发送按钮、停止按钮或运行状态。
- 菜单层级、边框、z-index、hover、focus、disabled、错误态清晰。
- 运行中禁用态不会让用户误以为已改变当前执行。

## UI 参考稿复刻合同

| 项 | 内容 |
|---|---|
| 保真模式 | 局部一致 / 风格迁移，不逐像素复刻 Codex 聊天框。 |
| 业务语义保留 | MoonBox 共享导航、空间权限、会话历史、轨迹详情、Diff、OpenSpec 治理边界、深浅主题。 |
| 参考稿反向工程 | 输入区配置栏、Agent 低权重显示、模型菜单、推理菜单、禁用原因、发送/停止动作、轮次配置摘要。 |
| Selector 映射 | `chat-execution-config-bar`、`chat-agent-selector`、`chat-model-selector`、`chat-reasoning-selector`、`chat-execution-config-menu`、`chat-effective-config`。 |
| 动作按钮矩阵 | Agent 控件为只读或 disabled select；模型控件触发 popover/menu；推理控件触发 popover/menu；发送按钮触发执行；停止按钮沿用父 REQ。 |
| Computed style 采样 | 1440px、1024px、390px；深浅主题；采样配置栏、selector chip、菜单、禁用项、错误提示、发送区。关键属性包括字体、字号、行高、padding、gap、border、background、color、z-index、overflow。 |
| 分批验收 | Skeleton、配置能力 API、配置栏控件、模型/推理菜单、发送链路、历史回显、窄屏/主题、观测与权限。 |

## API 与数据边界

- 配置能力接口：返回 Agent、模型、推理配置、默认值、可用状态、禁用原因和服务端策略版本。
- Chat 发送接口：接受 requested agent/model/reasoning 配置、既有行为链路字段和幂等请求标识。
- Chat 发送响应或轮次读取：返回 requested_config、effective_config、fallback_reason 或受控错误码。
- 数据库：保存轮次请求配置、实际配置、降级原因摘要、策略版本或等价 JSON 快照；历史轮次不可被当前选择覆盖。
- 生成客户端：前端请求封装和 Orval 类型必须能表达配置能力、发送参数和历史回显字段。

## 风险与取舍

| 风险 | 缓解 |
|---|---|
| 前端静态展示导致选择未真实生效 | spec 和 tasks 要求发送 API、后端校验、轮次事实源和历史回显全部闭环。 |
| 配置列表硬编码导致执行端不支持 | 服务端能力配置为唯一事实源，前端只渲染返回结果。 |
| 同会话运行中切换造成歧义 | 首版默认运行中禁用配置修改，后续预设下一轮需另行明确。 |
| 观测泄漏 Prompt 或内部配置 | 观测只记录脱敏配置标识、错误码和降级摘要，测试覆盖敏感字段过滤。 |
| Sprint 容量缓冲不足 | `sprint-006` 容量使用率接近满载，apply 阶段应优先完成核心链路和门禁，不扩展非目标能力。 |

## 迁移计划

1. 先补 UI Skeleton、配置能力接口契约和数据字段设计，确保现有文本 Chat 不回退。
2. 增加服务端配置能力、发送校验、轮次配置快照和历史读取字段。
3. 接入前端配置栏、菜单、加载/错误/禁用/运行中/归档状态。
4. 接入行为事件、请求日志、Task Trace 和流程节点脱敏摘要。
5. 完成 OpenAPI/客户端生成、SQLite/MySQL、前后端测试、1440px/窄屏截图、computed style 和 REQ 最终一致性回填。

回滚策略：可通过服务端能力配置隐藏模型/推理选择入口或只返回默认配置，保留既有文本 Chat 工作台；已记录历史轮次继续只读展示实际生效配置摘要。

## 待确认问题

- 模型与推理配置稳定值、展示名和默认值以实现阶段服务端配置为准。
- 若执行端要求同一会话固定模型或推理配置，首版 UI 需要禁用切换或引导新建会话。
- 降级策略是否允许自动 fallback 需要实现阶段按服务端策略确定；无明确规则时应拒绝并返回受控错误。
