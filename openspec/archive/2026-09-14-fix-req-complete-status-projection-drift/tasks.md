---
change_id: fix-req-complete-status-projection-drift
created_at: 2026-09-14 12:04:16
updated_at: 2026-09-14 12:12:50
source_bug: BUG-0020-req-complete-status-projection-drift
source_sprint: sprint-006
---

# Tasks

- [x] 1. 在 Workflow Sync 聚焦事件目标表中加入 `req.complete -> pending_review`。
- [x] 2. 确认 `req.complete` 写回 trace lifecycle、registry、CHANGELOG 与当前态看板时共用同一派生态。
- [x] 3. 补充 `req.complete` 从 `draft` 与 `enriching` 推进到 `pending_review` 的回归测试。
- [x] 4. 补充幂等测试，确认重复执行 `req.complete` 不会回退状态或产生漂移。
- [x] 5. 运行 Workflow Sync 相关单元测试和命令级校验。
- [x] 6. 更新 BUG-0020、sprint-006 与 OpenSpec 验收记录。
