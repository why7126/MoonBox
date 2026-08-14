---
created_at: 2026-08-10 22:36:56
updated_at: 2026-08-10 22:36:56
owner: MoonBox 产品团队
change_id: optimize-issues-changelog-current-state-index
change_type: governance
source_requirement: null
source_bug: null
sprint: sprint-002
---

# 优化 Issues CHANGELOG 当前态索引

## 背景

`issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` 已作为目录级索引存在，但当前采用按时间倒序追加生命周期事件的流水账形态，和单条 Issue `trace.md` 的变更记录高度重叠。

REQ/BUG 的完整生命周期事实已经由 `trace.md` 承载，当前状态和路径索引由 `_registry.yaml`、Sprint 四件套和 OpenSpec Change 共同确认。目录级 CHANGELOG 更适合承担“快速定位当前关注项”的入口职责。

## 目标

- 将 REQ/BUG 根目录 CHANGELOG 从事件流水表调整为“每 Issue 当前态看板”。
- 明确 CHANGELOG 只记录每个 Issue 的最新快照、下一步和事实源路径，不复制 `trace.md` 的完整事件链。
- 同步规则、技能和 OpenSpec delta spec 中的维护边界，要求相关命令更新对应 Issue 行，而不是追加每一步事件。
- 保持 `_registry.yaml`、单条 Issue `trace.md`、OpenSpec Change、Sprint 四件套和正式规格的事实源地位不变。

## 非目标

- 不修改业务 `src/` 代码。
- 不改造 Workflow Sync 脚本实现。
- 不修复既有 registry/trace 漂移。
- 不迁移或删除单条 Issue `trace.md` 中的历史变更记录。

## 影响范围

- `issues/requirements/CHANGELOG.md`
- `issues/bugs/CHANGELOG.md`
- `rules/requirement-management.md`
- `rules/bug-management.md`
- `rules/issues-lifecycle.md`
- `rules/document-governance.md`
- `rules/directory-structure.md`
- `rules/agent-context-budget.md`
- `.agents/skills/{capture,req-*,bug-*,sprint-propose,opsx-apply,opsx-archive,workflow-sync}/SKILL.md`
- `docs/spec-logs/`

## 验证计划

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate optimize-issues-changelog-current-state-index`
- `python scripts/validate-sprint-scope.py sprint-002 --item optimize-issues-changelog-current-state-index`
