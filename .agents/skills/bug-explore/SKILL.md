---
name: "bug-explore"
description: "缺陷探索 - 复现与影响分析，默认不写文档"
---

## Context Budget Guardrails（MUST）

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

# bug-explore

Use this skill when the user asks to run the migrated source command `bug-explore`.

## Command Template

探讨：能否稳定复现、影响面、是否回归、关联 REQ/Change、hotfix vs 常规 fix。

**Input**：完整 `BUG-xxxx-slug`

**默认**：不写任何文件、不写代码、不改 `src/`

用户明确要求时可更新 `capture.md`；trace 可标 `exploring`。

## 禁止

- 写 `bug.md`、root-cause、OpenSpec
- 自动修复代码

## Next

`/bug-generate <BUG-full-id>`，其中 `<BUG-full-id>` MUST 使用完整 `BUG-xxxx-slug`。
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。
