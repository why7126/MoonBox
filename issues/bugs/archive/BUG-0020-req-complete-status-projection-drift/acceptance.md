---
bug_id: BUG-0020-req-complete-status-projection-drift
title: req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移
acceptance_status: passed
created_at: 2026-09-14 11:42:05
updated_at: 2026-09-29 14:41:41
---

# 验收标准

## 回归 AC

- [ ] AC-001：新增单测覆盖 `req.complete` 聚焦事件，初始 `trace_status='draft'` 时派生状态为 `pending_review`。
- [ ] AC-002：新增单测覆盖 `req.complete` 聚焦事件，初始 `trace_status='enriching'` 时派生状态为 `pending_review`。
- [ ] AC-003：执行 `python scripts/sync-workflow-status.py --event req.complete --req <REQ-full-id> --sprint auto` 后，目标 REQ 的 `trace.md`、`issues/requirements/_registry.yaml` 和 `issues/requirements/CHANGELOG.md` 均为 `pending_review`。
- [ ] AC-004：需求中心当前态卡片不再因 `req.complete` 后 registry / CHANGELOG 残留旧状态而显示“存在数据漂移”。
- [ ] AC-005：重复执行同一 `req.complete` 同步保持幂等，不重复追加无意义变更记录，不把 `pending_review` 回退为 `draft` 或 `enriching`。
- [ ] AC-006：补充或确认 `bug.complete -> pending_review` 同域行为；若存在同类缺口，纳入同一修复与测试覆盖。
- [ ] AC-007：现有 `req.generate -> draft` 与 `bug.generate -> draft` 测试继续通过，不因新增事件目标态回归。

## 验收命令建议

```bash
uv run pytest tests/unit/test_workflow_sync_engine.py
python scripts/sync-workflow-status.py --event req.complete --req <REQ-full-id> --sprint auto --dry-run --output detail
```

## 未验收项

本阶段仅完成缺陷完善，不执行代码修复。上述 AC 在后续 OpenSpec Change 实施后验证。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: fix-req-complete-status-projection-drift
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

