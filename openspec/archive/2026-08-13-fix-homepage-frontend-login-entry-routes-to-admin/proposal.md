---
change_id: fix-homepage-frontend-login-entry-routes-to-admin
type: fix
status: proposed
created_at: 2026-08-10 22:23:07
updated_at: 2026-08-10 22:23:07
source_bug: BUG-0002-homepage-frontend-login-entry-routes-to-admin
source_sprint: sprint-002
---

# 修复首页前台登录入口误跳后台登录页

## 背景

`BUG-0002-homepage-frontend-login-entry-routes-to-admin` 已确认：访问首页后点击「打开第一个项目」或「开启 MoonBox」会跳转 `/admin`，并展示管理后台登录页。该行为阻断首页前台入口关键链路，也混淆了前台用户入口与后台管理员入口。

## 变更内容

- 将首页两个前台 CTA 的点击行为改为打开前台登录页。
- 保持直接访问 `/admin` 时展示管理后台登录页或已登录后台。
- 保持具备权限的前台用户通过「进入后台」入口访问 `/admin`。
- 更新首页与后台路由回归测试，移除“首页 CTA 跳 `/admin`”的错误期望。

## 影响范围

- 影响 Web 前台首页和登录页入口行为。
- 影响 `homepage.test.tsx` 及必要的后台路由回归测试。
- 不涉及 API、数据库、对象存储、部署或后台认证契约变化。

## 回滚计划

如修复导致首页登录入口不可用，可回滚首页 CTA 处理函数与对应测试改动，并继续通过 `/#login` 作为临时前台登录直达入口。不得将长期回滚状态作为最终方案；后台 `/admin` 明确入口仍应保持独立可用。
