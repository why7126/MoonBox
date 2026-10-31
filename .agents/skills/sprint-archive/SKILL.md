---
name: "sprint-archive"
updated_at: 2026-10-31 15:58:13
description: "批量归档 Sprint 内 OpenSpec Change 并关闭迭代"
---

# sprint-archive

Use when the user asks `/sprint-archive <sprint-id>` or wants to close a Sprint.

## 浏览器自主取证（MUST）

浏览器清单超时、单个工具失败或终端 HTTP 探测失败时，先按 `rules/root-cause-evidence.md` §5.0 检查现有标签页、直接连接浏览器窗口并尝试可行替代入口；区分旧页面展示和当前服务连通性，完成这些检查后才判断是否无法访问。

测试、验收、BUG 补证或问题排查需要产品运行态证据时，Agent 可在已有权限与任务范围内直接通过浏览器访问产品并取证，优先复用 Codex 侧边浏览器中与任务相关的产品标签页，无需人工二次确认；该入口不可用或不能取得所需证据时，使用已提供的其他浏览器或等价自动化工具，Firefox 作为后备。只有无法访问、权限不足、操作超出已授权边界，或自主取证后关键证据仍不足时，才请用户补证，并说明已尝试路径与具体缺口。证据脱敏、不可逆操作和存放边界遵循 `rules/root-cause-evidence.md` 第 5 节。

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
bash scripts/project-python.sh scripts/validate-sprint-archive-readiness.py --sprint <sprint-id>
bash scripts/project-python.sh scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary
```

Before reading raw Sprint/Issue/Change documents in detail, use the Sprint Fact Sheet as the compact read-first source. Only expand `sprint.md`、`acceptance-report.md`、Issue trace、Change `tasks.md` or `trace.md` when readiness blockers, stale scan warnings, missing evidence, or user focus requires it.

For single change mode:

```bash
bash scripts/project-python.sh scripts/validate-sprint-archive-readiness.py --sprint <sprint-id> --change <change-id>
```

Readiness distinguishes active and archived Change semantics: active Changes are checked for directory/tasks completion; archived Changes are additionally checked for `trace.md`. If an archived Change lacks `trace.md`, `proposal.md`、`design.md` or `tasks.md` MUST contain a complete `## 归档验证摘要` covering validation command/result, acceptance verdict, Issue/Sprint status, and archive path/time evidence.

Before any issue package is moved to `issues/**/archive/`, the promote step MUST pass the issue subdocument status gate:

```bash
bash scripts/project-python.sh scripts/promote-issues-for-archive.py --sprint <sprint-id>
```

If scoped REQ/BUG child Markdown files still contain non-closed frontmatter or fenced YAML `status` values such as `draft`、`pending_review`、`in_sprint`、`applied`、`todo`、`open`, keep the Sprint close blocked until those documents are reconciled.

Sprint 关闭陈旧扫描只以 Issue 主文档、trace 和验收文档的结构化当前状态字段判定 Issue 中间态；带日期的历史验收记录、排障样本和阶段性状态不得改写为当前态。已归档 Change 的证据链接仍须指向真实归档目录。

若已归档 Change 的验收附件哈希变化导致 Workflow Sync 将已签认 Issue 投影为 pending，先按 `docs/standards/opsx-acceptance.md` 核实；仅命令型 AC 可通过受控补证重跑原命令。原 manifest 不得手工改写，补证未通过时不得关闭 Sprint。

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
bash scripts/project-python.sh scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --json
```

Inspect `ai_usage_snapshot.snapshot_status`、`ai_usage_snapshot.ai_usage_mode`、`generated_at`、`coverage`、`warnings` and `recommended_action`.

- If `snapshot_status: present` and `ai_usage_mode: actual`, output only a compact summary: status, mode, path, generated_at, coverage status and warning_count.
- If snapshot is `missing`、`stale` or `failed`, first try the post-command hook or snapshot refresh path with local automatic session discovery. The hook checks explicit `--session-jsonl`, session environment variables, `AI_USAGE_SESSIONS_DIR`, and the default local Codex sessions directory `~/.codex/sessions` before falling back to unavailable.

When the operator provides a known session file, use:

```bash
bash scripts/project-python.sh scripts/extract-ai-usage.py --session-jsonl <local-session.jsonl> --sprint <sprint-id> --json
```

- If local session input is unavailable after automatic discovery, or generation fails, continue only with an explicit warning in the close report: `ai_usage_mode: estimated_fallback`, reason, impact, and recommended_action. Do not state that real token usage was used.
- Do not print raw session JSONL, prompts, system/developer instructions, local absolute paths, tool output bodies, or full snapshot contents.

## Archive Loop

For each `ARCHIVE NEXT`:

1. Execute `/opsx-archive` equivalent using `.agents/skills/opsx-archive/SKILL.md`.
2. Prefer `openspec archive "<change-id>" -y`; use manual fallback only with delta self-check.
3. Stop the whole Sprint archive on title mismatch, archive target conflict, failed sync/promote script, or user interruption.

## Close Sprint

Unless `--no-sprint-close`, close only when all Sprint changes are archived and readiness passes without `--force`:

```bash
bash scripts/project-python.sh scripts/validate-sprint-archive-readiness.py --sprint <sprint-id>
bash scripts/project-python.sh scripts/validate-env-ignore-policy.py
bash scripts/project-python.sh scripts/check-sprint-close-stale-scan.py --sprint <sprint-id>
```

Then update the four-piece as needed:

```text
sprint.yaml: status completed, lifecycle_stage archive
acceptance-report.md: final verdict/date/check summary
release-note.md: draft -> published if applicable
sprint.md: closure note only outside workflow-sync marker blocks
```

Move directory with `git mv iterations/change/<sprint-id> iterations/archive/<sprint-id>`.

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## 产品数据采集与链路观测归档门禁（MUST）

关闭 Sprint 前，若 Sprint 范围内存在 API、DB、日志审计、行为埋点、Task Trace、Web/管理端请求封装、对象存储或 Agent Workflow 链路观测相关 REQ、BUG 或 Change，MUST 读取 `docs/standards/product-data-collection-observability.md`，并复核 `product_data_collection_observability` 适用性、`affected_layers` 适用层级、N/A 原因、`validation` 验证摘要和验收结果。缺失时返回对应 REQ / Change 修复，不得归档。

## Final Step — Workflow Sync（MUST）

```bash
bash scripts/project-python.sh scripts/sync-workflow-status.py --event sprint.archive --sprint <sprint-id>
```

Exit code MUST be `0`; print summary Workflow Sync Report; use `--output detail` only for debugging.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report archived/skipped/blocked counts, Sprint close status, updated files, validation commands, and exact retry command if paused.

## 面向用户的表达

面向用户的输出遵循 `rules/language.md` 的“产品经理视角沟通”：先讲业务结果和用户影响，优先日常语言，必要技术术语随文解释；决策说明体验、成本、时间和风险。

## 当前正文与证据导航

Sprint stale scan 复用归档收尾的普通导航与明确当前正文检查；历史记录不自动改写，真实链接不因历史标题而豁免。review 项需核对证据，不能报告完整关闭成功；部分交付父需求沿用现有关闭策略。

关闭扫描仅在同一行识别到 Issue 编号时排除其完整原始标题中的状态词；标题之外的待实现、待归档和中间态仍阻断，不得因同行出现 done 而跳过整行。
