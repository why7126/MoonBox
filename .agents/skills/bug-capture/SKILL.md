---
name: "bug-capture"
description: "缺陷记录 - 轻量 capture，分配 BUG-ID；支持一次输入多条并按需拆分"
---

# bug-capture

Use this skill when the user asks to run the migrated source command `bug-capture`.

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

**Input**：现象描述、复现步骤、环境（可选截图路径）。用户可能在一条消息中描述**多个**独立缺陷。

Flags：`--severity blocker|critical|high|medium|low`（单条时；拆分时按每条单独评估）

**Output**：每条缺陷 → `issues/bugs/BUG-NNNN-slug/capture.md` + `trace.md`；更新 `_registry.yaml`

**禁止**：`bug.md`、`src/`、`openspec/`

---

## Steps

1. 读 `rules/bug-management.md`、`issues/bugs/_registry.yaml`
2. **评估并拆分**（见下节）
3. 为每条 BUG 分配 ID、创建 capture + trace、更新 registry
4. 输出 Capture 摘要（多条用表格）

---

## Multi-BUG 评估（MUST）

解析用户输入，决定 **1 条** 还是 **N 条** BUG。

**应拆分**（任一满足）：不同界面/层级；不同缺陷类型；不同修复面或独立 `fix-*` Change；独立严重度或交付优先级；用户显式枚举多条。

**保持单条**（全部满足）：同一页面/弹窗且一次修复可闭环；同一根因的不可分割现象；拆分会导致重复 repro/acceptance。

**规则**：每条独立 BUG-ID 与目录；禁止 umbrella BUG；同属一 REQ 时填相同 `related_requirement`；因果链用 `related_bug`。未拆分时回复一句话 rationale。

---

## capture.md 模板

```markdown
---
bug_id: BUG-0001-example
status: captured
created_at: YYYY-MM-DD HH:mm:ss
updated_at: 2026-08-15 09:50:00
severity_hint: high
environment: local|docker|prod
related_requirement:
related_bug:
---

# 现象
…

# 复现步骤
1. …

# 期望 vs 实际
…

# 附件
screenshots/…  logs/…
```

## Next

每条：`/bug-explore <BUG-full-id>` → `/bug-generate <BUG-full-id>`，其中 `<BUG-full-id>` MUST 使用完整 `BUG-xxxx-slug`。

---

## 当前态看板索引（MUST）

成功创建 BUG 后，MUST 在 `issues/bugs/CHANGELOG.md` 新增或更新对应 BUG 当前态行。该索引只记录目录级当前快照、下一步和事实源路径，不替代 `_registry.yaml` 或单条 BUG `trace.md` 事实源；不得复制复现日志原文、用户隐私、真实客户数据、密钥、未脱敏日志或本机绝对路径。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md`.对**本次创建的每一条** BUG：

```bash
for bug in BUG-xxxx-slug ...; do
  python scripts/sync-workflow-status.py --event bug.capture --bug "$bug" --sprint auto || exit 1
done
```

- Exit code **MUST** be `0`
- Print summary **Workflow Sync Report**（多条时注明共 N 条）；use `--output detail` only for debugging
- Do **not** hand-edit `sprint.md` Scope marker blocks
