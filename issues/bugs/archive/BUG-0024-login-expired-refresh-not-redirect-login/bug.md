---
bug_id: BUG-0024-login-expired-refresh-not-redirect-login
title: 登录失效时，页面刷新也没有重新定位到登录页
status: done
owner: user_f694abc671d548b48d9eb897f720ba4d
created_at: '2026-09-29 12:03:02'
updated_at: 2026-10-04 23:50:26
discovered_at: null
environment: 本地 Web `localhost:18102`；Chat 工作台 `/chat`；浏览器 DevTools Network 截图；版本显示 v0.1.0
related_requirement: null
related_change: null
lifecycle_stage: review
severity: medium
---

# 登录失效时，页面刷新也没有重新定位到登录页

## 现象

用户反馈：登录失效时，页面刷新也没有重新定位到登录页。

证据来源为同目录 capture.md 及用户补充的运行时截图。截图显示 Chat 工作台刷新后仍停留在受保护页面，页面提示“登录已失效，请重新登录”；Network 中多个业务 API 返回 401，选中的 `GET /api/v1/chat/spaces` 响应体为 `code: 1001`、`message: "认证或权限校验失败"`、`data: null`。

## 复现条件与步骤

以下为依据截图和代码路径整理的复现路径：

1. 登录后进入 Chat 工作台 `/chat`，本地仍保留 `moonbox.session`。
2. 服务端侧会话失效或访问令牌被拒绝。
3. 刷新当前 Chat 页面，触发 `spaces`、`messages`、`projects`、`capabilities` 等受保护请求。
4. 观察页面是否跳转 `/login`，并记录 Network 中 401 响应。

复现频率、影响账号范围和重新登录后的恢复情况仍待修复验收补充。

## 期望与实际

| 项目 | 描述 |
|---|---|
| 期望结果 | 登录态失效后刷新需要登录的页面，能够跳转到登录页，供用户重新登录。 |
| 实际结果 | 页面停留在 Chat 工作台，显示“登录已失效，请重新登录”或“重新连接”，未跳转登录页；相关 JSON 业务请求返回 401。 |

## 影响范围

当前反馈已确认涉及 Web 端 Chat 工作台。由于同类前端鉴权逻辑还覆盖需求中心、管理端和共享请求封装，修复评估需做横向回归。

该缺陷影响用户在登录失效后的恢复路径：用户看到错误但不会被引导回登录页。现有证据表明服务端拒绝业务 API 访问，未发现越权访问、数据泄露或数据损坏证据。

## 严重等级说明

沿用 medium：问题影响登录失效后的恢复引导和受保护页面一致性，但服务端已返回 401 拒绝访问，暂无数据越权或损坏证据。若后续确认大面积阻断关键工作流，可在评审时上调。

## 证据摘要

- Chat 工作台刷新后仍展示受保护页面和“登录已失效，请重新登录”。
- Network 多条业务请求返回 401，包括 `spaces`、`messages?page=1`、`projects`、`capabilities?...`。
- 选中 `GET /api/v1/chat/spaces` 的响应体为 `code: 1001`、`message: "认证或权限校验失败"`、`data: null`。
- 静态资源返回 200/304，说明并非前端资源加载失败。

## 根因与处理边界

根因状态为 confirmed。已补齐 [根因分析](root-cause.md)、[临时处理方案](workaround.md) 和 [回归验收方案](acceptance.md)。已通过 [缺陷评审](review.md)，待纳入 Sprint；当前仅完成修复决策，尚未实施代码修复或通过回归验收。
