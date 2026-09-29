---
title: OpenSpec CLI 模板标题中文化治理
status: applied
lifecycle_stage: change
created_at: 2026-09-15 00:23:57
updated_at: 2026-09-15 00:27:00
source_command: spec-opt
sprint: sprint-006
execution:
  schema_version: 1
  started_at: 2026-09-15 00:23:57
  completed_at: 2026-09-15 00:23:57
  last_event: opsx.apply
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 仅修改治理 Skill、规则、校验脚本和 OpenSpec 文档，不触达 API、DB、请求日志、行为事件、Task Trace、Web/管理端请求封装或对象存储。
  validation: 通过上下文预算校验、OpenSpec 中文校验、目录结构校验、目标 Change 校验、Sprint scope 校验和 Workflow Sync 校验确认。
---

# OpenSpec CLI 模板标题中文化治理

## 来源

- Command: `/spec-opt 对 OpenSpec CLI 模板标题做中文化，减少每次 req-opsx 后的重复修正`
- Sprint: `sprint-006`
- Change: `localize-openspec-cli-template-titles`

## 决策

- OpenSpec CLI template 只作为结构输入；项目文档落盘时标题中文优先。
- `/req-opsx` 与 `/bug-opsx` 同步采用标题映射，避免 REQ 与 BUG 链路行为分叉。
- 继续依赖 `validate-openspec-language.py --change <change-id> --residual-report` 捕获最终文档残留，并用上下文预算校验防止技能契约删除。

## 验证记录

| 时间 | 命令 | 结果 | 说明 |
|---|---|---|---|
| 2026-09-15 00:23:57 | `python scripts/validate-change-identity.py --new-id localize-openspec-cli-template-titles` | pass | Change ID 未冲突。 |
| 2026-09-15 00:23:57 | `openspec new change localize-openspec-cli-template-titles` | pass | CLI 创建 active Change。 |
| 2026-09-15 00:23:57 | `python scripts/add-sprint-scope-item.py --sprint sprint-006 --change localize-openspec-cli-template-titles ...` | pass | 纳入 Sprint 机器范围。 |
| 2026-09-15 00:25:00 | `python scripts/validate-agent-context-budget.py` | pass | 两个 opsx 技能中文化契约和既有命令输出契约通过。 |
| 2026-09-15 00:25:00 | `python scripts/validate-openspec-language.py --change localize-openspec-cli-template-titles --residual-report` | pass | 当前 Change 通过；未发现非当前 Change 中文残留。 |
| 2026-09-15 00:25:00 | `python scripts/validate-directory-structure.py` | fail | 既有根目录 `.vite` 未登记；非本轮新增或修改，记录为既有阻塞。 |
| 2026-09-15 00:25:00 | `openspec validate localize-openspec-cli-template-titles --strict` | pass | 目标 Change 结构校验通过。 |
| 2026-09-15 00:26:00 | `python scripts/sync-workflow-status.py --event opsx.apply --change localize-openspec-cli-template-titles --sprint auto` | pass | 解析到 `sprint-006`，Updated 3，Errors 0。 |
| 2026-09-15 00:26:00 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change localize-openspec-cli-template-titles --sprint sprint-006 --json` | warning | usage_mode unavailable，未发现可归因 command-run token 事件，不阻断本治理变更。 |
| 2026-09-15 00:26:00 | `python -m py_compile scripts/validate-agent-context-budget.py` | pass | 校验脚本语法通过。 |
| 2026-09-15 00:26:00 | `python scripts/validate-sprint-scope.py sprint-006 --item localize-openspec-cli-template-titles` | pass | Change 出现在 Sprint scope 与派生文档中。 |

## 影响说明

- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用。
- `src/` 业务代码：未修改。
- 文档安全：治理日志和 Change 文档不包含隐私、密钥、真实客户数据或未脱敏日志。
