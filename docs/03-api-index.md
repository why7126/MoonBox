---
purpose: API 索引
content: MoonBox REST API 模块、契约治理和客户端生成规则
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-08 22:18:00
owner: MoonBox 产品团队
---

# API 索引

MoonBox API 采用 REST 风格，由 FastAPI 暴露 OpenAPI 契约，前端通过 Orval 生成客户端。

| 模块 | 说明 | 状态 |
|---|---|---|
| Health | 健康检查 | planned |
| Admin Auth | 管理后台登录、退出、当前管理员和服务端会话 | done |
| Admin Users | 管理后台用户列表、创建、编辑、冻结/解冻、逻辑删除、重置密码和头像上传 | in_progress |
| Workspace | 组织空间和项目空间 | planned |
| Agent Workflow | 流程节点、状态流转、审批和执行记录 | planned |
| Knowledge Graph | 需求、设计、代码、测试、决策和经验关联 | planned |
| Assets | 文档与图片上传、签名 URL、元数据 | planned |

## 管理后台认证 API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/admin/auth/login` | 后台管理员账号密码登录；待激活后台管理员使用有效临时密码首次登录时自动激活为正常，并返回 access token、过期时间和管理员摘要 |
| POST | `/api/v1/admin/auth/logout` | 退出登录，撤销当前服务端会话 |
| GET | `/api/v1/admin/auth/me` | 读取当前后台管理员摘要 |

管理后台受保护接口使用 `Authorization: Bearer <access_token>`。access token 必须对应服务端会话记录，且会话未过期、未撤销、账号状态为“正常”并具备后台权限。待激活用户仅可在登录接口中完成首次登录激活，已冻结、已删除和前台用户不得进入管理后台。

## 管理后台用户 API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/admin/users` | 用户列表、关键词、角色、状态和分页查询；默认和“全部状态”不返回 `status=已删除`，已冻结用户返回 `status_before_freeze` 用于展示解冻恢复目标，`total` 按同规则计算 |
| POST | `/api/v1/admin/users` | 创建后台用户，用户名全局唯一且创建后不可修改；新用户状态为待激活，系统生成一次性临时密码并写入 `password_hash`，响应仅展示一次 |
| PUT | `/api/v1/admin/users/{user_id}` | 编辑头像、昵称和角色 |
| POST | `/api/v1/admin/users/{user_id}/freeze` | 冻结待激活或正常用户，记录 `status_before_freeze`，10 秒内使有效会话失效；重复冻结不得覆盖冻结前状态 |
| POST | `/api/v1/admin/users/{user_id}/unfreeze` | 解冻用户并恢复冻结前状态，待激活恢复待激活，正常恢复正常；缺少冻结前状态时返回受控错误 |
| DELETE | `/api/v1/admin/users/{user_id}` | 逻辑删除用户并保留审计 |
| POST | `/api/v1/admin/users/{user_id}/reset-password` | 重置密码，将新临时密码写入 `password_hash` 并撤销该用户会话，临时结果仅响应一次 |
| POST | `/api/v1/admin/users/avatar` | 上传头像到 MinIO `images/avatars/` 前缀，返回同会话可回显 URL |
| GET | `/api/v1/admin/users/avatar/{filename}` | 授权读取 MinIO 头像对象 |

管理端接口必须使用统一后台认证鉴权。`x-admin-role: admin` 仅为历史占位，不得作为正式权限来源。创建用户和重置密码返回的 `temporary_password` 属于一次性敏感结果，只允许响应给当前后台管理员，不得写入日志、埋点或前端持久化存储。临时密码可用于后台管理员首次登录激活或正常登录，不表示前台用户、已冻结或已删除用户可访问管理后台。

API 变更必须同步 OpenAPI、Orval 客户端、测试、`docs/03-api-index.md` 和相关 OpenSpec Change。
