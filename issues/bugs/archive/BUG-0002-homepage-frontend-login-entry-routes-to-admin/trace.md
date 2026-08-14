---
bug_id: BUG-0002-homepage-frontend-login-entry-routes-to-admin
status: done
severity: high
priority: P1
created_at: 2026-08-10 20:07:31
updated_at: 2026-08-13 23:04:21
lifecycle_stage: archive
lifecycle:
  captured: 2026-08-10 20:07:31
  generated: 2026-08-10 20:11:07
  completed: 2026-08-10 21:52:49
  reviewed: 2026-08-10 22:01:17
  approved: 2026-08-10 22:01:17
iteration: sprint-002
openspec_changes:
  - change_id: fix-homepage-frontend-login-entry-routes-to-admin
    type: fix
    status: archived
related_requirement: null
related_bug: null
---

# BUG Trace

## 基本信息

| 字段 | 值 |
|---|---|
| BUG | BUG-0002-homepage-frontend-login-entry-routes-to-admin |
| 标题 | 首页前台登录入口误跳后台登录页 |
| 严重等级 | high |
| 优先级 | P1 |
| 状态 | done |
| 阶段 | archive |
| 关联 Sprint | sprint-002 |
| 关联 Change | fix-homepage-frontend-login-entry-routes-to-admin |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 23:04:21 | /opsx-archive | Change `fix-homepage-frontend-login-entry-routes-to-admin` 已归档，状态同步完成。 |
| 2026-08-10 23:18:20 | /opsx-modify | Change `fix-homepage-frontend-login-entry-routes-to-admin` 验收返修已同步，待复验或 archive。 |
| 2026-08-10 23:01:05 | /opsx-apply | Change `fix-homepage-frontend-login-entry-routes-to-admin` apply 完成，待 archive。 |
| 2026-08-10 22:23:07 | bug.opsx | 创建 OpenSpec Change `fix-homepage-frontend-login-entry-routes-to-admin`。 |
| 2026-08-10 22:05:42 | sprint.include | 正式纳入 sprint-002，下一步创建 BUG 修复 OpenSpec Change。 |
| 2026-08-10 22:01:17 | bug.review.approve | 评审通过，确认需修复；下一步先纳入 Sprint。 |
| 2026-08-10 21:52:49 | bug.complete | 补齐根因、临时规避和验收标准，缺陷包进入待评审状态。 |
| 2026-08-10 20:11:07 | bug.generate | 生成 `bug.md`，明确复现步骤、期望实际、影响范围和严重等级说明。 |
| 2026-08-10 20:07:31 | bug.capture | 记录首页前台入口 CTA 误跳 `/admin` 并展示管理后台登录页的问题。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-08-13 22:48:07 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-homepage-frontend-login-entry-routes-to-admin
