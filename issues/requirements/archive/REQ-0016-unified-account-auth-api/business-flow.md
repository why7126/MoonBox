---
requirement_id: REQ-0016-unified-account-auth-api
created_at: 2026-08-12 10:04:53
updated_at: 2026-08-12 10:04:53
---

# 业务流程

## 当前问题地图

```text
当前登录页
  -> POST /api/v1/admin/auth/login
  -> moonbox.frontend.session
  -> 如果是后台管理员，再写 moonbox.admin.session
  -> 前台需求中心 / 管理后台分别读取不同 session

结果：
  - 后端实际是一套登录态
  - API 名称却表现为后台认证
  - 前端状态容易出现前后台不一致
```

## 目标流程

```text
统一登录页 /login
  -> POST /api/v1/auth/login
  -> 服务端创建 session
  -> 返回 access_token + user + can_access_admin
  -> 前端写入 moonbox.session
  -> 默认进入 /requirements
       |
       +-- 普通前台用户：使用需求中心、个人资料、头像上传、修改密码
       |
       +-- 后台管理员：可从前台进入 /admin
             -> /api/v1/admin/** 再做后台权限校验
```

## 当前用户资料流程

```text
打开个人资料
  -> 读取 moonbox.session.user 或 GET /api/v1/auth/me
  -> 修改昵称 / 上传头像
       |
       +-- POST /api/v1/auth/avatar
       |     -> 对象存储写入
       |     -> 返回持久头像 URL
       |
       +-- PATCH /api/v1/auth/me
             -> 后端按当前 token 解析 user_id
             -> 更新 nickname/avatar_url
             -> 返回最新 user
             -> 前端刷新当前上下文和 moonbox.session
```

## 修改密码流程

```text
用户提交当前密码、新密码、确认新密码
  -> POST /api/v1/auth/change-password
  -> 校验当前密码与新密码规则
  -> 更新 password_hash
  -> 撤销该用户所有服务端会话
  -> 前端清理 moonbox.session
  -> 跳转 /login
```

## 破坏性迁移流程

```text
后端路由
  /api/v1/admin/auth/*  -> 删除/停止暴露
  /api/v1/auth/*        -> 唯一正式路径

前端调用
  adminAuth.ts / frontendSession.ts / 页面测试
  -> 合并为统一 auth/session 客户端

文档与契约
  docs/03-api-index.md
  docs/standards/authentication.md
  OpenAPI / Orval 客户端
  -> 全量切换到 /api/v1/auth/*
```

## 与关联需求差异

| 关联需求 | 已有能力 | 本需求变化 |
|---|---|---|
| REQ-0005-admin-auth-system | 后台认证、服务端会话、后台权限 | 将认证域从 `admin/auth` 改为统一 `/auth`，并不保留旧路径 |
| REQ-0010-admin-user-menu-password-change | 后台用户自助修改密码 | 扩展为所有登录用户可通过 `/auth/change-password` 修改密码 |
| REQ-0011-admin-user-menu-profile | 后台当前用户资料弹窗 | 资料更新接口统一到 `/auth/me`，不再限制为后台管理员 |
| REQ-0014-frontend-user-menu-profile | 前台个人资料弹窗与头像上传 | 上传、保存和头像读取迁移到 `/auth/*`，并改用统一 session |

## 风险与控制

| 风险 | 控制方式 |
|---|---|
| 旧路径删除导致测试或页面遗漏 | 以 grep、OpenAPI、前后端测试验证旧 `/api/v1/admin/auth/*` 不再出现 |
| 普通用户资料接口越权 | 后端只从 Bearer token 解析当前用户，不接受请求体目标用户 |
| 统一 session 后后台权限误判 | `/api/v1/admin/**` 后端继续 require admin 权限 |
| 头像上传本地可用但 Docker 不可用 | 在 Docker `:3000` 环境验收上传、读取、回显闭环 |
