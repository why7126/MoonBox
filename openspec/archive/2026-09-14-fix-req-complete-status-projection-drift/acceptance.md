---
change_id: fix-req-complete-status-projection-drift
created_at: 2026-09-14 12:04:16
updated_at: 2026-09-14 12:12:50
source_bug: BUG-0020-req-complete-status-projection-drift
---

# Acceptance

## 验收标准

- [x] `req.complete` 对完整 REQ ID 执行后，trace 当前状态为 `pending_review`。
- [x] 同一 REQ 的 registry 记录刷新为 `pending_review`。
- [x] 同一 REQ 的 CHANGELOG entry 不再残留 `draft` 或 `enriching`，next action 指向 `/req-review <REQ-full-id>`。
- [x] 当前态看板不再提示该 REQ 存在状态数据漂移。
- [x] 回归测试覆盖 `draft -> pending_review` 与 `enriching -> pending_review`。
- [x] 重复执行 `req.complete` 保持幂等，不产生状态回退。

## 通过条件

全部验收标准通过，且 `openspec validate fix-req-complete-status-projection-drift --strict`、Workflow Sync 相关测试与 Sprint Scope 校验通过。

## 验收证据

| 时间 | 验证 | 结果 |
|---|---|---|
| 2026-09-14 12:16:41 | `uv run pytest tests/unit/test_workflow_sync_engine.py` | 11 passed |
| 2026-09-14 12:12:50 | `python scripts/sync-workflow-status.py --event req.complete --req REQ-0029-capture-multimodal-candidate-review --sprint auto --dry-run --output detail` | no delta；trace、registry、CHANGELOG 已一致 |
| 2026-09-14 12:12:50 | `python scripts/sync-workflow-status.py --event bug.complete --bug BUG-0020-req-complete-status-projection-drift --sprint auto --dry-run --output detail` | no delta；同域边界确认 |
