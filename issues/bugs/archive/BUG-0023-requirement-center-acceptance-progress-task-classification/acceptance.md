---
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
title: 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务
acceptance_status: passed
created_at: 2026-09-15 22:47:41
updated_at: 2026-09-29 14:44:19
owner: 产品团队
---

# 验收标准

## 回归 AC

- [ ] AC-001：需求中心验收中卡片的研发进度来自 `tasks.md` 研发类 checkbox 完成数 / 研发类 checkbox 总数，不再混入测试和人工验收任务。
- [ ] AC-002：需求中心验收中卡片的测试进度来自 `tasks.md` 测试类 checkbox 完成数 / 测试类 checkbox 总数，不再使用 `acceptance.md`、`review.md`、`trace.md` 文档存在性作为测试完成度。
- [ ] AC-003：需求中心验收中卡片的人工验收进度来自 `tasks.md` 人工验收类 checkbox 完成数 / 人工验收类 checkbox 总数，不再因 `manual_acceptance_count <= 0` 默认显示 `1/1`。
- [ ] AC-004：首次 `/opsx-apply` 任务和后续 `/opsx-modify` 返修追加的 checkbox 任务均进入当前卡片进度统计。
- [ ] AC-005：`/opsx-modify` 返修实现任务未完成时，研发进度不得显示完成态。
- [ ] AC-006：`/opsx-modify` 返修回归测试、视觉证据或校验任务未完成时，测试进度不得显示完成态。
- [ ] AC-007：人工复验、人工确认或 sign-off 任务未完成时，人工验收进度不得显示完成态。
- [ ] AC-008：`acceptance-fixes.md` 作为完整返修台账事实源保留，但台账表格正文、说明文字、证据链接不直接计入卡片进度分母。
- [ ] AC-009：若 `tasks.md` 缺少可识别分类，需求中心应显示明确的待核实或降级提示，不得误报三类进度满格。
- [ ] AC-010：后端/API 响应、OpenAPI、前端客户端类型和前端渲染保持一致，新增或调整字段时同步相关文档。
- [ ] AC-011：前端回归测试覆盖 Image #1 等价场景：验收中卡片存在研发、测试、人工验收三类任务，卡片按分类进度展示。
- [ ] AC-012：后端聚合测试覆盖 `tasks.md` 分类解析、无分类降级、返修任务纳入、历史台账不计入分母。
- [ ] AC-013：后续修复同步沉淀 `tasks.md` 三类任务与 `/opsx-modify` 返修任务统计口径，避免生成任务和卡片统计再次漂移。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:44:19
accepted_by: workflow-sync
source_change: fix-requirement-center-acceptance-progress-task-classification
source_sprint: sprint-007
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

