---
requirement_id: REQ-0016-unified-account-auth-api
status: done
priority: P1
created_at: 2026-08-12 00:11:02
updated_at: 2026-08-13 22:49:12
lifecycle:
  captured: 2026-08-12 00:11:02
  generated: 2026-08-12 00:14:27
  completed: 2026-08-12 10:04:53
  reviewed: 2026-08-12 10:15:13
  approved: 2026-08-12 10:15:13
iteration: sprint-002
openspec_changes:
  - change_id: update-unified-account-auth-api
    type: update
    status: archived
related_requirements:
  - REQ-0005-admin-auth-system
  - REQ-0010-admin-user-menu-password-change
  - REQ-0011-admin-user-menu-profile
  - REQ-0014-frontend-user-menu-profile
lifecycle_stage: archive
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
  - docs/knowledge-base/retrospectives/sprint-001-retrospective.md
cross_cutting_tags:
  - api
  - auth
  - frontend-session
  - media-upload
prototype_refs: []
---

# Trace

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 22:49:12 | /opsx-archive | Change `update-unified-account-auth-api` 已归档，状态同步完成。 |
| 2026-08-12 12:50:41 | /opsx-modify | Change `update-unified-account-auth-api` 验收返修已同步，待复验或 archive。 |
| 2026-08-12 11:44:57 | /opsx-apply | Change `update-unified-account-auth-api` apply 进行中，待补齐剩余验收。 |
| 2026-08-12 11:30:00 | req.opsx | 创建 OpenSpec Change `update-unified-account-auth-api`，Change 已归档并回填 Issue 状态为 done。 |
| 2026-08-12 10:23:30 | sprint.propose | 正式纳入 sprint-002，容量估算 M=3 人天；下一步执行 `/req-opsx REQ-0016-unified-account-auth-api` 创建 OpenSpec Change。 |
| 2026-08-12 10:15:13 | req.review | 需求评审通过；下一步先执行 `/sprint-propose --req REQ-0016-unified-account-auth-api` 纳入 Sprint。 |
| 2026-08-12 10:04:53 | req.complete | 补齐 user-stories、business-flow、acceptance；读取 sprint-001 复盘与 admin-media-upload-chain，写入 media-upload 横切 AC；本需求无新 UI prototype，下一步评审。 |
| 2026-08-12 00:14:27 | req.generate | 生成 requirement.md，确认统一 `/api/v1/auth/*` 为唯一正式认证与个人中心路径，所有登录用户可改昵称和头像，头像上传纳入统一 auth 范围。 |
| 2026-08-12 00:11:02 | req.capture | 创建需求记录：统一账号认证与个人中心 API，正式路径改为 `/api/v1/auth/*` 且不保留旧 `admin/auth` 路径。 |

- 阶段迁移：plan → review（/req-review --approve）
- 2026-08-13 22:48:07 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive update-unified-account-auth-api
