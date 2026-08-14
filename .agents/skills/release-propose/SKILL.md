---
name: "release-propose"
description: "创建或更新产品版本发布计划"
---

# release-propose

Use this skill when the user asks `/release-propose <version>` or wants to create/update a product release plan.

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
- 先从候选 Sprint 的 `sprint.yaml`、`release-note.md` 摘要和 Change/Issue 状态定位发布范围，不得全量读取所有 `iterations/**`、`issues/**`、`openspec/archive/**` 或 legacy `openspec/changes/archive/**`。
- 搜索历史归档时只按候选 Sprint / Change ID 精确定位；不要宽泛展开归档目录。
- 命令输出优先摘要：版本、范围、门禁缺口、生成/更新文件、下一步。

## Input

- `<version>`：必填，SemVer 风格，如 `v0.1.0`。
- Flags：`--sprint <sprint-id>`、`--req <REQ-id>`、`--bug <BUG-id>`、`--change <change-id>`、`--dry-run`。

## Command Order（MUST）

- `/release-propose` 位于交付闭环之后，优先基于已归档 Change 和已完成 Sprint；若仍有未归档或未关闭项，只能作为 gate gap 进入发布计划。
- 推荐发布链路为 `/release-propose <version>` → `/release-prepare <version>` → `/usage-docs-generate|update|validate <version>` → `/image-prepare <version>` → `/image-build <version>` → `/release-publish <version>`。
- 发布范围必须来自 Sprint、REQ、BUG 或 Change 的可追溯事实源；不得把未评审、未纳入 Sprint 或未交付事项写入正式发布范围。
- Release artifact、AI Usage hook 和后续产品手册/镜像计划写入 MUST 严格串行执行。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/document-governance.md
rules/directory-structure.md
rules/release.md
rules/security.md
rules/agent-context-budget.md
releases/README.md
releases/templates/release.json
```

按候选范围分段读取：

```text
iterations/change|archive/<sprint-id>/sprint.yaml
iterations/change|archive/<sprint-id>/release-note.md
iterations/change|archive/<sprint-id>/acceptance-report.md（门禁摘要）
issues/requirements/{plan,review,archive}/<REQ>/trace.md（状态摘要）
issues/bugs/{plan,review,archive}/<BUG>/trace.md（状态摘要）
openspec/changes/<change-id>/trace.md 或 openspec/archive/<date>-<change-id>/trace.md（存在时）
src/shared/product-version.ts
```

## Gates

| Gate | Rule |
|---|---|
| Version | `<version>` MUST match `vX.Y.Z` or SemVer-like pre-release form. |
| Scope | Release scope MUST come from Sprint / REQ / BUG / Change traceable artifacts. |
| Formal scope | `formal_scope_only` MUST be `true`; unreviewed or non-delivered items MUST NOT enter formal scope. |
| Sprint | Candidate Sprint SHOULD be completed or explicitly marked as planned release scope with open gates. |
| Change | Formal Changes SHOULD be archived before publish; unarchived Changes are allowed only in propose as blocking gate gaps. |
| Public safety | Do not include secrets, real customer data, internal DB URLs, MinIO/object storage credentials, tokens, or non-public ops details. |
| Product version | If `src/shared/product-version.ts` differs from `<version>`, set `version_change_rationale` or list the mismatch as a blocking gap for prepare/publish. |

## Artifacts（非 `--dry-run` MUST）

Create or update:

```text
releases/<version>/release.json
```

Use `releases/templates/release.json` as the base shape. The release object MUST include:

- `version`
- `release_time` in `YYYY-MM-DD HH:mm:ss`
- `summary`
- `formal_scope_only: true`
- `sprints`
- `requirements`
- `bugs`
- `changes`
- `gates`
- `known_issues`
- `upgrade_steps`
- `rollback`
- `impact_scope`
- `announcement`

For propose, unknown gates MAY remain `na` with clear `rationale`, or `blocked` only if a later validator/script supports it. Do not mark a gate `pass` without concrete evidence.

## Validation

Run after writing:

```bash
python scripts/validate-release.py --release-dir releases/<version>
```

If validation fails because expected publish-time evidence is still missing, report the gaps clearly and keep the release as a draft plan. Structural errors, invalid JSON, missing required keys, or public-safety failures MUST be fixed before ending.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report version, selected Sprint / REQ / BUG / Change counts, created/updated path, current gate gaps, validation result, and next command:

```text
/release-prepare <version>
```

## Final Step — AI Usage Post-command Hook (MUST)

After the release plan is written and validation has been attempted, run:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event release.propose \
  --release <version> \
  [--release-sprint <sprint-id>] \
  [--sprint <sprint-id>] \
  [--req <REQ-id>] \
  [--bug <BUG-id>] \
  [--change <change-id>] \
  --json
```

- Pass every Sprint / REQ / BUG / Change included in this release proposal so the hook can attribute the command run.
- Pass `--release <version>` so the hook writes `data/ai-usage/command-runs/releases/<version>/release.propose.json`.
- Pass each release-scope Sprint with repeated `--release-sprint <sprint-id>`.
- If the release has no Sprint scope, omit `--sprint`; Sprint snapshot output MUST be `skipped`.
- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `session_input`, `release_artifact`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.
