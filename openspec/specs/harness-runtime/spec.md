---
updated_at: 2026-09-10 09:16:21
---

# harness-runtime Specification

## Purpose
定义 MoonBox Agent 开发治理，包括 UI 返修证据、工作流状态、Apply 连续执行、完成门禁与中断续接，保证实现、验证和归档过程可追溯。
## Requirements
### Requirement: UI 返修附件截图逐项视觉对照

系统 MUST 在 UI 型 `/opsx-modify` 返修前，对验收反馈中的附件截图、标注截图、原型截图或实际截图建立逐项视觉对照表，并以该表作为进入实现返修的前置检查。完整验收返修台账 MUST 优先记录在 Change `acceptance-fixes.md`；`tasks.md` MUST 只保留返修任务勾选、简短摘要和台账链接，`trace.md` MUST 保留返修摘要、证据入口和验证结果。

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
- **AND** Agent MUST 在 Change `acceptance-fixes.md` 中记录完整对照表复验结果
- **AND** Agent MUST 在 `tasks.md` 保留返修任务勾选和台账链接
- **AND** Agent MUST 在 Change `trace.md` 记录台账路径、证据入口和验证摘要

### Requirement: 目录与临时证据治理

系统 MUST 明确区分正式项目目录、Git 忽略的本地临时目录、本地工具缓存目录、本地持久数据目录、运行时控制状态目录和可归档的验收证据目录，避免临时视觉证据、本地工具缓存或运行时控制状态阻断目录结构校验或误入长期文档。

#### Scenario: data 持久存储与 runtime 控制状态分离

- **WHEN** 本地开发、Docker 本地部署、Chat Platform 或治理控制器需要在仓库 `data/` 下写入数据
- **THEN** 本地 SQLite 持久数据库 MUST 归属 `data/sqlite/`
- **AND** 本地 MinIO/S3 对象数据 MUST 归属 `data/s3/`
- **AND** Chat Platform、Governance、Codex 执行器的会话状态、控制状态、工作区、备份和执行器内部状态 MAY 归属 `data/runtime/`
- **AND** `data/runtime/` MUST NOT 作为业务 SQLite 数据库或对象存储数据的 canonical 根目录

#### Scenario: legacy runtime backend 存储目录迁移期可见

- **WHEN** 目录结构校验发现 `data/runtime/backend/sqlite/` 或 `data/runtime/backend/media/`
- **THEN** 校验 SHOULD 输出迁移期 warning
- **AND** warning MUST 指向 `data/sqlite/` 与 `data/s3/` 的 canonical 归属
- **AND** 在完成独立迁移 Change 前，校验 MAY 不阻断当前工作流
- **AND** 迁移动作 MUST NOT 在未停服、未备份、未校验数据库完整性的情况下执行

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

### Requirement: Apply 连续执行与完成门禁
Agent MUST 在已授权 Change 范围内连续实现、验证和同步，不得仅因完成一批任务而等待用户继续；完整细则由命令顺序文档集中维护。

#### Scenario: 可修复自检失败
- **WHEN** 当前 apply 的编译、测试或视觉自检失败且可在授权范围内修复
- **THEN** Agent 在当前 apply 内补证、修复并重跑相关检查，不将自检转为用户必须另发的 modify

#### Scenario: 真实外部阻塞
- **WHEN** 必需权限、关键业务决策或人工证据缺失且无法自主解决
- **THEN** Agent 保留门禁并说明证据、已尝试动作与所需输入，在授权范围内继续不依赖阻塞的工作；用户明确停止时立即停止

#### Scenario: 完整交付
- **WHEN** 所有任务已有完成证据
- **THEN** Agent 核实必要验证、文档同步和串行 Workflow Sync 后才宣布完成，非阻断 AI Usage warning 如实披露

#### Scenario: 中断与恢复
- **WHEN** 执行被中断或上下文被压缩后恢复
- **THEN** Agent 根据 Change、任务、实际文件和验证证据核实进度，从首个可执行剩余任务继续，不重复确认已有授权，不把部分完成标记 applied

### Requirement: Apply停止决策与行为轨迹验收
Agent MUST 在结束apply前判断所有剩余任务的依赖；未完成且仍有可执行任务时持续执行。校验器 MUST 区分合成回归与真实行为证据。
#### Scenario: 测试失败后自行修复
- **WHEN** 范围内测试失败且可自主修复
- **THEN** Agent修复并重验，不结束等待继续
#### Scenario: 用户插话或上下文压缩
- **WHEN** 用户询问进度或运行内发生上下文压缩
- **THEN** Agent承接原目标继续首个可执行任务
#### Scenario: 局部部署依赖缺失
- **WHEN** 部署缺配置但有独立开发任务
- **THEN** Agent询问必要输入并继续独立任务
#### Scenario: 全部任务依赖外部输入
- **WHEN** 无可执行任务且剩余任务均依赖有证据的必要外部输入
- **THEN** Agent报告依赖和恢复动作，允许等待

### Requirement: opsx-modify 返修阶段流转

系统 SHALL 在 `/opsx-modify` 验收返修期间区分 Change canonical status、首次 apply execution facts、返修投影状态和验收状态。返修执行中用户可见阶段 SHALL 展示为研发中；返修完成并通过验证、文档同步和 Workflow Sync 后 SHALL 自动回到验收中。系统 SHALL 保留 Change `applied` 事实和首次 apply 的 `execution.completed_at`，不得用普通 `in_progress` 覆盖首次 apply 完成事实。

#### Scenario: 返修执行中展示研发中

- **GIVEN** Change 已完成 `/opsx-apply` 并处于 `applied`
- **WHEN** Agent 开始执行 `/opsx-modify` 并处理验收反馈
- **THEN** 用户可见阶段 SHALL 展示为研发中
- **AND** Change canonical status SHALL 继续保留 apply 完成事实
- **AND** 首次 apply 的 `execution.completed_at` SHALL NOT 被清空、覆盖或改写为新的普通进行中状态

#### Scenario: 返修完成后回到验收中

- **GIVEN** `/opsx-modify` 的返修任务、验证证据、文档同步和 Workflow Sync 已完成
- **WHEN** 返修结果仍属于原 Change 范围
- **THEN** 用户可见阶段 SHALL 回到验收中
- **AND** linked Issue 的验收入口 SHALL 保持待复验语义
- **AND** 下一步 SHALL 指向复验或 `/opsx-archive`

#### Scenario: 返修不回退 applied 事实

- **GIVEN** Change 已记录首次 apply 的 execution facts
- **WHEN** 返修过程需要表达正在处理
- **THEN** 系统 SHALL 使用返修投影语义表达研发中
- **AND** 系统 SHALL NOT 将 Change canonical status 简单覆盖为普通 `in_progress`
- **AND** 系统 SHALL NOT 伪造新的首次 apply 启动或完成时间

### Requirement: tasks 分类统计口径

MoonBox MUST 在 `tasks.md` 中沉淀可被需求中心稳定识别的研发、测试、人工验收三类任务口径。该口径 MUST 适用于首次 `/opsx-apply` 任务和后续 `/opsx-modify` 验收返修任务。

#### Scenario: 生成可分类任务

- **WHEN** `/req-opsx`、`/bug-opsx` 或等价命令生成 Change `tasks.md`
- **THEN** 任务应按实施任务、回归验证、文档同步和人工验收等稳定章节或显式标记组织
- **AND** 需求中心可将可关闭 checkbox 分类为研发、测试或人工验收
- **AND** 任务正文、证据链接、说明段落和表格正文不得作为卡片进度分母

#### Scenario: 返修任务纳入分类

- **WHEN** `/opsx-modify` 根据验收反馈追加返修任务
- **THEN** 返修实现任务必须进入研发类分母
- **AND** 返修回归测试、视觉证据和校验任务必须进入测试类分母
- **AND** 人工复验、人工确认或 sign-off 任务必须进入人工验收类分母
- **AND** `acceptance-fixes.md` 继续作为完整返修台账事实源，但其表格正文和说明文字不直接计入卡片进度

#### Scenario: 分类口径缺失时提示

- **WHEN** Change `tasks.md` 缺少可识别分类
- **THEN** 需求中心 SHALL 返回待核实或降级提示
- **AND** Agent 在后续修复、返修或归档前 SHOULD 补齐分类口径或记录不适用原因
- **AND** 系统不得通过文档存在性、默认人工验收计数或总 checkbox 完成率误报三类进度完成

### Requirement: 生成文档中文标题与一致性
所有生成 Markdown 文档 SHALL 包含中文 Frontmatter title 与一致的一级标题，覆盖 capture、trace、user-stories、review、requirement、bug、business-flow、acceptance、root-cause、workaround、proposal、design、tasks、spec 及其他生成文档。业务主文档表达业务目标，辅助文档结合业务主题及用途。注册表每条 SHALL 包含中文业务 title。

#### Scenario: 标题生成与注册表同步
- **WHEN** 创建或重新生成文档
- **THEN** 生成非空中文 title 和一致一级标题，允许英文专名，不接受纯类别或模板标题
- **AND** Issue 主文档业务标题同步注册表，不被 Change 业务标题覆盖；保留 OpenSpec 解析关键字

### Requirement: 标题校验阻止无效生成完成
CLI、技能及产品 Agent 生成入口 SHALL 在应用产物或声明完成之前校验标题，失败不得推进工作流。

#### Scenario: 不合法产物
- **WHEN** 产物缺标题、空白、纯英文或ID、模板/类别标题，或字段与一级标题冲突
- **THEN** 返回文件与字段级错误，不应用部分结果、不声明完成、不推进状态；修正后重验

#### Scenario: 历史资料与聚焦校验
- **WHEN** 校验当前 Issue 或 Change 的生成产物
- **THEN** 当前失败阻断完成，无关历史残留单独报告；不批量改写归档
- **AND** 读取历史缺失标题使用受控回退与提示，不阻断整个看板

