## ADDED Requirements

### Requirement: Workflow Sync Issue 子文档 apply 输出明细
Workflow Sync 在 `--apply-issue-subdocuments` 或聚焦事件触发 Issue 子文档同步时，SHALL 在 summary 输出中清晰报告本轮子文档 apply 结果。

#### Scenario: 子文档 apply summary 展示安全同步项
- **WHEN** Workflow Sync 对聚焦 Issue 执行子文档同步
- **AND** 存在 `safe_sync`、`safe_rename`、`residual_safe_sync` 或验收回填
- **THEN** summary 输出 MUST 包含聚焦 Issue、`updated_files`、`updated_fields`、`acceptance_status` 和安全同步项的文件、来源、旧值与目标值
- **AND** summary 输出 MUST 保留 warning/blocker 数量，避免把语义不明字段静默当作成功应用

### Requirement: Workflow Sync 当前态看板 next 使用最新派生态
Workflow Sync 在 `req.opsx` / `bug.opsx` 回填新 Change 后，SHALL 使用同一轮最新 Issue 派生态刷新当前态看板。

#### Scenario: req.opsx 后 next 进入 opsx-apply
- **WHEN** Workflow Sync 以 `--event req.opsx --req <REQ-full-id> --change <change-id>` 执行
- **AND** 目标 REQ 已纳入 Sprint
- **THEN** `issues/requirements/CHANGELOG.md` 对应行的 `关联 Change` MUST 为 `<change-id>`
- **AND** `下一步` MUST 为 `/opsx-apply <REQ-full-id>`

#### Scenario: bug.opsx 后 next 进入 opsx-apply
- **WHEN** Workflow Sync 以 `--event bug.opsx --bug <BUG-full-id> --change <change-id>` 执行
- **AND** 目标 BUG 已纳入 Sprint
- **THEN** `issues/bugs/CHANGELOG.md` 对应行的 `关联 Change` MUST 为 `<change-id>`
- **AND** `下一步` MUST 为 `/opsx-apply <BUG-full-id>`
