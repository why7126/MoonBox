---
purpose: API 索引
content: MoonBox REST API 模块、契约治理和客户端生成规则
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-18 13:04:39
owner: MoonBox 产品团队
---

# API 索引

MoonBox API 采用 REST 风格，由 FastAPI 暴露 OpenAPI 契约，前端通过 Orval 生成客户端。

| 模块 | 说明 | 状态 |
|---|---|---|
| Health | 健康检查 | planned |
| Admin Auth | 管理后台登录、退出、当前管理员和服务端会话 | done |
| Admin Users | 管理后台用户列表、创建、编辑、冻结/解冻、逻辑删除、重置密码和头像上传 | in_progress |
| Admin Spaces | 管理后台空间列表、申请审批、生命周期、配额和回收站 | in_progress |
| Requirement Center | 前台需求中心真实数据聚合、筛选、统计和权限态 | in_progress |
| Catalog Workspace Creation | 前台创建空间 | in_progress |
| Workspace | 组织空间和项目空间 | planned |
| Agent Workflow | 流程节点、状态流转、审批和执行记录 | planned |
| Knowledge Graph | 需求、设计、代码、测试、决策和经验关联 | planned |
| Assets | 文档与图片上传、签名 URL、元数据 | planned |

## 管理后台认证 API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/auth/login` | 统一账号密码登录；正常或待激活用户可登录，待激活用户首次登录成功后自动激活为正常，并返回 access token、过期时间和用户摘要；登录成功默认进入前台，是否可进入后台由服务端后台接口二次判权 |
| POST | `/api/v1/auth/logout` | 退出登录，撤销当前服务端会话 |
| GET | `/api/v1/auth/me` | 读取当前登录用户摘要，面向所有已登录用户，不要求后台管理员角色 |
| PATCH | `/api/v1/auth/me` | 当前登录用户更新自己的个人资料；仅允许更新 `nickname` 与 `avatar_url`，目标用户由服务端登录态决定，成功后返回最新当前用户摘要 |
| POST | `/api/v1/auth/change-password` | 当前登录用户自助修改密码；需 `Authorization: Bearer <access_token>`，请求包含当前密码、新密码和确认新密码，成功后撤销该用户所有服务端会话并要求重新登录 |

管理后台受保护接口使用 `Authorization: Bearer <access_token>`。access token 必须对应服务端会话记录，且会话未过期、未撤销、账号状态为“正常”。除登录和登出外，管理后台接口还必须要求当前用户角色为“后台管理员”；普通前台用户可以持统一登录态访问前台接口，但不得进入管理后台。待激活用户仅可在登录接口中完成首次登录激活，已冻结和已删除用户不得创建有效会话。当前用户资料更新接口不得接受请求体指定目标用户 ID、角色、状态、用户名、密码等字段；昵称非必填、最长 128 字符，头像 URL 必须为后端返回或系统可访问的持久 URL，不得保存 `blob:`。修改密码接口在当前密码错误、会话失效或账号不可用时返回 401，在新密码与当前密码相同、确认密码不一致或不符合密码规则时返回 400；响应不得返回新密码、密码哈希或任何可复用凭证。

统一头像 API 迁移后，历史用户记录中若仍保存 `/api/v1/admin/users/avatar/{filename}`，服务端返回登录用户摘要、当前用户摘要或用户列表摘要时应规范化为 `/api/v1/auth/avatar/{filename}`；旧 `/api/v1/admin/users/avatar/*` 读取接口不作为兼容路由保留。

## 管理后台用户 API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/admin/users` | 用户列表、关键词、角色、状态和分页查询；默认和“全部状态”不返回 `status=已删除`，已冻结用户返回 `status_before_freeze` 用于展示解冻恢复目标，`total` 按同规则计算 |
| POST | `/api/v1/admin/users` | 创建后台用户，用户名全局唯一且创建后不可修改；新用户状态为待激活，系统生成一次性临时密码并写入 `password_hash`，响应仅展示一次 |
| PUT | `/api/v1/admin/users/{user_id}` | 编辑头像、昵称和角色 |
| POST | `/api/v1/admin/users/{user_id}/freeze` | 冻结待激活或正常用户，记录 `status_before_freeze`，10 秒内使有效会话失效；重复冻结不得覆盖冻结前状态；当前登录用户冻结自己时返回 403 且不修改状态或撤销当前会话 |
| POST | `/api/v1/admin/users/{user_id}/unfreeze` | 解冻用户并恢复冻结前状态，待激活恢复待激活，正常恢复正常；缺少冻结前状态时返回受控错误 |
| DELETE | `/api/v1/admin/users/{user_id}` | 逻辑删除用户并保留审计；当前登录用户删除自己时返回 403 且不修改状态、不设置 `deleted_at` 或撤销当前会话 |
| POST | `/api/v1/admin/users/{user_id}/reset-password` | 重置密码，将新临时密码写入 `password_hash` 并撤销该用户会话，临时结果仅响应一次 |
| POST | `/api/v1/auth/avatar` | 当前登录用户上传头像到 MinIO `images/avatars/` 前缀，返回同会话可回显 URL |
| GET | `/api/v1/auth/avatar/{filename}` | 当前登录用户授权读取 MinIO 头像对象 |

管理端接口必须使用统一登录态叠加后台角色授权鉴权。`x-admin-role: admin` 仅为历史占位，不得作为正式权限来源。创建用户和重置密码返回的 `temporary_password` 属于一次性敏感结果，只允许响应给当前后台管理员，不得写入日志、埋点或前端持久化存储。临时密码可用于正常或待激活用户登录；前台用户登录后仅获得前台访问能力，不表示其可访问管理后台。

## 管理后台空间 API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/admin/spaces` | 空间列表，支持关键词、状态、来源、用量状态和分页；默认不返回回收站空间；空间对象返回负责人名称、角色和头像 URL |
| POST | `/api/v1/admin/spaces` | 后台创建空间，同步创建一空间一产品绑定，空间编码全局唯一 |
| GET | `/api/v1/admin/spaces/{space_id}` | 空间详情，返回负责人名称、角色、头像 URL、产品绑定、配额、有效期、状态和 `allowed_actions` |
| PUT | `/api/v1/admin/spaces/{space_id}` | 编辑空间基础信息和有效期；回收站空间不可编辑 |
| POST | `/api/v1/admin/spaces/{space_id}/freeze` | 冻结正常空间，必须填写原因并写入审计 |
| POST | `/api/v1/admin/spaces/{space_id}/restore` | 恢复冻结或回收站空间，清理冻结/删除字段 |
| POST | `/api/v1/admin/spaces/{space_id}/quota` | 调整成员、存储和 AI token 配额，必须填写原因 |
| POST | `/api/v1/admin/spaces/{space_id}/renew` | 修改有效期类型和到期时间；支持 `fixed_date` 与 `long_term` |
| POST | `/api/v1/admin/spaces/{space_id}/transfer-owner` | 转移空间负责人，目标用户必须存在且未删除 |
| GET | `/api/v1/admin/spaces/{space_id}/members` | 查询空间成员列表；负责人不在成员列表中返回；按管理员、编辑者、查看者排序，同角色按加入时间倒序 |
| POST | `/api/v1/admin/spaces/{space_id}/members` | 添加空间成员；候选用户必须为用户管理中状态正常用户，且不能是负责人或既有成员；角色限定为管理员、编辑者、查看者 |
| PUT | `/api/v1/admin/spaces/{space_id}/members/{member_id}` | 编辑空间成员角色；角色限定为管理员、编辑者、查看者，不通过成员接口产生负责人 |
| DELETE | `/api/v1/admin/spaces/{space_id}/members/{member_id}` | 移除空间成员，必须填写原因；负责人不可通过成员接口移除 |
| DELETE | `/api/v1/admin/spaces/{space_id}` | 将空间移入回收站，设置删除时间、删除人、原因和 30 天清理时间 |
| DELETE | `/api/v1/admin/spaces/{space_id}/purge` | 彻底删除回收站空间，仅系统超级管理员可执行 |
| GET | `/api/v1/admin/spaces/{space_id}/audit-events` | 查询空间审计日志，不返回 token、会话 ID 明文或敏感凭证 |
| GET | `/api/v1/admin/space-applications` | 查询空间申请，支持关键词、状态和分页；默认返回待审批 |
| POST | `/api/v1/admin/space-applications` | 创建空间申请 |
| POST | `/api/v1/admin/space-applications/{application_id}/approve` | 审批通过空间申请，并自动创建申请审批来源的空间 |
| POST | `/api/v1/admin/space-applications/{application_id}/reject` | 拒绝空间申请；重复审批返回受控错误 |

空间管理接口统一使用 `Authorization: Bearer <access_token>` 叠加后台管理员角色判权。服务端返回 `allowed_actions` 作为前端操作可用性的事实源；受保护空间不得冻结、回收或彻底删除，非系统超级管理员不得彻底删除。删除空间前服务层保留运行中任务阻塞检查入口，当前基线无 Agent 运行表时返回无阻塞。高风险操作必须提交原因，审计日志仅记录业务状态摘要和原因，不记录 token、会话 ID、密码、临时凭证或对象存储签名。成员数量口径为负责人加普通成员；负责人不进入成员列表，负责人变更必须使用负责人移交接口。后台空间申请审批能力作为管理后台兼容能力保留，不由前台创建空间入口触发。

## 前台创建空间 API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/catalog/workspace-applications/create` | 当前登录用户提交创建空间申请；服务端以当前用户作为申请人和拟负责人，按后台空间管理一致规则校验名称、标识、成员上限、存储空间、AI Tokens 和到期时间，成功后返回待审批申请 |

前台创建空间 API 使用统一登录态，不要求后台管理员角色。首版不提供加入空间、邀请码、公开目录、推荐空间、精准搜索空间、我的申请、撤回或重新提交能力。成员上限、存储空间、AI Tokens 和到期时间的输入限制与后台空间管理保持一致；存储空间单位为 GB，AI Tokens 输入框不额外展示 `Tokens` 单位；有效期为长期有效时不提交到期时间，固定日期必须晚于当前时间。审批通过前不会创建正式空间或返回进入 URL。

## 前台需求中心 API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/requirement-center/context` | 需 `Authorization: Bearer <access_token>`；接受统一登录态，不要求后台管理员角色；聚合 REQ、BUG、Sprint、OpenSpec Change、空间与用户权限，返回需求中心看板卡片、9 阶段映射、统计、漂移提示、空间列表、当前空间和当前用户摘要；`current_user.avatar_url` 返回当前用户头像地址，前端需继续用同一 Bearer token 读取受保护头像资源 |
| GET | `/api/v1/requirement-center/issues/{issue_id}/documents/{document_name}` | 需 `Authorization: Bearer <access_token>`；仅允许读取治理对象目录内的 `.md` 文档，返回 `name` 与 `content`，路径越界、缺失、类型不符和权限失败均返回脱敏错误 |
| PUT | `/api/v1/requirement-center/issues/{issue_id}/documents/{document_name}` | 需 `Authorization: Bearer <access_token>`；仅允许保存采集池阶段对象的 `capture.md`，请求体为 `{ content }`，内容长度受限；`trace.md`、非采集池阶段 Markdown、路径越界、缺失、类型不符和权限失败均返回脱敏错误且不写入 |
| GET | `/api/v1/requirement-center/issues/{issue_id}/documents/{document_name}/preview` | 需 `Authorization: Bearer <access_token>`；仅允许读取治理对象目录内的 `.html` 文档并以 HTML 预览响应返回，路径越界、缺失、类型不符和权限失败均返回脱敏错误 |

需求中心 context 接口是读聚合 BFF。治理对象数据源限定为 `project.yaml`、`issues/requirements/_registry.yaml`、`issues/bugs/_registry.yaml`、对应 issue 目录内的 Markdown/HTML 文件名与 `trace.md` frontmatter、`iterations/change/<sprint>/sprint.yaml`、`openspec/changes/<change>/tasks.md` 和 `trace.md` frontmatter。卡片响应额外返回受控 `document_entries`、`detail_url`、`archive_url`、`action`、`tasks` 与 `sprint_options`，用于前端文档抽屉、新 Tab 预览、阶段动作、只读 tasks 进度和 Sprint 选择；`document_entries[].editable` 仅对采集池 `capture.md` 为 true。空间上下文来自后台空间事实源 `admin_spaces`、`admin_space_members` 与 `admin_space_products`：仅返回当前登录用户作为负责人或成员已加入、且未处于回收状态的空间；冻结空间保留可见并返回 `status=FROZEN` 与 `readonly=true`。空间响应只输出 `workspace_id`、`name`、`slug`、`description`、`member_count`、`role`、`status`、`readonly` 等前台白名单字段，不返回后台配额、审计、删除原因、负责人内部详情或高风险动作。Docker 环境通过 `MOONBOX_GOVERNANCE_ROOT=/app/governance` 读取治理事实源。响应不返回本机绝对路径、系统用户名、Markdown 全文、`.env`、token、日志或堆栈；Markdown/HTML 全文只通过受控文档接口按单文件读取；`capture.md` 保存只通过受控写入接口并限制在采集池阶段；未登录返回 401，数据源不可读时返回脱敏 503。前端生产运行时不得再使用页面内静态 `initialIssues`、`workspaces` 或 `currentUser` 替代该接口。

API 变更必须同步 OpenAPI、Orval 客户端、测试、`docs/03-api-index.md` 和相关 OpenSpec Change。
