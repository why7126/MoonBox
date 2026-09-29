---
name: "req-review"
description: "需求评审 - 状态变更；approved 后先 sprint-propose，再 req-opsx"
---

# req-review

Use this skill when the user asks to run the migrated source command `req-review`.

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

**Input**：完整 `REQ-xxxx-slug`

Default：无 flag 时等价于 `approve`。`--approve` 仅作为兼容别名保留；反向结果必须显式使用 `--reject` 或 `--defer`。

**Output**：`review.md`；`trace.md` + `requirement.md` → `status: approved|rejected|deferred`

---

## Step 1 — 前置检查

- `status` 应为 `pending_review`（或 `enriching` 且 Readiness ≥ Partially Ready）
- 读 requirement、acceptance、trace；UI 类读 prototype

## Step 2 — 评审清单

- [ ] 范围清晰，Out of Scope 明确
- [ ] 验收标准可测试
- [ ] 优先级与依赖合理
- [ ] UI 类：原型或实现策略已决
- [ ] 无与现有 REQ 重复未说明
- [ ] API / DB / 日志审计 / 行为埋点 / Task Trace / Web/管理端请求封装 / 对象存储 / Agent Workflow 链路观测类需求已引用 `docs/standards/product-data-collection-observability.md`，并声明 `product_data_collection_observability`、`affected_layers`、N/A 原因和 `validation` 摘要

## Step 3 — 写 review.md

```markdown
---
review_id: REV-REQ-xxxx-001
date: YYYY-MM-DD
participants: []
result: approved | rejected | deferred
---

## 评审结论
…

## 条件通过项
- [ ] …
```

## Step 4 — 更新 status

| result | status |
|--------|--------|
| approve | `approved` |
| reject | `rejected` |
| defer | `deferred` |

填写 `lifecycle.reviewed`、`lifecycle.approved`（若 approve）

## Step 5 — 目录迁移（MUST，默认 approve 或 `--approve` 时）

Read `rules/issues-lifecycle.md`。

| Flag | 迁移 |
|------|------|
| 无 flag / `--approve` | `plan/` → `review/` |
| `--reject` / `--defer` | **跳过**（保留 `plan/`） |

默认 approve 或显式 `--approve` 时 **MUST** 在 Workflow Sync **之前**运行：

```bash
python scripts/promote-issue-stage.py --req <REQ-id> --to review --reason "/req-review"
```

- Exit code **MUST** be `0`（已在 `review/` 时可 no-op）。
- 打印脚本 stdout（迁移路径、引用更新计数）。
- `--dry-run` 仅用于预检，不得作为命令结束状态。

## 门禁

**仅 `approved`** 可执行 `/sprint-propose` 纳入 Sprint。`/req-opsx` MUST 位于 `/sprint-propose --req <REQ-full-id>` 成功之后；不得在评审完成后直接推荐或执行 `/req-opsx`。

涉及 API、DB、日志审计、行为埋点、Task Trace、Web/管理端请求封装、对象存储或 Agent Workflow 链路观测的 REQ，若缺少 `docs/standards/product-data-collection-observability.md` 引用、`product_data_collection_observability` 声明、验收项或具体 N/A 原因，MUST 在 `review.md` 记录为风险或条件通过项；阻断等级按当前需求风险判断。若评审前置材料、数据采集声明、验收项或风险判断不足以支持通过，必须按引导式反馈契约收敛问题，不得因为无 flag 默认 approve 而静默批准。

## Next

`/sprint-propose --req <REQ-full-id>` → `/req-opsx <REQ-full-id>`，其中 `<REQ-full-id>` MUST 使用完整 `REQ-xxxx-slug`。

---

## 当前态看板索引（MUST）

成功写入评审结论后，MUST 在 `issues/requirements/CHANGELOG.md` 更新对应 REQ 当前态行。approve 导致目录迁入 `review/` 时，当前态行 SHOULD 同步更新阶段、事实源路径和下一步。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.review --req <REQ-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).

## Final Step — AI Usage Post-command Hook (MUST)

After Workflow Sync exits with code `0`, run:

```bash
python scripts/extract-ai-usage.py --post-command-hook --workflow-event req.review --req <REQ-id> --json
```

- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.

## 中文标题生成门禁

本次生成或重生成的所有 Markdown 必须包含中文业务 Frontmatter `title` 与一致的唯一一级标题，辅助文档标题包含业务主题及用途；不得只有 ID、英文模板或文档类别。Issue 主文档的业务 title 同步注册表，Change proposal 标题不得覆盖 Issue 标题。保留 OpenSpec 解析关键字。

在完成态 Workflow Sync 之前，对本次产物执行 `python scripts/validate-document-titles.py` 并传入明确文件路径或当前 `--req` / `--bug` / `--change`；失败先修正，不宣称完成、不推进状态。不批量修复无关历史文档。
