---
name: "req-generate"
description: "需求生成 - 仅生成 requirement.md（PRD）"
---

# req-generate

Use this skill when the user asks to run the migrated source command `req-generate`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

**Input**：完整 `REQ-xxxx-slug`（须存在 `capture.md`）

**Output**：**仅** `requirement.md`；`trace.md` → `status: draft`，`lifecycle.generated`

**禁止**：user-stories、acceptance、prototype、openspec、src

---

## Steps

1. 读 `capture.md`、探索对话上下文、`rules/requirement-management.md`
2. 读 1–2 个同类 REQ 作结构参考（如 `REQ-0005-user-management-list-refine/requirement.md`）
3. 写 `requirement.md` frontmatter：

```yaml
---
requirement_id: REQ-xxxx
title:
terminal: web-admin | web-catalog | miniapp | multi
version: v1
status: draft
owner: product
source: capture.md
priority: P1
parent_requirement:
---
```

4. 正文含：背景、目标用户、范围（含/不含）、功能要求（FR-xxx）、UI 约束、关联需求、状态块
5. 同步 `requirement.md` 与 `trace.md` 的 `status: draft`
6. 追加 trace 变更记录

## Next

`/req-complete <REQ-full-id>`，其中 `<REQ-full-id>` MUST 使用完整 `REQ-xxxx-slug`。

---

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.generate --req <REQ-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
