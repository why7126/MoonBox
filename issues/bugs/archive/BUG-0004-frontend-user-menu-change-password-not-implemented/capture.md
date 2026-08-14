---
bug_id: BUG-0004-frontend-user-menu-change-password-not-implemented
status: done
created_at: 2026-08-11 16:07:33
updated_at: 2026-08-13 22:48:16
severity_hint: medium
environment: local
related_requirement:
related_bug:
---

# 现象

前台用户菜单栏中，“修改密码”入口已经展示，但点击后没有打开修改密码弹窗，也没有触发密码修改流程。

# 复现步骤

1. 登录前台并进入需求中心页面。
2. 点击左侧底部用户头像或用户名，打开前台用户菜单。
3. 点击“修改密码”菜单项。

# 期望 vs 实际

- 期望：点击“修改密码”后打开修改密码弹窗；提交后调用 `/api/v1/admin/auth/change-password`；修改成功后清理前后台会话并跳转登录页。
- 实际：菜单入口已展示，但未实现点击行为，用户无法从前台完成自助修改密码。

# 附件

无
