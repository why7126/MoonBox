---
bug_id: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
status: done
created_at: 2026-08-11 18:16:00
updated_at: 2026-08-13 22:45:08
severity_hint: medium
environment: local
related_requirement:
related_bug:
---

# 现象

从后台返回前台时，前台用户菜单栏会短暂或持续显示“未登录”。

# 复现步骤

1. 登录 MoonBox 并进入前台需求中心。
2. 通过前台用户菜单进入后台。
3. 再从后台返回前台需求中心。
4. 观察前台左侧底部用户菜单栏的用户名与头像区域。

# 期望 vs 实际

- 期望：返回前台后，用户菜单应保持显示当前登录用户；如果登录态确实失效，应清晰跳转登录页或给出一致的失效反馈。
- 实际：用户菜单会显示“未登录”；在接口加载较慢、前后台 session 不同步或鉴权请求失败时，可能持续停留在“未登录”状态。

# 附件

无
