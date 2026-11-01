---
title: 独立 Change 卡片更新时间缺失回归验收清单
created_at: '2026-10-30 09:48:10'
updated_at: 2026-11-01 08:06:41
acceptance_status: passed
---

# 独立 Change 卡片更新时间缺失回归验收清单

## 回归验收

7项验收通过，真实产品观察和合成回归分开记录。

- [x] AC-001 使用缺顶层时间但有execution时间的隔离样本复现，结果不再无解释地未知；兼容显示明确来源。
- [x] AC-002 新建 Change 生成合法 created_at/updated_at；有效变更刷新 updated_at，created_at 不变。
- [x] AC-003 opsx.start/apply/modify 等涉及时间更新的路径覆盖缺字段样本；不覆盖首次 execution.completed_at。
- [x] AC-004 同事件无实际变化重放不刷新业务时间；已完成对象不通过重放伪造历史时间。
- [x] AC-005 非法或完全缺失时间显示可理解缺口，不回退当前查询时间、文件mtime或复制时间。
- [x] AC-006 Asia/Shanghai 显示正确，活动与归档独立 Change、已有合法时间、REQ/BUG 卡均回归。
- [x] AC-007 新增元数据规则与 API 映射文档同步，真实产品刷新观察与合成回归分别报告。

## UI 证据

1440×900与390×844、深浅主题检查相关卡片状态，记录截图及按钮disabled/文本、字号、间距、颜色、overflow等样式；无需整页复刻用户截图。修复后重新采集，不沿用旧故障截图当通过证据。

## 验证记录

实现与验收已完成。证据：[完整验收报告](../../../../openspec/archive/2026-10-31-fix-standalone-change-updated-time/evidence/acceptance/20261031225550278663-da0cf131/summary.md)，[实施与视觉签认](../../../../openspec/archive/2026-10-31-fix-standalone-change-updated-time/verification.md)。原样本刷新显示“执行完成于 26/10/30 09:04”；无真实归档操作。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-11-01 08:06:41
accepted_by: workflow-sync
source_change: fix-standalone-change-updated-time
source_sprint: sprint-018
evidence: [openspec/archive/2026-10-31-fix-standalone-change-updated-time/evidence/acceptance/20261031225550278663-da0cf131/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

