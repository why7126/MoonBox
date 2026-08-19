---
name: "req-explore"
description: "需求探索 - 思考分析已记录需求，默认不写任何文档"
---

# req-explore

Use this skill when the user asks to run the migrated source command `req-explore`.

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

对标 `/opsx-explore`，面向 **需求域**。探讨范围、用户、风险、与现有 REQ 重复、是否子需求。

**Input**：完整 `REQ-xxxx-slug` 或 capture 阶段的一句话（无 ID 则先建议 `/req-capture`）

**默认**：**不生成任何文件、不写代码**。

**可选**：用户明确要求「记录结论」时，才更新 `capture.md#探索结论`；可将 trace `status` 标为 `exploring`。

---

## Stance

- 好奇、可视化（ASCII 依赖/范围图）
- 可读 `capture.md`、类似 REQ、相关 `src/`（只读）
- 不 prescriptive 到单一方案

## 可探讨

- 范围 In/Out、与 REQ-0005 等重复？
- 子需求 vs 独立 REQ
- UI 是否需要 prototype
- 技术风险与 Sprint 容量

## 禁止

- 写 `requirement.md`、六件套、OpenSpec
- 写 `src/`
- 自动更新文件（除非用户明确要求）

## Next

`/req-generate <REQ-full-id>` 或继续 explore；`<REQ-full-id>` MUST 使用完整 `REQ-xxxx-slug`。
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。
## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。
