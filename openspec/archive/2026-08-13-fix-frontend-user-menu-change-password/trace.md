---
change_id: fix-frontend-user-menu-change-password
type: fix
status: applied
created_at: 2026-08-11 17:37:04
updated_at: 2026-08-12 13:43:11
source_bug: BUG-0004-frontend-user-menu-change-password-not-implemented
sprint: sprint-002
---

# Change Trace

## 关联对象

| 类型 | ID | 说明 |
|---|---|---|
| BUG | BUG-0004-frontend-user-menu-change-password-not-implemented | 前台用户菜单栏修改密码入口未实现 |
| Sprint | sprint-002 | 已纳入迭代 |

## 状态

```yaml
change_id: fix-frontend-user-menu-change-password
status: applied
source_bug: BUG-0004-frontend-user-menu-change-password-not-implemented
sprint: sprint-002
implementation:
  files:
    - src/web/src/styles/globals.css
    - src/backend/app/api/v1/admin_auth.py
    - src/backend/app/repositories/admin_auth.py
    - src/web/src/pages/admin/adminAuth.ts
    - src/web/src/pages/admin/AdminUserManagementPage.tsx
    - src/web/src/pages/catalog/RequirementCenterPage.tsx
    - src/web/src/requirement-center.test.tsx
validation:
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - uv run pytest tests/integration/api/test_admin_users.py
  - 1440px Playwright computed style and screenshot for frontend change-password modal
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
incident_log: not_applicable
```

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-11 17:37:04 | bug.opsx | 从 BUG-0004 创建 OpenSpec 修复 Change。 |
| 2026-08-11 17:44:20 | opsx.apply | 复用后台修改密码弹窗，接入前台菜单点击行为；成功后清理前后台会话并跳转 `/login`，失败时保留弹窗与会话。 |
| 2026-08-11 17:44:20 | validation | 前端单测与生产构建通过；无需沉淀 `docs/knowledge-base/incidents/`，本次为窄范围交互漏绑修复。 |
| 2026-08-11 18:00:31 | opsx.modify | 验收反馈指出前台修改密码弹窗样式不可读；已在 `.requirement-center .admin-modal-backdrop` 桥接后台弹窗 `--admin-*` 变量到前台 `--rc-*` token。 |
| 2026-08-11 18:00:31 | validation | 前端单测、生产构建、OpenSpec 校验和 1440px computed style/截图验收通过；截图 `/tmp/moonbox-bug0004-change-password-readable-1440.png`。 |
| 2026-08-11 23:49:27 | opsx.modify | 验收反馈指出普通前台用户仅有 frontend session 时改密提示登录失效；`changeAdminPassword()` 已回退使用 `moonbox.frontend.session.access_token`。 |
| 2026-08-11 23:49:27 | validation | 前端单测与生产构建通过，覆盖 `Bearer front-token` 调用改密接口、成功后清理前后台 session 并跳转 `/login`。 |
| 2026-08-12 00:00:17 | opsx.modify | 验收反馈指出普通前台用户调用改密接口被后端要求后台管理员权限；`/change-password` 已改为登录用户自助改密权限，仓储层移除后台管理员角色限制。 |
| 2026-08-12 00:00:17 | validation | 后端集成测试通过，覆盖普通前台用户改密成功、旧 session 失效、新密码可登录，且后台用户管理接口仍返回 403。 |
| 2026-08-12 13:43:11 | opsx.modify | 验收反馈指出旧接口错误会与当前字段校验错误同时展示；已在任一密码字段变更时清理旧提交级错误。 |
| 2026-08-12 13:43:11 | validation | 前端单测与生产构建通过，覆盖接口错误后编辑字段只保留当前字段级错误。 |
