---
purpose: REQ/BUG 全局事件索引治理日志
content: 记录 issues/requirements 与 issues/bugs 新增 CHANGELOG.md 及相关规则、技能维护要求
created_at: 2026-08-10 09:05:11
updated_at: 2026-08-10 09:05:11
owner: MoonBox 产品团队
---

# REQ/BUG 全局事件索引治理日志

## 迭代目标

为 `issues/requirements/` 与 `issues/bugs/` 新增目录级 `CHANGELOG.md`，用于全局记录 REQ/BUG 生命周期关键事件摘要，并明确其不替代 `_registry.yaml`、单条 Issue `trace.md`、OpenSpec Change 或 Sprint 四件套事实源。

## 变更摘要

- 新增 `issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md`。
- 明确 REQ/BUG 全局事件索引字段、事件类型、轻量必记策略和安全边界。
- 更新 REQ/BUG 生命周期、issues lifecycle、文档治理、目录结构和上下文预算规则。
- 更新 `/capture`、`/req-*`、`/bug-*`、`/sprint-propose`、`/opsx-apply`、`/opsx-archive` 与 `workflow-sync` 技能，要求关键生命周期事件维护全局索引。
- 新增 OpenSpec Change `add-issues-changelog-index` 并纳入 `sprint-002`。

## 影响范围

| 范围 | 影响 |
|---|---|
| API | 不涉及 |
| DB | 不涉及 |
| Web | 不涉及 |
| 客户端生成 / Orval | 不涉及 |
| 管理端 | 不涉及 |
| Docker Compose | 不涉及 |
| 治理规则 | 涉及 REQ/BUG lifecycle、目录结构、文档治理和上下文预算 |
| Agent 技能 | 涉及 capture、req、bug、sprint、opsx、workflow-sync |

## 更新文件

- `issues/requirements/CHANGELOG.md`
- `issues/bugs/CHANGELOG.md`
- `rules/requirement-management.md`
- `rules/bug-management.md`
- `rules/issues-lifecycle.md`
- `rules/document-governance.md`
- `rules/directory-structure.md`
- `rules/agent-context-budget.md`
- `.agents/skills/capture/SKILL.md`
- `.agents/skills/req-capture/SKILL.md`
- `.agents/skills/req-generate/SKILL.md`
- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/req-review/SKILL.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/bug-capture/SKILL.md`
- `.agents/skills/bug-generate/SKILL.md`
- `.agents/skills/bug-complete/SKILL.md`
- `.agents/skills/bug-review/SKILL.md`
- `.agents/skills/bug-opsx/SKILL.md`
- `.agents/skills/sprint-propose/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `.agents/skills/workflow-sync/SKILL.md`
- `openspec/changes/add-issues-changelog-index/`
- `iterations/change/sprint-002/sprint.yaml`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-sprint-scope.py sprint-002 --item add-issues-changelog-index`：通过。
- `openspec validate add-issues-changelog-index`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-issues-changelog-index --sprint auto`：通过，`Updated: 0`、`Errors: 0`。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-issues-changelog-index --sprint sprint-002 --json`：通过，`usage_mode: actual`、`command_run_count: 1`、`warning_count: 0`。

## 后续建议

- 后续可评估是否由 `scripts/sync-workflow-status.py` 自动写入 `issues/*/CHANGELOG.md`，减少各技能手工维护遗漏。
