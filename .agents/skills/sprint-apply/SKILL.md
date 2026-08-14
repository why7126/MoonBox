---
name: "sprint-apply"
description: "按 Sprint 依赖与优先级编排 OpenSpec Change 开发"
---

# sprint-apply

Use this skill when the user asks to run `/sprint-apply <sprint-id>`.

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

- Sprint apply 必须逐 Change 聚焦读取，不得把整个 Sprint 历史、全部 issue 包或全部 active changes 同时装入上下文。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 先读 `sprint.yaml` 与必要 trace/status 片段，不全量读取 Sprint 四件套。
- 每个 Change 只读 `proposal.md`、`tasks.md`、依赖字段和必要 design/spec 片段。
- UI gate 只读取命中标签的 best-practices。
- Queue report 输出摘要；大 diff/test 输出分段读取。

## Input

- `<sprint-id>` required unless only one active Sprint exists.
- Flags: `--dry-run`、`--parallel`、`--force-req-check`、`--skip-cross-cutting-gate`（仅 P0 热修）。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/testing.md
rules/requirement-management.md
rules/bug-management.md
rules/iterations-lifecycle.md
rules/directory-structure.md
.agents/skills/workflow-sync/SKILL.md
iterations/change|archive/<sprint>/sprint.yaml
```

Focused snippets as needed:

```text
iterations/<stage>/<sprint>/sprint.md §目标/Scope/依赖/横切预防清单
issues/requirements|bugs/<stage>/<id>/trace.md
openspec/changes/<change>/proposal.md + tasks.md + trace.md
```

## Gates

### Review Gate（MUST）

All Sprint REQ/BUG in formal scope MUST be `approved` or `in_sprint`. If not, stop and report remediation; do not apply related changes.

### Change Status Gate

| Status | Action |
|---|---|
| archived | skip |
| all tasks complete | skip or suggest archive |
| blocked / missing artifacts | pause |
| active with pending tasks | eligible |

### Cross-cutting Gate

Before editing `src/`, run the same gate as `.agents/skills/opsx-apply/SKILL.md` for each APPLY NEXT change.

## Queue Algorithm

1. Resolve Sprint directory via lifecycle rules.
2. Load `requirements[]`、`bugs[]`、`changes[]` from `sprint.yaml`.
3. Map each Change to related REQ/BUG and priority.
4. Build dependencies from proposal/design/tasks/trace and Sprint dependency section.
5. Sort: P0 BUG > P0 REQ > P1 > P2; prerequisites before dependents.
6. Output Sprint Queue Report before changing files.

Queue Report MUST include:

```text
Sprint / status / lifecycle_stage
Eligible changes
Skipped changes + reason
Blocked changes + reason
Topological order
Next APPLY target
```

`--dry-run` stops after Queue Report.

## Execution Loop

For each eligible Change:

1. Announce APPLY target.
2. Execute `/opsx-apply` equivalent using `.agents/skills/opsx-apply/SKILL.md`.
3. Run focused tests/checks.
4. Update tasks and trace.
5. Continue until queue exhausted, blocked, or user interrupts.

Do not archive automatically unless user explicitly asks for sprint/archive flow.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report completed changes, skipped/blocked items, tests/checks, Sprint progress, and next suggested command.

## Final Step — Workflow Sync（MUST）

Run:

```bash
python scripts/sync-workflow-status.py --event sprint.apply --sprint <sprint-id>
```

- Exit code MUST be `0`。
- Print summary Workflow Sync Report；use `--output detail` only for debugging。
- Do not hand-edit workflow-sync marker blocks。
