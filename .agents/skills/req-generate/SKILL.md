---
name: "req-generate"
description: "需求生成 - 仅生成 requirement.md（PRD）"
---

# req-generate

Use this skill when the user asks to run the migrated source command `req-generate`.

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

## 当前态看板索引（MUST）

成功生成 `requirement.md` 后，MUST 在 `issues/requirements/CHANGELOG.md` 更新对应 REQ 当前态行。普通文案润色、格式调整或错别字修复 MAY 不更新。

`req.generate` 的 CHANGELOG 刷新 MUST 通过 Workflow Sync 派生完成；命令结束前必须确认 `python scripts/sync-workflow-status.py --event req.generate --req <REQ-id> --sprint auto` 报告中 `issues/requirements/CHANGELOG.md` 对目标 REQ 为 `Updated` 或明确 `Skipped (no delta)`。不得只手工修改 `requirement.md` / `trace.md` 后跳过当前态看板刷新。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.generate --req <REQ-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- 报告中 MUST 覆盖 `issues/requirements/CHANGELOG.md` 对应 REQ 行；若缺失该文件更新或 no-delta 记录，视为派生刷新未覆盖，必须修复 Workflow Sync 后重跑。
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
