---
note: workflow-sync — workflow-sync 自动同步 — 17/17 Change archived；0 applied；Sprint `completed`
sprint_id: sprint-001
status: completed
lifecycle_stage: archive
created_at: 2026-07-30 08:51:51
updated_at: 2026-08-08 23:38:25
---

# Sprint-001 官网、登录页、数据库兼容与用户管理迭代

## Sprint 目标

将已评审通过的 `REQ-0001-homepage`、`REQ-0002-login-page`、`REQ-0003-database-compatibility`、`REQ-0004-admin-user-management`、`REQ-0005-admin-auth-system`、`REQ-0006-admin-crud-list-template` 与 `REQ-0007-admin-user-first-login-activation` 纳入正式迭代范围，完成 MoonBox 官网首页品牌视觉、Web 登录页前端体验、开发 SQLite/生产 MySQL 的数据库兼容治理基础能力、管理后台用户账号生命周期治理能力、管理后台真实登录认证边界、后台 CRUD 列表页模板与组件化复用能力，以及待激活首次登录自动激活和解冻恢复冻结前状态规则。

正式范围：

- `REQ-0001-homepage`
- `REQ-0002-login-page`
- `REQ-0003-database-compatibility`
- `REQ-0004-admin-user-management`
- `REQ-0005-admin-auth-system`
- `REQ-0006-admin-crud-list-template`
- `REQ-0007-admin-user-first-login-activation`
- `add-homepage-brand-visual`
- `add-login-page`
- `add-database-compatibility`
- `add-admin-user-management`

### REQ-0001-homepage 要点

- 首页左上角使用 `Logo1-20260728001940.png`。
- 首页首屏右侧使用 `image.png` 产品视觉。
- 保留首屏左侧文案、两个 CTA 和三项能力摘要。
- 首页两个 CTA 进入登录页入口；首页本身不实现登录表单细节。

### REQ-0002-login-page 要点

- 登录页通过 `#login` 或等价前端状态展示。
- 登录页左上角提供返回首页入口，并清除登录页状态。
- 登录卡片展示 MoonBox Logo，背景复用首页产品视觉并叠加深色遮罩。
- 表单包含用户名、密码、记住我和登录按钮；用户名和密码必填。
- 本 Sprint 不实现真实鉴权接口、Token、会话管理或登录后工作台跳转。

### REQ-0003-database-compatibility 要点

- 开发环境保持 SQLite 快速启动体验。
- 生产环境必须显式使用 MySQL，禁止静默回退到 SQLite。
- 审计 ORM、Repository、schema 与迁移中的 SQLite/MySQL 差异。
- 建立 MySQL 可复现测试路径，覆盖连接、迁移、基础 CRUD、约束和事务。
- 同步数据库设计、部署、数据库规则和兼容性差异记录。

### REQ-0004-admin-user-management 要点

- 管理后台 `SYSTEM` 分组新增用户管理入口和页面。
- 用户列表支持头像、用户名、昵称、角色、状态、空间数、时间字段、搜索筛选、分页和固定操作列。
- 新增/编辑用户通过弹窗完成；角色范围仅保留“后台管理员”和“前台用户”。
- 支持冻结、解冻、逻辑删除和重置密码；冻结后目标用户有效会话必须在 10 秒内失效。
- 系统内置唯一超级管理员展示“系统内置”标识，但不可编辑、重置密码、冻结、解冻或删除。
- 头像上传必须具备状态机、同会话即时回显和 Docker `:3000` MinIO 对象访问验收。

### REQ-0005-admin-auth-system 要点

- 管理后台支持超级管理员账号密码登录。
- 登录成功签发 access token，并在服务端保存可撤销、可过期、可校验的会话记录。
- 退出登录、账号冻结、删除、重置密码或权限状态变化后，相关后台会话必须失效。
- 管理后台前端提供路由守卫，未登录或登录态失效时进入后台登录页或等价入口。
- 所有 `/api/v1/admin/**` 必须替换 `x-admin-role: admin` 占位鉴权，改为真实认证授权。
- 通过环境变量首次幂等创建唯一系统内置超级管理员，生产环境禁止空密码、示例密码或弱密码。

### REQ-0006-admin-crud-list-template 要点

- 首期聚焦管理后台 CRUD 列表页模板，不覆盖复杂仪表盘、详情页或跨端组件库。
- 模板覆盖页头、主操作、筛选栏、数据表格、分页、确认弹窗、表单弹窗、toast、加载和空状态。
- 以已归档的用户管理页作为视觉密度、分页 DOM、弹窗和操作反馈基准。
- 后续后台列表页优先通过模板和通用组件创建，减少复制用户管理页大段 JSX/CSS。
- OpenSpec design.md 必须引用 `knowledge_base_refs`，落地 admin-list 与 admin-modal 横切 AC。

### REQ-0007-admin-user-first-login-activation 要点

- 新建后台用户保持“待激活”，由用户本人首次登录成功后自动转为“正常”。
- 待激活后台管理员可使用有效临时密码完成首次登录激活，前台用户不得进入管理后台。
- 冻结用户时记录冻结前状态，解冻时恢复为“待激活”或“正常”，不再固定恢复为“正常”。
- 冻结用户不得登录后台或访问 `/api/v1/admin/**`，已删除用户不得通过解冻或首次登录恢复。
- OpenSpec design.md 必须引用 `knowledge_base_refs`，落地 admin-list 与 admin-modal 横切 AC。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0001-homepage | MoonBox 官网首页品牌视觉更新 | done | — | archived `add-homepage-brand-visual`（2026-07-30 22:21:30） |
| REQ | REQ-0002-login-page | Web 端登录页 | done | — | archived `add-login-page`（2026-08-07 18:03:38） |
| REQ | REQ-0003-database-compatibility | 数据库双环境兼容 | done | — | archived `add-database-compatibility`（2026-07-30 09:36:18） |
| REQ | REQ-0004-admin-user-management | 管理后台用户管理系统 | done | 5 人天 | archived `add-admin-user-management`（2026-08-08 19:20:56） |
| REQ | REQ-0005-admin-auth-system | 管理后台登录认证系统 | done | 5 人天 | archived `add-admin-auth-system`（2026-08-08 22:35:00） |
| REQ | REQ-0006-admin-crud-list-template | 管理后台 CRUD 列表页组件化与模板体系 | done | 3 人天 | archived `add-admin-crud-list-template`（2026-08-08 21:52:47） |
| REQ | REQ-0007-admin-user-first-login-activation | 后台用户首次登录激活与冻结前状态恢复 | done | 3 人天 | archived `update-admin-user-first-login-activation`（2026-08-08 22:22:42） |
| REQ | REQ-0008-prototype-driven-page-acceptance-gate | 原型驱动页面开发验收门禁 | done | 1 人天 | archived `enforce-prototype-driven-ui-gate`（2026-08-08 22:49:01） |
| Change | apply-projecttilesfst-spec-study | apply projecttilesfst spec study | archived | 1 人天 | archived `apply-projecttilesfst-spec-study`（2026-08-07 23:59:59） |
| Change | apply-projecttilesfst-governance-refinements | apply projecttilesfst governance refinements | archived | 1 人天 | archived `apply-projecttilesfst-governance-refinements`（2026-08-07 23:59:59） |
| Change | avoid-duplicate-spec-study-reports | avoid duplicate spec study reports | archived | 1 人天 | archived `avoid-duplicate-spec-study-reports`（2026-08-07 23:59:59） |
| Change | redact-spec-study-local-paths | redact spec study local paths | archived | 1 人天 | archived `redact-spec-study-local-paths`（2026-08-07 23:59:59） |
| Change | apply-projecttilesfst-command-order | apply projecttilesfst command order | archived | 1 人天 | archived `apply-projecttilesfst-command-order`（2026-08-08 23:59:59） |
| Change | optimize-next-step-issue-identity | optimize next step issue identity | archived | 1 人天 | archived `optimize-next-step-issue-identity`（2026-08-08 23:59:59） |
| Change | enforce-sprint-before-opsx | enforce sprint before opsx | archived | 1 人天 | archived `enforce-sprint-before-opsx`（2026-08-08 23:59:59） |
| Change | add-spec-logs-changelog | add spec logs changelog | archived | 1 人天 | archived `add-spec-logs-changelog`（2026-08-08 20:57:30） |
| Change | add-spec-logs-adoption-prompt-column | add spec logs adoption prompt column | archived | 1 人天 | archived `add-spec-logs-adoption-prompt-column`（2026-08-08 21:05:10） |

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0001 | MoonBox 官网首页品牌视觉更新 | P1 | done | archived `add-homepage-brand-visual`（2026-07-30 22:21:30） |
| REQ-0002 | Web 端登录页 | P1 | done | archived `add-login-page`（2026-08-07 18:03:38） |
| REQ-0003 | 数据库双环境兼容 | P1 | done | archived `add-database-compatibility`（2026-07-30 09:36:18） |
| REQ-0004 | 管理后台用户管理系统 | P1 | done | archived `add-admin-user-management`（2026-08-08 19:20:56） |
| REQ-0005 | 管理后台登录认证系统 | P1 | done | archived `add-admin-auth-system`（2026-08-08 22:35:00） |
| REQ-0006 | 管理后台 CRUD 列表页组件化与模板体系 | P1 | done | archived `add-admin-crud-list-template`（2026-08-08 21:52:47） |
| REQ-0007 | 后台用户首次登录激活与冻结前状态恢复 | P1 | done | archived `update-admin-user-first-login-activation`（2026-08-08 22:22:42） |
| REQ-0008 | 原型驱动页面开发验收门禁 | P1 | done | archived `enforce-prototype-driven-ui-gate`（2026-08-08 22:49:01） |
<!-- workflow-sync:scope-requirements:end -->

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
<!-- workflow-sync:scope-bugs:end -->

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `add-homepage-brand-visual` | REQ-0001-homepage | archived | archived `add-homepage-brand-visual`（2026-07-30 22:21:30） |
| `add-login-page` | REQ-0002-login-page | archived | archived `add-login-page`（2026-08-07 18:03:38） |
| `add-database-compatibility` | REQ-0003-database-compatibility | archived | archived `add-database-compatibility`（2026-07-30 09:36:18） |
| `apply-projecttilesfst-spec-study` | — | archived | archived `apply-projecttilesfst-spec-study`（2026-08-07 23:59:59） |
| `apply-projecttilesfst-governance-refinements` | — | archived | archived `apply-projecttilesfst-governance-refinements`（2026-08-07 23:59:59） |
| `avoid-duplicate-spec-study-reports` | — | archived | archived `avoid-duplicate-spec-study-reports`（2026-08-07 23:59:59） |
| `redact-spec-study-local-paths` | — | archived | archived `redact-spec-study-local-paths`（2026-08-07 23:59:59） |
| `add-admin-user-management` | REQ-0004-admin-user-management | archived | archived `add-admin-user-management`（2026-08-08 19:20:56） |
| `apply-projecttilesfst-command-order` | — | archived | archived `apply-projecttilesfst-command-order`（2026-08-08 23:59:59） |
| `add-admin-auth-system` | REQ-0005-admin-auth-system | archived | archived `add-admin-auth-system`（2026-08-08 22:35:00） |
| `optimize-next-step-issue-identity` | — | archived | archived `optimize-next-step-issue-identity`（2026-08-08 23:59:59） |
| `enforce-sprint-before-opsx` | — | archived | archived `enforce-sprint-before-opsx`（2026-08-08 23:59:59） |
| `add-admin-crud-list-template` | REQ-0006-admin-crud-list-template | archived | archived `add-admin-crud-list-template`（2026-08-08 21:52:47） |
| `add-spec-logs-changelog` | — | archived | archived `add-spec-logs-changelog`（2026-08-08 20:57:30） |
| `add-spec-logs-adoption-prompt-column` | — | archived | archived `add-spec-logs-adoption-prompt-column`（2026-08-08 21:05:10） |
| `enforce-prototype-driven-ui-gate` | REQ-0008-prototype-driven-page-acceptance-gate | archived | archived `enforce-prototype-driven-ui-gate`（2026-08-08 22:49:01） |
| `update-admin-user-first-login-activation` | REQ-0007-admin-user-first-login-activation | archived | archived `update-admin-user-first-login-activation`（2026-08-08 22:22:42） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0001`、`REQ-0002`、`REQ-0003`、`REQ-0004`、`REQ-0005`、`REQ-0006`、`REQ-0007` 已纳入正式范围；BUG：无 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 8 个 REQ 范围项关联 Change，另有 9 个纯治理 Change；17 个 Change 均已完成 OpenSpec archive。执行发布与验收复核时以 Scope 表、acceptance-report 和已归档 Change trace 为准。

## 工作量

| 项 | 数值 |
|---|---:|
| 总容量 | 30 人天 |
| 计划工作量 | 27 人天 |
| 容量占用 | 90.0% |
| fix 缓冲 | 3 人天 |
| 剩余未规划容量 | 3 人天 |

容量门禁：通过。`estimated_person_days = 27`，`capacity_person_days = 30`，未超过容量。

## fix 缓冲

本 Sprint 当前机器事实源保留 3 人天未规划容量，fix 缓冲比例为 10.0%，低于 30% 建议值。当前范围仍在总容量内，但后续新增 BUG 或返修需要优先替换低优先级范围或拆分到后续 Sprint。

## 里程碑

| 里程碑 | 目标日期 | 说明 |
|---|---|---|
| 规划完成 | 2026-07-30 08:51:51 | Sprint 四件套生成并同步追溯 |
| 首页实现准备完成 | 2026-08-06 08:51:51 | 完成首页资产与结构实现准备 |
| 登录页实现准备完成 | 2026-08-08 08:51:51 | 完成登录页状态、表单与视觉实现准备 |
| 数据库兼容实现准备完成 | 2026-08-11 08:51:51 | 完成数据库配置、迁移兼容和 MySQL 验证方案 |
| 用户管理实现准备完成 | 2026-08-15 08:51:51 | 完成后台用户管理 API、页面、头像上传与权限审计实现准备 |
| CRUD 列表模板实现准备完成 | 2026-08-18 08:51:51 | 完成后台列表页模板、通用组件边界和用户管理页适配方案 |
| 首次登录激活实现准备完成 | 2026-08-20 08:51:51 | 完成待激活首次登录、冻结前状态记录、解冻恢复和回归测试方案 |
| 验收材料准备完成 | 2026-08-13 08:51:51 | 完成测试和截图验收准备 |
| Sprint 结束窗口 | 2026-08-29 08:51:51 | 完成实现、验收和后续归档准备 |

## 风险

| 风险 | 缓解 |
|---|---|
| 首页视觉资产较大，可能影响 Web 打包体积 | 实现阶段评估 public asset 与压缩策略，但不得改变视觉主体 |
| 首页与登录页共用产品视觉，可能出现遮罩、裁切或加载策略不一致 | 在实现设计中明确首页清晰展示、登录页深色遮罩的差异 |
| 移动端布局可能出现文本、登录卡片或视觉遮挡 | 任务中纳入桌面和移动端截图/布局验收 |
| SQLite 与 MySQL 字段类型、默认值、排序规则和事务行为不一致 | 在实现前沉淀兼容性矩阵，并用 MySQL 关键路径测试兜底 |
| MySQL 测试引入 Docker 或 CI 服务依赖，可能增加验证成本 | 保留 SQLite 本地快速测试，把 MySQL 放入发布前关键路径验证 |
| 用户管理涉及权限、会话失效、对象存储和审计多条链路，可能扩大实现面 | 以 `add-admin-user-management` tasks 分层推进，先完成后端/API/上传链路，再完成 UI 与验收 |
| 头像上传本地 Docker `:3000` 回显可能受对象存储访问路径影响 | 将 `admin-media-upload-chain` gate 写入横切预防清单，并在 apply 阶段做上传、读取和回显验证 |
| 管理后台认证若只做前端路由守卫会形成假安全 | REQ-0005 明确要求替换 `/api/v1/admin/**` 的 `x-admin-role: admin` 占位鉴权，并以后端认证授权作为最终安全判断 |
| access token 若缺少服务端会话校验，会导致退出、冻结或重置密码后旧凭证继续可用 | `/req-opsx` 设计阶段必须明确服务端会话记录、撤销策略、过期策略和后台 API 每次校验路径 |
| CRUD 列表页模板抽象过早或过窄，可能无法承载后续后台页面 | 以用户管理页作为首个验收样板，只抽取列表页通用结构，保留业务字段、接口和规则在页面层 |
| 弹窗宽度、低视口滚动或 toast 反馈若未统一，可能复发 REQ-0004 的 UI 类问题 | 将 `admin-list-page-consistency` 与 `admin-modal-width-css-cascade` gate 写入横切预防清单，并在 apply 阶段做浏览器验证 |
| REQ-0007 追加后 fix 缓冲低于 30% 建议，后续返修空间变小 | 当前保留 3 人天缓冲；新增 BUG 或返修优先移出低优先级项，或拆分到后续 Sprint |
| 待激活首次登录和解冻恢复涉及认证、用户状态和数据库字段，可能与既有用户管理测试路径冲突 | `/req-opsx` 设计阶段必须明确 `status_before_freeze` 或等价持久化方案，并调整“解冻 = 激活”的旧测试路径 |

## 知识库承接

当前知识库未发现最近 Sprint 复盘文件。REQ-0004 命中并承接以下 best-practices：`admin-list-page-consistency.md`、`admin-modal-width-css-cascade.md`、`admin-media-upload-chain.md`。REQ-0006 命中并承接 `admin-list-page-consistency.md` 与 `admin-modal-width-css-cascade.md`，用于约束后台 CRUD 列表页模板、分页 DOM、fixed toast、确认弹窗、禁用 `window.confirm`、computed width 和低视口滚动。REQ-0007 继续承接 `admin-list-page-consistency.md` 与 `admin-modal-width-css-cascade.md`，用于约束待激活状态筛选、冻结/解冻确认弹窗、fixed toast、禁用 `window.confirm`、computed width 和低视口滚动。数据库兼容需求继续承接 `docs/knowledge-base/incidents/2026-07-29-openspec-archive-path.md` 的治理经验：路径与归档事实源需保持一致，避免实现、文档与追溯各写各的。

## 横切预防清单

| 标签 | 适用性 | 处理 |
|---|---|---|
| admin-list | 适用 | 用户列表与 CRUD 列表页模板的分页 DOM 与用户管理基准一致；fixed toast 不得造成 layout shift；状态变更使用 DS confirm；禁止 `window.confirm` |
| admin-form | N/A | 官网与登录页不涉及管理端表单页 |
| admin-modal | 适用 | 新增/编辑用户弹窗和 CRUD 模板弹窗不得出现通用 modal 与专属宽度类级联冲突；验收 computed width 和低视口滚动 |
| media-upload | 适用 | 头像上传必须覆盖 `idle -> uploading -> done/failed`、同会话即时回显、MinIO `images/avatars/` 写入和 Docker `:3000` 授权读取 |
| database-compatibility | 适用 | 非 UI 知识库标签；按 REQ-0003 AC-001 至 AC-020 验收 |
| admin-auth | 适用 | 非 UI 知识库标签；按 REQ-0005 AC-001 至 AC-024 验收后台登录、会话撤销、API 鉴权、初始化和安全测试 |
| admin-user-activation | 适用 | 非 UI 知识库标签；按 REQ-0007 AC-001 至 AC-025 验收待激活首次登录、冻结前状态记录、解冻恢复和回归测试 |

## 依赖 ASCII 树

```text
sprint-001
└── REQ-0001-homepage
    └── add-homepage-brand-visual
        ├── proposal.md
        ├── design.md
        ├── specs/web-catalog-homepage/spec.md
        └── tasks.md
└── REQ-0002-login-page
    └── add-login-page
        ├── proposal.md
        ├── design.md
        ├── specs/web-catalog-login-page/spec.md
        └── tasks.md
└── REQ-0003-database-compatibility
    └── add-database-compatibility
        ├── proposal.md
        ├── design.md
        ├── specs/database-compatibility/spec.md
        └── tasks.md
└── REQ-0004-admin-user-management
    └── add-admin-user-management
        ├── proposal.md
        ├── design.md
        ├── specs/web-admin-user-management/spec.md
        └── tasks.md
└── REQ-0005-admin-auth-system
    └── add-admin-auth-system
        ├── proposal.md
        ├── design.md
        ├── specs/web-admin-auth-system/spec.md
        └── tasks.md
└── REQ-0006-admin-crud-list-template
    └── add-admin-crud-list-template（已归档）
        ├── proposal.md
        ├── design.md
        ├── specs/web-admin-crud-list-template/spec.md
        └── tasks.md
└── REQ-0007-admin-user-first-login-activation
    └── update-admin-user-first-login-activation（已归档）
        ├── requirement.md
        ├── acceptance.md
        └── prototype/web/
```

## 发布计划

本 Sprint 输出 MoonBox 官网首页品牌视觉、Web 登录页前端体验、数据库双环境兼容基础能力、管理后台用户管理系统、管理后台登录认证系统、后台 CRUD 列表页模板体系与后台用户首次登录激活状态治理。发布说明以 `release-note.md` 为准，正式发布前需完成首页、登录页视觉验收、数据库兼容验证、用户管理功能、后台认证安全验收、后台列表页模板横切 UI 验收、待激活首次登录与解冻恢复验收以及 OpenSpec 归档。

## 关闭记录

- 2026-08-08 23:23:52：`/sprint-archive sprint-001` 完成归档关闭；17/17 Change 已归档，195/195 tasks 完成，readiness、env ignore、stale scan 均通过。
- AI Usage Snapshot：`snapshot_status=stale`，`ai_usage_mode=estimated_fallback`，未提供本地 session JSONL，关闭报告仅保留估算兜底，不作为真实 token 用量。

## 复盘记录

- 2026-08-08 23:35:30：`/sprint-exps sprint-001` 已生成复盘：[docs/knowledge-base/retrospectives/sprint-001-retrospective.md](../../../docs/knowledge-base/retrospectives/sprint-001-retrospective.md)。

## 关联文档

- `issues/requirements/archive/REQ-0001-homepage/`
- `issues/requirements/archive/REQ-0002-login-page/`
- `issues/requirements/archive/REQ-0003-database-compatibility/`
- `issues/requirements/archive/REQ-0004-admin-user-management/`
- `issues/requirements/archive/REQ-0005-admin-auth-system/`
- `issues/requirements/archive/REQ-0006-admin-crud-list-template/`
- `issues/requirements/archive/REQ-0007-admin-user-first-login-activation/`
- `openspec/archive/2026-07-30-add-homepage-brand-visual/`
- `openspec/archive/2026-08-07-add-login-page/`
- `openspec/archive/2026-07-30-add-database-compatibility/`
- `openspec/archive/2026-08-08-add-admin-user-management/`
- `openspec/archive/2026-08-08-add-admin-auth-system/`
- `iterations/archive/sprint-001/sprint.yaml`
- `iterations/archive/sprint-001/release-note.md`
- `iterations/archive/sprint-001/acceptance-report.md`
