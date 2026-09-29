---
name: "req-opsx"
description: "已评审需求 → OpenSpec Change（CLI 驱动）；原 /requirement-to-opsx"
updated_at: 2026-09-15 00:23:57
---

# req-opsx

Use this skill when the user asks to run the migrated source command `req-opsx`.

## Context Budget Guardrails（MUST）

### Guided User Feedback Contract（MUST）

当命令需要用户选择、确认、补充信息或处理阻塞时，MUST 采用引导式反馈：

- 优先使用原生交互卡片组织问题；当客户端或工具层不支持原生交互卡片时，MUST 先声明降级原因，再降级为文本结构化选项。
- 两种形态都必须包含「结构化选项 + 推荐项 + 可补充说明」，不用大段开放式追问替代。
- 每轮只聚焦 1-3 个关键决策；每个决策点 SHOULD 给出 2-4 个互斥选项。
- 至少一个选项 MUST 标注「推荐」，并用一句话说明推荐理由或适用前提。
- 默认提供「可补充说明」入口，允许用户用自然语言覆盖选项、补充约束或给出例外。
- 用户已回答的决策 MUST 在后续输出中被承接并动态收敛，只追问剩余阻塞点或新增风险点，避免重复询问已确认事项。
- 无需用户反馈的成功路径 SHOULD 保持紧凑，不为了套用格式而追加无意义问卷。

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- REQ 转 Change 时只读取目标 REQ 六件套摘要与候选 spec 片段；不得默认读取全部 `openspec/specs/**`。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

将已评审且已纳入 Sprint 的 `issues/requirements/REQ-*` 转为 `openspec/changes/<change-id>/`（proposal / design / specs / tasks）。**不写 `src/`**；实现用 `/opsx-apply`。

**Input**：完整 `REQ-xxxx-slug`

| Flag | 含义 |
|------|------|
| `--type add\|fix\|update` | 强制 change 类型 |
| `--strategy <name>` | css-port、tailwind-ds 等 |
| `--skip-explore` | 跳过 UI 策略探讨 |
| `--change-name <kebab-case>` | 指定 change id |

---

## 前置关系

```text
/req-capture → /req-explore → /req-generate → /req-complete → /req-review (approved)
        │
        └─ /sprint-propose --req REQ-xxxx-slug  →  /req-opsx REQ-xxxx-slug  →  /opsx-apply REQ-xxxx-slug  →  /opsx-modify REQ-xxxx-slug（可选） →  /opsx-archive REQ-xxxx-slug
```

---

## Command Order（MUST）

- 推荐顺序遵守 `docs/08-command-execution-order.md`：REQ approved → `/sprint-propose --req <REQ-full-id>` → REQ `status: in_sprint` → `/req-opsx <REQ-full-id>` → `/opsx-apply <REQ-full-id>` → `/opsx-modify <REQ-full-id>`（可选）→ `/opsx-archive <REQ-full-id>`。
- `/req-opsx` 完成后 MUST 通过 Workflow Sync 将 Change 回填到同一 Sprint 的 `changes[]` 和 `scope_estimates[].change`。
- 若后续输出 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive`，MUST 使用原始完整 `REQ-xxxx-slug`；只有无 REQ/BUG 来源的纯治理 Change 才使用裸 `<change-id>`。
- 写入 `sprint.yaml`、Issue trace、Change trace、Workflow Sync 和 AI Usage 快照的步骤 MUST 严格串行执行。

---

## Step 0 — 必须读取

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/requirement-management.md
rules/ui-design.md
rules/testing.md
rules/directory-structure.md
```

```bash
openspec list --json
openspec list --specs
```

REQ 目录：requirement.md、user-stories.md、business-flow.md、acceptance.md、trace.md、prototype/**

---

## Step 0.5 — 评审门禁（MUST — 无例外）

读 `trace.md`（或 requirement.md frontmatter）`status`：

| status | 动作 |
|--------|------|
| `approved` | **立即停止** → `/sprint-propose --req <REQ-full-id>`，纳入 Sprint 并同步为 `in_sprint` 后再执行 `/req-opsx` |
| `in_sprint` | 可继续（须已完成 `/req-review` 且已由 `/sprint-propose` 纳入 Sprint） |
| `done` | 可继续（追溯/补建 change） |
| `pending_review` / `draft` / `captured` / `enriching` / … | **立即停止** → `/req-review <REQ-full-id> --approve` |

未评审或未纳入 Sprint **不得** opsx；**不得**因口头确认、Change 名称已确定或用户急于开发而 bypass（见 `rules/requirement-management.md` §4.1）。

---

## Step 1 — Readiness

输出 **Requirement Readiness Report**（ready / partially ready / not ready）。

**Not Ready** → `/req-complete <REQ-full-id>`，**停止**，不创建 change。

---

## Step 2 — 影响分析与 Change 分类

```yaml
impact: { backend, web, miniapp, admin, database, storage, api }
capabilities: { new: [], modified: [] }
```

| 条件 | change_type | 示例 |
|------|-------------|------|
| 无相关 spec | add | add-user-login |
| 已有实现，验收/视觉未过 | fix | fix-login-css-port |
| 仅规范文案 | update | update-login-acceptance-sync |

---

## Step 3 — 原型与验收冲突（MUST）

### Step 2.5 — 产品数据采集与链路观测门禁（MUST）

若 REQ 或目标 Change 涉及 API、DB、日志审计、行为埋点、Task Trace、Web/管理端请求封装、对象存储或 Agent Workflow 链路观测，MUST 读取 `docs/standards/product-data-collection-observability.md`，并在 `design.md`、`trace.md`、`acceptance.md` 或 `tasks.md` 写入 `product_data_collection_observability` 固定声明，至少包含 `status`、`affected_layers`、`reason` 和 `validation`。

若不适用，MUST 记录具体 N/A 原因；不得只写“无”或“不涉及”。涉及 API contract 时还 MUST 声明 OpenAPI / Orval / API 文档 / 测试影响；涉及 DB 结构、索引、迁移或保留周期时还 MUST 声明 SQLite / MySQL schema、数据库文档和测试影响。

`prototype/web/` 存在时输出 Conflict Report；优先级：

```text
HTML > PNG > *-context.md > acceptance.md > ui-design.md > openspec/specs
```

design.md **MUST** 含 Conflict Resolution；delta spec 用 MODIFIED/REMOVED 消化。

### Step 3.1 — 原型拆解承接（MUST — 存在 prototype 时）

`prototype/**` 存在时，`/req-opsx` MUST 读取并承接 `/req-complete` 产出的原型拆解、`AC-PROTOTYPE-*`、`trace.md prototype_gate` 和 `docs/standards/prototype-ui-acceptance.md`：

- 若缺原型拆解、`prototype_refs`、`prototype_gate` 或 `AC-PROTOTYPE-*`，Requirement Readiness MUST 为 `Not Ready`，停止并输出 `/req-complete <REQ-full-id>`。
- Change `design.md` MUST 先新增 `UI Contract`，明确事实源优先级、前后台一致性 checklist、关键尺寸/字体/颜色/图标/文案、权限规则、Mock/API 边界和 computed style 验收点。
- Change `design.md` MUST 新增 `UI Skeleton` 章节，包含页面结构、区域边界、组件层级、状态容器、数据依赖、可测选择器和 1440px 验收焦点。
- Change `tasks.md` MUST 将 `UI Skeleton` 作为先行任务，并在任何细节实现任务前完成。
- Change `trace.md` MUST 记录 prototype 来源、Conflict Resolution、UI Contract、Skeleton 状态、1440px/关键交互截图、computed style、Mock/API 边界和最终一致性状态。
- Delta spec MUST 写明 prototype 是设计输入，最终验收以 Change design、acceptance、1440px/关键交互视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。

### Step 3.2 — UI Reference Replication Contract（MUST — 引用参考稿时）

当 REQ 或用户输入明确引用附件 HTML、截图、标注图、既有页面或参考稿，并要求“一对一复刻”“全面贴近”“保持一致”或等价目标时，`/req-opsx` MUST 在 Change `design.md` 写入 `UI Reference Replication Contract`：

- 保真模式和冲突优先级：一对一复刻、风格迁移或局部一致；明确业务语义保留项。
- 参考稿反向工程：页面壳、品牌/标题、指标/筛选、看板列头、空列、任务卡、标签、按钮、浮层、响应式、滚动/sticky 的组件清单。
- Selector 映射：参考稿 selector / 文本锚点、目标实现 selector、测试 selector、组件文件、状态类和验收批次。
- 动作按钮矩阵：涉及按钮触发弹窗、抽屉、Popover、确认框、Action Modal 或 AI 面板时，写入“动作按钮 → modal 类型 → selector → 状态 → 验收证据”，并标明所属组件族、共用状态和例外原因。
- Computed style 采样清单：页面、视口、主题、状态、selector、关键属性、期望值、当前值、容差和证据入口。
- 分批实现计划：每批包含目标组件、验收方式、截图或 computed style 证据、非目标未改说明；动作按钮与 modal 应作为组件族一次性设计和验收，避免逐按钮返修。

Change `tasks.md` MUST 把参考稿反向工程、selector 映射、动作按钮矩阵、computed style 采样和分批验收作为先行任务。缺少该 Contract 时，UI 参考稿复刻类 Change 不得进入最终实现验收。

---

## Step 4 — UI Explore Gate

`impact.web` 且有 prototype 时，无 `--strategy` 且非 `--skip-explore`：选 CSS Port / DS / Asset，写入 design.md D1。

---

## Step 5 — 创建 Change（CLI）

```bash
openspec new change "<change-id>"
openspec status --change "<change-id>" --json
```

---

## Step 6 — 生成 Artifacts

```bash
openspec instructions <artifact-id> --change "<change-id>" --json
```

按 schema 顺序写 proposal、design、specs、tasks。OpenSpec CLI 返回的英文 instruction 和 template 只作为结构参考，不得原样复制英文脚手架标题到项目文档。

### Step 6.1 — OpenSpec CLI 模板标题中文化（MUST）

生成或补齐 Change 文档时，MUST 将 CLI 模板标题替换为项目中文标题：

| 文件 | CLI 标题 | 项目标题 |
|---|---|---|
| `proposal.md` | `Why` | `背景` |
| `proposal.md` | `What Changes` | `变更内容` |
| `proposal.md` | `Capabilities` | `能力影响` |
| `proposal.md` | `New Capabilities` | `新增能力` |
| `proposal.md` | `Modified Capabilities` | `修改能力` |
| `proposal.md` | `Impact` | `影响范围` |
| `design.md` | `Context` | `背景与现状` |
| `design.md` | `Goals` / `Non-Goals` | `目标` / `非目标` |
| `design.md` | `Proposed Design` | `设计方案` |
| `design.md` | `Data and API` | `数据与 API` |
| `design.md` | `Risks` / `Rollback Plan` | `风险` / `回滚方案` |
| `tasks.md` | `Implementation` / `Testing` / `Documentation` | `实施任务` / `验证任务` / `文档同步` |

- MODIFIED spec 的 `Requirement:` 标题必须与 `openspec/specs/` 既有能力标题一致；OpenSpec 关键字、命令、路径、API 字段和代码标识可保留英文。
- 若 CLI template 中出现 HTML 注释、尖括号占位符或英文说明，写入项目前必须改写为当前 REQ 的中文事实，不得保留占位解释。
- 生成后必须运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`，确保当前 Change 不残留英文脚手架标题。

---

## Step 7 — 追溯

更新 REQ `trace.md`：

```yaml
openspec_changes:
  - change_id: …
    type: fix
    status: proposed
```

创建 `openspec/changes/<id>/trace.md`（UI 类含 PNG checklist）。新建 trace frontmatter MUST 固化 execution schema v1，最小模板如下：

```yaml
execution:
  schema_version: 1
  started_at: null
  completed_at: null
  last_event: req.opsx
```

- `schema_version` MUST 为数字 `1`，不得写成字符串或省略。
- `/req-opsx` 创建 Change 时只声明 schema 与创建事件，不把 `started_at` 伪造为实施启动时间；后续 `/opsx-apply` 的 Workflow Sync 会在 `opsx.start` / `opsx.apply` 中维护实际启动、完成与最后事件。
- 已存在 `execution` frontmatter 时，MUST 保留有效 `started_at`、`completed_at` 和 `last_event`，只补齐缺失的 `schema_version: 1`；不得批量重写历史终态。

---

## Step 7.5 — 当前 Change 中文校验与残留分离报告（MUST）

成功生成或确认 Change 文档后，MUST 运行当前 Change 聚焦中文优先校验，并输出全仓残留分离报告：

```bash
python scripts/validate-openspec-language.py --change <change-id> --residual-report
```

- 当前 Change 校验失败时，MUST 修复当前 Change 文档并重跑，退出码为失败时不得结束 `/req-opsx`。
- 其他 active Change 的中文残留只作为“全仓残留分离报告”输出，不得混入当前 REQ → Change 链路的失败结论。
- 若残留报告存在非当前 Change 问题，最终「执行链路复盘」可标记为 warning，并给出聚焦治理建议；默认不得自动修改无关 Change 或创建 follow-up Issue/Change。

---

## Step 8 — 输出

```text
## Req → OpenSpec 完成
**REQ:** …
**Change:** …
**Next:** `/opsx-apply <REQ-full-id>` 或 `/sprint-apply sprint-xxx`
```

---

## Guardrails

| 规则 | 说明 |
|------|------|
| 仅 in_sprint | 已评审但未纳入 Sprint 时先 `/sprint-propose --req <REQ-full-id>` |
| 不替代 req-complete | 文档不全先 complete |
| 不跳过 CLI | 禁止手写 change 目录 |
| 不写 src | 实现用 opsx-apply |

---

## 参考

- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`、`opsx-archive.md`、`opsx-explore.md`
- 归档样例：`openspec/archive/`

---

## 当前态看板索引（MUST）

成功创建或确认 REQ 对应 OpenSpec Change 后，MUST 在 `issues/requirements/CHANGELOG.md` 更新对应 REQ 当前态行，并记录关联 Sprint、Change、下一步和事实源路径。看板索引不替代 REQ `trace.md`、Change trace 或 Sprint scope。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.opsx --req <REQ-id> --change <change-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
- Workflow Sync 成功后仍 MUST 确认 Step 7.5 的当前 Change 聚焦中文校验已通过；全仓残留分离报告只影响复盘 warning 与后续治理建议，不阻断当前 Change。

## Change 身份门禁

遵循 `rules/document-governance.md` 的“Change 身份唯一性”：新建前运行 `python scripts/validate-change-identity.py --new-id <change-id>`；复用活动 Change 或归档前运行 `python scripts/validate-change-identity.py`。失败时先处理冲突，不得复用已归档 ID 或按日期自动取最新。

## 中文标题生成门禁

本次生成或重生成的所有 Markdown 必须包含中文业务 Frontmatter `title` 与一致的唯一一级标题，辅助文档标题包含业务主题及用途；不得只有 ID、英文模板或文档类别。Issue 主文档的业务 title 同步注册表，Change proposal 标题不得覆盖 Issue 标题。保留 OpenSpec 解析关键字。

在完成态 Workflow Sync 之前，对本次产物执行 `python scripts/validate-document-titles.py` 并传入明确文件路径或当前 `--req` / `--bug` / `--change`；失败先修正，不宣称完成、不推进状态。不批量修复无关历史文档。
