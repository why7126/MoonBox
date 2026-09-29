## 任务清单

### 1. 契约与 Skeleton

- [x] 1.1 确认 Chat 工作台现有组件、API、轮次模型和执行端配置来源，记录非目标不改范围。
- [x] 1.2 完成 ExecutionConfigBar UI Skeleton，覆盖 `chat-execution-config-bar`、`chat-agent-selector`、`chat-model-selector`、`chat-reasoning-selector`、`chat-execution-config-menu`、`chat-effective-config` 稳定选择器。
- [x] 1.3 采集或记录 1440px Skeleton 首轮证据，确认配置栏、输入框、发送/停止动作和菜单层级方向正确。
- [x] 1.4 完成 Mock/API 边界声明，明确 Skeleton 阶段 Mock 配置与后续真实配置 API 的差异。

### 2. 后端 API 与数据

- [x] 2.1 新增或扩展执行配置能力查询接口，返回 Agent、模型、推理配置、默认值、可用状态、禁用原因和策略版本。
- [x] 2.2 扩展 Chat 发送接口，接收请求 Agent、模型和推理配置，并重验用户、空间、会话、执行端能力和配置可用性。
- [x] 2.3 扩展轮次事实源，保存请求配置、实际生效配置、降级原因摘要和受控错误码。
- [x] 2.4 若新增 DB 字段或 JSON 快照，补齐 SQLite/MySQL 迁移、模型、Repository 和兼容说明。
- [x] 2.5 同步 OpenAPI、Orval 客户端类型、API 文档、错误码和接口测试。

### 3. Web 交互

- [x] 3.1 接入配置能力加载、默认值、加载中、加载失败和 retry 或禁用发送状态。
- [x] 3.2 实现 Agent 单项 Codex 状态，避免暗示多 Agent 已可用。
- [x] 3.3 实现模型和推理菜单，覆盖禁用项原因、长文本截断、tooltip 或菜单详情。
- [x] 3.4 实现发送参数绑定、发送中禁用、运行中/停止中/未知/归档状态和历史轮次实际配置展示。
- [x] 3.5 覆盖 1440px、1024px、390px、深浅主题、菜单 open、禁用、错误和文本溢出视觉验收。

### 4. 观测与安全

- [x] 4.1 增加配置加载、配置选择、发送结果、降级和拒绝的 usage_events 脱敏摘要。
- [x] 4.2 扩展 request_logs metadata，只记录脱敏配置标识、状态码、错误码、耗时和结果。
- [x] 4.3 扩展 task_traces / task_trace_spans 或等价执行链路 metadata，记录实际生效配置摘要和降级节点。
- [x] 4.4 验证观测失败不阻断主流程，并记录脱敏降级摘要。
- [x] 4.5 增加敏感字段过滤测试，确保不保存完整 Prompt、回复、Diff、Authorization、Cookie、Token、密钥、本机绝对路径或内部配置全文。

### 5. 测试与文档

- [x] 5.1 后端测试覆盖配置能力查询、发送校验、不可用配置、降级、拒绝、历史追溯和权限拒绝。
- [x] 5.2 前端测试覆盖 Agent 单项、模型选择、推理选择、不可用选项、加载失败、发送参数、运行中禁用、归档只读和窄屏布局。
- [x] 5.3 DB 相关变更运行 SQLite 快速验证；如新增迁移或生产字段，补充 MySQL 关键路径验证。
- [x] 5.4 运行 OpenSpec 当前 Change 校验、OpenAPI/客户端生成校验和相关前后端测试。
- [x] 5.5 回填 Change trace、REQ `acceptance.md` / `trace.md` 的视觉证据、computed style、Mock/API 边界和最终一致性状态。

### 6. 完成门禁

- [x] 6.1 `openspec validate add-chat-agent-model-reasoning-selector --strict` 通过。
- [x] 6.2 `python scripts/validate-openspec-language.py --change add-chat-agent-model-reasoning-selector --residual-report` 当前 Change 通过。
- [x] 6.3 Workflow Sync 能解析 REQ、Change 与 `sprint-006` 的双向追溯。
- [x] 6.4 linked REQ 与 Change 的 UI Contract、API/DB/观测声明、测试结果和验收证据一致。

## 验收返修记录

完整返修台账见 `acceptance-fixes.md`，本节仅保留可执行任务摘要。

- [x] F1 补齐需求中心可识别的交付验证来源入口：`trace.acceptance_refs` 指向 `acceptance-fixes.md`，并在 `trace.md` 增加非空 `## 验证记录`。
- [x] F2 补齐默认模型候选与 Codex 当前 5 款可选项，详见 `acceptance-fixes.md`。
