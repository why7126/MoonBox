---
name: openspec-apply-change
description: Implement tasks from an OpenSpec change. Use when the user wants to start implementing, continue implementation, or work through tasks.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.3.1"
updated_at: 2026-09-12 21:30:04
---


## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`。
- 已在同一会话读取过且无变更的规则和 Skill 文件，用摘要承接或摘要复用，不重复全量读取。
- 先用 `rg -l`、`rg --files`、`git diff --stat`、`git diff --name-only` 或 OpenSpec CLI `contextFiles` 定位，再分段读取必要片段。
- 禁止默认宽泛读取 `cat rules/*.md`、`cat docs/**`、`cat issues/**`、`cat iterations/**` 或 `ls -R`。
- 默认排除 generated、node_modules、coverage、dist、archive 大目录。

Implement tasks from an OpenSpec change.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

## Apply 连续执行契约（MUST）

MUST 读取并遵守 [Apply 连续执行契约](../../../docs/08-command-execution-order.md#apply-连续执行契约)，共用「连续推进」「硬阻塞与停止」「完成门禁」「中断续接」四项规则。每次final前执行中央「停止前决策」，CLI暂停提示不构成独立停止依据；按「行为验收」区分合成与真实证据。阶段进度不结束任务；自检修复留在当前 apply，完成判定和恢复入口均以该事实源为准。

MUST 同时遵守 `.agents/skills/opsx-apply/SKILL.md` 的 Target Resolution、BUG 根因、Sprint、横切、原型/参考稿、观测与收尾门禁；本入口不构成项目门禁的替代路径。

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the **AskUserQuestion tool** to let the user select

   Always announce: "Using change: <name>" and how to override (e.g., `/opsx:apply <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand:
   - `schemaName`: The workflow being used (e.g., "spec-driven")
   - Which artifact contains the tasks (typically "tasks" for spec-driven, check status for others)

3. **Get apply instructions**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - `contextFiles`: artifact ID -> array of concrete file paths (varies by schema - could be proposal/specs/design/tasks or spec/tests/implementation/docs)
   - Progress (total, complete, remaining)
   - Task list with status
   - Dynamic instruction based on current state

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): inspect the missing artifacts, fill authorized factual gaps and recheck; missing scope or key decisions follow the shared hard-blocker contract.
   - If `state: "all_done"`: verify the shared 完成门禁, repair missing validation/documentation/sync work, then report the actual outcome.
   - Otherwise: proceed to implementation

4. **Read context files**

   Read every file path listed under `contextFiles` from the apply instructions output.
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from CLI output

5. **Check Sprint inclusion before implementation**

   Every Change, including pure governance, must be formally included in a `sprint-xxx`; linked REQ/BUG also requires Issue trace consistency.

   - Run `python scripts/sync-workflow-status.py --event opsx.apply --change "<name>" --sprint auto --dry-run`.
   - Confirm sprint resolution succeeds; skipped/unresolved sprint is blocking.
   - Confirm the resolved `iterations/change|archive/<sprint>/sprint.yaml` contains the change in `changes[]` and the linked issue in `requirements[]` or `bugs[]`.
   - Confirm linked issue `trace.md` has `iteration: <sprint-id>` and status `in_sprint` or a later delivery state.

   If this gate fails, do not implement past the gate. Repair already-authorized synchronization gaps and recheck; otherwise follow the shared hard-blocker contract and Sprint inclusion workflow.

6. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Dynamic instruction from CLI

7. **连续实现与自检**

   按依赖实现任务，补齐证据并运行相关检查；失败在当前 apply 内修复。验证通过后再勾选，立即推进下一个可执行任务。阶段汇报使用 commentary，不以批次完成结束回复。

8. **完成或必要暂停**

   按共享完成门禁串行完成文档/任务回填、Workflow Sync 和 AI Usage Hook，再报告真实交付结果。只有共享硬阻塞、用户明确停止或环境强制中断时才暂停；遵守中断续接规则，不把剩余任务转成必须另发的继续命令。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。
## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## 研发启动与进度同步

实施前根因、Sprint与授权门禁通过后，正式实现前串行执行 `python scripts/sync-workflow-status.py --event opsx.start --change <change-id> --sprint auto`；启动失败先修复，dry-run不算启动。启动事实使0/N进入研发中。每批任务实现和验证后以相同参数执行opsx.progress，不触发完成验收回填。

完成门禁通过后才执行opsx.apply；全勾选不替代完成门禁。重复启动不重置时间，中断保留启动事实，不宣称Agent进程在线。CLI和后端共用执行事实判定，所有写入串行，冲突或中断后重跑修复投影；closed/archived Issue不重开。用户命令保留完整REQ/BUG身份。
