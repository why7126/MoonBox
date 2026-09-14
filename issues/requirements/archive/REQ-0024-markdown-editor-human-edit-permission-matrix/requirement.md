---
requirement_id: REQ-0024-markdown-editor-human-edit-permission-matrix
title: Markdown 编辑器按治理阶段扩展人工编辑权限矩阵
terminal: multi
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0021-markdown-editor-vditor-enhancement
created_at: 2026-09-03 21:55:37
updated_at: 2026-09-14 00:04:50
priority: P1
---

# Markdown 编辑器按治理阶段扩展人工编辑权限矩阵

## 背景

REQ-0021 已为需求中心 Markdown 抽屉引入增强编辑体验，但 MVP 明确只覆盖采集池 `capture.md`，避免一次性扩大治理文档编辑面。随着需求中心继续承载 REQ、BUG、Sprint 和 OpenSpec 的日常协作，单一 `editable` 布尔值已经不足以表达真实权限：不同阶段、不同文档、不同操作类型需要不同的人机边界。

本需求希望将 Markdown 文档能力拆成两层：Human Edit Capability 控制用户在页面中是否可以手动编辑；System Mutation Capability 控制 AI、Workflow、脚本和命令是否可以按治理流程生成、追加、修订文档。两者独立后，`trace.md` 可以对人工始终只读，同时仍允许 Workflow Sync、AI 命令链路和治理脚本追加审计记录。

当前实现中，后端文档入口只返回 `editable: bool`，且保存接口硬编码为“采集池 + `capture.md`”；前端也基于相同条件决定编辑态、保存、脏状态确认和 Vditor 工具栏。本需求将在不绕过 REQ/BUG/Sprint/OpenSpec 状态机的前提下，扩展为统一的文档能力矩阵。

## 目标用户

- 产品负责人：需要在合适阶段补充需求、缺陷、验收和评审材料，但不能误改审计记录或已进入受控流程的文档。
- 项目负责人：需要通过页面清楚区分可人工编辑、只读、系统可变更和任务勾选能力，减少权限误解。
- 研发协作者：需要在待开发阶段维护 OpenSpec Change 计划类文档，并在研发中、验收中避免手动改动执行事实。
- AI/Workflow 执行链路：需要在 UI 只读约束之外，继续通过受控命令追加 trace、更新 tasks 和同步状态。

## 范围

### 包含

- 定义文档能力模型，至少包含 `readable`、`human_editable`、`ai_mutable`、`task_toggle_only` 和 `reason`。
- 后端按对象类型、治理阶段、文档名、文档位置和用户权限计算每个文档的能力。
- 前端根据后端能力决定 Markdown 抽屉的阅读态、完整编辑态、Vditor/分栏能力和 checkbox-only 能力。
- 保存接口后端再次校验文档能力，拒绝越权保存，不能依赖前端判断作为最终授权。
- `trace.md` 对人工始终只读，系统治理链路仍可按 Workflow Sync、AI 命令或脚本更新。
- 验收中 `tasks.md` 仅提供任务勾选/取消勾选能力，不开放 Markdown 全文编辑。
- 待开发阶段允许编辑 OpenSpec Change 计划类文档，包括 `proposal.md`、Change 下的 `spec.md`、`design.md`、`tasks.md`。
- 已生效 `openspec/specs/**/spec.md` 始终不作为人工编辑目标，避免绕过 archive 合并流程。
- REQ 与 BUG 文档均纳入同一阶段能力矩阵。

### 不包含

- 不在本需求内改变 REQ、BUG、Sprint 或 OpenSpec 的状态机语义。
- 不在本需求内绕过评审、Sprint 纳入、OpenSpec Change、apply、modify 或 archive 门禁。
- 不在本需求内新增多人协同编辑、评论批注、版本 diff、自动保存或文档锁冲突解决。
- 不在本需求内开放 `trace.md`、运行时日志、系统审计记录或已生效规格的人工全文编辑。
- 不在本需求内实现新的 AI Agent 编排系统；AI/Workflow 修改仍复用既有命令和脚本治理链路。
- 不在本需求内要求所有历史文档一次性迁移，只要求新能力模型对当前文档入口和保存接口生效。

## 功能要求

### FR-001 文档能力模型

系统必须为每个可展示文档返回结构化能力，而不是仅返回单一 `editable` 布尔值。能力字段至少包括：

```yaml
readable: true
human_editable: false
ai_mutable: true
task_toggle_only: false
reason: "trace.md 仅允许系统治理链路追加审计记录"
```

`readable` 表示当前用户是否可查看文档；`human_editable` 表示用户是否可在页面中进入完整 Markdown 编辑器；`ai_mutable` 表示 AI、Workflow、脚本或命令是否可在治理流程内修改；`task_toggle_only` 表示页面仅允许切换任务勾选状态，不允许全文编辑；`reason` 用于向前端和用户解释受限原因。

### FR-002 人工编辑能力矩阵

系统必须按治理阶段计算 Human Edit Capability。初始矩阵如下：

| 阶段 | 可人工编辑文档 |
|---|---|
| 采集池 | `capture.md` |
| 规划中 | `requirement.md`、`bug.md` |
| 待评审 | `user-stories.md`、`business-flow.md`、`acceptance.md`、`root-cause.md`、`workaround.md`、`requirement.md`、`bug.md` |
| 已评审 | `user-stories.md`、`business-flow.md`、`acceptance.md`、`root-cause.md`、`workaround.md`、`requirement.md`、`bug.md`、`review.md` |
| 迭代规划 | 无 |
| 待开发 | `proposal.md`、`spec.md`、`design.md`、`tasks.md` |
| 研发中 | 无 |
| 验收中 | 无全文编辑；仅 `tasks.md` 支持勾选/取消勾选 |
| 已完成 | 无 |

不属于当前对象类型的文档即使出现在矩阵中也不得开放。例如 Requirement 不因待评审阶段出现 `bug.md` 而允许编辑不存在或不属于该对象的缺陷主文档。

### FR-003 `trace.md` 人工只读边界

`trace.md` 对人工始终只读，不随阶段变化开放完整编辑器，也不得提供 checkbox-only 操作。

`trace.md` 的 `ai_mutable` 可以为 true，但只代表 Workflow Sync、AI 命令、状态同步脚本和受控治理流程可追加或修订审计事实。页面保存接口不得因 `ai_mutable=true` 接受人工提交 `trace.md` 全文。

### FR-004 System Mutation Capability

系统必须明确区分系统修改能力和人工编辑能力。AI、Workflow、脚本和命令可以在其已有治理门禁下生成、追加、修订文档，不受前端只读 UI 限制，但必须继续遵守对应命令、状态机、OpenSpec 和 Workflow Sync 规则。

当文档对人工只读但系统可变更时，前端应显示只读状态和受限原因，不应暗示文档永远不可变。后端应在不同入口区分人工保存请求与系统治理请求，避免把 UI 只读误用为系统写入禁止。

### FR-005 `tasks.md` 验收中 checkbox-only 能力

验收中阶段的 `tasks.md` 不允许进入完整 Vditor 或源码编辑器。前端必须渲染任务列表 checkbox，只允许切换 Markdown task list 中的 `- [ ]` 与 `- [x]` 状态。

checkbox-only 操作不得修改任务描述、标题、分组、验收记录或非任务行。保存或提交时后端必须校验变更差异仅限任务勾选状态；若检测到其他文本变化，必须拒绝并提示原因。

### FR-006 待开发 OpenSpec Change 文档编辑边界

待开发阶段允许人工编辑 OpenSpec Change 计划类文档：`proposal.md`、Change 下的 `spec.md`、`design.md`、`tasks.md`。这些能力只适用于当前 Change 工作区中的文档。

已生效 `openspec/specs/**/spec.md` 不属于待开发阶段人工编辑范围，必须保持只读。任何已生效规格变化仍应通过 OpenSpec Change 和 archive 合并流程完成。

### FR-007 后端能力计算与保存校验

后端必须提供统一能力计算函数，输入至少包括对象类型、对象状态、阶段、文档名、文档路径类别、当前用户权限和文档存在性，输出文档能力对象。

文档列表接口必须返回能力对象；文档保存接口必须复用同一能力计算结果再次校验。前端隐藏编辑入口只作为体验优化，不能作为授权边界。

保存接口应区分完整 Markdown 保存与 task toggle 保存。完整 Markdown 保存要求 `human_editable=true`；task toggle 保存要求 `task_toggle_only=true`，并执行差异校验。

### FR-008 前端渲染与交互策略

前端必须根据后端能力决定 Markdown 抽屉行为：

- `human_editable=true`：允许进入编辑/分栏/Vditor，展示保存和脏状态保护。
- `task_toggle_only=true`：展示可勾选任务列表，不展示源码编辑器、Vditor 工具栏或全文保存入口。
- 其他可读文档：以阅读态只读展示，并显示必要的只读原因。

脏状态确认仅在用户真实产生可保存改动后触发。只读文档关闭、未改动文档关闭、保存成功后关闭不得触发未保存确认。

### FR-009 兼容既有 `editable` 字段

若前端或测试仍依赖旧字段，后端可以在过渡期保留 `editable` 作为 `human_editable` 的兼容别名，但新实现和新测试应优先使用能力对象。

过渡期结束后，所有新增逻辑应以能力对象为准，避免继续散落硬编码 `capture.md` 或单一阶段判断。

### FR-010 错误提示与受限原因

当用户尝试编辑只读文档、越权保存、在验收中全文修改 `tasks.md` 或编辑已生效规格时，系统必须返回稳定、可理解、已脱敏的错误提示。

错误提示不得暴露本机绝对路径、系统用户名、内部异常堆栈、真实密钥、访问令牌、`.env` 内容、未脱敏日志或完整治理目录结构。

### FR-011 权限、安全与审计

所有人工文档修改必须记录操作者、对象 ID、文档名、操作类型、结果和时间。高风险或失败操作应至少进入请求日志；若后续实现接入行为事件或 Task Trace，应按产品数据采集与链路观测标准保留脱敏摘要。

系统修改能力不得绕过既有 Workflow Sync、OpenSpec、Sprint 和 Issue trace 事实源。系统写入不得持久化完整 prompt、密钥、本机路径或未脱敏运行时数据。

## UI 约束

- Markdown 抽屉继续沿用 REQ-0021 的 Header、文档属性 Strip、阅读态、编辑态、分栏态和固定 footer 结构。
- 完整编辑态只能在 `human_editable=true` 时出现；只读文档不得出现 Vditor 工具栏、保存按钮或源码编辑区。
- `task_toggle_only=true` 时，`tasks.md` 应呈现任务清单操作界面，checkbox 是主交互，文本描述保持只读。
- `trace.md` 应始终显示只读标识或只读原因，避免用户误以为按钮消失是加载失败。
- 待开发阶段的 OpenSpec Change 文档应清楚展示其 Change 范围，避免用户把 Change 草案 `spec.md` 与已生效规格混淆。
- 禁用态、只读态、checkbox-only 态和保存失败态在深浅主题下都必须可读，且不得造成抽屉布局跳动。
- 长文件名、长错误原因、长表格、长代码块和长任务描述必须有溢出处理。

## 产品数据采集与链路观测

```text
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: "本需求影响 Web 端文档编辑行为、REST API 响应字段、保存接口授权校验和系统治理链路写入边界，需要记录人工编辑、checkbox-only 操作、越权拒绝和系统修改入口的脱敏摘要。"
  validation: "后续实现需验证前端请求封装、后端 request_id、越权保存错误、安全 metadata、task toggle 差异校验，以及 Workflow Sync/AI 命令写入不受 UI 只读限制。"
```

本需求不要求新增数据库表作为 PRD 前置条件，但后续 OpenSpec 需要判断是否复用既有请求日志与行为事件能力，或为文档保存、任务勾选、系统写入补充 Task Trace 覆盖。

## 关联需求

- REQ-0021-markdown-editor-vditor-enhancement：本需求承接 Markdown 抽屉与 Vditor 编辑体验，并将编辑范围从单点 `capture.md` 扩展为阶段能力矩阵。
- REQ-0020-requirement-center-card-document-actions-ai-chat：本需求依赖需求中心卡片文档入口、阶段动作和 AI 聊天动作承载。
- REQ-0012-frontend-requirement-center：本需求延续前台需求中心 9 阶段看板和 UI 结构。
- REQ-0013-requirement-center-real-data-integration：本需求依赖真实治理数据读取、文档列表和文档保存接口。
- REQ-0008-prototype-driven-page-acceptance-gate：后续若涉及 UI 原型和视觉验收，继续遵守原型驱动验收门禁。

## 状态块

```text
status: done
generated_at: 2026-09-03 21:55:37
completed_at: 2026-09-03 22:02:09
reviewed_at: 2026-09-04 08:01:56
approved_at: 2026-09-04 08:01:56
source_material:
  - capture.md
  - explore_context: "人工编辑权限按阶段收紧，AI/Workflow 修改权限另走治理链路"
  - related_requirement: REQ-0021-markdown-editor-vditor-enhancement
next: /opsx-apply REQ-0024-markdown-editor-human-edit-permission-matrix
iteration: sprint-004
openspec_change: update-markdown-editor-human-edit-permission-matrix
```
