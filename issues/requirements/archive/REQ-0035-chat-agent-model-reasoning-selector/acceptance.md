---
requirement_id: REQ-0035-chat-agent-model-reasoning-selector
title: 聊天框新增 Agent、模型和推理程序选择 - 验收标准
acceptance_status: passed
owner: product
created_at: 2026-09-14 23:18:06
updated_at: 2026-09-29 14:41:41
---

# 验收标准

## 功能 AC

- [ ] AC-001 Agent 入口展示：Chat 输入区可见 Agent 选择或只读入口，当前默认且唯一 Agent 为 Codex，状态清晰。
- [ ] AC-002 Agent 单项状态：当前仅 Codex 时，控件采用只读、禁用下拉或单项下拉均可，但不得暗示存在其他可用 Agent。
- [ ] AC-003 模型选项来源：模型列表来自服务端能力配置，包含显示名、稳定值、可用状态和禁用原因。
- [ ] AC-004 模型默认值：页面首次加载、新建会话和继续会话时显示服务端认可的默认模型。
- [ ] AC-005 推理配置来源：推理程序或推理强度列表来自服务端配置或前后端共享能力约束，稳定值能映射到执行端。
- [ ] AC-006 不可用选项：无权、额度不足、执行端不支持或策略禁用的模型/推理选项展示禁用态和短原因。
- [ ] AC-007 发送参数：发送消息时请求携带当前 Agent、模型和推理配置标识，并包含既有行为链路字段。
- [ ] AC-008 后端校验：后端发送接口重新校验 Agent、模型、推理配置、会话权限和空间权限，不能只信任前端选择。
- [ ] AC-009 实际生效配置：轮次事实源记录请求配置、实际生效配置和降级原因摘要。
- [ ] AC-010 历史追溯：历史轮次详情可查看该轮实际使用的 Agent、模型和推理配置；当前选择不改写历史。
- [ ] AC-011 降级展示：服务端因能力、额度或策略降级配置时，页面展示实际生效值和脱敏原因。
- [ ] AC-012 拒绝展示：配置不可用且无法降级时，页面展示可理解错误，不泄漏内部路径、完整配置、密钥、Token、Authorization、Cookie 或 `.env` 内容。
- [ ] AC-013 继续会话：继续已有会话时，配置切换默认只影响后续新消息；若策略要求固定会话配置，则控件禁用或引导新建会话。
- [ ] AC-014 运行中状态：同会话运行中、停止中或状态未知时，控件不能改变已经发出的执行；首版可禁用配置修改。
- [ ] AC-015 已归档会话：已归档会话保持只读，不允许通过配置控件触发新执行。
- [ ] AC-016 布局稳定：配置加载中、加载失败、长模型名、禁用原因和窄屏下不遮挡输入框、发送按钮、停止按钮或执行状态。
- [ ] AC-017 深浅主题：控件、菜单、禁用态、焦点态和错误态在深浅主题下符合 Ops 视觉 token。
- [ ] AC-018 浮层退出：模型/推理下拉或菜单支持选择后关闭、点击外部关闭或 Esc 关闭；内部点击不得误关闭父级浮层。
- [ ] AC-019 API 文档：如新增请求或响应字段，同步 API 文档、OpenAPI、客户端类型和错误码。
- [ ] AC-020 DB 兼容：如新增轮次配置持久化字段，同步 SQLite/MySQL 迁移、数据库设计和回归测试。
- [ ] AC-021 行为事件：记录配置选择和发送结果的脱敏事件名、配置标识和结果，不记录用户输入正文、完整回复或 Diff。
- [ ] AC-022 请求日志：请求日志只保存脱敏配置摘要、状态码、错误码和耗时，不保存完整请求体或响应体。
- [ ] AC-023 Task Trace：Codex 执行链路记录实际生效配置摘要、降级节点和错误摘要，不保存 Prompt、回复、Diff、密钥或路径。
- [ ] AC-024 测试覆盖：实现阶段覆盖 Agent 单项、模型选择、推理选择、不可用选项、加载失败、发送参数、历史追溯、运行中禁用、权限拒绝和窄屏布局。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解：`prototype/web/context.md` 已记录页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 UI Skeleton：后续 Change `design.md` 必须写入 Chat 输入区配置栏 UI Skeleton，覆盖控件插槽、菜单容器、状态容器、稳定选择器和 Mock/API 边界。
- [ ] AC-PROTOTYPE-003 1440px 视觉验收：实现阶段必须在 1440px 桌面视口验证输入区配置栏、菜单、禁用态、错误态和文本溢出。
- [ ] AC-PROTOTYPE-004 关键交互验收：实现阶段必须覆盖模型菜单、推理菜单、外部点击关闭、Esc 关闭、运行中禁用和窄屏换行或更多菜单。
- [ ] AC-PROTOTYPE-005 REQ 最终一致性：归档前确认 `requirement.md`、`acceptance.md`、`trace.md` 与最终 Change 设计、实现证据、截图、computed style 和 Mock/API 边界一致。

## 知识库横切 AC

本 REQ 为前台 Chat 输入区能力增强，不命中 `req-complete` 当前定义的 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 横切标签，因此不追加 `AC-XCUT-*`。已读取并引用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` 作为 UI 原型门禁参考。

## 非目标验收

- [ ] NFR-001 不新增除 Codex 外的真实 Agent 接入。
- [ ] NFR-002 不新增用户自定义模型、外部供应商绑定或个人 API Key 管理。
- [ ] NFR-003 不新增后台 Agent/模型配置管理页面。
- [ ] NFR-004 不改变 Chat 工作台既有会话权限、空间权限、仓库授权、执行隔离、停止、重试和历史管理规则。
- [ ] NFR-005 不允许通过模型或推理选项绕过 REQ/BUG 评审、Sprint 纳入、OpenSpec Change 或正式开发授权。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: add-chat-agent-model-reasoning-selector
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 实现验收证据

| 类别 | 证据 |
|---|---|
| 后端回归 | `uv run pytest src/backend/tests/test_chat.py -q`：35 passed, 1 skipped |
| 前端交互 | `node_modules/.bin/vitest run src/chat-composer.test.tsx`：9 passed |
| 类型与构建 | `node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 均通过 |
| UI 视觉 | `openspec/archive/2026-09-29-add-chat-agent-model-reasoning-selector/evidence/ui/` 三档截图与 computed-style |
| API/DB 文档 | `docs/03-api-index.md`、`docs/04-database-design.md` 已同步 REQ-0035 增量 |
| 验收返修 | 2026-09-15 模型列表补齐为 Codex 当前 5 款：`GPT-5.6 Sol`、`GPT-6 Astra`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5`；前端继续由接口返回值驱动 |
