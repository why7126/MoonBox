# agent-workflow-tooling Specification

## Purpose
定义 MoonBox Agent 工作流治理命令、跨项目学习、规范优化和原型驱动 UI 开发门禁，确保需求、Sprint、OpenSpec、实现、验收与归档之间保持可追溯、可验证和中文优先的协作规则。
## Requirements
### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。同一次 `/spec-study` 学习应用流程 MUST 只生成一份正式 `study` 报告，且持久化学习对象时 MUST 使用脱敏项目标识，不得记录本机绝对路径、系统用户名或用户主目录。跨项目学习应用命令执行顺序时，系统 MUST 产出可复用的命令顺序规则，并避免复制学习对象业务专属流程。

#### Scenario: 应用治理命令输出契约学习结果

- **WHEN** 用户确认应用外部 Harness 的命令输出契约治理经验
- **THEN** 系统 MUST 将输出契约改写为 MoonBox 技能、规则和校验脚本中的卫生约束
- **AND** 系统 MUST 校验命令技能不得保留易被原样输出的尖括号占位模板
- **AND** 系统 MUST 校验用户可见示例不得泄漏 `MUST`、`SHOULD` 或契约章节名等规范语气
- **AND** 系统 MUST NOT 复制学习对象业务专属命令或示例数据

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

#### Scenario: Issue 归档迁移后刷新当前态路径

- **WHEN** `promote-issues-for-archive.py` 成功将 REQ 或 BUG 目录从 `review/` 迁入 `archive/`
- **THEN** 系统 SHALL 在同一次 promote 命令内刷新对应 `_registry.yaml` 条目的 `lifecycle_stage` 与 `path`
- **AND** 系统 SHALL 刷新对应 `CHANGELOG.md` 当前态行的阶段、事实源路径与下一步
- **AND** 成功路径不应要求额外运行第二次 Workflow Sync 才能消除 `review/` 路径残留

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

### Requirement: Sprint AI Usage 矩阵语义

MoonBox MUST 在 Sprint AI Usage 复盘矩阵中区分真实数值 `0` 与未观测 workflow 阶段，避免将采集缺口误读为真实零成本。MoonBox MUST 通过本地 Codex session JSONL 生成脱敏 AI Usage 派生事实，并在普通 workflow hook 中优先尝试本地 session 自动发现。

#### Scenario: 未观测 workflow 阶段显示为短横线

- **WHEN** Sprint AI Usage 矩阵中某个对象和 workflow 阶段没有匹配 command run
- **THEN** 数据层 MUST 将该单元标记为 `unknown`
- **AND** Markdown 复盘输出 MUST 将该单元渲染为 `-`
- **AND** 已观测但 token 或调用次数为零的单元 MUST 保持数字 `0`

#### Scenario: 普通 workflow hook 自动发现本地 session

- **WHEN** workflow 命令完成同步并运行 AI Usage post-command hook
- **AND** 操作者未显式提供 `--session-jsonl`
- **THEN** 系统 MUST 依次检查 session 环境变量、`AI_USAGE_SESSIONS_DIR` 和默认本地 Codex sessions 目录 `~/.codex/sessions`
- **AND** 系统 MUST 使用 workflow event、REQ/BUG、Change、Sprint、release 或 slash-command 词项匹配近期 JSONL
- **AND** 自动发现失败、候选缺少 `token_count` 或覆盖不足时，系统 MUST 输出 unavailable 或 estimated fallback 与推荐动作
- **AND** 系统 MUST NOT 持久化 raw session JSONL、prompt、system/developer 指令、工具输出正文、密钥、真实 `.env` 内容或本机绝对路径

#### Scenario: 历史回填使用显式 session 和 manual map

- **WHEN** 操作者需要对历史 workflow 命令做 AI Usage 回填或审计
- **THEN** 系统 MUST 要求显式 session JSONL 输入
- **AND** 当历史 turn 无法自动归因到 REQ/BUG、Change、Sprint 或 workflow event 时，系统 SHOULD 支持使用 manual map 按 turn hash 补齐归因
- **AND** 系统 MUST NOT 将普通自动发现结果作为历史回填的唯一事实源

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

### Requirement: UI 参考稿复刻治理

MoonBox SHALL 对明确引用附件 HTML、截图、标注图、既有页面或参考稿并要求“一对一复刻”“全面贴近”“保持一致”的 UI Change 建立 UI Reference Replication Contract。该 Contract SHALL 在实现前完成参考稿反向工程、组件级视觉契约、selector 映射、computed style 采样清单、分批实现计划和验收门禁，避免 UI 复刻退化为逐元素问答返修。

#### Scenario: Explore 阶段反向工程参考稿

- **WHEN** 用户在 `/explore` 中要求分析当前实现与附件、HTML、截图或既有页面的一致性
- **THEN** 系统 SHALL 只读建立参考稿反向工程摘要
- **AND** 摘要 SHALL 区分一对一复刻、风格迁移或局部一致
- **AND** 摘要 SHALL 输出组件差异、selector 候选、computed style 采样候选、风险点和后续治理入口
- **AND** 系统 SHALL NOT 直接修改业务实现

#### Scenario: REQ 与 OpenSpec 承接复刻契约

- **WHEN** 一个 UI REQ 或 Change 明确要求对齐参考稿
- **THEN** `/req-complete` SHALL 在需求验收资料中记录参考事实源、保真模式、组件清单和关键验收点
- **AND** `/req-opsx` SHALL 在 Change `design.md` 写入 UI Reference Replication Contract
- **AND** Change `tasks.md` SHALL 将参考稿反向工程、selector 映射、computed style 采样和分批验收列为可跟踪任务

#### Scenario: Apply 和 Modify 执行分批验收

- **WHEN** `/opsx-apply` 或 `/opsx-modify` 实施参考稿复刻 UI Change
- **THEN** 系统 SHALL 按组件批次推进，不得仅用整体观感判断完成
- **AND** 每批 SHALL 记录目标 selector、关键视觉属性、截图或 computed style 证据、差异结论和非目标确认
- **AND** 若验收反馈暴露 Contract 缺口，系统 SHALL 先补齐 Contract，再继续返修

#### Scenario: Archive 阶段阻断证据缺失

- **WHEN** 参考稿复刻 UI Change 准备归档
- **THEN** 系统 SHALL 复核 UI Reference Replication Contract、最终截图、computed style 采样、selector 映射、REQ 验收资料和 Change 证据一致
- **AND** 若缺少关键组件证据、存在 stale 证据或非目标误改未解释，系统 SHALL 阻断归档

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

### Requirement: Workflow Sync 同步当前状态代码块

Workflow Sync MUST 在同步 Issue `trace.md` 时维护正文 `## 当前状态` 章节内的 fenced `yaml` 当前态快照，使其 `openspec_changes` 与 `next` 字段和派生事实源一致。

#### Scenario: 同步当前状态代码块的 Change 状态和下一步

- **GIVEN** Issue `trace.md` 的 `## 当前状态` 章节包含 fenced `yaml` 代码块
- **AND** 该代码块包含 `openspec_changes` 或 `next`
- **WHEN** Workflow Sync 根据目标 Issue、Change 状态和 Sprint scope 刷新该 trace
- **THEN** 系统 MUST 同步该代码块中的 `openspec_changes[].status`
- **AND** 系统 MUST 同步该代码块中的 `next`
- **AND** `next` MUST 继续遵守 REQ/BUG 链路身份参数规则

#### Scenario: 当前状态代码块同步范围受限

- **GIVEN** Issue `trace.md` 同时包含 Readiness、验收结果、历史示例或其他 fenced `yaml` 代码块
- **WHEN** Workflow Sync 刷新正文当前态快照
- **THEN** 系统 MUST 只处理 `## 当前状态` 章节内首个 fenced `yaml` 代码块
- **AND** 系统 MUST NOT 改写其他章节的 fenced `yaml` 示例或验收语义块

#### Scenario: 兼容旧式 scalar openspec_changes

- **GIVEN** `## 当前状态` fenced `yaml` 中的 `openspec_changes` 使用旧式 scalar 条目
- **WHEN** Workflow Sync 同步对应 Change 状态
- **THEN** 系统 MUST 将目标条目升级为包含 `change_id` 与 `status` 的结构化条目
- **AND** 系统 MUST 保留后续 Workflow Sync 可继续更新的结构

### Requirement: OpenSpec 中文优先语言校验

MoonBox MUST 校验 OpenSpec Change 文档的标题、任务项和业务叙述中文优先。校验可以按全部 active Change 执行，也可以按一个或多个指定 Change 聚焦执行；聚焦模式只用目标 Change 决定退出码，非目标残留通过分离报告呈现。

#### Scenario: req-opsx 与 bug-opsx 中文化 CLI 模板标题

- **WHEN** `/req-opsx <REQ-full-id>` 或 `/bug-opsx <BUG-full-id>` 使用 OpenSpec CLI `instructions` 或 template 生成 Change 文档
- **THEN** 系统 MUST 将 `proposal.md`、`design.md` 和 `tasks.md` 的英文脚手架标题替换为项目中文标题
- **AND** `Why` MUST 写为 `背景`
- **AND** `What Changes` MUST 写为 `变更内容`
- **AND** `Capabilities` MUST 写为 `能力影响`
- **AND** `Impact` MUST 写为 `影响范围`
- **AND** `Implementation`、`Testing` 和 `Documentation` MUST 写为中文任务标题
- **AND** 系统 MUST NOT 将 CLI template 中的 HTML 注释、尖括号占位符或英文说明原样写入最终 Change 文档
- **AND** OpenSpec 关键字、命令、路径、API 字段、代码标识和 capability ID MAY 保留英文

### Requirement: OpenSpec 校验总入口聚焦执行

MoonBox MUST 提供 OpenSpec 校验总入口脚本，用于串行运行当前 Change 常用 OpenSpec 文档门禁。总入口 MUST 支持按 Change ID 聚焦执行，并在聚焦模式下运行当前 Change 中文优先校验与 `openspec validate` 结构校验。

#### Scenario: 总入口按 Change 聚焦校验

- **WHEN** 系统运行 `bash scripts/validate-openspec.sh --change <change-id> --residual-report`
- **THEN** 脚本 MUST 只用目标 Change 作为当前中文优先校验范围
- **AND** 脚本 MUST 运行 `openspec validate <change-id>`
- **AND** 非当前 Change 的中文残留 MUST NOT 改变当前 Change 的退出码

#### Scenario: 总入口保持默认全局校验

- **WHEN** 系统运行 `bash scripts/validate-openspec.sh`
- **THEN** 脚本 MUST 运行目录结构校验
- **AND** 脚本 MUST 运行默认全量 active Change 中文优先校验

#### Scenario: 总入口聚焦归档 Change

- **WHEN** 系统运行 `bash scripts/validate-openspec.sh --include-archive --change <change-id> --residual-report`
- **AND** 目标 Change 已位于 `openspec/archive/`
- **THEN** 脚本 MUST 校验目标归档 Change 的中文优先文档
- **AND** 脚本 MUST 校验归档后已合并的正式规格结构

#### Scenario: bug-opsx 生成后自动运行聚焦校验

- **WHEN** `/bug-opsx <BUG-full-id>` 成功生成或确认当前 OpenSpec Change
- **THEN** 系统 MUST 运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`
- **AND** 当前 Change 的中文优先失败 MUST 阻断本次 `/bug-opsx` 完成
- **AND** 其他 active Change 的中文残留 MUST 以全仓残留分离报告呈现
- **AND** 其他 active Change 的残留 MUST NOT 作为当前 BUG 链路的失败结论

### Requirement: Change 执行事实

MoonBox MUST 使用 Change trace frontmatter 的 `execution.schema_version=1` 保存 OpenSpec Change 执行事实。`execution` MUST 包含 `schema_version`、`started_at`、`completed_at` 和 `last_event` 字段。`/req-opsx` 创建 Change 时 MUST 写入 schema v1 初始块，后续 `opsx.start` 与 `opsx.apply` 由 Workflow Sync 维护实际启动、完成和最后事件。

#### Scenario: req-opsx 创建 Change trace 时固化 execution schema v1

- **WHEN** 系统通过 `/req-opsx <REQ-full-id>` 创建或补齐 `openspec/changes/<change-id>/trace.md`
- **THEN** trace frontmatter MUST 包含 `execution.schema_version: 1`
- **AND** `execution.started_at` MUST 初始为 `null`
- **AND** `execution.completed_at` MUST 初始为 `null`
- **AND** `execution.last_event` MUST 初始为 `req.opsx`
- **AND** 系统 MUST NOT 在 `/req-opsx` 创建阶段伪造实施启动或完成时间

#### Scenario: Workflow Sync 维护执行事实

- **WHEN** 系统执行 `opsx.start` 或 `opsx.apply` Workflow Sync 事件
- **THEN** Workflow Sync MUST 复用 `execution.schema_version: 1`
- **AND** `opsx.start` MUST 写入真实 `started_at`
- **AND** `opsx.apply` MUST 写入真实 `completed_at`
- **AND** 旧 trace 缺少 `execution` 时 MAY 兼容补齐 schema v1，但不得批量重写历史终态

### Requirement: Capture 创建前重复相似 Issue 检查

`/capture`、`/req-capture` 和 `/bug-capture` MUST 在创建新 REQ/BUG 前执行重复/相似 Issue 检查。系统 MUST 先读取对应类型的 `CHANGELOG.md` 与 `_registry.yaml` 建立候选范围；候选不清晰时，MUST 只读取疑似候选目录中 `capture.md` 与 `trace.md` 的标题、Frontmatter、摘要、状态、关联 Sprint/Change 和下一步必要片段。系统 MUST NOT 为判重全量读取无关 Issue 正文、历史归档大目录或生成物。

#### Scenario: req-capture 识别已有需求补充

- **GIVEN** 用户输入的需求与现有 REQ 在业务域、目标用户、交付能力或验收闭环上高度相似
- **WHEN** 系统执行 `/req-capture`
- **THEN** 系统 MUST 在分配新 REQ ID 前输出候选 REQ、相似原因、当前状态、事实源路径和处理选项
- **AND** 系统 MUST 默认推荐关联或更新原 REQ，必要时使用 `parent_requirement`
- **AND** 系统 MUST 只有在用户确认非重复或候选仅弱相关后才创建新的 peer REQ

#### Scenario: bug-capture 识别已有缺陷补充

- **GIVEN** 用户输入的缺陷与现有 BUG 在页面、现象、触发条件、根因假设或修复面上高度相似
- **WHEN** 系统执行 `/bug-capture`
- **THEN** 系统 MUST 在分配新 BUG ID 前输出候选 BUG、相似原因、当前状态、事实源路径和处理选项
- **AND** 系统 MUST 默认推荐关联或更新原 BUG，必要时填写 `related_bug` 或 `related_requirement`
- **AND** 系统 MUST 只有在用户确认非重复或候选仅弱相关后才创建新的 peer BUG

#### Scenario: capture 混合输入分别检查

- **GIVEN** 用户通过 `/capture` 输入混合需求与缺陷
- **WHEN** 系统完成分类和拆分
- **THEN** 系统 MUST 对需求条目按 REQ 候选执行重复/相似检查
- **AND** 系统 MUST 对缺陷条目按 BUG 候选执行重复/相似检查
- **AND** 疑似重复条目 MUST 先完成用户决策，非重复条目 MAY 继续按正常 capture 流程创建

### Requirement: Workflow Sync sprint.propose 同步聚焦 Issue 主文档

Workflow Sync MUST 在 `sprint.propose` 聚焦 REQ 或 BUG 成功同步时，将对应 Issue 主文档的 `status` 镜像为当前派生主状态。REQ 主文档为 `requirement.md`，BUG 主文档为 `bug.md`；同步范围 MUST 限定为命令传入的聚焦 Issue，不得批量改写无关 Issue 子文档。

#### Scenario: BUG 纳入 Sprint 后同步 bug.md 主状态

- **GIVEN** 已评审 BUG 通过 `/sprint-propose --bug <BUG-full-id>` 纳入 Sprint
- **AND** Workflow Sync 将该 BUG 派生为 `in_sprint`
- **WHEN** Workflow Sync 执行 `--event sprint.propose --bug <BUG-full-id>`
- **THEN** 系统 MUST 将该 BUG 的 `bug.md` Frontmatter `status` 同步为 `in_sprint`
- **AND** 系统 MUST 保持未聚焦 BUG 的主文档状态不被本次同步改写

#### Scenario: REQ 纳入 Sprint 后同步 requirement.md 主状态

- **GIVEN** 已评审 REQ 通过 `/sprint-propose --req <REQ-full-id>` 纳入 Sprint
- **AND** Workflow Sync 将该 REQ 派生为 `in_sprint`
- **WHEN** Workflow Sync 执行 `--event sprint.propose --req <REQ-full-id>`
- **THEN** 系统 MUST 将该 REQ 的 `requirement.md` Frontmatter `status` 同步为 `in_sprint`
- **AND** 系统 MUST 保持未聚焦 REQ 的主文档状态不被本次同步改写

