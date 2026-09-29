---
change_id: fix-req-complete-status-projection-drift
created_at: 2026-09-14 12:04:16
updated_at: 2026-09-14 12:12:50
source_bug: BUG-0020-req-complete-status-projection-drift
---

# Test Plan

## 自动化测试

- `uv run pytest tests/unit/test_workflow_sync_engine.py`
- 如测试文件拆分，运行新增 Workflow Sync 状态传播测试所在文件。

## 命令级校验

- `python scripts/sync-workflow-status.py --event req.complete --req <REQ-full-id>`
- `python scripts/validate-root-cause-evidence.py --bug BUG-0020-req-complete-status-projection-drift`
- `python scripts/validate-sprint-scope.py sprint-006 --item BUG-0020-req-complete-status-projection-drift`
- `openspec validate fix-req-complete-status-projection-drift --strict`

## 人工抽查

- 抽查 trace、registry、CHANGELOG 与当前态看板对应条目，确认状态统一为 `pending_review`。
- 抽查 CHANGELOG next action，确认进入 `/req-review <REQ-full-id>`。

## 执行结果

| 命令 | 结果 |
|---|---|
| `uv run pytest tests/unit/test_workflow_sync_engine.py` | 11 passed |
| `python scripts/sync-workflow-status.py --event req.complete --req REQ-0029-capture-multimodal-candidate-review --sprint auto` | Updated 1，修复 REQ-0029 trace 状态投影 |
| `python scripts/sync-workflow-status.py --event req.complete --req REQ-0029-capture-multimodal-candidate-review --sprint auto --dry-run --output detail` | no delta，幂等通过 |
| `python scripts/sync-workflow-status.py --event bug.complete --bug BUG-0020-req-complete-status-projection-drift --sprint auto --dry-run --output detail` | no delta，同域行为确认 |
