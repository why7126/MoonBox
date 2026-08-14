# web-admin-auth-system Specification

## Purpose
定义 MoonBox Web 登录、统一账号认证、服务端会话、管理后台路由守卫、后台 API 鉴权和认证敏感信息保护的正式能力边界。
## Requirements
### Requirement: 超级管理员账号密码登录

系统 MUST 保持后台管理员和系统超级管理员可使用统一登录态进入后台，并继续拒绝无后台权限身份访问后台能力。

#### Scenario: 后台管理员通过统一登录后进入后台

- **GIVEN** 用户具备后台管理员角色
- **AND** 用户已通过统一登录入口登录
- **WHEN** 用户点击前台用户菜单中的“进入后台”
- **THEN** 系统校验当前用户具备后台权限
- **AND** 系统允许用户进入后台

#### Scenario: 超级管理员通过统一登录后进入后台

- **GIVEN** 用户为系统内置超级管理员
- **AND** 用户已通过统一登录入口登录
- **WHEN** 用户点击前台用户菜单中的“进入后台”
- **THEN** 系统校验当前用户具备后台权限
- **AND** 系统允许用户进入后台

#### Scenario: 前台用户不得进入后台

- **GIVEN** 用户角色为前台用户
- **AND** 用户已通过统一登录入口登录
- **WHEN** 用户访问后台页面或调用后台 API
- **THEN** 系统拒绝访问
- **AND** 系统不得将该用户视为后台管理员

### Requirement: access token 与服务端会话记录
系统 MUST 使用 access token 与服务端会话记录共同表达后台登录态，并确保后台登录态可过期、可撤销、可校验。

#### Scenario: 后台 API 校验会话
- **GIVEN** 请求目标为 `/api/v1/admin/**`
- **WHEN** 请求携带 access token
- **THEN** 系统校验 access token 签名或等价有效性
- **AND** 系统校验 access token 未过期
- **AND** 系统校验对应服务端会话存在、未过期且未撤销
- **AND** 系统校验关联账号状态为正常
- **AND** 系统拒绝待激活、已冻结、已删除或无后台管理员角色的账号访问后台 API

#### Scenario: 无效会话被拒绝
- **WHEN** 请求携带的 access token 过期、无效、对应会话不存在、已过期或已撤销
- **THEN** 系统返回 401
- **AND** 系统不得执行业务处理

### Requirement: 退出登录与会话失效
系统 MUST 支持后台管理员退出登录，并在账号状态变化时使相关后台会话失效。

#### Scenario: 退出登录撤销当前会话
- **GIVEN** 管理员已登录管理后台
- **WHEN** 管理员执行退出登录
- **THEN** 系统撤销当前服务端会话
- **AND** 前端清理本地登录态
- **AND** 再次使用同一个 access token 调用 `/api/v1/admin/**` 返回 401

#### Scenario: 账号状态变化使旧会话失效
- **WHEN** 账号被冻结、删除、重置密码或发生影响权限的状态变化
- **THEN** 系统使相关后台会话失效
- **AND** 相关旧 access token 不得继续访问 `/api/v1/admin/**`

#### Scenario: 临时密码说明登录前提
- **WHEN** 管理员创建后台用户或重置后台用户密码后展示临时密码
- **THEN** 前端必须提示临时密码可用于具备后台管理员角色的账号首次登录激活或正常登录
- **AND** 前端不得暗示前台用户、已冻结或已删除账号可凭临时密码登录后台

### Requirement: 后台路由守卫

系统 MUST 在 Web 前端使用统一 session 保护前台需求中心和管理后台路由，避免未登录、无后台权限或登录态失效用户进入不可用状态。

#### Scenario: 统一登录后默认进入前台需求中心

- **WHEN** 用户通过 `/login` 完成统一登录
- **THEN** 前端写入单一统一 session 存储
- **AND** 前端默认进入 `/requirements` 或等价前台工作台
- **AND** 具备后台权限的用户可从前台入口进入 `/admin`

#### Scenario: 管理后台入口基于统一 session 展示

- **GIVEN** 用户已登录
- **WHEN** 前端渲染进入后台入口或访问 `/admin`
- **THEN** 前端可基于当前用户摘要中的 `can_access_admin` 或等价服务端事实控制入口展示
- **AND** 后端 `/api/v1/admin/**` 接口仍独立执行后台权限校验

#### Scenario: 登录态异常清理统一 session

- **WHEN** 退出登录、修改密码成功、401 认证失败、会话撤销或账号不可用
- **THEN** 前端清理统一 session
- **AND** 前台和后台不得出现一边已退出、一边仍显示已登录的错位状态

### Requirement: 后台 API 正式鉴权

系统 MUST 在统一登录能力存在时继续保护 `/api/v1/admin/**` 管理接口，后台接口不得因为用户已登录前台而放宽权限。

#### Scenario: 管理接口拒绝普通前台用户

- **GIVEN** 普通前台用户已登录
- **WHEN** 用户请求 `/api/v1/admin/**`
- **THEN** 系统返回权限拒绝
- **AND** 系统不得执行业务处理

#### Scenario: 管理接口允许后台角色

- **GIVEN** 后台管理员或系统超级管理员已登录
- **WHEN** 用户请求 `/api/v1/admin/**`
- **THEN** 系统校验服务端会话、账号状态和后台权限
- **AND** 校验通过后执行业务处理

### Requirement: 超级管理员首次初始化

系统 MUST 支持通过环境变量首次幂等创建唯一系统内置超级管理员，并在生产环境拒绝弱初始密码。

#### Scenario: 首次初始化超级管理员

- **GIVEN** 系统不存在系统内置超级管理员
- **WHEN** 系统启动或执行初始化流程
- **THEN** 系统读取环境变量中的超级管理员用户名和初始密码
- **AND** 系统创建唯一系统内置超级管理员

#### Scenario: 重复启动不重复创建

- **GIVEN** 系统已存在系统内置超级管理员
- **WHEN** 系统再次启动或执行初始化流程
- **THEN** 系统不得创建第二个系统内置超级管理员

#### Scenario: 生产弱密码被拒绝

- **GIVEN** 系统运行在生产环境
- **WHEN** 超级管理员初始密码为空、为示例值或不满足强度要求
- **THEN** 系统拒绝完成生产初始化
- **AND** 系统给出受控错误
- **AND** 系统不得记录明文初始密码

### Requirement: 认证敏感信息保护

系统 MUST 防止认证敏感信息出现在 URL、日志、错误上报、埋点、截图、API 响应或审计明文中。

#### Scenario: 敏感凭证不进入可见通道

- **WHEN** 系统处理登录、退出、会话校验或认证失败
- **THEN** 明文密码、access token、会话 ID 明文不得写入 URL、日志、错误上报、埋点、截图、API 响应或审计明文

### Requirement: 前端统一 session 存储

系统 MUST 使用单一 Web session 存储表达当前登录态，并移除前台和后台双 session 的运行时依赖。

#### Scenario: 登录成功只写入统一 session

- **WHEN** 用户登录成功
- **THEN** 前端只写入 `moonbox.session` 或等价统一 session
- **AND** session 包含 access token、过期时间和当前用户摘要
- **AND** 前端不得再依赖 `moonbox.frontend.session` 与 `moonbox.admin.session` 作为运行时登录态来源

#### Scenario: 当前用户更新后刷新统一 session

- **WHEN** `PATCH /api/v1/auth/me` 成功返回最新当前用户摘要
- **THEN** 前端刷新当前用户上下文
- **AND** 前端刷新统一 session 中的当前用户摘要
- **AND** 前台需求中心、后台用户菜单和个人资料入口展示保持一致

### Requirement: 当前登录管理员个人资料读取与更新

系统 MUST 支持已登录后台管理员读取并更新自己的个人资料摘要，且更新目标必须来自服务端认证上下文。

#### Scenario: 当前用户资料读取使用认证上下文

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 前端读取当前用户资料或刷新当前用户摘要
- **THEN** 后端必须从 access token 与服务端会话解析当前操作者
- **AND** 响应必须包含当前用户 ID、用户名、昵称、头像 URL、角色和账号状态等摘要字段
- **AND** 后端不得信任前端传入的 `user_id`、`role`、`is_admin` 或等价身份字段

#### Scenario: 当前用户资料更新仅允许头像和昵称

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员提交个人资料更新请求
- **THEN** 后端必须只允许更新当前登录用户自己的 `nickname` 与 `avatar_url`
- **AND** 后端必须拒绝或忽略请求体中的目标用户 ID、角色、状态、用户名、密码、空间数、最近登录时间或系统内置超级管理员保护字段
- **AND** 更新成功后必须返回更新后的当前用户摘要

#### Scenario: 昵称规则

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员保存昵称
- **THEN** 后端必须去除昵称首尾空白
- **AND** 昵称必须允许为空
- **AND** 昵称最长不得超过 128 个字符
- **AND** 昵称为空时前端用户菜单必须回退展示用户名

#### Scenario: 头像 URL 必须为持久 URL

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员保存头像
- **THEN** 后端保存到 `avatar_url` 的值必须是持久可访问头像 URL
- **AND** 后端不得保存 `blob:` URL 或仅当前浏览器有效的临时预览 URL
- **AND** 头像保存失败时系统必须返回受控错误

#### Scenario: 登录态失效时资料读取或更新被拒绝

- **WHEN** 当前用户资料读取或更新请求携带的 access token 过期、无效、对应会话不存在、已过期、已撤销或账号不可用
- **THEN** 系统必须返回受控认证错误
- **AND** 系统不得读取或更新个人资料
- **AND** 前端必须触发已有登录态失效处理

#### Scenario: 资料更新失败不泄露内部信息

- **WHEN** 当前用户资料读取、头像 URL 校验或资料更新失败
- **THEN** 系统必须返回受控错误文案
- **AND** 响应不得泄露数据库错误、对象存储内部路径、堆栈、密钥、access token、会话 ID 明文或敏感配置

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

