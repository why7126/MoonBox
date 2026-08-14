---
bug_id: BUG-0003-homepage-start-moonbox-should-open-login-route
status: archived
created_at: 2026-08-11 08:19:05
updated_at: 2026-08-13 22:50:17
severity_hint: medium
environment: local
related_requirement:
related_bug:
---

# 现象

访问本地官网后，点击首页「开启 MoonBox」进入的是 `/#login` hash 视图，而不是 `/login` 独立登录页。

# 复现步骤

1. 访问 `http://localhost:18102/`。
2. 点击首页「开启 MoonBox」。
3. 观察浏览器地址栏与展示页面。

# 期望 vs 实际

- 期望：点击「开启 MoonBox」后进入 `http://localhost:18102/login`，登录页作为独立前端路由展示。
- 实际：点击后进入 `http://localhost:18102/#login`，登录视图由首页 hash 状态控制，不是独立页面路由。

# 附件

暂无。
