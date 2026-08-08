## ADDED Requirements

### Requirement: 评审后先 Sprint 再 opsx

MoonBox MUST 在 REQ/BUG 评审通过后先通过 `/sprint-propose` 纳入 Sprint，再通过 `/req-opsx` 或 `/bug-opsx` 创建 OpenSpec Change。`approved` 只表示评审通过；`in_sprint` 才表示可进入 opsx 转换。

#### Scenario: REQ 评审后推荐 Sprint

- **WHEN** 系统完成 `/req-review <REQ-full-id> --approve`
- **THEN** 下一步 MUST 输出 `/sprint-propose --req <REQ-full-id>`
- **AND** 系统 MUST NOT 将 `/req-opsx <REQ-full-id>` 作为直接下一步

#### Scenario: BUG 评审后推荐 Sprint

- **WHEN** 系统完成 `/bug-review <BUG-full-id> --approve`
- **THEN** 下一步 MUST 输出 `/sprint-propose --bug <BUG-full-id>`
- **AND** 系统 MUST NOT 将 `/bug-opsx <BUG-full-id>` 作为直接下一步

#### Scenario: opsx 转换要求已纳入 Sprint

- **WHEN** 系统执行 `/req-opsx <REQ-full-id>` 或 `/bug-opsx <BUG-full-id>`
- **THEN** 目标 Issue 状态 MUST 为 `in_sprint` 或后续交付态
- **AND** 若状态仍为 `approved`，系统 MUST 停止并提示先执行对应 `/sprint-propose`
