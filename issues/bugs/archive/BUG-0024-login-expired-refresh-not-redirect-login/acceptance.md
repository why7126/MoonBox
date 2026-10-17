---
bug_id: BUG-0024-login-expired-refresh-not-redirect-login
title: 登录失效刷新未跳转登录页回归验收方案
created_at: '2026-09-30 15:20:25'
updated_at: 2026-10-17 16:45:28
acceptance_status: passed
---

# 登录失效刷新未跳转登录页回归验收方案

## 验收范围

已确认反馈页面为 Chat 工作台。修复验收需覆盖 Chat 工作台，并对需求中心、管理端和共享请求封装做回归，避免 401/403/网络错误处理互相干扰。

| 编号 | 条件与操作 | 期望结果 | 执行结果 |
|---|---|---|---|
| AC-001 | 会话过期且保留本地会话，刷新 Chat 工作台 `/chat` | 清理前端会话并跳转登录页，不继续展示需鉴权的数据 | 自动化与浏览器验证通过；用户接受现有证据，人工验收通过 |
| AC-002 | Chat API 请求返回 401，响应体包含认证失败错误 | 清理失效会话并跳转，无循环跳转或无限重试 | 自动化与浏览器验证通过；用户接受现有证据，人工验收通过 |
| AC-003 | 无本地会话，直接访问受保护页面 | 跳转登录页 | 自动化验证通过；用户接受现有证据，人工验收通过 |
| AC-004 | 有效会话刷新页面 | 正常访问，不误登出 | 自动化回归通过；用户接受现有证据，人工验收通过 |
| AC-005 | 已登录但无资源权限，请求返回 403 | 显示权限不足，不误判会话过期 | 自动化回归通过；用户接受现有证据，人工验收通过 |
| AC-006 | 断网或服务端 5xx | 显示可恢复错误，不误清理有效会话 | 自动化回归通过；用户接受现有证据，人工验收通过 |
| AC-007 | 跳转后重新登录并访问原页面 | 恢复授权范围内的操作 | 自动化验证默认登录页恢复路径通过；用户接受现有证据，人工验收通过 |

## 证据与通过条件

逐项记录版本、页面、会话前置条件的脱敏描述、操作、实际结果、请求状态和时间。合成回归与真实浏览器观察分别记录；当前已完成自动化与浏览器验证，用户已接受现有自动化与浏览器验证证据并确认人工验收通过；本次未新增人工操作测试记录。

## 自动化验证记录

| 时间 | 类型 | 命令或工具 | 结果 | 覆盖 |
|---|---|---|---|---|
| 2026-10-04 12:39:40 | 合成回归 | `./node_modules/.bin/vitest run src/chat-auth.test.ts src/chat-workbench.test.tsx src/chat-activity.test.tsx src/requirement-center.test.tsx` | pass，131 项通过 | Chat 401 清理跳转、过期本地会话、无会话守卫、403/网络异常不误登出、需求中心 401 回归 |
| 2026-10-04 12:40:00 | 类型检查 | `./node_modules/.bin/tsc -b` | pass | Web TypeScript 构建检查 |
| 2026-10-04 12:43:00 | 真实浏览器 | Playwright Chromium + Vite `http://127.0.0.1:18102/chat`，拦截 `/api/v1/chat/spaces` 返回 401 | pass，最终路径 `/login`，`moonbox.session` 为 `null` | 刷新 Chat 工作台服务端会话失效后的真实浏览器重定位 |

## 数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - Web请求封装
    - 管理端请求封装
  reason: 候选修复涉及鉴权失败处理和 Web 请求封装；当前仅补齐文档，未变更 API、数据库、日志字段、行为事件、Task Trace 或对象存储。
  validation: 已验证 Chat 401 只记录脱敏状态码和业务错误摘要，前端清理会话并跳转；403 与网络错误不误清理有效会话。测试和浏览器证据未写入 Token、Cookie、Authorization header、完整请求体或完整响应体。
```

当前不计划新增 Task Trace：候选范围是现有客户端鉴权失败处理，尚无新增后端多步骤业务操作；若后续范围变化再评估。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:28
accepted_by: workflow-sync
source_change: fix-chat-auth-expired-redirect-login
source_sprint: sprint-008
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
