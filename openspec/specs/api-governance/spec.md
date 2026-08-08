---
purpose: API Governance 生效规格
content: 统一响应、错误码、OpenAPI 元数据和后端分层基线
created_at: 2026-07-29 23:10:00
updated_at: 2026-07-29 23:10:00
owner: MoonBox 产品团队
---

# API 治理

## Requirements

### Requirement: 统一 API 响应

MoonBox SHALL 使用 `{ code, message, data }` 作为 API 响应基线结构。

#### Scenario: 健康检查响应一致

- **GIVEN** 客户端调用 `GET /health`
- **WHEN** 后端服务健康
- **THEN** 响应体包含 `code: 0`、`message: success` 和 `data` 对象

### Requirement: 错误码注册表

MoonBox SHALL 在 `src/backend/app/core/error_codes.py` 维护通用错误码，并在 `docs/standards/error-codes.md` 中说明。

#### Scenario: 错误码可追溯

- **GIVEN** 后端处理器需要返回标准错误
- **WHEN** 它选择错误码
- **THEN** 该错误码已在共享注册表中定义

### Requirement: OpenAPI 路由元数据

MoonBox API routes SHALL 声明 `response_model`、`tags` 和 `summary` 元数据。

#### Scenario: 路由校验通过

- **GIVEN** API 路由模块存在
- **WHEN** `scripts/validate-api-standard.py` 运行
- **THEN** 交付前可发现路由元数据违规项
