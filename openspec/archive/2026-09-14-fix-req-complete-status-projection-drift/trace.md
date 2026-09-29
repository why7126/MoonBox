---
change_id: fix-req-complete-status-projection-drift
status: applied
created_at: 2026-09-14 12:04:16
updated_at: 2026-09-14 12:15:18
source_bug: BUG-0020-req-complete-status-projection-drift
source_sprint: sprint-006
execution:
  schema_version: 1
  started_at: 2026-09-14 12:08:53
  completed_at: 2026-09-14 12:15:18
  last_event: opsx.apply
---

# Trace

## 链路

| 项 | 值 |
|---|---|
| Source BUG | BUG-0020-req-complete-status-projection-drift |
| Sprint | sprint-006 |
| Change | fix-req-complete-status-projection-drift |
| 目标规格 | agent-workflow-tooling |
| 当前状态 | applied |

## 缺陷证据映射

| BUG 证据 | Change 覆盖 |
|---|---|
| `req.complete` 未配置聚焦目标状态 | 任务 1 与 spec delta 固化 `pending_review` 派生 |
| 历史 `draft`/`enriching` 完成后残留 | 任务 3 覆盖两类旧态回归 |
| registry、CHANGELOG、当前态看板漂移 | 任务 2 与验收标准覆盖同源刷新 |
| 需要 check/回归用例 | 任务 3、4、5 与 test-plan 覆盖 |

## 变更记录

| 时间 | 事件 | 结果 |
|---|---|---|
| 2026-09-14 12:04:16 | `/bug-opsx BUG-0020-req-complete-status-projection-drift` | 创建 OpenSpec fix Change 提案 |
| 2026-09-14 12:12:50 | `/opsx-apply BUG-0020-req-complete-status-projection-drift` | 完成 Workflow Sync 状态传播修复、回归测试与命令级验证 |

## 验证记录

| 时间 | 验证 | 结果 |
|---|---|---|
| 2026-09-14 12:12:50 | Root Cause Evidence Gate | pass，confirmed，证据数 5 |
| 2026-09-14 12:12:50 | Sprint Inclusion Gate | pass，sprint-006 包含 BUG 与 Change；`opsx.apply --dry-run` 仅因 tasks 未完成阻断 |
| 2026-09-14 12:12:50 | Cross-cutting Apply Gate | n/a，无管理端 UI、表单、弹窗或媒体上传实现变更 |
| 2026-09-14 12:12:50 | 产品数据采集与链路观测门禁 | not_applicable，仅治理脚本状态投影，不改 API/DB/日志/事件/Task Trace/请求封装 |
| 2026-09-14 12:16:41 | `uv run pytest tests/unit/test_workflow_sync_engine.py` | 11 passed |
| 2026-09-14 12:12:50 | `req.complete` 命令级验证 | REQ-0029 真实同步后 dry-run no delta |
| 2026-09-14 12:12:50 | `bug.complete` 命令级验证 | dry-run no delta；同域行为确认 |
