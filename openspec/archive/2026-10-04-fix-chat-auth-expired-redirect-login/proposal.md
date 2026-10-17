---
title: Chat 工作台登录失效重定位修复提案
change_id: fix-chat-auth-expired-redirect-login
source_bug: BUG-0024-login-expired-refresh-not-redirect-login
change_type: fix
created_at: 2026-10-04 11:18:13
updated_at: 2026-10-04 11:18:13
owner: MoonBox 产品团队
---

# Chat 工作台登录失效重定位修复提案

## 背景

BUG-0024 已确认：用户在本地仍保留前端会话但服务端认证失效后刷新 Chat 工作台 `/chat`，页面继续停留在受保护工作台，仅显示“登录已失效，请重新登录”或“重新连接”。浏览器 Network 中 `spaces`、`messages`、`projects`、`capabilities` 等受保护请求返回 401，选中的 `GET /api/v1/chat/spaces` 响应体为 `code: 1001`、`message: "认证或权限校验失败"`、`data: null`。

根因是 Chat 工作台入口只凭本地 session 存在放行，Chat API 收到 401 后只抛出页面错误，没有统一清理前端会话、触发路由重算并重定位到 `/login`。服务端已拒绝访问，暂无越权或数据损坏证据，但用户恢复路径不完整。

## 变更内容

- 为 Chat 工作台增加登录失效恢复契约：受保护 Chat API 返回 401 或本地会话已过期时，前端必须清理失效会话并跳转 `/login`。
- 收敛 Chat API 或调用层的认证失败处理，避免仅展示局部错误后继续留在受保护页面。
- 区分 401、403、网络异常和 5xx：401 触发登录恢复，403 展示权限不足，网络异常和服务端异常保留可恢复错误，不误清理有效会话。
- 保留跳转前必要的安全上下文和请求标识摘要，不记录 Token、Cookie、Authorization header、完整请求体或完整响应体。
- 补齐 Chat 工作台、需求中心和共享前台请求路径的回归验证，确认有效会话不误登出、无会话直接访问仍进入登录页。

## 能力影响

### 新增能力

无。本变更修复既有 Chat 工作台鉴权恢复行为，不创建独立 capability。

### 修改能力

- `web-catalog-chat-workbench`：补充受保护工作台登录失效后清理会话、重定位登录页和错误类型分层要求。
- `web-catalog-login-page`：复用既有登录页和统一登录态能力，不修改登录页视觉或后台管理员角色边界。

## 影响范围

```yaml
impact:
  backend: false
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
change_type: fix
capabilities:
  new: []
  modified:
    - web-catalog-chat-workbench
```

- Web：Chat 工作台入口守卫、Chat API 错误处理、前台会话清理与路由跳转。
- API：不计划变更接口 schema、错误码或 OpenAPI；实现阶段如发现需要变更响应结构，必须同步 API 文档与客户端生成。
- 数据库：不新增表、字段、索引、迁移或保留周期。
- 安全：不得绕过后端鉴权；不得在日志、错误提示或观测字段中保存凭证、Cookie、Authorization header 或完整本地会话。
- 观测：`product_data_collection_observability` 适用。受影响层包括 Web 请求封装和 `request_logs` 关联验证；本修复不新增行为事件、Task Trace 或数据库采集字段。
