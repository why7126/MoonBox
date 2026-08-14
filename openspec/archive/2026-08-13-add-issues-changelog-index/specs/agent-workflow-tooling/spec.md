## ADDED Requirements

### Requirement: Issues 全局事件索引

MoonBox SHALL 在 `issues/requirements/CHANGELOG.md` 与 `issues/bugs/CHANGELOG.md` 维护 REQ/BUG 目录级关键事件索引，用于按时间倒序记录 capture、文档生成/补齐、评审、纳入 Sprint、创建 OpenSpec Change、apply、archive、状态同步和历史漂移修复摘要。全局事件索引 SHALL 只作为入口地图和摘要，不得替代 `_registry.yaml`、单条 Issue `trace.md`、OpenSpec Change、Sprint 四件套或正式规格事实源。

#### Scenario: 记录 REQ 关键生命周期事件

- **WHEN** 系统完成 REQ 的 `capture`、`generate`、`complete`、`review.approve`、`review.reject`、`review.defer`、`sprint.include`、`opsx.create`、`apply.done`、`archive.done`、`status.sync` 或 `trace.fix` 事件
- **THEN** 系统 SHALL 在 `issues/requirements/CHANGELOG.md` 按时间倒序追加事件摘要
- **AND** 事件摘要 SHALL 包含时间、事件、REQ、标题、状态、阶段、关联 Sprint、关联 Change、摘要和后续建议
- **AND** 系统 SHALL NOT 使用该索引替代 REQ `trace.md` 或 `_registry.yaml` 判断当前状态

#### Scenario: 记录 BUG 关键生命周期事件

- **WHEN** 系统完成 BUG 的 `capture`、`generate`、`complete`、`review.approve`、`review.reject`、`review.defer`、`sprint.include`、`opsx.create`、`apply.done`、`archive.done`、`status.sync` 或 `trace.fix` 事件
- **THEN** 系统 SHALL 在 `issues/bugs/CHANGELOG.md` 按时间倒序追加事件摘要
- **AND** 事件摘要 SHALL 包含时间、事件、BUG、标题、严重等级、状态、阶段、关联 Sprint、关联 Change、摘要和后续建议
- **AND** 系统 SHALL NOT 在索引中复制复现日志原文、截图个人信息、未脱敏日志、真实客户数据、密钥、本机绝对路径、系统用户名或用户主目录

#### Scenario: 跳过普通文案更新

- **WHEN** 系统只执行普通文案润色、格式调整、错别字修复或非状态性验收措辞调整
- **THEN** 系统 MAY 不更新 `issues/requirements/CHANGELOG.md` 或 `issues/bugs/CHANGELOG.md`
- **AND** 系统 SHALL 继续在单条 Issue 文档中维护必要的 `updated_at` 或变更记录
