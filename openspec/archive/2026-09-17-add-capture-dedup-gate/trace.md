---
change_id: add-capture-dedup-gate
title: Capture 创建前去重门禁 Trace
sprint: sprint-007
status: applied
created_at: 2026-09-16 22:42:16
updated_at: 2026-09-16 22:50:49
owner: product
execution:
  schema_version: 1
  started_at: 2026-09-16 22:49:32
  completed_at: 2026-09-16 22:50:49
  last_event: opsx.apply
---

# Capture 创建前去重门禁 Trace

## Source

- Command: `/spec-opt 为 capture、req-capture、bug-capture 增加创建前重复/相似 Issue 检查门禁`
- Sprint: `iterations/archive/sprint-007/`

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 仅修改 Agent 技能、治理规则、OpenSpec Change 和治理日志，不触达 API、DB、请求日志、行为事件、Task Trace、Web/管理端请求封装或对象存储。
validation: 上下文预算、OpenSpec 语言、目录结构、中文标题、目标 Change validate、Sprint scope、Workflow Sync apply 与全局 Workflow Sync check 均已通过；AI Usage hook 为 warning/unavailable，不阻断本次治理变更。
```

## Implementation Notes

- 创建前先读对应 `CHANGELOG.md` 与 `_registry.yaml`，只对疑似候选读取 `capture.md` / `trace.md` 必要片段。
- 疑似重复时输出候选 Issue、相似原因和处理选项，默认推荐关联或更新原 Issue。
- 用户确认非重复或候选仅弱相关后，才允许分配新 REQ/BUG ID 并落盘。

## 验证记录

| Time | Command | Result |
|---|---|---|
| 2026-09-16 22:42 | `python scripts/validate-change-identity.py --new-id add-capture-dedup-gate` | pass |
| 2026-09-16 22:45 | `python scripts/validate-sprint-selection.py --sprint sprint-007` | pass，指定 active Sprint 可继续 |
| 2026-09-16 22:45 | `python scripts/add-sprint-scope-item.py --sprint sprint-007 --change add-capture-dedup-gate ...` | pass，写入 Sprint scope |
| 2026-09-16 22:46 | `python scripts/sync-workflow-status.py --event opsx.propose --change add-capture-dedup-gate --sprint auto` | pass，updated=2，skipped=17 |
| 2026-09-16 22:49 | `python scripts/validate-agent-context-budget.py` | pass |
| 2026-09-16 22:49 | `python scripts/validate-openspec-language.py --change add-capture-dedup-gate --residual-report` | pass，未发现非当前 Change 中文残留 |
| 2026-09-16 22:49 | `python scripts/validate-directory-structure.py` | pass |
| 2026-09-16 22:49 | `openspec validate add-capture-dedup-gate --strict` | pass |
| 2026-09-16 22:49 | `python scripts/validate-sprint-scope.py sprint-007 --item add-capture-dedup-gate` | pass |
| 2026-09-16 22:50 | `python scripts/sync-workflow-status.py --event opsx.start --change add-capture-dedup-gate --sprint auto` | pass，updated=2，skipped=18 |
| 2026-09-16 22:50 | `python scripts/sync-workflow-status.py --event opsx.apply --change add-capture-dedup-gate --sprint auto --dry-run` | blocked，tasks 未全勾选；完成任务回填后重跑 |
| 2026-09-16 22:50 | `python scripts/sync-workflow-status.py --event opsx.apply --change add-capture-dedup-gate --sprint auto` | pass，updated=3，skipped=17 |
| 2026-09-16 22:50 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-capture-dedup-gate --sprint sprint-007 --json` | warning，usage_mode unavailable，no command-run token_count events |
| 2026-09-16 22:51 | `python scripts/sync-workflow-status.py --sprint auto --check` | warning，检测到 `iterations/archive/sprint-007/sprint.md` 派生漂移；已运行 apply 同步修复 |
| 2026-09-16 22:51 | `python scripts/sync-workflow-status.py --event opsx.apply --change add-capture-dedup-gate --sprint auto` | pass，updated=3，skipped=17 |
| 2026-09-16 22:51 | `python scripts/sync-workflow-status.py --sprint auto --check` | pass，updated=0，skipped=19 |
| 2026-09-16 22:52 | `python scripts/validate-document-titles.py --change add-capture-dedup-gate` | pass，6 份文件 |

## AI Usage

```yaml
status: warning
usage_mode: unavailable
command_run_count: 0
sprint_snapshot: skipped
reason: no-command-runs
recommended_action: 如需精确用量，使用显式 session JSONL 重跑 AI Usage Hook。
```
