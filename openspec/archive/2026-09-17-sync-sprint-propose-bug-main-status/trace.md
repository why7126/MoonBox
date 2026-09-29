---
change_id: sync-sprint-propose-bug-main-status
sprint: sprint-007
status: applied
created_at: 2026-09-15 23:14:47
updated_at: 2026-09-15 23:24:10
owner: product
execution:
  schema_version: 1
  started_at: 2026-09-15 23:22:28
  completed_at: 2026-09-15 23:23:58
  last_event: opsx.apply
---

# Workflow Sync sprint.propose BUG 主状态同步 Trace

## Source

- Command: `/spec-opt 优化 Workflow Sync，让 sprint.propose 对聚焦 BUG 的 bug.md 主状态也自动同步，减少人工聚焦修正`
- Sprint: `iterations/archive/sprint-007/`

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 仅修改 Workflow Sync 治理脚本、单元测试、OpenSpec 文档和治理日志，不触达 API、DB、请求日志、行为事件、Task Trace、Web/管理端请求封装或对象存储。
validation: 聚焦 pytest、脚本编译、sprint.propose 真实 dry-run、上下文预算、目标 OpenSpec 语言、目标 Change validate、目录结构、Sprint scope 与 Workflow Sync check 通过。
```

## Implementation Notes

- 目标同步范围：`sprint.propose` 事件中由 `--req` 或 `--bug` 指定的聚焦 Issue。
- 目标文档：REQ 主文档 `requirement.md`，BUG 主文档 `bug.md`。
- 不同步范围：未聚焦 Issue、历史归档批量文档、语义不明的 `review.md` / `root-cause.md` / `workaround.md` 状态字段。

## 验证记录

| Time | Command | Result |
|---|---|---|
| 2026-09-15 23:10 | `python scripts/validate-change-identity.py --new-id sync-sprint-propose-bug-main-status` | pass |
| 2026-09-15 23:14 | `python scripts/validate-sprint-selection.py --sprint sprint-007` | pass，指定 active Sprint 可继续 |
| 2026-09-15 23:15 | `openspec new change sync-sprint-propose-bug-main-status` | pass |
| 2026-09-15 23:16 | `python scripts/add-sprint-scope-item.py --sprint sprint-007 --change sync-sprint-propose-bug-main-status ...` | pass，写入 Sprint scope |
| 2026-09-15 23:17 | `python scripts/sync-workflow-status.py --event opsx.propose --change sync-sprint-propose-bug-main-status --sprint auto` | pass，updated=0，skipped=17 |
| 2026-09-15 23:18 | `python -m py_compile scripts/workflow_sync/engine.py` | pass |
| 2026-09-15 23:18 | `python -m pytest tests/unit/test_workflow_sync_engine.py -k sprint_propose_syncs_focused_bug_primary_document` | pass，1 passed |
| 2026-09-15 23:19 | `python scripts/validate-sprint-scope.py sprint-007 --item sync-sprint-propose-bug-main-status` | pass |
| 2026-09-15 23:19 | `python scripts/validate-agent-context-budget.py` | pass |
| 2026-09-15 23:19 | `python scripts/validate-openspec-language.py --change sync-sprint-propose-bug-main-status --residual-report` | pass，未发现非当前 Change 中文残留 |
| 2026-09-15 23:20 | `python scripts/validate-directory-structure.py` | pass |
| 2026-09-15 23:21 | `openspec validate sync-sprint-propose-bug-main-status --strict` | pass |
| 2026-09-15 23:21 | `python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0023-requirement-center-acceptance-progress-task-classification --sprint sprint-007 --dry-run` | pass，Subdocuments checked=7，updated=1，验证聚焦 BUG 主文档进入同步路径；dry-run 未写入该 BUG |
| 2026-09-15 23:22 | `python scripts/sync-workflow-status.py --sprint auto --check` | pass，updated=0，skipped=17 |
| 2026-09-15 23:22 | `python scripts/sync-workflow-status.py --event opsx.start --change sync-sprint-propose-bug-main-status --sprint auto` | pass，updated=2 |
| 2026-09-15 23:23 | `python scripts/sync-workflow-status.py --event opsx.apply --change sync-sprint-propose-bug-main-status --sprint auto --dry-run` | pass，would update=3 |
| 2026-09-15 23:23 | `python scripts/sync-workflow-status.py --event opsx.apply --change sync-sprint-propose-bug-main-status --sprint auto` | pass，updated=3 |
| 2026-09-15 23:24 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change sync-sprint-propose-bug-main-status --sprint sprint-007 --json` | warning，usage_mode unavailable，no command-run token_count events |

## AI Usage

```yaml
status: warning
usage_mode: unavailable
command_run_count: 0
sprint_snapshot: skipped
reason: no-command-runs
recommended_action: 如需精确用量，使用显式 session JSONL 重跑 AI Usage Hook。
```
