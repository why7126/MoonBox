---
purpose: Workflow Sync req.complete 状态投影修复治理记录
content: 记录 req.complete/bug.complete 聚焦状态传播、旧式 openspec_changes 兼容和回归验证
created_at: 2026-09-14 13:11:05
updated_at: 2026-09-14 13:11:05
owner: MoonBox 产品团队
source_change: fix-req-complete-status-projection-drift
source_bug: BUG-0020-req-complete-status-projection-drift
---

# Workflow Sync req.complete 状态投影修复治理记录

## 背景

BUG-0020 发现 `/req-complete` 后 REQ 投影可能残留 `draft` 或 `enriching`，导致 trace、registry、CHANGELOG 与当前态看板不一致。根因是 Workflow Sync 缺少 `req.complete -> pending_review` 的聚焦事件目标态。

## 变更摘要

- 在 Workflow Sync 聚焦事件目标表中补齐 `req.complete -> pending_review`。
- 同步补齐 `bug.complete -> pending_review` 同域行为，并避免已进入 Sprint 的 BUG 被 complete 事件回退。
- `lifecycle.generated` 与 `lifecycle.completed` 仅在空值时写入，保证重复同步幂等。
- 读取端兼容旧式 `openspec_changes: [- change-id]`，写回端升级为 `change_id/status` 结构，确保 apply/archive 同步可追踪。

## 影响范围

- `scripts/workflow_sync/engine.py`
- `scripts/workflow_sync/patch.py`
- `scripts/workflow_sync/collect.py`
- `tests/unit/test_workflow_sync_engine.py`
- `openspec/archive/2026-09-14-fix-req-complete-status-projection-drift/`

## 验证结果

| 验证 | 结果 |
|---|---|
| `uv run pytest tests/unit/test_workflow_sync_engine.py` | 11 passed |
| `python scripts/sync-workflow-status.py --event req.complete --req REQ-0029-capture-multimodal-candidate-review --sprint auto --dry-run --output detail` | no delta |
| `python scripts/sync-workflow-status.py --event bug.complete --bug BUG-0020-req-complete-status-projection-drift --sprint auto --dry-run --output detail` | no delta |
| `openspec validate fix-req-complete-status-projection-drift --strict` | passed |
| `python scripts/sync-workflow-status.py --check --sprint auto` | passed |

## 跨项目落地提示词

请修复 Workflow Sync 中 complete 事件的状态传播：`req.complete` 和 `bug.complete` 应将补齐阶段的聚焦 Issue 推进到 `pending_review`，已进入 Sprint 或后续交付态的 Issue 不得被 complete 事件回退；trace、registry、CHANGELOG 必须使用同一派生态，生命周期时间戳只在空值时写入以保持幂等；同时兼容旧式 `openspec_changes` 标量列表并补充聚焦单元测试。

## 后续建议

无。
