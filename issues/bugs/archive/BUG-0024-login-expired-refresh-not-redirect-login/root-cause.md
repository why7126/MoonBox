---
bug_id: BUG-0024-login-expired-refresh-not-redirect-login
title: 登录失效刷新未跳转登录页根因分析
created_at: '2026-09-30 15:20:25'
updated_at: '2026-09-30 17:04:51'
status: confirmed
---

# 登录失效刷新未跳转登录页根因分析

## 根因状态

status: confirmed

## 现象

用户在 `localhost:18102` 的 Chat 工作台刷新后仍停留在受保护页面，页面主区域和输入框提示“登录已失效，请重新登录”，未重定位到 `/login`。浏览器 Network 显示多个受保护 API 返回 401，选中的 `GET /api/v1/chat/spaces` 响应体为 `code: 1001`、`message: "认证或权限校验失败"`、`data: null`。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | code_path | src/web/src/App.tsx:46 | 聊天和需求中心入口按 readFrontendSession 返回值放行 | 本地会话存在即可通过此入口检查 |
| E2 | code_path | src/web/src/pages/home/frontendSession.ts:13 | 解析本地会话，未检查 expires_at | 该函数不会过滤过期会话 |
| E3 | code_path | src/web/src/components/chat/chatApi.ts:17 | 401 抛出 ChatApiError，未执行清理或跳转 | 该请求路径未自动退出 |
| E4 | code_path | src/web/src/components/chat/useChatWorkbench.ts:24 | 初始化失败仅设置错误与加载状态 | 聊天初始化鉴权失败可能仍停留页面 |
| E5 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx:2168 | 上下文请求 401 时清理会话并跳转 | 部分页面路径已有鉴权失败跳转 |
| E6 | screenshot | 用户附件 codex-clipboard-8662cc6c-2cb2-478d-af5c-13aef04368c9.png | Chat 工作台仍显示主界面、主对象和输入框，页面提示“登录已失效，请重新登录”，顶部显示“本地项目 · 连接不可用” | 证明登录失效后页面未重定位到登录页，而是停留在 Chat 工作台 |
| E7 | network_request | 用户附件 codex-clipboard-79243781-17c1-46f8-89ce-21d3f88c736e.png | Network 中 `messages?page=1`、`projects`、`capabilities?...` 等多条 GET 请求返回 401 | 证明刷新或轮询后多个受保护接口鉴权失败 |
| E8 | screenshot | 用户附件 codex-clipboard-ad92c8fe-f8a1-4fc9-8561-0f276ad7573d.png | 新会话页仍停留在 Chat 工作台并展示“重新连接”，Network 中 `spaces`、`projects` 等请求返回 401，静态资源返回 200/304 | 证明前端资源加载正常，异常集中在业务 API 鉴权失败后未统一退出 |
| E9 | network_request | 用户附件 codex-clipboard-45ae12ca-768c-43bf-8b0f-1632b7077ba2.png | 选中 `GET /api/v1/chat/spaces`，状态 401，响应 JSON 为 `code: 1001`、`message: "认证或权限校验失败"`、`data: null` | 直接证明 Chat 工作台 API 鉴权失败，且前端仍未跳转登录页 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 静态资源加载失败导致页面异常 | E8、E9 中 JS、CSS、图标等资源返回 200/304，异常请求集中在 JSON 业务 API 401 |
| 所有受保护页面都没有 401 跳转处理 | E5 显示需求中心上下文请求 401 时已有清理会话并跳转 `/login` 的路径 |
| 只是项目连接不可用，与登录态无关 | E7、E9 的 401 与认证失败响应体说明至少存在鉴权失败信号，不是单纯本地项目连接不可用 |

## 已确认根因

Chat 工作台的路由入口只检查本地 session 是否存在，未校验会话是否已过期或已被服务端拒绝；Chat API 收到 401 后仅抛出页面错误并继续停留在当前工作台，没有统一清理前端会话、同步路由状态并跳转 `/login`。因此刷新时本地残留 session 仍让 `/chat` 通过入口守卫，后续 `spaces`、`messages`、`projects`、`capabilities` 等受保护请求返回 401 后只在页面内展示“登录已失效，请重新登录”，造成用户看到登录失效但页面未重新定位到登录页。

## 修复方向

统一前端鉴权失败处理：Chat API 或调用层遇到 401 时应清理前端会话、触发路由重新计算并跳转 `/login`；入口守卫应避免仅凭本地 session 残留放行已失效会话。修复时需要区分 401、403、网络错误和 5xx，避免把无权限、断网或服务端异常误判为登录过期。

## 补证清单与操作步骤

目的：补齐影响范围和验收输入，而不是阻断当前根因确认。

1. 记录入口路径、账号角色、应用版本、浏览器、发生时间及判断登录失效的依据。
2. 在问题页面打开开发者工具 Network，勾选 Preserve log，再按实际方式刷新。
3. 记录刷新后地址、页面提示、异常请求 method/path/status、业务错误码、响应摘要及可用的 trace_id/request_id。
4. 记录刷新方式和复现次数；若 Console 有相关红色错误，提供脱敏关键段。
5. 如仍无法判断，按时间与请求标识关联服务端鉴权日志，仅提供相关摘要。

返回格式：入口与路径；角色；环境与版本；时间；失效依据；刷新方式；刷新后地址与提示；请求 method/path/status/错误码；请求标识；复现次数。

脱敏要求：不要提供密码、Token、Cookie、Authorization、完整本地存储、真实客户数据或未脱敏日志。

## 验证闭环

已完成用户截图、Network 401 响应和代码路径的根因闭环，足以进入评审。尚未实施修复，也未执行修复后的浏览器回归；后续应在 `/opsx-apply` 中补充自动化或浏览器验证，确认 Chat 工作台、需求中心和管理端在 401/403/网络错误下行为一致且不误登出。
