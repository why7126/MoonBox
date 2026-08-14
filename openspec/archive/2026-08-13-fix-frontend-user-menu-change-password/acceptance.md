---
change_id: fix-frontend-user-menu-change-password
acceptance_status: passed
created_at: 2026-08-11 17:37:04
updated_at: 2026-08-12 13:43:11
source_bug: BUG-0004-frontend-user-menu-change-password-not-implemented
---

# 验收计划

## 验收来源

本 Change 继承 `BUG-0004-frontend-user-menu-change-password-not-implemented/acceptance.md` 中 AC-001 至 AC-006。

## 必须通过

- 前台用户菜单点击“修改密码”打开弹窗。
- 前台改密提交调用既有 `/api/v1/admin/auth/change-password`。
- 普通前台用户仅有 frontend session token 时，前台改密提交使用 frontend token，不提示登录失效。
- 后端允许正常登录的前台普通用户修改自己的密码，同时继续阻止其访问后台管理接口。
- 成功后清理前后台会话并跳转 `/login`。
- 失败时保留弹窗与会话。
- 新密码确认不一致时不发起请求。
- 后台修改密码流程不回归。
- 前台修改密码弹窗样式可读可填写，不受后台主题变量作用域缺失影响。
- 用户修改任一密码输入项后，旧提交级错误被清理，不与当前字段级错误同时展示。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-11 17:44:20
accepted_by: Codex
evidence:
  - pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx --run
  - pnpm --dir src/web build
  - uv run pytest tests/integration/api/test_admin_users.py
  - 1440px Playwright computed style: input color rgb(231, 232, 243), background rgb(14, 16, 35), border rgba(234, 242, 255, 0.18)
  - /tmp/moonbox-bug0004-change-password-readable-1440.png
failed_items: []
source_event: opsx.modify
notes: 已覆盖前台菜单打开弹窗、成功改密请求体与授权头、前后台会话清理、`/login` 跳转、接口失败保留弹窗与会话、确认密码不一致阻止提交、旧接口错误在继续编辑密码字段时清理、后台改密回归、普通前台用户仅有 frontend session token 时的改密提交、普通前台用户后端自助改密成功且后台管理接口仍 403，以及前台复用后台弹窗时的主题 token 桥接与 1440px 可读性验收。
```
