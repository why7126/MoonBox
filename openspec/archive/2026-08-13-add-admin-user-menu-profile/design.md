---
change_id: add-admin-user-menu-profile
status: proposed
source_requirement: REQ-0011-admin-user-menu-profile
source_sprint: sprint-002
created_at: 2026-08-10 09:30:11
updated_at: 2026-08-10 09:30:11
---

# 设计说明

## D1 UI 策略

采用“现有后台设计系统/弹窗样式复用 + 创建用户头像上传结构复用”的轻量 DS 策略：

- 复用现有后台用户菜单、按钮、输入框、toast 和 Modal 视觉语言。
- 个人资料 Modal 使用专属容器类控制宽度与滚动，不让通用 `modal-card` 与专属宽度类并存。
- 头像上传区参照创建用户表单结构，只保留一个 `admin-avatar large` 等价预览位、右侧格式提示和上传/更换按钮。
- 不引入独立页面、抽屉、新图标体系或额外身份摘要头像。
- 实现阶段必须通过浏览器 computed style 验收 Modal 宽度，并在 1440px 视口验收用户菜单、Modal、头像上传区、昵称输入、错误反馈、toast 和滚动。

## Conflict Resolution

| 来源 | 优先级 | 结论 |
|---|---:|---|
| `prototype/web/prototype.html` | 1 | 作为 HTML 结构输入，确认用户菜单触发、Modal、单头像上传区和底部保存操作。 |
| `prototype/web/context.md` | 2 | 作为原型拆解事实源，承接页面清单、组件层级、状态矩阵、数据依赖和 1440px 验收焦点。 |
| `acceptance.md` | 3 | 作为功能、安全、上传、刷新和横切 AC 事实源。 |
| `rules/ui-design.md` | 4 | 作为 MoonBox 视觉风格和 prototype-driven UI gate 事实源。 |
| `openspec/specs/web-admin-auth-system/spec.md` | 5 | 作为既有后台登录态与当前用户摘要规格，本 Change 在其上追加当前用户资料读取/更新。 |
| `openspec/specs/web-admin-user-management/spec.md` | 6 | 作为既有用户头像上传和创建用户表单头像结构规格，本 Change 复用头像上传链路但不开放他人资料编辑。 |

当前无阻断冲突。历史 req-complete 中曾短暂调整为独立页面，但最新 REQ、prototype、acceptance 和用户反馈均明确回到 Modal，最终设计以 Modal 为准。

## UI Skeleton

```text
AdminShell
  └─ AdminUserMenu
      ├─ UserTrigger: 当前头像 + 昵称/用户名
      └─ UserMenuOverlay
          ├─ menuitem: 个人资料
          ├─ menuitem: 修改密码
          ├─ switch/menuitem: 界面主题
          └─ menuitem: 退出登录

ProfileModal
  ├─ ModalHeader: 标题“个人资料” + 关闭入口
  ├─ UserSummaryText: username + role 文本摘要（不展示头像）
  ├─ AvatarUploader
  │   ├─ AvatarPreview: 单个 admin-avatar large 等价预览位
  │   ├─ AvatarHelpText: JPG/PNG/WEBP、1:1、最大 2MB
  │   ├─ UploadButton: 上传 / 更换 / 上传中
  │   ├─ HiddenFileInput
  │   └─ UploadError
  ├─ NicknameField: nickname，maxlength=128
  ├─ FormError / SuccessToast
  └─ ModalActions: 取消 / 保存
```

### 区域边界

- 用户菜单只负责触发、展示当前用户摘要和菜单项，不保存资料草稿。
- ProfileModal 管理头像草稿、昵称草稿、上传状态、保存状态和错误反馈。
- AvatarUploader 复用创建用户头像上传链路，但只返回持久头像 URL 给 ProfileModal。
- API 客户端负责当前用户资料更新请求和成功后刷新当前用户摘要。
- 后端认证依赖负责从 access token 与服务端会话解析当前用户，更新目标不得来自请求体。

### 状态容器

| 状态 | 前端表现 | 后端行为 |
|---|---|---|
| idle | Modal 打开，展示当前 username、role、头像和昵称 | 无写请求 |
| uploading | 上传/更换按钮与保存按钮禁用，展示上传中 | 上传头像对象并返回持久 URL |
| upload_failed | 保留表单和旧草稿，展示上传错误 | 不写入当前用户资料 |
| editing | 昵称或头像草稿已变化，保存可用 | 无写请求 |
| saving | 禁用保存，展示保存中 | 校验登录态并更新当前用户 nickname/avatar_url |
| save_failed | Modal 保持打开，展示可恢复错误 | 不污染当前用户摘要 |
| saved | 关闭 Modal 或展示成功 toast，菜单展示刷新 | 返回更新后的当前用户摘要 |

### 数据依赖

- 当前登录态：`access_token`、`expires_at`、`user`。
- 当前用户摘要：`id`、`username`、`nickname`、`avatar_url`、`role`、`status`、`is_system_superadmin`。
- 头像上传结果：后端返回的持久 `avatar_url`。
- 临时预览 URL：仅用于当前浏览器会话即时预览，不写入后端资料。

### 可测选择器

- 用户菜单个人资料项：role `menuitem` 与文本“个人资料”。
- 个人资料 Modal：role `dialog`，标题“个人资料”。
- 头像上传区：label “头像”，按钮文本“上传”“更换”“上传中”。
- 昵称输入：label “昵称”，`maxlength=128`。
- 保存按钮：文本“保存”。
- 错误反馈：`aria-live="polite"` 或等价可访问反馈区。

### 1440px 验收焦点

- 用户菜单浮层不被侧栏底部裁剪，点击“个人资料”后打开 Modal 并关闭菜单浮层。
- Modal 标题区、用户摘要文本、头像上传区、昵称输入区和底部操作区层级清楚。
- Modal 内只有一个头像图标，即头像上传区的预览位；身份摘要不得再展示头像。
- 头像预览、上传/更换按钮、昵称输入、错误提示、toast 和底部按钮没有重叠或溢出。
- 低视口下 Modal body 可滚动，底部取消/保存操作可访问。
- 保存成功后用户菜单头像、昵称或用户名即时刷新。

## 后端设计

- 在 `/api/v1/admin/auth` 或等价当前登录用户能力域下新增当前用户资料更新接口。
- 接口必须使用 `require_admin_user` 或等价依赖解析当前登录用户。
- 请求 schema 只接受 `nickname` 与 `avatar_url`；不得接受 `user_id`、`role`、`status`、`username`、`password`、`is_system_superadmin` 等字段。
- 昵称保存前去除首尾空白，允许为空，最长 128 个字符。
- `avatar_url` 必须来自后端头像上传结果或系统可访问的持久头像 URL；不得保存 `blob:` URL。
- 更新成功后返回当前用户摘要，字段与登录/`/me` 摘要保持一致。
- 失败响应必须使用受控错误，不泄露数据库错误、对象存储内部路径、堆栈或敏感配置。

## 前端设计

- 用户菜单“个人资料”从占位 toast 改为打开 ProfileModal。
- Modal 打开时使用当前会话摘要填充表单，必要时刷新 `/me` 或等价当前用户资料。
- 上传成功后先在 Modal 单头像预览位即时回显持久 URL；保存成功后再刷新全局当前用户摘要。
- 取消、关闭或未保存离开时丢弃草稿，不污染用户菜单展示。
- 保存成功后同步内存状态、本地会话缓存和用户菜单展示；昵称为空时菜单回退显示用户名。

## 测试设计

- 后端 pytest 覆盖成功更新、清空昵称、昵称超长、请求体指定目标用户无效、修改角色/状态/用户名/密码字段无效、未登录/会话失效、`blob:` URL 被拒绝或不持久 URL 不落库。
- 前端 Vitest/Testing Library 覆盖菜单打开 Modal、单头像预览位、上传/更换按钮文案、上传中禁用、保存禁用、取消丢弃草稿、保存成功刷新用户菜单、保存失败保留输入。
- 视觉验收覆盖 1440px 桌面视口和低视口 Modal 滚动。
- Docker 本地 `:3000` 验收覆盖头像上传、读取和回显链路。

## Knowledge Gate

引用：

- `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`
- `docs/knowledge-base/best-practices/admin-media-upload-chain.md`
- `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`
- `docs/knowledge-base/retrospectives/sprint-001-retrospective.md`

落地要求：

- `tasks.md` 必须包含 UI Skeleton 先行任务。
- `tasks.md` 必须包含 admin-modal 和 media-upload 横切验收任务。
- `tasks.md` 必须包含 1440px 视觉验收、Docker `:3000` 上传读取回显验收和 REQ 最终一致性回填。
