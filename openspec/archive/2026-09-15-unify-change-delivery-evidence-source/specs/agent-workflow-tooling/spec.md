## MODIFIED Requirements

### Requirement: 规范优化命令 spec-opt

`/spec-opt` MUST 作为项目治理规范优化入口，用于新增或修改 `.agents/skills/` 命令、`rules/` 文档、`docs/` 文档规范、`scripts/` 治理脚本、`AGENTS.md` 入口和 active OpenSpec Change 文档。`/spec-opt` 完成本项目规范、技能、脚本、目录边界或校验规则迭代后，MUST 在 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md` 写入治理迭代日志，并 SHOULD 同步更新 `docs/spec-logs/CHANGELOG.md` 的目录级变更历史。`/spec-opt` 不强制纯治理 Change 生成 `acceptance.md` 或 `verification.md`，但当 Change 进入 applied 前，MUST 在 Change 内保留需求中心可识别的交付验证来源，优先使用 `trace.md` 的 `## 验证记录` 或 `## 验证摘要`，或使用 `trace.acceptance_refs` 指向 Change 内 Markdown 证据。

#### Scenario: 输出治理迭代日志

- **WHEN** `/spec-opt` 完成本项目规范、技能、脚本、目录边界或校验规则迭代
- **THEN** `/spec-opt` MUST 在 `docs/spec-logs/` 写入治理迭代日志
- **AND** 日志文件名 MUST 使用 `YYYYMMDDhhmmss-governance-xxx.md`
- **AND** 日志 MUST 包含迭代目标、变更摘要、影响范围、更新文件、验证结果和后续建议
- **AND** 日志 MUST NOT 包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息或学习对象源码

#### Scenario: 维护治理变更历史

- **WHEN** `/spec-opt` 完成本项目规范、技能、脚本、目录边界或校验规则迭代
- **THEN** 系统 SHOULD 更新 `docs/spec-logs/CHANGELOG.md`
- **AND** `CHANGELOG.md` SHOULD 按时间倒序记录治理变更摘要、更新文件、验证结果和后续建议
- **AND** `CHANGELOG.md` MUST 指向对应的单次治理日志或学习报告
- **AND** `CHANGELOG.md` MUST NOT 替代单次治理日志、OpenSpec Change、Sprint 四件套或正式规格事实源
- **AND** `CHANGELOG.md` MUST NOT 包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、本机绝对路径、系统用户名或用户主目录

#### Scenario: 纯治理 Change 保留可识别交付验证来源

- **WHEN** `/spec-opt` 完成纯治理 Change 并准备进入 applied
- **THEN** Agent MUST NOT 因纯治理 Change 缺少 `acceptance.md` 或 `verification.md` 而阻断
- **AND** Agent MUST 在 Change 内记录可被需求中心识别的交付验证来源
- **AND** 该来源 MUST 是 `trace.md` 非空验证类章节、非空 `acceptance.md` / `verification.md`，或 `trace.acceptance_refs` 指向的 Change 内 Markdown
- **AND** Agent MUST NOT 只依赖最终回复、治理日志、tasks 全勾或 Workflow Sync 成功作为交付验证来源

### Requirement: 研发执行生命周期同步

系统 MUST 在 `/opsx-apply` 实施前写入 `opsx.start` 执行事实，在批次进展后写入 `opsx.progress`，并且只有完成门禁通过后才能写入 `opsx.apply`。执行事实 MUST 使用 `execution.schema_version: 1`，保存 `started_at`、`completed_at` 与 `last_event`；`status` MUST 由执行事实与任务进度派生，不能伪造历史启动或完成时间。所有 applied Change MUST 在完成态同步前保留 Change 内可识别交付验证来源；纯治理 Change 不强制生成 `acceptance.md` 或 `verification.md`，但 MUST 优先在 `trace.md` 写入 `## 验证记录` 或 `## 验证摘要`。

#### Scenario: 启动执行事实

- **WHEN** `/opsx-apply` 通过实施前门禁并准备修改当前 Change 范围
- **THEN** Agent MUST 先运行 `opsx.start` 同步
- **AND** Change trace MUST 写入或保留 `execution.schema_version: 1`
- **AND** `started_at` MUST 使用真实执行时间
- **AND** `completed_at` MUST 保持为空
- **AND** `last_event` MUST 记录启动或后续真实进展事件

#### Scenario: 进度不声明完成

- **WHEN** Agent 完成一批任务但尚未通过完成门禁
- **THEN** Agent MAY 运行 `opsx.progress`
- **AND** `completed_at` MUST 保持为空
- **AND** 系统 MUST NOT 将任务部分完成、CLI 进行中提示或前端查看进度解释为已完成

#### Scenario: 完成同步要求交付验证来源

- **WHEN** `/opsx-apply` 准备运行完成态 `opsx.apply`
- **THEN** Agent MUST 确认全部任务完成、相关验证通过、文档同步完成且 Change 内存在可识别交付验证来源
- **AND** 如果 Change 没有 `acceptance.md` 或 `verification.md`，Agent MUST 使用 `trace.md` 验证类章节或 `trace.acceptance_refs` 记录证据入口
- **AND** Workflow Sync MUST 在完成门禁通过后写入 `completed_at` 和 `last_event: opsx.apply`
- **AND** 系统 MUST NOT 用 tasks 全勾、`status: applied`、Workflow Sync 成功或治理日志替代交付验证来源

#### Scenario: 旧终态兼容读取

- **WHEN** 历史 Change 没有 execution block 但已有 legacy applied 状态或全量完成任务
- **THEN** 系统 MAY 按旧终态兼容读取
- **AND** 系统 MUST NOT 伪造 `started_at` 或 `completed_at`
- **AND** 后续新执行事件 MUST 使用 execution schema v1 记录真实事实
