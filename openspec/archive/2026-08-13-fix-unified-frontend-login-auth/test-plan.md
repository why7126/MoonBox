---
change_id: fix-unified-frontend-login-auth
status: proposed
created_at: 2026-08-11 23:26:45
updated_at: 2026-08-11 23:26:45
---

# Test Plan

## 后端

- 运行相关 pytest 集成测试，覆盖统一登录、待激活自动激活、前台接口鉴权、后台 API 权限拒绝和冻结/删除拒绝。
- 回归后台管理员登录、退出、修改密码和会话撤销测试。

## 前端

- 运行相关 Vitest/Testing Library 测试，覆盖 `/login` 提交、默认进入前台、用户菜单后台入口显隐、需求中心上下文请求和后台入口保护。
- 回归登录页密码显示/隐藏、前台用户菜单个人资料、修改密码和从后台返回前台 session 状态。

## 文档与契约

- 校验 OpenAPI 与前端调用契约同步。
- 校验 `docs/03-api-index.md` 与 `docs/standards/authentication.md` 更新。
