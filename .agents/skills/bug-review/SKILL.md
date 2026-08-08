---
name: "bug-review"
description: "缺陷评审 - 确认是否修复；approved 后先 sprint-propose，再 bug-opsx"
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

# bug-review

Use this skill when the user asks to run the migrated source command `bug-review`.

## Command Template

**Input**：完整 `BUG-xxxx-slug`

Flags：`--approve` | `--reject` | `--defer` | `--wont-fix`

**Output**：`review.md`；status → `approved` | `rejected` | `deferred` | `wont_fix`

## Step — 目录迁移（MUST，`--approve` 时）

Read `rules/issues-lifecycle.md`。

| Flag | 迁移 |
|------|------|
| `--approve` | `plan/` → `review/` |
| `--reject` / `--defer` / `--wont-fix` | **跳过**（保留 `plan/`） |

`--approve` 时 **MUST** 在 Workflow Sync **之前**运行：

```bash
python scripts/promote-issue-stage.py --bug <BUG-id> --to review --reason "/bug-review --approve"
```

- Exit code **MUST** be `0`（已在 `review/` 时可 no-op）。
- 打印脚本 stdout（迁移路径、引用更新计数）。

## 评审清单

- [ ] 可复现或根因充分
- [ ] 严重等级合理
- [ ] 回归验收明确
- [ ] 是否需 hotfix 路径

## 门禁

**仅 `approved`** 可执行 `/sprint-propose` 纳入 Sprint。`/bug-opsx` MUST 位于 `/sprint-propose --bug <BUG-full-id>` 成功之后；不得在评审完成后直接推荐或执行 `/bug-opsx`。（P0 BUG 优先纳入 Sprint）

## Next

`/sprint-propose --bug <BUG-full-id>` → `/bug-opsx <BUG-full-id>`，其中 `<BUG-full-id>` MUST 使用完整 `BUG-xxxx-slug`。

---

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event bug.review --bug <BUG-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
