## ADDED Requirements

### Requirement: Workflow Sync sprint.propose 同步聚焦 Issue 主文档

Workflow Sync MUST 在 `sprint.propose` 聚焦 REQ 或 BUG 成功同步时，将对应 Issue 主文档的 `status` 镜像为当前派生主状态。REQ 主文档为 `requirement.md`，BUG 主文档为 `bug.md`；同步范围 MUST 限定为命令传入的聚焦 Issue，不得批量改写无关 Issue 子文档。

#### Scenario: BUG 纳入 Sprint 后同步 bug.md 主状态

- **GIVEN** 已评审 BUG 通过 `/sprint-propose --bug <BUG-full-id>` 纳入 Sprint
- **AND** Workflow Sync 将该 BUG 派生为 `in_sprint`
- **WHEN** Workflow Sync 执行 `--event sprint.propose --bug <BUG-full-id>`
- **THEN** 系统 MUST 将该 BUG 的 `bug.md` Frontmatter `status` 同步为 `in_sprint`
- **AND** 系统 MUST 保持未聚焦 BUG 的主文档状态不被本次同步改写

#### Scenario: REQ 纳入 Sprint 后同步 requirement.md 主状态

- **GIVEN** 已评审 REQ 通过 `/sprint-propose --req <REQ-full-id>` 纳入 Sprint
- **AND** Workflow Sync 将该 REQ 派生为 `in_sprint`
- **WHEN** Workflow Sync 执行 `--event sprint.propose --req <REQ-full-id>`
- **THEN** 系统 MUST 将该 REQ 的 `requirement.md` Frontmatter `status` 同步为 `in_sprint`
- **AND** 系统 MUST 保持未聚焦 REQ 的主文档状态不被本次同步改写
