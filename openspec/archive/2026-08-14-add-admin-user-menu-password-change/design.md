---
change_id: add-admin-user-menu-password-change
status: applied
source_requirement: REQ-0010-admin-user-menu-password-change
source_sprint: sprint-002
created_at: 2026-08-10 09:14:08
updated_at: 2026-08-10 09:47:55
---

# 设计说明

## D1 UI 策略

采用“现有后台设计系统/弹窗样式复用 + 修改密码 modal 专属类”的轻量 DS 策略：

- 复用现有后台菜单、按钮、输入框、错误反馈和 modal 视觉语言。
- 为修改密码 modal 使用专属容器类控制宽度与滚动，不让通用 `modal-card` 与专属宽度类并存。
- 不引入新视觉资产，不新增独立页面。
- 实现阶段必须通过浏览器 computed style 验收 modal 宽度，并在 1440px 视口验收用户菜单、modal、错误反馈和滚动。

## Conflict Resolution

| 来源 | 优先级 | 结论 |
|---|---:|---|
| `prototype/web/prototype.html` | 1 | 作为 HTML 结构输入，确认用户菜单触发与 modal 表单结构。 |
| `prototype/web/context.md` | 2 | 作为原型拆解事实源，承接页面清单、组件层级、状态矩阵和 1440px 验收焦点。 |
| `acceptance.md` | 3 | 作为功能、安全、测试和横切 AC 事实源。 |
| `rules/ui-design.md` | 4 | 作为 MoonBox 视觉风格和 prototype-driven UI gate 事实源。 |
| `openspec/specs/web-admin-auth-system/spec.md` | 5 | 作为既有后台认证规格；本 Change 在其上追加自助改密能力。 |

当前无冲突：REQ 原型、验收和既有后台认证规格一致，均要求后端认证为最终安全边界、改密后旧会话失效、前端仅做体验优化。

## UI Contract

| 项 | 合同 |
|---|---|
| 事实源优先级 | `prototype/web/prototype.html` → `prototype/web/context.md` → `acceptance.md` → `rules/ui-design.md` / `docs/standards/prototype-ui-acceptance.md` → 既有后台认证规格 |
| 页面与入口 | 管理后台 `/admin` 底部用户菜单；后台用户打开“修改密码”后显示 modal，不跳转独立页面 |
| 信息架构 | 复用后台侧边栏、用户菜单和 `AdminModalBackdrop`；modal 内含标题、说明、三个密码字段、字段级/表单级错误、底部取消/更新密码操作 |
| 视觉 token | 复用后台暗/亮主题 token、2px 圆角、窄 modal 宽度、40px 输入框、36px 图标按钮和既有主按钮色 |
| 交互状态 | 支持必填、确认不一致、提交中、失败、成功清理登录态；三个密码字段分别支持显示/隐藏并具备可访问名称 |
| 图标与文案 | 菜单使用 `KeyRound`，显隐使用 `Eye` / `EyeOff`，文案中文优先：修改密码、当前密码、新密码、确认新密码、更新密码 |
| Mock/API 边界 | 视觉验收仅 mock 用户列表用于进入页面；提交契约使用真实统一认证接口 `/api/v1/auth/change-password`，本 Change 不引入新的 Mock API |
| 权限规则 | `/admin` 入口仍要求后台管理员登录态；改密接口使用服务端登录态定位当前用户，不信任前端目标身份字段 |
| 一致性参照 | 与现有后台用户菜单、重置密码 modal、登录页密码显隐交互保持一致 |

## UI Skeleton

```text
AdminUserManagementPage / 后台壳
  ├─ AdminSidebar
  │   └─ AdminUserMenu
  │       ├─ menuitem: 个人资料
  │       ├─ menuitem: 修改密码
  │       ├─ switch: 界面主题
  │       └─ menuitem: 退出登录
  └─ ChangePasswordModal
      ├─ header: 标题 + 改密后重新登录提示
      ├─ PasswordField: current_password
      ├─ PasswordField: new_password
      ├─ PasswordField: confirm_password
      ├─ VisibilityToggle: 每个 PasswordField 独立显示/隐藏
      ├─ FormError / FieldError
      └─ footer: 取消 / 更新密码
```

### 区域边界

- 用户菜单只负责触发和收起，不保存密码字段。
- 修改密码 modal 管理本地表单状态、提交中状态和错误反馈。
- 修改密码 modal 为当前密码、新密码、确认新密码提供独立显示/隐藏切换；切换仅影响本地输入类型，不改变提交 payload、不持久化密码字段。
- API 客户端封装请求和成功后的登录态清理。
- 认证仓储负责当前密码校验、密码哈希更新和会话撤销。

### 状态容器

| 状态 | 前端表现 | 后端行为 |
|---|---|---|
| idle | modal 打开，字段为空 | 无请求 |
| invalid_local | 必填缺失或确认不一致 | 无请求 |
| submitting | 禁用提交，显示提交中 | 校验登录态、当前密码和新密码 |
| failed | modal 保持打开，展示受控错误 | 不更新密码 |
| succeeded | 清理本地登录态并进入登录页 | 更新密码哈希，撤销全部会话 |

### 数据依赖

- 请求路径：`POST /api/v1/auth/change-password`。
- 请求 Header：`Authorization: Bearer <access_token>`。
- 请求体：`current_password`、`new_password`、`confirm_password` 或等价字段。
- 响应不得返回密码、密码哈希、access token 或会话 ID 明文。

### 可测选择器

- 用户菜单修改密码项：可通过 role `menuitem` 与文本“修改密码”定位。
- 修改密码 modal：role `dialog`，标题“修改密码”。
- 当前密码、新密码、确认新密码：使用中文 label。
- 显示/隐藏密码按钮：使用 `显示当前密码`、`隐藏当前密码`、`显示新密码`、`隐藏新密码`、`显示确认新密码`、`隐藏确认新密码` 等可访问名称。
- 提交按钮：文本“更新密码”。
- 错误反馈：`aria-live="polite"` 或等价可访问反馈区。

### 1440px 验收焦点

- 用户菜单中“修改密码”与其他菜单项视觉层级一致。
- modal 宽度、字段间距、显示/隐藏图标按钮、底部按钮和错误反馈不溢出。
- 低视口下 modal body 可滚动，底部操作可访问。
- 背景遮罩不吞掉 modal 内部滚动，也不导致页面主体误滚动。
- 修改成功后不得停留在看似已登录的后台页面。

## 后端设计

- 在 `/api/v1/admin/auth` 能力域下新增当前登录用户自助改密接口。
- 接口必须使用 `require_admin_user` 或等价依赖解析当前登录用户。
- 仓储层复用 `verify_password` 和 `hash_password`，新增当前用户密码变更逻辑。
- 新密码规则复用并收紧后台认证安全约束：拒绝空密码、示例密码、明显弱密码，并拒绝与当前密码相同。
- 成功后撤销当前用户所有未撤销后台会话，包括当前会话。
- 审计事件只记录动作、操作者、目标用户、时间和安全摘要。

## 测试设计

- 后端 pytest 覆盖成功改密、当前密码错误、弱密码、与当前密码相同、未登录、会话失效和旧 token 失效。
- 前端 Vitest/Testing Library 覆盖菜单打开 modal、字段校验、确认不一致、提交成功后清理登录态并进入登录入口。
- 实现阶段补充 API 文档和安全文档同步验证。

## Knowledge Gate

引用：

- `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`
- `docs/knowledge-base/retrospectives/sprint-001-retrospective.md`

落地要求：

- `tasks.md` 必须包含 UI Skeleton 先行任务。
- `tasks.md` 必须包含 admin-modal 横切验收任务。
- `tasks.md` 必须包含 1440px 视觉验收和 REQ 最终一致性回填。
