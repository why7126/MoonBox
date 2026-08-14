---
requirement_id: REQ-0014-frontend-user-menu-profile
title: 前台用户菜单栏个人资料功能验收标准
acceptance_status: passed
created_at: 2026-08-11 16:10:49
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## 功能 AC

- [ ] AC-001 前台需求中心用户菜单中的“个人资料”可点击，点击后关闭用户菜单并打开个人资料弹窗。
- [ ] AC-002 个人资料弹窗仅包含头像、昵称、仅用户名只读摘要、右上角关闭、保存和取消，不出现密码、角色、权限、产品域标签、后台用户管理或他人资料编辑字段。
- [ ] AC-003 弹窗使用 `rc-*` 前台视觉体系，深浅主题均可读，且不直接套用后台 `admin-*` 视觉类。
- [ ] AC-004 头像支持 JPG、PNG、WebP，单文件不超过 2MB；不支持的类型或过大文件展示受控错误。
- [ ] AC-005 头像上传成功后在同一弹窗内即时预览，最终保存的 `avatar_url` 为后端返回的持久 URL，不保存 `blob:` URL。
- [ ] AC-006 昵称最长 128 个字符，保存时去除首尾空白；昵称清空后保存为空值或等价空状态。
- [ ] AC-007 前台用户菜单展示优先使用昵称；昵称为空时回退显示用户名；头像为空时展示默认首字头像。
- [ ] AC-008 保存期间禁用重复提交，保存成功后直接使用接口返回的最新 user 更新前台当前用户上下文。
- [ ] AC-009 保存成功后用户菜单头像、昵称或用户名立即刷新，并同步本地会话缓存；页面刷新后不回退旧资料。
- [ ] AC-010 保存失败时弹窗保持打开，保留用户已输入内容，展示受控错误并允许重试。
- [ ] AC-011 登录态失效、账号不可用或凭证无效时复用既有登录态失效处理，不泄露内部错误。
- [ ] AC-012 现有用户菜单能力保持不变：切换空间、设置空间、界面主题、进入后台权限显示和退出登录不发生回归。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-media-upload-chain.md` — 预防上传状态、即时回显和 Docker 边界文件访问缺陷

- [ ] AC-XCUT-001 头像上传组件必须具备 `idle -> uploading -> done/failed` 状态机，并在单元测试中覆盖上传成功与失败状态。
- [ ] AC-XCUT-002 上传中必须禁用重复提交和重复选择触发；上传失败后必须允许重新选择文件并重试。
- [ ] AC-XCUT-003 上传成功后必须在同一会话、同一弹窗内立即回显头像，不依赖页面刷新或重新拉取需求中心上下文。
- [ ] AC-XCUT-004 上传成功后的 URL 或对象引用不得写入日志中的敏感上下文，且不得泄露临时凭据、MinIO 内部路径或对象存储配置。
- [ ] AC-XCUT-005 Docker 本地环境 `:3000` 边界必须能完成头像上传、受保护读取和前台菜单回显验收。
- [ ] AC-XCUT-006 后端上传接口和头像读取路径必须在容器网络、浏览器访问和反向代理路径下保持一致。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 `prototype/web/context.md` 已拆解页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 阶段必须在 Change `design.md` 写入 UI Contract 和 UI Skeleton，明确前台用户菜单入口、个人资料弹窗、头像上传状态和保存反馈。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 阶段必须先完成 UI Skeleton 首轮实现，并提供 1440px 视觉截图或等价证据后再进入细节实现。
- [ ] AC-PROTOTYPE-004 1440px 视觉验收必须覆盖用户菜单打开态、个人资料弹窗默认态、头像上传成功预览、上传失败提示、保存失败提示和保存成功后的菜单刷新。
- [ ] AC-PROTOTYPE-005 关键 computed style 或等价检查必须覆盖弹窗宽度、高度、padding、gap、border、background、color、z-index、overflow、按钮尺寸和头像预览尺寸。
- [ ] AC-PROTOTYPE-006 `/opsx-archive` 前必须完成 REQ 最终一致性检查，确认 requirement、acceptance、trace、Change design、实现证据和视觉验收结果一致。
- [ ] AC-PROTOTYPE-007 前后台个人资料 Modal 交互结构必须保持一致：标题行、右上角关闭、仅用户名摘要、单头像预览、昵称输入、错误提示和 footer 操作；前台仍必须使用 `rc-*` 视觉体系。
- [ ] AC-PROTOTYPE-008 前后台用户菜单头像必须统一为 32px，个人资料弹窗头像必须统一为 48px；前台昵称字段不得展示“保存后同步刷新前台用户菜单。”等实现说明文案。

## 非目标回归 AC

- [ ] AC-NON-001 前台个人资料弹窗不得包含“修改密码”流程；如用户点击用户菜单中既有“修改密码”入口，本需求不改变其现有行为。
- [ ] AC-NON-002 本需求不得新增后台用户管理入口、用户列表编辑、角色修改、账号冻结或重置密码能力。
- [ ] AC-NON-003 本需求不得改变 REQ-0012 需求中心看板阶段映射、卡片展示、空间切换或主题切换语义。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: add-frontend-user-menu-profile
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

