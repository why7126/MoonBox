---
change_id: fix-frontend-user-menu-session-state
status: applied
created_at: 2026-08-11 18:55:00
updated_at: 2026-08-11 19:05:00
source_bug: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
---

# 验收计划

## 验收项

- AC-BUG-0005-001：从后台返回前台且上下文接口 pending 时，用户菜单不得显示“未登录”。
- AC-BUG-0005-002：上下文接口成功返回后，用户菜单展示接口用户、头像和后台访问权限。
- AC-BUG-0005-003：上下文接口返回 `401/403` 时，清理前后台 session 并进入 `/login`。
- AC-BUG-0005-004：前台登录、进入后台、退出登录、前台修改密码流程不回归。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-11 19:05:00
accepted_by: AI
evidence:
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run
  - pnpm --dir src/web build
failed_items: []
notes: 已覆盖 context pending 用户兜底、401/403 会话清理与前台登录/后台入口/退出/改密回归。
```
