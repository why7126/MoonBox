---
purpose: 治理迭代日志
content: 为 spec-logs 变更历史新增跨项目落地提示词列
created_at: 2026-08-08 21:01:51
updated_at: 2026-08-08 21:05:10
owner: MoonBox 产品团队
---

# 为 spec-logs 变更历史新增跨项目落地提示词列

## 迭代目标

在 `docs/spec-logs/CHANGELOG.md` 的变更历史列表中新增“跨项目落地提示词”列，记录其他项目要落地同类治理规范时可直接使用的 Prompt。

## 变更摘要

- 更新 `CHANGELOG.md` 记录规则，新增“跨项目落地提示词”字段。
- 更新变更历史表格，新增“跨项目落地提示词”列。
- 为已有历史条目补充可复制 Prompt。
- 创建 `add-spec-logs-adoption-prompt-column` active OpenSpec Change，并补齐设计、任务、验收、验证计划和 delta spec。

## 影响范围

- 影响治理文档：`docs/spec-logs/CHANGELOG.md`。
- 影响 OpenSpec：`openspec/changes/add-spec-logs-adoption-prompt-column/`。
- 不影响 API、DB、Web、客户端、管理端、Orval 或 Docker Compose。

## 更新文件

- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260808210151-governance-spec-logs-adoption-prompt-column.md`
- `openspec/changes/add-spec-logs-adoption-prompt-column/`
- `iterations/change/sprint-001/sprint.yaml`
- `iterations/change/sprint-001/sprint.md`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate add-spec-logs-adoption-prompt-column`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item add-spec-logs-adoption-prompt-column`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-spec-logs-adoption-prompt-column --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-spec-logs-adoption-prompt-column --sprint sprint-001 --json`：通过，`usage_mode: actual`，warning 0。

## 影响矩阵

| 项 | 影响 |
|---|---|
| API | 不适用 |
| DB | 不适用 |
| Web | 不适用 |
| 客户端 | 不适用 |
| 管理端 | 不适用 |
| Orval | 不适用 |
| Docker Compose | 不适用 |

## 后续建议

后续维护 `CHANGELOG.md` 时，每条治理历史都应补充一段可复制、可迁移且不包含私有信息的跨项目落地 Prompt。
