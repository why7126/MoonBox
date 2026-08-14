---
bug_id: BUG-0006-frontend-login-needs-real-frontend-auth
status: done
lifecycle_stage: archive
severity: high
priority: P1
created_at: 2026-08-11 22:58:07
updated_at: 2026-08-13 22:51:59
related_requirement:
related_bug:
related_change: fix-unified-frontend-login-auth
iteration: sprint-002
openspec_changes:
  - change_id: fix-unified-frontend-login-auth
    type: fix
    status: archived
---

# BUG-0006 前台登录入口缺少真正前台用户认证能力

```yaml
bug_id: BUG-0006-frontend-login-needs-real-frontend-auth
status: done
lifecycle_stage: archive
severity: high
priority: P1
related_requirement:
related_bug:
related_change: fix-unified-frontend-login-auth
iteration: sprint-002
openspec_changes:
  - change_id: fix-unified-frontend-login-auth
    type: fix
    status: archived
```

## 当前状态

- 状态：done
- 阶段：archive
- 严重等级：high
- 优先级：P1
- 关联 Change：fix-unified-frontend-login-auth
- 下一步：无

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 22:51:29 | /opsx-archive | Change `fix-unified-frontend-login-auth` 已归档，状态同步完成。 |
| 2026-08-11 23:40:38 | /opsx-apply | Change `fix-unified-frontend-login-auth` apply 完成，待 archive。 |
| 2026-08-11 23:26:45 | bug.opsx | 创建 OpenSpec Change `fix-unified-frontend-login-auth`。 |
| 2026-08-11 23:22:56 | sprint.propose | 正式纳入 sprint-002，归档前已纳入 sprint-002。 |
| 2026-08-11 23:18:34 | bug.review | 评审通过，状态推进为 approved；下一步先纳入 Sprint。 |
| 2026-08-11 23:11:09 | bug.complete | 补齐 root-cause、workaround、acceptance，状态推进为 pending_review。 |
| 2026-08-11 23:07:58 | bug.generate | 生成 bug.md，明确统一登录、默认进入前台、后台角色展示后台入口、待激活用户首次登录自动激活为正常的目标行为。 |
| 2026-08-11 22:58:07 | bug.capture | 记录前台登录入口复用后台管理员认证，导致前台用户无法登录并提示无后台权限的缺陷；用户已选择修复方向 B：新增真正前台用户登录能力。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-08-13 22:48:35 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-unified-frontend-login-auth
