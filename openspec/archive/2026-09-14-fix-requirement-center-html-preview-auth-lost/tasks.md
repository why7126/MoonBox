## 1. 前置核实

- [x] 1.1 核实 `RequirementCenterPage` 中 HTML / `new-tab` 文档点击分支、`governanceRequest()` 和 `scopedUrl()` 的当前调用边界。
- [x] 1.2 核实 preview API 鉴权、项目作用域和错误响应映射，确认无需新增后端接口。
- [x] 1.3 梳理现有前端测试中对 `window.open(document.url)` 的断言，标记需要替换的回归场景。

## 2. 前端修复

- [x] 2.1 将 HTML / prototype 文档入口改为受控认证请求读取 HTML 内容，确保请求带 Bearer、`space_id` 与 `repository_id`。
- [x] 2.2 成功读取后使用 `text/html` Blob URL 打开新 Tab，并在合理时间内释放对象 URL。
- [x] 2.3 处理 401/403/404、缺少 URL、网络失败与浏览器弹窗拦截，原页面展示脱敏失败反馈。
- [x] 2.4 保持 Markdown 抽屉、卡片标题详情跳转、查看归档、阶段动作和文档保存行为不回退。

## 3. 验证与文档同步

- [x] 3.1 更新前端需求中心测试，覆盖成功 Blob 预览、认证失败、项目作用域参数、popup blocked 和缺失 URL。
- [x] 3.2 运行相关前端测试；如触及请求封装或类型，运行类型检查。
- [x] 3.3 记录手工或自动验收结果，确认新 Tab 地址不再是裸 preview API URL，且不泄漏 token、本机路径或内部文件系统结构。
- [x] 3.4 同步 BUG trace、Change trace/test-plan/acceptance 和 Sprint 状态。
