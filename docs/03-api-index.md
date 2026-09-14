---
purpose: API 索引
content: MoonBox REST API 模块、契约治理和客户端生成规则
created_at: 2026-07-29 22:55:00
updated_at: '2026-09-14 00:43:26'
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
| PUT | `/api/v1/requirement-center/issues/{issue_id}/documents/{document_name}` | 需 `Authorization: Bearer <access_token>`；按后端返回的 `document_entries[].capability.human_editable` 校验人工全文编辑权限，支持采集池 `capture.md`、规划中主文档、待评审/已评审完善类文档；请求体为 `{ content }`，内容长度受限；`trace.md`、当前阶段只读文档、路径越界、缺失、类型不符和权限失败均返回脱敏错误且不写入 |
| GET | `/api/v1/requirement-center/changes/{change_id}/documents/{document_name}` | 需 `Authorization: Bearer <access_token>`；读取当前 OpenSpec Change 下的 `.md` 文档，`spec.md` 会聚合 `specs/**/spec.md` 并用 source 标记分段；路径越界、缺失、类型不符和权限失败均返回脱敏错误 |
| PUT | `/api/v1/requirement-center/changes/{change_id}/documents/{document_name}` | 需 `Authorization: Bearer <access_token>`；仅当 Change 处于待开发阶段且文档为 `proposal.md`、`spec.md`、`design.md` 或 `tasks.md` 时允许人工全文保存；已生效 `openspec/specs/` 不通过该入口写入；`trace.md` 和其他阶段只读 |
| PUT | `/api/v1/requirement-center/changes/{change_id}/documents/{document_name}/tasks` | 需 `Authorization: Bearer <access_token>`；仅用于验收中 `tasks.md` 的 checkbox 勾选/取消，后端只接受 `- [ ]` 与 `- [x]` 标记变化，不允许修改标题、任务描述或其他正文 |
| GET | `/api/v1/requirement-center/issues/{issue_id}/documents/{document_name}/preview` | 需 `Authorization: Bearer <access_token>`；仅允许读取治理对象目录内的 `.html` 文档并以 HTML 预览响应返回，路径越界、缺失、类型不符和权限失败均返回脱敏错误 |

需求中心 context 接口是读聚合 BFF。治理对象数据源限定为 `project.yaml`、`issues/requirements/_registry.yaml`、`issues/bugs/_registry.yaml`、对应 issue 目录内的 Markdown/HTML 文件名与 `trace.md` frontmatter、`iterations/change/<sprint>/sprint.yaml`、`openspec/changes/<change>/tasks.md` 和 `trace.md` frontmatter。卡片响应额外返回受控 `document_entries`、`detail_url`、`archive_url`、`action`、`tasks` 与 `sprint_options`，用于前端文档抽屉、新 Tab 预览、阶段动作、tasks 进度和 Sprint 选择；`document_entries[].capability` 统一返回 `readable`、`human_editable`、`ai_mutable`、`task_toggle_only` 与 `reason`，前端据此决定 Vditor 全文编辑、只读阅读态或验收中 tasks checkbox 专用操作，兼容字段 `document_entries[].editable` 继续等同于 `human_editable`。`trace.md` 始终人工只读但允许系统治理链路更新；待开发阶段只显示并允许编辑当前 Change 下的 `proposal.md`、`spec.md`、`design.md`、`tasks.md`，不会写入已生效 `openspec/specs/`。`action.disabled_reason` 承载阶段主动作门禁：采集池 Requirement / Bug 生成动作要求 `capture.md` 与 `trace.md` 均存在且内容非空；规划中 Requirement / Bug 完善动作分别要求 `capture.md`、`trace.md`、`requirement.md` 或 `capture.md`、`trace.md`、`bug.md` 均存在且内容非空；待评审 Requirement / Bug 评审动作分别要求 `capture.md`、`trace.md`、`requirement.md`、`acceptance.md`、`business-flow.md`、`user-stories.md` 或 `capture.md`、`trace.md`、`bug.md`、`root-cause.md`、`workaround.md`、`acceptance.md` 均存在且内容非空；已评审 Requirement / Bug 加入迭代动作要求对应待评审文档包再加 `review.md` 非空。空间上下文来自后台空间事实源 `admin_spaces`、`admin_space_members` 与 `admin_space_products`：仅返回当前登录用户作为负责人或成员已加入、且未处于回收状态的空间；冻结空间保留可见并返回 `status=FROZEN` 与 `readonly=true`。空间响应只输出 `workspace_id`、`name`、`slug`、`description`、`member_count`、`role`、`status`、`readonly` 等前台白名单字段，不返回后台配额、审计、删除原因、负责人内部详情或高风险动作。Docker 环境通过 `MOONBOX_GOVERNANCE_ROOT=/app/governance` 读取治理事实源。响应不返回本机绝对路径、系统用户名、Markdown 全文、`.env`、token、日志或堆栈；Markdown/HTML 全文只通过受控文档接口按单文件读取；人工保存只通过受控写入接口并由后端按阶段、文档名、路径类别和勾选专用规则二次校验；未登录返回 401，数据源不可读时返回脱敏 503。前端生产运行时不得再使用页面内静态 `initialIssues`、`workspaces` 或 `currentUser` 替代该接口。

API 变更必须同步 OpenAPI、Orval 客户端、测试、`docs/03-api-index.md` 和相关 OpenSpec Change。


## Chat后端首批接口（REQ-0025）

路由前缀/api/v1/chat，使用现有Bearer认证。capabilities按空间返回execution_ready=false和授权仓库标识；conversations支持GET/POST以及单条GET/PATCH/DELETE；轮次支持会话下GET/POST、单轮GET、interrupt、events和diff。列表按本人和有效空间成员过滤，无跨用户管理员豁免。事件接口是鉴权SSE有限游标页，客户端按after续取，每次重新授权，不在URL放Token。

错误码2501空间无权、2502对象不可见、2503仓库不可用、2504冲突、2505执行未就绪、2506状态未知、2507清理未验证、2508额度/并发/容量不足（内部入队服务，HTTP发送入口尚未开放）。发送当前固定拒绝新执行；同幂等键已有轮次可返回原记录，不同输入拒绝。关联、重试和包含轮次的会话清理仍待实现。禁止将本批接口作为完整Chat交付。

OpenAPI来源src/backend/app/main.py，生成物src/web/openapi.json；Orval 8.29.0及src/web/orval.config.ts按Chat标签生成src/web/src/api/generated/chat.ts。生成工具为devDependency，未替换既有手写客户端。

Chat新增GET /api/v1/chat/spaces返回本人可用空间ID/名称，逐个重验有效期；GET /conversations/{id}/messages按页返回已持久化本人消息。Web会话管理已使用Bearer接口；事件使用鉴权fetch读取有限SSE页并按游标续读，失败停止重连并显示错误，重试由用户触发。历史轮次选择不改变停止按钮的当前运行目标。


Diff响应已登记DiffRead：available、reason、before_hash、after_hash、initial_hash、files与cumulative_files。未有可信快照时保持available=false；大文本/二进制/链接可返回元数据与不可展示原因，原样重命名包含previous_path；修改内容的重命名保守展示新增/删除对。事件新增execution.usage和execution.tool，保存用量数值及白名单工具类型、原标识/阶段。2026-09-11起 execution.tool 的既有payload可附加detail_version、tool_name、arguments、result、exit_code、status、recorded_at_ms、duration_ms、timing_source与truncated；工具参数和输出经过脱敏及限长，不保存完整原始协议、配置或RPC错误。OpenAPI及Orval已同步。

Chat 关联接口：GET conversations/{id}/objects（授权候选搜索）、GET/PUT conversations/{id}/relations（一个主对象、最多10个引用）、GET turns/{id}/context（本轮不可变快照），均位于 /api/v1/chat 下。2509 表示对象目录不可用或对象授权失败；对象目录路径从不接受客户端参数或返回客户端。

Chat 增量接口：POST turns/{id}/retries（仅确认失败/停止、幂等身份、原始授权快照）；GET conversations/{id}/deletion-check；DELETE conversations/{id}?expected_hash=确认的工作区hash；GET conversations/{id}/cleanup。列表filter支持all/pinned；未传时沿用archived筛选。Web请求带X-Chat-Client:web标记用于稳定行为归因，不是认证依据；服务端独立生成X-Request-ID，忽略客户端伪造的可信链路ID。发送/重试仍返回2505，直至平台隔离和额度配置完成。


Chat隔离验收入口更新（2026-09-08）：capabilities在显式本机测试配置、指定登录账号/空间和活跃worker下返回execution_ready=true；发送与重试经同一门禁调用已有事务入队，正常部署仍503。真实登录/所有者/空间/对象鉴权不变，浏览器不能提供执行目录。发送/重试将服务端X-Request-ID关联到Task Trace。响应字段与OpenAPI比较无变化，无新增端点或客户端生成差异。用量结算receipt为内部事件事实，不开放任意计费值写入接口。


### 执行进程计量范围补充（2026-09-09）

Chat会话/关联/发送/重试/停止/事件/Diff接口实现与权限、幂等及状态回归完成。路径和OpenAPI schema与现有生成客户端一致，本批不需要Orval再生成。计量修复只改变内部可信receipt范围；旧不明确用量仍通过既有usage_unavailable状态展示，正式发送门禁继续关闭。


### 单机常驻方案确认（2026-09-09）

用户已明确采用单机 Docker Compose、SQLite、本地独立备份、本机 Codex 认证单文件，取消用户/空间额度、并发和存储运营上限。显式 unlimited 与缺失配置区分，仍计量结算；同会话互斥、权限、未知态和单轮结果处理技术边界保留。历史及备份不自动过期；主动删除仍记录和跟踪主存储/执行线程/备份，副本无固定删除截止时间，旧备份物理移除前保持待清理。单机控制器顺序处理持久队列，容量不足不绕过隔离。正式仓库路径及空间映射尚待提供，当前不宣称正式服务已开放。方案细节以 docs/02-deployment.md 的单机常驻章节为准，替代此前“认证、限额和期限尚未决定”的当前态描述；历史证据保留。

## 本地项目治理接口（REQ-0022）

需求中心所有数据/文档/HTML预览请求新增必填space_id、repository_id；缺失返回422，未授权返回403，目录或稳定快照不可用返回503，不回退到全局目录。`GET /api/v1/requirement-center/projects` 返回授权项目连接状态、账号与空间目录，不含本机路径；Chat账号目录应使用此接口。

上下文新增repository_id、snapshot_revision、sync_status；Markdown读取新增version。三个原PUT保存入口新增expected_version和idempotency_key，返回202及操作ID/state，客户端需查询操作结果后重新读取文档；未应用前不得显示已保存。冻结空间可读不可写，撤权后不可访问。此契约需与Web同批升级。

| 路由 | 方法 | 结果 |
|---|---|---|
| /api/v1/chat/governance-preparations | POST | req-generate准备ID、新个人会话、完整对象ID和待发送建议；不会发送 |
| /api/v1/chat/conversations/{cid}/governance-candidates | GET | 固定版本、完整文件差异、不可应用原因 |
| /api/v1/chat/governance-candidates/{candidate_id}/applications | POST | 校验manifest/revision/幂等键/维护窗口确认，202入队 |
| /api/v1/chat/governance-applications/{operation_id} | GET | pending/applying/recovering/applied/conflict/failed/recovery_blocked |

错误码2601项目/对象权限、2602绑定不可用、2603快照不可用、2604成果非法、2605写入未就绪、2606内容/幂等冲突。接口复用ChatRoute统一响应、可信request_id和脱敏请求日志；轮询GET不生成用户行为。新Web业务动作使用X-Chat-Client=web关联固定governance.prepare/apply/document_save事件；直接API不伪造行为。准备/应用/恢复使用governance_application类型Task Trace，摘要不保存正文或绝对路径。


## Chat 创建请求幂等补充

POST /api/v1/chat/conversations 新增可选 client_request_id（1–64位字母数字、下划线或短横线）。同一用户重放返回同一授权会话，不传保留原创建行为。同标识不同空间/仓库返回2504冲突；失权或删除按原403/404返回。幂等键不替代认证、空间或对象授权；轮次请求继续使用自己的client_request_id。


需求中心聚合返修（REQ-0022）：对象清单按registry；终态Issue保持已完成，关联Change/Sprint支持归档定位。卡片展示文档与验收文件检查分离；历史漂移不等同已完成事项的当前阻塞。路由、响应schema与权限不变，无需重新生成OpenAPI/Orval。

需求中心卡片trace入口：document_entries中trace.md仅一个，label为trace.md、URL始终为所属Issue文档路由；不存在时不回退Change文档。既有Change文档API与内部阶段计算保留；schema、权限不变，无需OpenAPI/Orval再生成。


关联 Sprint 文档读取：现有 `/api/v1/requirement-center/issues/{issue_id}/documents/sprint.md` 在授权项目快照内解析 Issue 关联 Sprint，校验其成员关系，读取活动目录或同 ID 归档目录。活动目录存在但文档缺失时不读归档旧副本；缺失返回404，不回退Issue文件。卡片只读能力与聚合缺失校验共用关联解析。请求和响应schema不变。


卡片主文档：聚合始终优先返回真实存在的所属REQ requirement.md或BUG bug.md，关联Change后仍保留；按Issue文档路由读取，权限矩阵与API schema不变。


### 文档读取与刷新性能

单次Change文档请求复用同一授权稳定快照的临时目录，避免授权和正文读取重复物化；不引入跨请求缓存，保留项目授权、写入恢复、epoch及绑定版本检查。相同项目的context刷新复用进行中请求，初始加载完成后开始轮询；切换项目及卸载取消旧请求。文档内容/草稿/版本冲突处理与原型布局不变。分段日志仅含服务端request_id、操作名、成功状态及各阶段毫秒耗时，不含文档内容或本机路径。

## Capture 持久化创建（BUG-0014）

`POST /api/v1/requirement-center/captures?space_id=...&repository_id=...` 采用登录会话与项目写授权。请求为type（requirement/bug）、title（去首尾空格后1至60字）、description（最多200字）、按type选择的priority（REQ：P0/P1/P2/P3）或severity（BUG：blocker/critical/high/medium/low，必填且不能混用）、owner（产品团队/研发团队/设计团队/未分配）、source（explore/user-feedback/internal/incident）、idempotency_key（1至64位字母、数字、下划线或短横线）；禁止额外字段及客户端路径。

返回202只表示操作入队。轮询既有governance-applications接口，终态applied附完整object_id；随后重新读取context，卡片继续展示短编号，detail_url和文档地址保留完整ID。conflict为未完成写入的确定拒绝，修改写入条件后可新建请求；recovery_blocked需管理员处理，不能当作成功。超时结果未知时复用同一幂等键，相同actor/项目/键但请求摘要不同返回409。

Web创建记录governance.capture行为，properties仅含operation_id，parent_request_id与chat_request_logs和governance_application Task Trace关联；直接API只留请求/任务记录，不生成页面行为。沿用422校验、403权限、503未连接或维护未就绪和统一脱敏错误。OpenAPI与Orval同步生成；没有新增客户端依赖。


### 卡片更新时间格式

所有阶段REQ/BUG卡片统一显示“更新 YY/MM/DD HH:mm”，保留真实日期及源时间时分，各字段补零；缺失、无效或仅有日期/时分时显示“更新时间未知”，不补造日期和时间。footer必要时换行，时间自身不拆分，避免窄屏挤压动作。


### Capture 就绪查询

GET `/api/v1/requirement-center/capture-readiness`沿用space_id/repository_id及登录授权，返回ready、reason和mode（continuous/maintenance/unavailable）。只读项目返回ready=false；未连接或无访问权限仍按项目授权拒绝。原因脱敏，不返回私有目录、绑定正文或凭证。GET不产生行为事件；实际POST再次检查写入门禁，不能信任前端ready。OpenAPI与Orval同步。

## 需求中心研发阶段判定

BUG-0015：context沿用既有stage/tasks/snapshot_revision字段。版本化Change执行事实启动后，即使0/N也返回development；任务全勾选后，完成事件写入才进入acceptance。CLI与API共用app.governance.lifecycle；响应结构不变，无需OpenAPI/Orval重生成。


### 所属需求原型常驻入口

所属REQ的prototype.html及prototype目录内HTML存在时，在主文档后常驻展示；多端以相对路径区分，兼容活动/归档目录。发现与读取共用安全解析，缺失无占位、不回退其他Issue/Change、不扩大必需文档校验。维持项目授权、只读预览和4px紧凑分组。

## REQ-0026 Change 卡片读取契约

需求中心context保留原Issue身份，新增current_change、related_changes（id/title/stage/source_kind/task_progress/document_entries/warnings）与change_warning，stats新增standalone_changes。独立对象type=change，id为完整Change ID，priority可为空；没有当前项时current_change=null。完整快照先识别关联再授权，关联Change要求全部来源Issue可读，独立Change复用其自身object_access。

GET /api/v1/requirement-center/changes/{change_id}/documents/{document_name}支持独立只读对象；sprint.md须核对iteration及Sprint changes成员关系。活动文档不回退归档，归档不唯一或缺文档返回404，无权限返回403。新增来源读取不扩大原PUT/tasks写入范围；独立Change写入拒绝。全部路径继续要求space_id/repository_id，响应遵循现有ApiResponse/request_id。

OpenAPI来源app.main.app.openapi，已重新生成src/web/openapi.json及Orval governance客户端。GET复用现有请求日志，服务器生成request_id、忽略伪造ID与非法客户端标记，不记录文档正文；采集失败不影响读取。无新增DB、部署、对象存储或异步Task Trace。回归与真实观察见REQ-0026关联Change verification.md。

## 需求中心读取失败分类（BUG-0016）

HTTP 503 / code 2603 保持兼容；稳定读取失败可附带 `data.kind`（`source_invalid` 格式不可解析、`source_changing` 读取期间变化、`source_unavailable` 无法安全读取）及 `data.request_id`，与响应头 `X-Request-ID` 一致。其他旧错误仍可返回 `data: null`；客户端缺少分类时仅显示通用失败，不推断 YAML 根因。错误详情不含项目路径、文件行、正文或解析器原始异常。读取缓存仅复用已校验完整内容树，不缓存授权结论；每次请求保留内容扫描和数据库围栏，响应仍为 `Cache-Control: no-store`。无数据库迁移或新行为事件。

读取响应新增标准 `Server-Timing` 头，固定指标snapshot_and_fences、materialize、object_authorization、parse、cleanup、total（毫秒），沿用X-Request-ID关联；仅数值，无路径或正文。用于真实部署浏览器与后端分段耗时对照，不写入新DB字段。


原型入口标签仅显示区分多端所需相对路径（如web/prototype.html、admin/prototype.html），移除“原型 · ”前缀；常驻位置、排序、URL与预览权限不变。

## REQ-0026 独立 Change 的 Sprint 归属修正

context 既有 sprint_id 字段采用以下解析，不增加响应字段：独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

## REQ-0026 阶段按钮能力

独立Change复用action结构：ready-dev开始开发、development查看进度、acceptance完成/归档；done/unknown无action。写动作返回disabled_reason，未接入真实执行服务不可执行；冻结空间增加只读原因，缺唯一Sprint或验收证据提示核对。读取进度仍受对象授权。无schema或客户端生成变化。

## 固定禁用提示返修结论

本节替代上一轮独立Change一律禁用的结论。后端复用REQ/BUG阶段必需文档与非空门禁，并核对唯一Sprint；缺失/空文档/只读才返回相应原因，不再固定生成测试核对或能力未接入提示。文档存在不代表测试执行通过；前端复用已有testProgress/manualAcceptanceCount判断，数据不存在不伪造检查结论。

独立Change与REQ/BUG进入同一动作处理器：研发中读取tasks；真实模式中当前未支持的开发/归档动作点击后显示现有统一能力提示，不执行写入；Demo沿用现有弹窗和模拟流转，不接入真实执行。取消、提交防重入和刷新行为复用当前组件，未新增服务或权限。

验证：后端94项、前端79项、TypeScript通过；1440/390深浅主题4组真实组件合成API浏览器验收通过，截图和computed style位于evidence/action-gates/。非部署观察，未执行真实开发/归档。保留现有权限和真实能力限制；新证据替代旧固定禁用截图。

## 独立交付验收来源返修（当前结论）

验收中不再固定要求acceptance.md：优先校验trace.acceptance_refs声明的Change内相对Markdown路径；显式引用无效、缺失或为空返回具体待核实原因，不回退。未声明时查现有acceptance.md、verification.md，再识别trace中非空“验证记录/验收记录/验证结果/验收结果”章节。不得跨Change或通过绝对路径、父路径、符号链接越界读取。没有证据来源提示待核实，不补建文件；本机制定位证据，不自动判断验收通过，applied和tasks全勾均不代替验收。

真实仓库样本standardize-sprint-default-capacity以trace验证记录作为来源；unify-issue-classification-metadata使用acceptance.md，两者当前源码均无来源阻塞。后端95项回归通过，包含显式引用、缺失、空源、越界与历史trace来源；浏览器复用真实组件+合成API在1440/390深浅主题验收，证据evidence/action-gates，非部署验收。

运行页面核对：用户地址localhost:18102对应moonbox-web，加载index-y8JI4bjc.js，其中无旧能力提示；moonbox-backend镜像动作函数也无旧提示，但仍采用上一版固定acceptance.md清单，尚未部署本次解析。未对运行容器做重建或重启，截图旧提示的实际响应来源仍未取得，不断言缓存根因。

REQ主文档、故事、流程、验收、trace、原型context及HTML已核对同步；capture/review保留历史，不需改写。API既有action字段形状不变，无需OpenAPI/Orval生成；product_data_collection_observability为applicable，affected_layers为api，复用请求日志/授权，验证无越界；无新增DB、部署配置、存储、保留周期或Task Trace。
