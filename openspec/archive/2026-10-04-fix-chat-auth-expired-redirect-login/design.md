---
title: Chat 工作台登录失效重定位修复设计
change_id: fix-chat-auth-expired-redirect-login
source_bug: BUG-0024-login-expired-refresh-not-redirect-login
created_at: 2026-10-04 11:18:13
updated_at: 2026-10-04 11:18:13
owner: MoonBox 产品团队
---

# Chat 工作台登录失效重定位修复设计

## 现状与根因

Chat 工作台 `/chat` 入口目前通过 `readFrontendSession` 判断本地会话是否存在；该读取路径未过滤过期会话。Chat API 请求收到 401 时抛出 `ChatApiError`，调用层只设置页面错误和加载状态，没有清理失效会话或触发登录页重定位。需求中心部分请求已存在 401 清理并跳转 `/login` 的路径，说明缺陷集中在 Chat 工作台和共享前台鉴权失败处理不一致。

BUG-0024 的证据链包含代码路径 E1-E5、用户截图 E6/E8 和 Network 401 响应 E7/E9，足以确认根因。当前 Change 不做源码修复，仅定义修复范围、规格增量和验证门禁。

## 修复方案

1. 在 Chat API 或其上层调用处提供统一的认证失败处理入口。收到 401 且响应表示认证失败时，清理前端 session，撤销受保护工作台访问状态，并导航到 `/login`。
2. 路由入口需要避免仅凭残留本地 session 放行明显失效的会话。若本地会话存在可判定的过期时间且已过期，直接清理并进入登录页。
3. Chat 工作台初始化、消息读取、空间读取、项目读取和能力读取等受保护请求应共享同一 401 处理语义，避免某些请求触发跳转、某些请求只显示局部错误。
4. 403、网络异常和 5xx 不走登录失效流程。403 展示权限不足；网络异常和 5xx 展示可恢复错误或重试入口；有效会话不得被误清理。
5. 跳转前可保留目标路径用于重新登录后恢复，但不得持久化完整请求、响应、Token、Cookie、Authorization header、完整本地存储或真实客户数据。

## 验证策略

- 单元或组件测试覆盖 `readFrontendSession` 过期处理、Chat API 401 分支、403/网络异常/5xx 分支和有效会话刷新。
- 浏览器回归覆盖 `/chat` 刷新时服务端返回 401 的真实表现：清理会话、地址进入 `/login`、不继续展示需鉴权数据、无循环跳转。
- 横向回归覆盖需求中心已有 401 跳转行为不退化，管理端或后台登录态不被前台统一登录态误伤。
- 验证 Network 和日志中不出现 Token、Cookie、Authorization header、完整请求体或完整响应体。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web
    - request_logs
  reason: 修复触及 Web 前台请求封装和受保护 API 401 恢复路径，需要确认请求标识、状态码和安全错误摘要可用于排查，同时不新增后端响应 schema、数据库字段、行为事件或 Task Trace。
  validation: opsx-apply 阶段需验证 401 场景保留脱敏请求标识或可追踪状态，且日志、错误提示、本地状态和测试证据不包含 Token、Cookie、Authorization header、完整请求体、完整响应体或真实客户敏感数据。
```

## 风险与回滚

- 风险：误把 403、断网或 5xx 当作登录失效，导致用户被不必要登出。缓解方式是按状态码和受控错误码分支处理。
- 风险：跳转 `/login` 后丢失用户原目标。缓解方式是只保存安全的返回路径或在登录成功后回到授权范围内页面。
- 回滚：若修复导致误登出或循环跳转，可回退 Chat 401 处理逻辑，同时保留后端 401 拒绝访问能力；不得回退服务端鉴权。
