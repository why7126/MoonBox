---
change_id: fix-requirement-center-html-preview-auth-lost
type: fix
status: proposed
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
sprint_id: sprint-006
---

## 背景

需求中心卡片中的 HTML / prototype 文档入口当前直接 `window.open(document.url)` 打开后端 preview API。该 API 受登录态、`space_id` 与 `repository_id` 保护；新 Tab 直接访问时不会携带前端请求封装中的 Bearer，也不会补齐项目作用域参数，后端返回 401，并由统一响应映射为 `code=1001`、`message="认证或权限校验失败"`。

BUG-0022 已完成根因确认、评审通过并纳入 sprint-006。本 Change 将 HTML 预览修复纳入 OpenSpec，约束前端使用受控认证请求获取 HTML，再以 Blob URL 打开新 Tab，避免裸 API URL 暴露到浏览器地址栏。

## 变更内容

- 修复需求中心 HTML / prototype 文档入口直开受保护 preview API 导致 Bearer 丢失的问题。
- 统一 HTML 文档点击行为：使用项目作用域 URL 与 Bearer 发起受控请求，成功后以 `text/html` Blob URL 打开新 Tab。
- 保持 Markdown 抽屉、详情跳转、卡片动作与文档保存行为不回退。
- 失败时在原页面给出可理解的失败反馈，不误报打开成功，不泄漏 token、Cookie、本机路径或内部文件系统结构。
- 补齐前端回归测试与验收材料，覆盖成功打开、401/403/404、缺少 URL、弹窗被浏览器拦截、Blob URL 释放和项目作用域参数。

## 能力影响

### 新增能力

无。

### 修改能力

- `web-catalog-requirement-center`：明确 HTML 文档从新 Tab 打开时必须走受控认证预览链路，而不是直接暴露受保护 API URL。

## 影响面

- Web：需求中心卡片 HTML / prototype 文档入口点击处理、用户反馈、Blob URL 生命周期。
- API：复用现有 `/api/v1/requirement-center/.../preview` 受保护接口，不预期新增端点或变更响应结构。
- 数据库：不涉及 schema 或迁移。
- 对象存储：不涉及。
- 安全：避免 token 写入 URL，避免裸 preview API 在地址栏触发 1001；保留后端鉴权、项目作用域和错误脱敏。
- 数据采集与观测：适用 `request_logs` 与前端操作排障；不新增 `usage_events` 埋点要求，不记录 HTML 正文、Bearer、Cookie、本机路径或无权对象内容。
