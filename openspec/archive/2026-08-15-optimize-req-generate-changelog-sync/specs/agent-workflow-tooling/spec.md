## ADDED Requirements

### Requirement: req.generate 当前态看板派生刷新

Workflow Sync MUST 在 `req.generate --req <REQ-full-id>` 成功同步时刷新 `issues/requirements/CHANGELOG.md` 对应 REQ 当前态行。

#### Scenario: req.generate 刷新需求 CHANGELOG

- **GIVEN** 一个已存在的 REQ 文档包
- **AND** `requirement.md` 与 `trace.md` 已进入 `draft`
- **WHEN** 运行 `python scripts/sync-workflow-status.py --event req.generate --req <REQ-full-id> --sprint auto`
- **THEN** Workflow Sync MUST patch `issues/requirements/CHANGELOG.md` 对应 REQ 行
- **AND** 当前状态 MUST 来自 Issue trace / derived issue status
- **AND** 下一步 SHOULD 为 `/req-complete <REQ-full-id>`

#### Scenario: req.generate dry-run 暴露派生覆盖

- **GIVEN** 目标 REQ 当前态看板行需要刷新
- **WHEN** 运行 `python scripts/sync-workflow-status.py --event req.generate --req <REQ-full-id> --sprint auto --dry-run --output detail`
- **THEN** 报告 MUST 在 Updated 或 Skipped 列表中包含 `issues/requirements/CHANGELOG.md`
