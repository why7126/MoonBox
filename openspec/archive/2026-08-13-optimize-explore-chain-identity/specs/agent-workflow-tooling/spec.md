## ADDED Requirements

### Requirement: 探索命令保留后续 opsx 链路身份

探索类命令在输出下一步 `/opsx-*` 命令时，MUST 根据上下文识别 Change 是否来源于 REQ 或 BUG；可识别来源时 MUST 使用完整 Issue ID 作为用户可执行命令参数，只有无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

#### Scenario: Explore 识别到 REQ 来源 Change

- **WHEN** `/explore` 或 `/opsx-explore` 基于某个 OpenSpec Change 输出下一步 `/opsx-*` 命令
- **AND** 当前上下文、Change 文档或 Sprint scope 可识别该 Change 来源于完整 `REQ-xxxx-slug`
- **THEN** 下一步命令 MUST 使用该完整 `REQ-xxxx-slug`
- **AND** MUST NOT 使用 `<change-id>` 替代该 REQ 链路身份

#### Scenario: Explore 识别到 BUG 来源 Change

- **WHEN** `/explore` 或 `/opsx-explore` 基于某个 OpenSpec Change 输出下一步 `/opsx-*` 命令
- **AND** 当前上下文、Change 文档或 Sprint scope 可识别该 Change 来源于完整 `BUG-xxxx-slug`
- **THEN** 下一步命令 MUST 使用该完整 `BUG-xxxx-slug`
- **AND** MUST NOT 使用 `<change-id>` 替代该 BUG 链路身份

#### Scenario: Explore 面向纯治理 Change

- **WHEN** `/explore` 或 `/opsx-explore` 输出下一步 `/opsx-*` 命令
- **AND** 已确认该 Change 无 REQ/BUG 来源且属于纯治理 Change
- **THEN** 下一步命令 MAY 使用 `<change-id>`
- **AND** SHOULD 保持 Sprint Inclusion Gate 提示，不得暗示纯治理 Change 可跳过 Sprint
