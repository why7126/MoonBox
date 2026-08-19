---
change_id: add-opsx-modify-ui-screenshot-comparison-gate
status: applied
created_at: 2026-08-15 13:17:18
updated_at: 2026-08-15 13:22:00
---

# Tasks

## 1. 规范与技能

- [x] 1.1 更新 `/opsx-modify` 技能，在 UI 返修前置阶段加入附件截图逐项视觉对照表门禁。
- [x] 1.2 更新 `rules/ui-design.md`，将截图逐项对照纳入 UI 返修验收规则。
- [x] 1.3 更新 `docs/standards/prototype-ui-acceptance.md`，定义对照表字段、补证和 stale 规则。
- [x] 1.4 更新 `rules/agent-context-budget.md`，要求 UI 型 `/opsx-modify` 聚焦读取当前附件截图、UI Skeleton 和对照表证据。

## 2. OpenSpec 与治理日志

- [x] 2.1 新增 OpenSpec Change 文档和 delta spec。
- [x] 2.2 将纯治理 Change 纳入 `sprint-003`。
- [x] 2.3 写入 `docs/spec-logs/` 治理迭代日志并更新索引。

## 3. 验证

- [x] 3.1 运行上下文预算、OpenSpec 语言、目录结构和目标 Change 校验。
- [x] 3.2 运行 Workflow Sync 与 AI Usage Hook。
