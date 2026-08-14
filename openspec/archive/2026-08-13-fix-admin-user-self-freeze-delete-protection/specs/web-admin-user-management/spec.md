# web-admin-user-management Delta

## MODIFIED Requirements

### Requirement: 用户状态治理
系统 SHALL 支持后台管理员冻结、解冻和逻辑删除用户，并保留审计追溯所需数据。

#### Scenario: 当前登录用户不得冻结自己
- **GIVEN** 当前登录用户具备后台管理员权限
- **AND** 目标用户 ID 等于当前登录用户 ID
- **WHEN** 当前登录用户确认冻结该目标用户
- **THEN** 后端 MUST 返回 `403 Forbidden`
- **AND** 系统 MUST NOT 修改该用户状态
- **AND** 系统 MUST NOT 撤销该用户当前会话
- **AND** 前端 MUST 保留当前账号行的冻结按钮但将其置为禁用状态

#### Scenario: 当前登录用户不得删除自己
- **GIVEN** 当前登录用户具备后台管理员权限
- **AND** 目标用户 ID 等于当前登录用户 ID
- **WHEN** 当前登录用户确认删除该目标用户
- **THEN** 后端 MUST 返回 `403 Forbidden`
- **AND** 系统 MUST NOT 将该用户标记为已删除
- **AND** 系统 MUST NOT 设置该用户 `deleted_at`
- **AND** 系统 MUST NOT 撤销该用户当前会话
- **AND** 前端 MUST 保留当前账号行的删除按钮但将其置为禁用状态

### Requirement: 用户管理 UI 横切一致性
系统 SHALL 遵循 MoonBox 管理后台 UI 规则和用户管理横切验收要求，并将用户管理页作为后台 CRUD 列表页模板化适配的首个验收样板。

#### Scenario: 当前账号行危险操作保护
- **WHEN** 用户管理列表渲染当前登录账号所在行
- **THEN** 当前账号行 MUST 展示禁用态冻结按钮并提供不可冻结当前登录账号的原因
- **AND** 当前账号行 MUST 展示禁用态删除按钮并提供不可删除当前登录账号的原因
- **AND** 当前账号行 MUST NOT 显示额外“当前账号”文案
- **AND** 其他非系统用户行 SHOULD 保持既有冻结、解冻、删除和重置密码操作能力
