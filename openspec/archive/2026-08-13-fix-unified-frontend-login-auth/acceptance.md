---
change_id: fix-unified-frontend-login-auth
status: proposed
created_at: 2026-08-11 23:26:45
updated_at: 2026-08-11 23:26:45
source_bug: BUG-0006-frontend-login-needs-real-frontend-auth
---

# 验收计划

- 普通前台用户可登录并默认进入前台。
- 待激活前台用户和后台管理员首次登录后自动激活为正常。
- 后台管理员和超级管理员登录后默认进入前台，并在用户菜单显示“进入后台”。
- 普通前台用户不显示“进入后台”，且不能访问后台页面或后台 API。
- 冻结、删除、账号不存在、密码错误均无法登录，且不创建有效会话。
- 需求中心前台上下文接口接受统一登录态，不要求后台管理员角色。
- OpenAPI、API 文档、认证文档、前后端测试同步完成。
