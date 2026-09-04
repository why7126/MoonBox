---
change_id: enforce-openapi-client-generator-dependency-check
status: applied
source: spec-opt
sprint: sprint-003
created_at: 2026-08-27 08:06:17
updated_at: 2026-08-27 08:12:00
---

# 追溯记录

```yaml
lifecycle:
  status: applied
  sprint: sprint-003
  source: spec-opt
requirements: []
bugs: []
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: "本次只补强本地 OpenAPI 客户端生成脚本的依赖提示、fallback 与治理校验，不改变 API 请求头、响应字段、错误码、请求封装、行为事件、request_logs、usage_events、Task Trace 或数据库采集路径。"
  validation: "已通过脚本语法、实际生成脚本诊断路径、API 标准校验、上下文预算、OpenSpec 语言、目录结构、目标 Change 和 Workflow Sync 校验；AI Usage hook 已执行但因缺少可持久化 token_count 事件返回 usage_mode: unavailable。变更范围限定在治理脚本与文档。"
```

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-08-27 08:06:17 | /spec-opt | 创建 OpenAPI 客户端生成依赖提示治理 Change，并纳入 sprint-003。 |
| 2026-08-27 08:12:00 | /spec-opt | 补强 pnpm 版本错配诊断、Orval 缺失 fallback、API 标准校验和治理日志；状态 applied。 |
| 2026-08-27 08:12:00 | /workflow-sync | opsx.apply 同步完成，AI Usage hook 执行但无可持久化 token_count 事件。 |

## 验证记录

| 命令 | 结果 |
|---|---|
| `bash -n scripts/generate-openapi-client.sh` | pass |
| `scripts/generate-openapi-client.sh` | expected failure，OpenAPI JSON 已导出，客户端生成因缺少 `src/web/orval.config.ts` 被明确阻断并输出修复提示 |
| `python scripts/validate-api-standard.py` | pass |
| `python scripts/validate-agent-context-budget.py` | pass |
| `python scripts/validate-openspec-language.py` | pass |
| `python scripts/validate-directory-structure.py` | pass |
| `openspec validate enforce-openapi-client-generator-dependency-check` | pass |
| `python scripts/sync-workflow-status.py --event opsx.apply --change enforce-openapi-client-generator-dependency-check --sprint auto` | pass |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change enforce-openapi-client-generator-dependency-check --sprint sprint-003 --json` | warning，usage_mode unavailable |
