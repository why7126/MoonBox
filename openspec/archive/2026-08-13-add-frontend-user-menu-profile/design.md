---
change_id: add-frontend-user-menu-profile
status: proposed
created_at: 2026-08-11 17:36:19
updated_at: 2026-08-11 18:48:00
source_requirement: REQ-0014-frontend-user-menu-profile
sprint: sprint-002
---

# Design

## 决策摘要

| 决策 | 结论 |
|---|---|
| D1 UI 策略 | 使用前台 `rc-*` Design System 扩展，不直接复用后台 `admin-*` 样式。 |
| D2 资料保存 | 复用当前用户资料保存能力或封装等价前台服务；保存成功后直接使用返回 user 更新前台上下文。 |
| D3 头像上传 | 复用现有对象存储头像上传和受保护读取链路；保存持久 URL，不保存 `blob:` URL。 |
| D4 昵称空值 | 允许清空，后端保存为空值或等价空状态，前台展示回退用户名。 |
| D5 数据刷新 | 不强制重新拉取 `/api/v1/requirement-center/context`；只更新 currentUser 与会话缓存。 |
| D6 前后台一致性 | 前后台个人资料弹窗保持同构交互结构；前台继续使用 `rc-*` token，后台使用 `admin-*` token。 |

## Conflict Resolution

事实源优先级：

```text
prototype/web/prototype.html
  > prototype/web/context.md
  > acceptance.md
  > requirement.md
  > rules/ui-design.md
  > existing src/web implementation
  > openspec/specs
```

冲突处理：

- 若原型与现有用户菜单行为冲突，以 REQ-0012 已验收的用户菜单分组、空间浮层、进入后台权限和退出登录行为为底线，本 Change 只补“个人资料”入口闭环。
- 若后台个人资料样式与前台原型冲突，以前台 `rc-*` 视觉为准；后台 `admin-*` 仅作为交互结构和 API 复用参照。
- 若验收要求前后台交互样式一致，统一 Modal 信息架构、宽度、标题行、关闭入口、单头像预览位和 footer 行为；视觉色彩、边框圆角和 class 前缀仍按前台/后台域区分。
- 若保存接口返回字段与需求中心 currentUser 字段命名不同，前端必须在边界层归一化，不把后端 snake_case 泄露到组件内部。
- 若头像上传成功但头像读取失败，弹窗必须展示受控错误并允许重试，不得保存 `blob:` URL。
- 若前台与后台在同一 SPA 会话内切换，当前用户头像/昵称和界面主题偏好必须使用共享本地状态同步，不得停留在各页面初始化时的旧 state。

## UI Contract

### 页面与入口

- 页面：`/requirements` 前台需求中心。
- 入口：左侧边栏底部 `rc-user-menu` 账号分组内“个人资料”菜单项。
- 默认行为：点击“个人资料”关闭用户菜单，打开前台个人资料弹窗。
- 权限：仅当前登录用户可编辑自己的头像和昵称；目标用户由后端认证上下文决定，前端不得传入任意目标用户 ID。

### 信息架构

```text
RequirementCenterPage
  ├─ rc-sidebar
  │  └─ rc-user-zone
  │     ├─ rc-user-trigger
  │     └─ rc-user-menu
  │        └─ 账号 / 个人资料
  └─ rc-profile-mask
     └─ rc-profile-modal
        ├─ header: 个人资料 + 关闭
        ├─ account summary: 仅显示用户名
        ├─ avatar picker: 单头像预览 + 上传/更换按钮 + 隐藏 file input
        ├─ nickname field
        ├─ upload/save error
        └─ footer: 取消 + 保存
```

### 视觉 Token

- 使用 `rc-*` 前台 token：深色默认背景、细线边框、金色主操作、近直角、低阴影。
- 弹窗宽度采用与后台个人资料 Modal 一致的 `min(560px, calc(100vw - 40px))`，低视口 body 可滚动。
- 标题行与后台保持同构：左侧标题“个人资料”，右侧关闭按钮；前台不得额外展示 eyebrow。
- 头像预览仅出现一个，并与后台个人资料头像预览位保持 48px 圆形尺寸。
- 前后台用户菜单头像统一为 32px 圆形尺寸。
- 昵称输入框必须显式使用可读文字色和光标色，避免在深色 `rc-*` 面板中与背景低对比。
- 按钮高度、字号和间距需与前台用户菜单/空间设置弹窗密度一致，不得引入后台 `admin-profile-modal`、`admin-avatar-picker` 等视觉类。

### 交互状态

| 状态 | 要求 |
|---|---|
| idle | 当前头像或首字头像、昵称可编辑、保存可用。 |
| uploading | 上传按钮显示上传中，上传与保存禁用。 |
| upload_failed | 展示错误，允许重新选择文件。 |
| upload_done | 立即预览新头像，保存提交持久 URL。 |
| saving | 保存按钮显示保存中并禁用重复提交。 |
| save_failed | 保留输入内容和头像选择，展示错误并允许重试。 |
| saved | 关闭弹窗，刷新 currentUser、用户菜单和会话缓存。 |

### 跨前后台同步

- 当前用户资料保存成功后，前台必须同步后台 admin session，并通知顶层路由状态刷新；随后进入 `/admin` 时后台用户菜单展示最新头像、昵称或用户名。
- 前台与后台“界面主题”使用共享 UI 偏好缓存；任一端切换后，另一端在同 SPA 路由切换或事件通知后必须跟随最新主题。

### 图标与文案

- “个人资料”继续使用与前后台一致的用户图标。
- 修改密码入口不在本 Change 中实现或调整。
- 上传按钮文案随状态为“上传”“更换”“上传中”或等价产品化文案。
- 个人资料弹窗只读摘要仅显示用户名，不附加“需求中心”“超级管理员”等产品域或角色文本。
- 昵称字段不展示“保存后同步刷新前台用户菜单”一类实现说明文案。
- 错误提示不得暴露对象存储内部路径、数据库错误、堆栈或密钥。

### Mock/API 边界

- 真实 API：头像上传、头像读取、当前用户资料保存。
- 不使用生产 Mock 数据冒充保存成功。
- 若实现阶段复用 `/api/v1/admin/auth/me` 和 `/api/v1/admin/users/avatar`，Change trace 必须声明前台复用边界与权限理由。
- 如需新增前台别名接口，必须同步 `docs/03-api-index.md` 和测试。

### Computed Style 验收点

- `.rc-profile-modal`：`width`、`max-height`、`overflow`、`background`、`border`、`z-index`。
- `.rc-profile-avatar-picker`：`display`、`gap`、`padding`、头像预览 `width/height`。
- `.rc-profile-actions button`：`height`、`padding`、`background`、`color`、disabled 样式。
- 错误提示：`color`、`font-size`、`line-height`、不撑破容器。

### 前后台一致性 Checklist

- 相同“个人资料”功能使用一致用户图标，但前台样式使用 `rc-*`。
- 前后台个人资料 Modal 信息架构保持一致：标题行、仅用户名摘要、头像上传、昵称、错误提示、footer。
- 前后台均提供右上角关闭按钮；取消按钮仍保留为 footer 次要操作。
- 前台弹窗不得出现后台角色、状态、重置密码、冻结、删除等字段。
- 头像上传结构对齐后台单头像预览位，弹窗头像统一 48px；用户菜单头像统一 32px；不得出现两个头像图标。
- 用户菜单既有空间二级浮层、退出登录危险色和进入后台权限显示不回归。

## UI Skeleton

先行 Skeleton 必须完成：

- 在 `RequirementCenterPage` 增加 `isProfileModalOpen` 状态容器。
- 将“个人资料”菜单项接线为打开弹窗并关闭用户菜单。
- 增加 `FrontendProfileModal` 或等价组件，包含头像区、昵称输入、错误区、取消/保存 footer。
- 增加上传状态容器：`idle/uploading/done/failed`。
- 增加保存状态容器：`idle/saving/failed`。
- 增加 currentUser 更新回调，保存成功后更新页面状态与会话缓存。
- 提供可测选择器或可访问标签：`role="dialog" aria-label="个人资料"`、`aria-label="选择头像文件"`、保存按钮、错误提示。
- 产出 1440px Skeleton 截图，覆盖用户菜单打开态和个人资料弹窗默认态。

## 技术方案

### 前端

- 扩展 `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的用户菜单和当前用户状态。
- 复用或抽取后台认证服务中的当前用户资料更新方法，确保保存后返回用户摘要。
- 复用已存在的受保护头像读取方法，上传成功后以 object URL 预览，保存持久 URL。
- 单元测试覆盖菜单打开弹窗、上传成功/失败、保存成功刷新、保存失败保留内容、昵称清空回退和非目标回归。

### 后端/API

- 优先复用现有当前用户资料更新接口和头像上传接口。
- 如前端复用后台路径，必须保证 Bearer token、权限校验、错误脱敏和前台使用场景合法。
- 若需要新增前台友好路径，必须补齐 schema、API index 和集成测试。

### 存储

- 头像对象继续写入 `images/avatars/{uuid}.{ext}` 或现有配置前缀。
- 前端不得直连 MinIO 私有对象。
- Docker 本地 `:3000` 环境必须完成上传、读取和回显验证。

## 验证策略

- 前端：`pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx --run`
- 前端构建：`pnpm --dir src/web build`
- 后端：如新增/调整 API，运行对应 pytest 集成测试。
- OpenSpec：`openspec validate add-frontend-user-menu-profile --strict`
- UI：1440px 截图与 computed style 证据。
- Docker 边界：本地 `:3000` 上传、受保护读取、前台菜单回显。

## 文档同步

- 如 API 路径或响应契约变化，同步 `docs/03-api-index.md`。
- 如对象存储策略变化，同步 `docs/07-object-storage-strategy.md`；当前预期无策略变化。
- 如 UI 实现偏离 REQ 原型，回填 REQ acceptance/trace 与 Change trace。
