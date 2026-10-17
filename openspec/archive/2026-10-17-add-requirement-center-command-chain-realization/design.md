---
title: 需求中心卡片全命令产品链路真实化设计
change_id: add-requirement-center-command-chain-realization
source_requirement: REQ-0027-requirement-center-command-chain-realization
created_at: 2026-09-30 18:06:35
updated_at: 2026-10-04 10:43:55
owner: MoonBox 产品团队
---

# 需求中心卡片全命令产品链路真实化设计

## 背景与现状

需求中心已有阶段卡片、文档抽屉、Chat 工作台和 OpenSpec/Sprint 治理事实源。REQ-0027 要求把卡片上八类命令从“能进入入口”提升为“能证明真实执行并可恢复”的产品链路。

现状中可复用入口包括 `RequirementCenterPage.tsx` 的 ActionDialog/confirmActionDialog/runIssueAction、后端 governance preparation/candidate/writer/controller、需求中心 context API 和 Workflow Sync。上述入口证明已有局部能力，但不能直接推定八类动作端到端全部真实写入、同步和恢复。

## 目标

- 八类动作均使用完整 REQ ID、授权项目、动作类型和对象版本进入后端裁判。
- 需求分析保持只读，不修改治理事实源，也不触发生命周期推进。
- 七类写操作必须在产物写入、校验、Workflow Sync 和事实源重读均成功后才展示完成。
- 工作区、assistant 输出和治理 candidate 仅作为候选或执行证据；完成态以治理事实源、Workflow Sync 和同步后重读投影为准。
- 失败、重复点击、断网、并发修改、多文件部分写入和同步失败有可查询操作身份和恢复语义。
- 研发中和验收中投影来自 Change execution schema 与 tasks/验收事实，不用普通 `in_progress` 覆盖 REQ canonical `in_sprint`。
- UI Contract、UI Skeleton、动作按钮矩阵、computed style 与 1440px 视觉验收门禁在实现前可执行。
- 产品数据采集与链路观测按四层模型脱敏记录，观测失败不阻断主业务，Workflow Sync 失败阻断完成。

## 非目标

- 不重建 BUG 卡片、独立 Change 卡片、Capture 创建或导入能力。
- 不引入一键执行完整生命周期，也不跳过评审、Sprint、OpenSpec、apply 或 archive 门禁。
- 不建设新的 Chat 会话管理体系；对象会话复用由 REQ-0039 及其 Change 承接。
- 不执行生产部署、真实环境修改、数据库恢复、对象存储维护或新认证体系。
- 不在 req-opsx 阶段写业务源码；实现由 `/opsx-apply REQ-0027-requirement-center-command-chain-realization` 执行。

## 设计方案

### 受控动作分发

前端所有卡片动作请求都必须携带：

- 对象类型 `requirement`。
- 完整 REQ ID `REQ-0027-requirement-center-command-chain-realization` 或运行时目标 REQ ID。
- 当前项目/空间上下文。
- 动作类型：`analyze`、`generate`、`complete`、`review`、`sprint`、`opsx`、`apply`、`archive`。
- 对象版本、当前阶段、幂等键、可选确认选择和行为链路字段。

后端 controller 或等价受控分发器负责读取最新文件事实，校验对象存在、权限、阶段、必备材料、版本、动作白名单和幂等键。客户端传入路径、状态、权限、Sprint 或 Change 只作为上下文，不得覆盖后端事实。

### 八动作执行契约

| 动作 | 执行模式 | 成功事实 |
|---|---|---|
| 需求分析 | 只读 Chat / AI 面板 | 无治理文件变更，无 Workflow Sync 生命周期推进 |
| 生成需求 | 受控写操作 | requirement.md 写入，req.generate 同步 draft |
| 完善需求 | 受控写操作 | 六件套和适用 prototype 补齐，req.complete 同步 pending_review |
| 发起评审 | 确认弹窗 | review.md 写入，req.review 同步 approved/rejected/deferred |
| 加入迭代 | Sprint 选择弹窗 | Sprint 四件套和 REQ trace 双向一致，sprint.propose 同步 in_sprint |
| 生成 OpenSpec | 受控写操作 | active Change 文档、delta spec 和 trace 创建，req.opsx 回填同 Sprint |
| 开始开发 | 受控长任务 | opsx.start 记录真实 started_at，研发中为执行事实投影 |
| 完成归档 | 归档门禁确认 | Change 归档、规格合并、Issue/Sprint 同步；全部关联 Change 归档后 REQ done |

请求已受理只能展示受理态，不等同于命令完成。关闭反馈窗口不取消后端任务，再次进入必须能按操作身份查询结果。

### 幂等与恢复

同一对象的写操作串行执行。重复点击、请求重试、断线重连和未知超时必须关联同一操作身份，不得重复生成文档、Sprint、Change 或归档记录。恢复逻辑必须先核实已写文件、Workflow Sync 事件和索引投影，再重放未完成步骤。

治理写入采用“事实源唯一，工作区是候选沙箱”的完成模型：

- 工作区用于执行工具、保留差异和恢复证据，不作为卡片阶段或文档状态事实源。
- assistant 输出只表达模型执行结果，不代表治理文件已经生效。
- candidate 必须携带 manifest、revision、binding revision 和来源 turn；应用前校验这些版本仍匹配。
- writer 成功写入候选文件后必须执行对应 Workflow Sync；同步成功后重读治理事实源并刷新卡片投影。
- Workflow Sync、同步后事实源重读、manifest 校验或 binding revision 校验失败时，操作进入 conflict、stale 或待恢复语义，不得展示成功或更新卡片阶段。
- source 模式收尾在候选 revision 与准备基线一致后，于项目锁内核对源文件全集，执行对应 Workflow Sync 的 `--check` 一致性校验并再次重读；只有候选 manifest、binding revision、校验结果和事实源均一致才写入 `applied / verified`。安全回退不可确认时保留 `source_recovery_blocked`，普通项目读取暂停，受信任的同轮恢复流程可核对保留现场。
- 本地常驻部署默认使用 `workspace_mode: source`，执行器直接以 `source_root` 当前工作树为工作区，避免会话副本漂移和重复占用空间；`copy` 保留为共享或强隔离部署的显式模式。

失败态区分：

- 未执行。
- 部分写入、待恢复。
- Workflow Sync 失败、待恢复。
- 版本冲突。
- 权限不足。
- 门禁未满足。
- 已完成。

多文件部分写入不得声称全部回滚；已确认的真实事实必须保留。外部修改或权限变化导致恢复不安全时，返回阻塞和操作标识。

默认 `source` 模式的候选轮次在执行失败或中断后，仍须先读取该轮不可变基线，再核对当前字节并执行安全恢复；只有回读与基线一致才能报告已恢复。遇到非治理改动、未知外部编辑或逐字节不匹配时保留现场并标记恢复受阻。Chat 直接命令的逐步恢复另按命令事实核验，不得借用候选写入器的结论。

## UI Contract

### 事实源优先级

REQ 业务语义与门禁 > `prototype/web/context.md` > `prototype/web/prototype.html` > `acceptance.md` > `rules/ui-design.md` > 既有需求中心实现。原型是局部一致示意，不是一对一复刻参考稿。

### 页面与入口

- 页面：既有前台需求中心 `/requirements` 或等价当前需求中心路由。
- 入口：REQ 卡片主动作和辅助分析动作。
- 组件族：既有卡片、按钮、Modal/Dialog、Chat 抽屉、执行反馈容器和 Toast。
- 不新增独立生产路由；prototype.html 仅作为评审示意。

### 信息架构与状态

卡片展示 ID、标题、阶段、分级、Sprint、Change 和阶段动作。动作反馈容器展示操作状态、门禁摘要、安全错误摘要、产物入口和重试/刷新入口。写动作浮层必须提供取消或关闭路径，提交后关闭只隐藏反馈，不取消任务。

状态矩阵覆盖 default、hover、focus、disabled、loading、open、accepted、running、blocked、failure、partial、sync failed、conflict、denied、success。

### 视觉 token 与响应式

复用 MoonBox Ops Token、近直角、细边框、高信息密度和深浅主题。1440px 为主验收宽度，390px 验证长 ID、按钮、弹窗、反馈和文档入口不溢出。矮视口浮层内部滚动，底部取消与提交可达。

### 动作按钮矩阵

| 动作 | modal 类型 | 按钮 selector 候选 | 浮层 selector 候选 | 验收证据 |
|---|---|---|---|---|
| 需求分析 | `ai-panel` / Chat 抽屉 | `req-action-analyze` | `req-panel-analysis` | 只读 Chat、文件差异、权限错误 |
| 生成需求 | `action-modal` | `req-action-generate` | `req-panel-generate` | 运行、失败、成功、重试 |
| 完善需求 | `action-modal` | `req-action-complete` | `req-panel-complete` | 缺材料、标题校验、同步 |
| 发起评审 | `confirm` / 评审 Modal | `req-action-review` | `req-panel-review` | 通过/拒绝/延后、理由、取消 |
| 加入迭代 | `dialog` / Sprint 选择 | `req-action-sprint` | `req-panel-sprint` | 0/1/多 active、容量、冲突 |
| 生成 OpenSpec | `action-modal` | `req-action-opsx` | `req-panel-opsx` | Change 创建、中文校验、Sprint 回填 |
| 开始开发 | `action-modal` | `req-action-apply` | `req-panel-apply` | opsx.start、阻塞、applied |
| 完成归档 | `confirm` / 归档门禁 | `req-action-archive` | `req-panel-archive` | 验收门禁、部分归档、恢复 |

生产实现可替换 selector，但必须在实现前建立目标 selector 映射；多卡片场景必须按完整 REQ ID 限定作用域，避免串对象。

当前实现使用卡片完整 ID 与可访问名称定位动作，没有沿用原型候选 `req-action-*` / `req-panel-*` 测试标识。映射如下；卡片必须先限定在 `article.rc-card[data-issue-id="完整 REQ ID"]`，再查找按钮，浮层通过 `role="dialog"` 与名称查找。生成、完善、评审、迭代、OpenSpec、开发和归档均由阶段门禁控制，不应在同一张卡上同时出现。

| 原型后缀 | 当前卡片按钮名称 | 当前浮层名称或反馈入口 |
|---|---|---|
| `analyze` / `analysis` | `需求分析`（辅助按钮） | `需求分析` |
| `generate` | `生成需求 →` | `生成需求` |
| `complete` | `完善需求 →` | `完善需求` |
| `review` | `发起评审 →` | `发起评审`；确认阶段另有 `确认评审结果` |
| `sprint` | `加入迭代 →` | `加入迭代` |
| `opsx` | `生成 Opsx →` | `生成 Opsx` |
| `apply` | `开始开发 →` | `开始开发`；已启动后卡片改为 `查看进度 →`，进度进入文档抽屉 |
| `archive` | `完成 / 归档 →` | `完成 / 归档`；迭代归档另有独立的 `归档当前迭代` 对话框 |

映射以 `RequirementCenterPage.tsx` 的卡片、动作浮层和当前组件测试渲染为依据；隔离产品视觉与交互证据另由 AC-PROTOTYPE-003/005 验证。

### Mock/API 边界

prototype.html 中的状态、Sprint、操作结果和产物入口均为 Mock，不得用于产品完成声明。实现阶段必须明确哪些区域使用真实 API、哪些区域是本地状态展示、哪些失败分支来自合成注入测试。

## UI Skeleton

Skeleton 先行任务必须覆盖：

- 需求中心页面壳、REQ 卡片动作区和辅助分析入口。
- 统一动作反馈容器，含状态、门禁、产物入口、错误摘要和恢复提示。
- `ai-panel`、`action-modal`、`confirm`、`dialog` 四类浮层容器。
- 按完整 REQ ID 定位的可测 selector。
- 1440px 首轮截图或等价 DOM 证据，确认布局密度、按钮层级和反馈容器方向。

Skeleton 通过前不得关闭细节实现任务。

## 数据与 API

接口语义至少覆盖：

- 输入：对象类型、完整对象 ID、动作类型、幂等键、对象版本、确认选择、行为链路字段。
- 输出：操作身份、状态、已落盘步骤、同步结果、允许访问的产物引用、刷新后的对象版本、可恢复性、错误码和脱敏错误摘要。
- 查询：按操作身份读取最新状态，不依赖前端内存。
- 权限：对象读取、写入、Sprint/Change 操作和恢复均需服务端重验。

若新增或修改 REST API、错误码、请求头、响应字段或客户端请求封装，必须同步 OpenAPI、Orval、`docs/03-api-index.md` 和聚焦测试。若新增或修改数据库表、字段、索引、迁移或保留周期，必须同步 SQLite/MySQL schema、迁移、`docs/04-database-design.md` 和数据库测试。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 卡片点击触发受控 API 和多步骤 Agent Workflow，涉及文件持久化、状态同步、幂等恢复、Change 执行和归档门禁。
  validation: 实现阶段需验证界面行为到服务端 request_id、操作身份、workflow/run、task trace/spans 和文件事实源的关联；直接 API 不伪造 usage_events；metadata 只保存 ID、类型、数量、状态、错误码、耗时和脱敏摘要，不保存完整 Prompt、文件正文、请求/响应正文、密钥、Cookie、Authorization header、本机路径或未脱敏材料。
```

行为事件采集失败、请求日志写入失败或 Task Trace 写入失败不得阻断主业务，但必须保留脱敏降级摘要。Workflow Sync 失败必须阻断命令完成声明。

## 冲突处理

- prototype.html 表达八动作反馈结构，但不调用 API、不写文件；最终验收以真实页面、真实 API、Workflow Sync 和文件事实源为准。
- 分析动作是只读，不因为用户在 Chat 中请求写入而提升权限。
- `opsx.start` 和 `opsx.apply` 执行事实投影不得覆盖 REQ canonical `in_sprint`，直到归档闭环。
- 归档成功必须以 Change 归档、规格合并、Issue/Sprint 同步和验收证据为依据，不以 tasks 全勾替代人工验收。
- 对象存储和生产部署不适用，因为本变更不新增上传或环境维护；如实现中引入对象存储写入，需另行扩展声明与验证。

## 风险

- 八动作跨度大，容易把请求受理误当成功完成：用状态机和事实重读拆分。
- 多文件写入中断可能造成半状态：用操作身份、步骤记录和恢复校验处理。
- 前端禁用态与后端门禁不一致：后端作为最终裁判，前端只展示可理解原因。
- 观测 metadata 误存敏感内容：持久化前做脱敏、截断和安全 JSON 序列化。
- UI 细节实现跳过 Skeleton：tasks 中设置 UI Contract/Skeleton 先行门禁。

## 回滚方案

若实现阶段发现高风险故障，可临时禁用写操作入口，仅保留只读分析和文档查看；不得伪造成功状态，不得绕过治理命令。已写入的真实治理文件保留，恢复前先运行 Workflow Sync 和事实源一致性检查。
