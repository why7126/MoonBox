---
change_id: fix-requirement-center-html-preview-auth-lost
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
status: applied
---

# Acceptance

## 必须满足

- HTML / prototype 文档入口点击后不再直接打开裸 `/api/v1/requirement-center/.../preview` API URL。
- 预览请求必须携带当前登录 Bearer 与项目作用域参数。
- 成功时新 Tab 使用 `text/html` Blob URL 展示 HTML 内容，并释放对象 URL。
- 401/403/404、缺少 URL、网络失败和 popup blocked 时必须在原页面给出脱敏失败反馈。
- Markdown 抽屉、卡片详情跳转、查看归档、阶段动作和文档保存行为不回退。
- URL、toast、日志、测试输出不得包含 Bearer、Cookie、本机路径、内部文件系统结构或无权对象内容。

## 验收证据

- 前端自动化测试已覆盖受控 fetch、Blob URL 打开、错误反馈、项目作用域参数、Bearer header、缺 URL 和 popup blocked。
- 本次 apply 使用组件测试断言新 Tab 打开的 URL 为 Blob URL，且没有调用裸 preview API URL；真实浏览器截图可在后续人工验收补充。
- Change trace 已记录测试命令、结果和观测安全结论。
