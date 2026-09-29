---
title: data 目录持久存储与运行时边界治理
status: applied
lifecycle_stage: change
created_at: 2026-09-18 16:07:12
updated_at: 2026-09-18 16:07:12
source_command: spec-opt
sprint: sprint-007
execution:
  schema_version: 1
  started_at: 2026-09-18 16:07:12
  completed_at: 2026-09-18 16:07:12
  last_event: opsx.apply
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 仅修改目录治理规则、部署/数据库文档、校验脚本和 OpenSpec 治理事实源，不修改 API、数据库 schema、请求封装、行为事件、请求日志、Task Trace 或对象存储实现。
  validation: 通过目录结构校验、上下文预算校验、OpenSpec 中文校验、目标 Change 校验、Sprint scope 校验和 Workflow Sync 校验确认。
---

# data 目录持久存储与运行时边界治理

## 来源

- Command: `/spec-opt 统一 data 目录结构治理`
- Sprint: `sprint-007`
- Change: `standardize-data-runtime-storage-layout`

## 决策

- `data/sqlite/` 是本地 SQLite 唯一持久数据库目录。
- `data/s3/` 是本地 MinIO/S3 对象数据目录。
- `data/runtime/` 仅承载 Chat Platform、Governance、Codex 执行器等运行控制状态，不作为业务数据库或对象存储 canonical 根。
- `data/runtime/backend/sqlite/` 与 `data/runtime/backend/media/` 进入迁移期 legacy warning；本 Change 不移动或删除真实运行数据。

## 验证记录

| 时间 | 命令 | 结果 | 说明 |
|---|---|---|---|
| 2026-09-18 16:07:12 | `python scripts/validate-change-identity.py --new-id standardize-data-runtime-storage-layout` | pass | Change ID 未冲突。 |
| 2026-09-18 16:07:12 | `openspec new change standardize-data-runtime-storage-layout` | pass | CLI 创建 active Change。 |
| 2026-09-18 16:07:12 | `python scripts/add-sprint-scope-item.py --sprint sprint-007 --change standardize-data-runtime-storage-layout ...` | pass | 纳入 Sprint 机器范围，容量进入 warning。 |
| 2026-09-18 16:07:12 | `python -m py_compile scripts/validate-directory-structure.py` | pass | 校验脚本语法通过。 |
| 2026-09-18 16:07:12 | `python scripts/validate-directory-structure.py` | pass | 目录结构通过，legacy runtime backend 存储目录输出 warning。 |
| 2026-09-18 16:07:12 | `python scripts/validate-agent-context-budget.py` | pass | 上下文预算与命令契约校验通过。 |
| 2026-09-18 16:07:12 | `python scripts/validate-openspec-language.py --change standardize-data-runtime-storage-layout --residual-report` | pass | 当前 Change 通过；残留报告仅作分离提示。 |
| 2026-09-18 16:07:12 | `openspec validate standardize-data-runtime-storage-layout --strict` | pass | 目标 Change 结构校验通过。 |
| 2026-09-18 16:07:12 | `python scripts/validate-sprint-scope.py sprint-007 --item standardize-data-runtime-storage-layout` | pass | Change 出现在 Sprint scope 与派生文档中。 |
| 2026-09-18 16:07:12 | `python scripts/sync-workflow-status.py --event opsx.apply --change standardize-data-runtime-storage-layout --sprint auto` | pass | 解析到 `sprint-007`，同步成功。 |
| 2026-09-18 16:07:12 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change standardize-data-runtime-storage-layout --sprint sprint-007 --json` | warning | usage_mode unavailable，未发现可归因 command-run token 事件，不阻断本治理变更。 |

## 影响说明

- API/DB/Web/管理端/客户端/Orval：不适用。
- Docker Compose：未修改挂载路径，避免未迁移真实数据前切换运行库位置。
- `src/` 业务代码：未修改。
- 文档安全：治理日志和 Change 文档不包含隐私、密钥、真实客户数据或未脱敏日志。
