---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
acceptance_status: passed
created_at: 2026-09-14 10:23:16
updated_at: 2026-09-29 14:41:41
owner: 产品团队
---

# 验收标准

## 回归验收项

- [x] AC-001：当独立 Change 处于验收中，且 trace 中存在非空 `## 验证摘要` 章节时，需求中心卡片不展示“验收来源待核实：未找到交付验证记录”。
- [x] AC-002：当独立 Change 处于验收中，且 trace 中存在非空 `## Validation Log` 章节时，需求中心卡片不展示“验收来源待核实：未找到交付验证记录”。
- [x] AC-003：既有可识别来源继续有效，包括非空 `acceptance.md`、非空 `verification.md`、非空 `## 验证记录`、非空 `## 验收记录`、非空 `## 验证结果` 和非空 `## 验收结果`。
- [x] AC-004：显式 `acceptance_refs` 的安全边界保持不变；无效、越界、缺失或空文件必须展示具体待核实原因，不得回退掩盖错误。
- [x] AC-005：验收来源存在不等于自动验收通过；tasks 全勾、开发完成状态或文件存在不得单独推断归档可通过。
- [x] AC-006：对 `refresh-issue-index-after-archive-promotion`、`enhance-workflow-sync-current-status-block` 或等价合成样本，页面卡片不再误报“未找到交付验证记录”。

## 验证建议

- 增加后端单元测试覆盖 `## 验证摘要` 与 `## Validation Log`。
- 复用或扩展 `src/backend/tests/test_change_visibility.py` 中独立 Change 交付来源测试。
- 如涉及前端展示，补充需求中心卡片渲染回归，确认后端不返回阻塞原因时前端不显示红色阻塞提示。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: fix-standalone-change-acceptance-source
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

