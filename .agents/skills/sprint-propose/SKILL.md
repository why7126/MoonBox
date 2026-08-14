---
name: "sprint-propose"
description: "提议并创建新 Sprint 迭代规划（四件套）"
---

# sprint-propose

Use this skill when the user asks to run `/sprint-propose` or create/update a Sprint plan.

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

- Sprint 范围分析先读取候选 `trace.md` 与摘要，不得全量展开上一 Sprint 四件套、复盘库或所有 active changes。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 不要 `ls -R` 或全量 `cat iterations/** docs/knowledge-base/**`；先列清单，再分段读取。
- 复盘默认只读最近 1 份；只有 open 行动项跨 Sprint 复发或用户要求时读第 2 份。
- `best-practices/` 只读取候选 REQ/BUG/Change 标签命中的文件。
- 已存在 Sprint 时先读 `sprint.yaml` 和 `sprint.md` 的目标/Scope/知识库承接片段。
- 搜索候选项默认排除 `openspec/archive/**`；编号冲突只看目录名。
- 命令输出优先 `max_output_tokens <= 8000`。

## Input

- `sprint-xxx`：指定 Sprint ID。
- 自然语言目标：由 Agent 推导候选范围和编号。
- Flags：`--req`、`--bug`、`--change`、`--duration 2w`、`--dry-run`。

## Command Order（MUST）

- `/sprint-propose` 位于 `/req-review --approve` 或 `/bug-review --approve` 之后，位于 `/req-opsx`、`/bug-opsx`、`/opsx-apply` 之前。
- 正式纳入 Sprint 后 MUST 通过 Workflow Sync 将 REQ/BUG trace 更新为 `in_sprint`，并让后续 `/opsx-apply --sprint auto` 可解析到同一 Sprint。
- 对已存在 active Change 的治理项，MUST 将 Change 写入 `sprint.yaml changes[]` 和估算字段后再继续 apply。
- 写入 Sprint 四件套、Issue trace、Change trace 和 Workflow Sync 的步骤 MUST 严格串行执行，不得并行改同一事实源。

## Sprint ID Rules（MUST）

- Sprint ID MUST 使用 `sprint-xxx` 三位数字递增格式，例如 `sprint-002`。
- 当用户未指定 Sprint ID 且当前没有 `iterations/change/sprint-xxx/` 进行中迭代时，MAY 自动创建下一个 Sprint。
- 自动编号 MUST 同时扫描 `iterations/archive/` 与 `iterations/change/` 下符合 `sprint-[0-9]{3}` 的目录和 `sprint.yaml:sprint_id`，取最大编号加一；例如最新归档为 `sprint-001` 且无进行中迭代时，自动创建 `sprint-002`。
- 如果已存在 `iterations/change/sprint-xxx/` 进行中迭代，MUST 优先复用或要求用户明确选择，不得默认另建并行 Sprint。
- 不得使用日期、主题词或混合命名创建 Sprint，例如 `sprint-2026-08-07-spec-study`。

## Must Read

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/document-governance.md
rules/requirement-management.md
rules/bug-management.md
rules/directory-structure.md
rules/iterations-lifecycle.md
.agents/skills/workflow-sync/SKILL.md
docs/knowledge-base/README.md（存在时）
```

按候选范围分段读取：

```text
project.yaml（容量，若存在）
issues/requirements/{plan,review,archive}/<REQ>/trace.md + requirement/acceptance 摘要
issues/bugs/{plan,review,archive}/<BUG>/trace.md + bug/root-cause/acceptance 摘要
openspec/changes/<change>/proposal.md + tasks.md 摘要
iterations/change|archive/<sprint>/sprint.yaml（编号/冲突）
docs/knowledge-base/retrospectives/<latest>-retrospective.md（最近复盘）
docs/knowledge-base/best-practices/<matched>.md（按标签）
```

## Gates

### Review Gate（MUST）

纳入 Sprint 正式规划前，REQ/BUG status MUST 为 `approved` 或 `in_sprint`。

未评审条目：

- 不得写入 `sprint.yaml` 的 `requirements[]` / `bugs[]`。
- 不得写入 Sprint 目标、Scope、里程碑、工作量合计、release、acceptance 正式范围。
- 不得更新 `trace.md` `iteration`。
- 只能列入 `sprint.md`「延后项（待评审）」并提示 `/req-review` 或 `/bug-review --approve`。

### Readiness Gate

| 类型 | Ready 条件 | Not Ready 处理 |
|---|---|---|
| REQ | `requirement.md`、`acceptance.md`、`trace.md` 齐全且 approved/in_sprint | 延后并建议 `/req-complete` 或 `/req-review` |
| BUG | `bug.md`、`root-cause.md`、`acceptance.md`、`trace.md` 齐全且 approved/in_sprint | 延后并建议 `/bug-complete` 或 `/bug-review` |
| Change | `proposal.md`、`design.md`、`tasks.md` 存在且未 archived | 缺失时提示 `/req-opsx` 或 `/bug-opsx` |

### Capacity Gate

- 优先级：P0 BUG > P0 REQ > P1 > P2。
- 估算：XS=0.5、S=1、M=3、L=5、XL=8、XXL=13 人天。
- add-* 主能力 SHOULD <= 6。
- fix 缓冲 SHOULD >= 30% SP/人天。
- 必须在生成正式四件套或更新 REQ/BUG/Change trace 前计算：
  `capacity_usage = estimated_person_days / capacity_person_days`。
- 若容量或估算缺失导致无法计算，MUST 先补齐输入；不得默认通过。
- `estimated_person_days > capacity_person_days * 1.2` 时 MUST 硬阻断正式规划：
  - 不得生成 `iterations/change/<sprint>/` 四件套。
  - 不得更新 `trace.md` 的 `iteration` 或 Change trace。
  - 输出硬提示：必须拆分 Sprint、移出低优先级项或替换范围后重新运行 `/sprint-propose`。
- `capacity_person_days < estimated_person_days <= capacity_person_days * 1.2` 时 MAY 继续，但 MUST 写入容量风险、fix 缓冲影响和延后项建议。
- `estimated_person_days <= capacity_person_days` 时按既有 Review Gate、Readiness Gate 和 Capacity Gate 继续。

## Knowledge Intake

- 读取最近 Sprint 复盘，提取 open 行动项并写入 §知识库承接。
- 按范围标签选择 best-practices：`admin-list`、`admin-form`、`admin-modal`、`media-upload`。
- `sprint.md` 必须包含 §横切预防清单，列出适用 best-practices 与验收 gate 摘要。

## Artifacts（非 `--dry-run` MUST）

目录：`iterations/change/sprint-xxx/`

```text
sprint.yaml
sprint.md
release-note.md
acceptance-report.md
```

`sprint.yaml` MUST 包含：

```yaml
sprint_id: sprint-xxx
status: planning
lifecycle_stage: change
start_date: YYYY-MM-DD HH:mm:ss
end_date: YYYY-MM-DD HH:mm:ss
capacity: { developers: <int>, testers: <int> }
requirements: []
bugs: []
changes: []
estimated_story_points: <number>
estimated_person_days: <number>
```

`sprint.md` MUST 包含：目标、Scope、工作量、fix 缓冲、里程碑、风险、知识库承接、横切预防清单、依赖 ASCII 树、发布计划、关联文档。

Markdown frontmatter MUST 含 `created_at`、`updated_at`；更新只改 `updated_at`。

## Trace Updates

对正式纳入 `iterations/change/<sprint-id>/` 四件套的 REQ/BUG/Change 更新：

```text
trace.md iteration: sprint-xxx
trace.md status: in_sprint
openspec/changes/<change>/trace.md（若存在）
```

`sprint.yaml` `status: planning` 已表示正式规划完成、尚未开始批量执行；它不是“未启动 Sprint”。`/sprint-propose` 成功后 MUST 通过 Workflow Sync 将纳入项置为 `in_sprint`，使后续 `/opsx-apply --sprint auto` 可直接解析该 planning Sprint。

## 当前态看板索引（MUST）

正式纳入 REQ 或 BUG 后，MUST 分别在 `issues/requirements/CHANGELOG.md` 或 `issues/bugs/CHANGELOG.md` 更新对应 Issue 当前态行，并记录 Sprint ID、下一步和事实源路径。仅纳入纯治理 Change 时无需维护 Issue 当前态看板。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

报告 Sprint ID、状态、纳入 REQ/BUG/Change 数量、估算、知识库承接、容量门禁、四件套路径、下一步。

下一步参数规则：

- 若本次纳入 REQ，下一步 MUST 输出 `/req-opsx <REQ-full-id>`。
- 若本次纳入 BUG，下一步 MUST 输出 `/bug-opsx <BUG-full-id>`。
- 若本次仅纳入无 REQ/BUG 来源的纯治理 Change，下一步 MAY 输出 `/opsx-apply <change-id>`。

## Final Step — Workflow Sync（MUST）

Run:

```bash
python scripts/sync-workflow-status.py --event sprint.propose --sprint <sprint-id>
```

- Exit code MUST be `0`。
- MUST verify included REQ/BUG traces are updated to `status: in_sprint` and `iteration: <sprint-id>`。
- Print summary Workflow Sync Report；use `--output detail` only for debugging。
- Do not hand-edit workflow-sync marker blocks。
