# web-admin-auth-system Delta

## ADDED Requirements

### Requirement: 当前登录管理员自助修改密码

系统 MUST 支持已登录后台管理员从管理后台用户菜单自助修改自己的登录密码，并在修改成功后撤销当前用户全部旧后台会话。

自助修改密码接口 MUST 位于统一认证能力域 `POST /api/v1/auth/change-password`，并通过服务端登录态定位当前用户；管理后台入口仍 MUST 在前端路由和后台管理接口层执行后台管理员权限约束。

#### Scenario: 用户菜单打开修改密码 modal

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员打开用户菜单并点击“修改密码”
- **THEN** 前端必须打开修改密码 modal
- **AND** modal 必须包含当前密码、新密码、确认新密码、提交和取消操作
- **AND** 当前密码、新密码、确认新密码输入框 MUST 分别支持显示和隐藏密码明文
- **AND** 前端不得仅展示占位 toast 或跳转到独立页面

#### Scenario: 本地表单校验失败

- **GIVEN** 修改密码 modal 已打开
- **WHEN** 当前密码、新密码或确认新密码为空，或确认新密码与新密码不一致
- **THEN** 前端必须阻止提交
- **AND** 前端必须展示可恢复的字段级或表单级反馈

#### Scenario: 当前密码错误不得更新密码

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员提交错误当前密码和有效新密码
- **THEN** 后端必须返回受控错误
- **AND** 后端不得更新当前用户密码哈希
- **AND** 响应不得泄露账号状态、密码哈希算法、内部用户状态或系统路径

#### Scenario: 新密码不符合安全规则

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员提交空密码、示例密码、明显弱密码或与当前密码相同的新密码
- **THEN** 后端必须返回受控错误
- **AND** 后端不得更新当前用户密码哈希

#### Scenario: 修改密码成功后撤销全部旧会话

- **GIVEN** 后台管理员已登录管理后台
- **AND** 管理员提交正确当前密码和符合规则的新密码
- **WHEN** 后端完成密码修改
- **THEN** 后端必须更新当前用户密码哈希和更新时间
- **AND** 后端必须记录不含密码明文、密码哈希、access token 或会话 ID 明文的审计事件
- **AND** 后端必须撤销当前用户全部后台会话，包括当前会话
- **AND** 前端必须清理本地后台登录态并进入后台登录入口
- **AND** 再次使用旧 access token 调用 `/api/v1/admin/**` 必须返回 401

#### Scenario: 修改目标来自服务端登录态

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员提交修改密码请求
- **THEN** 后端必须从 access token 与服务端会话解析当前操作者
- **AND** 后端不得信任前端传入的 `user_id`、`role`、`is_admin` 或等价身份字段作为修改目标

### Requirement: 修改密码 modal 原型驱动验收

系统 MUST 将 REQ-0010 的 prototype 作为设计输入，并在实现、验收和归档前完成 UI Skeleton、1440px 视觉验收和最终一致性检查。

#### Scenario: Change 设计承接原型拆解

- **GIVEN** REQ-0010 提供 `prototype/web/context.md` 和 `prototype/web/prototype.html`
- **WHEN** 创建 OpenSpec Change
- **THEN** Change `design.md` 必须包含 UI Skeleton
- **AND** UI Contract / UI Skeleton 必须覆盖用户菜单触发、modal 容器、字段插槽、错误区、底部操作、状态容器、数据依赖、Mock/API 边界、可测选择器和 1440px 验收焦点

#### Scenario: 实现阶段完成 modal 横切验收

- **WHEN** 实现修改密码 modal
- **THEN** TSX 实现不得让通用 `modal-card` 与专属宽度类并存
- **AND** 必须通过浏览器 computed style 验收 modal 最终宽度
- **AND** 必须记录 Mock/API 边界，区分视觉验收 mock 数据与真实提交接口
- **AND** 低视口下 modal body 必须可滚动，底部提交和取消操作必须可访问
- **AND** modal 背景遮罩不得吞掉内部滚动，也不得导致页面主体误滚动
- **AND** 必填字段、错误提示和底部操作区不得互相遮挡

#### Scenario: 归档前完成 REQ 最终一致性检查

- **WHEN** 准备归档本 Change
- **THEN** 必须确认最终实现与 REQ-0010 的 requirement、acceptance、prototype 和 Change design 一致
- **AND** 必须记录 1440px 视觉验收证据或等价证据入口
