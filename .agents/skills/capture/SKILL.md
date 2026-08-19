---
name: "capture"
description: "智能收集 - 自动区分需求与缺陷，按需拆分并分别走 req-capture / bug-capture 落盘"
---

# capture

Use this skill when the user asks to run the migrated source command `capture`.

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

**Input**：用户不确定是需求还是 BUG 时的原始描述；可含混合多条。可选：`--priority`、`--severity`、`--parent REQ-xxxx`

**Output**：分类分析表 + 各 REQ/BUG 的 capture.md + trace.md + registry 更新

**禁止**：`requirement.md`、`bug.md`、`src/`、`openspec/`

**定位**：类型已知时用 `/req-capture` 或 `/bug-capture`；本命令用于类型未决或混合输入。

---

## Steps

1. 读 `rules/requirement-management.md`、`rules/bug-management.md`、两个 `_registry.yaml`
2. **解析 → 分类（REQ/BUG）→ 拆分**（见 `.agents/skills/capture/SKILL.md`）
3. 落盘：REQ 遵循 req-capture 模板与规则；BUG 遵循 bug-capture 模板与规则；frontmatter 加 `captured_via: capture` 与 `classification_rationale`
4. 输出分类分析表 + Capture 摘要

---

## 分类要点

- 已有能力/规范下的偏差 → **BUG**
- 尚未交付的新能力/流程 → **REQ**
- 混合输入 → 拆条目后分别归类
- 新功能 PRD 未达标 → BUG + `related_requirement`
- 边界不清 → 分类表标注待澄清，capture 写待澄清项

拆分分别套用 `/req-capture` Multi-REQ 与 `/bug-capture` Multi-BUG 规则。

---

## 当前态看板索引（MUST）

成功创建 REQ 或 BUG 后，MUST 分别在 `issues/requirements/CHANGELOG.md` 或 `issues/bugs/CHANGELOG.md` 新增或更新对应 Issue 当前态行。看板索引只记录目录级当前快照、下一步和事实源路径，不替代 `_registry.yaml`、单条 Issue `trace.md`、OpenSpec Change 或 Sprint 四件套事实源。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md`.对每条创建的 REQ / BUG：

```bash
for req in REQ-xxxx-slug ...; do
  python scripts/sync-workflow-status.py --event req.capture --req "$req" --sprint auto || exit 1
done
for bug in BUG-xxxx-slug ...; do
  python scripts/sync-workflow-status.py --event bug.capture --bug "$bug" --sprint auto || exit 1
done
```

- Exit code **MUST** be `0`
- Print summary **Workflow Sync Report**（注明 REQ N 条 + BUG M 条）；use `--output detail` only for debugging
- Do **not** hand-edit `sprint.md` Scope marker blocks
