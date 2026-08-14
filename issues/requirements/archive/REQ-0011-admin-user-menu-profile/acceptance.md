---
requirement_id: REQ-0011-admin-user-menu-profile
acceptance_status: passed
created_at: 2026-08-10 08:56:14
updated_at: 2026-08-14 16:29:34
owner: product
---

# 验收标准

## 功能 AC

- [x] AC-001 用户点击管理后台用户菜单栏“个人资料”后，系统打开个人资料 Modal，不再只展示占位 toast。
- [x] AC-002 个人资料 Modal 展示用户名、角色摘要、单个头像预览位和昵称输入项；不展示角色、状态、冻结、删除、重置密码等用户管理操作。
- [x] AC-003 当前用户资料读取以后端认证上下文为准；未登录、凭证无效、会话撤销或账号不可用时返回受控认证错误。
- [x] AC-004 当前用户资料更新接口只允许更新当前登录用户自己的 `nickname` 和 `avatar_url`，请求体不得指定目标用户 ID 或修改角色、状态、用户名、密码等字段。
- [x] AC-005 昵称非必填，最长 128 个字符；保存时去除首尾空白；清空昵称后用户菜单栏回退展示用户名。
- [x] AC-006 头像上传支持 JPG、PNG、WEBP，单文件不超过 2MB；类型不支持或文件过大时展示受控错误。
- [x] AC-007 上传成功后同一会话内即时回显头像预览；保存到用户资料中的 `avatar_url` 必须是后端返回的持久 URL，不得是 `blob:` URL。
- [x] AC-008 点击保存时禁用重复提交并展示保存中状态；保存成功后刷新当前用户摘要、本地会话缓存和用户菜单栏展示。
- [x] AC-009 保存失败时保留用户已输入的昵称和头像选择状态，展示可恢复错误，并允许用户修正后重试。
- [x] AC-010 用户点击取消、关闭 Modal 或未保存离开时，系统放弃本次未保存修改，不污染当前用户摘要。
- [x] AC-011 头像上传区必须参照创建用户表单交互：只展示一个头像预览位、右侧格式提示、一个“上传/更换/上传中”按钮和隐藏文件选择控件。
- [x] AC-012 Modal 内不得同时展示身份摘要头像和上传区头像两个图标；用户名和角色摘要必须用文本展示。
- [x] AC-013 无头像时按钮文案为“上传”，已有头像或已选择头像时按钮文案为“更换”，上传中为“上传中”且禁用重复选择。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 `prototype/web/context.md` 已拆解页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [x] AC-PROTOTYPE-002 `/req-opsx` 阶段必须在 Change `design.md` 写入 UI Skeleton，覆盖用户菜单入口、个人资料 Modal、创建用户同款头像上传结构、单头像预览位、昵称输入、底部保存 CTA 和保存反馈。
- [x] AC-PROTOTYPE-003 `/opsx-apply` 阶段必须在 1440px 桌面视口完成视觉验收，确认 Modal 尺寸、单头像预览位、上传/更换按钮、昵称输入、错误提示、保存按钮、toast 与用户菜单展示无重叠或溢出。
- [x] AC-PROTOTYPE-004 `/opsx-archive` 前必须确认最终实现与本 REQ、原型拆解、Change 设计和验收证据一致；不一致时先回填文档或返修实现。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`、`docs/knowledge-base/best-practices/admin-media-upload-chain.md` — 预防 Sprint 002/003 复发类缺陷

- [x] AC-XCUT-001 TSX 或模板实现中不得让通用 `modal-card` 与个人资料 Modal 专属宽度类并存，避免 CSS 级联覆盖弹窗宽度。
- [x] AC-XCUT-002 浏览器 computed style 必须验收个人资料 Modal 最终宽度，确认与设计预期一致。
- [x] AC-XCUT-003 低视口下个人资料 Modal body 必须可滚动，单头像预览位、昵称输入、错误提示、取消和保存按钮均可访问。
- [x] AC-XCUT-004 Modal 背景遮罩不得吞掉内部滚动，也不得导致页面主体误滚动。
- [x] AC-XCUT-005 上传组件必须具备 `idle -> uploading -> done/failed` 状态机。
- [x] AC-XCUT-006 上传中必须禁用重复提交和重复选择触发；上传失败后必须允许重试。
- [x] AC-XCUT-007 上传成功后必须在同一会话立即回显到当前 Modal 和用户菜单展示链路，不依赖刷新页面。
- [x] AC-XCUT-008 上传成功后的 URL 或对象引用不得写入日志中的敏感上下文，且不得泄露临时凭据。
- [x] AC-XCUT-009 Docker 本地环境 `:3000` 边界必须能完成头像上传、读取和回显验收。
- [x] AC-XCUT-010 后端上传接口和对象访问路径必须在容器网络、浏览器访问和反向代理路径下保持一致。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: add-admin-user-menu-profile
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

