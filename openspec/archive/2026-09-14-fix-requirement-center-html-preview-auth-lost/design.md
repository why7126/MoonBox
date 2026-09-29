---
change_id: fix-requirement-center-html-preview-auth-lost
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
sprint_id: sprint-006
---

## 根因分析

BUG-0022 的根因已由 `root-cause.md` 确认为前端点击 HTML / `new-tab` 文档时直接打开 `document.url`：

- preview API 依赖后端 `require_session_user`、`space_id` 与 `repository_id`。
- 需求中心前端请求封装 `governanceRequest()` 才会统一携带 Bearer。
- 项目作用域参数由 `scopedUrl()` 补齐。
- 新 Tab 裸开 API URL 绕过请求封装，导致 Bearer 与项目作用域缺失，后端返回 401，统一响应映射为 `code=1001`。

## 修复方案

前端保留 HTML 文档入口的新 Tab 预览体验，但将点击链路改为受控请求：

1. 用户点击 HTML / prototype 文档入口。
2. 前端阻止事件冒泡，校验文档 URL 与打开方式。
3. 使用现有项目上下文构造 scoped preview URL。
4. 使用现有认证请求封装读取 HTML 内容。
5. 成功后创建 `Blob([html], { type: "text/html" })` 与 `URL.createObjectURL()`。
6. 使用 Blob URL 打开新 Tab，并在合理时间内释放对象 URL。
7. 失败时在原页面提示预览失败原因摘要，保留卡片、筛选和看板状态。

## UI Contract

| 状态 | 用户反馈 | 行为约束 |
|---|---|---|
| loading | 点击入口后可出现轻量 loading 或保持入口可读 | 不清空看板，不触发卡片详情 |
| success | 新 Tab 打开 HTML 预览 | 地址栏为 Blob URL，不包含 Bearer、Cookie、本机路径或内部文件路径 |
| unauthorized | 原页面提示认证或权限校验失败 | 不再打开裸 API URL |
| not_found | 原页面提示文档不可用或已变更 | 不泄漏本机路径或真实文件系统结构 |
| popup_blocked | 提示浏览器拦截预览窗口 | 不误报打开成功，可允许用户再次点击 |
| missing_url | 提示文档入口不可用 | 不发起无效请求 |

## Security

- 不将 Bearer、Cookie 或 session 信息写入 URL。
- 不绕过后端鉴权；仍由 preview API 判定登录态、权限和项目作用域。
- 不在 toast、日志或错误详情中展示 HTML 正文、本机绝对路径、内部目录或无权对象内容。
- Blob URL 仅承载当前已授权响应内容，并在打开后释放。

## Observability

本 Change 影响前端预览请求与后端 `request_logs` 排障，不新增数据库表、对象存储路径、后台任务或 Task Trace。验证时需确认：

- preview 请求仍可在后端请求日志中以脱敏路径定位。
- 前端失败提示只展示脱敏摘要。
- 测试或调试输出不包含完整 HTML 正文、Bearer、Cookie、本机路径或无权对象内容。

## Tests

- 更新 `src/web/src/requirement-center.test.tsx` 或相邻测试，覆盖 HTML 文档入口不再调用裸 `window.open(document.url)`。
- 覆盖受控 fetch 成功后以 Blob URL 打开新 Tab，并释放对象 URL。
- 覆盖 401/403/404、缺失 URL、popup blocked 和项目作用域参数。
- 如涉及请求封装 helper 调整，补齐 helper 单元测试，避免影响 Markdown 抽屉与其他治理 API 调用。
