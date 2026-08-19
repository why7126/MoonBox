---
name: "opsx-modify"
description: "验收返修：在 OpenSpec Change 已 opsx-apply、未 archive 前，根据验收反馈调整实现并同步文档、验证和 AI Usage"
---

# opsx-modify

Use this skill when the user asks `/opsx-modify <REQ-full-id|BUG-full-id|change-id> <修改内容>` or wants to adjust implementation after `/opsx-apply` during acceptance, before `/opsx-archive`.

## Context Budget Guardrails（MUST）

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，优先摘要复用，不重复全量读取。
- 返修定位先读验收反馈、`tasks.md`、`trace.md`、相关 acceptance 摘要；不要全量重读 Issue、Sprint、archive 或 generated 文件。
- 大 diff 先用 `git diff --stat` / `git diff --name-only`；只展开手写源码、测试和本次文档片段。
- 命令输出优先 `max_output_tokens <= 8000`；测试失败只展开失败用例、关键栈和相关片段。

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

## Input

```text
/opsx-modify <REQ-full-id|BUG-full-id|change-id> <修改内容>
```

Examples:

```text
/opsx-modify add-login-page 登录按钮 hover 色和验收稿不一致，改成金色 token，并补截图验收说明
/opsx-modify REQ-0008-login-page 验收发现移动端标题溢出，修正响应式布局
```

## Scope

`/opsx-modify` 用于 **apply 后、archive 前** 的验收返修。

## Command Order（MUST）

- `/opsx-modify` 只能位于 `/opsx-apply` 之后、`/opsx-archive` 之前；不得用于已归档 Change。
- 返修仍在原 Change 边界内时，继续使用原始完整 `REQ-xxxx-slug` 或 `BUG-xxxx-slug` 参数；纯治理 Change 才使用 `<change-id>`。
- REQ 参数 MUST 是完整 `REQ-xxxx-slug`；BUG 参数 MUST 是完整 `BUG-xxxx-slug`。
- 返修完成后 MUST 先更新 Change 文档、任务返修记录和验证证据，再串行执行 Workflow Sync 与 AI Usage Post-command Hook。
- 若反馈扩大 API、DB、权限、部署、对象存储或产品边界，停止本命令并引导创建新的 REQ/BUG 或 OpenSpec Change。

适用：

- 原验收项未满足。
- 原实现的 UI、API、数据、测试或文档存在偏差。
- 验收反馈仍属于当前 Change 的目标与边界。
- 需要补充二次验证证据和 AI Usage 统计。

不适用：

- 新增原需求未包含的功能。
- 改变新的 API / DB / 权限 / 部署 / 对象存储边界。
- 发现独立缺陷且影响范围超出当前 Change。
- 当前 Change 已 archive。

超出范围时 MUST stop，并建议走 `/req-capture`、`/bug-capture` 或新 OpenSpec Change。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/coding.md
rules/testing.md
rules/security.md
rules/root-cause-evidence.md
rules/document-governance.md
rules/directory-structure.md
rules/requirement-management.md
rules/bug-management.md
rules/iterations-lifecycle.md
.agents/skills/workflow-sync/SKILL.md
```

Resolve target:

- If input is a full `REQ-xxxx-slug` / `BUG-xxxx-slug`, read its `trace.md` and resolve linked `openspec_changes[]`.
- If multiple active Changes match, ask user to choose.
- If target Change is archived, BLOCKED.

Then read focused snippets:

```text
openspec/changes/<change-id>/tasks.md
openspec/changes/<change-id>/trace.md（存在时）
openspec/changes/<change-id>/acceptance.md（存在时）
issues/requirements|bugs/**/<REQ-or-BUG>/acceptance.md
issues/requirements|bugs/**/<REQ-or-BUG>/trace.md
iterations/change|archive/<sprint>/acceptance-report.md
iterations/change|archive/<sprint>/sprint.yaml
```

Run preflight:

```bash
python scripts/sync-workflow-status.py --event opsx.modify --change <change-id> --sprint auto --dry-run
```

If sprint cannot resolve for a REQ/BUG-sourced Change, BLOCKED and ask to fix Sprint trace/scope first.

## Root Cause Evidence Gate（MUST）

- MUST 遵守 `rules/root-cause-evidence.md`。
- 当验收反馈属于“效果不如预期”、UI 视觉偏差、交互异常、API/数据结果不符、测试失败或疑似 BUG 时，MUST 先记录偏差证据：期望、实际、复现条件、影响范围和证据来源。
- 证据不足时，MUST 输出人工补证操作步骤，包括证据名称、为什么需要、操作步骤、需要返回字段、脱敏要求和返回格式；不得直接猜测根因或修复方向。
- BUG 来源 Change 返修前 SHOULD 运行 `python scripts/validate-root-cause-evidence.py --bug <BUG-full-id>`；如果返修反馈改变或推翻原根因，MUST 先更新 linked BUG `root-cause.md` 或输出补证阻塞。

## Workflow

1. **Clarify Feedback**
   - Summarize the acceptance issue in 1-3 bullets.
   - Identify whether it is in-scope for the current Change.
   - Identify affected files and tests.
   - Identify evidence status: `confirmed`、`probable`、`hypothesis` 或 `unknown`; if not `confirmed`, request human evidence before fixing unless there is an explicit P0 workaround reason.
   - UI/visual feedback preflight: if the feedback mentions UI、visual、prototype、截图、标注图、附件、页面状态或关键交互状态, MUST first identify all attached/reference screenshots and build an “附件截图逐项视觉对照表” before implementation.

   附件截图逐项视觉对照表 MUST include:

   | 字段 | 内容 |
   |---|---|
   | 附件/截图编号 | 用户附件、原型截图、实际截图、标注图或历史视觉证据编号 |
   | 页面/状态 | 路由、视口、主题、交互状态、弹窗/浮层/空态/错误态 |
   | 对照对象 | 原型、验收截图、标注区域、当前实现或历史证据 |
   | 期望表现 | 附件或原型表达的目标视觉/交互结果 |
   | 实际表现 | 当前实现、复现截图或已有证据中的表现 |
   | 偏差项 | 间距、字号、颜色、对齐、层级、溢出、文案、图标、状态等 |
   | 检查方式 | 视觉对照、Playwright 截图、computed style、DOM 选择器或人工补证 |
   | 处置结论 | 本次修复、无需修改并说明理由、超出范围、证据不足 |
   | 证据入口 | 截图、trace、style JSON、测试输出或脱敏摘要 |

   If route, viewport, theme, expected screenshot, actual screenshot, key interaction state, selector, or computed style evidence is missing and the deviation cannot be confirmed, BLOCK modification and output focused human evidence steps. Do not mark the root cause as `confirmed` before the table is complete enough to support the conclusion.

2. **Modify Implementation**
   - Make minimal scoped code changes.
   - Add or adjust tests when behavior changes.
   - Do not mark new feature scope as complete under this command.

3. **Update Documents**
   - Documentation update is a **MUST gate**, not optional bookkeeping. Before validation, decide whether the acceptance feedback changes any behavior, UI rule, validation rule, user-visible text, API/DB contract, release note, acceptance criterion, or archive-bound spec wording.
   - Update `openspec/changes/<change-id>/tasks.md` with a `## 验收返修记录` section if absent.
   - Update Change `trace.md` when present with feedback, adjustment, and validation summary.
   - If feedback changes or clarifies acceptance criteria, update the linked Issue `acceptance.md` or BUG acceptance/repro document, preserving frontmatter and refreshing `updated_at`.
   - If feedback changes or clarifies product behavior, UI/UE behavior, boundary, non-goal, validation strategy, or implementation decision while staying within the same Change scope, update the active Change docs such as `proposal.md`, `design.md`, `acceptance.md`, `test-plan.md`, or `implementation/` notes as applicable.
   - If feedback changes archive-bound capability wording, update `openspec/changes/<change-id>/specs/**/spec.md` delta so `/opsx-archive` will merge the corrected behavior into `openspec/specs/`.
   - If feedback changes Sprint-visible scope, acceptance evidence, release note, or user-visible behavior, update `iterations/change|archive/<sprint>/acceptance-report.md`, `sprint.md`, and/or `release-note.md` as applicable. Do not hand-edit workflow-sync marker blocks in `sprint.md`.
   - If feedback changes long-lived API, DB, deployment, compatibility, security, media, or product documentation, update the corresponding `docs/**` file required by `rules/document-governance.md`.
   - Update linked Issue `trace.md` through Workflow Sync rather than hand-editing marker blocks.
   - If docs/spec wording must change but capability boundary is unchanged, update the active Change docs; if boundary changes, BLOCKED and suggest `/req-capture`, `/bug-capture`, or a new OpenSpec Change.
   - Run focused documentation checks after edits: at minimum `openspec validate <change-id> --strict` when active Change docs/specs change, and `git diff --check -- <touched-docs>` for touched Markdown/spec files.

   Documentation decision matrix:

   | Feedback touches | MUST update |
   |---|---|
   | Acceptance wording, pass/fail criteria, or verification evidence | `openspec/changes/<change-id>/tasks.md`, Change `trace.md`, linked Issue `acceptance.md` if criteria changed, Sprint `acceptance-report.md` |
   | Product/UI behavior that should survive archive | Change `design.md` and/or `proposal.md`, `openspec/changes/<change-id>/specs/**/spec.md`, linked Issue `requirement.md` / BUG doc when applicable |
   | User-visible release behavior | Sprint `release-note.md` |
   | Sprint plan, scope notes, risk notes, or implementation notes | Sprint `sprint.md` outside workflow-sync marker blocks |
   | API, DB, deployment, environment, security, media, compatibility, or public product docs | Corresponding `docs/**` file per `rules/document-governance.md` |
   | Pure implementation-only bug with no behavior/spec/docs drift | Still update `tasks.md` + Change `trace.md`; explicitly record “无需更新其他文档” with reason |

   Prototype-driven UI Gate:

   - If the Change has `prototype/**`, `prototype_refs`, `AC-PROTOTYPE-*`, UI Contract, or UI Skeleton in `design.md`, every UI/visual acceptance feedback MUST be checked against the original prototype decomposition, current UI Contract, current UI Skeleton and `docs/standards/prototype-ui-acceptance.md`.
   - If UI/visual acceptance feedback includes user attachments, marked screenshots, prototype screenshots, or actual-page screenshots, the “附件截图逐项视觉对照表” is a MUST preflight gate before code changes; incomplete attachment evidence blocks UI返修 until the user supplies focused evidence.
   - If feedback changes layout, component hierarchy, state behavior, visual priority, responsive breakpoint, copy, icon, permission display, Mock/API boundary, computed style, or interaction implied by prototype, update Change `design.md`, linked REQ `acceptance.md` when criteria changed, and Change `trace.md`.
   - After any UI 返修, rerun 1440px desktop and affected key interaction visual acceptance; record fresh screenshot/evidence, computed style checks for risky points, updated attachment comparison results, and updated Mock/API boundary when impacted. Previous visual evidence is invalid once the relevant UI changed.
   - If feedback reveals the prototype itself is obsolete, record Conflict Resolution in Change `design.md` and update linked REQ docs before validation.

   REQ Subdocument Consistency Sweep:

   - If the target Change is sourced from a full `REQ-xxxx-slug`, before Validate MUST locate the linked REQ directory and check all existing REQ subdocuments/assets for consistency with the post-modify behavior.
   - The sweep MUST cover existing `requirement.md`, business process documents, user story documents, `acceptance.md`, `trace.md`, and `prototype/**` including `prototype.html`, `context.md`, screenshots, or equivalent prototype notes.
   - If the modify changes product behavior, UI/interaction, acceptance wording, Mock/API boundary, prototype intent, business flow, state transition, role/permission path, or user story, update every affected REQ subdocument before completing `/opsx-modify`.
   - If a checked subdocument does not need updates, record “REQ 子文档一致性扫尾检查：无需更新 <items>，原因：...” in Change `tasks.md` `## 验收返修记录` or Change `trace.md`.
   - If the sweep finds drift that remains inside the current Change boundary, BLOCK completion until the relevant REQ subdocuments are updated. If the drift expands the boundary, BLOCK and suggest `/req-capture`, `/bug-capture`, or a new OpenSpec Change.

4. **Validate**
   - Run focused tests/checks for touched areas.
   - Run broader checks when API / DB / UI / deployment / security boundary is touched.
   - Keep validation output summarized.

5. **Workflow Sync**

```bash
python scripts/sync-workflow-status.py --event opsx.modify --change <change-id> --sprint auto
```

- Exit code MUST be `0`.
- Print summary Workflow Sync Report.
- Do not hand-edit workflow-sync marker blocks.

6. **AI Usage（MUST）**

After successful workflow sync, run the post-command hook:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event opsx.modify \
  --change <change-id> \
  --sprint <sprint-id|auto-resolved-id-if-known> \
  --json
```

Rules:

- If session JSONL is unavailable, report the compact `usage_mode: unavailable` summary and recommended action.
- Do not fail `/opsx-modify` solely because AI Usage session input is unavailable.
- Do not persist prompt text, raw session logs, tool outputs, secrets, `.env` content, cookies, tokens, or local absolute paths.

## Completion Output

Report:

```text
Change:
验收反馈:
调整内容:
文档更新:
文档未更新项与原因:
验证:
Workflow Sync:
AI Usage:
是否仍可 archive:
```

输出下一步时，REQ 来源 MUST 使用 `/opsx-archive <REQ-full-id>`，BUG 来源 MUST 使用 `/opsx-archive <BUG-full-id>`；纯治理 Change 才使用 `/opsx-archive <change-id>`。

## Event

Workflow event: `opsx.modify`

This event means “验收返修已同步”，not first implementation and not archive.
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。
## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。
