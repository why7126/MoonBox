---
bug_id: BUG-0002-homepage-frontend-login-entry-routes-to-admin
acceptance_status: passed
created_at: 2026-08-10 21:52:49
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-001 首页主 CTA 打开前台登录页

访问 `http://localhost:18102` 后点击「开启 MoonBox」，必须展示前台登录页，不得跳转到 `/admin` 或展示管理后台登录页。

## AC-002 首页次 CTA 打开前台登录页

访问 `http://localhost:18102` 后点击「打开第一个项目」，必须展示前台登录页，不得跳转到 `/admin` 或展示管理后台登录页。

## AC-003 前台登录直达入口保持可用

直接访问 `http://localhost:18102/#login` 时，应展示前台登录页；点击「返回首页」后应回到首页并清除登录 hash。

## AC-004 管理后台明确入口保持可用

明确访问 `http://localhost:18102/admin` 时，仍应展示管理后台登录页或已登录管理后台；具备权限的前台用户点击「进入后台」时仍可进入 `/admin`。

## AC-005 回归测试覆盖正确入口语义

首页测试必须断言两个首页 CTA 打开前台登录页，而不是断言跳转 `/admin`。后台入口测试必须继续覆盖 `/admin` 或具备权限的「进入后台」入口。

## AC-006 前台登录原型提交进入需求中心

在当前未接入真实前台认证的原型边界内，用户点击「登录并开启宝盒」后必须进入前台需求中心 `/requirements`；不得静默无响应、不得误跳后台登录页、不得发起真实认证请求。

## 回归验证建议

- 运行前端单元测试，重点覆盖 `homepage.test.tsx` 与后台认证路由相关测试。
- 在浏览器验证首页两个 CTA、`/#login` 直达和返回首页。
- 在浏览器验证 `/admin` 直达仍进入后台登录或后台管理页。
- 检查前台入口与后台入口文案、路由和权限语义是否一致。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-homepage-frontend-login-entry-routes-to-admin
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

