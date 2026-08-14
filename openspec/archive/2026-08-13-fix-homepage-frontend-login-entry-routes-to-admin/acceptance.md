---
change_id: fix-homepage-frontend-login-entry-routes-to-admin
acceptance_status: passed
created_at: 2026-08-10 22:23:07
updated_at: 2026-08-10 23:34:40
source_bug: BUG-0002-homepage-frontend-login-entry-routes-to-admin
source_sprint: sprint-002
---

# 验收标准

## AC-001 首页主 CTA 打开前台登录页

点击首页「开启 MoonBox」后，系统必须展示前台登录页，不得跳转 `/admin`。

## AC-002 首页次 CTA 打开前台登录页

点击首页「打开第一个项目」后，系统必须展示前台登录页，不得跳转 `/admin`。

## AC-003 前台登录直达和返回保持可用

直接访问 `/#login` 时应展示前台登录页；点击「返回首页」后应恢复首页并清除登录状态。

## AC-004 后台明确入口保持可用

直接访问 `/admin` 或具备权限的用户点击「进入后台」时，仍可进入管理后台登录页或已登录后台。

## AC-005 测试覆盖错误期望回归

测试必须断言首页 CTA 打开前台登录页，并保留后台明确入口测试；不得继续断言首页 CTA 跳 `/admin`。

## AC-006 前台登录原型提交进入需求中心

在当前未接入真实前台认证的原型边界内，用户点击「登录并开启宝盒」后必须进入前台需求中心 `/requirements`；系统不得静默无响应，不得误跳后台登录页，不得发起真实认证请求。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-10 23:34:40
accepted_by: ai
source_change: fix-homepage-frontend-login-entry-routes-to-admin
source_sprint: sprint-002
evidence:
  - pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx
  - pnpm --dir src/web build
  - openspec validate fix-homepage-frontend-login-entry-routes-to-admin --strict
  - git diff --check -- <touched-files>
failed_items: []
source_event: opsx.modify
notes: 首页两个 CTA 已改为前台登录入口；后台明确入口回归保留；前台登录原型提交已进入前台需求中心。
```
