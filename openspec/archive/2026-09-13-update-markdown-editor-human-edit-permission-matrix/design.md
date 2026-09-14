## 背景

REQ-0024 来源于 REQ-0021 的 Markdown 抽屉增强后续需求。现状中，需求中心文档入口和保存接口以单一 `editable` 布尔值表达人工可编辑性，且主要硬编码为采集池阶段的 `capture.md`。这无法表达三类不同能力：用户手动全文编辑、验收中 `tasks.md` 勾选、AI/Workflow/脚本按治理流程写入。

本 Change 只建立 OpenSpec 设计、规格和任务，不修改 `src/`。后续实现必须继续遵守 REQ、BUG、Sprint 和 OpenSpec 状态机；前端只读仅限制 Human Edit Capability，不得成为 System Mutation Capability 的禁止条件。

## 目标与非目标

**目标：**

- 为每个展示文档提供结构化能力对象：`readable`、`human_editable`、`ai_mutable`、`task_toggle_only`、`reason`。
- 用统一后端能力计算覆盖 REQ、BUG 和 OpenSpec Change 文档。
- 让前端 Markdown 抽屉由能力对象驱动完整编辑、只读和 checkbox-only 三类状态。
- 在保存接口后端复用能力计算完成最终授权，拒绝越权全文保存和非法 task toggle。
- 让 `trace.md` 对人工始终只读，同时保留 Workflow Sync、AI 命令和治理脚本写入。
- 保持已生效 `openspec/specs/**/spec.md` 人工只读，避免绕过 archive 合并。

**非目标：**

- 不改变 REQ、BUG、Sprint 或 OpenSpec 生命周期状态机。
- 不新增多人协同编辑、评论、版本 diff、自动保存或文档锁。
- 不把 UI 只读策略推广为系统治理写入禁令。
- 不直接修改已生效 `openspec/specs/`。

## 设计决策

### D1 能力模型分层

文档能力拆为 Human Edit Capability、System Mutation Capability 和 Task Toggle Capability。

- `human_editable=true` 只代表用户可在页面进入完整 Markdown 编辑器。
- `ai_mutable=true` 只代表 AI、Workflow、脚本和命令可在既有治理门禁下修改文档。
- `task_toggle_only=true` 只代表页面可提交任务勾选变化，不开放全文编辑。

备选方案是继续扩展 `editable` 布尔值，但它无法解释 `trace.md` 人工只读但系统可写、验收中 `tasks.md` 可勾选但不可全文编辑这两个核心边界。

### D2 后端统一计算和二次校验

后端提供统一能力计算函数，输入对象类型、阶段、状态、文档名、路径类别、存在性和用户权限，输出能力对象。文档列表接口返回该对象；全文保存和 task toggle 保存接口复用同一计算结果做最终授权。

前端隐藏编辑入口只作为体验优化；任何人工保存请求都必须由后端重新校验。

### D3 阶段矩阵作为产品规则

Human Edit Capability 初始矩阵如下：

| 阶段 | 人工全文编辑 |
|---|---|
| 采集池 | `capture.md` |
| 规划中 | Requirement 的 `requirement.md`，Bug 的 `bug.md` |
| 待评审 | Requirement 的 `user-stories.md`、`business-flow.md`、`acceptance.md`、`requirement.md`；Bug 的 `root-cause.md`、`workaround.md`、`acceptance.md`、`bug.md` |
| 已评审 | 待评审可编辑文档 + `review.md` |
| 迭代规划 | 无 |
| 待开发 | 当前 OpenSpec Change 下 `proposal.md`、`spec.md`、`design.md`、`tasks.md` |
| 研发中 | 无 |
| 验收中 | 无全文编辑；仅 `tasks.md` checkbox-only |
| 已完成 | 无 |

矩阵必须结合对象类型和路径类别解释。例如 Requirement 不因矩阵包含 `bug.md` 而开放缺陷主文档；待开发的 `spec.md` 只限当前 Change 下的 delta spec，不包括已生效规格。

### D4 `tasks.md` checkbox-only 差异校验

验收中 `tasks.md` 的提交入口必须与全文保存分离。后端对原文和提交内容做结构化或行级 diff，仅允许 Markdown task list marker 在 `- [ ]` 与 `- [x]` 之间切换；任务描述、标题、非任务行、验收记录和其他 Markdown 内容变化必须拒绝。

### D5 UI Contract

本 Change 无 prototype 目录，UI 不需要建立原型承接；实现需复用 REQ-0021 Markdown 抽屉结构。

- Header、文档属性 Strip、阅读态、编辑态、分栏态和固定 footer 沿用现有交互。
- `human_editable=true` 展示完整 Vditor、分栏、保存和脏状态保护。
- `task_toggle_only=true` 展示任务清单 checkbox，不展示 Vditor 工具栏、源码编辑区或全文保存入口。
- 只读文档展示只读原因；关闭只读或未改动文档不触发未保存确认。
- 待开发 Change 文档必须展示 Change 范围标识，降低草案 `spec.md` 与已生效规格混淆风险。

### D6 产品数据采集与链路观测

```text
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: "本 Change 影响 Web 端文档编辑行为、REST API 响应字段、保存接口授权校验和系统治理链路写入边界，需要记录人工编辑、checkbox-only 操作、越权拒绝和系统修改入口的脱敏摘要。"
  validation: "实现与验收需覆盖前端请求封装、后端可信 request_id、稳定行为事件名、越权保存错误、安全 metadata、task toggle 差异校验，以及 Workflow Sync/AI 命令写入不受 UI 只读限制。"
```

请求日志至少记录对象 ID、文档名、操作类型、结果、错误码和脱敏原因。行为事件只能使用稳定事件名与脱敏属性。Task Trace 对 task toggle 差异校验作为候选：若实现判断该校验为单请求低风险操作，可以记录不接入 Task Trace 的具体原因。

## 风险与权衡

- 权限字段被前端误解为最终授权 -> 保存接口必须复用后端能力计算，测试覆盖篡改前端状态后的越权保存。
- `ai_mutable` 被误用为人工保存许可 -> 接口区分人工保存请求和系统治理写入入口，并为 `trace.md` 覆盖 403 场景。
- `tasks.md` checkbox-only 误改文本 -> 后端 diff 校验只允许 task marker 切换，失败时返回脱敏错误。
- Change 草案 `spec.md` 与已生效规格混淆 -> 路径类别参与能力计算，前端展示 Change 范围标识。
- 观测 metadata 泄漏 Markdown 内容 -> metadata 仅保存摘要、错误码和安全枚举，不保存完整请求体、响应体或 Markdown 全文。

## 迁移计划

1. 在后端新增文档能力计算和响应 schema，保留 `editable` 作为 `human_editable` 兼容别名。
2. 更新文档列表、文档读取、全文保存和 task toggle 保存接口。
3. 更新前端 Markdown 抽屉三态渲染、保存入口和脏状态判断。
4. 补充后端与前端测试。
5. 更新 API 文档、OpenAPI/Orval 相关产物或记录不适用原因。

Rollback：若新能力对象导致前端兼容问题，可保留旧 `editable` 字段继续驱动旧只读逻辑，同时关闭新增 checkbox-only 入口；后端授权矩阵仍应保留，避免回退到前端授权。

## 待确认问题

- 无阻塞问题。`review.md` 在已评审阶段按 REQ-0024 评审结论开放人工编辑；后续如需拆分普通用户与评审权限用户，可另立权限细化需求。
