---
change_id: fix-req-complete-status-projection-drift
change_type: fix
status: proposed
created_at: 2026-09-14 12:04:16
updated_at: 2026-09-14 12:12:50
source_bug: BUG-0020-req-complete-status-projection-drift
source_sprint: sprint-006
related_specs:
  - agent-workflow-tooling
---

# 修复 req.complete 状态投影漂移

## 背景

BUG-0020 记录了 `/req-complete` 后 REQ 状态投影可能残留 `draft` 或 `enriching` 的问题。以 REQ-0029 为例，trace 已进入 `enriching`，但 registry 与 CHANGELOG 仍显示 `draft`，需求中心卡片提示“存在数据漂移”。根因证据显示 Workflow Sync 对 `req.complete` 缺少聚焦事件的目标状态推进，导致同步逻辑沿用既有 trace 状态，无法稳定把需求推进到待评审态。

## 目标

- 让 `/req-complete` 成功后，聚焦 REQ 的 trace、registry、CHANGELOG 与当前态看板统一进入 `pending_review`。
- 覆盖 `draft`、`enriching` 等历史中间态，避免旧数据在完成事件后继续漂移。
- 补充 check 与回归用例，验证 `req.complete` 状态传播链路。

## 非目标

- 不改变正式业务 API、数据库结构、Web UI 或部署配置。
- 不重写 REQ/BUG 生命周期模型。
- 不在本 Change 中修复与 `req.complete` 无关的历史文档内容。

## 方案概述

Workflow Sync 需要把 `req.complete` 纳入聚焦事件状态目标表：当命令带有完整 REQ ID 时，状态派生不再读取旧 trace 状态作为最终状态，而是将聚焦 REQ 推进为 `pending_review`，随后刷新 trace lifecycle、registry、CHANGELOG、当前态投影与 Sprint/Issue 关联视图。实现时同时补充对应单元测试和命令级校验，确保历史 `draft`/`enriching` 输入均收敛到同一当前态。

## 影响面

- `scripts/workflow_sync/engine.py`
- Workflow Sync 相关单元测试
- OpenSpec `agent-workflow-tooling` 能力规格
- BUG-0020 与 sprint-006 的工作流链路元数据

## product_data_collection_observability

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本 Change 仅修改本地 Agent Workflow 治理脚本的状态投影逻辑，不新增或变更产品运行时 API、数据库、request_logs、usage_events、task_traces、task_trace_spans、对象存储、客户端请求封装或端侧链路字段。
  validation: 已通过 Workflow Sync 单元测试、req.complete 命令级 dry-run、bug.complete 命令级 dry-run、OpenSpec 校验和 Sprint Scope 校验证明治理链路状态传播一致。
```
