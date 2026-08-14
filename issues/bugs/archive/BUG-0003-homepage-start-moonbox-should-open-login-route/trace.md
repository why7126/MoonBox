---
bug_id: BUG-0003-homepage-start-moonbox-should-open-login-route
status: done
severity: medium
priority: P2
created_at: 2026-08-11 08:19:05
updated_at: 2026-08-13 22:49:27
lifecycle_stage: archive
lifecycle:
  captured: 2026-08-11 08:19:05
  generated: 2026-08-11 08:23:13
  completed: 2026-08-11 08:27:11
  reviewed: 2026-08-11 08:31:11
  approved: 2026-08-11 08:31:11
iteration: sprint-002
openspec_changes:
  - change_id: fix-homepage-login-route
    type: fix
    status: archived
related_requirement: null
related_bug: null
---

# BUG Trace

## 基本信息

| 字段 | 值 |
|---|---|
| BUG | BUG-0003-homepage-start-moonbox-should-open-login-route |
| 标题 | 官网开启 MoonBox 应进入 /login 独立登录页 |
| 严重等级 | medium |
| 优先级 | P2 |
| 状态 | done |
| 阶段 | archive |
| 关联 Sprint | sprint-002 |
| 关联 Change | fix-homepage-login-route |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 22:49:27 | /opsx-archive | Change `fix-homepage-login-route` 已归档，状态同步完成。 |
| 2026-08-11 12:14:08 | /opsx-modify | 验收返修前台用户菜单未显示头像；需求中心 BFF 已返回 `current_user.avatar_url`，前台菜单通过 admin token 读取受保护头像，空头像回退首字。 |
| 2026-08-11 09:08:47 | /opsx-modify | Change `fix-homepage-login-route` 验收返修已同步，待复验或 archive。 |
| 2026-08-11 08:54:03 | /opsx-apply | Change `fix-homepage-login-route` apply 完成，待 archive。 |
| 2026-08-11 08:41:00 | bug.opsx | 创建 OpenSpec Change `fix-homepage-login-route`。 |
| 2026-08-11 08:36:53 | sprint.include | 正式纳入 sprint-002，下一步创建 BUG 修复 OpenSpec Change。 |
| 2026-08-11 08:31:11 | bug.review.approve | 评审通过，确认需修复；下一步先纳入 Sprint。 |
| 2026-08-11 08:27:11 | bug.complete | 补齐根因、临时规避和验收标准，缺陷包进入待评审状态。 |
| 2026-08-11 08:23:13 | bug.generate | 生成 `bug.md`，明确现象、复现步骤、期望实际、影响范围和严重等级说明。 |
| 2026-08-11 08:19:05 | bug.capture | 记录官网「开启 MoonBox」跳转到 `/#login`，应进入 `/login` 独立登录页的问题。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-08-13 22:40:16 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-homepage-login-route
