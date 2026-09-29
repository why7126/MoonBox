## ADDED Requirements

### Requirement: req.complete 当前态投影派生刷新
Workflow Sync MUST 在 `req.complete` 聚焦同步成功后，将目标 REQ 的当前状态派生为 `pending_review`，并使用同一派生态刷新 trace、registry、CHANGELOG 与当前态看板。

#### Scenario: 从 draft 完成后推进到 pending_review
- **GIVEN** 目标 REQ 的 trace 或 registry 当前状态为 `draft`
- **WHEN** 执行 `sync-workflow-status.py --event req.complete --req <REQ-full-id>`
- **THEN** trace 当前状态 MUST 为 `pending_review`
- **AND** registry、CHANGELOG 与当前态看板 MUST 使用 `pending_review`
- **AND** CHANGELOG 的 next action MUST 指向 `/req-review <REQ-full-id>`

#### Scenario: 从 enriching 完成后推进到 pending_review
- **GIVEN** 目标 REQ 的 trace 或 registry 当前状态为 `enriching`
- **WHEN** 执行 `sync-workflow-status.py --event req.complete --req <REQ-full-id>`
- **THEN** trace 当前状态 MUST 为 `pending_review`
- **AND** registry、CHANGELOG 与当前态看板 MUST 使用 `pending_review`
- **AND** 当前态看板 MUST NOT 报告该 REQ 存在状态数据漂移

#### Scenario: 重复完成事件保持幂等
- **GIVEN** 目标 REQ 已经处于 `pending_review`
- **WHEN** 再次执行 `sync-workflow-status.py --event req.complete --req <REQ-full-id>`
- **THEN** trace、registry、CHANGELOG 与当前态看板 MUST 保持 `pending_review`
- **AND** 同步过程 MUST NOT 将状态回退为 `draft` 或 `enriching`

### Requirement: bug.complete 当前态投影派生刷新
Workflow Sync MUST 在 `bug.complete` 聚焦同步成功后，将仍处于补齐阶段的目标 BUG 当前状态派生为 `pending_review`，并使用同一派生态刷新 trace、registry 与 CHANGELOG；已进入 Sprint 或后续交付态的 BUG MUST 保持当前交付状态不被 complete 事件回退。

#### Scenario: BUG 从 draft 完成后推进到 pending_review
- **GIVEN** 目标 BUG 的 trace 或 registry 当前状态为 `draft`
- **WHEN** 执行 `sync-workflow-status.py --event bug.complete --bug <BUG-full-id>`
- **THEN** trace 当前状态 MUST 为 `pending_review`
- **AND** registry 与 CHANGELOG MUST 使用 `pending_review`

#### Scenario: 已纳入 Sprint 的 BUG 不被 complete 事件回退
- **GIVEN** 目标 BUG 已经处于 `in_sprint`
- **WHEN** 执行 `sync-workflow-status.py --event bug.complete --bug <BUG-full-id>`
- **THEN** trace、registry、CHANGELOG 与 Sprint 投影 MUST 保持 `in_sprint`
- **AND** 同步过程 MUST NOT 将状态回退为 `pending_review`
