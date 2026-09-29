---
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
created_at: '2026-09-14 15:18:00'
updated_at: '2026-09-14 15:18:00'
---

# 根因分析

## 根因状态

status: confirmed

确认范围：当前代码路径能够解释用户点击需求中心卡片 HTML 文件后出现 `code=1001` 的现象。尚未完成修复，也未完成浏览器真实回归验收。

## 现象

用户在需求中心点击卡片里的 `prototype.html` 或 `prototype/**.html` 入口时，新 Tab 直接打开受保护的 preview API，页面显示：

```json
{
  "code": 1001,
  "message": "认证或权限校验失败",
  "data": null
}
```

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | bug.md、capture.md | 用户复现入口为需求中心卡片 HTML 文件，实际响应为 `code=1001` 与“认证或权限校验失败” | 证明用户可见故障与鉴权失败有关 |
| E2 | code_path | `src/backend/app/api/v1/requirement_center.py:17`、`:207` | preview 路由依赖 `get_reader`；`get_reader` 要求 `space_id`、`repository_id`，并通过 `require_session_user` 获取当前用户 | preview API 是受保护接口，不是可裸开的静态文件 |
| E3 | code_path | `src/backend/app/chat/api.py:31` | `HTTPException` 中 401 被映射为 `code=1001`、`message=认证或权限校验失败` | 用户看到的错误码与后端鉴权失败分支一致 |
| E4 | code_path | `src/web/src/components/workbench/governanceApi.ts:7`、`:14` | `governanceRequest()` 会带 Bearer header；`scopedUrl()` 会补 `space_id` 与 `repository_id` | 项目已有受控读取所需的认证与作用域机制 |
| E5 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx:1943` | HTML / `new-tab` 分支直接 `window.open(document.url)`，未走 `governanceRequest()` 或 `scopedUrl()` | HTML 预览绕开了认证 header 与项目作用域拼接 |
| E6 | code_path | `src/web/src/requirement-center.test.tsx:1481` | 现有测试断言 `window.open` 参数就是裸 `/api/v1/.../preview` URL | 测试固化了旧的直开受保护 API 行为，缺少鉴权 fetch + Blob 预览覆盖 |

## 已排除假设

| 假设 | 排除依据 |
|---|---|
| 后端 preview API 不应鉴权，是后端误拦截 | E2 显示该接口显式依赖 `get_reader` 和 `require_session_user`，并需要项目作用域；这符合需求中心受控文档接口契约 |
| Markdown 文档抽屉同样缺少认证 | E4 与 bug.md 范围显示 Markdown 读取使用受控请求链路；本 BUG 范围限定 HTML / `new-tab` 分支 |
| 只是缺少 `space_id` / `repository_id`，与 Bearer 无关 | E5 显示直开分支同时绕开认证 header 与 `scopedUrl()`；两者都需要修复，单补查询参数仍不能让浏览器导航附带 Bearer |
| 只是某个 HTML 文件损坏 | E1 的响应是统一鉴权错误，E2/E5 显示问题出在访问链路；文件内容是否有效不是当前 `1001` 的必要原因 |

## 已确认根因

需求中心 HTML 文档入口被实现为直接 `window.open(document.url)`，而 `document.url` 指向后端受保护的 preview API。浏览器新 Tab 导航不会附带前端本地登录态中的 Bearer header，同时该分支也没有通过 `scopedUrl()` 补齐当前项目的 `space_id` 与 `repository_id`。后端将缺失或无效认证映射为 `code=1001`，因此用户看到“认证或权限校验失败”。

## 修复方向

- HTML / `new-tab` 分支不再直接打开受保护 API URL。
- 使用当前项目作用域生成 `scopedUrl(document.url, selectedProject)`。
- 通过带 Bearer header 的受控请求读取 HTML 文本。
- 将返回的 HTML 文本创建为 `text/html` Blob URL 后再 `window.open(blobUrl)`。
- 保留 workflow demo 的 `document.htmlContent` 本地 Blob 分支。
- 更新前端测试，删除裸 preview URL 直开断言，覆盖鉴权 fetch、Blob URL 打开、失败提示和项目未连接分支。

## 验证闭环

本次完善阶段完成的是根因确认，不代表修复已完成。修复后需要：

1. 用单元/组件测试断言点击 HTML 文档时请求 URL 包含 `space_id` 与 `repository_id`，请求 headers 包含 Bearer 登录态。
2. 断言 `window.open` 接收的是 Blob URL，而不是 `/api/v1/requirement-center/.../preview`。
3. 用失败响应覆盖错误提示和草稿/抽屉状态不受影响。
4. 在真实浏览器中打开至少一个 `prototype.html`，确认新 Tab 渲染 HTML 内容而不是 JSON 错误。
5. 记录浏览器 Network 证据：preview API 返回 200，且不暴露 Authorization header、Cookie 或真实 token。
