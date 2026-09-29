---
title: 本地 Vite 缓存目录结构校验治理
status: applied
lifecycle_stage: change
created_at: 2026-09-15 00:30:08
updated_at: 2026-09-15 00:32:30
source_command: spec-opt
sprint: sprint-006
execution:
  schema_version: 1
  started_at: 2026-09-15 00:30:08
  completed_at: 2026-09-15 00:30:08
  last_event: opsx.apply
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 仅修改目录结构规则、校验脚本、Git 忽略边界和 OpenSpec 文档，不触达 API、DB、请求日志、行为事件、Task Trace、Web/管理端请求封装或对象存储。
  validation: 通过目录结构校验、上下文预算校验、OpenSpec 中文校验、目标 Change 校验、Sprint scope 校验和 Workflow Sync 校验确认。
---

# 本地 Vite 缓存目录结构校验治理

## 来源

- Command: `/spec-opt 处理根目录 .vite 未登记导致目录结构校验失败`
- Sprint: `sprint-006`
- Change: `ignore-local-vite-cache-directory`

## 决策

- `.vite/` 是本地工具缓存，不登记为正式项目顶层目录。
- `.vite/` 必须被 `.gitignore` 覆盖，目录结构校验允许忽略。
- 其它未知根目录仍保持阻断，避免借本次修复放宽目录边界。

## 验证记录

| 时间 | 命令 | 结果 | 说明 |
|---|---|---|---|
| 2026-09-15 00:30:08 | `python scripts/validate-change-identity.py --new-id ignore-local-vite-cache-directory` | pass | Change ID 未冲突。 |
| 2026-09-15 00:30:08 | `openspec new change ignore-local-vite-cache-directory` | pass | CLI 创建 active Change。 |
| 2026-09-15 00:31:00 | `python scripts/add-sprint-scope-item.py --sprint sprint-006 --change ignore-local-vite-cache-directory ...` | pass | 纳入 Sprint 机器范围。 |
| 2026-09-15 00:31:00 | `python scripts/validate-directory-structure.py` | pass | 根目录 `.vite/` 存在时目录结构校验通过。 |
| 2026-09-15 00:31:00 | `python -m py_compile scripts/validate-directory-structure.py` | pass | 校验脚本语法通过。 |
| 2026-09-15 00:31:00 | `python scripts/validate-agent-context-budget.py` | pass | 上下文预算与命令契约校验通过。 |
| 2026-09-15 00:31:00 | `python scripts/validate-openspec-language.py --change ignore-local-vite-cache-directory --residual-report` | pass | 当前 Change 通过；未发现非当前 Change 中文残留。 |
| 2026-09-15 00:31:00 | `openspec validate ignore-local-vite-cache-directory --strict` | pass | 目标 Change 结构校验通过。 |
| 2026-09-15 00:32:00 | `python scripts/sync-workflow-status.py --event opsx.apply --change ignore-local-vite-cache-directory --sprint auto` | pass | 解析到 `sprint-006`，Updated 2，Errors 0。 |
| 2026-09-15 00:32:00 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change ignore-local-vite-cache-directory --sprint sprint-006 --json` | warning | usage_mode unavailable，未发现可归因 command-run token 事件，不阻断本治理变更。 |
| 2026-09-15 00:32:00 | `python scripts/validate-sprint-scope.py sprint-006 --item ignore-local-vite-cache-directory` | pass | Change 出现在 Sprint scope 与派生文档中。 |

## 影响说明

- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用。
- `src/` 业务代码：未修改。
- 文档安全：治理日志和 Change 文档不包含隐私、密钥、真实客户数据或未脱敏日志。
