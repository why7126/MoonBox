---
name: "opsx-apply"
description: "Implement tasks from an OpenSpec change"
---

# opsx-apply

Use this skill when the user asks to run `/opsx-apply <REQ-full-id|BUG-full-id|change-id>` or implement an OpenSpec change.

## Context Budget Guardrails（MUST）

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
- Workflow Sync 和 AI Usage Post-command Hook MUST 在实现、任务勾选和验证之后串行执行；不得与写同一事实源的步骤并行。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/coding.md
rules/testing.md
rules/security.md
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

## Sprint Inclusion Gate（MUST before implementation）

Before editing `src/`, running implementation checks, or marking any task complete, verify the target Change is eligible for `/opsx-apply`.

For every Change linked to a REQ/BUG:

1. Identify linked `REQ-*` / `BUG-*` from Change trace, proposal/design, tasks, or Issue `trace.md` `openspec_changes[]`.
2. Confirm `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` resolves a Sprint and does not report sprint skipped/unresolved.
3. Read the resolved `iterations/change|archive/<sprint>/sprint.yaml` snippet and confirm:
   - `changes[]` contains `<change-id>`.
   - `requirements[]` contains linked `REQ-*` and/or `bugs[]` contains linked `BUG-*`.
4. Confirm each linked Issue `trace.md` has `iteration: <sprint-id>` and `status: in_sprint` or a later delivery state.

If any check fails, **BLOCKED**: do not implement. Tell the user to run `/sprint-propose` to include the REQ/BUG/Change in a `sprint-xxx`, then rerun `/opsx-apply`.

A resolved `sprint.yaml` with `status: planning` is eligible. Planning means `/sprint-propose` has created the official Sprint scope; it MUST NOT be treated as “Sprint not started” when the Issue trace is already `in_sprint` and the Sprint contains the linked Change.

Only a Change with no linked REQ/BUG may bypass this gate; output the reason explicitly.

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

1. Before editing UI implementation, read only the focused prototype context/HTML, Change `design.md` UI Skeleton, linked REQ `acceptance.md` AC-PROTOTYPE section, and matched best-practice `prototype-driven-ui-gate.md`.
2. Confirm `tasks.md` has an explicit UI Skeleton task before detailed UI implementation tasks. If absent, update `tasks.md` first and keep it unchecked until the skeleton exists.
3. Build the UI Skeleton first: route/page shell, layout regions, component slots, state containers, stable selectors, loading/empty/error/disabled states, and placeholder data boundaries.
4. Do not mark UI implementation tasks complete until a 1440px desktop viewport visual acceptance has been run with Playwright/browser or an equivalent project-approved visual check.
5. Record the 1440px evidence in Change `trace.md` or `acceptance.md`: command/tool, viewport, inspected path, screenshot/evidence path when available, pass/fail summary, and known exceptions.
6. If 1440px acceptance fails, keep the task unchecked and continue through `/opsx-modify` or focused fixes inside the same Change.

Report:

```text
Prototype Gate: pass|warn|blocked
UI Skeleton: done|missing|n/a
1440px visual acceptance: pass|fail|pending|n/a
REQ final consistency: pending archive check
```

BLOCKED if a prototype-backed UI task is about to be completed without UI Skeleton evidence or 1440px visual acceptance evidence.

## Implementation Loop

For each pending task:

1. Announce current task.
2. Make minimal scoped changes.
3. Add/update tests when behavior changes.
4. Mark task `- [ ]` → `- [x]` immediately after completion.
5. Re-run focused checks/tests.
6. Stop and ask if task is ambiguous, gate is blocked, or implementation reveals design conflict.

## Completion Output

Report change id, schema, completed tasks this session, total progress, tests/checks run, remaining tasks, and whether archive is ready.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Final Step — Workflow Sync（MUST）

Run:

```bash
python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto
```

- Exit code MUST be `0`。
- Print summary Workflow Sync Report；use `--output detail` only for debugging。
- Verify linked REQ/BUG trace has `openspec_changes[].status: applied` and `/opsx-apply` in `## 变更记录`; if missing, fix workflow sync and rerun instead of hand-editing marker blocks.
- Do not hand-edit workflow-sync marker blocks。
