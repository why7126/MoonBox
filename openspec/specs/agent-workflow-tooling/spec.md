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
系统 SHALL 对带 `prototype/` 的 UI 页面建立从需求完善、OpenSpec 转换、实现、返修到归档的连续门禁，确保原型拆解、UI Contract、UI Skeleton 首轮确认、1440px 与关键交互视觉验收、computed style 验收、Mock/API 边界声明、图标文案一致性检查和 REQ 文档最终一致性检查均被记录并通过。

#### Scenario: 需求完善拆解 prototype
- **GIVEN** 一个 UI REQ 存在 `prototype/web/` 或等价页面原型目录
- **WHEN** 执行 `/req-complete <REQ-full-id>`
- **THEN** 系统 SHALL 在需求文档中记录原型页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点
- **AND** 系统 SHALL 将可测试验收项写入 `acceptance.md` 并在 `trace.md` 记录 `prototype_refs`

#### Scenario: OpenSpec 承接 UI Contract 和 UI Skeleton
- **GIVEN** 一个带 prototype 的 REQ 已进入 `/req-opsx`
- **WHEN** 系统生成 active Change
- **THEN** Change `design.md` SHALL 包含 UI Contract，声明事实源优先级、页面入口、信息架构、视觉 token、交互状态、图标文案、Mock/API 边界、权限规则和一致性参照
- **AND** Change `design.md` SHALL 包含 UI Skeleton 章节
- **AND** Change `tasks.md` SHALL 包含先完成 UI Contract 与 UI Skeleton 再实现细节的独立任务
- **AND** Change SHALL 记录 prototype 与 acceptance 的冲突处理结论

#### Scenario: 实现阶段执行视觉和样式验收
- **GIVEN** 一个带 prototype 的 UI Change 正在 `/opsx-apply` 或 `/opsx-modify`
- **WHEN** 相关 UI 任务准备标记完成
- **THEN** 系统 SHALL 先在 1440px 桌面视口完成视觉验收
- **AND** 系统 SHALL 对关键交互记录截图或等价证据
- **AND** 系统 SHALL 对原型敏感或曾返修的视觉点记录 computed style 或等价检查
- **AND** 系统 SHALL 记录 Mock/API 边界、验收命令和结果摘要

#### Scenario: 前后台一致性检查
- **GIVEN** 一个带 prototype 的 UI Change 需要对齐前台、后台或既有页面
- **WHEN** 系统执行 `/req-opsx`、`/opsx-apply` 或 `/opsx-modify`
- **THEN** 系统 SHALL 对品牌区、菜单分组、导航密度、active 态、折叠按钮、用户菜单、浮层层级、字体 token、图标尺寸、hover/click outside、危险色、图标和文案进行 checklist 验收

#### Scenario: 归档前检查 REQ 最终一致性
- **GIVEN** 一个带 prototype 的 UI Change 准备 `/opsx-archive`
- **WHEN** 系统执行归档前文档同步门禁
- **THEN** 系统 SHALL 复核 linked REQ 的 `requirement.md`、`acceptance.md`、`trace.md` 与 Change 设计、实现证据、验收结果一致
- **AND** 若发现验收口径、非目标、UI 行为、Mock/API 边界、computed style、视觉证据或实现差异，系统 SHALL 阻断归档并要求先回填或返修

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

### Requirement: 探索命令保留后续 opsx 链路身份

探索类命令在输出下一步 `/opsx-*` 命令时，MUST 根据上下文识别 Change 是否来源于 REQ 或 BUG；可识别来源时 MUST 使用完整 Issue ID 作为用户可执行命令参数，只有无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

#### Scenario: Explore 识别到 REQ 来源 Change

- **WHEN** `/explore` 或 `/opsx-explore` 基于某个 OpenSpec Change 输出下一步 `/opsx-*` 命令
- **AND** 当前上下文、Change 文档或 Sprint scope 可识别该 Change 来源于完整 `REQ-xxxx-slug`
- **THEN** 下一步命令 MUST 使用该完整 `REQ-xxxx-slug`
- **AND** MUST NOT 使用 `<change-id>` 替代该 REQ 链路身份

#### Scenario: Explore 识别到 BUG 来源 Change

- **WHEN** `/explore` 或 `/opsx-explore` 基于某个 OpenSpec Change 输出下一步 `/opsx-*` 命令
- **AND** 当前上下文、Change 文档或 Sprint scope 可识别该 Change 来源于完整 `BUG-xxxx-slug`
- **THEN** 下一步命令 MUST 使用该完整 `BUG-xxxx-slug`
- **AND** MUST NOT 使用 `<change-id>` 替代该 BUG 链路身份

#### Scenario: Explore 面向纯治理 Change

- **WHEN** `/explore` 或 `/opsx-explore` 输出下一步 `/opsx-*` 命令
- **AND** 已确认该 Change 无 REQ/BUG 来源且属于纯治理 Change
- **THEN** 下一步命令 MAY 使用 `<change-id>`
- **AND** SHOULD 保持 Sprint Inclusion Gate 提示，不得暗示纯治理 Change 可跳过 Sprint

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

### Requirement: 引导式命令用户反馈

Agent 命令在需要用户选择、确认、补充信息或处理阻塞时，MUST 优先采用“结构化选项 + 推荐项 + 可补充说明”的引导式反馈格式，每轮只聚焦少量关键决策，并根据用户答案动态收敛。

#### Scenario: 需要用户选择范围或策略

- **WHEN** 命令需要用户在范围、优先级、策略、验收口径、发布确认或阻塞处理之间做选择
- **THEN** 输出 MUST 包含 1-3 个关键决策点
- **AND** 每个决策点 SHOULD 包含 2-4 个互斥选项
- **AND** 至少一个选项 MUST 标注“推荐”并说明推荐理由
- **AND** SHOULD 提供“可补充说明”入口，允许用户用自然语言覆盖或补充选项

#### Scenario: 用户已回答部分决策

- **WHEN** 用户已经选择或确认某个决策点
- **THEN** 后续命令输出 MUST 承接该答案
- **AND** MUST 只追问剩余阻塞点或新增风险点
- **AND** MUST NOT 重复询问已确认事项

#### Scenario: 成功路径无需用户反馈

- **WHEN** 命令已完成且不存在需要用户选择、确认、补充或处理的事项
- **THEN** 输出 SHOULD 保持紧凑
- **AND** MUST NOT 为了套用格式而追加无意义问卷

### Requirement: spec-study 日志优先学习顺序

`/spec-study` 在学习对象存在 `docs/spec-logs/CHANGELOG.md` 时，MUST 优先从日志索引入手理解治理演进，再读取相关单次日志，并横向校验真实治理资产；日志不得替代当前资产、OpenSpec Change、Sprint 四件套或正式规格事实源。

#### Scenario: 学习对象存在 spec-logs 变更历史

- **WHEN** `/spec-study` 学习对象包含 `docs/spec-logs/CHANGELOG.md`
- **THEN** Phase 1 MUST 先读取该文件作为治理演进入口地图
- **AND** MUST 根据主题读取相关 `YYYYMMDDhhmmss-study-xxx.md` 或 `YYYYMMDDhhmmss-governance-xxx.md`
- **AND** MUST 再回到 `AGENTS.md`、`rules/`、`docs/`、Agent 目录、`scripts/`、部署与环境示例等真实资产做横向校验
- **AND** SHOULD 只在证据不足或需要确认实际执行语义时读取必要代码、脚本或配置片段

#### Scenario: 日志与真实资产存在漂移

- **WHEN** `CHANGELOG.md` 或单次日志描述与当前治理资产不一致
- **THEN** `/spec-study` MUST 在候选学习内容中标注漂移风险
- **AND** MUST 以当前真实资产和正式规格作为最终事实依据
- **AND** SHOULD 将日志内容作为历史背景或设计意图参考

### Requirement: 证据化根因分析治理
MoonBox SHALL 在问题探索、BUG 完善、验收返修和 BUG 来源 OpenSpec 实现前执行证据化根因分析门禁。系统 SHALL 区分 `unknown`、`hypothesis`、`probable` 和 `confirmed` 根因状态；只有存在可复核证据链时，才能将根因标记为 `confirmed`。

#### Scenario: 探索阶段不得猜测定根因
- **WHEN** `/explore` 或 `/bug-explore` 面对问题、异常、效果不如预期或疑似 BUG
- **AND** 当前证据不足以支撑根因
- **THEN** 系统 SHALL 将根因标记为 `unknown`、`hypothesis` 或 `probable`
- **AND** 系统 SHALL NOT 输出已确认根因
- **AND** 系统 SHALL 输出人工补证清单、操作步骤、返回字段、脱敏要求和返回格式

#### Scenario: 人工补证后再确认根因
- **WHEN** 用户按补证步骤返回日志、截图、Network、Console、测试失败、数据库样本、配置差异或其他证据
- **THEN** 系统 SHALL 先复核证据是否能支撑根因
- **AND** 证据充分时 SHALL 将根因状态提升为 `confirmed`
- **AND** 证据仍不足时 SHALL 继续输出剩余证据缺口和下一轮补证步骤

#### Scenario: BUG 完善要求 confirmed evidence
- **WHEN** `/bug-complete <BUG-full-id>` 生成或更新 `root-cause.md`
- **THEN** `root-cause.md` SHALL 包含根因状态、现象、证据链、已排除假设、已确认根因、修复方向和验证闭环
- **AND** 若根因状态不是 `confirmed` 或缺少证据链，系统 SHALL NOT 将 BUG 推进到 `pending_review`

#### Scenario: BUG 来源实现前校验证据链
- **WHEN** `/opsx-apply <BUG-full-id>` 准备实现 BUG 来源 Change
- **THEN** 系统 SHALL 运行或等价执行 `scripts/validate-root-cause-evidence.py --bug <BUG-full-id>`
- **AND** 校验失败时 SHALL 阻断实现并提示先补证或重新执行 `/bug-complete`

#### Scenario: 验收返修先记录偏差证据
- **WHEN** `/opsx-modify` 处理验收失败、效果不如预期、UI 不一致或运行异常
- **THEN** 系统 SHALL 先记录偏差证据、期望/实际、影响范围和复现条件
- **AND** 若证据不足，系统 SHALL 输出人工补证操作步骤
- **AND** 系统 SHALL NOT 在缺少证据时把修复方向描述为已确认根因

### Requirement: 命令执行复盘 Hook Skill 覆盖

所有 `.agents/skills/` 命令 Skill MUST 保留 Command Execution Review Hook 短引用，指向 `.agents/skills/workflow-sync/SKILL.md` 中央契约，并显式包含「执行链路复盘」「链路状态」「问题证据」「规范优化建议」和「未自动创建 Issue/Change」。

#### Scenario: 命令 Skill 包含短引用

- **GIVEN** 一个 `.agents/skills/<command>/SKILL.md`
- **WHEN** 该文件描述命令最终输出契约
- **THEN** 它 MUST 包含 Command Execution Review Hook 短引用
- **AND** 短引用 MUST 指向 `.agents/skills/workflow-sync/SKILL.md`

#### Scenario: 校验脚本发现漏引用

- **GIVEN** 一个命令 Skill 缺少 Command Execution Review Hook 短引用
- **WHEN** 运行 `python scripts/validate-agent-context-budget.py`
- **THEN** 校验 MUST 失败
- **AND** 输出缺失短引用的文件路径与缺失字段

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

### Requirement: 命令执行复盘 Hook
MoonBox SHALL 在 workflow 命令完成后输出轻量命令执行复盘，反馈本次链路状态、问题证据和规范优化建议。该 Hook SHALL NOT 自动创建 follow-up REQ、BUG 或 Change，除非用户明确授权。

#### Scenario: 成功命令输出轻量复盘
- **WHEN** workflow 命令完成且所有关键门禁通过
- **THEN** 系统 SHALL 输出 `执行链路复盘`
- **AND** 复盘 SHALL 包含链路状态、问题证据和规范优化建议
- **AND** 若未发现问题，系统 SHALL 输出“无明显优化点”或等价简短结论

#### Scenario: Warning 或 blocker 必须引用证据
- **WHEN** 命令执行中出现 warning、blocker、脚本失败、文档漂移、门禁阻断或执行链路不顺
- **THEN** 系统 SHALL 在复盘中引用脚本输出、文件路径、校验报告、日志摘要或用户提供证据
- **AND** 系统 SHALL NOT 在没有证据时猜测流程根因

#### Scenario: Follow-up 只输出建议不自动创建
- **WHEN** 复盘发现可沉淀的规范优化、缺陷或需求线索
- **THEN** 系统 SHALL 输出建议命令，例如 `/spec-opt`、`/bug-capture`、`/req-capture` 或 `/capture`
- **AND** 系统 SHALL 明确未自动创建 follow-up Issue 或 Change
- **AND** 只有用户明确授权时，系统才 MAY 进入对应创建流程

### Requirement: opsx-modify REQ 子文档一致性扫尾检查

MoonBox MUST 在 REQ 来源的 `/opsx-modify` 完成前执行 REQ 子文档一致性扫尾检查，避免只更新 PRD 或单一验收文档而遗漏业务流程、用户故事、`acceptance.md`、`trace.md` 和 `prototype/**` 等事实源。该检查 MUST 按 linked REQ 目录中实际存在的子文档和原型资产逐项判断是否需要同步；无需更新时 MUST 记录理由。

#### Scenario: REQ 来源返修完成前扫尾

- **GIVEN** `/opsx-modify` 目标 Change 来源于完整 `REQ-xxxx-slug`
- **WHEN** 返修实现、Change 文档和验证证据准备进入最终同步
- **THEN** 系统 MUST 定位 linked REQ 目录并检查现有 `requirement.md`、业务流程文档、用户故事文档、`acceptance.md`、`trace.md` 和 `prototype/**`
- **AND** 若返修改变产品行为、UI/交互、验收口径、Mock/API 边界、原型意图或用户故事，系统 MUST 同步更新受影响 REQ 子文档或原型说明
- **AND** 若某项无需更新，系统 MUST 在 Change `tasks.md` 验收返修记录或 Change `trace.md` 中记录无需更新的项目与原因

#### Scenario: 子文档漂移阻断返修完成

- **GIVEN** REQ 子文档一致性扫尾检查发现业务流程、用户故事或 `prototype/**` 与返修后行为不一致
- **WHEN** 该差异仍属于当前 Change 边界
- **THEN** 系统 MUST 先回填对应 REQ 子文档后再完成 `/opsx-modify`
- **AND** 若差异扩大当前 Change 边界，系统 MUST 阻断 `/opsx-modify` 完成并建议新建 REQ、BUG 或 OpenSpec Change

