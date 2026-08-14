---
bug_id: BUG-0002-homepage-frontend-login-entry-routes-to-admin
status: archived
created_at: 2026-08-10 20:07:31
updated_at: 2026-08-13 23:04:33
severity_hint: high
environment: local
related_requirement:
related_bug:
---

# 现象

访问本地首页后，点击首页前台入口按钮会误跳转到管理后台登录页。

# 复现步骤

1. 访问 `http://localhost:18102`。
2. 点击首页「打开第一个项目」。
3. 或点击首页「开启 MoonBox」。
4. 观察跳转目标与展示页面。

# 期望 vs 实际

- 期望：上述首页前台入口应打开前台登录页；后台登录页只应在明确访问 `/admin`，或点击具备权限的进入后台入口时出现。
- 实际：点击「打开第一个项目」或「开启 MoonBox」后跳转到 `/admin`，并展示管理后台登录页。

# 附件

暂无。
