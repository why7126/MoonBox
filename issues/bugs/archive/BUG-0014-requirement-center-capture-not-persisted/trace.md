---
bug_id: BUG-0014-requirement-center-capture-not-persisted
title: 需求中心新建 Capture 仅创建前端临时卡片，未持久化 REQ/BUG 目录、文档、注册表与索引
status: done
created_at: 2026-09-11 18:51:46
updated_at: 2026-09-14 08:50:10
lifecycle_stage: archive
related_requirement: REQ-0012-frontend-requirement-center
related_bug: null
iteration: sprint-005
openspec_changes:
  - change_id: fix-requirement-center-capture-persistence
    type: fix
    status: archived
lifecycle:
  captured: 2026-09-11 18:51:46
  generated: 2026-09-11 18:55:53
  completed: 2026-09-11 19:02:59
  reviewed: 2026-09-11 19:05:35
  approved: 2026-09-11 19:05:35
related_change: fix-requirement-center-capture-persistence
severity: high
---

# BUG-0014-requirement-center-capture-not-persisted Trace

## 当前状态

已纳入sprint-005，BUG保持迭代内/high/P1；关联Change fix-requirement-center-capture-persistence已验收态。AC-001至010回归与隔离真实观察通过，acceptance_status按流程为待定，等待最终签收与归档；父REQ-0012保持归档。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-09-14 08:50:10 | /opsx-archive | Change `fix-requirement-center-capture-persistence` 已归档，状态同步完成。 |
| 2026-09-12 21:16:08 | /opsx-modify | Change `fix-requirement-center-capture-persistence` 验收返修已同步，待复验或 archive。 |
| 2026-09-12 17:25:03 | /opsx-apply | Change `fix-requirement-center-capture-persistence` apply 完成，待 archive。 |
| 2026-09-11 18:51:46 | /bug-capture | captured | 新建 Capture 持久化缺失按单条记录；事实来源为用户反馈，严重度暂定 high。 |
| 2026-09-11 18:55:53 | /bug-generate | draft | 生成缺陷主文档，承接探索证据与验证边界。 |
| 2026-09-11 19:02:39 | /bug-complete | enriching | 补齐根因、规避、验收；关联 REQ-0012，等待根因证据门禁。 |
| 2026-09-11 19:02:59 | /bug-complete | 评审中 | 根因证据门禁通过（5 条）；10 项回归条件待实施，未执行真实部署验收。 |
| 2026-09-11 19:05:35 | /bug-review | approved | 根因与 10 项验收条件评审通过，常规修复；按流程迁入 review。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-14 08:50:10 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-requirement-center-capture-persistence
