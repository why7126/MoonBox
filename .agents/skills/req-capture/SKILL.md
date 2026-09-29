---
name: "req-capture"
description: "需求记录 - 轻量 capture，防遗忘，分配 REQ-ID；支持一次输入多条并按需拆分"
---

# req-capture

Use this skill when the user asks to run the migrated source command `req-capture`.

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

**Input**：一句话描述，或粘贴会议/反馈原文。用户可能在一条消息中描述**多个**独立需求。

可选：`--priority P0|P1|P2`、`--parent REQ-xxxx`

**Output**：每条需求 → `issues/requirements/REQ-NNNN-slug/capture.md` + `trace.md`；更新 `_registry.yaml`

**禁止**：创建 `requirement.md`、写 `src/`、写 `openspec/`。

---

## Steps

1. 读 `rules/requirement-management.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md`
2. **评估并拆分**（见下节）
3. 对每条候选 REQ 执行创建前重复/相似 Issue 检查（见下节），确认非重复后才分配新 ID
4. 为每条新 REQ 创建 capture + trace、更新 registry
5. 输出重复检查摘要 + Capture 摘要（多条用表格）

---

## Multi-REQ 评估（MUST）

解析用户输入，决定 **1 条** 还是 **N 条** REQ。

**应拆分**（任一满足）：不同业务能力/模块/端；独立优先级；独立 OpenSpec Change 或验收闭环；用户显式枚举多条。

**保持单条**（全部满足）：同一功能域的一个交付单元；同一 PRD 内的细节展开；对已有 REQ 的小幅 refinement → 优先 `--parent` 或更新原 REQ，而非新 peer REQ。

**实为缺陷** → 引导 `/bug-capture`，不要 req-capture。

**规则**：每条独立 REQ-ID 与目录；禁止 umbrella REQ。未拆分时回复一句话 rationale。

---

## 创建前重复/相似 Issue 检查（MUST）

在分配新 REQ ID 前，MUST 检查项目中是否已有相同、相似或可作为父级的需求。

检查顺序：

1. 先读取 `issues/requirements/CHANGELOG.md` 与 `issues/requirements/_registry.yaml`，形成 plan / review / archive 中的候选 REQ 清单。
2. 基于用户输入的标题、关键词、业务域、目标用户、交付能力、验收闭环、非目标和关联模块筛选候选。
3. 候选不清晰时，只读取候选目录中 `capture.md` 与 `trace.md` 的标题、Frontmatter、摘要段落、当前状态、关联 Sprint/Change 和下一步；不得为判重全量读取无关 REQ 正文或历史归档大目录。

发现疑似重复或 refinement 时，MUST 先输出候选表，包含：REQ ID、标题、当前状态/阶段、相似原因、建议处理方式、事实源路径。

处理选项：

- 关联/更新原 REQ（推荐）：同一业务目标、同一交付能力、同一验收闭环或只是补充细节时使用；必要时引导后续更新原 REQ。
- 作为父子关系记录：对已有 REQ 的体验、策略或边界补充，优先使用 `parent_requirement`，而不是创建无关联 peer REQ。
- 确认非重复后新建：只有用户确认目标独立、优先级/验收/交付闭环不同，或候选只是背景相关时才继续创建新 REQ。

如果疑似重复但用户尚未确认，MUST 暂停该条创建，并在「待用户决策/处理」给出推荐选项；不得静默分配新 REQ ID。

---

## capture.md 模板

```markdown
---
req_id: REQ-0008-example
status: captured
created_at: YYYY-MM-DD HH:mm:ss
updated_at: 2026-09-12 17:46:39
recorded_by: product
source: 会议|反馈|竞品
priority: P1
parent_requirement:
---

# 一句话
…

# 原始描述
…

# 待澄清
- [ ] …

# 探索结论
（/req-explore 后人工确认写入）
```

## Next

每条：`/req-explore <REQ-full-id>` → `/req-generate <REQ-full-id>`，其中 `<REQ-full-id>` MUST 使用完整 `REQ-xxxx-slug`。

---

## 当前态看板索引（MUST）

成功创建 REQ 后，MUST 在 `issues/requirements/CHANGELOG.md` 新增或更新对应 REQ 当前态行。该索引只记录目录级当前快照、下一步和事实源路径，不替代 `_registry.yaml` 或单条 REQ `trace.md` 事实源；不得复制用户隐私、真实客户数据、密钥、未脱敏日志或本机绝对路径。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md`.对**本次创建的每一条** REQ：

```bash
for req in REQ-xxxx-slug ...; do
  python scripts/sync-workflow-status.py --event req.capture --req "$req" --sprint auto || exit 1
done
```

- Exit code **MUST** be `0`
- Print summary **Workflow Sync Report**（多条时注明共 N 条）；use `--output detail` only for debugging
- Do **not** hand-edit `sprint.md` Scope marker blocks

分级元数据遵循 `rules/document-governance.md` 的“Issue 分级元数据”：REQ 使用 priority，BUG 使用 severity，写入 Frontmatter；trace 为当前事实源，主文档与 capture 同步，初判依据留正文。

## 中文标题生成门禁

本次生成或重生成的所有 Markdown 必须包含中文业务 Frontmatter `title` 与一致的唯一一级标题，辅助文档标题包含业务主题及用途；不得只有 ID、英文模板或文档类别。Issue 主文档的业务 title 同步注册表，Change proposal 标题不得覆盖 Issue 标题。保留 OpenSpec 解析关键字。

在完成态 Workflow Sync 之前，对本次产物执行 `python scripts/validate-document-titles.py` 并传入明确文件路径或当前 `--req` / `--bug` / `--change`；失败先修正，不宣称完成、不推进状态。不批量修复无关历史文档。
