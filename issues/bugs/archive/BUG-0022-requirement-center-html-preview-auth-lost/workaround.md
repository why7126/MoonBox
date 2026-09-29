---
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
created_at: '2026-09-14 15:18:00'
updated_at: '2026-09-14 15:18:00'
---

# 临时规避

## 可用方式

- 对于需要查看的 HTML 原型，先打开同一卡片的 Markdown 文档或 trace，确认具体 Issue ID 和 HTML 文件名。
- 在本地开发环境中，可直接从工作区文件系统查看对应 `prototype.html` 或 `prototype/**.html` 文件内容。
- 若只是核对原型是否存在，可在需求中心卡片文档列表中确认 HTML 入口名称，不依赖新 Tab 预览结果。

## 限制

- 产品界面内没有可切换的临时开关来恢复 HTML 新 Tab 预览。
- 不建议将 preview API 改成免登录公开访问；这会绕过需求中心项目授权边界。
- 不建议把 Bearer token 写入 URL 查询参数；这会造成浏览器历史、日志和分享链接泄漏风险。
- 文件系统直接查看只适用于本地开发或维护人员，不适用于普通前台用户验收。

## 正式处理

正式修复应在前端 HTML 预览点击链路中使用受控 fetch 读取 HTML，再以 Blob URL 打开新 Tab。修复后通过组件测试和真实浏览器预览证据确认临时规避可解除。
