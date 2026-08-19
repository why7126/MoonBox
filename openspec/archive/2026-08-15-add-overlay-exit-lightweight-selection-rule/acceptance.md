---
change_id: add-overlay-exit-lightweight-selection-rule
status: applied
created_at: 2026-08-15 15:24:58
updated_at: 2026-08-15 15:24:58
---

# Acceptance: 浮层退出路径与轻量选择确认规则

## 验收要点

- `rules/ui-design.md` 明确要求浮层交互必须有退出路径。
- 轻量选择场景明确优先选择即应用、点击外部关闭等低摩擦模式。
- 高成本编辑、提交、删除、权限或不可逆动作仍保留确认按钮使用条件。
- 本次变更未触碰 `src/` 业务代码、API、数据库、部署和安全实现。
