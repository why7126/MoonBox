---
name: workflow-sync
description: Sync REQ/BUG/Sprint/OpenSpec workflow status after req/bug/sprint/opsx commands
---

# workflow-sync

After any workflow command that changes REQ, BUG, Change, or Sprint scope/status, **MUST** run workflow sync.

## Command

```bash
python scripts/sync-workflow-status.py \
  --event <event> \
  [--sprint auto|sprint-xxx] \
  [--change <change-id>] \
  [--req <REQ-id>] \
  [--bug <BUG-id>]
```

## AI Usage Post-command Hook（MUST after successful workflow sync）

After a `/req-*`, `/bug-*`, `/opsx-*`, or `/sprint-*` workflow command finishes its main work and the Workflow Sync command above exits with code `0`, run the unified AI usage hook or report why it is skipped:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event <event> \
  [--req <REQ-id>] \
  [--bug <BUG-id>] \
  [--change <change-id>] \
  [--sprint <sprint-id>] \
  [--session-jsonl <local-session.jsonl>] \
  --json
```

Rules:

1. The hook is best-effort for normal workflow commands. If session input is unavailable, print the short `usage_mode: unavailable` summary and recommended action; do not fail the parent command.
2. If the command has no Sprint scope, command-run generation may proceed, but Sprint snapshot output MUST be `skipped`; do not invent a Sprint.
3. If one command run fails persistence safety checks, the hook MUST skip that record, report `unsafe-records-skipped:<count>`, and continue writing any safe records. If all target records are unsafe, report `usage_mode: unavailable` and `no-safe-command-runs`; do not raise an unhandled exception.
4. Workflow IDs containing business words such as `password` or `token` MUST NOT be treated as secrets by word match alone. Only auth headers, assigned secret-like fields, `.env` content, raw local absolute paths, and equivalent sensitive values should block persistence.
5. Successful standard workflow hook output MUST stay compact and user-facing summaries MUST include only: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
   - Release workflow hooks MAY also include `session_input` and `release_artifact` because release commands maintain a version-level AI usage artifact.
   - Do not print full hook JSON, `outputs`, raw `warnings`, command-run detail files, Sprint snapshot contents, session JSONL, prompts, skill bodies, local absolute paths, or tool output bodies on the success path.
6. The hook MUST NOT persist prompt text, system/developer instructions, skill bodies, raw session JSONL, local absolute paths, tool output bodies, secrets, cookies, Authorization headers, or `.env` content.
7. Exploration commands with no workflow state change MAY run the hook in `--dry-run` mode or output the same recommended action; they MUST NOT modify REQ/BUG/Change/Sprint status just to create usage data.

Session input discovery:

- Prefer explicit `--session-jsonl <local-session.jsonl>` when available.
- Otherwise the hook checks `AI_USAGE_SESSION_JSONL`, then `CODEX_SESSION_JSONL`.
- Raw session files remain local-only and MUST NOT be copied into the repository.
- Do not pass a known-missing `--session-jsonl` merely to produce a non-failing hook summary; `session-jsonl-not-found` is diagnostic fallback, not evidence that usage data was generated.
- For historical backfill or audit, do not rely on automatic session discovery. Use explicit `--session-jsonl` and, when the historical turn text cannot be classified into canonical REQ/BUG, Change, Sprint, or workflow event, provide a `--manual-map` keyed by `turn_hash`.
- Snapshot freshness checks should pass timezone-aware ISO timestamps such as `2026-07-15T05:20:00Z`; avoid naive local times unless the caller has confirmed the script's timezone interpretation.

| Flag | Purpose |
|------|---------|
| `--sprint auto` | Resolve sprint by context (see below) |
| `--sprint none` | Skip sprint-level artifacts; sync issue/trace/registry only |
| `--check` | Fail if derived docs drift (CI) |
| `--dry-run` | Report only, no writes |
| `--scan-issue-subdocuments` | Scan focused Issue child docs for status / acceptance drift |
| `--apply-issue-subdocuments` | Apply safe focused Issue child doc status / acceptance updates |
| `--output summary\|detail` | Report verbosity; default `summary` hides no-delta file lists, `detail` prints every result |

### Sprint resolution (`--sprint auto`)

| Event kind | Resolution |
|------------|------------|
| `req.*` / `bug.*` with `--req` / `--bug` | Sync sprint **only if** that issue is listed in `iterations/<sprint>/sprint.yaml` `requirements` or `bugs`; otherwise skip sprint artifacts and report `_skipped — BUG-xxxx not in sprint scope_` |
| `opsx.*` with `--change` | Sync sprint **only if** that change is in sprint `changes` |
| `sprint.*` | Use explicit sprint or the single `in_progress` sprint |
| No issue/change focus | Fall back to single `in_progress` sprint (legacy default) |

When sprint sync is skipped, the script still updates the target issue `trace.md`, `_registry.yaml`, and parent requirement related-bug index when applicable.

For `opsx.apply`, sprint sync skipped/unresolved is a **blocking precondition failure** for REQ/BUG-sourced changes. The parent command MUST stop before implementation and ask to run `/sprint-propose` first, unless the Change is explicitly documented as a non-REQ/BUG pure technical governance Change.

### Issue subdocument residual status reconcile

When issue archive promotion is blocked by residual `status` fields in issue subdocuments, do not hand-edit files in bulk. Use workflow sync reconcile mode:

```bash
python scripts/sync-workflow-status.py \
  --event req.archive \
  --req REQ-xxxx-slug \
  --sprint auto \
  --reconcile-issue-status-residuals \
  --dry-run
```

```bash
python scripts/sync-workflow-status.py \
  --event req.archive \
  --req REQ-xxxx-slug \
  --sprint auto \
  --reconcile-issue-status-residuals \
  --apply-reconcile
```

Use `--bug BUG-xxxx-slug` and `--event bug.archive` for BUGs.

Guardrails:

1. Always run dry-run first and inspect file path, source, old status, target status, and `updated_at`.
2. Reconcile is only for already-closed issues. If the report says the issue trace or linked Change is not closed, run the upstream workflow command first. A single REQ/BUG may reconcile and promote after all of its linked Changes are archived even when its Sprint is still planning/in_progress; Sprint completion remains a `/sprint-archive` gate.
3. Reconcile MUST NOT be used to bypass review, acceptance, `/opsx-archive`, or `/sprint-archive`.
4. Successful reconcile refreshes modified Markdown `updated_at` and reports changed file/field counts.

### Issue 子文档同步

Workflow Sync 会在聚焦事件中同步 Issue 主文档和验收文档：

- `req.*` / `bug.*`：同步当前 `--req` / `--bug` 的主文档状态。
- `opsx.apply` / `opsx.modify`：将关联 Issue 的 `acceptance.md` 标记为 `acceptance_status: pending`。
- `opsx.archive` / `sprint.archive`：将已闭环 Issue 的验收回填为 `acceptance_status: passed`，并记录 source Change/Sprint。
- 对带 prototype 的 UI Change，`opsx.apply` / `opsx.modify` SHOULD 在关联 Issue `acceptance.md` 或 `trace.md` 中保留 `prototype_gate.visual_acceptance_1440: pending|passed|failed` 与证据入口；`opsx.archive` MUST 在回填前确认 `prototype_gate.req_final_consistency: passed`，否则报告 blocker 而不是静默标记验收通过。
- Workflow Sync 不直接推断视觉通过；它只同步父命令已经记录的 1440px 验收证据和最终一致性状态。缺证据、证据 stale 或 REQ 文档与 Change trace 不一致时，父命令 MUST 先补齐再重跑 sync。
- `--scan-issue-subdocuments` 用于只扫描当前聚焦 Issue；`--apply-issue-subdocuments` 只应用脚本判定为 safe 的同步项。
- 对 `review.md`、`root-cause.md`、`workaround.md` 等语义不明的 `status` 字段，脚本只报告 warning/blocker，不静默改写。

## Event mapping

| Command family | `--event` |
|----------------|-----------|
| capture | `req.capture` 与/或 `bug.capture`（按本次创建的条目分别执行） |
| req-capture | `req.capture` |
| req-generate | `req.generate` |
| req-complete | `req.complete` |
| req-review | `req.review` |
| req-opsx | `req.opsx` |
| bug-capture | `bug.capture` |
| bug-generate | `bug.generate` |
| bug-complete | `bug.complete` |
| bug-review | `bug.review` |
| bug-opsx | `bug.opsx` |
| opsx-propose | `opsx.propose` |
| opsx-apply | `opsx.apply` |
| opsx-modify | `opsx.modify` |
| opsx-archive | `opsx.archive` |
| sprint-propose | `sprint.propose` |
| sprint-apply | `sprint.apply` |
| sprint-archive | `sprint.archive` |

## Guardrails

1. Print only the summary **Workflow Sync Report** from script stdout on the success path. Successful commands SHOULD use the default summary output; rerun with `--output detail` only when diagnosing drift, skipped files, or failures.
2. If exit code != 0, fix drift and re-run before ending the parent command.
3. Do **not** hand-edit `sprint.md` Scope marker blocks; use the script.
4. Marker blocks: `<!-- workflow-sync:scope-*:start/end -->`.
5. Scope 表 archived 时间与 §里程碑「目标日期」MUST 为 `YYYY-MM-DD HH:mm:ss` 且时分秒 MUST 非 `00:00:00`（见 `rules/document-governance.md` §6.1）。
6. §Sprint 目标 不在 sync 范围；纳入 REQ/BUG 时 MUST 同步更新 **编号列表** 与 **`### xxx 要点`** 两处。
7. Issue `trace.md` 的 `## 变更记录` MUST 保持表头紧跟章节标题；若历史记录行出现在表头前，脚本 SHOULD 自动归一化并在报告中体现 delta。
8. `/opsx-apply` 前 MUST confirm linked REQ/BUG is in a `sprint-xxx`; `--sprint auto` unresolved means do not run apply.

## Refreshed artifacts

- `iterations/<sprint>/sprint.md` Scope tables + note；§里程碑「目标日期」列 legacy 仅日期 → `YYYY-MM-DD HH:mm:ss`
- `iterations/<sprint>/acceptance-report.md` issue status lines + note
- `iterations/<sprint>/release-note.md` publish status
- `issues/requirements|bugs/*/trace.md` status + iteration + `openspec_changes[].status`（Frontmatter 与 fenced `yaml` 块均需同步）+ `## 变更记录` workflow event 行 / 表格格式归一化
- `issues/requirements|bugs/*/{requirement.md,bug.md,acceptance.md}` 中可安全同步的主状态与验收回填
- parent requirement `trace.md` related bug index
- `issues/requirements/_registry.yaml` / `issues/bugs/_registry.yaml`
- 写入时自动维护 Frontmatter `created_at` / `updated_at`（`rules/document-governance.md` §2.4）
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。
