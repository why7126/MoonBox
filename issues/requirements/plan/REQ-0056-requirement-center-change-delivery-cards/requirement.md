---
requirement_id: REQ-0056-requirement-center-change-delivery-cards
title: 需求中心交付阶段按 Change 独立成卡
terminal: web-catalog
version: v1
status: pending_review
owner: 产品团队
source: capture.md 与同会话 explore
priority: P1
parent_requirement: REQ-0026-requirement-center-standalone-change-cards
created_at: '2026-10-29 18:34:19'
updated_at: 2026-10-29 18:40:34
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - web_request_wrapper
  - usage_events
  - request_logs
  - task_traces
  reason: 交付卡片身份、任务读写和阶段动作需携带来源 Issue 与明确目标 Change，保持授权及链路关联。
  validation: 计划验证项目/Issue/Change身份在卡片、请求、会话、任务链路中一致，覆盖授权拒绝、直接API调用、请求关联、脱敏及采集失败不阻断；本轮仅生成PRD，尚未执行产品验证。
---

# 需求中心交付阶段按 Change 独立成卡

## 1. 背景与问题

需求中心以 REQ/BUG 聚合多个 Change 时，同一张卡无法同时表达多次交付的阶段、迭代和进度。REQ-0048-chat-isolated-acceptance-orchestration 的已归档子交付 add-isolated-candidate-validation 属于 sprint-015，后续 add-chat-isolated-acceptance-orchestration 在探索取证时属于 sprint-016 研发中。用户截图显示“关联多个 Change，无法确定 tasks.md 来源”，阻断查看进度。

证据依据为同会话用户截图、Issue trace、两次交付 trace，以及 src/backend/app/governance/change_index.py 的 cards 当前项选择与 src/web/src/pages/catalog/RequirementCenterPage.tsx 的 openTasksAt 分支。上述为探索时事实，不保证样本未来始终处于相同状态；后续回归应构建等价固定样本。

父需求 REQ-0026 已交付独立 Change 可见性，并规定关联 Change 留在 Issue 卡内。本需求经用户确认作为其后续子需求，调整交付阶段的卡片组织方式；不重写父需求归档结果，不把旧交付追溯记录改成新模型。P1 初判依据为交付可见性与操作归属受影响，不认定生产紧急事故。

## 2. 目标用户与成功标准

面向产品负责人、研发成员和验收人员。用户能从一张交付卡准确辨认本次交付做什么、属于哪个 Sprint、处于什么阶段、任务与验收进展如何，并直接操作正确的 Change。

成功标准：每个有权查看的有效 Change 在交付看板最多一张卡；任务、验收、筛选、统计和执行上下文均与该 Change 一致；需求整体结果仍可追溯，不因一个子交付完成就宣告全部需求完成。

## 3. 范围与非目标

### 3.1 包含

- 前期 REQ/BUG 卡与交付期 Change 卡的切换和来源追溯。
- 有来源、无来源、多个来源的 Change，以及活动与归档交付。
- 独立阶段、Sprint、文档、任务、验收、估算与统计口径。
- 搜索筛选、刷新恢复、会话入口及阶段操作的明确目标传递。
- 既有权限、不可用反馈、请求观测和桌面/窄屏交互一致性。

### 3.2 不包含

不复制或拆分实际 Issue 文档，不自动创建 Change、分配 Sprint、修改历史状态或补齐缺失估算；不重做整个需求中心视觉体系，不新增跨项目看板，不改变评审、验收、归档授权门禁，不引入新的执行器。本阶段仅 PRD，不生成原型、验收子文档或业务代码。

## 4. 功能要求

### FR-001 卡片对象与切换门槛

收集、完善、评审阶段以 REQ/BUG 为对象。已评审但尚无有效 Change 时保留 Issue 入口，并提示待生成交付方案，不制造空 Change 卡。存在合法且可解析关联的 Change 后，交付区域按 Change 生成卡片，不继续叠加同一 Issue 的聚合交付卡。

切换只影响展示对象，不修改 Issue 生命周期。一个 Issue 仍有未建 Change 的剩余范围时，在来源详情中保留整体状态、未交付范围及后续规划入口；不得因已有 Change 全部完成而自动判定需求完成。全部关联异常、缺失或不可见时保持有权限的 Issue 可发现入口，展示待核实/受限反馈，不从看板静默消失或泄露隐藏对象。

### FR-002 Change 唯一身份与来源

交付卡以项目身份和完整 Change ID 唯一标识，不使用数组位置、标题或来源 Issue ID 作为唯一键。一个 Change 关联多个 REQ/BUG 仍仅一张交付卡；来源标签提供授权范围内的完整身份与详情入口。无来源的合法独立 Change 保留原有能力。

关系先在完整稳定快照中解析，再按既有权限过滤；不可见来源不能被重新解释为“独立 Change”。同 ID 活动/归档记录沿用现有身份优先级与冲突诊断，不生成双卡，不自动修复事实源。来源显示按完整 ID 稳定排序，不代表默认执行来源。

### FR-003 标题、文档与信息层级

以 Change 中文业务标题作为交付标题，显示完整 Change ID、来源 Issue、该 Change 的 Sprint 和阶段。缺少可信业务标题时回退完整 ID 并提示待完善，不使用“Change 1/2”代替身份。

卡片主要文档区只展示该 Change 的文档，来源 Issue 文档通过明确标识的来源入口访问；同名 trace.md、acceptance.md 不混淆。文档权限、版本冲突和只读归档规则保持有效。责任人、优先级/严重度如来自 Issue，应标明来源；多来源冲突时显示分别归属，不随意取首项。

### FR-004 阶段与 Sprint 独立投影

每张 Change 卡根据自身可信状态及既有状态解释规则进入待开发、研发中、验收中、已完成；返修展示沿用既有语义，不覆盖首次 apply 完成事实。未知或冲突状态明确标识，不伪装为已完成。

Sprint 标签与筛选使用该 Change 的归属，历史子交付不继承 Issue 的最新 Sprint。缺失或冲突时显示未确定归属，仍在允许查看的全部范围中可发现。需求整体进度、partial 交付与未交付范围在来源详情表达。

### FR-005 任务进度与读写

研发与测试进度从本卡 Change 的任务来源读取；查看进度定位对应 tasks.md 章节，不再依赖 Issue.current_change 猜测。不存在任务源时显示具体缺口，不回退兄弟 Change。勾选任务以项目、Change、文档及版本绑定提交，保持权限、版本冲突和幂等保护。

切换卡片、筛选、刷新或迟到响应不得把另一 Change 内容覆盖当前抽屉。归档卡不因此获得任务写权限。

### FR-006 两层验收与整体完成

交付卡只显示对应 Change 的验收来源、结果、就绪与待核对状态；Issue acceptance.md 属于需求整体层，不复制其数量作为所有 Change 的验收进度。

未执行、部分通过、失败、阻塞、缺证据和通过需可区分，不能用任务全勾或 wrapper 成功代替验收通过。归档仍使用当前有效验收证据与原有门禁。本需求不改变 Issue 物理归档所需的全部关联交付和整体范围闭环条件。

### FR-007 搜索、筛选与统计

搜索匹配 Change ID/标题及有权查看的来源 Issue ID/标题；通过来源筛选可得到多个相关 Change，每个唯一身份只计一次。无来源 Change 仍可按 Change 类型筛选；REQ/BUG 来源筛选按关联存在性匹配，多来源同时匹配仍不重复。

交付列头标明交付项数量，前期列头标明需求/缺陷项数量。需求总数按 REQ ID 去重、缺陷按 BUG ID 去重、交付数按 Change ID 去重，独立 Change 不虚增 Issue 数；不能把前期卡和交付卡简单求和称为需求总数。数量与当前权限、筛选结果保持一致；Sprint 自身完成数不从交付卡数量推断。

### FR-008 工作量与容量

交付卡仅显示有明确 Change 归属的估算；缺失显示待估算，不能把 Issue 总人天复制给多个 Change，也不能自行平均分摊。共享估算仍归原估算事实源，不因拆卡改变 Sprint 总容量与已用量；存在未归属估算时提示口径不完整，不将缺失视为零。独立估算字段与容量映射方案在后续设计中确认。

### FR-009 操作与会话目标绑定

查看、任务编辑、开始开发、返修、自动验收、归档等入口在打开弹窗、预填命令、确认、提交、重试和续接全程绑定同一项目与完整目标 Change；来源 Issue 链路仍保留完整 ID。纯治理 Change 可无来源 Issue。

有唯一来源时明确展示来源及目标；多个来源且执行能力要求唯一来源时，按既有权限让用户明确选择来源，不按排序默认执行。已绑定的对象会话只有在目标一致时复用；若现有会话只绑定 Issue，须保留可验证的本次目标上下文，不能继承上一次兄弟 Change。

本 PRD 不臆造 CLI 参数。后续设计需定义并验证完整 Issue 命令身份与明确 Change 选择的承载方式；工具不支持或上下文丢失时阻止执行并说明原因。UI 选择不替代服务端校验，直接 API 请求同样检查目标、来源关系、阶段与权限。不得为拆卡自动发送命令、自动批准或扩大执行授权。

### FR-010 权限、异常与兼容

沿用项目隔离和对象授权，不因多来源展示、历史卡或直接文档 URL 绕过限制。缺失源、关系冲突、快照失败、无权限、操作能力未接入分别给出可理解反馈；未知来源不得静默重分类。已有收藏/深链或会话入口应解析为明确对象，无法唯一定位时提示选择，禁止猜测。

刷新保持当前筛选和可恢复目标；目标归档或消失后以新事实解释，不在旧阶段继续执行。已有独立 Change、单 Change Issue、前期 Issue 的正常流程均需回归。

## 5. UI 约束与参考契约初稿

本次为既有页面局部一致性演进。用户截图仅证明原卡片结构与错误提示，不是新拆卡布局的定稿；业务语义优先于旧版聚合结构。复用现有 token、卡片、抽屉、按钮和筛选组件，避免完整复制 Issue 文档链接导致每张卡过长。

| 部件 | 约束 | 后续证据 |
|---|---|---|
| 列头 | 明确计数对象，空列可理解 | 阶段/筛选对照 |
| 卡片顶部 | Change 身份、中文标题、Sprint 与来源可辨认；长 ID 可换行复制 | 1440px/390px 截图与字体/间距采样 |
| 文档与进度 | 当前 Change 为主要内容，Issue 入口明确区分 | DOM 定位、请求目标与抽屉内容 |
| 阶段动作 | 目标确认、loading、disabled、error、防重入一致 | 动作→浮层类型→selector→状态→证据矩阵 |
| 多来源与异常 | 不截断关键身份或泄露受限来源 | 键盘、窄屏、权限样本 |

后续 req-complete 补原型拆解与 UI Reference Replication Contract，req-opsx 将 selector、computed style 采样和动作族矩阵细化到 Change；本轮不宣称已完成视觉验收。既有卡片定位入口为 RequirementCenterPage.tsx 的 renderIssueCard/openTasksAt，具体 selector 与样式值由实施前真实 DOM 采样确认。

## 6. 关键场景与验证方向

| 场景 | 期望 |
|---|---|
| REQ-0048 等价样本：一个历史、一个当前 | 各一张卡，各自阶段/Sprint/任务；当前迭代仅当前交付 |
| 一个 Issue 多活动 Change | 可同时处于研发和验收，操作互不串源 |
| 一个 Change 多 Issue | 一张卡、多来源入口、统计去重；必要时明确执行来源 |
| 全部交付归档但需求有剩余范围 | 历史可追溯，整体需求不自动完成 |
| 无 Change 或仅异常关联 | 前期/待核实入口保留，不制造空卡 |
| 独立 Change | 无伪造 Issue，权限、文档与阶段动作维持原能力 |
| 缺少估算或验收证据 | 显示缺口，不伪造零、通过或 ready |
| 切卡、刷新、重试、会话续接 | 项目、Issue、Change 上下文一致，迟到响应隔离 |
| 权限受限及直接 API | 与 UI 相同授权，不泄露隐藏来源、不跨目标写入 |

验证应分开记录合成回归与真实产品观察；上述为验收设计方向，不是已执行结果。后续补齐 AC、浏览器视觉与请求/执行证据。

## 7. 数据采集、影响面与边界

product_data_collection_observability 为 applicable，affected_layers 为 web、api、web_request_wrapper、usage_events、request_logs、task_traces。遵循 docs/standards/product-data-collection-observability.md，行为、请求和任务上下文应关联明确 Change 与来源 Issue；禁止将完整文档、Prompt、凭据或本机路径写入 metadata。直接 API 不伪造行为事件，采集失败不阻断主业务。

后续验证聚焦目标一致、服务端可信 request_id、授权拒绝、脱敏和失败降级。Web/API 合同和相关测试随实际实现同步，接口变化时更新 OpenAPI/客户端生成；DB 迁移当前无新增业务存储目标，若设计需要持久化目标绑定则重新评估；部署、对象存储与保留周期当前不涉及，因为本范围不新增运行基础设施或证据存储机制。安全边界沿用既有授权，目标校验属于必要回归。

## 8. 关联需求与规则承接

- 父需求 REQ-0026-requirement-center-standalone-change-cards：本需求在交付阶段替代其“关联 Change 仅留在 Issue 卡内”的展示规则；未实施前旧规格继续有效。
- REQ-0048-chat-isolated-acceptance-orchestration：多 Change、跨 Sprint 样本，不扩展该需求业务范围。
- REQ-0027-requirement-center-command-chain-realization、REQ-0039-requirement-center-card-chat-session-reuse：复用执行与会话能力，明确 Change 目标的兼容性需设计验证。
- REQ-0034-requirement-center-default-current-iteration-cards：保留默认当前迭代体验，归属改按 Change 事实。

## 9. 状态与后续准备

本轮补齐用户故事、业务流程、验收与交互原型，文档校验已通过，当前 pending_review；未评审、未纳入 Sprint、未创建 OpenSpec Change。捕获阶段已确认父子关系和总体方案；本稿中的切换门槛、多来源选择、缺失估算展示为评审草案，不冒充额外用户确认。

本轮 business-flow、acceptance 与 prototype/web/context 已细化 UI 契约种子、统计兼容、目标传递及剩余范围入口；具体 CLI/API 承载方式仍在设计阶段验证既有能力。后续评审命令为 `/req-review REQ-0056-requirement-center-change-delivery-cards`；评审通过后先纳入 Sprint，再转 OpenSpec。
