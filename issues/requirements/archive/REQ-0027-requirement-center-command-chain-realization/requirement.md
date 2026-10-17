---
requirement_id: REQ-0027-requirement-center-command-chain-realization
title: 需求中心卡片全命令产品链路真实化
terminal: web-catalog
version: v1
status: done
owner: 产品团队
source: capture.md
parent_requirement: null
created_at: 2026-09-30 08:05:39
updated_at: 2026-10-17 16:21:01
priority: P1
---

# 需求中心卡片全命令产品链路真实化

## 背景

REQ-0027 原为 BUG-0014 部署验收中创建的 Capture 测试记录，现按用户指示沿用编号，承接需求中心卡片全命令的真实执行闭环。已有需求中心卡片、文档查看与 Chat 动作映射是本需求的承接基础；仅打开 Chat、发送命令文本或显示成功消息，不足以证明业务产物已写入和状态已同步。

本需求规定目标行为，不把所有入口尚未实现或某个具体实现缺陷作为已经查证的结论。后续 Change 需逐项盘点可复用能力，补齐前端入口、后端 controller、文件事实源和 Workflow Sync 之间的执行证据。

本地部署的产品策略以治理事实源为默认工作区：受信任本地常驻部署默认采用 `workspace_mode: source`，让 Chat 工作台和需求中心写动作直接读写 `source_root` 当前工作树；`copy` 作为共享、多人或强隔离场景的显式副本模式保留。

## 目标用户

- 产品负责人：从需求卡片完成分析、PRD 生成、文档完善与评审，能查看真实产物。
- 项目负责人：将已评审需求纳入合规 Sprint，并查看关联 Change 和执行阶段。
- 开发与验收协作者：启动开发、观察执行结果，在验收满足后归档并追溯交付证据。

## 目标与成功标准

八类动作均有明确的入口、执行模式、状态门禁和可验证结果。七类写操作只有在对应产物校验、Workflow Sync 成功、事实源重读和卡片投影刷新后才报告该步骤完成；分析操作不改变治理事实。工作区、assistant 输出和 candidate 只能作为候选或执行证据，不能替代文件事实源。重新打开页面或重启服务后，卡片与文档仍能从持久化事实源恢复一致状态。成功、失败、重复提交和权限拒绝均有跨层回归证据。

## 范围

### 包含

需求中心 REQ 卡片的需求分析、生成需求、完善需求、发起评审、加入迭代、生成 OpenSpec、开始开发、完成归档；对应 controller 执行、状态刷新、文件写入、Workflow Sync、异常恢复和链路观测。沿用项目现有权限体系、治理命令和卡片结构。

### 不包含

- BUG 卡片、独立 Change 卡片、Capture 新建或导入能力的重新建设。
- 新的工作流状态机、自动跳过评审或验收、一键执行整条生命周期。
- 新建聊天会话管理体系、对象会话复用策略、聊天历史迁移；对象会话复用由 REQ-0039 承接。
- 发布、生产部署、真实环境修改、数据库恢复或对象存储维护。
- 共享生产仓库或多人并发编辑场景下强制切换为真实仓库工作区；该类场景应显式使用 `copy` 隔离模式并配套副本清理策略。
- 需求文档阶段不执行业务开发，不创建 Sprint 或 OpenSpec；req-complete 补齐需求子文档与交互原型。

## 功能要求

### FR-001 命令身份与入口一致性

卡片动作携带当前授权项目和完整 REQ ID，服务端解析当前阶段目录、关联 Sprint 和 Change。不得只凭标题、短编号或客户端路径定位写入目标。客户端传入的状态、权限、文件路径和引用快照仅作上下文，不能扩大工具权限或覆盖后端事实。

所有写操作进入对应后端 controller 或等价受控分发器。controller 负责身份与项目权限、命令白名单、阶段门禁、产物校验、同步和结果查询；不将任意 Chat 文本当作可执行 shell。后续设计确定真实接口与复用模块，不在 PRD 中虚构已存在的路由。

### FR-002 需求分析保持只读

“需求分析”打开只读 Chat，关联完整 REQ ID、授权项目、分析命令及可读取的文档引用/版本，明确展示“只读分析”。参数语义包括对象类型 REQ、完整对象 ID、项目上下文、只读执行模式和引用版本；具体字段名在 API 设计中确定。

分析不生成或修改 requirement、capture、trace、registry、CHANGELOG、Sprint、OpenSpec 和归档文件，不触发推进生命周期的 Workflow Sync，不将 captured 自动改为 exploring。服务端执行能力限制保证只读，不能仅依靠提示词。聊天正常会话持久化与脱敏观测可沿用既有机制，但不能被解释为治理写入授权。

缺少主动作必备文档不锁定分析入口；读取权限不足或对象不存在时展示对应原因。只读 Chat 中出现生成、开发或归档请求时，提示使用对应受控动作，不能静默提升权限。

### FR-003 动作、产物与状态契约

下表中的命令参数均使用当前完整 REQ ID；表中产物为允许范围，具体写入仍受该命令技能与治理门禁约束。

| 按钮文案 | 命令 | 入口门禁 | 成功产物与同步事实 |
|---|---|---|---|
| 需求分析 | /req-explore | 采集阶段，可读取当前对象 | 只读 Chat，无治理文件变更、无阶段流转 |
| 生成需求 | /req-generate | captured 或 exploring；capture、trace 非空 | 仅生成 requirement.md，req.generate 同步 draft、lifecycle.generated 和索引 |
| 完善需求 | /req-complete | draft 或 enriching；capture、trace、requirement 非空 | 补齐六件套，按 UI 适用性补原型；校验通过后 req.complete 同步 pending_review |
| 发起评审 | /req-review | pending_review；所需需求文档齐全 | 写 review.md 和明确结论；req.review 同步 approved、rejected 或 deferred；通过后按治理迁入 review 阶段 |
| 加入迭代 | /sprint-propose --req | approved；评审记录存在且通过 | 写 Sprint 四件套与双向关联，sprint.propose 同步 in_sprint 和 iteration |
| 生成 OpenSpec | /req-opsx | in_sprint；Sprint 正式范围包含当前 REQ | 生成 proposal、design、tasks、增量 specs 和 trace；req.opsx 回填同一 Sprint 的 Change 关联，展示待开发 |
| 开始开发 | /opsx-apply | 已关联有效 Change，REQ 与 Change 均在 Sprint 范围且实施门禁满足 | opsx.start 记录真实启动并展示研发中；完成开发、验证、文档后 opsx.apply 记录 applied，展示验收中 |
| 完成归档 | /opsx-archive | 已完成 apply，任务、测试、验收和文档门禁全部通过 | 合并生效规格并归档 Change；opsx.archive 同步后按顺序迁移 Issue；全部关联 Change 归档后 REQ done |

入口同时复用既有“阶段 + 对象类型”必备文档表，区分缺少、空文件和事实漂移。具体条件以后端最新事实判断；禁用按钮不能代替后端校验。分析之外的任意一步不得自动执行下一步。

### FR-004 评审与迭代选择

“发起评审”复用明确的确认交互，取消不提交、不写入；成功只表示评审记录和结论真实落盘，评审不通过不能展示已评审通过。拒绝或延后需显式选择并保留理由。

“加入迭代”运行 Sprint 选择校验：无 active Sprint 默认下一个连续编号；一个 active Sprint 默认当前；多个 active Sprint 要求显式选择。新建时扫描 active/archive 编号取最大值加一。保留已有有效容量，默认 30 人天；不得通过此动作静默覆盖已有容量。选择已关闭 Sprint、缺少权限或评审不通过时拒绝写入。

### FR-005 开发启动与归档真实性

开始开发仅在前置门禁通过、执行真实启动后写入 opsx.start；请求已接收或 Chat 已发送不能作为研发已启动证据。Change 使用 execution.schema_version: 1，区分 started_at、completed_at、last_event；创建 Change 时两个执行时间为 null。REQ 的主状态仍为 in_sprint，研发中/验收中由关联执行事实投影。

长任务持续展示运行、阻塞或失败状态，完成开发不自动归档。归档以验收证据为依据，不得将任务全勾选等同于人工验收通过。归档部分失败需展示待恢复，不能提前将卡片标为已完成；单个 REQ 归档不额外要求整个 Sprint 完成。

### FR-006 写入、幂等与失败恢复

同一对象的冲突写操作串行执行。重复点击、请求重试和断线重连应关联同一操作结果，不能重复生成文档、Sprint、Change 或归档记录。运行中禁用重复提交并保留结果查看入口。

提交前检查对象版本、最新状态、权限和必备材料；快照过期或多人并发修改时报告冲突，保留已有文件，刷新后再决定重试。文件缺失、解析或中文标题校验失败时不推进状态。

执行顺序为产物写入及校验、Workflow Sync、读取事实并刷新卡片。多文件写入中断或同步失败时明确区分“未执行”“部分写入、待恢复”“同步失败”“已完成”，展示安全错误摘要与操作标识。工作区、assistant 输出和 candidate 只能说明“产生了候选成果”，不得让卡片、文档入口或阶段标签进入完成态；只有事实源重读确认一致后才更新投影。保留已确认的真实事实，不声称全部回滚或继续展示虚假成功；恢复先核实已落盘步骤，再重放未完成步骤。具体事务、锁和恢复设计由 Change 落实。

### FR-007 结果展示与权限反馈

展示受理、运行、成功、失败和需补充信息等操作状态，操作状态与需求生命周期分开。成功后从服务端重读卡片、允许展示的文档和阶段动作；刷新页面仍显示相同结果。产物入口可打开真实最新文档，不能仅显示 AI 成功文案。

提示文案采用：“缺少必备文档，请先补齐”“当前阶段不支持此操作”“你没有执行此操作的权限”“对象已更新，请刷新后重试”“文件已写入，状态同步失败，待恢复”。认证失效按既有登录流程处理；未授权项目或对象返回受控错误，不暴露内部路径、堆栈或其他项目数据。

### FR-008 跨层回归要求

- 八类动作逐一验证按钮、发送身份、controller 执行模式与结果；七类写动作逐一核对实际文件、trace、registry、CHANGELOG 和适用 Sprint/Change 关联。
- 分析前后对治理文件内容与状态作差异断言，包含在聊天中要求写入的反例。
- 完整主链覆盖 captured → draft → pending_review → approved → in_sprint → 真实开发启动 → applied/验收中 → archive/done，断言每一步下一动作重算。
- 反例覆盖越级执行、未授权、空文档、错误评审结论、过期快照、重复提交、并发写入、断网/重启、文件写入失败和同步失败；失败后不伪造完成。
- 归档覆盖未通过验收、多 Change 尚未全部归档，以及部分归档恢复。成功后验证详情可读、目录迁移和索引一致。
- 分别记录前端交互、后端控制器、隔离文件系统集成与真实界面端到端证据；Mock 成功或合成回归不能代替真实文件链路验收。

## UI 约束

沿用 Web 需求中心现有卡片布局、设计 token、Chat 抽屉和模态组件，不增加一套独立交互系统。按钮文案采用 FR-003；加载、禁用原因、错误重试与成功反馈保持一致。分析为辅助动作，不受生成文档门禁联动禁用。

评审使用确认弹窗，加入迭代使用选择弹窗；生成和完善沿用既有方式选择入口，本需求验收 AI 命令执行路径，不重建文件导入。OpenSpec 与开发动作沿用执行反馈容器，归档展示门禁与确认结果。关闭反馈窗口不等于取消后端任务，重新进入可查询结果。

本轮 prototype/web/context.md 已建立“动作按钮 → modal 类型 → selector → 状态 → 验收证据”矩阵，覆盖键盘焦点、取消、加载、错误和权限差异；若采用参考稿或 prototype，补齐 UI Contract、Skeleton 首轮确认、1440px 关键交互截图和 computed style 证据。本轮未提供视觉参考附件，不宣称完成视觉验收。

## 数据采集与链路观测

依据 docs/standards/product-data-collection-observability.md：

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 卡片点击触发受控 API 和多步骤 Agent Workflow，涉及文件持久化、状态同步与错误恢复。
  validation: 已在独立隔离产品复验界面行为到请求和任务节点的关联、服务端可信 request_id、直接 API 不伪造行为、敏感字段过滤与采集失败降级；详见 Change AC-014/015 证据。完整 REQ 验收仍以 acceptance.md 和自动验收 ready 门禁为准。
```

界面命令行为沿用稳定事件字典，携带行为链路标识；服务端生成可信 request_id，多步骤任务关联操作、workflow/run 和各节点。记录校验、写入、同步、恢复与结果节点的受限状态，不保存完整 Prompt、文件正文、请求/响应正文、密钥或本机路径。直接 API 调用不伪造界面行为。

分析的普通文档读取无需额外 Task Trace，因为没有多步骤写任务；模型调用沿用既有 Chat 观测。请求/任务明细默认 90 天、行为明细 180 天，沿用既有保留策略；观测失败不阻断主业务，Workflow Sync 失败则不能宣告命令完成。

对象存储写入和生产部署为 N/A：本需求以项目治理文件及既有 Chat 能力为边界，不新增上传或环境维护。DB 物理结构、迁移与复用结论以 Change 设计、实现及 AC-014/015 证据为准，不把标准中的逻辑层名称直接当作物理表名。

## 影响与后续设计约束

实施范围涉及 Web UI、后端 API/controller、项目权限、治理文件、工作流和观测；Change 已同步相关 API、数据库、UI 文档与测试，具体文件和验证见 Change trace 与 tasks。部署拓扑和新的认证体系不在范围内。此 PRD 表达目标契约，实际验收状态由 acceptance.md 逐项记录。

## 关联需求

- REQ-0020-requirement-center-card-document-actions-ai-chat：沿用卡片动作映射、Chat、文档和进度入口；本需求补齐真实执行与持久化验收。
- REQ-0022-local-project-import-product-iteration：承接已绑定项目与治理文件的执行上下文，不扩展项目导入能力。
- REQ-0039-requirement-center-card-chat-session-reuse：负责对象会话复用；本需求只要求绑定正确对象和执行权限，避免重复建设。
- BUG-0014：原 Capture 测试记录的来源，作为背景追溯，不宣称本需求已修复该 BUG 或继承其验收结论。

## 待细化事项

req-complete 已在 acceptance.md 落实逐项验收编号，在 business-flow.md 记录复用入口、结果协议语义、权限和恢复矩阵，在 prototype/web/context.md 建立候选 selector 与动作矩阵。真实接口字段、锁与恢复实现、角色映射及生产 selector 由关联 Change 设计和代码落实；未完成的产品与视觉验收仍在 acceptance.md 保持未签认。

## 状态块

```yaml
status: done
generated_at: 2026-09-30 08:05:39
completed_at: 2026-09-30 14:47:17
reviewed_at: 2026-09-30 16:15:39
approved_at: 2026-09-30 16:15:39
iteration: sprint-008
openspec_changes:
  - add-requirement-center-command-chain-realization
source_material:
  - capture.md
next: /opsx-apply REQ-0027-requirement-center-command-chain-realization
```
