---
change_id: add-change-delivery-evidence-source-check
title: Change 交付验证来源校验脚本
source: spec-opt
sprint: sprint-007
status: applied
created_at: 2026-09-15 09:38:43
updated_at: 2026-09-15 09:38:43
acceptance_refs:
  - trace.md
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本 Change 只新增治理校验脚本和规则说明，不修改业务 API、DB、请求日志、行为事件、Task Trace、Web 请求封装或对象存储。
  validation: 验证范围限定为脚本自身、治理文档、OpenSpec、Sprint scope、目录结构和需求中心识别口径。
execution:
  schema_version: 1
  started_at: 2026-09-15 09:38:43
  completed_at: 2026-09-15 09:38:43
  last_event: opsx.apply
---

# Trace

## 来源

- 命令：`/spec-opt`
- Sprint：`sprint-007`
- 类型：纯治理 Change，无 REQ/BUG 来源。

## 影响分析

```yaml
impact:
  scripts: true
  skills: true
  rules: true
  docs: true
  src_business: false
  api: false
  database: false
  web: false
```

## 验证记录

| 时间 | 验证项 | 结果 |
|---|---|---|
| 2026-09-15 09:38:43 | `python scripts/validate-change-delivery-evidence.py --change add-chat-agent-model-reasoning-selector` | pass，聚焦 Change 已有需求中心可识别验证来源。 |
| 2026-09-15 09:38:43 | `python scripts/validate-change-delivery-evidence.py --json` | pass，所有 active applied Change 均有需求中心可识别验证来源。 |
| 2026-09-15 09:38:43 | `python scripts/validate-agent-context-budget.py` | pass。 |
| 2026-09-15 09:38:43 | `python scripts/validate-openspec-language.py --change add-change-delivery-evidence-source-check --residual-report` | pass。 |
| 2026-09-15 09:38:43 | `python scripts/validate-directory-structure.py` | pass。 |
| 2026-09-15 09:38:43 | `openspec validate add-change-delivery-evidence-source-check --strict` | pass。 |
| 2026-09-15 09:38:43 | `python scripts/validate-sprint-scope.py sprint-007 --item add-change-delivery-evidence-source-check` | pass。 |
| 2026-09-15 09:38:43 | `python scripts/sync-workflow-status.py --event opsx.apply --change add-change-delivery-evidence-source-check --sprint auto` | pass。 |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-15 09:38:43 | spec.opt | 新增 applied Change 交付验证来源校验脚本，纳入 sprint-007 并完成治理文档同步。 |
