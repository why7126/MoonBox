---
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
title: 需求中心卡片 HTML 预览直开受保护接口导致认证失败
status: done
created_at: '2026-09-14 15:10:06'
updated_at: 2026-09-14 18:20:45
related_requirement: REQ-0012-frontend-requirement-center
related_bug: null
environment: local
severity: medium
---

# 现象

用户在需求中心点击卡片中的 HTML 文件时，无法正常预览。页面显示接口错误：

```json
{
  "code": 1001,
  "message": "认证或权限校验失败",
  "data": null
}
```

严重度初判 medium：该问题阻断需求中心原型/HTML 文档预览体验，影响 UI 参考稿、prototype.html 和验收材料查看；当前未发现数据丢失、越权访问或生产全站不可用证据。

# 复现步骤

1. 登录 MoonBox 前台并进入需求中心。
2. 找到包含 `prototype.html` 或 `prototype/**.html` 文档入口的 REQ/BUG 卡片。
3. 点击该 HTML 文档入口。
4. 新 Tab 直接打开 `/api/v1/requirement-center/issues/{issue_id}/documents/{document_name}/preview`。
5. 观察页面是否返回 `code=1001`、`message=认证或权限校验失败`。

# 期望 vs 实际

| 项目 | 期望 | 实际 |
|---|---|---|
| HTML 预览 | 登录态下点击卡片 HTML 文件后正常打开受控 HTML 预览 | 新 Tab 直接访问受保护 preview API，返回认证或权限校验失败 |
| 项目作用域 | 请求携带当前 `space_id` 与 `repository_id` | 当前点击链路疑似直接使用后端返回的裸 URL |
| 认证方式 | 预览请求复用前端 Bearer 登录态 | 浏览器新 Tab 导航无法附加前端存储中的 Bearer header |

# 已有探索证据

- `src/backend/app/api/v1/requirement_center.py` 的 HTML 预览接口通过 `get_reader` 读取项目作用域并依赖 `require_session_user` 鉴权。
- `src/backend/app/chat/api.py` 将 401 映射为 `code=1001`、`message=认证或权限校验失败`。
- `src/web/src/components/workbench/governanceApi.ts` 的 `scopedUrl()` 会追加 `space_id` 与 `repository_id`，Markdown 抽屉读取路径已使用该方法。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 HTML / `new-tab` 分支当前直接 `window.open(document.url)`，未经过 `scopedUrl()`，也无法附加 Bearer header。
- `src/web/src/requirement-center.test.tsx` 现有测试断言打开裸 preview URL，未覆盖鉴权 fetch + Blob URL 的预览契约。

# 初步修复方向

- 前端点击 HTML 文档时使用带 Authorization 的 fetch 读取 `scopedUrl(document.url, selectedProject)`。
- 成功读取 `text/html` 后创建 Blob URL 并用 `window.open(blobUrl)` 打开。
- 更新测试：断言 HTML 预览不再直接打开裸 API URL，并覆盖缺少项目连接、读取失败、Blob URL 打开与释放。

# 附件

无新增截图或日志附件。证据来自用户错误信息和本会话只读代码定位；未持久化原始会话、Token、Cookie、Authorization header 或敏感日志。
