---
bug_id: BUG-0008-admin-users-self-freeze-delete-not-forbidden
status: done
lifecycle_stage: archive
severity: high
priority: P1
created_at: 2026-08-12 13:39:06
updated_at: 2026-08-13 22:42:01
related_requirement:
related_bug:
related_change: fix-admin-user-self-freeze-delete-protection
iteration: sprint-002
openspec_changes:
  - change_id: fix-admin-user-self-freeze-delete-protection
    type: fix
    status: archived
---

# BUG-0008 管理后台登录用户不能冻结和删除自己

```yaml
bug_id: BUG-0008-admin-users-self-freeze-delete-not-forbidden
status: done
lifecycle_stage: archive
severity: high
priority: P1
related_requirement:
related_bug:
related_change: fix-admin-user-self-freeze-delete-protection
iteration: sprint-002
openspec_changes:
  - change_id: fix-admin-user-self-freeze-delete-protection
    type: fix
    status: archived
```

## 当前状态

- 状态：done
- 阶段：archive
- 严重等级：high
- 优先级：P1
- 关联 Change：fix-admin-user-self-freeze-delete-protection
- 下一步：无

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 22:41:26 | /opsx-archive | Change `fix-admin-user-self-freeze-delete-protection` 已归档，状态同步完成。 |
| 2026-08-12 14:19:28 | /opsx-modify | Change `fix-admin-user-self-freeze-delete-protection` 验收返修已同步，待复验或 archive。 |
| 2026-08-12 14:07:24 | /opsx-apply | Change `fix-admin-user-self-freeze-delete-protection` apply 完成，待 archive。 |
| 2026-08-12 14:00:30 | bug.opsx | 创建 OpenSpec Change `fix-admin-user-self-freeze-delete-protection`。 |
| 2026-08-12 13:56:45 | sprint.propose | 正式纳入 sprint-002，归档前已纳入 sprint-002。 |
| 2026-08-12 13:53:37 | bug.review | 评审通过，状态推进为 approved；下一步先纳入 Sprint。 |
| 2026-08-12 13:51:18 | bug.complete | 补齐 root-cause、workaround、acceptance，状态推进为 pending_review，待评审确认是否修复。 |
| 2026-08-12 13:43:11 | bug.generate | 生成 bug.md，明确当前登录用户自冻结/自删除应后端 403 拒绝、前端隐藏或禁用危险操作，并补充 API 与前端回归测试。 |
| 2026-08-12 13:39:06 | bug.capture | 记录管理后台当前登录用户不得冻结或删除自己的缺陷；后端应 403 拒绝，前端应隐藏或禁用当前账号危险操作，并补充 API 与前端回归测试。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-08-13 22:40:16 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-admin-user-self-freeze-delete-protection
