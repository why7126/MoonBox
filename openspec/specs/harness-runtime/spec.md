# harness-runtime Specification

## Purpose
TBD - created by archiving change add-opsx-modify-ui-screenshot-comparison-gate. Update Purpose after archive.
## Requirements
### Requirement: UI 返修附件截图逐项视觉对照

系统 MUST 在 UI 型 `/opsx-modify` 返修前，对验收反馈中的附件截图、标注截图、原型截图或实际截图建立逐项视觉对照表，并以该表作为进入实现返修的前置检查。

#### Scenario: UI 返修前建立逐项视觉对照表

- **WHEN** `/opsx-modify` 的验收反馈涉及 UI 视觉偏差、prototype、截图附件、标注图或关键交互状态
- **THEN** Agent MUST 先识别当前反馈中的附件截图、原型截图、实际截图和历史视觉证据
- **AND** Agent MUST 建立逐项视觉对照表，记录附件/截图编号、页面/状态、对照对象、期望表现、实际表现、偏差项、检查方式、处置结论和证据入口
- **AND** Agent MUST 在完成对照前不得开始修改业务实现

#### Scenario: 附件证据不足时阻断 UI 返修

- **WHEN** 附件截图缺少页面路由、视口、主题、关键交互状态、期望截图或实际截图，导致无法确认偏差
- **THEN** Agent MUST 输出人工补证步骤
- **AND** Agent MUST 标明需要返回的字段、脱敏要求和可接受证据格式
- **AND** Agent MUST NOT 将偏差根因标记为 confirmed

#### Scenario: UI 返修后复验对照结果

- **WHEN** Agent 完成 UI 返修
- **THEN** Agent MUST 将相关旧截图标记为 stale
- **AND** Agent MUST 重新执行 1440px 或受影响视口的视觉验收
- **AND** Agent MUST 在 Change `trace.md`、`tasks.md` 验收返修记录或等价验收证据中记录对照表复验结果

### Requirement: 目录与临时证据治理

系统 MUST 明确区分正式项目目录、Git 忽略的本地临时目录和可归档的验收证据目录，避免临时视觉证据阻断目录结构校验或误入长期文档。

#### Scenario: 本地视觉证据临时目录被 ignore

- **WHEN** Agent 或开发者在 UI 验收中生成截图、computed style JSON 或视觉对照中间产物
- **THEN** 这些临时产物 MAY 写入被 `.gitignore` 覆盖的 `tmp/visual-evidence/`
- **AND** 根目录 `tmp/` MUST NOT 被视为正式项目顶层目录
- **AND** 目录结构校验 MUST NOT 因被 ignore 的根目录 `tmp/` 存在而失败

#### Scenario: 长期视觉证据必须沉淀到 Change

- **WHEN** 视觉证据需要支撑 Change 验收、Issue 验收或归档闭环
- **THEN** 关键证据 MUST 转存到对应 `openspec/changes/<change-id>/evidence/` 或写入脱敏后的证据摘要
- **AND** `/opsx-archive` MUST NOT 只依赖 `tmp/visual-evidence/` 作为唯一证据入口
- **AND** 证据 MUST NOT 包含真实客户数据、密钥、访问令牌、Cookie、Authorization header、真实 `.env`、未脱敏日志或个人信息

### Requirement: 引导式用户反馈契约

系统 MUST 在 Agent 命令需要用户选择、确认、补充信息或处理阻塞时，优先使用原生交互卡片组织问题；当客户端或工具层不支持原生交互卡片时，必须降级为文本结构化选项，并保持结构化选项、推荐项和可补充说明入口。

#### Scenario: 交互卡片顶部说明避免重复

- **WHEN** Agent 使用原生交互卡片向用户收集选择、确认或补充信息
- **THEN** 卡片顶部 MUST 只保留一处主说明来承载流程背景或决策意图
- **AND** 副标题、hint、description 或说明正文 MUST NOT 重复承载同一流程信息
- **AND** 其他字段 SHOULD 只提供互补约束、选项差异或补充说明入口

#### Scenario: 文本降级输出保持紧凑

- **WHEN** 原生交互卡片不可用，Agent 降级为文本结构化选项
- **THEN** Agent MUST 保留结构化选项、推荐项和可补充说明
- **AND** Agent SHOULD 避免在标题、说明和提示语中重复表达同一流程信息

### Requirement: Harness 治理资产学习应用

系统 MUST 在通过 `/spec-study apply` 应用外部 Harness 学习成果时，以 MoonBox 当前 OpenSpec、REQ/BUG、Sprint、Workflow Sync 和 `.agents/skills/` 体系为事实源，转写可迁移治理能力，不得照搬外部目录结构或与本项目事实源冲突的自动化。

#### Scenario: 学习成果转写为本项目治理规则

- **WHEN** 外部 Harness 的治理能力被确认采纳
- **THEN** Agent MUST 将其改写为适配 MoonBox 的规则、文档、脚本说明、Skill 或 active Change 内容
- **AND** Agent MUST NOT 恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/` 等非本项目入口目录
- **AND** Agent MUST NOT 修改业务 `src/` 或 `openspec/specs/` 正式规格

#### Scenario: 学习报告承载应用结果

- **WHEN** `/spec-study apply` 完成治理资产应用
- **THEN** Agent MUST 在 `docs/spec-logs/` 写入或更新一份 `YYYYMMDDhhmmss-study-xxx.md` 学习报告
- **AND** 同一次学习应用流程 MUST NOT 额外生成内容重复的 `governance` 日志
- **AND** `docs/spec-logs/CHANGELOG.md` MUST 将该学习报告作为目录级索引条目登记

### Requirement: 发布产物可复核记录

系统 MUST 在发布、镜像或公开站点构建证据中保留可复核记录，使发布确认能够追溯到明确输入、产物和校验结果。

#### Scenario: 发布确认基于已验证产物

- **WHEN** 发布流程使用构建产物、镜像包、公开文档站投影或外部构建证据作为发布依据
- **THEN** 发布对象或关联 manifest MUST 记录版本、来源范围、输入摘要、产物位置或摘要、生成时间、校验命令和校验结果
- **AND** 发布写入动作 MUST 基于已验证产物或经批准的外部证据
- **AND** 输入漂移、manifest 过期或校验缺失时 MUST 阻断发布确认

### Requirement: 慢测试分区与调度治理

系统 MUST 允许慢测试、覆盖率或浏览器验收按稳定分区调度，但调度方式必须可复核、可复现并能保留失败摘要。

#### Scenario: 慢测试使用分区或并行池

- **WHEN** 测试命令为了降低耗时而使用分区、worker 池或串并行混合调度
- **THEN** 测试规则 MUST 说明分区数量、worker 来源、串行前置用例、失败停止策略和输出摘要要求
- **AND** 高风险互斥用例 SHOULD 串行运行后再进入并行池
- **AND** 失败输出 MUST 保留失败分区、命令、用例和关键错误摘要

### Requirement: 文档事实唯一归属

系统 MUST 为长期治理文档维护事实唯一归属，避免同一规则、状态、验收或脚本语义在多个文档中各自展开并发生漂移。

#### Scenario: 长期文档更新前确认事实源

- **WHEN** Agent 新增或修改长期文档中的规则、流程、状态、验收或脚本语义
- **THEN** Agent MUST 先确认该事实的唯一归属文档
- **AND** 其他文档 SHOULD 使用摘要和链接引用该事实源
- **AND** 不得在多个长期文档中复制同一规则的完整说明

### Requirement: 最小相关验证

系统 MUST 按变更影响面选择能够证明风险被覆盖的最小相关验证组合，并在无法覆盖时说明残余风险。

#### Scenario: 治理变更选择验证

- **WHEN** Change 只修改治理规则、Skill、文档或校验脚本
- **THEN** Agent MUST 优先运行对应治理校验、目标 OpenSpec validate、Sprint scope 和 Workflow Sync
- **AND** 业务 API、数据库、Web、管理端或客户端测试 MAY 标记为不适用
- **AND** 不适用原因 MUST 写入学习报告、治理日志、trace 或最终回复

### Requirement: REQ Review 默认正向评审路径

系统 MUST 将 `/req-review <REQ-full-id>` 作为需求评审的默认正向通过命令，并保留显式反向结果和治理收尾。

#### Scenario: 默认调用 req-review 评审通过

- **WHEN** 用户执行 `/req-review REQ-xxxx-slug`
- **AND** 目标需求满足评审前置条件且评审清单无阻断项
- **THEN** 系统必须将本次评审结果记录为 `approved`
- **AND** 系统必须写入或更新 `review.md`
- **AND** 系统必须同步 `trace.md` 与 `requirement.md` 的主状态
- **AND** 系统必须在 Workflow Sync 前将需求目录从 `plan/` 迁移到 `review/`
- **AND** 系统必须刷新 `issues/requirements/CHANGELOG.md` 当前态看板行
- **AND** 系统必须输出下一步 `/sprint-propose --req REQ-xxxx-slug`

#### Scenario: 显式反向评审结果

- **WHEN** 用户执行 `/req-review REQ-xxxx-slug --reject` 或 `/req-review REQ-xxxx-slug --defer`
- **THEN** 系统必须记录对应的 `rejected` 或 `deferred` 结果
- **AND** 系统不得将需求目录迁入 `review/`
- **AND** 系统必须刷新 trace、registry 和当前态看板

#### Scenario: 评审存在阻断风险

- **WHEN** 目标需求缺少评审必需文档、产品数据采集与链路观测声明、验收项或关键风险判断
- **THEN** 系统必须在通过前输出引导式反馈或阻断摘要
- **AND** 系统不得因为无 flag 默认语义而静默批准不满足门禁的需求

#### Scenario: req-review 收尾同步

- **WHEN** `req-review` 主操作完成且 Workflow Sync 成功
- **THEN** 系统必须运行 AI Usage Post-command Hook 或报告不可用原因
- **AND** 成功路径只输出 compact 摘要字段
- **AND** 最终回复必须包含下一步、待用户决策/处理和执行链路复盘

### Requirement: UI 参考稿复刻动作按钮矩阵

系统 MUST 在参考稿复刻类 UI Change 的实现前，为会触发弹窗、抽屉、Popover、确认框、Action Modal、AI 面板或内联展开区域的动作按钮建立矩阵，并以该矩阵驱动组件族实现和验收。

#### Scenario: 实现前建立动作按钮矩阵

- **WHEN** UI Change 引用附件 HTML、截图、标注图、既有页面或参考稿
- **AND** 复刻范围包含动作按钮、卡片 footer、FAB、工具栏动作或阶段动作
- **THEN** Agent MUST 在实现前建立“动作按钮 → modal 类型 → selector → 状态 → 验收证据”矩阵
- **AND** 矩阵 MUST 记录参考 selector、目标 selector、组件族、交互状态、验收证据和处置结论
- **AND** 缺少矩阵时不得将相关 UI 实现任务标记完成

#### Scenario: 同一动作族一次性实现组件族

- **WHEN** 多个动作按钮共享相同 modal 类型、视觉等级、状态模型、关闭路径或提交反馈
- **THEN** Agent MUST 将它们归入同一动作族
- **AND** Agent MUST 一次性设计、实现和验收按钮与 modal 组件族
- **AND** Agent MUST 覆盖 default、hover、focus、active、disabled、loading、open、submitted、error 和权限隐藏等适用状态
- **AND** Agent MUST NOT 将同一动作族拆成逐按钮问答返修，除非矩阵记录明确例外原因

#### Scenario: 返修反馈先回补动作族矩阵

- **WHEN** UI 返修反馈指出某个按钮、modal、Action Modal 或 AI 面板不符合参考稿
- **THEN** Agent MUST 先判断该反馈是否属于更大的动作族
- **AND** 若属于同一动作族，Agent MUST 更新矩阵中相关按钮、modal 类型、selector、状态和证据入口
- **AND** Agent MUST 基于更新后的组件族合同返修，而不是只对单个按钮做孤立修改

#### Scenario: 归档前复核动作按钮矩阵

- **WHEN** 参考稿复刻类 UI Change 准备归档
- **THEN** Agent MUST 复核动作按钮矩阵、selector 映射、computed style 采样、截图证据、非目标保留和最终实现记录一致
- **AND** 若矩阵缺少已实现动作或证据 stale，归档必须阻断

### Requirement: Workflow Sync 主状态字段解析边界

系统 MUST 在 Workflow Sync 读取 Markdown Frontmatter 主状态时，只将顶层 `status` 作为 Issue、Change 或 Sprint 主状态事实源，不得把嵌套声明对象中的同名字段提升为主状态。

#### Scenario: 嵌套观测声明状态不覆盖主状态

- **GIVEN** Issue 或 Change 文档 Frontmatter 同时包含顶层主状态和嵌套 `product_data_collection_observability` 声明状态
- **WHEN** Workflow Sync 读取该文档并推导主状态
- **THEN** 主状态必须解析为 `in_sprint`
- **AND** 嵌套 `product_data_collection_observability.status` 只能作为产品数据采集与链路观测声明状态使用
- **AND** Workflow Sync 不得因为嵌套状态值将 Issue、Change 或 Sprint 派生状态改为 `not_applicable`

#### Scenario: 轻量 Frontmatter 解析只读取顶层键

- **WHEN** Workflow Sync 使用轻量 Frontmatter 解析器读取 `status`、`title`、`priority`、`severity` 或 `updated_at`
- **THEN** 解析器必须忽略缩进字段
- **AND** 结构化嵌套对象应由结构化 YAML 解析路径读取

