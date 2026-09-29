---
title: Capture 创建前去重门禁治理日志
created_at: 2026-09-16 22:48:15
updated_at: 2026-09-16 22:48:15
type: governance
change_id: add-capture-dedup-gate
owner: MoonBox 产品团队
---

# Capture 创建前去重门禁治理日志

## 迭代目标

为 `/capture`、`/req-capture` 和 `/bug-capture` 增加创建前重复/相似 Issue 检查门禁，避免同一需求、同一缺陷或已有 Issue 的补充内容被误建为新的 peer REQ/BUG。

## 变更摘要

- `/capture` 分类拆分后按 REQ/BUG 分别执行重复/相似检查。
- `/req-capture` 在分配新 REQ ID 前读取需求 `CHANGELOG.md` 与 `_registry.yaml`，按需读取候选 `capture.md` / `trace.md` 片段。
- `/bug-capture` 在分配新 BUG ID 前读取缺陷 `CHANGELOG.md` 与 `_registry.yaml`，按需读取候选 `capture.md` / `trace.md` 片段。
- 疑似重复时输出候选、相似原因、当前状态、事实源路径和处理选项；默认推荐关联/更新原 Issue。
- 同步需求管理、缺陷管理、上下文预算和 AGENTS 入口红线。

## 影响范围

- Agent 技能：`capture`、`req-capture`、`bug-capture`。
- 治理规则：REQ/BUG lifecycle、上下文预算、项目入口红线。
- OpenSpec：新增纯治理 Change `add-capture-dedup-gate`。
- Sprint：纳入 `sprint-007`，估算 0.5 人天。

## 更新文件

- `.agents/skills/capture/SKILL.md`
- `.agents/skills/req-capture/SKILL.md`
- `.agents/skills/bug-capture/SKILL.md`
- `AGENTS.md`
- `rules/agent-context-budget.md`
- `rules/requirement-management.md`
- `rules/bug-management.md`
- `openspec/changes/add-capture-dedup-gate/`
- `iterations/change/sprint-007/sprint.yaml`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `python scripts/validate-change-identity.py --new-id add-capture-dedup-gate`：通过。
- `python scripts/validate-sprint-selection.py --sprint sprint-007`：通过。
- `python scripts/add-sprint-scope-item.py --sprint sprint-007 --change add-capture-dedup-gate ...`：通过。
- `python scripts/sync-workflow-status.py --event opsx.propose --change add-capture-dedup-gate --sprint auto`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py --change add-capture-dedup-gate --residual-report`：通过，未发现非当前 Change 中文残留。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate add-capture-dedup-gate --strict`：通过。
- `python scripts/validate-sprint-scope.py sprint-007 --item add-capture-dedup-gate`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-capture-dedup-gate --sprint auto`：通过。
- `python scripts/sync-workflow-status.py --sprint auto --check`：最终通过。
- AI Usage Hook：warning，`usage_mode: unavailable`，未发现可归因 token_count command-run，不阻断本次治理变更。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

不适用。本次仅修改治理技能、规则、OpenSpec 文档和治理日志，不触达业务运行时代码、API、数据库、Web UI、客户端生成、管理端或 Docker Compose。

## 后续建议

后续如需要更强自动化，可评估新增脚本对 `_registry.yaml`、`CHANGELOG.md` 与候选 `capture.md` / `trace.md` 进行结构化候选提取；当前先以流程门禁固化，避免引入额外脚本复杂度。
