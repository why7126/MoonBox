---
change_id: derive-sprint-md-planning-sections
status: proposed
created_at: 2026-08-27 01:16:16
updated_at: 2026-08-27 01:25:00
---

# Tasks

## 1. OpenSpec 与 Sprint

- [x] 1.1 使用 OpenSpec CLI 创建 active Change。
- [x] 1.2 将纯治理 Change 纳入 `sprint-003` scope。

## 2. Workflow Sync 与校验

- [x] 2.1 增强 `scripts/workflow_sync/patch.py`，派生工作量与容量章节。
- [x] 2.2 增强 `scripts/workflow_sync/patch.py`，派生里程碑章节。
- [x] 2.3 增强 `scripts/workflow_sync/patch.py`，派生风险与缓冲章节。
- [x] 2.4 增强 `scripts/workflow_sync/patch.py`，派生知识库承接章节。
- [x] 2.5 增强 `scripts/validate-sprint-scope.py`，校验四个规划章节及 marker。

## 3. 规则、技能与日志

- [x] 3.1 同步 `rules/iterations-lifecycle.md`。
- [x] 3.2 同步 `.agents/skills/{workflow-sync,sprint-propose,sprint-apply}.md`。
- [x] 3.3 写入 `docs/spec-logs/YYYYMMDDhhmmss-governance-sprint-md-planning-sections.md`。
- [x] 3.4 更新 `docs/spec-logs/CHANGELOG.md`。

## 4. 验证与同步

- [x] 4.1 运行脚本级验证、上下文预算、OpenSpec 语言、目录结构、目标 Change validate 和 Sprint scope 校验。
- [x] 4.2 运行 Workflow Sync 与 AI Usage hook。
- [x] 4.3 复核聚焦 diff，确认本次未修改 `src/`。
