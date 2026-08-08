# agent-workflow-tooling Specification

## Purpose
定义 MoonBox Agent 工作流治理命令、跨项目学习、规范优化和原型驱动 UI 开发门禁，确保需求、Sprint、OpenSpec、实现、验收与归档之间保持可追溯、可验证和中文优先的协作规则。
## Requirements
### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。同一次 `/spec-study` 学习应用流程 MUST 只生成一份正式 `study` 报告，且持久化学习对象时 MUST 使用脱敏项目标识，不得记录本机绝对路径、系统用户名或用户主目录。跨项目学习应用命令执行顺序时，系统 MUST 产出可复用的命令顺序规则，并避免复制学习对象业务专属流程。

#### Scenario: 应用命令执行顺序学习结果

- **WHEN** 用户确认应用跨项目命令执行顺序学习结果
- **THEN** 系统 MUST 将推荐命令链路写入本项目治理文档或技能
- **AND** 系统 MUST 区分 REQ、BUG、Sprint、OpenSpec、release、image 和 usage-docs 命令族的先后关系
- **AND** 系统 MUST 明确会写同一机器事实源的步骤需要串行执行
- **AND** 系统 MUST NOT 复制学习对象业务专属命令作为 MoonBox 默认流程

### Requirement: 规范优化命令 spec-opt

`/spec-opt` MUST 作为项目治理规范优化入口，用于新增或修改 `.agents/skills/` 命令、`rules/` 文档、`docs/` 文档规范、`scripts/` 治理脚本、`AGENTS.md` 入口和 active OpenSpec Change 文档。`/spec-opt` 完成本项目规范、技能、脚本、目录边界或校验规则迭代后，MUST 在 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md` 写入治理迭代日志，并 SHOULD 同步更新 `docs/spec-logs/CHANGELOG.md` 的目录级变更历史。

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

### Requirement: 原型驱动 UI 开发门禁
系统 SHALL 对带 `prototype/` 的 UI 页面建立从需求完善、OpenSpec 转换、实现、返修到归档的连续门禁，确保原型拆解、UI Skeleton、1440px 视觉验收和 REQ 文档最终一致性检查均被记录并通过。

#### Scenario: 需求完善拆解 prototype
- **GIVEN** 一个 UI REQ 存在 `prototype/web/` 或等价页面原型目录
- **WHEN** 执行 `/req-complete <REQ-full-id>`
- **THEN** 系统 SHALL 在需求文档中记录原型页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点
- **AND** 系统 SHALL 将可测试验收项写入 `acceptance.md` 并在 `trace.md` 记录 `prototype_refs`

#### Scenario: OpenSpec 承接 UI Skeleton
- **GIVEN** 一个带 prototype 的 REQ 已进入 `/req-opsx`
- **WHEN** 系统生成 active Change
- **THEN** Change `design.md` SHALL 包含 UI Skeleton 章节
- **AND** Change `tasks.md` SHALL 包含先完成 UI Skeleton 再实现细节的独立任务
- **AND** Change SHALL 记录 prototype 与 acceptance 的冲突处理结论

#### Scenario: 实现阶段执行 1440px 视觉验收
- **GIVEN** 一个带 prototype 的 UI Change 正在 `/opsx-apply` 或 `/opsx-modify`
- **WHEN** 相关 UI 任务准备标记完成
- **THEN** 系统 SHALL 先在 1440px 桌面视口完成视觉验收
- **AND** 系统 SHALL 记录截图或等价证据入口、验收命令和结果摘要

#### Scenario: 归档前检查 REQ 最终一致性
- **GIVEN** 一个带 prototype 的 UI Change 准备 `/opsx-archive`
- **WHEN** 系统执行归档前文档同步门禁
- **THEN** 系统 SHALL 复核 linked REQ 的 `requirement.md`、`acceptance.md`、`trace.md` 与 Change 设计、实现证据、验收结果一致
- **AND** 若发现验收口径、非目标、UI 行为、视觉证据或实现差异，系统 SHALL 阻断归档并要求先回填或返修

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

### Requirement: 命令执行顺序治理

MoonBox MUST 维护 AI 工作流命令的推荐执行顺序，并在技能输出中给出符合链路身份的下一步命令。REQ 来源链路的后续实现和归档命令 MUST 使用原始 `REQ-*`，BUG 来源链路 MUST 使用原始 `BUG-*`，无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

#### Scenario: 推荐标准执行顺序

- **WHEN** 系统需要引导用户从需求或缺陷进入交付
- **THEN** 系统 SHOULD 推荐 `capture/complete/review → sprint-propose → req-opsx/bug-opsx → opsx-apply → opsx-modify → opsx-archive → sprint-archive → release/image/usage-docs` 的顺序
- **AND** `opsx-modify` MUST 只用于 `opsx-apply` 后、`opsx-archive` 前的验收返修
- **AND** release、image 和 usage-docs 命令 SHOULD 位于 OpenSpec 与 Sprint 关键门禁之后

#### Scenario: 串行写入事实源

- **WHEN** 命令会写入 `sprint.yaml`、Workflow Sync 派生块、Issue promote 结果或 AI Usage snapshot
- **THEN** 系统 MUST 严格串行执行这些步骤
- **AND** 系统 MUST NOT 并行运行多个会写同一 Sprint scope、Issue 状态或 AI Usage snapshot 的命令
- **AND** 系统 MUST 先写机器事实源，再运行 Workflow Sync 和对应校验

