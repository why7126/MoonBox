---
created_at: 2026-08-10 09:05:11
updated_at: 2026-08-10 09:05:11
owner: MoonBox 产品团队
change_id: add-issues-changelog-index
change_type: governance
source_requirement: null
source_bug: null
sprint: sprint-002
---

# 新增 Issues 全局事件索引

## 背景

当前 REQ/BUG 治理已有 `_registry.yaml` 作为当前索引、单条 Issue `trace.md` 作为状态事实源，以及 Sprint/OpenSpec 作为交付事实源。但当需求或缺陷数量增长后，团队缺少一个按时间倒序浏览全局生命周期事件的轻量入口。

`docs/spec-logs/CHANGELOG.md` 已验证“目录级索引 + 单次事实源”的模式适合治理资产演进。REQ/BUG 也需要类似索引，但必须避免形成第二套状态账。

## 目标

- 在 `issues/requirements/` 与 `issues/bugs/` 根目录新增 `CHANGELOG.md`。
- 定义全局事件索引的记录字段、事件类型、安全边界和轻量必记策略。
- 同步 REQ/BUG 生命周期规则、文档治理、目录结构、上下文预算和相关 Agent 技能维护要求。
- 保持 `_registry.yaml`、单条 Issue `trace.md`、OpenSpec Change 与 Sprint 四件套的事实源地位不变。

## 非目标

- 不修改业务 `src/` 代码。
- 不改造 Workflow Sync 脚本实现。
- 不迁移历史 REQ/BUG 记录。
- 不将全局事件索引用作机器状态判断依据。

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
- `openspec validate add-issues-changelog-index`
- `python scripts/validate-sprint-scope.py sprint-002 --item add-issues-changelog-index`
