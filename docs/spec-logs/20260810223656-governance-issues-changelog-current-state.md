---
created_at: 2026-08-10 22:36:56
updated_at: 2026-08-10 22:36:56
owner: MoonBox 产品团队
change_id: optimize-issues-changelog-current-state-index
type: governance
---

# Issues CHANGELOG 当前态看板优化

## 迭代目标

将 `issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` 从生命周期事件流水账调整为每个 Issue 一行的当前态看板，减少与单条 `trace.md` 的重复，并明确 CHANGELOG 只作为目录级索引入口。

## 变更摘要

- REQ/BUG CHANGELOG 改为当前态看板，字段聚焦当前状态、阶段、关联 Sprint、关联 Change、最近更新时间、下一步和事实源。
- 规则文档统一将“全局事件索引”表述调整为“当前态看板索引”。
- 相关 Agent Skill 的维护契约从“追加事件摘要”调整为“新增或更新对应 Issue 当前态行”。
- 新增 OpenSpec Change `optimize-issues-changelog-current-state-index`，并纳入 `sprint-002` 纯治理范围。

## 影响范围

- 影响 REQ/BUG 治理文档入口和 Agent 命令输出契约。
- 不改变 Issue 状态机、Workflow Sync 状态判断、OpenSpec Change 流程或 Sprint 门禁。
- 不触碰业务 `src/` 运行时代码。

## 更新文件

- `issues/requirements/CHANGELOG.md`
- `issues/bugs/CHANGELOG.md`
- `rules/requirement-management.md`
- `rules/bug-management.md`
- `rules/issues-lifecycle.md`
- `rules/document-governance.md`
- `rules/directory-structure.md`
- `rules/agent-context-budget.md`
- `.agents/skills/{capture,req-*,bug-*,sprint-propose,opsx-apply,opsx-archive,workflow-sync}/SKILL.md`
- `openspec/changes/optimize-issues-changelog-current-state-index/`
- `iterations/change/sprint-002/sprint.yaml`
- `iterations/change/sprint-002/sprint.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py`
- 通过：`python scripts/validate-directory-structure.py`
- 通过：`openspec validate optimize-issues-changelog-current-state-index`
- 通过：`python scripts/validate-sprint-scope.py sprint-002 --item optimize-issues-changelog-current-state-index`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change optimize-issues-changelog-current-state-index --sprint auto`
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-issues-changelog-current-state-index --sprint sprint-002 --dry-run --json`

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：无影响。
- DB：无影响。
- Web：无业务实现影响。
- 客户端生成：无影响。
- 管理端：无业务实现影响。
- Orval：无影响。
- Docker Compose：无影响。

## 后续建议

- 后续可考虑让 Workflow Sync 在状态同步成功后自动刷新对应 CHANGELOG 当前态行，进一步降低人工维护漂移。
