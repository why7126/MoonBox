---
purpose: API Governance 生效规格
content: 统一响应、错误码、OpenAPI 元数据和后端分层基线
created_at: 2026-07-29 23:10:00
updated_at: 2026-07-29 23:10:00
owner: MoonBox 产品团队
---

# API 治理

## Purpose

定义 MoonBox REST API 的统一响应、错误码、OpenAPI 元数据和生成客户端契约基线，确保前端、后端、文档与测试围绕同一接口事实源交付。
## Requirements
### Requirement: 统一 API 响应

MoonBox SHALL 使用 `{ code, message, data }` 作为 API 响应基线结构。认证、当前用户、修改密码、个人资料、头像上传和头像读取相关接口 MUST 使用统一响应结构和受控错误码。

#### Scenario: 认证成功响应一致

- **GIVEN** 客户端调用 `POST /api/v1/auth/login`
- **WHEN** 登录成功
- **THEN** 响应体包含 `code: 0`、`message` 和 `data`
- **AND** `data` 包含 access token、token 类型、过期时间和当前用户摘要

#### Scenario: 认证与个人中心错误响应受控

- **WHEN** 登录失败、未认证、凭证过期、会话撤销、权限不足、账号不可用、头像上传失败、资料校验失败或密码规则失败
- **THEN** 系统返回统一响应结构
- **AND** 401 表示认证失败或会话失效
- **AND** 403 表示已认证但权限不足
- **AND** 响应不得泄露明文密码、access token、会话 ID 明文、密码哈希、对象存储密钥、签名凭证或 `.env` 内容

### Requirement: 错误码注册表

MoonBox SHALL 在 `src/backend/app/core/error_codes.py` 维护通用错误码，并在 `docs/standards/error-codes.md` 中说明。

#### Scenario: 错误码可追溯

- **GIVEN** 后端处理器需要返回标准错误
- **WHEN** 它选择错误码
- **THEN** 该错误码已在共享注册表中定义

### Requirement: OpenAPI 路由元数据

MoonBox API routes SHALL 声明 `response_model`、`tags` 和 `summary` 元数据。认证与个人中心 API 的 OpenAPI 契约 MUST 只暴露 `/api/v1/auth/*` 作为正式路径，并移除旧 `/api/v1/admin/auth/*` 路径。

#### Scenario: 统一认证路径进入 OpenAPI

- **GIVEN** 后端注册认证与个人中心路由
- **WHEN** OpenAPI 文档生成
- **THEN** 文档包含 `/api/v1/auth/login`
- **AND** 文档包含 `/api/v1/auth/logout`
- **AND** 文档包含 `/api/v1/auth/me`
- **AND** 文档包含 `/api/v1/auth/change-password`
- **AND** 文档包含 `/api/v1/auth/avatar` 或等价统一头像路径

#### Scenario: 旧后台认证路径不进入 OpenAPI

- **WHEN** OpenAPI 文档生成
- **THEN** 文档不得包含 `/api/v1/admin/auth/login`
- **AND** 文档不得包含 `/api/v1/admin/auth/logout`
- **AND** 文档不得包含 `/api/v1/admin/auth/me`
- **AND** 文档不得包含 `/api/v1/admin/auth/change-password`

#### Scenario: 生成客户端不引用旧路径

- **GIVEN** OpenAPI 客户端生成完成
- **WHEN** 开发者检索生成客户端和前端 API wrapper
- **THEN** 运行时代码不得继续引用 `/api/v1/admin/auth/*`
- **AND** 前端认证、当前用户、资料更新、修改密码和头像上传流程调用 `/api/v1/auth/*` 或等价统一路径

#### Scenario: 历史头像 URL 规范化为统一路径

- **GIVEN** 用户记录中仍保存 `/api/v1/admin/users/avatar/{filename}` 形式的历史头像 URL
- **WHEN** 系统返回登录用户摘要、当前用户摘要或后台用户列表摘要
- **THEN** 响应中的 `avatar_url` MUST 规范化为 `/api/v1/auth/avatar/{filename}`
- **AND** 系统 MUST NOT 重新注册 `/api/v1/admin/users/avatar/{filename}` 作为可用读取接口
