---
created_at: 2026-09-15 09:46:43
updated_at: 2026-09-15 09:46:43
---

# 提案：明确 opsx-modify 返修阶段流转

## 背景

`/opsx-modify` 用于 apply 后、archive 前的验收返修。现有规则已明确返修完成后将验收状态重新置为待复验，但对返修执行中的用户可见阶段没有明确约束，容易出现正在由研发侧修改的事项仍停留在“验收中”的表达偏差。

## 变更内容

- 明确 `/opsx-modify` 返修执行中用户可见阶段展示为“研发中”。
- 明确返修完成、验证和 Workflow Sync 通过后，用户可见阶段自动回到“验收中”。
- 保留 Change 的 `applied` 事实和首次 apply 的 `execution.completed_at`，不得用普通 `in_progress` 覆盖或回退首次 apply 完成事实。
- 将返修执行态作为展示/投影语义处理，不改变 `/opsx-apply`、`/opsx-archive` 的顺序门禁。

## 影响范围

- `.agents/skills/opsx-modify/SKILL.md`
- `AGENTS.md`
- `docs/08-command-execution-order.md`
- `rules/document-governance.md`
- `rules/agent-context-budget.md`
- `openspec/archive/2026-09-15-clarify-opsx-modify-repair-stage-flow/`
- `iterations/archive/sprint-007/sprint.yaml`
- `docs/spec-logs/`

## 不涉及

- 不修改业务 `src/` 运行时代码。
- 不新增 API、DB、权限、部署、对象存储或客户端生成边界。
- 不改变已归档 Change 的历史事实。
