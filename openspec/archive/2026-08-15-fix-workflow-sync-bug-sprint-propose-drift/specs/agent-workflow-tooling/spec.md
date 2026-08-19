## MODIFIED Requirements

### Requirement: Issues 当前态看板索引

MoonBox SHALL 在 `issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` 维护 REQ/BUG 目录级当前态看板索引。该索引 SHALL 每个 Issue 保留一行最新快照，用于快速定位当前状态、阶段、关联 Sprint、关联 Change、下一步和事实源路径；该索引 SHALL NOT 复制单条 Issue `trace.md` 的完整生命周期事件流水。

#### Scenario: 维护 REQ 当前态行

- **WHEN** 系统完成 REQ 的新建、文档生成/补齐、评审、纳入 Sprint、创建 OpenSpec Change、apply、archive、状态同步或历史漂移修复
- **THEN** 系统 SHALL 更新 `issues/requirements/CHANGELOG.md` 中对应 REQ 的当前态行
- **AND** 当前态行 SHALL 包含 REQ、标题、当前状态、阶段、优先级、关联 Sprint、关联 Change、最近更新时间、下一步和事实源
- **AND** 系统 SHALL NOT 在该索引中复制 REQ `trace.md` 的完整变更记录、验收全文或 UI 证据清单

#### Scenario: 维护 BUG 当前态行

- **WHEN** 系统完成 BUG 的新建、文档生成/补齐、评审、纳入 Sprint、创建 OpenSpec Change、apply、archive、状态同步或历史漂移修复
- **THEN** 系统 SHALL 更新 `issues/bugs/CHANGELOG.md` 中对应 BUG 的当前态行
- **AND** 当前态行 SHALL 包含 BUG、标题、严重等级、当前状态、阶段、关联 Sprint、关联 Change、最近更新时间、下一步和事实源
- **AND** 系统 SHALL NOT 在该索引中复制复现日志原文、截图个人信息、未脱敏日志、真实客户数据、密钥、本机绝对路径、系统用户名或用户主目录

#### Scenario: sprint.propose 刷新 BUG 当前态行

- **GIVEN** BUG 已评审通过并位于 `issues/bugs/review/<BUG-full-id>/`
- **AND** `/sprint-propose --bug <BUG-full-id>` 已将该 BUG 写入 `iterations/change/<sprint-id>/sprint.yaml`
- **WHEN** Workflow Sync 执行 `sprint.propose` 且聚焦该 BUG
- **THEN** Workflow Sync SHALL patch `issues/bugs/CHANGELOG.md` 对应 BUG 行
- **AND** 报告 SHALL 在 Updated 或 Skipped 列表中包含 `issues/bugs/CHANGELOG.md`
- **AND** 当前态行 SHALL 显示 `in_sprint`、`review`、`<sprint-id>`、关联 Change 或“无”、下一步 `/bug-opsx <BUG-full-id>` 或后续可执行命令

#### Scenario: sprint.propose 同步 BUG trace 与 registry

- **GIVEN** BUG 已被写入 `iterations/change/<sprint-id>/sprint.yaml`
- **WHEN** Workflow Sync 执行 `sprint.propose` 且聚焦该 BUG
- **THEN** BUG `trace.md` frontmatter SHALL 同步 `status: in_sprint` 与 `iteration: <sprint-id>`
- **AND** BUG `trace.md` fenced yaml SHALL 同步 `status: in_sprint`、`lifecycle.status: in_sprint`、`lifecycle.stage: review` 和 `lifecycle.iteration: <sprint-id>`
- **AND** `issues/bugs/_registry.yaml` SHALL 同步该 BUG 的 `status`、`iteration`、`lifecycle_stage` 和真实阶段目录 `path`

#### Scenario: 事实判断继续读取权威来源

- **WHEN** Agent、脚本或人工评审需要确认单条 Issue 的真实状态、验收、Sprint、Change 或归档闭环
- **THEN** 系统 SHALL 读取 `_registry.yaml`、目标 Issue `trace.md`、Sprint 四件套、OpenSpec Change 或正式规格
- **AND** 系统 SHALL NOT 使用 `issues/requirements/CHANGELOG.md` 或 `issues/bugs/CHANGELOG.md` 替代权威事实源

#### Scenario: 跳过普通文案更新

- **WHEN** 系统只执行普通文案润色、格式调整、错别字修复或非状态性验收措辞调整
- **THEN** 系统 MAY 不更新 `issues/requirements/CHANGELOG.md` 或 `issues/bugs/CHANGELOG.md`
- **AND** 系统 SHALL 继续在单条 Issue 文档中维护必要的 `updated_at` 或变更记录
