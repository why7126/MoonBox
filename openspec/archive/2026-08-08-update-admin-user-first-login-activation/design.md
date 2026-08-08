# 设计说明

## 背景

REQ-0007 补充 REQ-0004 用户管理与 REQ-0005 后台认证之间的账号生命周期规则。当前已有“待激活”“正常”“已冻结”“已删除”主状态，且用户管理列表已支持状态筛选；本 Change 采用保守方案，不拆分双状态模型，只新增冻结前状态记录或等价持久化能力，避免扩大数据模型和 UI 范围。

## 目标与非目标

**Goals:**

- 新建用户保持“待激活”，由用户本人首次后台登录成功后自动激活为“正常”。
- 冻结用户时记录冻结前状态，解冻时恢复冻结前状态。
- 保持已冻结、已删除、前台用户不能进入后台的安全边界。
- 在用户管理 UI 中清晰表达“解冻后恢复目标状态”，避免把解冻误解为激活。
- 将 prototype 拆解承接到 UI Skeleton、任务和验收追溯中。

**Non-Goals:**

- 不拆分 `activation_status` 与 `access_status` 双状态模型。
- 不新增邀请邮件、激活链接、首次登录改密向导、MFA、SSO、OAuth 或短信/邮箱验证码。
- 不新增独立审计日志查询页面。
- 不改变系统内置超级管理员保护规则。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: true
  database: true
  storage: false
  api: true
  security: true
capabilities:
  new: []
  modified:
    - web-admin-user-management
    - web-admin-auth-system
```

## D1. 前端策略

采用保守的 Design System 原生实现策略，不做整页 CSS Port。`prototype/web/prototype.html` 作为后台用户状态治理页的结构和交互输入，最终实现应复用现有后台用户管理页面、设计系统确认弹窗、fixed toast、状态标签、筛选栏和分页模式。

`knowledge_base_refs` 必须落入实现与验收：

- `docs/knowledge-base/best-practices/admin-list-page-consistency.md`
- `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`

状态变更确认必须使用设计系统弹窗，不得调用 `window.confirm`。弹窗宽度和低视口滚动需通过浏览器 computed style 或等价证据验收。

## D2. 状态模型

继续使用现有用户主状态表达账号当前可用性：

```text
pending_activation -> active
pending_activation -> frozen -> pending_activation
active -> frozen -> active
deleted -> terminal
```

冻结时记录冻结前状态。推荐字段为 `status_before_freeze`，等价实现也可接受，但必须满足：

- 仅在从“待激活”或“正常”进入“已冻结”时写入冻结前状态。
- 对已冻结用户重复冻结不得覆盖既有冻结前状态。
- 解冻时根据冻结前状态恢复主状态。
- 解冻成功后清空或重置冻结前状态。
- 已删除用户不得因冻结前状态被恢复。

若历史冻结用户缺少冻结前状态，服务端必须返回受控错误或采用明确兼容策略；不得静默恢复为“正常”。

## D3. 首次登录激活

后台登录认证在凭证有效后必须先校验用户角色和状态：

- 后台管理员 + 待激活 + 有效临时密码：允许登录，事务内更新状态为“正常”，创建后台会话。
- 后台管理员 + 正常 + 凭证有效：按既有规则登录。
- 已冻结或已删除：拒绝登录和首次激活。
- 前台用户：不得进入管理后台，即使处于待激活或正常状态。

登录失败响应必须使用受控文案，不泄露账号是否存在、冻结前状态字段、密码哈希或内部状态细节。

## D4. UI Skeleton

原型来源：

- `issues/requirements/review/REQ-0007-admin-user-first-login-activation/prototype/web/prototype.html`
- `issues/requirements/review/REQ-0007-admin-user-first-login-activation/prototype/web/context.md`

页面结构：

```text
AdminUserStatusPage
├── PageHeader
│   ├── title: 后台用户状态治理 / 用户管理
│   ├── helper: 待激活由用户首次登录完成
│   └── primaryAction: 新增用户
├── AdminUserFilterBar
│   ├── searchInput
│   ├── roleSelect
│   └── statusSelect: 全部状态 / 待激活 / 正常 / 已冻结
├── AdminUserStatusTable
│   ├── userCell
│   ├── roleCell
│   ├── statusBadge
│   ├── statusBeforeFreezeCell
│   ├── lastLoginAtCell
│   └── rowActions: 编辑 / 重置密码 / 冻结或解冻
├── PaginationBar
│   ├── total
│   └── pageControls
├── UnfreezeConfirmModal
│   ├── targetUserSummary
│   ├── restoreTargetHint
│   ├── reasonField
│   └── actions
└── AdminFixedToast
```

状态容器：

- `filters`: 搜索词、角色、状态、页码、每页条数。
- `users`: 列表数据、总数、loading、empty、error。
- `statusMutation`: 当前操作、目标用户、原因、提交中状态、错误。
- `sensitiveResult`: 创建或重置密码的一次性临时密码展示状态。
- `toast`: fixed 成功/失败反馈。

数据依赖：

- 用户列表 API 返回 `status`，并在已冻结用户上提供 `status_before_freeze` 或可推导的恢复目标状态。
- 冻结/解冻 API 接收目标用户、原因，并返回更新后的用户状态或刷新列表所需信息。
- 登录 API 在待激活后台管理员首次登录成功后返回 access token、过期时间和当前用户摘要。

可测选择器建议：

- `[data-testid="admin-user-status-filter"]`
- `[data-testid="admin-user-status-badge"]`
- `[data-testid="admin-user-status-before-freeze"]`
- `[data-testid="admin-user-freeze-action"]`
- `[data-testid="admin-user-unfreeze-action"]`
- `[data-testid="admin-user-unfreeze-modal"]`
- `[data-testid="admin-user-unfreeze-restore-target"]`
- `[data-testid="admin-fixed-toast"]`

1440px 验收焦点：

- 筛选栏三列布局稳定，不因状态文案变化挤压搜索框。
- 表格状态标签、冻结前状态和行内操作不重叠。
- 解冻确认弹窗最终 computed width 与设计预期一致。
- “解冻后恢复为待激活/正常”提示可见，且不与原因输入遮挡。
- fixed toast 位于视口固定位置，不引发布局位移。
- 页面无 `window.confirm` 交互痕迹。

## D5. Conflict Resolution

原型与验收优先级：

```text
HTML > PNG > *-context.md > acceptance.md > ui-design.md > openspec/specs
```

本 REQ 没有 PNG 原型。`prototype.html` 表达用户管理页结构、解冻弹窗和 fixed toast 位置；`context.md` 已完成拆解，负责承接页面清单、状态矩阵和 1440px 验收焦点。若原型文案与验收冲突，以 `acceptance.md`、安全规则和本 design 的状态模型为准。若既有 `web-admin-user-management` 规格仍写“解冻恢复可用状态”，本 Change 的 delta spec 将其修订为“恢复冻结前状态”。

最终验收以 Change design、acceptance、1440px 视觉证据和 REQ 最终一致性回填共同为准。

## D6. Migration Plan

1. 数据库新增 `status_before_freeze` 或等价字段，并为 SQLite/MySQL 保持兼容。
2. 对历史已冻结用户缺少冻结前状态的场景，采用受控错误或明确兼容策略，并补充测试。
3. 后端冻结/解冻与登录流程先完成事务和审计，再接入前端展示。
4. 前端先落 UI Skeleton 和状态容器，再实现具体 API 联动。
5. 实现后同步 OpenAPI、API 文档、数据库文档和测试证据。

## 风险与取舍

- 历史冻结数据缺少冻结前状态 -> 通过受控错误或明确兼容策略避免误恢复为正常。
- 待激活登录放宽可能误放前台用户 -> 后端必须同时校验后台角色、状态和凭证，测试覆盖前台用户拒绝。
- 解冻弹窗文案误导管理员 -> UI 必须展示恢复目标状态，不使用“激活”含义。
- 弹窗宽度被通用样式覆盖 -> 实现阶段必须检查 computed width 和低视口滚动。

## 待决问题

- 无。
