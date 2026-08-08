## 背景

REQ-0004 已评审通过，需求包位于 `issues/requirements/review/REQ-0004-admin-user-management/`。本 Change 只创建 OpenSpec 工件，不实现源码；实现阶段由 `/opsx-apply` 或 Sprint 队列执行。

当前 OpenSpec 中没有管理后台用户管理规格，因此本次作为新增 capability `web-admin-user-management`。需求包含 Web 管理后台、REST API、数据库、对象存储、权限和审计影响。

## 目标与非目标

**目标：**

- 建立管理后台用户管理系统的规格事实源。
- 约束用户列表、筛选、分页、创建、编辑、冻结、解冻、逻辑删除、重置密码和超级管理员保护。
- 约束头像上传状态机、同会话即时回显和 Docker `:3000` 边界验收。
- 将 REQ-0004 的 knowledge-base 横切 AC 纳入 Change 设计和任务。

**非目标：**

- 不实现用户自主注册、忘记密码、邮箱验证、短信验证、企业 SSO 或组织目录同步。
- 不实现自定义平台角色、细粒度权限矩阵或平台管理员授权体系扩展。
- 不实现 Workspace 停用/恢复/所有者转让、授权配额、独立审计日志页面或平台管理员页面。
- 不新增移动端、小程序或桌面端能力。

## 设计决策

### D1. UI 策略：CSS Port + 设计系统约束

采用 CSS Port 策略：以 `prototype/web/prototype.html` 和 `prototype/web/prototype.png` 为布局、信息密度和交互基准，同时落到 MoonBox 现有 UI 规则中。

理由：
- HTML 原型优先级高于 PNG、context、acceptance、ui-design 和现有 specs。
- 原型已经覆盖用户管理导航、筛选栏、表格、分页、超级管理员保护和新增/编辑弹窗。
- MoonBox UI 要求深浅主题、金色强调、近直角、细线、衬线标题和克制后台密度，不能直接引入通用 SaaS 蓝白风格。

### D2. 原型冲突消解

Conflict Resolution：

| 来源 | 决策 |
|---|---|
| HTML 原型 | 作为页面结构、DOM 行为、筛选区、分页、弹窗和超级管理员行的最高优先级参考。 |
| PNG 截图 | 用于视觉密度、深色主题和 1440px 桌面布局验收。 |
| prototype context | 用于字段、接口预期、组件规范和数据注意事项。 |
| acceptance.md | 作为可测试验收清单，若与 HTML 文案轻微不一致，以 acceptance 的用户决策为准。 |
| ui-design.md | 作为 MoonBox 视觉风格边界，约束颜色、字体、圆角和主题。 |

用户已确认：
- 角色范围仅保留“后台管理员”和“前台用户”。
- 冻结后会话失效时限为 10 秒内。

### D3. 数据与接口边界

用户管理需要服务端权限校验和审计事实源。前端权限只控制可见性，服务端必须重新鉴权；系统内置唯一超级管理员必须由服务端保护，不能只依赖前端隐藏按钮。

用户列表、搜索、角色/状态筛选和分页必须以后台用户 API 返回的真实分页数据为准。前端不得保留演示用用户数组作为运行时数据源；创建、编辑、冻结、解冻、逻辑删除和重置密码成功后刷新真实列表，并使用后台返回的 `total` 驱动分页总数。逻辑删除用户默认不进入列表和“全部状态”结果；前端状态筛选只提供“全部状态”、“待激活”、“正常”和“已冻结”，不提供“已删除”筛选项；后端 `total` 必须按同一筛选规则计算。

创建用户和重置密码必须生成一次性临时密码，并使用现有后台认证哈希算法写入 `admin_users.password_hash`。临时密码仅随当前 API 响应返回并由前端即时展示，不得进入审计前后值、日志、埋点或前端持久化存储；重置密码后必须撤销目标用户现有会话。前端应使用 `TemporaryPasswordModal` 展示一次性密码，包含用户名、密码、复制按钮、安全提示和“关闭”按钮；复制成功只反馈复制状态，不把密码写入 toast。

头像上传属于对象存储/静态访问链路，必须覆盖上传状态机、同会话即时回显和 Docker `:3000` MinIO 对象访问验收。`self-storage-sqlite` 本地环境也必须写入 Compose MinIO 的单 Bucket `images/avatars/{uuid}.{ext}` 前缀，并通过后台授权读取接口代理回显。

### D4. Knowledge-base 引用

`design.md` 与实现任务必须引用以下知识库治理项：

- `docs/knowledge-base/best-practices/admin-list-page-consistency.md`
- `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`
- `docs/knowledge-base/best-practices/admin-media-upload-chain.md`

这些引用用于避免列表分页 DOM、fixed toast、DS confirm、弹窗宽度 CSS 级联、低视口滚动、上传状态机和 Docker 文件访问问题复发。

## 风险与权衡

- [Risk] 仅前端隐藏超级管理员操作入口可能被绕过 → 服务端对唯一超级管理员写操作必须返回拒绝，并进入测试。
- [Risk] 冻结后 10 秒会话失效涉及 token/session 缓存 → 实现时需要统一会话失效策略和集成测试。
- [Risk] 头像上传跨容器和浏览器访问路径不一致 → Docker `:3000` 验收必须覆盖 MinIO 写入、授权读取和回显。
- [Risk] 弹窗样式被通用 modal 类覆盖 → 实现需检查 computed width 和低视口滚动。

## 迁移计划

1. 增加后端数据模型、接口、鉴权、审计和上传链路。
2. 增加 Web 管理后台页面、弹窗、表格、状态操作和头像回显。
3. 增加后端、API、前端和 Docker 本地文件访问验证。
4. 通过验收后归档 Change，并同步 `openspec/specs/web-admin-user-management/spec.md`。

## 待确认问题

- 无阻断问题。实现阶段可根据现有认证和对象存储模块选择最小改动路径。
