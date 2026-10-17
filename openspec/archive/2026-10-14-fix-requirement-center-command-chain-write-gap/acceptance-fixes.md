---
title: 需求中心治理命令链真实写入修复验收返修台账
created_at: 2026-09-29 16:47:32
updated_at: 2026-10-14 00:21:30
---

# 需求中心治理命令链真实写入修复验收返修台账

## 反馈批次

### AF-045 AC-051 评审索引阶段与下一步遗漏

- 反馈与真实产品证据：专用隔离 BUG-0999 从需求中心发起 `bug-review`，产品轮次 completed、候选和应用 applied/verified；评审文档、trace、registry 和目录均为 approved/review，但 CHANGELOG 目标行仍为 `plan`，下一步仍指向 `/bug-review`。旧实现的应用成功不等于索引四列一致。[逐轮证据](evidence/acceptance/inputs/AC-051-review.md)。
- 根因：`review_finalization.py` 仅替换索引行的状态与 trace 路径，未改阶段及下一步；`review.py` 的完整评审校验仅要求状态和路径，因而漏过上述矛盾。
- 调整：后端只对目标行补齐状态、阶段、下一步和 trace 路径；若现值既非旧值也非目标值则拒绝。完整 CHANGELOG 行必须校验阶段和下一步；精简历史测试行保留既有兼容。缺原始行时安全拒绝，不猜测结论或扩大写入范围。
- 验证：增加 REQ/BUG 完整索引行回归，评审测试 59 passed，1 条既有依赖弃用 warning。修复后隔离 BUG-0998 与 REQ-0997 的产品轮次均 completed，候选/应用 applied/verified，文件回读为 approved/review，CHANGELOG 下一步均为对应 `/sprint-propose`；两张看板显示已评审及“加入迭代”。AC-051 定向机器检查通过。copy 模式 checkpoint 和异常门禁由真实文件系统/SQLite 聚焦回归覆盖，不把 source 模式产品观察冒充 copy 模式。
- 边界与文档：原 Change 内的评审投影完整性返修；同步 design、delta spec、tasks、trace、BUG acceptance 与 Sprint 验收。API、DB schema、Web UI、权限、部署拓扑、对象存储及客户端生成无变化。`product_data_collection_observability: applicable`，`affected_layers: [agent_workflow, task_traces, task_trace_spans]`；沿用现有 turn/candidate/application 关联及错误码，仅保存脱敏 ID 与状态，不新增采集字段或保留周期。

### AF-044 未接入命令误建产品对象会话

- 偏差证据：当前 Web 能力矩阵将未知命令归为 `codex_command_only`，但需求中心真实模式的点击分支仍无条件调用 `/api/v1/chat/object-sessions`，与 AC-007/008 要求的明确提示和不伪成功不符。源码路径和新增组件回归可复现；本批未将尚未重建的隔离产品页面当成修复后运行态。
- 调整：仅在真实模式、未知命令点击处先显示带完整 Codex 命令的既有提示并返回；已接入的 generate、complete、review、Sprint、Opsx 写入路径不变。增加未知命令零对象会话请求回归及 REQ Generate 既有入口回归。
- 验证：`src/web/src/requirement-center.test.tsx` 完整 125 项通过；后端原候选测试和独立未知命令测试合计 46 项通过。AC-007/008/009/010 按命令及组件证据复验，视觉/真实产品轮次不由此替代。新后端断言单列文件并纳入 AC-010，避免使共用候选测试输入变更而撤销其他 AC 的有效指纹。AC-006 原文把 complete/review 等列为未接入，与当前真实对象会话能力矩阵不一致，保留待核对，不擅自改写原验收标准。
- 文档与边界：仅修复既有非 demo 行为，不改 API、DB、权限、部署拓扑或客户端生成；无需修改长期规格边界。`product_data_collection_observability: applicable`，`affected_layers: [web, agent_workflow, request_logs]`；验证为未知命令无请求、既有生成请求仍正确，不新增采集字段、敏感内容或保留周期。BUG 子文档主描述、根因与 workaround 无需调整，验收证据同步本台账、tasks、trace、Issue 与 Sprint。

### AF-043 旧未绑定候选阻断同会话续接

- 反馈与直接证据：当前代码隔离产品的 BUG-0039 已有一条 10 月 11 日未绑定轮次的 `prepared` 候选；10 月 13 日同会话 `bug-generate` 候选已 `applied`。点击“完善 Bug”后，发送门禁仍选中更早的 prepared 基准并报告“项目文件已变化”，无新轮次。隔离库只读查询与产品提示一致。
- 根因：`_current_prepared_candidate()` 先按 `state=prepared` 过滤再取最新，忽略同会话时间更晚且已应用的候选，使旧准备态重新生效。
- 调整：先取会话最新候选，仅当其仍为未绑定的 `prepared` 时返回；旧候选保留、不删除，不改变已应用成果、权限或版本门禁。`test_applied_candidate_does_not_reactivate_older_unbound_preparation` 固化该场景。
- 产品闭环：聚焦后端 3 passed；隔离 backend/worker 同步单文件并重启后均健康，BUG-0039 原会话从看板显示“治理可写”，`/bug-complete` 新轮次 `c87b495f-9b33-4e41-bebe-5b761323fdad` completed；候选及 application applied，五件套草稿写回，trace/registry 为 enriching、完成时间 null、根因 unknown。证据见 `evidence/acceptance/inputs/AC-041-review.md`，定向 AC-041 passed。标准镜像重建曾因隔离 Docker apt 阶段长时间无进展而中断，本轮运行验证使用隔离容器单文件同步，不作为正式部署更新证明。
- 文档决策：仅修复既有同会话候选选择偏差，不改 API/DB schema、UI、权限、部署拓扑、客户端生成或 archive-bound 规格措辞；相关验收事实同步本台账、tasks、trace、Issue 与 Sprint 验收报告。`product_data_collection_observability: applicable`，affected_layers: Agent Workflow、request_logs、task_traces；验证为脱敏 turn/candidate/application 状态与真实看板投影，无新增字段或保留周期变化。

### AF-042 准备后版本变化错误类型与隔离产品复验

- 偏差：隔离产品 BUG-0038 真实轮次正确阻断旧基准并允许新 key 续接，但 `governance/preparation.py::check_send` 的 2606 未带 `workspace_fact_source_stale` kind，不能满足 AC-052 的结构化错误契约。
- 修复：仅为该分支补 kind；旧候选、原文件和版本门禁不变。聚焦测试新增 kind 断言，1 passed。隔离 backend/worker/controller 重建健康，BUG-0039 经 Firefox 再次准备、改写目标 capture、发送，显示“项目文件已变化，请重新准备治理动作”，无 turn/application。BUG-0038 新 key application 已 applied/verified。
- 边界：不改 API/DB schema、Web UI、客户端生成、部署拓扑或权限；复用既有错误类型和候选观测。`product_data_collection_observability: applicable`，affected_layers: Agent Workflow、request_logs、task_traces；验证为脱敏 candidate/application 状态和聚焦 kind 断言。验收 24/52，Change 保持 applied，未归档。


### AF-041 Bug Generate 真实轮次的候选拒绝与分级元数据无差异写入

2026-10-12 续验预检：归档尝试暴露 delta spec 的 `MODIFIED` Requirement 在当前有效规格中没有同名目标。核对后把 local-project-governance-loop 的五条、web-catalog-requirement-center 的四条移到各自 `ADDED Requirements`，正文及场景原样保留；`openspec validate ... --strict` 通过。在临时规格副本执行 `openspec archive ... -y`，成功合并 13 条新增、5 条修改并完成临时归档；正式 Change 未归档。此项只修正归档合并声明，不表示 AF-041 产品轮次已通过。

- 偏差证据：Firefox `localhost:39002/chat`，2026-10-10 11:28:10，390×900 视口，从专用 `BUG-0036-bug` 卡片发送 `/bug-generate`；Chat 轮次显示已完成，工作树 `bug.md`、trace、registry、索引均已变成 draft。但本地运行 SQLite 中该轮 candidate `253c1efd-…` 为 `rejected/governance_validation_failed`，无 application。11:43:40 再次在 1440×900 视口运行，candidate `a4a6c11f-…` 仍 rejected、无 application，说明模型回复和卡片投影不能代替后端应用成功事实。
- 根因证据：首轮私有 baseline 与最终工作区 manifest 相比共有 5 个变化文件，其中额外的目标 `capture.md` 只因 Workflow Sync 的 `sync_classification()` 把已正确的 `severity: low` 移到 Frontmatter 末尾并刷新 `updated_at`。这超出 `bug-generate` 四文件 allowlist。第二轮修正后 capture 不再变化，但同时有另一流程改写 BUG-0026 acceptance 和其 Change 台账，导致完整源工作区差异仍超出 allowlist；后端拒绝是正确保护，当前共享项目无法提供独占产品写入窗口。两轮原始私有 baseline 留在运行态私有目录，不转存全文或敏感路径。
- 调整：`scripts/workflow_sync/classification.py` 对已经只有正确 `severity`/`priority` 的 Frontmatter 原样保留字节，避免无语义改写；`tests/unit/test_issue_classification.py` 增加现有正确 capture 保持字节不变的回归。未放宽候选四文件范围、其他对象保护或 source 模式拒绝门禁。
- 验证：`tests/unit/test_issue_classification.py` 6 passed；对当前夹具运行 `bug.generate --dry-run` 后 capture 为 no delta。第二轮真实产品已确认无 capture 附加修改，但因并行写入仍 rejected。AC-004、005、012、015 和完整生成链继续待验，不能据 `bug.md` 存在勾选。
- 文档与边界：同步本台账、tasks、trace、Issue acceptance、verification 和 Sprint acceptance-report。BUG 主文档、原 root-cause、workaround 不变，原缺陷边界未变化。API/DB schema、Web UI、权限、部署拓扑、安全模型、对象存储和客户端生成不变。`product_data_collection_observability: applicable`；`affected_layers: Agent Workflow, task_traces, task_trace_spans`；沿用现有 candidate/application 与安全错误码，校验依据为脱敏状态查询和四文件差异，不保存 Prompt、凭证或文件正文。
- 2026-10-12 独立产品复验：在独立 MoonBox 副本的真实 Firefox 看板点击 `BUG-9101-af041-fixture` 的「生成 Bug」，Chat 同轮 `9165da4e-aa32-4ebd-9ee2-77940c57bcf9` 完成；候选 `b105b07c-d993-537a-81b4-ff40bcb3aedc` 为 `applied`，应用 `cadc06bb-0c23-4ae9-8052-dec68763e6b7` 为 `applied/verified`。可信项目副本 `bug.md` 与 `trace.md` 均为 draft，注册表目标条目和当前态索引同步为 draft，索引下一步为 `/bug-complete`；同一隔离事实源的需求看板读模型投影为 `BUG-9101 planning`，文档入口包括 `bug.md`、`capture.md`、`trace.md`。先前 BUG-9100 隔离夹具因漏写索引行被完整快照校验拒绝，修正夹具后用新 ID 新会话重跑；没有把模型回复或普通治理写入当成成功证据。隔离数据仅在私有临时目录，未写正式项目。
- 当前状态：AF-041 产品写入闭环已复验，`BUG-0036-bug` 与 `BUG-9101-af041-fixture` 均为验收夹具，不纳入 Sprint；本 Change 保持 canonical applied，Issue 仍待其余验收，不归档。

### AF-039 BUG 生成准备阶段 stale 错误诊断与续接

- 反馈：产品内 `/bug-generate BUG-0028` 在执行器启动前显示通用“工作区准备失败”；需要保留成果并能从新基准继续。
- 证据：用户截图为 2026-10-07 21:38 的原会话；worker 结构化事件的 `api_code=2606`、`exception_type=ChatError`，但 `error_code=workspace_prepare_failed`。原候选绑定完整 BUG-0028 ID，状态 prepared；准备后事实源 revision 与候选基准不一致，绑定版本仍一致。失败时具体写入者没有历史快照，不能用事后差异冒充当时原因。
- 附件截图逐项视觉对照：截图 1，Chat `/chat` 深色对话、执行前阻断态；期望显示“治理文件版本已变化，请刷新后重新发送”，实际显示“工作区准备失败，请检查服务日志”。偏差为错误文案和恢复动作不明确，不涉及尺寸、颜色或布局。检查入口为 `TurnActivity` 的 `workspace_fact_source_stale` 映射及运行态 turn 错误码；本次修复后待标准部署复验该错误态。
- 调整：准备期候选基准不一致的 2606 明确标记 `workspace_fact_source_stale`，沿用既有安全错误事件及前端提示；不放宽版本校验、不自动覆盖旧候选或文件。新 idempotency key 创建新候选以当前事实源继续，旧候选保留。
- 验证：`test_governance_candidates.py` 和 `test_chat_preparation_failure.py` 51 passed，覆盖 stale 拒绝、原文件保留、新候选续接、终态错误码。真实产品 BUG-0028 新候选与当前治理/源码 revision 及绑定一致，22:20 新轮次 completed；`bug.md` 已生成，trace、registry、索引均为 draft，根因保持 probable。当前部署尚未含本批错误分类修复，旧错误态的前端文案仍待部署复验。
- 文档边界：既有 API 错误码、事件 payload、DB schema、权限、部署和客户端生成不变；补充 API 语义说明、BUG 验收与 Sprint 验收。`product_data_collection_observability: applicable`，affected_layers 为 Agent Workflow、既有 Chat execution.state/Task Trace；复用原 turn 关联，不记录文档正文、路径或凭证。

### AF-038 后端评审投影收尾与隔离控制文件同步

- 反馈：避免仅恢复 BUG-0033；后续 REQ/BUG 评审遗漏 registry/索引同步时由后端收尾，隔离执行使用当前迁移脚本。
- 证据与根因：collect 原先直接 validate，迁移文档正确但 registry_target/index 过期会被拒绝；评审使用的 `_initialize_command_workspace` 仅覆盖技能，未更新迁移与同步工具。代码和临时仓库/DB 回归确认，非 UI 视觉变更，无新增截图对照要求。
- 调整：先验证完整评审结论、目录集合、主文档、trace、根因、权限及范围，只有 registry_target/index 遗漏才派生目标投影并重新完整校验。仅接受旧值或正确终值，不覆盖其他状态冲突，不自动批准或猜测迁移。不修改 Sprint 或其他对象。
- 收尾：授权和绑定复核、项目锁、快照比对、逐文件条件替换与全量 manifest 回读；隔离工作区同时保留补正后的成果，正常 controller 回写后可 checkpoint。真实仓库收尾失败保留文件，原轮次恢复入口校验候选、绑定、后续轮次与应用记录后重验；不是跨文件原子事务。
- 控制文件：新建干净评审工作区同步当前迁移脚本、Workflow Sync 模块、标题校验及技能；双读防变化，不带入 env，不覆盖有未应用成果的工作区。
- 验证：128 passed，1 项既有 Starlette/httpx 弃用 warning。覆盖 REQ/BUG、approved/rejected/deferred、冲突/缺文档/越界拒绝、同会话原轮次恢复、source 中途写入失败重试、copy 自动应用和 checkpoint、未提交控制文件同步。测试入口见 evidence/af038-review-finalization.md。
- 证据边界：本轮未部署、未发送真实模型评审命令，不将合成回归声明为线上已生效。缺候选、缺基准、评审文件/迁移不完整仍明确阻断，不能凭模型回复生成批准事实。
- product_data_collection_observability：applicable；affected_layers 为 Agent Workflow、task_traces/task_trace_spans，沿用 candidate/application 关联及安全原因码；无新增 HTTP、DB、Web schema，无客户端生成。validation 为候选拒绝无应用记录、成功 applied/verified 断言。
- 文档：同步 design、delta spec、tasks、trace、BUG acceptance、Sprint 验收/发布说明与命令顺序文档；BUG 主文档/root-cause/workaround 无需修改，原命令链缺陷与权限门禁未改变。REQ 子文档扫尾不适用，本 Change 来源 BUG。
- 状态：代码验证完成，产品部署后待复验；canonical applied 和首次完成时间保持不变，未自动创建 Issue/Change。

### AF-037 评审迁移后注册表与卡片同步

- 阶段：验收中/待复验。BUG-0033 的七份文档已在 review 目录，trace/review/bug 为 approved，但 registry 仍为 pending_review、plan 路径；Firefox 需求中心实际显示六份文档缺失，动作禁用。确认事实源投影未同步，不是文档被删除。
- 代码证据：promote-issue-stage.py 原入口仅移动目录和修改 trace；已在 review 时直接跳过。现将评审迁移和定向 Workflow Sync 串行衔接，已迁移对象可重试同步，并重读 registry 的路径、阶段和状态，失败返回非零且保留文档。后端 validate_review 已有严格一致性检查，本批不移除或绕过。
- 附带回归发现 registry 缺字段时固定四空格插入会损坏两空格格式；改为沿用目标列表项缩进，匹配标量不跨行。
- 实际恢复：对 BUG-0033 执行幂等 review 迁移入口，未重新移动或评审，Workflow Sync 更新注册表、索引及 acceptance 来源事件；七份文件保留，approved 与 reviewed 时间保留，未纳入 Sprint。Firefox 刷新后进入已评审、缺失警告消失、加入迭代可用、review.md 抽屉正文可读。
- 回归：迁移与同步、半完成重试、伪成功退出码、dry-run/check 不落盘、目录冲突保留、工作流及后端评审门禁；命令与结果见 evidence/af037-review-projection.md。
- product_data_collection_observability：applicable；affected_layers：Agent Workflow CLI、治理文件投影。沿用同步报告，无新增日志字段、API/DB schema、客户端生成或权限变化。未改 Web/CSS，不需要前端构建；本轮修复真实仓库脚本并恢复当前事实源，未重建镜像或发送新模型轮次。
- 文档扫尾：同步 design/spec/tasks/trace、BUG-0025 acceptance、Sprint 验收/发布说明、命令顺序文档。BUG-0033 的缺陷本体是实现权限，未宣称其源码缺陷已修复；保留原评审/根因/方案。BUG-0025 主描述及根因范围不变，REQ 子文档不适用。

| 参考 | 页面/状态 | 期望 | 实际偏差 | 检查方式 | 处置与证据 |
|---|---|---|---|---|---|
| 本轮无新附件，Firefox 真实页面 | localhost:18102/requirements，深色卡片 | 已评审且文档可读 | 待评审、六份文档缺失、动作禁用 | 修改前后 AX 树与真实文档抽屉；无 CSS 变化，不涉及尺寸调整 | 已恢复，见 AF-037 证据；未以手工 DOM 替代 |

### AF-036 未完成 Change 与会话权限误报

- 阶段：验收中/待复验。confirmed：运行态 BUG-0029 会话所有者空间鉴权通过，目标 bug/capture/trace 存在；新建 fix-chat-workbench-nonempty-page-scroll 只有 .openspec.yaml。旧 _entries 全量读取该 Change 的 trace/proposal 失败，污染 resolve_object 与 authorize_history；实际 relations/objects/messages/conversation 请求均出现 403。前端统一转换为切换空间提示。
- 调整：REQ/BUG 定向扫描对应 registry，不读取无关 Change；Change 精确匹配，候选列表隔离单项不可读目录。仅文档缺失使用 503/尚未就绪，权限/安全拒绝仍 403；fallback 不吞符号链接或路径安全拒绝。Change ACL 在读取文档前检查。前端按既有 2509 区分对象拒绝，不误称空间失权。
- 保留：准备态目录、.openspec.yaml、会话历史、快照、ACL 与未知轮次均不删除或改写。未创建替代会话，未重跑模型。
- 验证：后端 90 passed、1 skipped（显式启用的真实模型测试）；前端 7 passed。标准 down/up self-storage-sqlite 均退出 0。真实 Firefox 原会话刷新后空间错误消失、主对象恢复、原草稿保留、治理可写且发送按钮可用；未发送新轮次。两个原会话的运行态历史授权和关联读取通过，候选列表均返回 77 项，准备态目录仍仅含 .openspec.yaml。证据见 `evidence/af036-object-isolation.md`。
- product_data_collection_observability：applicable；affected_layers：web、api、request_logs。沿用请求日志和既有业务码，无新增敏感采集、DB schema、API 字段或客户端生成；503 为临时对象可用性，403 为真实访问限制。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| codex-clipboard-81b28b4d-7d84-4026-91c1-4ec817ef1980.png | BUG-0029 Chat 深色历史入口，具体视口未采样 | 原会话历史及主对象 | 已授权历史和关联可读 | 标题存在、正文空白、主对象未关联、提示无权访问 | 对象读取失败及错误分类，非布局偏差 | 运行态只读权限/文件检查、403 路由日志、API 与前端测试 | 本批修复；无 CSS/computed style 变化 | 本批根因记录与测试 |

- 文档决策：同步 Change design/spec/tasks/trace、BUG acceptance、API 索引、Sprint 验收与发布说明。BUG 主描述/root-cause/workaround 保留原事实源根因边界；本批为原链路返修，不修改准备态 Change。REQ 子文档不适用。部署拓扑、安全权限和 DB 不变。

### AF-035 执行镜像工具链完整性

- 阶段：验收中/待复验。反馈为 Chat 执行环境缺少 Node 与 OpenSpec CLI，不涉及扩大执行权限。
- confirmed 证据：旧执行镜像离线只读容器内 command-v 仅找到 Python、Git、Bash、rg，未找到 node/npm/pnpm/openspec/curl；Dockerfile 仅安装 Git 和 Codex。技能 req-opsx/bug-opsx 实际调用 openspec new/status/instructions，项目 Web 固定 pnpm 11.2.2。
- 调整：Node 22.22.0、OpenSpec 1.3.1、pnpm 11.2.2、uv 0.8.15 与 curl/jq/patch/zip/unzip 随镜像提供；npm 依赖树锁定，禁用安装脚本和遥测。构建以非 root 校验，产品每次准备在只读沙箱检查工具和固定版本，失败以 container_toolchain_unavailable 明确终止，不进入模型调用和无限等待。
- 安全边界：工具可用不等于允许联网安装依赖；现有网络拒绝、Git 只读、凭证隔离和治理写入范围不变。不挂 Docker socket，不附带浏览器/移动端 SDK 或个人配置。
- 验证计划：单元覆盖缺工具/版本错配/预检异常；真实容器验证创建 Change、status、instructions、validate、只读 list；标准部署后核对工具清单与服务状态。真实容器命令使用临时项目，不冒充真实模型驱动的业务状态流转。
- product_data_collection_observability：applicable；affected_layers：chat_turns、execution.state、task_traces、web。复用安全错误码与既有失败事件；新增控制器诊断 chat.toolchain_preflight_failed 仅记录白名单 tools，不记录完整工具异常/凭证。无 API schema、DB 迁移或客户端生成。
- 实际沙箱首次回归发现 pnpm 探针失败，设置 HOME/XDG 缓存到本容器 /tmp 后通过；工具进程与 app-server 凭证 HOME 分离，/runtime 仍 deny。构建非 root 校验通过，真实容器预检隔离两会话及 OpenSpec 命令两项通过；前端阻断文案六项通过。标准 down/up 均退出 0，新服务健康、执行镜像 ready=true、localhost:18102 实际 bundle 包含新错误码和中文提示。详细证据见 `evidence/af035-toolchain.md`。
- 文档扫尾：更新 Change design/spec/tasks/trace、BUG acceptance、部署文档与 Sprint 验收记录；BUG 主描述、root-cause、workaround 无需改，原事实源写入边界未变。REQ 子文档不适用，本 Change 为 BUG 来源。

### AF-033 停止评审后原会话继续执行

- 当前阶段：验收中/待复验；BUG-0029 的评审事实源已为 approved，但原 Chat 会话的评审轮次 stopped，关联候选仍为 running。随后两轮 sprint-propose 均在执行器启动前 failed/workspace_prepare_failed，BUG-0029 未纳入 Sprint。
- 根因证据：本机运行库中停止的评审轮次绑定旧候选，候选仍为 running；失败的 Sprint 轮次均未绑定该候选。worker 记录 ChatError 2604；容器内 `initialize_workspace` 使用会话级最新 running 候选并触发“治理基准不可重复覆盖”。证据仅记录状态与代码分支，不保存 Prompt、会话正文或本机路径。
- 修复：工作区准备和成果收集按当前轮次绑定候选；仅允许未绑定任何轮次的合法候选兼容回退。旧轮次候选与保留成果不删除、不自动标记应用。若工作区有未应用差异，既有冲突门禁继续生效。
- product_data_collection_observability：applicable；affected_layers：governance_candidates、chat_turns、execution.state、task_traces。复用现有状态和脱敏错误码；无新采集字段、API 响应字段、表、迁移或客户端生成。验证覆盖旧候选与新轮次隔离、合法未绑定候选兼容和准备失败状态。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户原会话失败截图 | Chat 深色，Sprint 命令执行前阻断 | 已停止评审后的原会话 | 同会话后续命令按当前轮次准备工作区 | 旧 running 候选导致两轮准备失败 | 状态/交互阻断，非视觉样式偏差 | 轮次与候选状态、worker 安全日志、容器代码、聚焦测试 | 本批修复候选归属；无样式改动 | 本批次根因证据与回归结果 |

- 自动化验证：`test_governance_candidates.py`、`test_chat_preparation_failure.py`、`test_governance_review.py` 共 82 项通过；随后将回归测试加强为真实同会话 source 模式准备，聚焦用例通过。标准本地部署预检与更新均通过，backend、web、chat-worker、governance-controller 均健康；容器内确认新选择逻辑。原会话当前事实源的 Sprint 命令预检为 approved，source/governance revision 一致。旧失败轮次的旧基线已过期，不能作为新发送验证；由于浏览器控制超时，本轮未实际发送新的产品轮次，AC-047 继续待复验。
- BUG-0025 子文档一致性：本批仅修复现有治理命令的候选归属，补充验收 AC-047；原 bug.md、root-cause.md、workaround.md 的现象与根因不变。Change canonical applied 与首次执行时间保持不变。

### AF-032 评审结论兼容与原成果重验

- 当前阶段：验收中/待复验；Workflow Sync 0错误、2项既有文档warning、0blocker，验收状态pending。AI Usage warning/unavailable、command_run_count=0，不估算；需要实际统计时须提供可归属session输入。canonical applied 与首次执行时间不变，未归档、未自动创建Issue/Change。
- 证据状态：confirmed。BUG-0024 两轮评审候选 rejected，无 application；隔离目录 approved/review，项目 pending_review/plan。只读重放在 outcome 拒绝：review.md 使用 status: approved，校验器只读取 result。
- 范围：兼容单一 status 或 result，双字段不一致拒绝；保留其他迁移与权限门禁。原 rejected 候选仅在无应用、无后续轮次、原基准匹配时重验，不重跑模型、不清空成果。
- product_data_collection_observability：applicable；affected_layers：web、api、governance_candidates、governance_applications、task_traces。沿用 error_code 输出白名单原因，不输出异常原文、文档正文或敏感路径；无新表、无新增权限。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| f39e1683 评审回复截图 | Chat 深色、完成态 | BUG-0024 原成果 | 应用成功后确认事实源状态，失败明确原因 | 工作区 approved，后端校验拒绝 | 状态/错误语义，非布局偏差 | DB、只读校验重放、真实文件 | 兼容结论契约，具体轻量提示；不改布局 | 本批次回归与恢复结果 |

- 自动化验证：后端114项、前端17项通过，涵盖单字段与一致双字段、冲突拒绝、验收来源事件保持、具体原因持久化、同会话重复恢复，以及事实源冲突、后续轮次和越界差异拒绝；TypeScript、OpenSpec strict、中文标题、diff检查通过。
- 真实恢复：原轮次 b175a4fa-925f-4dca-8626-3fd593932f54、原候选 e7bd0524-d252-57fc-b7a0-64cb9e43d708 重验后由 controller 自动应用；application 01aed5ae-ce22-49fc-ad91-54038b0b6658 为 applied/verified，error_code 为空。15项文件变化完整回写，BUG-0024 registry/trace/review 状态 approved，目录迁入 review，旧 plan 目录不存在；7份标题校验通过。恢复前基准保存在 recovery-origin；原工作区内容与应用成果一致、Git差异为空、workspace_checkpoint_commit 已生成。重复恢复返回原候选 applied，没有新增应用或模型轮次。
- 部署证据：执行标准 docker-down.sh self-storage-sqlite 与 docker-up.sh self-storage-sqlite，五个服务均 healthy；backend、chat-worker、governance-controller 的四个修改模块 SHA256 与本地测试源码一致。HTTP实际提供 index-DrYyWL0H.js，SHA256=4b00f8eab422575cf4abcce054ffbd422de362834d4f6824ed38274883c9aa11，与Web容器产物一致；包含具体结论冲突文案，不含待应用成果、查看成果、审阅治理成果、确认应用。
- 浏览器真实观察：Firefox刷新原会话后连接恢复且无治理成果面板；需求中心 AX 显示 BUG-0024 位于已评审，含 review.md 与加入迭代动作，截图目视复核已评审列。只读取实际页面，不执行下一阶段动作。错误提示的冲突与同候选原因更新由真实React组件合成DOM回归覆盖，本批次未新增Playwright双视口或独立浏览器Network导出，不把HTTP哈希核验称为完整Network验收。
- 文档扫尾：已同步BUG验收、Change设计/规格/任务/追溯、API索引与Sprint验收/发布说明；BUG来源，无需修改REQ定义和原型。原BUG-0025根因、临时方案未改变；BUG-0024子文档按原评审成果迁移，不人工重写结论。无DB迁移、API字段新增或客户端重新生成。

### AF-031 评审成果与目录迁移回写

- 当前阶段：验收中/待复验；Workflow Sync退出码0、0错误、2项既有warning、0blocker。AI Usage warning/unavailable、command_run_count=0；如需实际统计需提供可归属会话输入，不估算。保留 canonical applied 与首次执行时间，未归档、未自动创建Issue/Change。
- 证据状态：confirmed。REQ-0027 评审轮次执行完成，隔离工作区为 approved/review，项目事实源仍 pending_review/plan；该轮没有候选。prepare_command_snapshot 只为 complete 创建候选，collect 缺候选直接返回；原 writer 不支持目录迁移删除。
- 范围：req-review/bug-review 当前轮候选、权限、完整目标目录迁移、评审状态校验、自动应用、可恢复删除及工作区基准；不新增 Sprint/Change，不绕过根因确认。
- product_data_collection_observability：applicable；affected_layers：task_traces、governance_candidates、governance_applications；沿用现有操作身份与阶段记录，无新表、无敏感正文日志。API 路由和客户端生成不变。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户评审回复截图 | Chat 深色、完成态 | REQ-0027 本轮执行 | 区分执行完成与事实源应用 | 回复已 approved，但未创建候选 | 状态语义 | DB、文件快照、代码调用链 | 修复候选和回写，轻量应用提示 | 本批次测试及恢复记录 |
| 用户待评审卡片截图 | 需求中心、待评审列 | 事实源 registry/trace | 成功应用后进入已评审 | 仍 pending_review，缺 review.md | 数据未应用，不是样式偏差 | controller、事实文件、运行态 API/DOM | 修复事实源链路，不调整卡片布局 | 本批次验证记录 |

- 后端验证：97项回归通过，涵盖REQ/BUG评审三种结果、迁移文件集、越界修改、原基准冲突、控制器中断重放及旧complete候选不替代review。前端16项回归覆盖应用前后提示、只读GET轮询与无治理面板；TypeScript与生产构建通过。
- 真实恢复：复用原review轮次e982a68b-4ebe-4a49-a3b2-58fb06ca5b4c；新候选b766ce07-0e89-5c44-b5a0-97f2994a5b9c自动创建application，controller状态applied/verified、error_code为空。保留原模型评审结论，应用19项变化含8个旧路径删除；工作区checkpoint已记录且git状态干净。REQ-0027 registry/trace为approved，review.md与完整子文档在review目录；8份Markdown标题校验通过。
- 真实浏览器证据：标准self-storage-sqlite部署后，Firefox localhost:18102/requirements刷新时待评审1→0、已评审0→1；REQ-0027出现review.md与加入迭代。点击review.md打开真实文档抽屉，显示已评审及原评审结论；本轮工具返回的AX状态及截图可复核。未使用合成响应替代该真实观察，未重跑模型。
- 最终部署证据：按标准down/up脚本完成部署；backend、chat-worker、governance-controller中review/recovery/writer/preparation代码SHA256均与当前源码一致，服务健康。HTTP读取实际Web bundle index-JU_wcwLZ.js，应用中与已同步文案均存在，待应用成果/查看成果/审阅治理成果/确认应用均不存在。重启后同会话complete与review仍applied，review application保持verified且无错误。
- 迁移扫尾：发现仅删除文件会留下旧空目录，导致标题工具报Issue身份不唯一；新增应用后以no-follow目录句柄只移除空的原目录，非空目录不删除。REQ-0027空目录清理后身份校验通过。应用记录保留原始内容与删除标记。
- 验证边界：BUG评审为合成回归，未推进仍待补证的BUG-0024；本批次真实复用的是既有complete→review链路，不声称新模型全流程重跑。没有新增布局或CSS，沿用现有Toast与卡片，本批次未新增双视口Playwright截图或独立Network导出。
- 文档扫尾：BUG来源，无需改写REQ-0027需求定义；恢复保留原评审结论及子文档，仅依据已有成果迁移和同步，避免重跑模型。

### AF-040 移除规划中卡片的草稿标签

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户本轮 BUG-0028 卡片截图 | 需求中心规划中、深色、draft | BUG-0028 卡片标签行 | 不显示草稿状态标签，保留 severity、负责人和完善 Bug 动作 | severity 前显示“草稿” | 多余状态文案 | JSX 条件、桌面/移动端组件断言与截图 | 移除可见状态标签，内部 draft 与流程不变 | 本轮附件、`RequirementCenterPage.tsx`、`requirement-enriching.cjs` |

- 偏差根因已确认：规划中且 `issue.status === "draft"` 时，卡片 JSX 直接渲染独立草稿标签；AF-030 曾显式保留它。本轮反馈覆盖该展示约定，不改变状态事实源。
- UI Contract：规划中卡片不渲染草稿或完善中的独立状态标签；保留 severity、负责人、已有文档、补证提示、主动作和所有内部状态门禁。无新 modal、API、DB 或权限边界。
- 验证：需求中心组件 114 项通过，TypeScript 无错误，OpenSpec 当前 Change 中文与结构校验通过。独立 Vite 预览的 Playwright 合成 API 未渲染测试卡片，双视口截图尚未取得；当前产品仍为旧构建，不将组件断言等同于部署后真实观察。部署新构建后仍需在 1440px 与 390px 复验 BUG-0028 卡片标签、severity、负责人及完善入口。
- 文档扫尾：Change design/spec、BUG-0025 acceptance、Sprint 验收和发布说明已改为不展示两类独立状态标签。BUG-0025 原始现象和根因、BUG-0028 业务内容均不变；API、数据库、权限、安全、客户端生成无需同步。

### AF-030 移除完善中标签

- 收尾：Workflow Sync 0错误、2项既有warning、0blocker；回到验收中/待复验，未归档、未新增Issue/Change。AI Usage unavailable，不估算用量；如需统计需提供可归属session数据。

- 验证：前端 requirement-center 111 passed、TypeScript、OpenSpec strict、中文、根因证据校验通过；标准 docker-down/up self-storage-sqlite 已完成。部署组件 + 合成 API 的1440/390px浏览器断言通过：无完善中标签、草稿保留、长 owner nowrap/ellipsis/hidden 且 right 不超出父容器；子文档可打开，继续完善仍 POST bug-complete 并跳转 Chat。截图与 computed/Network 证据：logs/requirement-enriching-no-label；已目视复核。
- 全仓 Design System 仍为既有176项违规，本轮无新增违规；不据此声明全仓校验通过。未修改后端门禁、API、DB、权限或安全，不需重新生成客户端。product_data_collection_observability=N/A：仅卡片展示，未新增请求或埋点；affected_layers=web；validation 为既有请求路径浏览器断言。
- 子文档扫尾：BUG acceptance 增补AC-044；原 bug/root-cause/workaround 无需更新，根因和业务处理未变；Change design/spec/tasks/trace 与 Sprint 验收/发布说明已同步；非 REQ 来源，不涉及原型子文档。旧 AF-029 截图保留，新证据独立目录。

- 研发中；保留 canonical applied。confirmed：截图中独立完善中标签被长负责人名称挤成竖排，用户要求移除标签；既有 JSX 明确渲染该标签，meta flex 行未限制负责人宽度。
- UI Contract 覆盖 AF-029 的标签要求：仅 draft 保留草稿标签；enriching 不渲染状态标签，保留真实子文档、补证提示、继续完善及所有内部状态门禁。长负责人省略显示并提供 title 全文。动作/modal 路由均沿用 AF-029，无新增交互。

| 附件/页面状态 | 对象/期望 | 实际偏差 | 检查方式 | 处置/证据 |
|---|---|---|---|---|
| 2c9e3214，需求中心规划中，深色卡片截图688×734 | `.rc-card-tags` 无完善中标签；负责人不挤压其他标签 | 完善中竖排、负责人越界 | JSX/CSS、1440/390px DOM、computed style、截图 | 移除标签并限制负责人；src/web/tests/requirement-enriching.cjs |

### AF-029 完善中卡片事实展示

- 收尾：Workflow Sync 0 错误、2 项既有子文档 warning、0 blocker；回到验收中 / 待复验，不归档、不改首次 applied。AI Usage unavailable，command_run_count=0，未估算用量；如需用量，提供可归属 session JSONL 后重跑 Hook。未新增 Issue/Change。

- 研发中，canonical applied 及首次执行时间不变。confirmed：BUG-0024 的 bug/trace/registry 为 enriching，根因为 hypothesis；后端 STAGES 将 draft/enriching 合并为 planning，前端 stageVisibleDocs.planning 隐藏已生成子文档。
- UI Contract：保留规划中列，在 `.rc-card[data-issue-id]` 显示草稿/完善中；完善中展示实际存在的完善子文档、轻量待补证原因与继续完善动作。原因不作为 complete 按钮禁用条件；根因 confirmed 与证据门禁不变。不新增 modal 或写权限。

| 附件/状态 | 对照对象与期望 | 实际与偏差 | 检查方式 | 处置与证据 |
|---|---|---|---|---|
| 8822aa1a，文件树，478×398 | 已生成 root-cause/workaround/acceptance 可访问 | 文件存在但卡片未展示 | 文件与 API document_entries 对照 | 修复前端文档过滤；BUG-0024 目录 |
| c0b9d043，需求中心规划中卡片，664×524，深色 | 完善中、补证原因、继续完善 | 与草稿同列且无状态提示，仅主文档和 trace | 真实组件 DOM、1440px 截图、computed style/溢出 | 已修复卡片投影；无须移动到待评审；logs/requirement-enriching |

- 验证：后端 test_governance_board + test_bug_completion 91 passed；前端 requirement-center 111 passed；TypeScript、OpenSpec strict、中文、标题和 git diff 检查通过。OpenAPI 导出成功，生成脚本受本机 pnpm 缓存缺失影响，改用已安装 Orval 8.29.0 完成客户端生成。
- 运行态：标准 docker-down/up self-storage-sqlite 完成，Web/backend/chat-worker/governance-controller/minio 启动正常。真实 BUG-0024 文件投影返回 status=enriching、stage=planning、六份文档、根因未确认提示、完整 bug-complete 命令且 disabled_reason=null；本轮不执行业务命令、不修改 BUG-0024 状态。
- 浏览器边界：部署 Web + 合成 API，1440×1000 与 390×1000 真实组件 DOM、截图和 Network 通过。提示 clientWidth=scrollWidth，无正文溢出；文档 GET 可打开；继续完善 POST object-sessions action=bug-complete 并进入 Chat。截图已目视复核，证据 logs/requirement-enriching/card-1440.png、card-390.png、evidence.json。移动端既有助手浮钮靠近卡片 footer，本轮未改变该全局布局，不据此声明全站视觉验收完成。
- 全仓 Design System 校验有 176 项既有违规（Chat 原生控件与硬编码色等）；未新增 CSS，不扩大返修范围。当前改动复用原卡片 token/样式。
- product_data_collection_observability：applicable，affected_layers=web/api；沿用 context 与 object-sessions 请求观测，不增加 DB、usage_events、request_logs 或 Task Trace 字段；validation 为真实投影、Network 和组件回归。无数据库迁移、权限/安全/部署拓扑变更。
- 子文档一致性扫尾：BUG acceptance 新增 AC-043；bug.md/root-cause.md/workaround.md 无需更新，原缺陷目标及根因未被推翻；trace 由 Workflow Sync 更新。Change design/spec/trace/tasks、Sprint 验收与发布说明、API 索引已同步。非 REQ 来源，无 REQ 原型或子文档变更。

### AF-028 零差异幂等核验

- 收尾：Workflow Sync `opsx.modify` 通过，0 错误，2 项既有子文档 warning，无 blocker；返修回到验收中 / 待复验，保留 canonical applied 与首次执行时间，不归档。AI Usage hook 为 unavailable（无可归属 command runs），不估算用量；`git diff --check` 通过。
- 研发中，保留 applied 原事实。confirmed：最新轮次 95057572-3794-46ff-a121-b54c9aea7d91 completed，候选 rejected/governance_validation_failed；完整工作区 manifest 差异为空，目标事实源与基准一致。validate_completion 将 not changed 作为 scope 错误。
- 截图对照：64c2a30d，Chat 深色、2048×872、执行完成；期望无改动时核验成功，实际出现失败 Toast；检查方式为 DB、完整 manifest、事实源与组件通知断言。本次只改结果语义，不改布局、颜色或尺寸；无需 computed style 调整，不恢复治理面板。
- 方案：零差异继续验证完整文档与状态，重新校验权限、binding 与事实源 revision；成功记 unchanged，不创建 application、不写文件、不推进状态。历史入口使用当前/最新候选，不能复活旧 rejected。
- product_data_collection_observability：applicable；affected_layers：api、web、task_traces；复用候选 state 与事件，无 DB schema 迁移或新增权限边界。验证包含重复 complete、缺文档/状态不符/源版本变化阻断及历史旧错误隔离。
- 验证：后端 79 passed，前端 15 passed，TypeScript、OpenSpec strict、中文与标题校验通过。标准 docker-down/up self-storage-sqlite 更新 backend/web/chat-worker/governance-controller，全部服务启动完成。
- 真实原会话重复 complete：轮次 a0bbaaba-af27-4042-96b7-ad6830a61544 completed/error_code=null，候选 b1e5e32e-d3fd-5a54-b485-7bf0b314ad22 unchanged/error_code=null，无 application。完整 workspace_manifest_unchanged=true，source_bytes_unchanged=true，workspace_clean=true，result_files=[]。旧 rejected 记录保留审计，不篡改历史。
- 浏览器 1440px 正常打开/历史恢复通过：最新 unchanged 加历史 rejected 的合成 API 驱动真实部署组件，显示无需更新且无错误 Toast、无成果面板、无应用请求。截图与 DOM/computed style/Network 证据为 logs/chat-governance-noop/history.png、open.png、evidence.json；该浏览器证据与真实模型/DB/文件证据分开标注。
- 文档一致性：Change 设计/spec/tasks/trace、BUG 根因/AC-042、Sprint 验收/发布与 API state 说明同步。REQ 子文档无需更新，本次未改变需求业务契约；无需数据库迁移、生成客户端、安全边界或部署拓扑调整。建议将无差异、真实冲突和业务未就绪分开验收，不自动创建 Issue/Change。

### AF-027 缺陷完善候选与草稿自动回写

- 研发中，保留 canonical applied。confirmed：bug-complete 没有本轮候选，权限读取同会话历史已应用 generate 候选后返回只读；成果仅在临时目录，没有正式回写。
- 附件 4e0119ea：Chat 深色、2048×845、完成态；期望正式文档和准确阶段，实际回复临时草稿与 /work 只读。通过 DB 候选绑定、权限函数、事实源文件核对；本次修复后端，无布局变更，不把模型完成当作应用成功。
- 契约：当前轮候选绑定、隔离工作区治理写入、成果收集与 controller 自动回写。根因 unknown/hypothesis/probable 保存 enriching 草稿且不改完成时间；confirmed 且证据有效才允许 pending_review。原有成果与其他对象不得覆盖。
- product_data_collection_observability：applicable；affected_layers：executor、api、task_traces；复用现有候选及应用记录，无数据库 schema 或客户端生成变化。
- 合成回归：135 passed、1 skipped。覆盖同会话 generate→complete、旧候选权限回退、四种根因状态、无证据/状态矛盾/缺文档/越界/提前完成拒绝、自动 application、原基准恢复及权限隔离。
- 真实回归：标准 docker-down/up self-storage-sqlite 更新全部服务并健康。复用 BUG-0024 原 generate 会话，本轮 a6154fb4-38d8-40be-983e-6d3edebe3589 completed/error_code=null；候选 3209e972-3bb0-5ccd-bd8a-f41be6e4b638 与应用 3b595686-0cfc-4fb6-acf0-dc63344ae385 均 applied。运行中权限 governance_write/governance_candidate_running，历史 generate 保持 applied。
- 文件事实源：正式新增 root-cause、workaround、acceptance；bug/trace/注册表/索引统一 enriching，根因 hypothesis，lifecycle.completed=null。capture SHA256 保持 c3b5115d7c90f13d10d137d1f3c81df5b0ea7d09776cfdb188fc462f260b7596。原先临时文件未作为可恢复事实，使用本轮正式文档重新生成。
- Worker 独立核验：active_turn=null，workspace_clean=true，checkpoint_matches_head=true。历史 turn.prompt 仅为 /bug-complete BUG-0024-capture，不含内部约束。没有人工应用环节，没有清空文件、绕过门禁或伪造 confirmed。
- 一致性扫尾：BUG-0025 根因/AC-041、Change 设计/spec/tasks/trace、Sprint 验收/发布、API说明同步；BUG-0024 五件套及索引由真实 controller 更新，capture 保留；REQ 文档无需修改，本次未改变需求业务契约。无 UI、DB schema、权限范围或客户端生成变更；部署继续使用标准脚本。
- 待用户补证属于 BUG-0024 业务根因，不阻断本次草稿自动回写验收。建议以后每条写入命令均按当前候选、文件事实源、application 和工作区基准验收，不仅检查模型完成；未自动创建新 Issue/Change。
- 收尾：OpenSpec strict、当前 Change 中文校验、BUG-0024 六份文档标题及 diff 检查通过。Workflow Sync Errors=0、blockers=0、既有 warnings=2；AI Usage warning/unavailable，无可归属统计，不伪造用量。返修回到验收中/待复验，未归档；本轮不要求人工确认应用。


### AF-026 原工作区需求完善成果续接

- 研发中，保留 canonical applied。confirmed：执行器治理沙箱未允许默认临时目录写入，Workflow Sync 临时锁失败；req-complete 没有候选收集及自动应用入口，留下未应用成果并阻断后续命令。
- 附件 e6762db5：Chat 深色历史显示执行前阻断，期望原成果可安全续接；实际未应用文件被保护但没有恢复闭环。通过 DB、原工作区文件摘要和 controller 测试核对，不改变页面布局或恢复治理面板。
- 修复范围：临时目录与治理配置真实锁预检；同对象已执行轮次原始基准匹配后续接；完整文档、身份、状态、文件边界校验后自动应用。不得删除成果、忽略冲突或强行推进状态。
- product_data_collection_observability：applicable；affected_layers：executor、api、task_traces。复用候选、应用和错误事件；无数据库 schema 或外部 API 字段变更。
- 合成回归：115 passed、1 skipped；覆盖原文件字节不变、无来源/版本变化/越界阻断、完整五件套、controller 自动应用及 Worker 基准更新。发送前只读核验，Worker 串行锁定空闲会话后才更新已应用基准，活跃轮次禁止提交。
- 真实恢复：同会话续接 f2bf0d50-be23-456b-9523-6dca5ea88615 已 completed，候选 a81b4303-1626-5ff5-b26c-14e6a9e3de1d 和 application 均 applied/error_code=null。本地 requirement.md、trace.md 均 pending_review，lifecycle.completed=2026-09-30 14:47:17；原文档、原型均保留，未清空工作区，未进入评审/Sprint/OpenSpec。
- 实际模型运行报告标题校验 7 份、同步 dry-run/正式同步/check 通过；本地事实源和 DB 独立复核支持应用成功。Readiness 为 Partially Ready，真实产品与视觉验收仍属于后续实施，不宣称 REQ-0027 全功能完成。
- 子文档一致性：恢复产生的 requirement、user-stories、business-flow、acceptance、trace、prototype/context 与 HTML 同步回写，capture 保持原摘要。BUG 根因、AC-040、设计/spec、部署/API说明与 Sprint 发布验收同步；无 UI 组件变更，不新增截图布局验收声明。
- 最终标准 docker-down/up self-storage-sqlite 部署完成，backend/web/chat-worker/governance-controller/minio 全部 healthy。真实 Worker 查询：candidate=applied，active_turn=null，workspace_clean=true，checkpoint_recorded=true，checkpoint_matches_head=true。基准由 Worker 自动确认，未手工清空或强制标记应用；capture 摘要仍为 8ae7d484912096e7b2704215c7b296679df2647df69ad8b7c4fe94f0c21bab42。
- 最后补测只读 API 准备不执行 Git add/commit、活跃轮次阻止基准更新，相关 22 项通过；OpenSpec strict、中文标题与 diff 检查通过。规范建议：后续命令接入必须包含部分成果续接、实际 application 与工作区基准的闭环证据，不能只检查模型 completed；未自动创建新 Issue/Change。
- Workflow Sync：Errors=0、blockers=0、既有子文档 warnings=2；返修回到验收中/待复验，不归档。AI Usage hook 为 warning/unavailable，无可归属用量，不伪造统计。待用户决策/处理：无；下一步为产品端复验待评审文档与原会话恢复。

### AF-025 工作区准备失败终态与成果保留

- 研发中，canonical applied 与首次 completed_at 不变。截图 a7909e72 的 14:08 轮次 5661f8f6-aa1c-4fb7-a718-1710b332ad51 在一秒内 unknown/platform_workspace_unavailable，executor_turn_id=null。平台 worker 在 initialize_workspace 异常时统一 mark_unknown 且不记录原因，confirmed。
- 当前只读重验：对象 preflight、binding_revision、source/governance revision 全部一致；会话 workspace 存在 requirement/trace 修改及 acceptance/business-flow/user-stories/prototype 新文件，治理候选为空。代码因此拒绝覆盖未应用成果；旧 catch 丢失原始异常，不能将重验结果冒充历史异常日志。
- 安全恢复：仅 unknown + platform_workspace_unavailable + executor_turn_id=null 且会话 generation/active_turn 匹配的旧轮次改为 failed；释放占用并按未启动结算，不修改、覆盖或自动应用工作区文件。不处理租约失联或有执行器 ID 的 unknown。
- 实现：准备阶段错误使用 allowlist 错误码、结构化阶段日志与 execution.state，前端显示“执行前阻断”和处理建议；真正 unknown 显示核实提示而非无限等待。不恢复治理成果面板。
- product_data_collection_observability：applicable；affected_layers：web、api、task_traces、task_trace_spans。复用现有 status/error_code/events，无 schema/权限边界及客户端生成变化；日志仅 turn_id、阶段和安全错误码，不含路径、Prompt、凭证。
- 子文档扫尾：BUG 来源，REQ-0027 业务文档不改；其隔离副本成果保留，未宣称完成应用。安全恢复不等于 req-complete 产品写入链路验收通过。
- 验证：后端 Chat、准备失败、长任务及治理候选共 88 passed、1 skipped；前端 14 passed，TypeScript 通过。相邻 source-workspace 回归发现 preparation 缺少 json 导入，已补齐并复验。OpenSpec strict、中文校验与 diff 检查通过。
- 首次部署后真实 DB：目标旧轮次 failed/workspace_prepare_failed、executor_turn_id=null；conversation.active_turn_id=null。Worker 输出 chat.workspace_prepare_failed、recovered=true、exception_type=legacy_unavailable，不伪造历史异常原因。真实部署组件配合合成 API 验证首次打开及历史恢复，Network 返回 failed/workspace_unapplied_changes，DOM 无等待正文；1440px 截图已人工检查，证据 logs/chat-preparation-failure/evidence.json、open.png、history.png。
- 浏览器证据边界：使用实际构建组件与合成响应验证 UI；真实数据库恢复单独核对，不冒充已登录真实用户端到端模型执行。8 个隔离成果文件部署前摘要为 93243288bc77708808d40baafaae85ce8909767ff7508c2c2d40c0768d83101b，部署后复核同值才确认保留。
- 最终验证完成：标准 docker-down/up self-storage-sqlite 后所有服务 healthy，运行态 json 导入存在，目标轮次 failed、active_turn=null；8 个成果文件摘要与上述部署前值一致，确认未覆盖。浏览器打开/历史恢复二次回归通过；平台补充 5 项通过，后端累计 93 passed、1 skipped。Workflow Sync Errors=0、warnings=2、blockers=0；AI Usage warning/unavailable，不伪造用量。返修回到验收中/待复验，不归档、不自动创建 Issue/Change。规范建议：准备阶段与执行阶段使用分开的终态恢复验收矩阵。

| 附件/截图 | 页面/状态 | 对照对象 | 期望 | 实际/偏差 | 检查方式 | 处置 | 证据入口 |
|---|---|---|---|---|---|---|---|
| a7909e72 | Chat 历史，深色，截图 2048×328 | TurnActivity 状态/正文 | 准备失败显示原因，不等待 | unknown 与等待正文并存 | DB、代码路径、真实组件 DOM，1440px 浏览器截图 | 本次修复状态文案，无布局改动 | chat-preparation-failure 测试及 logs/chat-preparation-failure |

### AF-024 长任务固定时限与原轮次恢复

- 用户授权先恢复 REQ-0027 原轮次，再取消固定 300 秒限制。confirmed：DB error_code=execution_deadline_unknown；执行器持久 turn 的权威状态 interrupted，部分业务流程、用户故事、验收和原型 context 已存在，未确认完成。
- 恢复阻塞：thread/read 历史响应超过 256KB；只读探针确认后，正式适配器将 RPC 响应上限调整为 4MiB，流式事件仍限定 256KiB。使用标准 reconcile_unknown 按 interrupted 归并 stopped，不伪造完成、不重置用量。
- 返修：run_claim 默认不设置总执行时限，显式测试时限仍支持；保留中断、权限、租约、额度和协议边界。原始任务与续接结果分别记录，不能把入队当作业务完成。
- 验证：后端回归 44 passed、1 skipped；合成时钟超过 300 秒仍可完成，显式截止及协议大小边界通过。标准 docker-down/up self-storage-sqlite 部署完成，backend、web、chat-worker、governance-controller、minio 均 healthy。
- 真实恢复：原轮次 df271d94-26d7-4e77-aba7-b81f4e25d26d 已归并 stopped；同会话续接轮次 6e77d72b-681e-4a23-a0fe-295534db4a70 经标准发送入口创建，DB 已确认 running、error_code=null。续接保留既有部分文件，不声明业务完成。
- product_data_collection_observability：applicable；affected_layers：executor、api、task_traces。复用原执行状态与恢复记录，无 DB schema、外部 API schema、UI 或客户端生成变化；validation：状态核对、边界回归与标准部署验证。REQ 业务子文档未修改。

### AF-023 未落库运行输出独立满宽

- 根因 confirmed：用户截图的运行输出在 turn-user 下，命中 720px/72% 子节点限制及 TurnActivity 1120px 上限；旧浏览器测试手工构建 turn-assistant，遗漏真实组件分支。
- 研发中，保留 applied 事实。方案：运行输出成为用户 block 的独立 assistant 兄弟区；落库后由 assistant 消息接管，不重复显示。用户气泡限制不变。
- 验证完成：真实部署页面加载实际 ConversationMessages 与 TurnActivity，合成 API 驱动运行/落库/历史恢复，1440/1920/390px 共 9 个 DOM/computed width 状态通过。1440px 历史/block/article=1168px，内容列/正文/activity=1126px；1920px 正文=1606px，max-width=none；用户 article 保持 760px 上限。证据：logs/chat-live-output-width/computed-width.json 及各视口截图，测试入口 src/web/tests/chat-live-output-width.cjs。未启动真实模型执行。
- 消息组件 9 项回归、TypeScript、标准 docker-down/up self-storage-sqlite 部署、OpenSpec strict 和中文校验通过。Web 与配套服务均 healthy；未用局部 Compose 代替标准部署。
- 文档同步：design、tasks、trace、capability delta、BUG AC-037、Sprint 验收/发布说明。product_data_collection_observability：N/A，仅前端布局归属变更，不改变 API、DB、请求包装、日志、安全、权限、部署拓扑或客户端生成；无 REQ 子文档变化。旧人工 DOM 用例不再作为本项充分验收证据。

| 附件/截图 | 页面/状态 | 对照对象 | 期望 | 实际/偏差 | 检查方式 | 处置 | 证据入口 |
|---|---|---|---|---|---|---|---|
| e4ac148a 用户截图 | /chat 深色，执行中、DevTools 展开 | status 正文及样式面板 | AI 正文占满内容列 | 命中 min(720px,72%)，右侧大片空白 | 真实 ConversationMessages/TurnActivity，1440px/移动端 computed width，落库前后网络驱动 | 本次修复，不改变用户气泡及 meta 排列 | 用户截图；新增真实组件浏览器回归 |

### AF-022 Worker 心跳与能力探测恢复

- 研发中，保留 Change applied 与首次执行完成事实。证据 confirmed：Worker 主循环在心跳之间执行同步维护；24 次运行态采样中有 5 次心跳年龄超过 5 秒门禁，前端 capabilities 仅在 space/boot 变化时获取。
- 附件逐项对照：`codex-clipboard-f037c0c4-413c-44c0-bcea-4ab75dfa4068.png`；/chat，深色，1912×1312 展示视口，完善需求草稿待发送。期望服务恢复后发送可用、草稿不变；实际治理可写但显示执行服务未就绪。检查 Composer 的 chat-send disabled、草稿及 capabilities 网络重试；本次修复状态行为，不改变布局。
- 方案：独立心跳生命周期；能力自动重探测，不重置会话或草稿；就绪原因分类且不泄漏配置路径、凭证。保留后端发送门禁。
- 补充根因：已应用 GovernanceResult 使用不稳定刷新回调，父组件更新触发反复刷新；refreshSelected 改为按 conversation ID 稳定回调，完整工作台测试恢复通过。
- Workflow Sync：Errors=0，BUG pending，返回验收中/待复验；保留两条既有子文档 status warning（confirmed/active）。AI Usage unavailable，无可归属 token 事件，不伪造用量。未创建新 Issue/Change；归档仍需业务复验。
- 验证：后端 Chat/platform 44 passed、1 skipped；前端恢复/Composer/工作台 29 passed；TypeScript、Vite 构建、OpenSpec strict、中文/标题检查通过。
- 标准部署：依次执行 docker-down.sh self-storage-sqlite、docker-up.sh self-storage-sqlite，Web/backend/chat-worker/governance-controller healthy。部署前确认无活跃任务，保留数据。
- 真实观测：部署后 24 次心跳采样最大年龄 0.551 秒、超时 0 次、指纹一致；真实会话绑定 readiness=ready。
- 浏览器：已部署 Web、合成 API 故障，1440×1000 深色；3 次 capabilities 请求覆盖未就绪、网络失败、恢复；草稿/历史保留，chat-send.disabled=false，点击后仅一次原草稿 POST。证据：logs/chat-capabilities-recovery/evidence.json、unavailable.png、recovered.png。未触发真实模型执行或推进 REQ-0027 业务状态。
- product_data_collection_observability：applicable；affected_layers：api、request_logs；复用既有请求观测，新增安全 reason_code 不含路径、凭证、原始错误或用户内容，无新日志事件、数据库字段、保留周期或生成客户端 schema。BUG 来源无 REQ 子文档同步；权限、安全边界及正式 openspec/specs 不变。

| 附件/截图 | 页面/状态 | 期望与实际偏差 | 检查方式 | 处置与证据 |
|---|---|---|---|---|
| f037c0c4 用户截图 | /chat；深色；展示 1912×1312；完善需求草稿待发 | 治理可写但发送持续禁用；期望服务恢复后自动可发且不丢草稿 | 心跳采样、DOM disabled、Network capabilities、1440px 截图 | 已修复；上述恢复截图及 evidence.json，按钮宽 40px，保留原布局 |

### AF-020 当前工作树事实源同步

- 反馈：完善需求因治理文件未提交被阻断；用户要求所有写入命令按当前 manifest/revision 校验并同步执行区。
- 根因 confirmed：preparation 的 Git status 前置检查把 dirty 等同于不可见；原 initialize_workspace 仅支持 generate candidate，普通 complete/review/sprint/opsx 缺少覆盖当前文件路径。
- 调整：取消 Git dirty 条件；校验 source_root 与投影 revision；发送时保存私有基线，worker 重验绑定、权限、revision 并自动同步治理文件与命令技能。源仓库不执行提交。已应用成果与完整工作区 manifest 精确一致时允许建立隔离基线后继续；额外修改阻断。
- 验证：后端命令矩阵覆盖 complete/review/sprint/opsx 未提交事实源、无关文档、凭证不导入、版本变化、工作区冲突，以及真实 writer 应用 generate 后同会话 complete 的合成链路。真实模型执行与业务完成态不由合成测试替代。
- product_data_collection_observability：applicable；affected_layers：api、request_logs、task_traces。沿用原请求/任务观测，无新事件、DB schema、保留周期或客户端 schema；私有基线不进入通用日志。API 安全错误回归校验无正文或本机路径泄漏。
- 文档一致性：更新 design、两份 capability delta、BUG AC-033、Sprint 验收与发布摘要、API 与部署说明。未改正式 openspec/specs、规则、技能、数据库、权限模型。
- 验证结果：后端 candidates/writer/scope/chat 合成回归 96 passed、1 skipped；前端两项 Toast 回归通过；Web 构建 TypeScript/Vite 通过。OpenSpec strict、中文与标题校验通过，diff whitespace 通过。
- 标准部署：已顺序执行 docker-down.sh self-storage-sqlite、docker-up.sh self-storage-sqlite，Web/backend/chat-worker/governance-controller 均 healthy。运行态 Web bundle 为 index-BzMM1hV-.js；Worker preparation.py SHA256 与本地一致。
- 真实运行态只读证据：后端当前源目录与治理投影 manifest_match=true；REQ-0027 完善 preflight=true，status=draft，document_present=true。未触发真实模型执行，未宣告需求已完善或业务状态已推进。
- Workflow Sync：Errors=0，BUG 验收 pending；两条已有 warning 为 root-cause confirmed、workaround active 子文档 status 语义未声明，保留原语义。AI Usage unavailable，command_run_count=0，不阻断返修。
- 当前状态：验收中 / 待复验。没有自动创建新 Issue/Change；归档仍需真实业务验收。

### AF-021 本地真实仓库工作区执行模式

- 反馈：用户选择将“产品支持本地真实仓库工作区执行模式：所有命令读取当前工作树并直接写入真实仓库，统一项目级写入协调、命令权限、产物校验与看板刷新，取消该模式的副本同步和候选二次应用”作为 BUG-0025 验收返修处理。
- 范围判断：属于 BUG-0025 产品内命令真实写入链路的执行模式补充，关联 `workspace_fact_source_stale` 与隔离工作区同步返修；不新建独立 REQ，不新增 API schema、DB schema、对象存储、客户端生成或生产共享部署能力。
- 根因 confirmed：当前 Chat 执行器与治理 candidate 默认以 `<workspace_root>/<conversation_id>` 会话副本作为工作区，并在 generate 成果后通过 candidate/application 二次应用到项目事实源；该模型不满足本地可信部署下“命令直接读写当前真实仓库”的用户期望，也让会话删除、diff 和 unknown task 恢复隐含依赖副本目录。
- 调整：新增显式 `workspace_mode: source` 绑定语义。平台 worker 在该模式下直接把执行工作区映射到 `source_root`，跳过副本准备；Chat execution 以 `workspace_id=source` 记录 claim/baseline 并校验真实源目录；preparation 初始化候选时只记录真实源 manifest/revision，不做 overlay 或隔离 baseline 提交；collect 校验 allowlist/manifest 后直接登记 `governance_applications` 为 `applied`，并把 candidate 标记为 `applied`，不再调用二次 `apply_candidate`。
- 协调与权限：真实仓库模式仍复用项目级 conversation/workspace claim、成员写权限、action allowlist、治理对象状态、产物 allowlist、manifest/revision 校验和 Task Trace 记录；写入结果由现有需求中心事实源刷新读取，不绕过看板投影。
- 清理与恢复：会话删除、diff 状态和 unknown task recovery 已识别 `workspace_id=source`，不再假定存在 `<workspace_root>/<conversation_id>` 副本；copy 模式仍保持原有副本同步和隔离应用链路。
- product_data_collection_observability：applicable；affected_layers：api、request_logs、task_traces、task_trace_spans。复用既有 Chat 执行、candidate/application 和 Task Trace 观测字段，仅新增绑定配置语义 `workspace_mode=source`；无 usage_events、DB schema、日志保留周期或客户端 schema 变化。真实本机路径不得进入对外错误正文。
- 文档一致性：更新 BUG AC-034/035、Change tasks、design、两份 capability delta、Sprint 验收报告、API 索引、部署说明和 trace；未修改正式 `openspec/specs/`，未新增规则、技能、数据库迁移或生产部署拓扑。
- 验证结果：`validate-root-cause-evidence` 通过；`py_compile` 覆盖 Chat execution、platform worker、cleanup、service、governance preparation 和新增后端测试。因当前本机缺少项目 Python 依赖环境，`uv` 不存在且系统 `python3` 缺少 `yaml`，pytest、Workflow Sync、OpenSpec 中文/标题校验需在项目依赖环境可用后复跑。

| 批次 | 时间 | 验收反馈 | 范围判断 | 证据状态 |
|---|---|---|---|---|
| AF-021 | 2026-09-30 12:19:57 | 产品支持本地真实仓库工作区执行模式；所有命令读取当前工作树并直接写入真实仓库，统一项目级写入协调、命令权限、产物校验与看板刷新，取消该模式副本同步和候选二次应用；关联 BUG-0025。 | 属于当前 Change 的本地可信执行模式返修；不新增 API schema、DB schema、对象存储、客户端生成或生产共享部署能力。 | confirmed |
| AF-001 | 2026-09-29 16:47:32 | `bug-generate` 产品准备态把内部治理约束直接裸露在 Chat 输入框；期望输入框只展示简洁命令，内部约束作为隐藏上下文或折叠详情传递。 | 属于当前 Change 的 Bug Generate 产品链路体验与写入准备边界返修，不新增 API、DB、权限、部署或对象存储边界。 | confirmed |
| AF-002 | 2026-09-29 17:06:04 | 发送 `/bug-generate BUG-0024` 后，历史消息仍展示完整内部治理约束；输入框上方 `prepared` 且 0 文件的治理成果面板一直显示，用户不理解其用途。 | 属于当前 Change 的 Bug Generate 产品链路展示层返修，不新增 API、DB、权限、部署或对象存储边界。 | confirmed |
| AF-003 | 2026-09-29 17:17:44 | 命令执行完后仍要求用户再审阅并点击“确认应用”，对 generate 命令显得多此一举；期望覆盖所有已接入真实治理候选链路的命令，校验通过后自动应用，异常时才人工确认。 | 属于当前 Change 的真实候选与应用链路体验返修，覆盖 `req-generate` 与 `bug-generate`；不扩展 complete、review、sprint-propose、opsx 系列真实写入能力，不新增 API、DB、权限、部署或对象存储边界。 | confirmed |
| AF-004 | 2026-09-29 17:26:38 | Chat 对话区仍显示 `BUG-0024-capture / 正在生成 / 查看成果` 治理成果大面板；期望所有命令都不显示该面板。 | 属于当前 Change 的 Chat 治理结果展示返修，不改变后端写入边界、不扩展未接入命令能力、不新增 API、DB、权限、部署或对象存储边界。 | confirmed |
| AF-005 | 2026-09-29 17:36:23 | Chat 对话区 AI assistant 输出没有占满消息历史可用宽度；期望 assistant 输出满宽展示，不再受 `.chat-message` 的 `720px/72%` 限制，用户消息仍保持右侧气泡宽度限制。 | 属于当前 Change 的 Chat 前端布局返修，不改变治理写入、后端 API、DB、权限、部署或对象存储边界。 | confirmed |
| AF-006 | 2026-09-29 17:58:01 | 执行中 assistant 消息外层历史轨道仍未占满对话区；执行完成后 pending candidate 没有自动应用和刷新事实源；从历史打开会话时又出现治理成果面板。 | 属于当前 Change 的 Chat 布局、真实候选自动应用和历史恢复展示返修，不改变后端 API、DB、权限、部署或对象存储边界。 | confirmed |
| AF-007 | 2026-09-29 18:15:32 | 执行中 assistant 消息视觉块仍不像占满整行；期望不仅取消源码 max-width，还要让 assistant 正文 bubble/markdown 容器运行态 computed width 等于消息历史可用宽度。 | 属于当前 Change 的 Chat 前端视觉块与回归证据返修，不改变治理写入、后端 API、DB、权限、部署或对象存储边界。 | confirmed |
| AF-008 | 2026-09-29 18:28:21 | 产品运行态疑似仍使用旧前端构建，导致治理面板和人工应用流程回退；期望重新构建部署 Web 产物，并用 dist/运行态 bundle、历史入口 DOM 和 governance_applications 自动创建断言确保 `localhost:18102` 不再包含人工应用面板文案，`bug-generate` 完成后生成 `bug.md` 并流转状态。 | 属于当前 Change 的运行态部署、自动应用门禁和回归证据返修；不新增 DB schema、API schema、对象存储或未接入命令能力，但调整 generate 写入门禁从人工维护窗口收敛为 controller-ready。 | confirmed |
| AF-009 | 2026-09-29 19:10:00 | 生成命令产品链路仍未达到预期：需要将 `req-generate`/`bug-generate` 的低风险候选自动应用迁移到后端 controller；发送前增加执行器 sandbox/dry-run preflight；区分 `executor_unavailable` 与 `governance_validation_failed`；Chat 历史只保存 `display_prompt`，不落库内部治理约束；所有历史入口不恢复 `GovernanceResult` 面板，并补充运行态 DOM、Network、DB、文件事实源回归断言。 | 属于当前 Change 的真实生成链路责任边界返修：前端不再承担自动应用写入，后端负责执行 prompt 恢复、preflight、候选收集、application 自动创建与错误分类；不新增 DB schema、对象存储或未接入命令能力。 | confirmed |
| AF-010 | 2026-09-29 20:22:29 | 历史入口再次出现 `已应用 / 查看成果` 治理成果面板；判断为旧前端实例或浏览器缓存把已移除组件恢复到运行态。期望应用启动时校验构建版本，旧 bundle 自动刷新，历史入口清理旧 DOM，并补充浏览器运行态 Network/DOM 证据。 | 属于当前 Change 的 Web 运行态缓存、自愈和历史入口 DOM 清理返修；不新增 API、DB schema、对象存储、权限模型或未接入命令能力。 | confirmed |
| AF-011 | 2026-09-29 23:01:37 | Chat 推理程度默认值当前为 High；期望新会话默认显示 Low，降低默认执行成本和等待时间。 | 属于当前 Change 的 Chat 执行配置默认值返修；不新增 API、DB schema、权限、部署、对象存储或未接入命令能力。 | confirmed |
| AF-012 | 2026-09-29 23:13:30 | 前序多次出现“镜像服务未更新至最新”；实际验收曾使用裸 `docker compose ... backend web` 局部重建，未统一走 `bash scripts/docker-down.sh self-storage-sqlite && bash scripts/docker-up.sh self-storage-sqlite`。期望 BUG-0025 运行态部署和验收证据统一到项目标准脚本入口，覆盖 Web、backend、chat-worker 与 governance-controller。 | 属于当前 Change 的部署验收口径与证据返修；不新增部署拓扑、端口、环境变量、API、DB schema、权限或对象存储能力。 | confirmed |
| AF-013 | 2026-09-30 08:23:25 | `req-generate` 执行中 assistant 消息仍未占满整行；期望所有 role=assistant / AI 输出，不区分 req-generate、bug-generate、普通 Chat、执行中、完成后或历史恢复，外层 block、article、bubble、markdown、TurnActivity 与 status/alert 文案运行态 computed width 均占满消息历史可用宽度，用户消息仍保持右侧气泡宽度限制。 | 属于当前 Change 的 Chat 前端布局返修，不改变治理写入、后端 API、DB schema、权限、部署或对象存储边界。 | confirmed |
| AF-014 | 2026-09-30 09:39:42 | Chat assistant 执行状态条位置异常：工具调用/完成状态条漂在消息正文上方中间，和 assistant 头像及正文左边界脱节；期望状态条作为轻量 meta 左对齐到 assistant 内容列，正文和执行输出继续保持满宽。 | 属于当前 Change 的 Chat 前端布局返修，是 AF-013 满宽规则的细化，不改变治理写入、后端 API、DB schema、权限、部署或对象存储边界。 | confirmed |
| AF-015 | 2026-09-30 10:10:16 | 发送消息后先显示“正在连接工作台”，随后裸露 `NetworkError when attempting to fetch resource.`；同时已生成成功的消息仍在页面中。期望 chat/governance/events fetch 异常统一包装，导航或历史恢复 AbortError 不渲染错误，工作台初始化、项目绑定、执行轨迹轮询错误分层展示，已生成成功消息不被全局错误覆盖。 | 属于当前 Change 的 Chat 工作台异常展示和局部轮询容错返修，不改变治理写入、后端 API schema、DB schema、权限、部署、安全或对象存储边界。 | confirmed |
| AF-016 | 2026-09-30 10:46:48 | `req-complete` 执行中 assistant 消息仍未占满整行；期望所有 role=assistant 的运行中输出不按命令场景生效，覆盖 `req-generate`、`req-complete`、`bug-generate`、`bug-complete`、review、sprint、opsx 和普通 Chat，TurnActivity、status/alert、正文 bubble、markdown 和 assistant 内容列 computed width 均等于消息历史可用宽度。 | 属于当前 Change 的 Chat 前端布局与回归矩阵返修，不改变治理写入、后端 API schema、DB schema、权限、部署、安全或对象存储边界。 | confirmed |
| AF-017 | 2026-09-30 11:00:40 | `/req-complete REQ-0027-requirement-center-command-chain-realization` 在产品运行态仍允许执行，但执行器 `/work` 只看到旧的 `REQ-0027-capture`、缺少 `requirement.md`，导致命令失败；期望不只修 `req-complete`，所有产品写入型命令发送前都以后端/执行器同一 `/work` 快照校验完整对象 ID、registry path、trace 状态和关键文档存在，不一致时阻断并提示 `workspace_fact_source_stale`。 | 属于当前 Change 的产品命令写入链路发送前门禁返修；统一覆盖 complete、review、sprint、opsx 等对象写入命令，不改变 API schema、DB schema、权限、部署拓扑、安全或对象存储边界。 | confirmed |
| AF-018 | 2026-09-30 11:22:03 | 点击需求中心 `完善需求` 后 Toast 仍统一提示“执行器工作区快照不可校验，请确认标准部署已更新后重试”；期望 `workspace_fact_source_stale` 区分本地治理事实源未提交/未同步、标准部署未更新、Git 快照不可读三类原因，并提示具体阻断文件类别和处理建议。 | 属于当前 Change 的产品命令写入链路阻断提示返修；复用既有 `workspace_fact_source_stale` 错误 kind，只扩展安全错误详情和前端展示，不改变 DB schema、权限、部署拓扑、安全或对象存储边界。 | confirmed |
| AF-019 | 2026-09-30 11:41:41 | 用户指出该逻辑与 Codex 命令不一致：产品 backend 的 `governance_root` 是 `/app/governance` 治理目录投影且不含 `.git`，不应直接在该目录执行 `git status`；期望改用 `source_root` Git 快照或产品化 manifest/revision 校验，点击 `完善需求` 不再误报 Git 快照不可读。 | 属于当前 Change 的产品命令写入链路事实源门禁语义返修；调整 Git 快照根目录和标准 Chat 部署只读挂载，不新增 API schema、DB schema、权限模型、安全边界或对象存储能力。 | confirmed |

## 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件 `codex-clipboard-c1f11dd1-4009-4cad-9f47-809a2151227c.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；点击需求中心 `生成 Bug` 后进入 Chat 准备态；深色主题；输入框待发送 | 产品准备态 Chat 输入框 | 输入框只展示 `/bug-generate BUG-0024-capture` 这类简洁命令；内部治理约束不直接占据输入框正文 | 输入框显示 `/bug-generate BUG-0024-capture` 后紧跟“所有生成Markdown必须有中文业务title...”等内部治理约束 | 文案暴露、信息层级过重、用户理解成本高 | 用户截图 + 代码路径核查：`RequirementCenterPage.tsx` 将 `result.prompt` 写入 `moonbox.governance.prompt`，`ChatWorkbenchPage.tsx` 将该 key 作为输入框草稿，`Composer.tsx` 按草稿直接发送 | 本次修复：后端 preparation 只返回短命令 display_prompt；Chat turn 和消息历史只保存短命令；执行器内部约束由后端根据 candidate 恢复 | 本台账 AF-001、AF-009；前端用例 `chat-composer.test.tsx`，后端用例 `test_governance_candidates.py` |
| 用户附件 `codex-clipboard-0bc4837d-c9c5-4a6e-88e9-81a0d48dc41a.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；发送 `/bug-generate BUG-0024-capture` 后等待执行结果；深色主题 | 历史消息气泡与输入框上方治理成果面板 | 历史消息只展示用户可理解的短命令；内部治理约束不出现在消息气泡。尚无文件成果时，不显示占用空间的大型治理成果面板 | 用户消息气泡展示完整内部治理约束；`BUG-0024-capture / 等待发送 / 查看成果 · 0 个文件` 面板常驻 | 文案暴露、空成果面板占位、状态含义不清 | 用户截图 + 代码路径核查：`ConversationMessages.tsx` 直接渲染 `turn.prompt`；`GovernanceResult.tsx` 对 `prepared` 且 0 文件 candidate 仍渲染面板 | 本次修复：历史消息展示层识别治理执行 prompt 并只显示第一行命令；`prepared` 且 0 文件时隐藏治理成果面板 | 本台账 AF-002；前端用例 `chat-messages.test.tsx` 与 `governance.test.tsx` |
| 用户附件 `codex-clipboard-fc195caa-8226-4814-a0c2-8a4a686c50ff.png`、`codex-clipboard-5785b9c5-e981-45dc-8bd9-fc53df9baa51.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`bug-generate` 已生成 4 个文件，状态为 `待应用成果`；用户打开“审阅治理成果”弹窗 | 自动应用与人工确认链路 | 已接入真实治理候选链路的 generate 命令在候选合法后由后端自动创建 application 并写入项目事实源；前端只轮询已有 operation | 生成完成后仍停留在 `待应用成果`，需要用户勾选维护窗口并点击“确认应用” | 低风险生成命令步骤过多，且写入责任落在前端 UI | 用户截图 + 代码路径核查：`GovernanceResult.tsx` 对 `pending` candidate 只展示手动确认入口；后端 `apply_candidate` 已执行 confirmed、manifest、revision 与 binding revision 校验 | 本次修复：`collect` 在候选合法后直接调用后端 `apply_candidate` 入队；`GovernanceResult` 不再 POST application，只轮询后端 operation 并轻量提示 | 本台账 AF-003、AF-009；后端用例 `test_governance_candidates.py`、前端用例 `governance.test.tsx` |
| 用户附件 `codex-clipboard-529b08ea-1e85-4886-95cc-752786646856.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`bug-generate` 正在执行；深色主题；对话主区域 | Chat 主对话区治理结果展示 | 所有命令都不显示治理成果大面板；generate 后台自动应用，异常通过轻量提示或轨迹处理 | 对话区仍显示 `BUG-0024-capture / 正在生成 / 查看成果 · 0 个文件` 大面板 | 面板占据对话主区域，用户认为无必要且所有命令均不应显示 | 用户截图 + 代码路径核查：`ChatWorkbenchPage.tsx` 固定渲染 `GovernanceResult`，`GovernanceResult.tsx` 负责卡片、查看成果按钮和审阅弹窗 | 本次修复：`GovernanceResult` 改为不可见后台控制器；Chat 页面只接收自动应用成功刷新和轻量错误 toast；不再渲染治理成果卡片或审阅弹窗 | 本台账 AF-004；前端用例 `governance.test.tsx` |
| 用户附件 `codex-clipboard-c66e473e-f934-4680-9440-2de0aed78bea.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`bug-generate` assistant 回复；深色主题；消息历史区域 | Chat assistant 消息布局 | assistant 输出应占满消息历史可用宽度；用户命令消息仍保持右侧气泡宽度限制 | assistant 回复内容被压在左侧较窄列，未使用剩余消息历史宽度 | 共享 `.chat-message` 宽度限制错误作用到 assistant 消息 | 用户截图 + 代码路径核查：`.turn-assistant .chat-message` 此前仅设置 flex/gap，仍继承 `.chat-message { width: min(720px, 72%) }`；`.chat-message-user` 已有独立右侧气泡宽度限制 | 本次修复：assistant message 与 bubble 显式 `width: 100%`、`max-width: none`；保留 `.chat-message-user` 的 `min(760px, 88%)` 与 `max-width: 88%` | 本台账 AF-005；前端用例 `chat-messages.test.tsx` |
| 用户附件 `codex-clipboard-fd85eeda-4509-4f86-8ce7-46092a27be9e.png`、`codex-clipboard-99a52e20-d07e-4720-8630-34e034d3c50b.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`bug-generate` 执行中与执行完成；深色主题；历史会话恢复 | Chat assistant 消息轨道、自动应用和历史恢复治理展示 | assistant 输出外层历史轨道占满对话区可用宽度；pending candidate 已由后端创建 application 并刷新事实源；历史打开只轮询 operation，不恢复治理成果大面板 | 执行中 assistant 文本仍处在窄轨道；完成后仍显示 `待应用成果` 和 `查看成果 · 4 个文件`，未自动应用；历史打开会话恢复面板 | 外层轨道限宽、自动应用责任放在前端导致历史恢复不稳定、历史恢复仍有旧面板风险 | 用户截图 + 代码路径核查：`.chat-message-history` 仍 `max-width: 1120px`；`GovernanceResult` 自动应用曾以 pending、有文件和 manifest 为门禁，并在前端发起 POST；`ChatWorkbenchPage` 轮询候选并挂载后台控制器 | 本次修复：`.chat-message-history` 改为 `width: 100%; max-width: none`；后端 collect 自动创建 application；历史入口只轮询后端 operation，补充 Network/DOM 断言确保无 application POST 且不渲染面板文案 | 本台账 AF-006、AF-009；前端用例 `chat-messages.test.tsx`、`governance.test.tsx`、`chat-workbench.test.tsx` |
| 用户附件 `codex-clipboard-0f5ace22-c4cb-4966-b23b-bc74dbdea89f.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`bug-generate` 执行中；深色主题；assistant 文本消息 | Chat assistant 正文视觉块 | assistant 正文 bubble 与 markdown 容器在运行态 computed style 中铺满消息历史可用宽度，视觉块不再只表现为自然文本宽度 | assistant 文本虽然在宽轨道内，但没有明显整行视觉块，验收感知仍为“没有占满整行” | 只校验 CSS 源码规则不足，assistant column/bubble/markdown 容器缺少完整 stretch/full-width 运行态断言 | 用户截图 + 代码路径核查：`chat-assistant-col`、`.turn-assistant .chat-message-bubble` 与 `.turn-assistant .chat-markdown` 是实际承载正文的视觉块层级 | 本次修复：assistant column、bubble、markdown 均显式 stretch/full-width/box-sizing，并补 DOM + computed style 回归断言 | 本台账 AF-007；前端用例 `chat-messages.test.tsx` |
| 用户附件 `codex-clipboard-80d225ca-e11f-4361-b239-1dda31b47c54.png`、`codex-clipboard-2b089c6c-6d86-4444-b7fb-c881f0375530.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`bug-generate` 已完成；深色主题；历史入口恢复 | 运行态构建、自动应用和历史恢复 | `localhost:18102` 应使用最新 Web 构建，不包含人工治理成果面板文案；历史打开不恢复面板；pending candidate 自动创建 application 并写入事实源 | 页面仍显示旧人工面板，`bug.md` 未生成、状态未流转 | 运行态 dist 未部署最新前端，且 generate 写入仍可能被人工维护窗口门禁阻断 | 用户截图 + 运行态证据：`src/web/dist/assets/index-*.js` 仍包含旧文案；`data/runtime/governance/` 无 `maintenance.json`；数据库中 BUG-0024 有 pending candidate 但无 application，事实源无 `bug.md` | 本次修复：新增 dist/运行态 bundle 文案断言；重新构建部署 Web；generate 候选改用 controller-ready 自动应用门禁；补历史入口 DOM/Network 和 application 创建断言 | 本台账 AF-008；`assert:runtime-bundle`、`chat-workbench.test.tsx`、`test_governance_writer.py`、运行态 `localhost:18102` 检查 |
| 本轮文字反馈 AF-009 | `/bug-generate` / `/req-generate` 产品生成链路；后端执行器、Chat 历史、历史入口恢复 | 后端 controller 生成链路 | 自动应用应由后端完成；发送前应 preflight；消息历史只保存 display_prompt；错误码可区分执行器不可用与治理校验失败 | 旧实现依赖前端隐藏 prompt 和前端自动 application，执行器失败与治理失败混淆，历史入口可能恢复面板或无法写入事实源 | 责任边界错误，导致多轮修复后仍表现为无法生成文档或旧面板回退 | 用户反馈 + 代码路径核查：`preparation.prepare/check_send/collect/list_candidates`、`chat.execution.run_claim`、`Composer.tsx`、`GovernanceResult.tsx` | 本次修复：后端 display/execution prompt 分离、preflight、错误码分类、collect 自动 application、候选列表返回 application；前端只发送 display_prompt、只轮询 operation、不渲染面板 | 本台账 AF-009；后端/前端/构建验证记录 |
| 用户附件 `codex-clipboard-35d09be9-5698-4b5b-9698-349c6141ebad.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；历史入口打开已完成 `bug-generate` 会话；深色主题 | 旧 bundle 与历史入口旧 DOM 清理 | 新前端构建应在应用启动时标记构建版本；发现 HTML 最新资产与当前脚本不一致时自动刷新；历史入口不得恢复任何旧治理成果面板 DOM | 页面仍出现旧的 `BUG-0024-capture / 已应用 / 查看成果 · 4 个文件` 面板 | 源码和 dist 已移除面板，但活跃旧 SPA 实例或浏览器缓存仍可保留旧脚本、旧 DOM 或历史节点，缺少运行时自愈机制 | 用户截图 + 运行态核查：当前源码无面板渲染路径，dist 文案断言通过但浏览器历史入口仍可见旧节点 | 本次修复：新增 `runtimeBuild.ts` 构建版本校验和旧 bundle reload；Chat 历史入口调用旧面板 DOM 清理；补运行态 bundle、Playwright DOM、Network 证据 | 本台账 AF-010；`runtimeBuild.test.ts`、`chat-workbench.test.tsx`、运行态 `localhost:18102` DOM 检查 |
| 本轮文字反馈 AF-011 | Chat 输入框执行配置区；新建会话默认配置 | 推理程度默认值 | 新会话和 capabilities 默认推理程度应为 Low；capabilities 未加载完成时前端 fallback 也应显示 Low | 默认值为 High | 后端 `execution_config().defaults.reasoning` 与前端 `fallbackExecution.reasoning` 均硬编码为 high | 只读定位：`src/backend/app/chat/settings.py` 与 `src/web/src/components/chat/Composer.tsx`；测试断言也使用 high | 本次修复：后端 defaults 与前端 fallback 同步改为 low，并补前端 fallback 用例 | 本台账 AF-011；`test_chat.py`、`chat-composer.test.tsx` |
| 本轮文字反馈 AF-012 | `localhost:18102` Chat + governance 产品运行态部署；BUG-0025 验收证据 | 部署验收入口 | 运行态验收应使用项目标准脚本 `bash scripts/docker-down.sh self-storage-sqlite` 与 `bash scripts/docker-up.sh self-storage-sqlite`，由脚本按 `.env` 自动加载 Chat/governance overlay 或显式 `--chat-platform`；验证服务集合和 bundle 均为最新 | 既有台账中仍记录裸 `docker compose -f docker-compose.yml up -d --build web/backend web`，并出现 orphan `chat-worker` / `governance-controller` 提示，容易造成局部服务更新而产品链路仍回退 | 部署口径不统一、验收证据只覆盖局部 Compose 服务，未强制证明 worker/controller 与 Web bundle 同步更新 | 用户反馈 + 部署脚本核查：`scripts/docker-common.sh` 在 local-codex/chat-platform 模式追加 `deploy/docker-compose.chat-platform.yml` 与 `deploy/docker-compose.governance.yml`，并把 `chat-worker`、`governance-controller` 纳入服务集合；裸 compose 不经过该服务解析 | 本次修复：部署文档和 BUG-0025 验收计划统一要求使用根脚本配对重启；裸 compose 降级为基础局部调试，不作为 Chat + governance 产品验收依据 | 本台账 AF-012；`docs/02-deployment.md`；脚本部署与服务健康验证记录 |
| 用户附件 `codex-clipboard-441ae6e3-dbd0-4940-a278-5ad6721fc285.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`req-generate` 执行中；深色主题；assistant 运行中状态文案 | Chat assistant 全链路满宽 | 所有 role=assistant / AI 输出均应占满消息历史可用宽度，包括 req-generate、bug-generate、普通 Chat、执行中、完成后、历史恢复、TurnActivity 和 status/alert 文案；用户消息继续保持右侧气泡限制 | 运行中 `REQ-0027...` assistant 文案仍只占左侧文本宽度，视觉上没有铺满整行 | 前序修复覆盖最终 Markdown/bubble 较多，漏掉执行中 `TurnActivity` 与 `p[role=status]` 渲染链 | 用户截图 + 代码路径核查：`ConversationMessages.tsx` 在 bubble 前独立渲染 `TurnActivity`，`TurnActivity.tsx` 将执行中输出渲染为 `p[role="status"]`；旧 CSS 仍允许 activity 子层按内容收缩 | 本次修复：`chat-workbench.css` 显式让 `.turn-assistant .chat-turn-activity`、其子层、`status/alert` 文案 stretch/full-width/box-sizing；补 Vitest DOM/computed style 与 Playwright 浏览器宽度采样 | 本台账 AF-013；`chat-messages.test.tsx`；`tests/chat-assistant-width.cjs` |
| 用户附件 `codex-clipboard-fa823727-9f96-406a-b100-223ad91c0d62.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`bug-generate` 历史/完成态；深色主题；assistant 消息头部与正文之间 | Chat assistant 工具调用/完成状态条 | 状态摘要应作为轻量 meta 左对齐到 assistant 内容列，贴近头像与正文左边界；正文、markdown 与执行中 status/alert 输出继续占满内容列宽 | 工具调用/完成状态条漂在正文上方中间，和 assistant 头像及正文左边界脱节 | AF-013 将 `.turn-assistant .chat-turn-activity > *` 全部强制满宽，误把 `button.chat-tool-summary` 当成执行输出块；视觉上变成漂浮的大块状态条 | 用户截图 + 代码路径核查：`ConversationMessages.tsx` 在正文 bubble 前渲染 `TurnActivity`；`TurnActivity.tsx` 的 `button.chat-tool-summary` 是工具摘要，`p[role="status"]` 才是执行中正文输出；CSS 子元素满宽规则误伤摘要按钮 | 本次修复：`chat-workbench.css` 将满宽规则改为 `:not(.chat-tool-summary)`，并让 summary `align-self:flex-start`、`width:fit-content`、透明背景；Playwright 断言 summary left 等于 assistant column left、summary width 小于 column，status/bubble 仍满宽 | 本台账 AF-014；`chat-messages.test.tsx`；`tests/chat-assistant-width.cjs` |
| 用户附件 `codex-clipboard-2733f99c-b395-4879-8f0c-a6b1583692aa.png`、`codex-clipboard-db0f08c5-8ada-4635-9b1f-e65ddb8b3aed.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`req-generate` 完成后或历史恢复；深色主题；顶部连接态、错误提示与 assistant 成功消息共存 | Chat 工作台网络错误与局部轮询失败 | fetch 网络异常应转为中文局部提示；导航、历史恢复或卸载导致的 AbortError 不渲染错误；工作台初始化、项目绑定、消息读取、执行轨迹轮询应分层提示；已生成成功消息不被后续轮询失败覆盖为全局错误 | 页面显示 `NetworkError when attempting to fetch resource.`，顶部连接状态变为不可用；但下方 assistant 已显示 `REQ-0027 PRD` 已生成成功 | `chatRequest`、`governanceRequest`、`readChatEvents` 和多个 catch 分支直接透传浏览器原生 `error.message`；selected 会话的 turns/refresh 局部失败也会写入全局 `model.error`，导致成功消息旁出现全局连接错误 | 用户截图 + 代码路径核查：`chatApi.ts`、`chatEvents.ts`、`governanceApi.ts`、`useChatWorkbench.ts`、`ChatWorkbenchPage.tsx`、`ConversationMessages.tsx`、`ExecutionPanel.tsx`、`TurnActivity.tsx` | 本次修复：新增 chat/governance 错误归一化；NetworkError/Failed to fetch 转中文提示；AbortError 保留给调用方按 signal 静默；turns 与 refreshSelected 局部失败不再覆盖全局错误；选中会话后全局工作台错误不遮盖已有消息 | 本台账 AF-015；`chat-events.test.ts`、`governance.test.tsx`、`chat-messages.test.tsx`、`chat-workbench.test.tsx` |
| 用户附件 `codex-clipboard-2eb05297-c164-4919-bbe1-b01fa5500fd3.png` | `/chat?conversation_id=<conversation>&space_id=<space>`；`req-complete` 执行中；深色主题；assistant 运行中输出 | Chat assistant 运行中消息满宽规则 | 所有 role=assistant 的运行中输出必须按同一布局规则铺满消息历史可用宽度，不得按命令名或 generate 场景白名单生效；TurnActivity、status/alert、bubble、markdown 和 assistant 内容列 computed width 均应等于内容列宽 | `/req-complete ...` 的 assistant 运行中输出仍只占左侧内容宽度，右侧留白明显 | 前序回归矩阵只覆盖 generate、普通完成和历史恢复，且通用 `.chat-turn-activity > *` 限宽规则仍可能影响非 generate 运行中输出 | 用户截图 + 代码路径核查：运行中文案来自 `TurnActivity.tsx` 的 `p[role="status"]`，外层由 `ConversationMessages.tsx` 的 `.turn-assistant` 渲染；样式中通用 activity 限宽需只作用于非 assistant | 本次修复：以 `.turn-assistant` 角色选择器统一 stretch assistant 外层 block、article、内容列、TurnActivity、status/alert、bubble 与 markdown；将非 assistant activity 限宽隔离到 `.chat-message-block:not(.turn-assistant)`；Playwright 增加 req-complete、complete、review、sprint、opsx 和普通 Chat running 矩阵 | 本台账 AF-016；`chat-messages.test.tsx`、`tests/chat-assistant-width.cjs` |

## 偏差证据

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E-AF-001 | screenshot | 用户附件 `codex-clipboard-c1f11dd1-4009-4cad-9f47-809a2151227c.png` | Chat 输入框内展示完整内部治理约束文案 | 证明用户可见输入框存在内部约束裸露 |
| E-AF-002 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 需求中心准备成功后直接把后端 `result.prompt` 写入 `moonbox.governance.prompt` | 证明完整 prompt 被当作可见草稿来源 |
| E-AF-003 | code_path | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx` | Chat 页面从 `moonbox.governance.prompt:<conversation_id>` 初始化 `draftState.text` | 证明裸露文案会进入输入框 |
| E-AF-004 | code_path | `src/web/src/components/chat/Composer.tsx` | Composer 发送时此前只使用 `draft` 构造 signature 与 turn prompt | 证明可见草稿与执行 prompt 未分离 |
| E-AF-005 | screenshot | 用户附件 `codex-clipboard-0bc4837d-c9c5-4a6e-88e9-81a0d48dc41a.png` | 发送后的用户消息气泡仍显示完整内部治理约束，且 `prepared / 0 files` 面板常驻 | 证明隐藏执行上下文仍通过历史消息与空成果面板外露 |
| E-AF-006 | code_path | `src/web/src/components/chat/ConversationMessages.tsx` | 用户消息展示层按 `row.content` 渲染，未识别治理执行 prompt | 证明消息历史会继续展示内部约束 |
| E-AF-007 | code_path | `src/web/src/components/chat/GovernanceResult.tsx` | 只要存在 candidate 即渲染治理成果面板，`prepared` 且 0 文件未被隐藏 | 证明空成果面板常驻来源 |
| E-AF-008 | screenshot | 用户附件 `codex-clipboard-fc195caa-8226-4814-a0c2-8a4a686c50ff.png`、`codex-clipboard-5785b9c5-e981-45dc-8bd9-fc53df9baa51.png` | `bug-generate` 已生成 4 个文件后仍停留在 `待应用成果`，需要用户再次确认应用 | 证明 generate 命令存在不必要的二次确认体验 |
| E-AF-009 | code_path | `src/web/src/components/chat/GovernanceResult.tsx` | `pending` candidate 此前只显示手动确认 checkbox 与“确认应用”按钮 | 证明自动应用缺失点在前端治理成果组件 |
| E-AF-010 | code_path | `src/backend/app/governance/writer.py` | `apply_candidate` 已校验 confirmed、manifest hash、candidate revision、binding revision，并在 worker 中执行 allowlist 与冲突校验 | 证明自动提交仍复用后端受控写入门禁，不绕过事实源安全校验 |
| E-AF-011 | screenshot | 用户附件 `codex-clipboard-529b08ea-1e85-4886-95cc-752786646856.png` | Chat 主对话区仍显示 `BUG-0024-capture / 正在生成 / 查看成果` 大面板 | 证明所有命令均不应显示治理成果大面板的验收偏差 |
| E-AF-012 | code_path | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx` 与 `src/web/src/components/chat/GovernanceResult.tsx` | Chat 页面固定挂载 `GovernanceResult`，组件负责卡片、查看成果按钮和审阅弹窗 | 证明移除面板需要在共享治理结果组件层统一处理 |
| E-AF-013 | screenshot | 用户附件 `codex-clipboard-c66e473e-f934-4680-9440-2de0aed78bea.png` | assistant 回复正文只占据消息历史左侧窄列，右侧空白明显 | 证明 assistant 消息宽度未占满可用区域 |
| E-AF-014 | code_path | `src/web/src/styles/chat-workbench.css` | `.chat-message` 设置 `width: min(720px, 72%)`；`.turn-assistant .chat-message` 此前未覆盖 width/max-width | 证明 assistant 被共享消息宽度限制收窄 |
| E-AF-015 | screenshot | 用户附件 `codex-clipboard-fd85eeda-4509-4f86-8ce7-46092a27be9e.png` | 执行中 assistant 消息仍在窄历史轨道内展示 | 证明外层 `.chat-message-history` 限宽仍影响 assistant 满宽体验 |
| E-AF-016 | screenshot | 用户附件 `codex-clipboard-99a52e20-d07e-4720-8630-34e034d3c50b.png` | 执行完成后仍显示 `待应用成果`、`查看成果 · 4 个文件` 治理大面板 | 证明 pending candidate 自动应用和历史恢复无面板仍未满足验收 |
| E-AF-017 | code_path | `src/web/src/styles/chat-workbench.css` | `.chat-message-history` 此前仍保留 `max-width: 1120px` | 证明上轮只解除内层 message 限制，外层历史轨道仍收窄 |
| E-AF-018 | code_path | `src/web/src/components/chat/GovernanceResult.tsx` | 自动应用由 `pending` candidate 触发，组件是历史恢复时治理候选的后台控制器 | 证明应在该组件层同时处理自动应用和不渲染面板 |
| E-AF-019 | screenshot | 用户附件 `codex-clipboard-0f5ace22-c4cb-4966-b23b-bc74dbdea89f.png` | 执行中 assistant 文本在宽轨道内仍缺少整行视觉块感知 | 证明需修正正文 bubble/markdown 容器运行态铺满，而非只取消外层 max-width |
| E-AF-020 | code_path | `src/web/src/styles/chat-workbench.css` 与 `src/web/src/components/chat/ConversationMessages.tsx` | assistant 正文由 `.chat-assistant-col`、`.chat-message-bubble` 和 `.chat-markdown` 承载 | 证明 computed style 回归应覆盖真实视觉块层级 |
| E-AF-BUNDLE-001 | runtime_bundle | `src/web/dist/assets/index-BtAZASzR.js` | 运行态构建产物仍包含 `待应用成果`、`查看成果`、`审阅治理成果`、`确认应用` 文案 | 证明产品服务使用的 dist 未刷新，会把已修源码回退成旧治理面板 |
| E-AF-022 | runtime_state | `data/runtime/governance/` | 运行目录只有 `controller-ready.json` 与 lock 文件，没有 `maintenance.json` | 证明 generate 自动应用若仍依赖人工维护窗口，会在运行态继续无法写入事实源 |
| E-AF-023 | database | `governance_candidates` / `governance_applications` / BUG-0024 事实源查询 | BUG-0024 存在 pending candidate 且无 application；`issues/bugs/plan/BUG-0024-capture/bug.md` 不存在，trace 仍为 captured | 证明旧运行态没有创建应用操作，也没有写入 `bug.md` 或流转状态 |
| E-AF-024 | code_path | `src/backend/app/governance/preparation.py` 与 `src/backend/app/chat/execution.py` | preparation 返回 display_prompt，run_claim 根据候选恢复 execution prompt；check_send 执行 isolated preflight；collect 成功后自动调用后端 apply_candidate | 证明生成链路责任迁移到后端，消息历史不再需要保存内部治理约束 |
| E-AF-025 | code_path | `src/web/src/components/chat/GovernanceResult.tsx` | 组件不再调用 `/governance-candidates/{id}/applications`，只轮询 candidate.application 或 legacy operation id | 证明历史入口不再由浏览器补发应用请求，也不会恢复治理成果面板 |
| E-AF-026 | screenshot | 用户附件 `codex-clipboard-35d09be9-5698-4b5b-9698-349c6141ebad.png` | 历史入口仍显示旧治理成果面板，状态为 `已应用` 且包含查看成果按钮 | 证明仅移除源码组件不足以覆盖活跃旧 SPA 实例或缓存脚本回退 |
| E-AF-027 | code_path | `src/web/src/runtimeBuild.ts` 与 `src/web/vite.config.ts` | Vite 构建注入 `__MOONBOX_BUILD_ID__`；运行时记录 `<html data-moonbox-build-id>`，并以 `cache: no-store` 拉取最新 HTML 比对当前脚本资产 | 证明应用启动时具备旧 bundle 检测和一次性自动刷新能力 |
| E-AF-028 | code_path | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx` 与 `src/web/src/runtimeBuild.ts` | Chat 历史入口按会话和 candidate 变化执行旧治理面板 DOM 清理 | 证明旧 DOM 节点即使来自历史缓存，也会在当前页恢复时被移除 |
| E-AF-029 | runtime_bundle | `http://localhost:18102` | 运行态 HTML 加载 `/assets/index-BcoXmN7-.js` 和 `/assets/index-BuEJyOc-.css`，旧治理面板禁用文案命中数为 0 | 证明已部署运行态 bundle 不再包含旧面板文本 |
| E-AF-030 | browser_dom | `http://localhost:18102/chat?conversation_id=77acd2e1-9339-5b97-ad52-8ead46674995&space_id=space_e4f61f87dfa442429e58862ddaa8df49` | Playwright 运行态 DOM：`buildId=mumn7qzm-f2xr1z`、`forbiddenHits=[]`、`panelCount=0` | 证明浏览器运行态具备构建版本标记且历史入口未渲染旧治理面板 |
| E-AF-031 | code_path | `src/backend/app/chat/settings.py` | `execution_config().defaults.reasoning` 此前为 `high` | 证明后端 capabilities 默认推理程度来源 |
| E-AF-032 | code_path | `src/web/src/components/chat/Composer.tsx` | `fallbackExecution.reasoning` 此前为 `high` | 证明 capabilities 尚未返回时前端默认显示 High 的来源 |
| E-AF-033 | config_diff | `scripts/docker-common.sh` | local-codex/chat-platform 模式会追加 Chat 与 governance overlay，并把 `chat-worker`、`governance-controller` 纳入服务集合 | 证明标准脚本入口才覆盖 Chat + governance 产品运行态服务集合 |
| E-AF-034 | deployment_evidence | `acceptance-fixes.md` 历史验证记录 | 既有记录包含 `docker compose -f docker-compose.yml up -d --build web` 和 `docker compose -f docker-compose.yml up -d --build backend web`，后者伴随 orphan `chat-worker` / `governance-controller` 提示 | 证明此前验收证据存在局部重建，不能保证产品链路服务全部更新 |
| E-AF-026 | regression | `test_governance_candidates.py` / `test_governance_writer.py` | 后端测试覆盖 DB 中自动创建 `governance_applications`，以及 `bug-generate` candidate 写入 `bug.md` 与状态事实源 | 证明 DB 与文件事实源回归断言已覆盖 |
| E-AF-035 | screenshot | 用户附件 `codex-clipboard-fa823727-9f96-406a-b100-223ad91c0d62.png` | 工具调用/完成状态条位于消息正文上方中间，与 assistant 头像和正文左边界脱节 | 证明 AF-013 的满宽规则误把状态摘要按钮作为正文输出块处理 |
| E-AF-036 | code_path | `src/web/src/styles/chat-workbench.css` | `.turn-assistant .chat-turn-activity > *` 强制所有子元素 `width: 100%`，覆盖 `.chat-tool-summary { width: fit-content }` | 证明状态摘要漂浮来源是子元素满宽规则过宽 |
| E-AF-037 | browser_dom | `tests/chat-assistant-width.cjs` | Playwright 采样显示 assistant column 宽 1334，summary left=74 与 column left=74 对齐，summary width≈319.9，status/bubble 宽 1334，errors=[] | 证明状态摘要已回到轻量左对齐 meta，正文与执行输出仍保持满宽 |
| E-AF-038 | screenshot | 用户附件 `codex-clipboard-2eb05297-c164-4919-bbe1-b01fa5500fd3.png` | `/req-complete REQ-0027...` 执行中 assistant 输出未占满整行 | 证明满宽规则不能只覆盖 generate 命令或完成态消息 |
| E-AF-039 | browser_dom | `tests/chat-assistant-width.cjs` | Playwright 命令矩阵覆盖 11 类样本：`req-generate-running`、`req-complete-running`、`bug-generate-running`、`bug-complete-running`、`req-review-running`、`bug-review-running`、`sprint-propose-running`、`opsx-running`、`plain-chat-running`、`plain-assistant-completed`、`history-restored`，errors=[] | 证明 role=assistant 的运行中/完成/历史恢复输出按角色统一满宽，用户气泡仍受限 |

## 调整内容

- `RequirementCenterPage.tsx`：真实治理准备成功后只接收并缓存短命令 `/<action> <issue-id>`；不再把内部治理约束作为前端执行 prompt 传入 Chat。
- `ChatWorkbenchPage.tsx`：保留对旧 sessionStorage 隐藏 prompt 的兼容读取，但新链路不再依赖它；历史恢复时只挂载不可见轮询控制器。
- `Composer.tsx`：发送请求、请求签名和 Chat turn payload 均使用可见草稿 `text`；旧 `hiddenPrompt` 不再作为请求体 prompt，用户消息历史只保存 display_prompt。
- `preparation.py` / `execution.py`：新增 display prompt 与 execution prompt 服务端分离；`prepare` 返回短命令，`run_claim` 在执行器启动前根据 candidate 恢复内部治理约束，并按真实 execution prompt 计算预留。
- `preparation.py`：`check_send` 增加执行器 sandbox/dry-run preflight；`collect` 成功校验候选后由后端自动创建 application，失败时区分 `executor_unavailable` 与 `governance_validation_failed`。
- `preparation.py` / `chat/api.py`：`workspace_fact_source_stale` 增加安全细分详情，区分 `local_governance_dirty`、`git_snapshot_unreadable` 与旧部署兜底；错误响应只返回根类别、中文类别、处理建议标识和数量，不返回本机路径、对象完整 ID 或 Git 输出全文。
- `governanceApi.ts` / `RequirementCenterPage.tsx`：需求中心写入型卡片动作按 `workspace_fact_source_stale` 的 `reason` 和 `categories` 生成 Toast，提示阻断文件类别与处理建议；缺少细分详情时按运行服务未更新到最新治理门禁兜底提示标准部署更新。
- `ConversationMessages.tsx`：用户消息展示层识别 `req-generate` / `bug-generate` 治理执行 prompt；当后续正文包含内部治理约束时，只展示第一行短命令，并让复制消息也只复制可见短命令。
- `GovernanceResult.tsx`：当 candidate 仍为 `prepared` 且文件数为 0、尚无应用操作时，不渲染大型治理成果面板。
- `GovernanceResult.tsx`：不再发起 application POST；当候选包含后端 application 时只轮询 operation，pending 但无 operation 时仅给轻量提示。
- `GovernanceResult.tsx`：自动应用失败、执行器不可用、治理校验失败、冲突、失败和恢复阻塞状态均只通过轻量 notice 反馈。
- `GovernanceResult.tsx`：改为不可见后台控制器，不再渲染治理成果卡片、查看成果按钮、维护窗口 checkbox 或审阅治理成果弹窗。
- `ChatWorkbenchPage.tsx`：将后台应用成功回调接入会话刷新，将失败、冲突、恢复阻塞和校验拒绝接入轻量 toast 提示。
- `vite.config.ts`：为每次 Web 构建注入 `__MOONBOX_BUILD_ID__`，提供运行态构建版本识别。
- `runtimeBuild.ts`：应用启动时设置 `data-moonbox-build-id`，并通过 no-store HTML 比对当前脚本资产；发现旧 bundle 时一次性刷新，避免活跃旧实例继续渲染已移除面板。
- `ChatWorkbenchPage.tsx`：在会话和 candidate 恢复时执行旧治理面板 DOM 清理，阻止历史入口遗留 `.pg-result`、旧弹窗或旧 aria 节点继续占据对话区。
- `runtimeBuild.test.ts`：覆盖 build mismatch reload、同构建不刷新、旧治理面板 DOM 清理且不误删普通消息文本。
- `chat-messages.test.tsx`：补充源码断言，确保 `.chat-message-history` 不再残留 `780px` 或 `820px` max-width 限制。
- `settings.py`：将 Chat capabilities 的默认推理程度从 `high` 调整为 `low`。
- `Composer.tsx`：将 capabilities 未加载时的前端 fallback 推理程度从 `high` 调整为 `low`。
- `test_chat.py` 与 `chat-composer.test.tsx`：同步默认值断言，并新增前端 fallback 显示 Low 的回归用例。
- `docs/02-deployment.md`：明确原生 Compose 命令仅适用于基础局部调试；Chat + governance 产品运行态验收必须使用根目录 up/down 脚本，由脚本统一加载 overlay 和服务集合。
- 本台账：将既有裸 compose 运行态证据标记为历史偏差证据，新增标准脚本部署验收要求，避免只重建 `backend`/`web` 后误判产品链路已更新。
- `chat-workbench.css`：为 `.turn-assistant .chat-message` 增加 `width: 100%` 与 `max-width: none`，并让 assistant bubble 占满列宽；保留 `.chat-message-user` 的右侧气泡宽度限制。
- `chat-messages.test.tsx`：新增布局回归断言，校验 assistant 满宽规则与用户气泡宽度限制同时存在。
- `chat-workbench.css`：将 `.chat-message-history` 改为占满对话区可用宽度，不再用 `max-width: 1120px` 限制 assistant 输出轨道。
- `GovernanceResult.tsx`：自动应用门禁显式收敛为 `pending`、存在文件差异、存在 manifest，避免空 prepared 误申请，同时确保历史恢复的 pending candidate 会自动进入 application。
- `governance.test.tsx`：补充 Network/DOM 断言，覆盖 pending candidate 不由前端 POST application、后端 operation 轮询、prepared/0 文件不 POST、所有状态不出现 `待应用成果`、`查看成果` 或 `审阅治理成果`。
- `chat-workbench.test.tsx`：修正样式源码读取路径，使 Chat 工作台布局回归纳入前端聚焦回归。
- `chat-workbench.css`：为 assistant 正文视觉块补充运行态铺满规则：`.chat-assistant-col` 增加 `width: 100%` 与 `align-items: stretch`；`.turn-assistant .chat-message-bubble` 增加 `align-self: stretch`、`display: block`、`box-sizing: border-box`、`min-width: 0`；`.turn-assistant .chat-markdown` 增加 `display: block`、`box-sizing: border-box`、`width: 100%`、`max-width: none`。
- `chat-messages.test.tsx`：补充 DOM + computed style 回归断言，渲染真实消息后校验 history、assistant message、assistant column、bubble 和 markdown 的运行态宽度/铺满属性。
- `chat-workbench.css`：将 assistant `TurnActivity` 的满宽子元素规则收敛为 `:not(.chat-tool-summary)`；`chat-tool-summary` 作为轻量 meta 左对齐到 assistant 内容列，使用 `fit-content`、透明背景和 `flex-start` 对齐。
- `chat-messages.test.tsx` 与 `tests/chat-assistant-width.cjs`：新增状态摘要 DOM/computed style 与浏览器盒模型断言，确认 summary 左边界等于 assistant column 左边界、宽度小于正文列，status/bubble/markdown 继续满宽。
- `chat-workbench.css`：将通用 `.chat-turn-activity > *` 的 `720px/72%` 限宽隔离到非 assistant 消息；`.chat-message-block.turn-assistant`、`.turn-assistant .chat-message` 和 `.chat-assistant-col` 显式 stretch/full-width，确保 assistant 运行中输出不按命令名分支。
- `chat-messages.test.tsx` 与 `tests/chat-assistant-width.cjs`：补充 req-complete 截图场景和通用命令矩阵 DOM/computed style 回归，覆盖 generate、complete、review、sprint、opsx 与普通 Chat 的 running 输出。
- `writer.py`：`req-generate` 与 `bug-generate` 固定候选写入改为要求 controller-ready 写入服务就绪，不再要求用户人工维护窗口；`capture` 与普通 document 写入仍保留原门禁。
- `test_governance_writer.py`：补充 generate candidate 在无 maintenance 文件但 controller-ready 时可自动入队并应用的回归，同时证明普通 document 写入仍被维护窗口保护。
- `chat-workbench.test.tsx`：补充从历史 URL 恢复会话的 DOM/Network 回归，断言只轮询后端 application operation、不自动 POST application，且不出现 `待应用成果`、`查看成果`、`审阅治理成果`、`确认应用`。
- `src/web/scripts/assert-runtime-bundle.mjs` 与 `package.json`：新增 dist bundle 文案断言，构建后扫描 `index.html`、JS 和 CSS 产物，禁止人工治理面板文案进入运行 bundle。

## 文档同步

- 已更新 Change `design.md`，明确产品准备态只保存可见短命令，执行上下文由后端按 candidate 恢复。
- 已更新 Change delta spec `web-catalog-requirement-center/spec.md`，归档后保留“Bug Generate 输入框不得裸露内部治理约束”的能力约束，并声明前端历史入口不得自动 POST application。
- 已更新 linked BUG `acceptance.md`，新增 AC-013 覆盖准备态输入框简洁命令与后端执行上下文恢复。
- 已更新 linked BUG `acceptance.md`，新增 AC-014 覆盖历史消息隐藏内部约束与空成果面板隐藏。
- 已更新 linked BUG `acceptance.md`，新增 AC-015 覆盖所有已接入真实治理候选链路 generate 命令的自动应用与异常降级人工确认。
- 已更新 linked BUG `acceptance.md`，新增 AC-016 覆盖 Chat 主对话区所有命令不渲染治理成果大面板。
- 已更新 linked BUG `acceptance.md`，新增 AC-017 覆盖 Chat assistant 消息满宽且用户消息仍保持右侧气泡宽度限制。
- 已更新 linked BUG `acceptance.md`，新增 AC-018 覆盖外层消息历史轨道满宽、pending candidate 自动应用和历史打开不恢复治理成果面板。
- 已更新 linked BUG `acceptance.md`，新增 AC-019 覆盖 assistant 正文 bubble/markdown 容器运行态 computed width 铺满。
- 已更新 linked BUG `acceptance.md`，新增 AC-020 覆盖最新 Web 构建部署、运行态 bundle 文案、历史入口 DOM 和 governance application 自动创建。
- 已更新 linked BUG `acceptance.md`，新增 AC-021 到 AC-023，覆盖后端 controller 自动应用、Chat 历史只保存 display_prompt、发送前 preflight 与错误码分类。
- 已更新 linked BUG `acceptance.md`，新增 AC-026 覆盖 BUG-0025 运行态部署验收必须使用项目标准脚本入口。
- 已更新 linked BUG `acceptance.md`，新增 AC-028 覆盖 Chat assistant 工具调用/完成状态摘要左对齐轻量 meta，且不影响正文和执行输出满宽。
- 已更新 linked BUG `acceptance.md`，新增 AC-030 覆盖所有 role=assistant 运行中输出不按命令场景生效，req-complete、complete、review、sprint、opsx 和普通 Chat 均需满宽。
- 已更新 `docs/02-deployment.md`，明确裸 compose 只用于基础局部调试，Chat + governance 产品验收必须使用根目录脚本配对重启并验证完整服务集合。
- 已更新 Sprint `acceptance-report.md`，补充 BUG-0025 部署验收口径。
- 已更新 Change `design.md` 与 `local-project-governance-loop` delta，明确 generate 自动应用使用后端 collect/controller 与 controller-ready 受控写入服务门禁，普通文档写入仍保留维护窗口。
- 已更新 Sprint `acceptance-report.md`，补充 BUG-0025 返修验收计划。
- 部署侧已补充运行态构建和容器部署验证；API schema、DB schema、安全模型、对象存储和客户端生成未更新：本次不改变接口字段、数据库结构、对象存储或 Orval 生成物，权限变化限定为 generate 固定候选复用 controller-ready 写入服务。

## 验证计划

- 前端聚焦回归：`node node_modules/vitest/vitest.mjs run src/chat-messages.test.tsx src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx`。
- 后端聚焦回归：`uv run pytest src/backend/tests/test_governance_candidates.py src/backend/tests/test_governance_writer.py`。
- 类型校验：`node node_modules/typescript/bin/tsc --noEmit`。
- Web 构建与 bundle 断言：`node_modules/.bin/vite build`、`node scripts/assert-runtime-bundle.mjs`。
- 运行态部署与证据：`bash scripts/docker-down.sh self-storage-sqlite` 后执行 `bash scripts/docker-up.sh self-storage-sqlite`；检查脚本解析的服务集合覆盖 Web、backend、chat-worker、governance-controller，`localhost:18102` 运行 bundle 不含人工治理面板文案，并用运行态配置核查证明后端为最新默认 Low。
- OpenSpec 与中文校验：`bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report`。
- Markdown diff 校验：`git diff --check -- <touched files>`。
- Workflow Sync：`python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary`。

## 验证结果

| 时间 | 类型 | 命令 | 结果 | 说明 |
|---|---|---|---|---|
| 2026-09-29 16:49:05 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/requirement-center.test.tsx src/chat-composer.test.tsx` | passed | 2 个测试文件、123 个用例通过；覆盖短命令可见、隐藏执行上下文发送、用户编辑后清除隐藏上下文和 Bug Generate 准备态存储。 |
| 2026-09-29 16:49:05 | 类型校验 | `node node_modules/typescript/bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 16:50:20 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-29 16:50:20 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-29 16:50:20 | Diff 校验 | `git diff --check -- <touched files>` | passed | 未发现 whitespace 错误。 |
| 2026-09-29 16:52:20 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=2、Skipped=8、Errors=0；BUG acceptance_status 保持 pending，用户可见阶段回到验收中/待复验。 |
| 2026-09-29 16:52:40 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-29 17:10:05 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/chat-messages.test.tsx src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx` | passed | 4 个测试文件、138 个用例通过；覆盖历史消息隐藏内部治理约束、复制只复制短命令、prepared 且 0 文件面板隐藏、输入框短命令和需求中心既有链路。 |
| 2026-09-29 17:10:05 | 类型校验 | `node node_modules/typescript/bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 17:17:13 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx src/chat-messages.test.tsx` | passed | 4 个测试文件、139 个用例通过；覆盖 pending candidate 自动应用、自动失败后人工重试、已有 operation 不重复申请、历史消息和需求中心既有链路。 |
| 2026-09-29 17:17:13 | 类型校验 | `node node_modules/typescript/bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 17:26:14 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx src/chat-messages.test.tsx` | passed | 4 个测试文件、139 个用例通过；覆盖后台自动应用、失败轻量提示、所有状态不渲染治理成果面板、已有 operation 不重复申请和需求中心既有链路。 |
| 2026-09-29 17:26:14 | 类型校验 | `node node_modules/typescript/bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 17:40:50 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/chat-messages.test.tsx src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx` | passed | 4 个测试文件、140 个用例通过；覆盖 assistant 满宽布局断言、用户气泡宽度限制、治理面板移除、自动应用和需求中心既有链路。 |
| 2026-09-29 17:40:50 | 类型校验 | `node node_modules/typescript/bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 17:41:31 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-29 17:41:31 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-29 17:41:31 | Diff 校验 | `git diff --check -- <touched files>` | passed | 未发现 whitespace 错误。 |
| 2026-09-29 17:41:31 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=9、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2。 |
| 2026-09-29 17:41:31 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-29 17:57:34 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/chat-workbench.test.tsx src/chat-messages.test.tsx src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx` | passed | 5 个测试文件、149 个用例通过；覆盖外层消息历史轨道满宽、pending candidate 自动应用 Network 断言、prepared 空候选不申请、治理面板 DOM 不存在和需求中心既有链路。 |
| 2026-09-29 17:58:01 | 类型校验 | `node node_modules/typescript/bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 18:00:44 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-29 18:00:44 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-29 18:00:44 | Diff 校验 | `git diff --check -- <touched files>` | passed | 未发现 whitespace 错误。 |
| 2026-09-29 18:00:44 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=9、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2。 |
| 2026-09-29 18:00:44 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-29 18:14:29 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/chat-messages.test.tsx` | passed | 1 个测试文件、7 个用例通过；新增 DOM + computed style 断言，覆盖 assistant 视觉块运行态铺满。 |
| 2026-09-29 18:14:41 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/chat-workbench.test.tsx src/chat-messages.test.tsx src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx` | passed | 5 个测试文件、150 个用例通过；覆盖 assistant 视觉块 computed style、历史轨道、自动应用、无治理面板和需求中心既有链路。 |
| 2026-09-29 18:14:41 | 类型校验 | `node node_modules/typescript/bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 18:17:55 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-29 18:17:55 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-29 18:17:55 | Diff 校验 | `git diff --check -- <touched files>` | passed | 未发现 whitespace 错误。 |
| 2026-09-29 18:17:55 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=9、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2。 |
| 2026-09-29 18:17:55 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-29 18:31:13 | 后端聚焦回归 | `uv run pytest src/backend/tests/test_governance_writer.py -q` | passed | 11 个用例通过；新增覆盖 generate candidate 在无 `maintenance.json` 但 controller-ready 就绪时可入队并应用，普通 document 写入仍需维护窗口。 |
| 2026-09-29 18:34:44 | 前端历史入口回归 | `node node_modules/vitest/vitest.mjs run src/chat-workbench.test.tsx -t "restores history" --testTimeout=10000 --reporter=verbose` | passed | 历史 URL 恢复会话时 pending candidate 自动 POST application；DOM 不出现 `待应用成果`、`查看成果`、`审阅治理成果`、`确认应用`。 |
| 2026-09-29 18:34:44 | 前端聚焦回归 | `node node_modules/vitest/vitest.mjs run src/chat-messages.test.tsx src/governance.test.tsx --testTimeout=10000 --reporter=default` | passed | 2 个测试文件、19 个用例通过；覆盖 assistant computed width、自动应用组件和治理面板不可见。 |
| 2026-09-29 18:34:44 | 类型校验 | `node node_modules/typescript/bin/tsc -b` | passed | 前端 TypeScript project build 通过。 |
| 2026-09-29 18:35:05 | Web 构建 | `node node_modules/vite/bin/vite.js build` | passed | 生成 `dist/assets/index-BgRU6-8i.js` 与 `dist/assets/index-C9hHe-xh.css`；Vite 仅提示 chunk size warning。 |
| 2026-09-29 18:35:05 | dist bundle 断言 | `node scripts/assert-runtime-bundle.mjs` | passed | 扫描 dist 3 个产物，`待应用成果`、`查看成果`、`审阅治理成果`、`确认应用` 命中数为 0。 |
| 2026-09-29 18:36:52 | 运行态部署 | `docker compose -f docker-compose.yml -f deploy/docker-compose.chat-platform.yml -f deploy/docker-compose.governance.yml up -d --build backend chat-worker governance-controller web` | passed | backend、chat-worker、governance-controller、web 均重建并启动；后续 `docker compose ps` 显示 backend/chat-worker/governance-controller healthy，web up。 |
| 2026-09-29 18:37:17 | 运行态 bundle 断言 | `node -e <fetch localhost:18102 bundle>` | passed | `localhost:18102` 加载 `/assets/index-BgRU6-8i.js`，旧治理面板文案命中数为 0。 |
| 2026-09-29 18:39:14 | 历史 candidate 应用实测 | `POST /api/v1/chat/governance-candidates/c6fce925.../applications` | blocked | admin 令牌不是历史 candidate actor，产品 API 返回 404/2601；未尝试密码探测或越权内部调用。自动 application 创建由前端 Network 单测和后端 writer 回归覆盖，真实旧会话需候选所属用户打开历史页或提供授权后触发。 |
| 2026-09-29 18:43:03 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-29 18:43:03 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-29 18:43:03 | Diff 校验 | `git diff --check` | passed | 未发现 whitespace 错误。 |
| 2026-09-29 18:43:03 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=9、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2；用户可见阶段回到验收中/待复验。 |
| 2026-09-29 18:43:03 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-29 19:05:00 | 后端聚焦回归 | `uv run pytest src/backend/tests/test_governance_candidates.py src/backend/tests/test_governance_writer.py` | passed | 24 个用例通过；覆盖 display_prompt 与 execution prompt 服务端分离、发送前 executor preflight、候选合法后 DB 自动创建 `governance_applications`、`bug-generate` 写入 `bug.md` 与状态事实源。 |
| 2026-09-29 19:09:44 | 前端聚焦回归 | `node_modules/.bin/vitest run src/governance.test.tsx src/chat-composer.test.tsx src/chat-messages.test.tsx --testTimeout=10000` | passed | 3 个测试文件、36 个用例通过；覆盖 Chat 历史只发送 display_prompt、assistant DOM/computed style、GovernanceResult 不渲染面板且不由前端 POST application。 |
| 2026-09-29 19:09:44 | 前端历史入口回归 | `node_modules/.bin/vitest run src/chat-workbench.test.tsx -t "restores history" --testTimeout=10000` | passed | 历史 URL 恢复会话时只轮询后端 application operation，不自动 POST application；DOM 不出现 `待应用成果`、`查看成果`、`审阅治理成果`、`确认应用`。 |
| 2026-09-29 19:09:00 | 类型校验 | `node_modules/.bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 19:18:16 | 需求中心入口回归 | `node_modules/.bin/vitest run src/requirement-center.test.tsx -t "starts real bug-generate" --testTimeout=10000` | passed | Bug Generate 准备态只写入 display_prompt，不再写入 `moonbox.governance.executionPrompt`。 |
| 2026-09-29 19:18:26 | 类型校验 | `node_modules/.bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 19:19:00 | Web 构建 | `node_modules/.bin/vite build` | passed | 生成 `dist/assets/index-BLHTtByD.js` 与 `dist/assets/index-C9hHe-xh.css`；Vite 仅提示 chunk size warning。 |
| 2026-09-29 19:19:00 | dist bundle 断言 | `node scripts/assert-runtime-bundle.mjs` | passed | 扫描 dist 3 个产物，`待应用成果`、`查看成果`、`审阅治理成果`、`确认应用` 命中数为 0。 |
| 2026-09-29 19:20:00 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-29 19:20:00 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-29 19:20:00 | Diff 校验 | `git diff --check` | passed | 未发现 whitespace 错误。 |
| 2026-09-29 19:20:00 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=9、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2。 |
| 2026-09-29 19:20:00 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-29 20:22:29 | 前端聚焦回归 | `node_modules/.bin/vitest run src/runtimeBuild.test.ts src/chat-messages.test.tsx src/governance.test.tsx --testTimeout=10000` | passed | 3 个测试文件、23 个用例通过；覆盖旧 bundle 自动刷新、历史入口旧治理面板 DOM 清理、assistant 历史轨道无残留 max-width 和 GovernanceResult 不渲染面板。 |
| 2026-09-29 20:22:29 | 类型校验 | `node_modules/.bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 20:22:29 | Web 构建 | `node_modules/.bin/vite build` | passed | 生成最新 dist 产物；Vite 仅提示 chunk size warning。 |
| 2026-09-29 20:22:29 | dist bundle 断言 | `node scripts/assert-runtime-bundle.mjs` | passed | 扫描 dist 3 个产物，旧治理面板禁用文案命中数为 0。 |
| 2026-09-29 20:22:29 | 前端历史入口回归 | `node_modules/.bin/vitest run src/chat-workbench.test.tsx -t "restores history" --testTimeout=10000` | passed | 历史 URL 恢复会话时只轮询后端 application operation，不自动 POST application；DOM 不出现旧治理面板。 |
| 2026-09-29 20:22:29 | 运行态部署 | `docker compose -f docker-compose.yml up -d --build web` | passed | `moonbox-web` 已重建并运行于 `localhost:18102`；`moonbox-backend` healthy。包含 chat-platform override 的重建因本地 `MOONBOX_CHAT_AUTH_SOURCE` 未配置而失败，未移除既有 chat-worker/governance-controller。 |
| 2026-09-29 20:22:29 | 运行态 bundle 断言 | `node -e <fetch localhost:18102 bundle>` | passed | `localhost:18102` 加载 `/assets/index-BcoXmN7-.js` 与 `/assets/index-BuEJyOc-.css`；旧治理面板禁用文案命中数为 0。 |
| 2026-09-29 20:22:29 | 浏览器运行态 DOM 证据 | `node - <<'NODE' <Playwright 历史入口检查>` | passed | 历史入口页面 DOM 采样得到 `buildId=mumn7qzm-f2xr1z`、`forbiddenHits=[]`、`panelCount=0`。默认 admin 登录返回 401，使用合成前端 session 完成纯 DOM 证据，未进行越权 API 写入。 |
| 2026-09-29 23:01:37 | 后端 Chat 回归 | `uv run pytest src/backend/tests/test_chat.py -q` | passed | 39 个用例通过，1 个跳过；覆盖 capabilities 默认推理程度为 Low。 |
| 2026-09-29 23:01:37 | 前端 Composer 回归 | `node_modules/.bin/vitest run src/chat-composer.test.tsx --testTimeout=10000` | passed | 17 个用例通过；覆盖 capabilities 默认 Low 和前端 fallback Low。 |
| 2026-09-29 23:01:37 | 类型校验 | `node_modules/.bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-29 23:06:14 | 运行态部署 | `docker compose -f docker-compose.yml up -d --build backend web` | passed | `moonbox-backend` 与 `moonbox-web` 已重建并启动；Docker 提示存在 chat-worker/governance-controller orphan，未清理。 |
| 2026-09-29 23:06:14 | 运行态配置核查 | `docker compose -f docker-compose.yml exec -T backend python -c "from app.chat.settings import execution_config; print(execution_config()['defaults'])"` | passed | 运行态后端返回 `{'agent': 'codex', 'model': 'gpt-6-astra', 'reasoning': 'low'}`。直接 HTTP capabilities 因未登录返回 401，未尝试越权读取。 |
| 2026-09-29 23:15:12 | 标准脚本停止 | `bash scripts/docker-down.sh self-storage-sqlite` | passed | 标准 down 同时停止并移除 `moonbox-web`、`moonbox-backend`、`moonbox-minio`、`moonbox-chat-worker`、`moonbox-governance-controller`；常规数据库与对象存储数据保留。 |
| 2026-09-29 23:15:58 | 标准脚本启动 | `bash scripts/docker-up.sh self-storage-sqlite` | passed | Chat 常驻部署和治理私有目录预检通过；脚本构建 `moonbox-backend:local`、`moonbox-web:local`、`moonbox-chat-executor:0.153.4-test`、`moonbox-chat-worker:local`，并等待 Web、backend、MinIO、chat-worker、governance-controller 健康。 |
| 2026-09-29 23:16:15 | 服务集合健康核查 | `docker ps --filter name=moonbox --format ...` | passed | 标准脚本启动后的服务集合包含 `moonbox-web`、`moonbox-backend (healthy)`、`moonbox-minio (healthy)`、`moonbox-chat-worker (healthy)`、`moonbox-governance-controller (healthy)`；未见 orphan 服务。 |
| 2026-09-29 23:16:29 | 运行态配置核查 | `docker exec moonbox-backend python -c "from app.chat.settings import execution_config; print(execution_config()['defaults'])"` | passed | 已启动后端容器返回 `{'agent': 'codex', 'model': 'gpt-6-astra', 'reasoning': 'low'}`，证明运行态后端使用最新默认配置。 |
| 2026-09-29 23:16:55 | 运行态 bundle 断言 | `node -e <fetch localhost:18102 bundle>` | passed | `localhost:18102` 加载 `/assets/index-m2QbOa08.js` 与 `/assets/index-BuEJyOc-.css`；`待应用成果`、`查看成果`、`审阅治理成果`、`确认应用` 命中数为 0。 |
| 2026-09-29 23:18:31 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-29 23:18:31 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-29 23:18:31 | Diff 校验 | `git diff --check -- <touched docs>` | passed | 本次触达的部署文档、Change 台账/trace/tasks、BUG acceptance 和 Sprint acceptance-report 未发现 whitespace 错误。 |
| 2026-09-29 23:18:31 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=9、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2；用户可见阶段回到验收中/待复验。 |
| 2026-09-29 23:18:31 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-30 08:23:25 | 前端聚焦回归 | `node_modules/.bin/vitest run src/chat-messages.test.tsx --testTimeout=10000` | passed | 1 个测试文件、8 个用例通过；新增执行中 assistant `TurnActivity` 与 `p[role=status]` 的 DOM/computed style 满宽断言。 |
| 2026-09-30 08:23:25 | 浏览器宽度采样 | `node tests/chat-assistant-width.cjs` | passed | Playwright 合成运行态覆盖 `req-generate-running`、`bug-generate-running`、`plain-assistant-completed`、`history-restored` 四类场景；history 宽 1376、assistant block/article 宽 1376，assistant column/activity/status/bubble/markdown 宽 1334，用户气泡宽 760，errors=[]。 |
| 2026-09-30 08:23:25 | 前端相邻回归 | `node_modules/.bin/vitest run src/chat-messages.test.tsx src/governance.test.tsx src/requirement-center.test.tsx src/chat-composer.test.tsx --testTimeout=10000` | passed | 4 个测试文件、145 个用例通过；覆盖 assistant 满宽、治理面板不可见、需求中心既有链路和 Composer 默认配置。 |
| 2026-09-30 08:23:25 | 类型校验 | `node_modules/.bin/tsc --noEmit` | passed | 前端 TypeScript 类型通过。 |
| 2026-09-30 08:23:25 | 前端旧测试池 | `node_modules/.bin/vitest run src/chat-workbench.test.tsx --testTimeout=10000 --reporter=verbose` | warning | 测试池挂起后手工中断，未出现断言失败；本次满宽验收改由 `chat-messages.test.tsx` 的 DOM/computed style 和 Playwright 浏览器宽度采样覆盖，后续需单独稳定 `chat-workbench.test.tsx`。 |
| 2026-09-30 09:39:42 | 前端聚焦回归 | `node_modules/.bin/vitest run src/chat-messages.test.tsx --testTimeout=10000` | passed | 1 个测试文件、8 个用例通过；新增断言覆盖 `TurnActivity` 容器仍满宽、`status/alert` 输出满宽，且 `chat-tool-summary` 为 `fit-content`、透明背景、左对齐轻量 meta。 |
| 2026-09-30 09:39:42 | 浏览器宽度采样 | `node tests/chat-assistant-width.cjs` | passed | Playwright 合成运行态 4 类场景通过；assistant column/activity/status/bubble/markdown 仍满宽，summary left=column left，summary width≈319.9 小于 column 1334，errors=[]。 |
| 2026-09-30 09:45:48 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-30 09:45:48 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-30 09:45:48 | Diff 校验 | `git diff --check -- <touched files>` | passed | 本次触达的前端样式、测试和 Change/BUG/Sprint 文档未发现 whitespace 错误。 |
| 2026-09-30 09:45:48 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=11、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2；用户可见阶段回到验收中/待复验。 |
| 2026-09-30 09:45:48 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-30 10:03:21 | pnpm 入口 | `pnpm --dir src/web test src/chat-events.test.ts src/chat-messages.test.tsx src/governance.test.tsx -- --run --testNamePattern "network|NetworkError|localized|治理请求"` | warning | 本机 corepack pnpm 缓存缺失，报错 `Cannot find module .../.cache/node/corepack/v1/pnpm/12.4.1/bin/pnpm.cjs`；改用项目本地 `./node_modules/.bin/vitest`，不阻断产品代码验证。 |
| 2026-09-30 10:06:53 | 前端 Network 聚焦回归 | `./node_modules/.bin/vitest run src/chat-events.test.ts src/chat-messages.test.tsx src/governance.test.tsx --testNamePattern "network|NetworkError|localized|治理请求"` | passed | 3 个测试文件聚焦用例通过；覆盖 chat/events/governance 网络错误中文化、AbortError 保留给调用方静默处理、消息区不显示浏览器英文 NetworkError。 |
| 2026-09-30 10:07:48 | 前端历史会话局部失败回归 | `./node_modules/.bin/vitest run src/chat-workbench.test.tsx --testNamePattern "turn polling|history without governance panels"` | passed | 2 个聚焦用例通过；覆盖历史入口无治理面板，以及已完成会话在 turns 轮询 NetworkError 时保留 assistant 成功消息、不显示全局重新连接。 |
| 2026-09-30 10:08:36 | 前端四文件完整回归 | `./node_modules/.bin/vitest run src/chat-events.test.ts src/chat-workbench.test.tsx src/chat-messages.test.tsx src/governance.test.tsx` | warning | `chat-events`、`chat-messages`、`governance` 已通过；`chat-workbench.test.tsx` 测试池因既有轮询定时器未自然退出被手工中断。已用聚焦工作台用例覆盖本次 Network/DOM 验收。 |
| 2026-09-30 10:09:21 | 类型校验 | `./node_modules/.bin/tsc -b --pretty false` | passed | 前端 TypeScript project build 通过。 |
| 2026-09-30 10:19:03 | 前端 Network 聚焦回归复跑 | `./node_modules/.bin/vitest run src/chat-events.test.ts src/chat-messages.test.tsx src/governance.test.tsx --testNamePattern "network|NetworkError|localized|治理请求"` | passed | 3 个测试文件、3 个聚焦用例通过，24 个用例跳过；确认本次最终代码仍不裸露浏览器 NetworkError。 |
| 2026-09-30 10:19:03 | 前端历史会话局部失败复跑 | `./node_modules/.bin/vitest run src/chat-workbench.test.tsx --testNamePattern "turn polling|history without governance panels"` | passed | 1 个测试文件、2 个聚焦用例通过，8 个用例跳过；确认历史入口无治理面板且 turns 轮询网络失败不覆盖已完成消息。 |
| 2026-09-30 10:19:03 | 类型校验复跑 | `./node_modules/.bin/tsc -b --pretty false` | passed | 前端 TypeScript project build 通过。 |
| 2026-09-30 10:20:10 | OpenSpec 校验 | `bash scripts/validate-openspec.sh --change fix-requirement-center-command-chain-write-gap --residual-report` | passed | 当前 Change 中文优先与 OpenSpec 结构校验通过；未发现非当前 Change 中文残留。 |
| 2026-09-30 10:20:10 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-30 10:20:10 | Diff 校验 | `git diff --check -- <touched files>` | passed | 本次触达的前端请求/错误处理、测试和 Change/BUG/Sprint 文档未发现 whitespace 错误。 |
| 2026-09-30 10:21:22 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=11、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2。 |
| 2026-09-30 10:21:22 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-30 10:25:09 | Web 构建 | `./node_modules/.bin/vite build` | passed | 生成 `dist/assets/index-knRA4DNg.js` 与 `dist/assets/index-Cd9pp4Jp.css`；Vite 仅提示 chunk size warning。 |
| 2026-09-30 10:25:09 | dist bundle 断言 | `node scripts/assert-runtime-bundle.mjs` | passed | 扫描 dist 3 个产物，`待应用成果`、`查看成果`、`审阅治理成果`、`确认应用` 命中数为 0。 |
| 2026-09-30 10:45:50 | 前端 Chat 消息布局回归 | `./node_modules/.bin/vitest run src/chat-messages.test.tsx --testTimeout=10000` | passed | 1 个测试文件、9 个用例通过；覆盖 assistant 内容列、TurnActivity、status/alert、bubble、markdown 满宽和用户气泡限制。 |
| 2026-09-30 10:45:54 | 类型校验 | `./node_modules/.bin/tsc -b --pretty false` | passed | 前端 TypeScript project build 通过。 |
| 2026-09-30 10:46:17 | 浏览器命令矩阵宽度采样 | `node src/web/tests/chat-assistant-width.cjs` | passed | 沙盒内 Chromium 因 Mach port 权限失败，提权复跑通过；Playwright 合成运行态 11 类场景通过、errors=[]；覆盖 req-generate、req-complete、bug-generate、bug-complete、req-review、bug-review、sprint-propose、opsx、普通 Chat running、普通完成和历史恢复。req-complete-running 中 history=1376、assistant article=1376、assistant column/activity/status/bubble=1334、用户气泡=760。 |
| 2026-09-30 10:47:05 | Web 构建 | `./node_modules/.bin/vite build` | passed | 生成 `dist/assets/index-BvKnlx9P.js` 与 `dist/assets/index-BXZDgoNq.css`；Vite 仅提示 chunk size warning。 |
| 2026-09-30 10:47:05 | dist bundle 断言 | `node scripts/assert-runtime-bundle.mjs` | passed | 扫描 dist 3 个产物，旧治理面板禁用文案命中数为 0。 |
| 2026-09-30 11:00:40 | 后端对象命令事实源门禁回归 | `uv run pytest src/backend/tests/test_governance_candidates.py -q` | passed | 31 个用例通过；新增覆盖写入型对象命令矩阵遇到执行器 `/work` stale fact source 时统一返回 `workspace_fact_source_stale`，只读 explore 不阻断，缺主文档返回 `governance_validation_failed`，clean draft fact source 可创建会话。 |
| 2026-09-30 11:26:08 | 后端 stale 提示分层回归 | `uv run pytest src/backend/tests/test_governance_candidates.py -q` | passed | 33 个用例通过；新增覆盖 `local_governance_dirty`、`git_snapshot_unreadable` 与 `/object-sessions` API 安全错误详情，确认响应和请求日志不包含本机路径或完整对象 ID。 |
| 2026-09-30 11:26:46 | 前端需求中心 Toast 回归 | `node node_modules/vitest/vitest.mjs run src/requirement-center.test.tsx src/governance.test.tsx` | passed | 2 个测试文件、123 个用例通过；新增覆盖写入型卡片动作遇到 stale fact source 时展示阻断类别与提交/同步建议，以及缺少 reason 的旧部署兜底提示。 |
| 2026-09-30 11:27:18 | 类型校验 | `node node_modules/typescript/bin/tsc -b` | passed | 前端 TypeScript project build 通过。 |
| 2026-09-30 11:27:38 | OpenSpec 校验 | `openspec validate fix-requirement-center-command-chain-write-gap --strict` | passed | 当前 Change 结构校验通过。 |
| 2026-09-30 11:27:52 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto` | passed | Updated=1、Skipped=11、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2。 |
| 2026-09-30 11:28:11 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-30 11:41:41 | 后端投影目录 Git 快照根回归 | `uv run pytest src/backend/tests/test_governance_candidates.py -q` | passed | 35 个用例通过；新增覆盖 `governance_root` 为无 `.git` 投影目录、`source_root` 为完整仓库时，clean 可创建对象会话，dirty 返回 `local_governance_dirty` 且不误报 `git_snapshot_unreadable`。 |
| 2026-09-30 11:41:41 | 治理 scope 授权回归 | `uv run pytest src/backend/tests/test_governance_scope.py -q` | passed | 8 个用例通过；确认 `ProjectScope` 新增 source_root 元数据后，项目授权、只读、跨项目隔离和文档读取仍正常。 |
| 2026-09-30 11:41:41 | OpenSpec 校验 | `openspec validate fix-requirement-center-command-chain-write-gap --strict` | passed | 当前 Change 结构校验通过。 |
| 2026-09-30 11:41:41 | 标题校验 | `python scripts/validate-document-titles.py --change fix-requirement-center-command-chain-write-gap --bug BUG-0025-requirement-center-command-chain-write-gap` | passed | 中文标题校验通过，14 份文件。 |
| 2026-09-30 11:41:41 | Diff 校验 | `git diff --check -- <本轮触达文件>` | passed | 本轮触达的后端 scope/preparation、部署 overlay、后端测试、Change/BUG/部署文档未发现 whitespace 错误。 |
| 2026-09-30 11:45:27 | Workflow Sync | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint auto --output summary` | passed | Updated=1、Skipped=11、Errors=0；BUG acceptance_status 保持 pending，子文档 checked=7、updated=1、warnings=2。 |
| 2026-09-30 11:45:27 | AI Usage | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change fix-requirement-center-command-chain-write-gap --sprint sprint-008 --json` | warning | usage_mode=unavailable、command_run_count=0、sprint_snapshot=skipped，未阻断本次返修。 |
| 2026-09-30 11:49:08 | 标准部署重启 | `bash scripts/docker-down.sh self-storage-sqlite` / `bash scripts/docker-up.sh self-storage-sqlite` | passed | Web、backend、minio、chat-worker、governance-controller 均启动并健康；服务入口 `http://localhost:18102`、`http://localhost:18101/docs`。 |
| 2026-09-30 11:49:08 | 运行态 source_root 挂载验证 | `docker exec moonbox-backend sh -lc 'test -d "$MOONBOX_CHAT_SOURCE_ROOT/.git" ...'` | passed | backend 容器可见 `MOONBOX_CHAT_SOURCE_ROOT/.git`，路径为 ProjectMoonBox 原仓库；确认产品运行态 Git 快照门禁不再依赖 `/app/governance` 投影目录。 |

### 2026-09-30 AF-013 所有 AI/assistant 消息运行态未满宽

- 反馈摘要：`req-generate` 执行中 assistant 消息仍未占满整行；用户期望所有 AI/assistant 消息不再区分命令类型或运行状态，外层 block、article、正文 bubble、markdown、TurnActivity 与执行中 status/alert 文案均占满消息历史可用宽度。
- 证据入口：用户附件 `codex-clipboard-441ae6e3-dbd0-4940-a278-5ad6721fc285.png` 显示 `REQ-0027...` 执行中输出只占左侧自然文本宽度；代码核查确认执行中输出不是最终 Markdown bubble，而是 `ConversationMessages.tsx` 独立渲染的 `TurnActivity`，其正文由 `TurnActivity.tsx` 输出到 `p[role="status"]`。
- 根因结论：前序 AF-005 到 AF-007 主要修正 `.chat-message`、assistant column、bubble 与 markdown 容器；执行中 `TurnActivity` 和 `status/alert` 文案没有独立 stretch/full-width 规则，也缺少运行态 computed style 断言，因此在 req-generate 执行中仍可能按内容收缩。
- 调整摘要：`chat-workbench.css` 为 `.turn-assistant .chat-turn-activity`、其直接子层、`p[role="status"]` 与 `p[role="alert"]` 增加 `align-self: stretch`、`box-sizing: border-box`、`width: 100%`、`max-width: none` 和 `overflow-wrap: anywhere`；保留用户消息右侧气泡宽度限制。
- 回归证据：`chat-messages.test.tsx` 新增执行中 assistant activity/status 的 DOM 与 computed style 断言；`tests/chat-assistant-width.cjs` 使用 Playwright 采样 `req-generate-running`、`bug-generate-running`、普通完成消息和历史恢复四类场景，确认 assistant block/article 与消息历史同宽，activity/status/bubble/markdown 与 assistant column 同宽，用户消息仍被限制。
- 文档同步：已更新 `tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance、Sprint acceptance-report 和本台账；API、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：`chat-messages.test.tsx` 8 个用例通过；Playwright 宽度采样 4 类场景通过且 errors=[]；前端相邻回归 4 个测试文件、145 个用例通过；`tsc --noEmit` 通过。`chat-workbench.test.tsx` 单文件测试池挂起被中断，未发现断言失败，记录为后续测试稳定性缺口，不作为本次满宽修复的失败证据。

### 2026-09-30 AF-014 Assistant 执行状态条漂浮

- 反馈摘要：工具调用/完成状态条漂在消息正文上方中间，和 assistant 头像及正文左边界脱节；期望状态条只作为轻量 meta 左对齐到 assistant 内容列，正文和执行输出继续保持满宽。
- 证据入口：用户附件 `codex-clipboard-fa823727-9f96-406a-b100-223ad91c0d62.png`；代码路径确认 `button.chat-tool-summary` 是 `TurnActivity` 工具摘要，而 `p[role="status"]`/`p[role="alert"]` 才是需要满宽承载的执行输出。
- 根因结论：AF-013 为修复执行中输出未满宽，使用 `.turn-assistant .chat-turn-activity > * { width: 100% }` 覆盖所有子元素，误伤 `.chat-tool-summary { width: fit-content }`，导致摘要按钮被拉成整行视觉块并在正文上方显得漂浮。
- 调整摘要：`chat-workbench.css` 将 assistant TurnActivity 子元素满宽规则收敛为 `:not(.chat-tool-summary)`；`chat-tool-summary` 改为 `align-self:flex-start`、`justify-content:flex-start`、`width:fit-content`、`max-width:100%`、透明背景和无边框；`status/alert`、bubble、markdown 仍保持满宽。
- 回归证据：`chat-messages.test.tsx` 新增源码和 computed style 断言；`tests/chat-assistant-width.cjs` 在浏览器中采样 req-generate、bug-generate、普通 assistant 和历史恢复，确认 summary 左边界等于 assistant column 左边界、summary 宽度小于 column，status/bubble/markdown 仍等于 column 宽度。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：`chat-messages.test.tsx` 8 个用例通过；Playwright 宽度采样 4 类场景通过且 errors=[]。本次未触发后端、API、DB、部署或客户端生成边界变化。

### 2026-09-30 AF-015 Chat 工作台 NetworkError 裸露与连接态误报

- 反馈摘要：发送 `/req-generate REQ-0027` 后先显示“正在连接工作台”，随后页面裸露 `NetworkError when attempting to fetch resource.`，顶部变为连接不可用；但同一页面里 assistant 已显示 PRD 生成成功。期望网络/轮询错误不裸露英文原文，并且不覆盖已成功生成的 assistant 消息。
- 证据入口：用户附件 `codex-clipboard-2733f99c-b395-4879-8f0c-a6b1583692aa.png`、`codex-clipboard-db0f08c5-8ada-4635-9b1f-e65ddb8b3aed.png`；代码路径 `chatApi.ts`、`chatEvents.ts`、`governanceApi.ts`、`useChatWorkbench.ts`、`ChatWorkbenchPage.tsx`、`ConversationMessages.tsx`、`ExecutionPanel.tsx`、`TurnActivity.tsx`。
- 根因结论：Chat、governance 和 events 请求未统一捕获浏览器 fetch 网络异常，多个调用点直接 `setError(e.message)`，导致原生英文 `NetworkError` 进入页面；selected conversation 的 turns/refresh 局部失败也会污染全局 `model.error`，让已生成成功消息旁出现全局连接错误。
- 调整摘要：新增 `normalizeChatError` 与 governance 请求错误归一化；chat/events/governance fetch 异常归一化为中文业务提示；AbortError 保留给调用方按 signal 静默处理；turns 和 `refreshSelected` 局部读取失败不再设置全局 error；ChatWorkbenchPage 仅在未选中会话时展示阻断工作台错误，已选会话保留消息区内容和可编辑草稿。
- 回归证据：`chat-events.test.ts` 覆盖 `chatRequest` / `readChatEvents` 网络错误中文化和 AbortError；`governance.test.tsx` 覆盖 governance NetworkError 中文化；`chat-messages.test.tsx` 覆盖消息区局部错误不显示浏览器英文；`chat-workbench.test.tsx` 覆盖历史会话 turns 轮询失败时保留已成功 assistant 消息、不显示全局重新连接。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：Network 聚焦回归 3 个测试文件通过；工作台历史会话局部失败聚焦回归 2 个用例通过；`tsc -b` 通过。全四文件 Vitest 集合因 `chat-workbench.test.tsx` 既有轮询定时器未自然退出被中断，未观察到新增断言失败，记录为测试稳定性 warning。

### 2026-09-30 AF-016 Assistant 运行中满宽按命令漏测

- 反馈摘要：`req-complete` 执行中 assistant 消息仍未占满整行；用户明确指出该规则应与命令无关，覆盖 req/bug generate、complete、review、sprint、opsx 和普通 Chat。
- 证据入口：用户附件 `codex-clipboard-2eb05297-c164-4919-bbe1-b01fa5500fd3.png`；代码路径 `chat-workbench.css`、`ConversationMessages.tsx`、`TurnActivity.tsx`、`chat-messages.test.tsx`、`tests/chat-assistant-width.cjs`。
- 根因结论：前序 AF-013/AF-014 已修复 generate 与状态摘要样本，但浏览器矩阵未覆盖 `req-complete` 这类运行中失败/未完成输出；同时通用 `.chat-turn-activity > *` 限宽规则仍可能影响非 generate 场景，导致修复表现像命令白名单而不是 role=assistant 规则。
- 调整摘要：`chat-workbench.css` 将 `.chat-message-block.turn-assistant`、`.turn-assistant .chat-message`、`.chat-assistant-col`、TurnActivity、status/alert、bubble 与 markdown 全部按 assistant 角色 stretch/full-width；通用 activity 限宽只保留给非 assistant 消息，用户消息右侧气泡限制不变。
- 回归证据：`chat-messages.test.tsx` 增加源码和 computed style 断言，要求 assistant column `max-width:none` 且 TurnActivity/status 满宽；`tests/chat-assistant-width.cjs` 扩展为 11 类命令矩阵，覆盖 `req-complete-running` 截图场景和 complete/review/sprint/opsx/普通 Chat running。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：`chat-messages.test.tsx` 9 个用例通过；`tsc -b` 通过；Playwright 宽度采样 11 类场景通过且 errors=[]，其中 `req-complete-running` 证明 assistant article 与 history 同宽、assistant 内容列/activity/status/bubble 同宽，用户气泡仍限制为 760px。

### 2026-09-30 AF-017 产品写入命令事实源 stale 门禁

- 反馈摘要：`/req-complete REQ-0027-requirement-center-command-chain-realization` 在产品运行态仍进入执行，但执行器 `/work` 只包含旧 `REQ-0027-capture` 且缺少 `requirement.md`，导致命令在 Chat 中失败。用户明确要求这不是 `req-complete` 单点问题，所有命令产品链路都应在发送前阻断 stale fact source。
- 证据入口：用户附件 `codex-clipboard-32068244-de58-4910-aae5-0688ce081fba.png` 显示执行失败原因是工作区只有旧 `REQ-0027-capture`、缺少目标完整 REQ 和 `requirement.md`；代码路径 `prepare_workspace()` 只从 committed `HEAD` 执行 `git archive`，而 `prepare_object_session()` 旧实现仅 `resolve_object()` 并创建/复用会话，没有验证执行器将看到的治理事实源。
- 根因结论：generate 链路有 governance candidate baseline overlay，因此能把稳定快照覆盖进执行器 `/work`；complete、review、sprint、opsx 等对象会话链路没有 overlay，仍直接依赖执行器从 Git committed tree 初始化。当需求中心事实源存在未提交或未跟运行态部署同步的治理改动时，产品入口仍允许发送，执行器看到的是旧事实源，造成“产品显示可执行但工作区不具备文档”的偏差。
- 调整摘要：`prepare_object_session()` 对所有写入型对象命令统一执行后端 preflight；`req-explore`、`bug-explore` 和 `open-chat` 保持只读打开。写入型命令会先检测 `issues/`、`iterations/`、`openspec/`、`docs/`、`rules/` 是否存在执行器 `/work` 不会看到的未提交或未跟踪治理改动，命中则以 `workspace_fact_source_stale` 阻断且不创建会话；clean 快照下再校验完整对象 ID、registry path、trace status 和关键文档。
- 回归证据：`test_governance_candidates.py` 新增后端回归：dirty fact source 下 `req-complete` 阻断且不创建会话；complete、review、sprint、opsx 写入型命令矩阵全部共享 `workspace_fact_source_stale`；只读 `req-explore` 允许在 dirty fact source 中打开会话；clean 但缺少 `requirement.md` 返回 `governance_validation_failed`；clean draft fact source 下 `req-complete` 可创建对象会话。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、BUG acceptance 和 Change trace；本次未新增 API 字段、DB schema、部署拓扑、安全模型、对象存储或客户端生成物，错误 kind 复用现有 `ChatError.kind` 响应通道。
- 验证摘要：`uv run pytest src/backend/tests/test_governance_candidates.py -q` 31 个用例通过，覆盖新增事实源门禁和既有 generate/object-session 回归。

### 2026-09-30 AF-018 workspace_fact_source_stale 提示分层

- 反馈摘要：需求中心点击 `完善需求` 时 Toast 仍统一提示“确认标准部署已更新”，无法区分是本地治理事实源未提交/未同步、标准部署没有更新，还是 Git 快照不可读。
- 证据入口：用户附件 `codex-clipboard-e8a594e4-5593-4aa5-b6cd-40e2187f26e5.png`；代码证据为 `_workspace_fact_source_stale()` 此前仅返回 bool 或抛出统一文案，`RequirementCenterPage.tsx` 直接 `setToast(error.message)`。
- 根因结论：后端 stale 门禁已经能阻断发送，但错误负载缺少结构化分类；前端也没有按 `workspace_fact_source_stale` 专门生成产品文案，导致不同阻断原因被压平成同一句标准部署提示。
- 调整摘要：`ChatError` 与 ChatRoute 错误响应增加安全 `details`；Git status dirty 时返回 `local_governance_dirty` 和 `issues`、`openspec` 等根类别，Git status 不可读时返回 `git_snapshot_unreadable`；需求中心 Toast 根据 reason/categories 显示阻断范围和处理建议，缺少 reason 时兜底提示运行服务可能未更新。
- 回归证据：后端新增 dirty fact source details、Git snapshot unreadable、API 安全错误响应断言；前端新增写入型卡片动作 Toast 断言，验证包含阻断类别和提交/同步建议，且不再出现“确认标准部署已更新”的统一提示。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、BUG acceptance、design、delta specs 与 `docs/03-api-index.md`；API 响应只扩展错误 `data` 的安全详情，不新增 DB schema、权限、部署拓扑、安全模型、对象存储或客户端生成物。

### 2026-09-30 AF-019 投影治理目录误用 Git 快照根

- 反馈摘要：用户指出产品 backend 的 `governance_root` 是治理目录投影且不含 `.git`，不应直接在 `/app/governance` 执行 `git status`；Codex 命令运行在真实仓库中能读到 `.git` 和当前事实源，因此产品门禁语义应与 Codex 对齐。
- 证据入口：运行态 binding 显示 `governance_root=/app/governance`、`source_root=<ProjectMoonBox 原仓库>`；`deploy/docker-compose.chat-platform.yml` 此前 backend 未挂载 `MOONBOX_CHAT_SOURCE_ROOT`，而 `chat-worker` 已挂载；代码证据为 `_ensure_clean_executor_snapshot(project)` 直接调用 `_workspace_fact_source_stale(project.root)`。
- 根因结论：AF-017/AF-018 的事实源 stale 门禁选错了 Git 根目录。`ProjectScope.root` 是产品内容读取根，产品部署中可为治理投影；它不等于执行器从 committed tree 初始化 `/work` 时对应的完整 Git 仓库根。直接在投影根运行 `git status` 会把合法部署形态误判为 `git_snapshot_unreadable`。
- 调整摘要：`ProjectScope` 增加 `source_root` 与不可用标记；写入型对象命令的 Git stale 门禁优先使用 `source_root` 的完整仓库快照，`governance_root` 继续作为治理内容读取根。标准 Chat 部署为 backend 增加 `MOONBOX_CHAT_SOURCE_ROOT` 只读挂载；若绑定声明了 `source_root` 但运行态不可读或缺少 `.git`，按 `standard_deployment_outdated` 阻断，不再退回投影目录误报 Git 损坏。
- 回归证据：后端新增两类投影目录回归：`governance_root` 无 `.git` 且 `source_root` clean 时 `req-complete` 可创建对象会话；`source_root` dirty 时返回 `workspace_fact_source_stale.reason=local_governance_dirty` 且不创建会话，确认不会因投影目录无 `.git` 返回 `git_snapshot_unreadable`。
- 文档同步：已更新 `design.md`、`tasks.md`、delta specs、部署文档、本台账和 BUG acceptance；本次不新增 API schema、DB schema、权限模型、安全边界、对象存储或客户端生成物。

## BUG 子文档一致性扫尾检查

### AF-034 已评审对象加入迭代命令参数

- 反馈与偏差：期望 REQ 使用 `/sprint-propose --req <完整ID>`、BUG 使用 `/sprint-propose --bug <完整ID>`；实际服务端卡片动作省略类型参数，点击后原样注入 Chat Prompt。影响需求中心已评审两类卡片；用户前次运行态截图与 `_stage_action()`、`issueAction()`、`openIssueActionDialog()` 代码路径共同确认。
- 调整：服务端已评审卡片按对象类型拼接参数，不改变对象会话 API、权限、数据库或 Sprint 选择逻辑。前端现有带类型参数的兜底保持不变。
- 验证：后端 `_stage_action` 两类参数化回归通过；前端两类卡片点击跳转回归通过，覆盖 object-session 请求、Chat 路由及 `sessionStorage` Prompt。真实部署浏览器复验待进行，本轮不将合成测试宣称为产品运行态验收。
- 文档决策：更新本台账、任务、Change trace、BUG acceptance、Change design/spec delta 和 Sprint acceptance-report；BUG 主文档、root-cause、workaround 无需改，原始缺陷边界未变。无 API/DB/部署/安全/客户端生成变更。

| 子文档 | 结论 | 原因 |
|---|---|---|
| `bug.md` | 无需更新 | 原缺陷现象仍为产品命令链真实写入缺口，本次返修不改变缺陷主描述。 |
| `root-cause.md` | 无需更新 | 根因证据门禁已通过，本次反馈不推翻原根因；属于应用后的 UI/交互返修。 |
| `workaround.md` | 无需更新 | 没有新增手工绕过路径。 |
| `acceptance.md` | 已更新 | 新增 AC-013 到 AC-032，覆盖准备态短命令、历史消息隐藏内部约束、generate 自动应用、无治理面板、assistant 满宽、历史入口自动 application、正文视觉块铺满、运行态最新构建部署、后端自动应用、display_prompt、preflight 错误码、旧 bundle 自愈、默认 Low、标准脚本部署验收入口、所有 AI/assistant 消息 TurnActivity/status 满宽、工具调用/完成状态摘要轻量左对齐、NetworkError 分层中文提示、AbortError 静默、已成功消息不被局部轮询失败覆盖，req-complete/complete/review/sprint/opsx/普通 Chat 运行中输出通用满宽矩阵，所有写入型产品命令发送前事实源 stale 门禁，以及 source_root Git 快照根与 governance_root 投影目录分离。 |
| `trace.md` | 由 Workflow Sync 同步 | 不手工编辑 workflow-sync 投影事实。 |
