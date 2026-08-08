---
name: "sprint-archive"
description: "批量归档 Sprint 内 OpenSpec Change 并关闭迭代"
---

# sprint-archive

Use when the user asks `/sprint-archive <sprint-id>` or wants to close a Sprint.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- Start from `sprint.yaml`; do not full-read Sprint four-piece unless closing fields are needed.
- For each Change, read only `tasks.md`, trace/status, and delta headings.
- Reuse `.agents/skills/opsx-archive/SKILL.md`; do not duplicate full archive reasoning.
- `--dry-run` must stop after queue/readiness report.

## Input

- `<sprint-id>` preferred; if omitted, infer only when one active Sprint exists.
- Flags: `--dry-run`、`--change <change-id>`、`--force`、`--skip-sync`（不推荐）、`--no-sprint-close`。

## Command Order（MUST）

- `/sprint-archive` 位于 Sprint 内所有 `/opsx-archive` 完成之后；仍有 active Change、未关闭 Issue 或 archive evidence 缺失时不得关闭 Sprint。
- Sprint close 前 MUST 先完成 AI Usage Snapshot Gate，再执行目录/env/陈旧扫描、Sprint 四件套关闭、Workflow Sync。
- 归档单个 Change、关闭 Sprint、Issue promote、Workflow Sync 和 AI Usage 相关快照 MUST 严格串行执行。
- Sprint 完成后才进入发布链路：`/release-propose` → `/release-prepare` → `/usage-docs-*` → `/image-prepare` → `/image-build` → `/release-publish`。

## Must Read / Run

```text
AGENTS.md
rules/document-governance.md
rules/directory-structure.md
rules/iterations-lifecycle.md
.agents/skills/opsx-archive/SKILL.md
.agents/skills/workflow-sync/SKILL.md
iterations/change/<sprint-id>/sprint.yaml
iterations/change/<sprint-id>/sprint.md（依赖/Scope 片段）
```

```bash
openspec list --json
python scripts/validate-sprint-archive-readiness.py --sprint <sprint-id>
python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary
```

For single change mode:

```bash
python scripts/validate-sprint-archive-readiness.py --sprint <sprint-id> --change <change-id>
```

Readiness distinguishes active and archived Change semantics: active Changes are checked for directory/tasks completion; archived Changes are additionally checked for `trace.md`. If an archived Change lacks `trace.md`, `proposal.md`、`design.md` or `tasks.md` MUST contain a complete `## 归档验证摘要` covering validation command/result, acceptance verdict, Issue/Sprint status, and archive path/time evidence.

Before any issue package is moved to `issues/**/archive/`, the promote step MUST pass the issue subdocument status gate:

```bash
python scripts/promote-issues-for-archive.py --sprint <sprint-id>
```

If scoped REQ/BUG child Markdown files still contain non-closed frontmatter or fenced YAML `status` values such as `draft`、`pending_review`、`in_sprint`、`applied`、`todo`、`open`, keep the Sprint close blocked until those documents are reconciled.

If readiness returns non-zero or `Verdict: BLOCKED`, stop unless user explicitly passed `--force` and confirms each blocker.

Local real env files (`.env`、`.env.*`、`deploy/**/*.env`、`scripts/build-images.env`) may exist for deployment acceptance. They MUST NOT block Sprint archive by existence alone when covered by Git ignore policy; block only if they are tracked/staged, not ignored, copied into governed artifacts, or leaked in output/docs.

## Queue Rules

1. Only archive Change ids listed in `sprint.yaml`.
2. Skip already archived changes and record path.
3. Block by default when tasks/artifacts are incomplete, `tasks.md` is missing, change dir is missing, or MODIFIED title cannot be matched.
4. Sort dependencies as in sprint apply: base `add-*` before dependent `fix-*` / `update-*`; unrelated changes keep `sprint.yaml` order.
5. Output Sprint Archive Queue Report before moving anything.

Queue Report MUST include Sprint, mode, readiness verdict, each change action (`SKIP` / `ARCHIVE NEXT` / `QUEUE` / `BLOCKED`), blockers, and warnings.

## AI Usage Snapshot Gate（MUST before Close Sprint）

Before the final close step, check the Sprint AI usage snapshot through the Fact Sheet:

```bash
python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --json
```

Inspect `ai_usage_snapshot.snapshot_status`、`ai_usage_snapshot.ai_usage_mode`、`generated_at`、`coverage`、`warnings` and `recommended_action`.

- If `snapshot_status: present` and `ai_usage_mode: actual`, output only a compact summary: status, mode, path, generated_at, coverage status and warning_count.
- If snapshot is `missing`、`stale` or `failed`, try to generate/refresh it only when the operator provides a local session input, using:

```bash
python scripts/extract-ai-usage.py --session-jsonl <local-session.jsonl> --sprint <sprint-id> --json
```

- If local session input is unavailable or generation fails, continue only with an explicit warning in the close report: `ai_usage_mode: estimated_fallback`, reason, impact, and recommended_action. Do not state that real token usage was used.
- Do not print raw session JSONL, prompts, system/developer instructions, local absolute paths, tool output bodies, or full snapshot contents.

## Archive Loop

For each `ARCHIVE NEXT`:

1. Execute `/opsx-archive` equivalent using `.agents/skills/opsx-archive/SKILL.md`.
2. Prefer `openspec archive "<change-id>" -y`; use manual fallback only with delta self-check.
3. Stop the whole Sprint archive on title mismatch, archive target conflict, failed sync/promote script, or user interruption.

## Close Sprint

Unless `--no-sprint-close`, close only when all Sprint changes are archived and readiness passes without `--force`:

```bash
python scripts/validate-sprint-archive-readiness.py --sprint <sprint-id>
python scripts/validate-env-ignore-policy.py
python scripts/check-sprint-close-stale-scan.py --sprint <sprint-id>
```

Then update the four-piece as needed:

```text
sprint.yaml: status completed, lifecycle_stage archive
acceptance-report.md: final verdict/date/check summary
release-note.md: draft -> published if applicable
sprint.md: closure note only outside workflow-sync marker blocks
```

Move directory with `git mv iterations/change/<sprint-id> iterations/archive/<sprint-id>`.

## Final Step — Workflow Sync（MUST）

```bash
python scripts/sync-workflow-status.py --event sprint.archive --sprint <sprint-id>
```

Exit code MUST be `0`; print summary Workflow Sync Report; use `--output detail` only for debugging.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report archived/skipped/blocked counts, Sprint close status, updated files, validation commands, and exact retry command if paused.
