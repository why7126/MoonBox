---
updated_at: 2026-10-23 08:31:02
name: workflow-sync
description: Sync REQ/BUG/Sprint/OpenSpec workflow status after req/bug/sprint/opsx commands
---

# workflow-sync

## Governance Feedback Loop

按 `docs/standards/governance-feedback-loop.md` 执行 `scripts/governance_feedback.py` 的 start → finish/review → plan/decide → evaluate 链路。非只读命令入口开始记录，完成门禁后结束；失败也记录真实结果。AI Usage Hook 自动导入脱敏 provisional 用量，不替代完整运行。

本项目治理范围已有用户明确授权，`rules/governance-feedback-policy.json` 为范围与预算策略；在有效授权下发现证据充分的问题，自动续接 spec-opt、Change/Sprint 门禁和验证，不重复询问同一授权。默认未授权及业务范围仍「未自动创建 Issue/Change」。只读 explore 不落盘；优化任务只记自身成本，不递归优化；精确 Token 不可用时不宣称收益或自动预算通过。主任务状态、优化状态和量化结果分别报告。

`opsx.accept` 用于逐 AC 证据包验收后的状态投影。有验收计划时，Issue `acceptance_status` 仅依据最新证据清单与当前输入就绪判定；`opsx.modify` 不得无故重置仍有效的 passed，`opsx.archive` 不得仅凭目录迁移把待验收改成 passed。具体证据契约见 `docs/standards/opsx-acceptance.md`。

After any workflow command that changes REQ, BUG, Change, or Sprint scope/status, **MUST** run workflow sync.

## 浏览器自主取证（MUST）

浏览器清单超时、单个工具失败或终端 HTTP 探测失败时，先按 `rules/root-cause-evidence.md` §5.0 检查现有标签页、直接连接浏览器窗口并尝试可行替代入口；区分旧页面展示和当前服务连通性，完成这些检查后才判断是否无法访问。

测试、验收、BUG 补证或问题排查需要产品运行态证据时，Agent 可在已有权限与任务范围内直接通过浏览器访问产品并取证，优先复用 Codex 侧边浏览器中与任务相关的产品标签页，无需人工二次确认；该入口不可用或不能取得所需证据时，使用已提供的其他浏览器或等价自动化工具，Firefox 作为后备。只有无法访问、权限不足、操作超出已授权边界，或自主取证后关键证据仍不足时，才请用户补证，并说明已尝试路径与具体缺口。证据脱敏、不可逆操作和存放边界遵循 `rules/root-cause-evidence.md` 第 5 节。

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

## Command Execution Review Hook（MUST）

After every workflow command finishes its main work, validation, Workflow Sync, and AI Usage hook when applicable, the final user-facing output MUST include a compact execution review:

```text
执行链路复盘：
- 链路状态：正常 / warning / blocked
- 问题证据：无 / <脚本输出、文件路径、校验报告、日志摘要或用户证据>
- 规范优化建议：无明显优化点 / <建议命令或建议 capture 文案>
- follow-up 状态：未自动创建 Issue/Change
```

Rules:

1. 链路状态 MUST be derived from evidence, not guessing. Use `正常` only when required validations and workflow hooks passed or were explicitly not applicable. Use `warning` when non-blocking gaps, skipped optional hooks, stale evidence, or partial validation remain. Use `blocked` when a required gate fails or missing user evidence prevents root-cause or acceptance confirmation.
2. 问题证据 MUST cite concrete evidence such as script exit summaries, focused file paths, validation reports, relevant log excerpts, screenshots, UI acceptance evidence, or user-supplied evidence. If no issue is observed, write `无`.
3. 规范优化建议 MUST be based on the actual execution chain. If no reusable rule, script, template, or skill improvement is supported by evidence, write `无明显优化点`.
4. The hook MUST NOT automatically create a follow-up REQ/BUG/Change. When a follow-up seems useful, output the suggested command or capture text and state `未自动创建 Issue/Change`. Continue only after explicit user authorization.
5. Do not print full logs, full hook JSON, raw session input, local absolute paths, secrets, `.env` content, or broad tool output bodies on the success path.

Session input discovery:

- Prefer explicit `--session-jsonl <local-session.jsonl>` when available.
- Otherwise the hook checks `AI_USAGE_SESSION_JSONL`, then `CODEX_SESSION_JSONL`.
- If neither explicit nor environment session input is available, the hook scans `AI_USAGE_SESSIONS_DIR` when set, otherwise the default local Codex sessions directory `~/.codex/sessions`, and matches recent JSONL files by workflow event, REQ/BUG, Change, Sprint, release, or slash-command terms.
- Normal workflow commands MUST try local automatic discovery before stating `usage_mode: unavailable`; missing session input is a warning path, not the first assumption.
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
- 有 acceptance-plan 的 `opsx.apply` / `opsx.modify`：按当前指纹、证据和就绪结论派生状态；保留仍有效的 passed。仅无新计划的历史链路沿用 pending 兼容策略。
- `opsx.archive` / `sprint.archive`：有计划时仅投影已经有效签认的证据结论；无计划的历史链路按原交付证据门禁回填，不以目录迁移本身伪造 passed。记录 source Change/Sprint。
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
3. Do **not** hand-edit `sprint.md` workflow-sync marker blocks; use the script.
4. Marker blocks include `<!-- workflow-sync:scope-*:start/end -->` and `<!-- workflow-sync:sprint-*-section:start/end -->`.
5. Scope 表 archived 时间与 §里程碑「目标日期」MUST 为 `YYYY-MM-DD HH:mm:ss` 且时分秒 MUST 非 `00:00:00`（见 `rules/document-governance.md` §6.1）。
6. §Sprint 目标、§工作量与容量、§里程碑、§风险与缓冲、§知识库承接均在 Sprint sync 范围；纳入 REQ/BUG/Change 或 Change 状态变化时 MUST 通过 Workflow Sync 更新目标编号列表、`### xxx 要点`、Scope 主表和规划派生章节。
7. Issue `trace.md` 的 `## 变更记录` MUST 保持表头紧跟章节标题；若历史记录行出现在表头前，脚本 SHOULD 自动归一化并在报告中体现 delta。
8. `/opsx-apply` 前 MUST confirm linked REQ/BUG is in a `sprint-xxx`; `--sprint auto` unresolved means do not run apply.

## Refreshed artifacts

- `iterations/<sprint>/sprint.md` Sprint 目标、Scope tables、工作量与容量、里程碑、风险与缓冲、知识库承接 + note；§里程碑「目标日期」列 legacy 仅日期 → `YYYY-MM-DD HH:mm:ss`
- `iterations/<sprint>/acceptance-report.md` issue status lines + note
- `iterations/<sprint>/release-note.md` publish status
- `issues/requirements|bugs/*/trace.md` status + iteration + `openspec_changes[].status`（Frontmatter 与 fenced `yaml` 块均需同步）+ `## 变更记录` workflow event 行 / 表格格式归一化
- `issues/requirements|bugs/*/{requirement.md,bug.md,acceptance.md}` 中可安全同步的主状态与验收回填
- parent requirement `trace.md` related bug index
- `issues/requirements/_registry.yaml` / `issues/bugs/_registry.yaml`
- `issues/requirements/CHANGELOG.md` / `issues/bugs/CHANGELOG.md` 当前态看板行（capture、generate、complete、review、sprint.include、opsx.create、apply.done、archive.done、status.sync、trace.fix 后更新对应 Issue 快照）
- 写入时自动维护 Frontmatter `created_at` / `updated_at`（`rules/document-governance.md` §2.4）
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

分级同步遵循 `rules/document-governance.md` 的“Issue 分级元数据”；聚焦同步前校验合法值，trace 优先，更新已有镜像与注册表，保留正文历史；缺失或非法值报告错误。

## 执行生命周期事件

opsx.start和opsx.progress为Change事件，同样要求Sprint范围与Issue门禁。execution.schema_version=1保存started_at、completed_at、last_event，区分启动、进度、完成。opsx.apply只在完成门禁通过后调用；CLI校验任务全完成。先写Change执行事实，再重放Issue/Sprint投影；重复操作幂等，旧终态兼容，CLI不伪造界面行为事件。启动同步不执行AI Usage完成Hook。

## 面向用户的表达

面向用户的输出遵循 `rules/language.md` 的“产品经理视角沟通”：先讲业务结果和用户影响，优先日常语言，必要技术术语随文解释；决策说明体验、成本、时间和风险。
