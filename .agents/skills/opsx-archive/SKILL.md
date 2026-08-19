---
name: "opsx-archive"
description: "Archive a completed OpenSpec change"
---

# opsx-archive

Use when the user asks `/opsx-archive <REQ-full-id|BUG-full-id|change-id>` or wants to archive one OpenSpec change.

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

- 归档复核优先 `openspec status`、`tasks.md` checkbox、delta spec heading 与 sync/promote 报告摘要；不得为归档全量读取 active/archived specs。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- Read focused artifacts only: `tasks.md`, delta spec headings, related trace/status snippets.
- Do not full-read `issues/**`, `iterations/**`, or all `openspec/specs/**`; use `rg -n "^### Requirement:|^### ADDED|^### MODIFIED|^### REMOVED"` then open the relevant sections.
- If a script fails, inspect the named files/snippets from the report instead of broad directory reads.
- Keep command output summarized; include full stdout only for validation reports or failures.

## Input

- `<REQ-full-id>`：来源于 REQ 的 Change，MUST 使用完整 `REQ-xxxx-slug`。
- `<BUG-full-id>`：来源于 BUG 的 Change，MUST 使用完整 `BUG-xxxx-slug`。
- `<change-id>`：仅用于无 REQ/BUG 来源的纯治理 Change。
- If omitted and not uniquely inferable, list active changes from `openspec list --json` and ask; never guess.

## Target Resolution

- `/opsx-archive <REQ-full-id>`：先解析该完整 `REQ-xxxx-slug` 关联的已 applied Change，再归档。
- `/opsx-archive <BUG-full-id>`：先解析该完整 `BUG-xxxx-slug` 关联的已 applied Change，再归档。
- `/opsx-archive <change-id>`：仅在用户明确给出 Change ID，或处理无 REQ/BUG 关联的治理 Change 时使用。
- 后续 `openspec status`、`scripts/archive-change.sh`、Workflow Sync、Issue promote、AI Usage hook 均使用解析后的真实 `<change-id>`。

## Command Order（MUST）

- `/opsx-archive` MUST 位于 `/opsx-apply` 和必要的 `/opsx-modify` 之后；任务未完成、验证未过或文档同步未完成时不得归档。
- 后续参数 MUST 延续来源：REQ 来源用 `/opsx-archive <REQ-full-id>`，BUG 来源用 `/opsx-archive <BUG-full-id>`，纯治理 Change 才用 `/opsx-archive <change-id>`。
- 目录校验、归档移动、Workflow Sync、Issue promote 和 AI Usage Post-command Hook MUST 严格串行执行，不得并行。
- 归档目录 MUST 为 `openspec/archive/YYYY-MM-DD-<change-id>/`；不得写入 `openspec/changes/archive/`。

## Must Read / Run

```text
AGENTS.md
openspec/project.md
rules/document-governance.md
rules/directory-structure.md
rules/issues-lifecycle.md
.agents/skills/workflow-sync/SKILL.md
openspec/changes/<change-id>/tasks.md
openspec/changes/<change-id>/trace.md（存在时）
```

```bash
openspec status --change "<change-id>" --json
```

## Gates

| Gate | Default |
|---|---|
| Artifact status | incomplete => warn + require explicit user confirmation |
| Task status | `- [ ]` exists => warn + require explicit user confirmation |
| Delta spec | if `specs/` exists, assess ADDED/MODIFIED/REMOVED before moving |
| MODIFIED title | matching `openspec/specs/<capability>/spec.md` requirement title MUST exist |
| Documentation sync | before archive, affected long-lived docs / README / `.env.example` / API index / DB design / Orval notes / release or deployment docs MUST be checked and updated or explicitly marked not applicable |
| Prototype final consistency | if linked REQ or Change has `prototype/**`, `prototype_refs`, `AC-PROTOTYPE-*`, or UI Skeleton, linked REQ `requirement.md` / `acceptance.md` / `trace.md` MUST match final Change design, implementation evidence and 1440px visual acceptance |
| Archive target | `openspec/archive/YYYY-MM-DD-<change-id>/` MUST NOT already exist |
| Legacy archive root | `openspec/changes/archive/` MUST NOT exist before or after archive; if present, stop and migrate its children to `openspec/archive/` first |
| Archive evidence | if a historical archived Change lacks `trace.md`, it MUST contain a complete `## 归档验证摘要` fallback in proposal/design/tasks before Sprint close readiness can pass |
| Local env files | gitignored real env files may exist locally and MUST NOT block archive by existence alone; block only if tracked/staged, not ignored by policy, copied into governed artifacts, or leaked in command output/docs |

## Steps

1. Resolve change and verify active directory exists.
   - Also verify `openspec/changes/archive/` does not exist as a real directory. Compatibility references in scripts/tests are allowed; the filesystem path is not.
2. Count tasks and artifact status; stop on incomplete items unless user confirms.
3. Assess delta specs:
   - no delta specs => archive as metadata-only change;
   - delta exists => summarize capability, operation type, and affected Requirement titles;
   - prefer `scripts/archive-change.sh "<change-id>"` so OpenSpec CLI output is normalized to canonical `openspec/archive/` and legacy `openspec/changes/archive/` is migrated/blocked.
4. Before moving or merging the Change, complete documentation sync:
   - inspect `tasks.md`, `trace.md`, delta spec headings, and implementation notes to identify affected docs;
   - update required long-lived docs according to `rules/document-governance.md` and task-specific rules, including `docs/03-api-index.md` / Orval notes for API changes, `docs/04-database-design.md` for DB changes, deployment / release docs and `.env.example` for environment or Docker changes, and README or compatibility docs when affected;
   - do not read, print, copy, or archive real env file contents; local `.env`、`.env.*`、`deploy/**/*.env`、`scripts/build-images.env` are allowed to exist when Git ignore policy covers them;
   - if no documentation update is required, record the reason in the archive output; do not silently skip this gate.
   - for prototype-backed UI Changes, run the REQ Final Consistency Check before archive:
     - compare linked REQ `requirement.md`, `acceptance.md` AC-PROTOTYPE / AC-XCUT, `trace.md prototype_gate`, Change `design.md` UI Skeleton, Change `trace.md` evidence, and final 1440px visual acceptance result;
     - update REQ docs and Change trace when wording, non-goals, UI behavior, visual evidence, or acceptance status drift from implementation;
     - BLOCK archive if 1440px evidence is missing, failed, stale after `/opsx-modify`, or if REQ docs still describe obsolete prototype behavior.
5. If the wrapper fails because OpenSpec CLI is unavailable, manual fallback is allowed only after delta self-check:
   - merge delta into `openspec/specs/` according to OpenSpec semantics;
   - move to `openspec/archive/YYYY-MM-DD-<change-id>/`.
6. Update related issue/change trace only through workflow sync/promote scripts where possible.

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Steps（MUST）

Run these commands strictly sequentially. Do not use parallel execution or `multi_tool_use.parallel` for directory validation, Workflow Sync and issue promotion: each step depends on the files written by the previous step, and issue promotion depends on the files written by Workflow Sync.

```bash
python scripts/validate-directory-structure.py
python scripts/validate-env-ignore-policy.py
python scripts/validate-archive-evidence.py --change <change-id> --archive-path openspec/archive/YYYY-MM-DD-<change-id>
python scripts/sync-workflow-status.py --event opsx.archive --change <change-id> --sprint auto
python scripts/promote-issues-for-archive.py --change <change-id> --reason "/opsx-archive <change-id>"
```

- All exit codes MUST be `0`.
- Directory validation MUST fail if `openspec/changes/archive/` exists. Do not continue by treating it as a historical archive location; migrate to `openspec/archive/` first.
- Env ignore validation MUST fail if real env file patterns are not ignored or env examples are accidentally ignored. It MUST NOT fail solely because ignored real env files exist locally.
- Archive evidence validation MUST pass. If an archived Change lacks `trace.md`, the script may generate a minimal trace from completed `tasks.md` and archive path facts; otherwise it requires a complete `## 归档验证摘要` fallback.
- Print summary Workflow Sync Report and Promote Issue Stage report; use `--output detail` only for debugging.
- `promote-issues-for-archive.py` includes the issue subdocument status gate. If it reports `Issue Subdocument Status Gate` blockers, stop and reconcile the listed child Markdown `status` values before retrying; do not move REQ/BUG packages to `archive/` with residual `draft`、`pending_review`、`in_sprint`、`applied`、`todo`、`open` or equivalent non-closed states.
- Single REQ/BUG promote after `/opsx-archive <change-id>` MUST NOT be blocked solely because the containing Sprint is still planning/in_progress. Sprint completion remains a `/sprint-archive` gate, not a single Issue archive gate.
- Do not hand-edit `sprint.md` workflow-sync marker blocks.

## 当前态看板索引（MUST）

若归档 Change 来源于 REQ 或 BUG，Workflow Sync 与 Issue promote 成功后 MUST 分别在 `issues/requirements/CHANGELOG.md` 或 `issues/bugs/CHANGELOG.md` 更新对应 Issue 当前态行。若本次只修复历史状态漂移或路径迁移，当前态行 SHOULD 同步更新状态、阶段、事实源路径和最近更新时间。

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync and issue promotion exit with code `0`, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.archive --change <change-id> --sprint <resolved-sprint-id> [--req <linked-REQ-id>] [--bug <linked-BUG-id>] --json
```

- If the archived change has `source_requirement` / `source_bug` or an issue trace link, pass the linked REQ/BUG explicitly. The extractor must also enrich `opsx.archive` from active or archived change trace/proposal and issue traces before writing usage facts.
- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- Use the Sprint resolved by Workflow Sync; do not pass the literal value `auto` to `extract-ai-usage.py`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report change id, archive path, documentation sync status, spec sync status, warnings/confirmations, scripts run, promoted issues, and next step.
