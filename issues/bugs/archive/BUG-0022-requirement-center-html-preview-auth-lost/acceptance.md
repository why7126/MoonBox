---
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
created_at: '2026-09-14 15:18:00'
updated_at: 2026-09-29 14:41:41
acceptance_status: passed
---

# 验收清单

当前全部待执行；根因确认不代表缺陷已修复。

## 回归标准

- [ ] AC-001：点击真实 context 返回的 `prototype.html` 文档入口时，前端通过受控请求读取 HTML，request URL 包含当前 `space_id` 与 `repository_id`。
- [ ] AC-002：HTML 预览请求携带 Bearer 登录态；不得把 token、Cookie 或 Authorization 信息写入 URL。
- [ ] AC-003：成功读取 HTML 后，`window.open` 打开 Blob URL，而不是裸 `/api/v1/requirement-center/.../preview` API URL。
- [ ] AC-004：新 Tab 正常渲染 HTML 内容，不显示 `code=1001` 或 JSON 错误响应。
- [ ] AC-005：HTML 读取失败时，用户在原页面收到可理解的失败反馈；不得误标文档已打开成功。
- [ ] AC-006：项目未连接或缺少当前项目作用域时，HTML 预览不发起裸 API 导航，并提示项目未连接或文档暂不可用。
- [ ] AC-007：workflow demo 的 `document.htmlContent` 本地 Blob 预览仍可用，不依赖后端 API。
- [ ] AC-008：Markdown 文档抽屉读取、保存、tasks 勾选和 Change 文档打开不回归。
- [ ] AC-009：前端测试覆盖 HTML 预览受控 fetch + Blob URL 流程，并删除或更新裸 preview URL 直开断言。
- [ ] AC-010：真实浏览器验收记录至少一个 HTML 文档预览成功的 Network 摘要和页面截图；证据不得包含 Authorization header、Cookie、token 或真实敏感数据。

## 验证方式与证据边界

- AC-001 至 AC-003、AC-005 至 AC-009 优先用前端组件测试或 Playwright 受控数据验证。
- AC-004 与 AC-010 需要真实浏览器观察或等价 E2E 证据。
- 后端 preview API 鉴权契约保持不变；本 BUG 不要求新增公开 API、数据库迁移、对象存储变更、部署配置变更或客户端生成。
- 若实现方案改动 API contract、权限边界或错误响应结构，必须在后续 OpenSpec Change 中重新评估 API、权限、安全和文档同步范围。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: fix-requirement-center-html-preview-auth-lost
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

