---
name: "bug-complete"
description: "缺陷完善 - 补齐 root-cause、workaround、acceptance、trace"
---

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
- 不要默认 `cat rules/*.md`、`cat AGENTS.md openspec/project.md rules/...` 或读取整目录；按本命令 Step 0 列表读取必要文件，已在同一会话读取过且无变更时用摘要承接。
- 检索先用 `rg -l` / `rg --files` 定位文件，再用 `sed -n '<start>,<end>p'` 或 `nl -ba ... | sed -n` 读取必要片段。
- 大范围 `rg` MUST 限制目录与输出：优先加 `--glob '!openspec/archive/**' --glob '!**/node_modules/**' --glob '!**/.git/**'`；只有追溯历史归档时才放开 archive，并说明原因。
- 对 Harness / 模板工程 / agent 资产目录执行搜索时，默认排除 `pm-harness*/**`、`**/assets/**`、历史/外部 agent 目录（如 `.claude/**`、`.kiro/**`、`.opencode/**`）；除非当前任务明确要求分析这些目录。
- 命令输出优先控制在 `max_output_tokens <= 8000`；预期超出时先输出文件清单或命中计数，再分段读取。
- 不重复读取同一大文件集合；若需要再次确认，优先读取变更片段、`git diff -- <file>` 或具体 frontmatter/status 字段。

# bug-complete

Use this skill when the user asks to run the migrated source command `bug-complete`.

## Command Template

**Input**：完整 `BUG-xxxx-slug`（须 `bug.md`）

**Output**：root-cause.md、workaround.md、acceptance.md、trace.md；logs/、screenshots/ 目录（若需）

**禁止**：`openspec/`、`src/`

---

## 文档要点

| 文件 | 内容 |
|------|------|
| root-cause.md | 直接原因、根本原因、触发条件、分类（code/design/db/…） |
| workaround.md | 临时规避或无 |
| acceptance.md | 回归 AC-xxx |
| trace.md | status → enriching → pending_review |

## Readiness

Ready：bug + root-cause + acceptance + trace

## Next

`/bug-review <BUG-full-id> --approve`，其中 `<BUG-full-id>` MUST 使用完整 `BUG-xxxx-slug`。

---

## 当前态看板索引（MUST）

成功补齐缺陷包、根因、workaround 或验收资料后，MUST 在 `issues/bugs/CHANGELOG.md` 更新对应 BUG 当前态行。该索引只做目录级当前快照，不替代单条 BUG `trace.md`。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event bug.complete --bug <BUG-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
