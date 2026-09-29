---
name: "opsx-apply"
description: "Implement tasks from an OpenSpec change"
updated_at: 2026-09-15 09:13:30
---

# opsx-apply

Use this skill when the user asks to run `/opsx-apply <REQ-full-id|BUG-full-id|change-id>` or implement an OpenSpec change.

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

- 大 diff 先用 `git diff --stat` / `git diff --name-only`；不得默认展开 `src/web/openapi.json`、Orval generated、coverage 或构建产物全文。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- `openspec instructions apply --json` returned `contextFiles` is the default read boundary.
- UI/test定位先 `rg -l` 找文件，再分段读取目标片段。
- 默认排除 generated、node_modules、coverage、dist、archive 大目录。
- best-practices 只读 Cross-cutting Gate 命中的标签文件。
- 完成一组 task 后用 `git diff -- <changed-files>` 或 `tasks.md` 片段复核，避免重复读全部上下文。
- 命令输出优先 `max_output_tokens <= 8000`。

## Input

- `<REQ-full-id>`：来源于 REQ 的 Change，MUST 使用完整 `REQ-xxxx-slug`。
- `<BUG-full-id>`：来源于 BUG 的 Change，MUST 使用完整 `BUG-xxxx-slug`。
- `<change-id>`：仅用于无 REQ/BUG 来源的纯治理 Change。
- Omitted：若上下文唯一可推断则使用；否则列 active changes 并询问。
- `--skip-cross-cutting-gate`：仅 P0 热修可跳过，输出必须说明理由。

## Target Resolution

- `/opsx-apply <REQ-full-id>`：先解析该 REQ 关联的当前 Change，并校验 Sprint scope；用户可执行命令 MUST 保留完整 `REQ-xxxx-slug`。
- `/opsx-apply <BUG-full-id>`：先解析该 BUG 关联的当前 Change，并校验 Sprint scope；用户可执行命令 MUST 保留完整 `BUG-xxxx-slug`。
- `/opsx-apply <change-id>`：仅在用户明确给出 Change ID，或处理无 REQ/BUG 关联的治理 Change 时使用。
- 完成后输出下一步时，REQ 来源使用 `/opsx-archive <REQ-full-id>`，BUG 来源使用 `/opsx-archive <BUG-full-id>`；不要把下一步退回成裸 `<change-id>`，除非 Change 没有关联 Issue。

## Command Order（MUST）

- `/opsx-apply` MUST 位于 `/req-opsx` 或 `/bug-opsx` 之后，并且目标 Change 已纳入 Sprint scope；纯治理 Change 也 MUST 先纳入 Sprint。
- 验收发现返修时，下一步使用 `/opsx-modify <REQ-full-id|BUG-full-id|change-id> <修改内容>`；返修完成并验证后再进入 `/opsx-archive`。
- 后续命令参数 MUST 延续来源：REQ 用完整 `REQ-xxxx-slug`，BUG 用完整 `BUG-xxxx-slug`，纯治理 Change 才用 `<change-id>`。
- 完成态 Workflow Sync 和 AI Usage Post-command Hook MUST 在实现、任务勾选和验证之后串行执行；不得与写同一事实源的步骤并行。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/coding.md
rules/testing.md
rules/security.md
rules/root-cause-evidence.md
rules/directory-structure.md
rules/document-governance.md
rules/requirement-management.md
rules/bug-management.md
rules/iterations-lifecycle.md
.agents/skills/workflow-sync/SKILL.md
```

Then run:

```bash
openspec status --change "<change-id>" --json
openspec instructions apply --change "<change-id>" --json
```

Read every concrete path in `contextFiles`.

When relevant, read focused snippets from:

```text
issues/requirements/<REQ>/acceptance.md + trace.md
issues/bugs/<BUG>/root-cause.md + acceptance.md + trace.md
iterations/change|archive/<sprint>/sprint.md §横切预防清单
docs/knowledge-base/best-practices/<matched>.md
```

## Root Cause Evidence Gate（MUST before BUG implementation）

For every BUG-sourced Change, before editing `src/`, running implementation checks, or marking tasks complete:

1. Read `rules/root-cause-evidence.md` and the linked BUG `root-cause.md`.
2. Run `python scripts/validate-root-cause-evidence.py --bug <BUG-full-id>`.
3. BLOCKED if root cause status is not `confirmed`, evidence chain is missing, or the script exits non-zero.
4. If BLOCKED, output the missing evidence and 人工补证操作步骤; tell the user to补证 or rerun `/bug-complete <BUG-full-id>` before `/opsx-apply`.

REQ-sourced and pure governance Changes MAY report this gate as `n/a` unless the acceptance feedback itself is a defect or effect mismatch.

## Sprint Inclusion Gate（MUST before implementation）

Before editing `src/`, running implementation checks, or marking any task complete, verify the target Change is eligible for `/opsx-apply`.

For every Change linked to a REQ/BUG:

1. Identify linked `REQ-*` / `BUG-*` from Change trace, proposal/design, tasks, or Issue `trace.md` `openspec_changes[]`.
2. Confirm `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` resolves a Sprint and does not report sprint skipped/unresolved.
3. Read the resolved `iterations/change|archive/<sprint>/sprint.yaml` snippet and confirm:
   - `changes[]` contains `<change-id>`.
   - `requirements[]` contains linked `REQ-*` and/or `bugs[]` contains linked `BUG-*`.
4. Confirm each linked Issue `trace.md` has `iteration: <sprint-id>` and `status: in_sprint` or a later delivery state.

If any check fails, do not implement past the gate. Repair already-authorized scope synchronization gaps and recheck where possible; actual missing Sprint inclusion follows `/sprint-propose` and the shared hard-blocker contract.

A resolved `sprint.yaml` with `status: planning` is eligible. Planning means `/sprint-propose` has created the official Sprint scope; it MUST NOT be treated as “Sprint not started” when the Issue trace is already `in_sprint` and the Sprint contains the linked Change.

Pure governance Changes MUST also resolve a Sprint containing the Change in `changes[]`; missing inclusion is blocking. No Issue trace is required when there is no linked REQ/BUG.

## Cross-cutting Apply Gate（MUST before `src/`）

Skip only with `--skip-cross-cutting-gate` and explicit P0/hotfix reason.

Infer tags from trace, proposal/design, change id, and tasks:

| Tag | Trigger | Best-practice |
|---|---|---|
| `admin-list` | 管理端列表、分页、table-card | `admin-list-page-consistency.md` |
| `admin-form` | 表单页、设置页、保存 CTA | `admin-form-page-consistency.md` |
| `admin-modal` | 弹窗 CRUD / modal fix | `admin-modal-width-css-cascade.md` |
| `media-upload` | 图片、视频、Logo、头像上传 | `admin-media-upload-chain.md` |

Report:

```text
Change / Tags / Refs
AC-XCUT: pass|warn|n/a
knowledge_base_refs: pass|warn|n/a
best-practices read: pass|n/a
Verdict: PROCEED | WARN-PROCEED | BLOCKED
```

BLOCKED if add-* UI lacks required cross-cutting AC. Do not edit `src/` until resolved.

## Prototype-driven UI Gate（MUST before completing UI tasks）

For any Change with `prototype/**`, `prototype_refs`, `AC-PROTOTYPE-*`, or UI Skeleton in `design.md`:

1. Before editing UI implementation, read only the focused prototype context/HTML, Change `design.md` UI Contract + UI Skeleton, linked REQ `acceptance.md` AC-PROTOTYPE section, `docs/standards/prototype-ui-acceptance.md`, and matched best-practice `prototype-driven-ui-gate.md`.
2. Confirm `tasks.md` has explicit UI Contract, UI Skeleton and visual evidence tasks before detailed UI implementation tasks. If absent, update `tasks.md` first and keep them unchecked until the evidence exists.
3. Build the UI Skeleton first: route/page shell, layout regions, component slots, state containers, stable selectors, loading/empty/error/disabled states, and placeholder data boundaries; record the first 1440px Skeleton evidence before continuing detailed UI work.
4. Do not mark UI implementation tasks complete until 1440px desktop and required key interaction visual acceptance have been run with Playwright/browser or an equivalent project-approved visual check.
5. Record evidence in Change `trace.md` or `acceptance.md`: command/tool, viewport, inspected path, screenshot/evidence path when available, pass/fail summary, computed style checks for risky visual points, Mock/API boundary, and known exceptions.
6. If visual or computed style acceptance fails, keep the task unchecked and perform evidence-based focused fixes inside the current apply until the required checks pass; follow the shared hard-blocker contract if external input is indispensable.

Report:

```text
Prototype Gate: pass|warn|blocked
UI Skeleton: done|missing|n/a
1440px visual acceptance: pass|fail|pending|n/a
key interaction screenshots: pass|fail|pending|n/a
computed style acceptance: pass|warn|blocked|n/a
Mock/API boundary: declared|missing|n/a
REQ final consistency: pending archive check
```

BLOCKED if a prototype-backed UI task is about to be completed without UI Contract, UI Skeleton evidence, 1440px/required key interaction visual evidence, computed style checks for known risk points, or Mock/API boundary declaration.

## UI Reference Replication Gate（MUST before completing reference-backed UI tasks）

For any Change that references attachment HTML、截图、标注图、既有页面、UI 参考稿 or contains `UI Reference Replication Contract`:

1. Before editing UI implementation, read the focused reference assets, current UI Contract/UI Skeleton, `docs/standards/prototype-ui-acceptance.md`, and the Contract section only.
2. Confirm `design.md` contains fidelity mode, reference source priority, component inventory, selector mapping, action button to modal matrix when applicable, computed style sampling list, implementation batches, non-goals and preserved business semantics.
3. If the Contract is missing or only says “贴近附件”“更现代” without selector/style evidence, update the Change docs first and keep UI implementation tasks unchecked.
4. If action buttons trigger dialogs, drawers, popovers, confirms, Action Modal or AI panel, complete the matrix “动作按钮 → modal 类型 → selector → 状态 → 验收证据” before editing the UI; then implement the related button/modal component family in one pass, including shared visual level, loading/disabled/error/open/close states and evidence.
5. Implement by batches such as shell/layout, brand/title, metrics/filter, Kanban header/empty state, cards/tags, action buttons and modal component family, responsive/sticky. Do not close the whole UI task from a single overall screenshot.
6. For each batch, record screenshot or equivalent evidence plus key computed style values for the mapped selectors.
7. Confirm non-target areas were not changed, especially existing click behavior, data boundary, accessibility state and responsive behavior.

Report `UI Reference Replication Gate: pass|warn|blocked` with completed batch names and remaining evidence.

## 产品数据采集与链路观测门禁（MUST）

Before implementation, if the Change touches API, DB, audit logs, usage events, Task Trace, Web/admin request wrapper, object storage, or Agent Workflow observability, MUST read `docs/standards/product-data-collection-observability.md` and confirm the Change has `product_data_collection_observability` with `status`, `affected_layers`, `reason`, and `validation`.

If the declaration is missing, update the Change governance docs before marking tasks complete. If the declaration says `not_applicable`, the `reason` MUST explain why API, DB, `request_logs`, `usage_events`, Task Trace, and request wrappers are unaffected; "无"、"不涉及" or bare "N/A" is not enough.

## Apply 连续执行契约（MUST）

MUST 读取并遵守 [Apply 连续执行契约](../../../docs/08-command-execution-order.md#apply-连续执行契约)，共用「连续推进」「硬阻塞与停止」「完成门禁」「中断续接」四项规则。每次final前执行中央「停止前决策」，CLI暂停提示不构成独立停止依据；按「行为验收」区分合成与真实证据。阶段进度不结束任务；自检修复留在当前 apply，完成判定和恢复入口均以该事实源为准。

## Implementation Loop

For each pending task:

1. Announce current task.
2. Make minimal scoped changes.
3. Add/update tests when behavior changes.
4. Run focused checks/tests and repair failures inside this apply.
5. Mark task `- [ ]` → `- [x]` only after implementation and required verification pass.
6. Continue to the next eligible task; handle hard blockers and resumption using the shared Apply 连续执行契约.

## Completion Output

Only after the shared 完成门禁 passes, report change id, schema, total progress, verification evidence, documentation and sync results, and archive readiness. For a hard pause, report the blocker evidence and 中断续接 checkpoint without claiming completion.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync（MUST）

仅在共享完成门禁中实现、验证和文档条件满足后运行；部分实现或暂停不得执行 applied 完成同步。随后按 workflow-sync Skill 执行 AI Usage Hook，使用已解析的真实 Sprint。

完成态同步前 MUST 确认 Change 内存在需求中心可识别的交付验证来源。允许的来源包括非空 `acceptance.md`、非空 `verification.md`、`trace.acceptance_refs` 指向的 Change 内 Markdown，或 Change `trace.md` 中非空 `## 验证记录` / `## 验证摘要` / `## 验证结果` / `## 验收记录` / `## 验收结果` / `## Validation Log` / `## 实施与验证记录` 章节。纯治理 Change 不强制生成 `acceptance.md` 或 `verification.md`，但不得只依赖最终回复、治理日志、tasks 全勾或 Workflow Sync 成功作为交付验证来源。

```bash
python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto
```

- Exit code MUST be `0`。
- Print summary Workflow Sync Report；use `--output detail` only for debugging。
- Verify linked REQ/BUG trace has `openspec_changes[].status: applied` and `/opsx-apply` in `## 变更记录`; if missing, fix workflow sync and rerun instead of hand-editing marker blocks.
- Do not hand-edit workflow-sync marker blocks。

## 当前态看板索引（MUST）

若 Change 来源于 REQ 或 BUG，`opsx.apply` Workflow Sync 成功后 MUST 分别在 `issues/requirements/CHANGELOG.md` 或 `issues/bugs/CHANGELOG.md` 更新对应 Issue 当前态行。纯治理 Change 无需维护 Issue 当前态看板，但仍按 `/spec-opt` 或对应命令维护 `docs/spec-logs/CHANGELOG.md`。

## 研发启动与进度同步

实施前根因、Sprint与授权门禁通过后，正式实现前串行执行 `python scripts/sync-workflow-status.py --event opsx.start --change <change-id> --sprint auto`；启动失败先修复，dry-run不算启动。启动事实使0/N进入研发中。每批任务实现和验证后以相同参数执行opsx.progress，不触发完成验收回填。

完成门禁通过后才执行opsx.apply；全勾选不替代完成门禁。重复启动不重置时间，中断保留启动事实，不宣称Agent进程在线。CLI和后端共用执行事实判定，所有写入串行，冲突或中断后重跑修复投影；closed/archived Issue不重开。用户命令保留完整REQ/BUG身份。
