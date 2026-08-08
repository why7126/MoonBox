## ADDED Requirements

### Requirement: 下一步命令 Issue 身份参数

MoonBox MUST 在命令完成输出中保留下一步可执行命令的链路身份。REQ 来源链路的 `/req-*` 和后续 `/opsx-*` 命令 MUST 使用完整 `REQ-xxxx-slug`，BUG 来源链路的 `/bug-*` 和后续 `/opsx-*` 命令 MUST 使用完整 `BUG-xxxx-slug`；无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

#### Scenario: REQ 链路进入 opsx 后仍使用完整 REQ ID

- **WHEN** 系统完成 `/req-opsx <REQ-full-id>` 或 `/opsx-apply <REQ-full-id>`
- **THEN** 下一步可执行命令 MUST 使用同一个完整 `REQ-xxxx-slug`
- **AND** 系统 MUST NOT 输出 `/opsx-apply <change-id>` 或 `/opsx-archive <change-id>` 作为该 REQ 链路的默认下一步
- **AND** Change ID MAY 仅用于内部解析、OpenSpec CLI、Workflow Sync 或归档路径

#### Scenario: BUG 链路进入 opsx 后仍使用完整 BUG ID

- **WHEN** 系统完成 `/bug-opsx <BUG-full-id>` 或 `/opsx-apply <BUG-full-id>`
- **THEN** 下一步可执行命令 MUST 使用同一个完整 `BUG-xxxx-slug`
- **AND** 系统 MUST NOT 输出 `/opsx-apply <change-id>` 或 `/opsx-archive <change-id>` 作为该 BUG 链路的默认下一步
- **AND** Change ID MAY 仅用于内部解析、OpenSpec CLI、Workflow Sync 或归档路径

#### Scenario: 纯治理 Change 使用 Change ID

- **WHEN** Change 没有关联 REQ 或 BUG
- **THEN** `/opsx-apply`、`/opsx-modify`、`/opsx-archive` 的用户可执行命令 MAY 使用 `<change-id>`
- **AND** 系统 MUST 仍先确认该纯治理 Change 已纳入 Sprint scope
