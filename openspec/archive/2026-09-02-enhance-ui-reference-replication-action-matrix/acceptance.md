---
change_id: enhance-ui-reference-replication-action-matrix
created_at: 2026-09-02 19:12:31
updated_at: 2026-09-13 16:00:41
---

# Acceptance: UI 参考稿复刻动作矩阵治理

## 验收标准

| 编号 | 标准 | 状态 |
|---|---|---|
| AC-1 | `docs/standards/prototype-ui-acceptance.md` 已包含动作按钮与 modal 组件族矩阵字段、适用条件和一次性组件族实现要求。 | passed |
| AC-2 | `rules/ui-design.md` 已将动作按钮矩阵纳入 UI Reference Replication Gate。 | passed |
| AC-3 | `req-complete`、`req-opsx`、`opsx-apply`、`opsx-modify`、`opsx-archive` 已承接矩阵门禁。 | passed |
| AC-4 | OpenSpec delta 已覆盖实现前矩阵、组件族一次性实现、返修回补和归档复核场景。 | passed |
| AC-5 | 治理校验、OpenSpec validate、Sprint scope、Workflow Sync 和 AI Usage hook 已记录结果。 | passed |

## 业务测试适用性

本 Change 仅修改治理资产，不修改 `src/` 业务运行时代码；前端、后端、数据库、API、客户端生成和 Docker Compose 业务测试不适用。
