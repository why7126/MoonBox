---
title: Chat 工作台登录失效重定位修复任务
change_id: fix-chat-auth-expired-redirect-login
source_bug: BUG-0024-login-expired-refresh-not-redirect-login
created_at: 2026-10-04 11:18:13
updated_at: 2026-10-04 12:44:13
owner: MoonBox 产品团队
---

# Chat 工作台登录失效重定位修复任务

## 实施任务

- [x] 复核 Chat 工作台入口守卫、`readFrontendSession`、Chat API 错误处理和需求中心现有 401 跳转路径，确定共享复用边界。
- [x] 实现 Chat API 401 认证失败统一处理：清理前端会话、触发路由重算并跳转 `/login`。
- [x] 补充本地会话过期判断，避免明显过期的本地 session 继续放行 `/chat`。
- [x] 保持 403、网络异常和 5xx 的独立错误处理，不误清理有效会话。
- [x] 确认重新登录后可回到授权范围内页面或明确进入默认工作台，不泄漏原请求敏感信息。

## 验证任务

- [x] 增加或更新前端测试，覆盖 Chat API 401、403、网络异常、5xx、有效会话和无会话直接访问。
- [x] 执行 Web TypeScript、Vitest 或项目等价前端回归。
- [x] 执行浏览器级验证：会话失效后刷新 `/chat`，确认跳转 `/login`，不继续展示需鉴权数据，无循环跳转。
- [x] 横向回归需求中心已有 401 行为，确认不退化。
- [x] 校验日志和错误提示不包含 Token、Cookie、Authorization header、完整请求体、完整响应体或真实客户敏感数据。

## 文档同步

- [x] 根据最终实现更新 BUG-0024 `acceptance.md` 验证结果。
- [x] 如改动 API schema、错误码、OpenAPI 或客户端生成，补充 `docs/03-api-index.md`、OpenAPI 和 Orval 生成物；若未改动，记录 N/A 原因。
- [x] 如改动数据库、部署、安全或后台登录态边界，补充对应规则和设计文档；若未改动，记录 N/A 原因。
- [x] 在 Change `trace.md` 中记录 `opsx.start`、`opsx.apply`、验证命令与结果摘要。
