## MODIFIED Requirements

### Requirement: 超级管理员账号密码登录

系统 MUST 提供统一账号密码登录入口，支持系统内置超级管理员、具备后台管理员角色的用户和普通前台用户使用用户名和密码登录 MoonBox。登录认证 MUST 使用 `/api/v1/auth/login` 作为唯一正式 API；旧 `/api/v1/admin/auth/login` MUST 停止暴露。

#### Scenario: 超级管理员通过统一登录成功

- **GIVEN** 系统存在唯一系统内置超级管理员
- **AND** 超级管理员账号状态允许访问后台
- **WHEN** 超级管理员通过 `POST /api/v1/auth/login` 提交正确用户名和密码
- **THEN** 系统创建服务端会话记录
- **AND** 系统返回 access token、token 类型、过期时间和当前用户摘要
- **AND** 当前用户摘要包含用户 ID、用户名、昵称、头像 URL、角色、状态、是否系统内置超级管理员和是否可访问后台的服务端派生字段

#### Scenario: 普通前台用户通过统一登录成功

- **GIVEN** 用户不具备后台管理员角色
- **AND** 用户账号状态允许登录
- **WHEN** 用户通过 `POST /api/v1/auth/login` 提交正确用户名和密码
- **THEN** 系统创建服务端会话记录
- **AND** 系统返回 access token、过期时间和当前用户摘要
- **AND** 当前用户摘要表明该用户不可访问后台

#### Scenario: 待激活用户首次登录自动激活

- **GIVEN** 用户状态为待激活
- **WHEN** 用户通过统一登录接口提交有效临时密码登录
- **THEN** 系统允许本次首次登录激活
- **AND** 系统将用户状态更新为正常
- **AND** 系统创建服务端会话记录

#### Scenario: 已冻结或已删除用户不得登录

- **GIVEN** 用户状态为已冻结或已删除
- **WHEN** 用户提交正确用户名和密码
- **THEN** 系统拒绝登录
- **AND** 系统不得完成首次登录激活
- **AND** 系统不得创建服务端会话记录

#### Scenario: 旧后台登录路径不可用

- **WHEN** 客户端调用 `POST /api/v1/admin/auth/login`
- **THEN** 系统不得将该路径作为可用登录接口暴露
- **AND** 前端运行时代码、测试、OpenAPI 和生成客户端不得继续引用该路径

### Requirement: access token 与服务端会话记录

系统 MUST 使用 access token 与服务端会话记录共同表达统一登录态，并确保登录态可过期、可撤销、可校验。

#### Scenario: 统一认证接口校验会话

- **GIVEN** 请求目标为 `/api/v1/auth/me`、`/api/v1/auth/logout`、`/api/v1/auth/change-password` 或 `/api/v1/auth/avatar`
- **WHEN** 请求携带 access token
- **THEN** 系统校验 access token 签名或等价有效性
- **AND** 系统校验 access token 未过期
- **AND** 系统校验对应服务端会话存在、未过期且未撤销
- **AND** 系统校验关联账号状态可用

#### Scenario: 管理接口继续校验后台权限

- **GIVEN** 请求目标为 `/api/v1/admin/**`
- **WHEN** 请求携带统一登录获得的 access token
- **THEN** 系统校验 access token 和服务端会话
- **AND** 系统校验关联账号状态为正常
- **AND** 系统校验当前身份具备后台管理员角色或等价后台权限
- **AND** 系统拒绝无后台权限的普通前台用户访问后台 API

### Requirement: 退出登录与会话失效

系统 MUST 支持登录用户通过统一退出接口撤销当前会话，并在账号状态变化或密码修改成功时使相关会话失效。

#### Scenario: 统一退出登录撤销当前会话

- **GIVEN** 用户已登录 MoonBox
- **WHEN** 用户调用 `POST /api/v1/auth/logout`
- **THEN** 系统撤销当前服务端会话
- **AND** 前端清理统一 session 存储
- **AND** 再次使用同一个 access token 调用受保护接口返回 401

#### Scenario: 旧后台退出路径不可用

- **WHEN** 客户端调用 `POST /api/v1/admin/auth/logout`
- **THEN** 系统不得将该路径作为可用退出接口暴露
- **AND** 前端退出流程不得继续调用该路径

## ADDED Requirements

### Requirement: 当前用户与个人资料

系统 MUST 通过统一认证 API 面向所有已登录用户提供当前用户读取和本人资料更新能力。

#### Scenario: 当前用户读取

- **GIVEN** 用户已登录且会话有效
- **WHEN** 用户调用 `GET /api/v1/auth/me`
- **THEN** 系统返回当前用户摘要
- **AND** 系统不要求该用户具备后台管理员角色
- **AND** 当前用户摘要由后端登录态解析，不信任前端传入的用户 ID、角色、权限或后台访问字段

#### Scenario: 当前用户更新本人昵称和头像

- **GIVEN** 用户已登录且会话有效
- **WHEN** 用户调用 `PATCH /api/v1/auth/me` 提交昵称和头像 URL
- **THEN** 系统只更新当前登录用户自己的资料
- **AND** 昵称保存前去除首尾空白且最长 128 个字符
- **AND** 昵称清空时保存为空值或等价空状态
- **AND** 头像 URL 必须是后端返回或系统可访问的持久 URL
- **AND** 系统返回最新当前用户摘要

#### Scenario: 当前用户资料更新不得越权

- **WHEN** `PATCH /api/v1/auth/me` 请求体包含目标用户 ID、用户名、角色、状态、权限、密码或其他管理字段
- **THEN** 系统不得按这些字段修改目标或管理属性
- **AND** 系统返回受控校验错误或忽略非允许字段

#### Scenario: 旧后台当前用户路径不可用

- **WHEN** 客户端调用 `GET /api/v1/admin/auth/me` 或 `PATCH /api/v1/admin/auth/me`
- **THEN** 系统不得将这些路径作为可用当前用户接口暴露

### Requirement: 当前用户自助修改密码

系统 MUST 允许所有已登录用户通过统一认证 API 修改自己的密码，并在成功后撤销该用户所有服务端会话。

#### Scenario: 当前用户修改密码成功

- **GIVEN** 用户已登录且会话有效
- **WHEN** 用户调用 `POST /api/v1/auth/change-password` 提交当前密码、新密码和确认新密码
- **AND** 当前密码正确
- **AND** 新密码符合密码规则且确认一致
- **THEN** 系统更新当前用户密码哈希
- **AND** 系统撤销该用户所有服务端会话
- **AND** 响应不得返回新密码、密码哈希、access token、会话 ID 明文或任何可复用凭证
- **AND** 前端清理统一 session 并引导用户回到 `/login`

#### Scenario: 当前用户修改密码失败

- **WHEN** 当前密码错误、会话失效、账号不可用、新密码与当前密码相同、确认密码不一致或新密码不符合密码规则
- **THEN** 系统返回 401 或 400 的受控错误
- **AND** 系统不得泄露密码哈希、会话 ID、内部状态细节或可复用凭证

#### Scenario: 旧后台修改密码路径不可用

- **WHEN** 客户端调用 `POST /api/v1/admin/auth/change-password`
- **THEN** 系统不得将该路径作为可用自助修改密码接口暴露

### Requirement: 当前用户头像上传与读取

系统 MUST 将当前用户头像上传和读取纳入统一认证 API 范围，面向所有已登录用户可用。

#### Scenario: 当前用户上传头像成功

- **GIVEN** 用户已登录且会话有效
- **WHEN** 用户调用 `POST /api/v1/auth/avatar` 或等价统一认证路径上传头像
- **AND** 文件为 JPG、PNG 或 WebP
- **AND** 文件大小不超过 2 MB
- **THEN** 系统校验 MIME 类型、文件大小和对象存储写入结果
- **AND** 系统只为当前登录用户生成或返回头像资源引用
- **AND** 系统返回持久头像 URL 和处理状态

#### Scenario: 当前用户头像读取使用受保护代理

- **GIVEN** 用户资料包含头像 URL
- **WHEN** 前端展示头像
- **THEN** 头像读取通过受保护的后端代理路径完成
- **AND** 前端不得直连 MinIO 私有对象
- **AND** 前端不得暴露对象存储密钥、签名凭证或内部对象路径

#### Scenario: 头像上传状态机与回显

- **WHEN** 用户在个人资料入口上传头像
- **THEN** 前端必须表达 `idle -> uploading -> done/failed` 状态机
- **AND** 上传中禁用重复选择和重复提交
- **AND** 失败后允许重试
- **AND** 上传成功后在同一会话立即回显到当前个人资料入口和用户菜单

#### Scenario: 迁移后个人资料头像回显优先使用统一上下文

- **GIVEN** 统一 session 中仍保存 `/api/v1/admin/users/avatar/{filename}` 形式的历史头像 URL
- **AND** `/api/v1/auth/me` 或前台上下文接口返回了规范化后的 `/api/v1/auth/avatar/{filename}` 当前用户头像 URL
- **WHEN** 前端渲染前台用户菜单、前台个人资料弹窗、后台用户菜单或后台个人资料弹窗
- **THEN** 前端必须优先使用规范化后的当前用户头像 URL
- **AND** 前端不得让旧 session 头像快照覆盖已恢复的统一头像 URL
- **AND** 后台当前用户入口可通过 `GET /api/v1/auth/me` 刷新旧 session 中的当前用户摘要
- **AND** 没有头像图片时，前台与后台用户入口和个人资料弹窗使用同一套两字文字头像 fallback 规则

## MODIFIED Requirements

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

## ADDED Requirements

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
