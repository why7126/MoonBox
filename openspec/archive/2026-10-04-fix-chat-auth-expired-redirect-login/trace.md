---
title: Chat 工作台登录失效重定位修复追溯记录
change_id: fix-chat-auth-expired-redirect-login
type: fix
status: applied
source_bug: BUG-0024-login-expired-refresh-not-redirect-login
sprint: sprint-008
created_at: 2026-10-04 11:18:13
updated_at: 2026-10-04 23:47:07
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web
    - request_logs
  reason: 本 Change 修复 Web 前台请求鉴权失败恢复路径，需要确认 401 请求标识、状态码和安全错误摘要可用于排查，同时不新增后端响应 schema、数据库字段、行为事件或 Task Trace。
  validation: 已通过 Vitest、TypeScript 和 Playwright 浏览器验证 401 清理跳转、403/网络异常不误登出；验证记录只包含脱敏状态、路径和合成 token 标识，不包含 Token、Cookie、Authorization header、完整请求体、完整响应体或真实客户敏感数据。
execution:
  schema_version: 1
  started_at: 2026-10-04 11:27:52
  completed_at: 2026-10-04 12:47:38
  last_event: opsx.apply
---

# Chat 工作台登录失效重定位修复追溯记录

## 来源

| 项 | 值 |
|---|---|
| BUG | `BUG-0024-login-expired-refresh-not-redirect-login` |
| Sprint | `sprint-008` |
| Change | `fix-chat-auth-expired-redirect-login` |
| 类型 | fix |
| 状态 | in_progress |

## Bug Readiness Report

| 项 | 结论 | 说明 |
|---|---|---|
| 根因状态 | confirmed | `root-cause.md` 通过 E1-E9 形成代码路径、截图和 Network 401 证据闭环 |
| 评审门禁 | pass | `review.md` 已通过，严重度 medium，采用正常迭代修复 |
| Sprint 门禁 | pass | BUG 已同步为 `in_sprint` 并纳入 `sprint-008` |
| 修复边界 | ready | Chat 工作台 401 处理、前台会话清理、路由重定位和错误类型分层 |
| 产品数据采集与链路观测 | applicable | 覆盖 Web 请求封装和 request_logs 关联验证，不新增 DB、usage_events 或 Task Trace 字段 |

## 影响分析

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

## Conflict Report

| 事实源 | 优先级 | 结论 |
|---|---:|---|
| `root-cause.md` | 1 | 401 后未统一清理会话并跳转 `/login` 是 confirmed 根因 |
| `acceptance.md` | 2 | AC-001 至 AC-007 覆盖 401、403、网络异常、有效会话和重新登录 |
| `web-catalog-chat-workbench` | 3 | Change 规格增量落在 Chat 工作台入口与权限 |
| `web-catalog-login-page` | 4 | 复用登录页能力，不改变登录页视觉或管理员角色边界 |

## 生成产物

| 文件 | 用途 |
|---|---|
| `proposal.md` | 提案 |
| `design.md` | 设计 |
| `tasks.md` | 实施任务 |
| `specs/web-catalog-chat-workbench/spec.md` | Chat 工作台规格增量 |

## 验证记录

| 时间 | 命令 | 结果 | 摘要 |
|---|---|---|---|
| 2026-10-04 11:18:13 | `python scripts/validate-change-identity.py --new-id fix-chat-auth-expired-redirect-login` | pass | Change 身份校验通过 |
| 2026-10-04 11:21:41 | `openspec validate fix-chat-auth-expired-redirect-login --strict` | pass | OpenSpec Change 严格校验通过 |
| 2026-10-04 11:21:41 | `python scripts/validate-document-titles.py --change fix-chat-auth-expired-redirect-login` | pass | Change 5 份文件中文标题校验通过 |
| 2026-10-04 11:21:41 | `python scripts/validate-openspec-language.py --change fix-chat-auth-expired-redirect-login --residual-report` | pass | 当前 Change 中文校验通过，全仓残留分离报告无非当前残留 |
| 2026-10-04 11:21:41 | `python scripts/validate-product-data-observability.py --change fix-chat-auth-expired-redirect-login` | pass | 产品数据采集与链路观测门禁校验通过 |
| 2026-10-04 11:24:55 | `python scripts/sync-workflow-status.py --event bug.opsx --bug BUG-0024-login-expired-refresh-not-redirect-login --change fix-chat-auth-expired-redirect-login --sprint auto` | pass | Workflow Sync 无错误；BUG 关联 Change，Sprint 范围同步 |
| 2026-10-04 11:24:55 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event bug.opsx --bug BUG-0024-login-expired-refresh-not-redirect-login --change fix-chat-auth-expired-redirect-login --sprint sprint-008 --json` | warning | AI Usage 自动归因不可用，未写入 sprint snapshot；建议需要精确用量时提供显式 session JSONL |
| 2026-10-04 11:27:52 | `python scripts/sync-workflow-status.py --event opsx.start --change fix-chat-auth-expired-redirect-login --sprint auto` | pass | Change 启动同步成功，进入研发中 |
| 2026-10-04 12:39:40 | `./node_modules/.bin/vitest run src/chat-auth.test.ts src/chat-workbench.test.tsx src/chat-activity.test.tsx src/requirement-center.test.tsx` | pass | 4 个前端测试文件 131 项通过；覆盖 Chat 401/403/网络异常/过期会话、App Chat 守卫和需求中心 401 回归 |
| 2026-10-04 12:40:00 | `./node_modules/.bin/tsc -b` | pass | Web TypeScript 构建检查通过 |
| 2026-10-04 12:43:00 | Playwright Chromium + Vite `http://127.0.0.1:18102/chat` | pass | 真实浏览器拦截 `GET /api/v1/chat/spaces` 返回 401 后，页面重定位 `/login`，`moonbox.session` 清空 |
| 2026-10-04 12:47:38 | `python scripts/sync-workflow-status.py --event opsx.apply --change fix-chat-auth-expired-redirect-login --sprint auto` | pass | Workflow Sync 无错误；Change applied，BUG 验收投影为 pending |
| 2026-10-04 12:47:38 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --bug BUG-0024-login-expired-refresh-not-redirect-login --change fix-chat-auth-expired-redirect-login --sprint sprint-008 --json` | warning | AI Usage 自动归因不可用，未写入 sprint snapshot；建议需要精确用量时提供显式 session JSONL |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-04 12:47:38 | opsx.apply | applied | Workflow Sync 完成 applied 投影；等待人工验收或归档。 |
| 2026-10-04 12:44:13 | opsx.apply 验证完成 | in_progress | Chat 401 统一清理跳转、本地过期会话守卫、403/网络错误分层和需求中心回归验证通过；待 Workflow Sync 完成 applied 投影。 |
| 2026-10-04 11:27:52 | opsx.start | in_progress | Workflow Sync 启动 Change 执行投影 |
| 2026-10-04 11:18:13 | bug.opsx | proposed | 根据 `BUG-0024-login-expired-refresh-not-redirect-login` 创建 OpenSpec Change 文档与规格增量 |

## 人工验收确认

- 确认时间：2026-10-04 23:47:07。
- 用户接受现有自动化与浏览器验证证据，明确确认 BUG-0024 人工验收通过并授权归档。
- 验收依据为既有 131 项合成回归、TypeScript 检查及浏览器拦截 401 后跳转验证；本次未新增人工操作测试记录。
- 验收结论已回填 BUG acceptance.md。当前会话对归档目录与正式规格目录只读，尚未执行归档、规格合并、opsx.archive 同步或 Issue 阶段迁移，Change 保持 applied。
