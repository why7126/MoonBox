---
requirement_id: REQ-0016-unified-account-auth-api
title: 统一账号认证与个人中心 API
terminal: multi
version: v1
status: done
owner: product
source: capture.md
priority: P1
parent_requirement:
created_at: 2026-08-12 00:14:27
updated_at: 2026-08-13 22:50:11
---

# 统一账号认证与个人中心 API

## 背景

MoonBox 当前已经具备账号密码登录、服务端会话、退出登录、当前用户读取、自助修改密码、个人资料更新和头像上传等能力。后端实际使用同一套 Bearer token 与服务端会话支持 Web 前台需求中心和管理后台，但正式接口仍挂在 `/api/v1/admin/auth/*` 下，前端也同时维护 `moonbox.frontend.session` 与 `moonbox.admin.session` 两套本地会话存储。

这种形态会让“统一账号登录”在产品语义和技术边界上显得割裂：前台用户可以登录需求中心，却需要调用带 `admin/auth` 命名的登录和退出接口；具备后台权限的用户会产生额外后台 session 缓存；个人资料和头像能力也容易被误解为仅属于后台管理员。随着前台需求中心成为主工作台，账号认证和个人中心能力需要从后台命名中剥离，形成清晰的统一账号 API。

本需求要求新增并改用 `/api/v1/auth/*` 作为唯一正式认证与个人中心 API 路径，并且不保留旧 `/api/v1/admin/auth/*` 路径。迁移完成后，后台权限仍由 `/api/v1/admin/**` 资源接口进行二次授权；认证、当前用户、修改密码、个人资料和头像上传则面向所有已登录用户。

## 目标用户

- 前台需求中心用户：需要通过统一登录态进入需求中心，并维护自己的昵称、头像和密码。
- 后台管理员：需要使用同一账号登录前台和管理后台，并在具备后台权限时进入后台管理能力。
- 产品与研发团队：需要消除 `admin/auth` 路径命名和双 session 存储带来的认知成本，降低后续新增端和客户端生成的维护风险。
- 安全与运维角色：需要明确认证、授权、会话撤销和敏感凭证保护边界，避免前端状态被误用为后端权限来源。

## 范围

### 包含

- 新增 `/api/v1/auth/login`，作为统一账号密码登录接口。
- 新增 `/api/v1/auth/logout`，作为统一退出登录和当前服务端会话撤销接口。
- 新增 `/api/v1/auth/me`，支持读取当前登录用户摘要。
- 新增 `PATCH /api/v1/auth/me`，支持所有登录用户修改自己的昵称和头像 URL。
- 新增 `/api/v1/auth/change-password`，支持所有登录用户自助修改密码，成功后撤销该用户所有服务端会话。
- 新增 `/api/v1/auth/avatar` 和受保护头像读取路径，支持所有登录用户上传和读取自己的头像资源。
- 删除或停止暴露旧 `/api/v1/admin/auth/*` 路径，不提供兼容别名。
- 前端统一为单一登录态存储，例如 `moonbox.session`，替代 `moonbox.frontend.session` 与 `moonbox.admin.session` 双存储。
- 前台需求中心和管理后台共同读取统一 session；是否可进入后台由当前用户摘要中的角色、权限或 `can_access_admin` 等服务端事实决定。
- 同步 API 文档、认证标准、OpenAPI 契约、客户端生成物和相关后端/前端测试。

### 不包含

- 不新增用户注册、忘记密码、邮箱验证、短信验证、OAuth、企业 SSO 或组织目录同步。
- 不新增 refresh token、自动续期、多端互踢、设备管理或复杂会话列表。
- 不新增 MFA；敏感操作重新认证、MFA 或账号恢复由后续安全需求承接。
- 不改变后台用户管理接口 `/api/v1/admin/users/*` 的资源边界和后台管理员授权要求。
- 不改变后台管理员重置他人密码、冻结、解冻、删除用户等管理能力。
- 不重做登录页、前台用户菜单、后台用户菜单或个人资料弹窗的视觉设计。
- 不新增移动端、小程序或桌面端登录能力。

## 功能要求

### FR-001 统一登录接口

系统 MUST 提供 `POST /api/v1/auth/login` 作为唯一正式账号密码登录接口。

登录请求 MUST 支持用户名、密码和记住登录或等价会话时长选项。登录成功后，系统 MUST 返回 access token、token 类型、过期时间和当前用户摘要。当前用户摘要 SHOULD 至少包含用户 ID、用户名、昵称、头像 URL、角色、状态、是否系统内置超级管理员，以及是否可访问后台的服务端派生字段。

正常用户和待激活用户 MAY 使用统一登录接口登录；待激活用户首次登录成功后 SHOULD 按现有策略自动激活为正常。已冻结、已删除或账号不可用用户不得获得有效会话。

系统 MUST 停止暴露 `POST /api/v1/admin/auth/login`。迁移后前端、测试、API 文档和客户端生成物不得继续引用旧登录路径。

### FR-002 统一退出登录与会话撤销

系统 MUST 提供 `POST /api/v1/auth/logout` 作为唯一正式退出登录接口。

退出登录请求 MUST 使用 `Authorization: Bearer <access_token>` 识别当前服务端会话，并撤销该会话。退出成功后，继续使用同一 access token 调用受保护接口 MUST 返回 401。

系统 MUST 停止暴露 `POST /api/v1/admin/auth/logout`。前端退出流程 MUST 只调用统一退出接口，并清理统一 session 存储。

### FR-003 当前用户读取

系统 MUST 提供 `GET /api/v1/auth/me` 读取当前登录用户摘要。

该接口 MUST 面向所有已登录用户，不要求后台管理员角色。未登录、token 缺失、token 无效、会话过期或会话已撤销时 MUST 返回 401。账号状态不可用时 MUST 返回受控错误，不得泄露内部状态细节。

当前用户摘要 MUST 由后端登录态解析，不得信任前端传入的 `user_id`、`role`、`is_admin`、`can_access_admin` 或等价字段。

系统 MUST 停止暴露 `GET /api/v1/admin/auth/me`。

### FR-004 当前用户个人资料更新

系统 MUST 提供 `PATCH /api/v1/auth/me`，允许所有登录用户修改自己的昵称和头像 URL。

资料更新目标 MUST 以后端认证上下文中的当前用户为准，不得允许请求体指定目标用户 ID、用户名、角色、状态、权限、密码或其他管理字段。

昵称允许为空，最长 128 个字符。保存时系统 MUST 去除首尾空白；用户清空昵称时，系统 MUST 保存为空值或等价空状态。头像 URL MUST 是后端返回或系统可访问的持久 URL，不得保存 `blob:`、本地临时路径或不可复用对象地址。

更新成功后，系统 MUST 返回最新当前用户摘要，供前端立即刷新前台需求中心、后台用户菜单和统一 session 缓存。

系统 MUST 停止暴露 `PATCH /api/v1/admin/auth/me`。

### FR-005 当前用户自助修改密码

系统 MUST 提供 `POST /api/v1/auth/change-password`，允许所有登录用户修改自己的密码。

请求 MUST 包含当前密码、新密码和确认新密码。当前密码错误、会话失效或账号不可用时 MUST 返回 401；新密码与当前密码相同、确认密码不一致或不符合密码规则时 MUST 返回 400。

修改成功后，系统 MUST 更新当前用户密码哈希，撤销该用户所有服务端会话，并返回受控成功结果。响应不得返回新密码、密码哈希、access token、会话 ID 明文或任何可复用凭证。

前端收到修改成功响应后 MUST 清理统一 session，并引导用户回到 `/login` 或等价统一登录入口。

系统 MUST 停止暴露 `POST /api/v1/admin/auth/change-password`。

### FR-006 统一头像上传与读取

系统 MUST 将当前用户头像上传纳入 `/api/v1/auth/*` 统一范围，提供 `POST /api/v1/auth/avatar` 或等价统一路径。

头像上传 MUST 面向所有登录用户，不要求后台管理员角色。上传请求 MUST 经过 Bearer token 鉴权，只允许当前登录用户为自己的资料上传头像资源。

头像上传 MUST 支持 JPG、PNG、WebP，单文件大小不超过 2MB。后端 MUST 校验 MIME 类型、文件大小和对象存储写入结果。上传成功后 MUST 返回持久头像 URL 和处理状态，供 `PATCH /api/v1/auth/me` 保存。

头像读取 MUST 通过受保护的后端代理路径完成，前端不得直连 MinIO 私有对象，不得暴露对象存储密钥、签名凭证或内部对象路径。若沿用 `/api/v1/admin/users/avatar/{filename}` 会造成统一边界混淆，系统 SHOULD 提供 `/api/v1/auth/avatar/{filename}` 或等价读取路径，并迁移前端引用。

### FR-007 单一前端 session 存储

前端 MUST 使用单一统一 session 存储保存当前登录态，例如 `moonbox.session`。该 session SHOULD 包含 access token、过期时间和当前用户摘要。

前端 MUST 移除对 `moonbox.frontend.session` 与 `moonbox.admin.session` 双存储的运行时依赖。登录成功后，无论用户是否具备后台权限，都只写入统一 session。

前台需求中心路由守卫 MUST 基于统一 session 判断是否已登录。管理后台路由守卫 MUST 基于统一 session 中的用户摘要和后端权限事实判断是否可进入后台；最终安全判断仍以后端 `/api/v1/admin/**` 接口授权结果为准。

退出登录、修改密码成功、401 认证失败和账号不可用等场景 MUST 清理统一 session，避免前台和后台出现一边已退出、一边仍显示已登录的错位状态。

### FR-008 后台授权边界保持独立

统一认证 API 不得削弱管理后台授权边界。

所有 `/api/v1/admin/**` 管理资源接口 MUST 继续要求有效 Bearer token、服务端会话、账号状态正常和后台管理员角色或等价后台权限。普通前台用户可以登录、进入需求中心、修改自己的资料和密码，但不得访问后台用户管理、角色管理、用户状态管理、重置他人密码或其他管理端接口。

前端可使用当前用户摘要中的 `can_access_admin` 或等价字段控制“进入后台”入口展示，但不得把该字段作为后端授权依据。

### FR-009 破坏性迁移与契约同步

本需求明确要求不保留旧 `/api/v1/admin/auth/*` 路径。实现时 MUST 将旧路径从后端路由、前端调用、集成测试、前端测试、API 文档、OpenAPI 契约和客户端生成物中移除。

若外部部署、脚本或文档仍引用旧路径，系统 MUST 在交付前同步迁移或明确标记为已废弃并不可用。不得通过兼容别名、重定向或双注册路由绕过本需求。

由于该变更是破坏性 API 迁移，发布说明或验收报告 SHOULD 明确提示旧路径不可用。

### FR-010 错误反馈与安全约束

登录失败、未认证、凭证过期、会话撤销、权限不足、账号不可用、头像上传失败、资料校验失败和密码规则失败等场景 MUST 使用统一 API 响应和受控错误码。

认证与个人中心相关日志、审计、错误响应、前端缓存、测试 fixture 和文档示例不得保存明文密码、access token、会话 ID 明文、密码哈希、对象存储密钥、签名凭证或 `.env` 内容。

系统 SHOULD 保持 401 表示认证失败或会话失效，403 表示已认证但权限不足。资源归属不匹配不得泄露不该知道的资源存在性。

## UI 约束

- 本需求不重做登录页、前台需求中心用户菜单、后台用户菜单或个人资料弹窗视觉。
- 登录页仍作为统一入口使用 `/login`，登录成功后默认进入前台 `/requirements`；具备后台权限的用户可继续从前台入口进入 `/admin`。
- 个人资料弹窗可继续沿用前台 `rc-*` 与后台 `admin-*` 各自视觉体系，但保存、上传、头像读取和当前用户刷新必须调用统一 `/api/v1/auth/*` 能力。
- 修改密码成功后，前台和后台都必须表现为已退出并回到统一登录入口，不得停留在看似仍已登录的页面。
- 登录态失效、无后台权限和账号不可用状态应有清晰、可恢复的中文反馈，不得出现空白页、死循环跳转或前后台状态不一致。

## 关联需求

- REQ-0005-admin-auth-system：提供当前真实认证、服务端会话、后台权限和超级管理员初始化基础；本需求将认证路径从 `admin/auth` 统一迁移到 `/auth`。
- REQ-0010-admin-user-menu-password-change：提供自助修改密码体验与会话撤销要求；本需求将能力扩展为所有登录用户并迁移到 `/api/v1/auth/change-password`。
- REQ-0011-admin-user-menu-profile：提供后台个人资料弹窗和当前用户资料更新能力；本需求将资料更新迁移到 `/api/v1/auth/me` 并面向所有登录用户。
- REQ-0014-frontend-user-menu-profile：提供前台用户菜单个人资料能力；本需求统一其 API、头像上传和 session 存储边界。
- REQ-0012-frontend-requirement-center：提供前台需求中心和当前用户上下文；本需求要求其路由守卫和用户上下文改读统一 session。

## 状态块

```yaml
status: archived
generated_at: 2026-08-12 00:14:27
completed_at: 2026-08-12 10:04:53
reviewed_at: 2026-08-12 10:15:13
approved_at: 2026-08-12 10:15:13
source_material:
  - capture.md
  - req-explore: 后端当前实际是一套认证能力，但路径命名和前端双 session 造成边界混淆
  - req-explore: REQ-0016 应作为独立需求推进，覆盖 API 边界治理、前端 session 模型统一和破坏性迁移
  - user-confirmed: 所有登录用户都可修改自己的昵称和头像
  - user-confirmed: 头像上传纳入本次 /api/v1/auth/* 统一范围
  - req-complete: 补齐 user-stories、business-flow、acceptance；media-upload 横切 AC 引用 admin-media-upload-chain
next: /sprint-propose --req REQ-0016-unified-account-auth-api
iteration: null
```
