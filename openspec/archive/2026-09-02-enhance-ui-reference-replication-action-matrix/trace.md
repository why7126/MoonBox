---
change_id: enhance-ui-reference-replication-action-matrix
status: archived
lifecycle_stage: archive
sprint: sprint-004
created_at: 2026-09-02 19:12:31
updated_at: 2026-09-13 23:45:17
---

# Trace: UI 参考稿复刻动作矩阵治理

## 状态

```yaml
status: archived
lifecycle_stage: archive
sprint: sprint-004
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本 Change 仅修改治理规则、Agent 技能和 OpenSpec 文档，不改变 API、DB、请求日志、行为事件、Task Trace、对象存储或 Web/管理端请求封装。
  validation: 上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope、Workflow Sync 和 AI Usage hook 均通过。
```

## 执行记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-02 19:12:31 | /spec-opt | 创建并应用 UI 参考稿复刻动作按钮矩阵治理 Change，补齐规则、标准、Skill、OpenSpec delta 和治理日志。 |
| 2026-09-02 19:12:31 | validation | `validate-agent-context-budget`、`validate-openspec-language`、`validate-directory-structure`、`openspec validate --strict`、`validate-sprint-scope`、Workflow Sync 和 AI Usage hook 通过。 |

## 影响面

- API：N/A，未修改接口契约。
- DB：N/A，未修改 schema、迁移、索引或保留周期。
- Web/管理端：N/A，未修改运行时代码；仅影响后续 UI Change 的治理门禁。
- 客户端生成/Orval：N/A，未修改 OpenAPI 或生成配置。
- Docker Compose：N/A，未修改部署拓扑或环境变量。

## 身份与归档状态纠正（2026-09-13 16:00:41）

原初建与强化均使用 `add-ui-reference-replication-governance`；本次保留初建身份，2026-09-02 强化独立为 `enhance-ui-reference-replication-action-matrix`。本记录是治理纠正时间，不代表实际归档时间。原 trace 状态为 applied，强化另有 lifecycle_stage: change；现按既有归档目录同步 archived/archive。原实施与验证记录保留，旧 ID 命令按当时身份解释。修正前文件校验和见 `openspec/archive/2026-09-13-repair-change-identity-uniqueness/evidence/before-sha256.json`。
