---
requirement_id: REQ-0025-chat-workbench
title: 实现 Chat 工作台功能
status: done
created_at: 2026-09-08 08:50:32
updated_at: 2026-09-14 00:04:50
lifecycle_stage: archive
lifecycle:
  captured: 2026-09-08 08:50:32
  generated: 2026-09-08 08:59:39
  completed: '2026-09-08 11:27:56'
  reviewed: '2026-09-08 11:53:44'
  approved: '2026-09-08 11:53:44'
iteration: sprint-004
openspec_changes:
  - change_id: add-chat-workbench-codex
    type: add
    status: archived
related_requirements:
- REQ-0020-requirement-center-card-document-actions-ai-chat
- REQ-0023-product-workbench-modern-ops-visual-system
- REQ-0022-local-project-import-product-iteration
- REQ-0024-markdown-editor-human-edit-permission-matrix
knowledge_base_refs:
- docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
- docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
- docs/knowledge-base/best-practices/admin-list-page-consistency.md
- docs/knowledge-base/retrospectives/sprint-003-retrospective.md
cross_cutting_tags: []
knowledge_base_gate: Pass
readiness: Ready
prototype_refs:
- path: issues/requirements/archive/REQ-0025-chat-workbench/prototype/web/prototype.html
  role: sanitized-interaction-reference
- path: issues/requirements/archive/REQ-0025-chat-workbench/prototype/web/context.md
  role: decomposition-and-replication-contract
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  req_final_consistency: passed
ui_reference_replication:
  mode: style-migration
  contract_seed: issues/requirements/archive/REQ-0025-chat-workbench/prototype/web/context.md
  status: verified
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web_request_wrapper
  - api
  - db
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  reason: 真实 Codex 长耗时执行、上下文和会话持久化涉及权限与观测；无附件上传和新增管理页。
  validation: AC-029/030 及权限、恢复验收已定义；真实接入未验证。
review_ref: issues/requirements/archive/REQ-0025-chat-workbench/review.md
review_conditions:
- RC-001
- RC-002
- RC-003
- RC-004
related_change: add-chat-workbench-codex
priority: P1
---

## 当前交付事实（最终验收回填）

用户确认的单机Compose、SQLite、本地独立备份、本机Codex认证单文件和显式unlimited策略已实际部署到所选项目仓库及moonbox编码空间。用户重新登录后通过真实页面完成两轮发送，分别结算14969/15189 Tokens；刷新保留两轮回复，轮次数量2、互斥及并发占用归零、两轮Diff均为空。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/account-verification.json及logged-in-acceptance.png。实际源仓库未被模型修改，工作区从已提交树初始化，当前目录未提交改动不会自动导入。

最终需求边界：无用户/空间运营配额；同会话互斥、单机顺序调度、有限结果处理缓冲和容器/协议安全边界保留。聊天和备份不自动过期；主动删除主数据、记录独立删除日志，旧备份物理expire前保持待清理，恢复前重放删除。API不挂载凭证或Docker socket，受信任控制器使用单文件认证，执行容器保持隔离。本期不交付MySQL/S3正式灾备、异机灾备或独立平台账号；SQLite与MySQL的业务兼容测试保留。

34项功能、8项横切、8项原型AC均有实现及验证映射；RC-001至004已关闭。Ops样式迁移、共享侧边栏、深浅主题、1440/1024/390视口及computed style承接evidence/sidebar-ui和live-web-execution，视觉Mock范围明确；本批当前账号Web/API/Worker/模型验证不使用Mock。PRD、流程、故事、验收、review、trace及prototype context已按最终认证/配额/保留策略核对一致。下文的未实现、暂缓、待映射、待登录及阶段进度均为历史检查点，不代表当前待办。归档与发布仍为后续独立动作。



# REQ-0025-chat-workbench Trace

## 当前状态

需求已完成并归档，P1；关联 add-chat-workbench-codex 的46项任务完成，最终实际部署与当前账号执行证据见归档 Change trace，后续视觉调整的合成验收与真实执行分开记录。capture 保留原始采集快照。

## Readiness Report

| 项 | 结果 | 证据 |
|---|---|---|
| 文档 | 齐全 | PRD、13 条 US、业务流程、34 条功能 AC、trace |
| Knowledge-base | Pass | 8 条 AC-XCUT；前台无匹配管理端标签，显式类比复用 |
| Prototype | Passed | 拆解、UI Skeleton、1440px及窄屏分批视觉/样式证据与 REQ 最终一致性通过，见归档 Change trace |
| 产品实现 | 未验证 | 功能、接入、Skeleton、截图、样式均未验收 |
| 评审关注 | 条件通过 | 策略已确认；接入验证、阈值/副本清理、入口映射与视觉证据见 review.md |

## Knowledge-base Cross-cutting Report

| 标签或适用模式 | 来源 | AC 数 |
|---|---|---:|
| 无 admin-* / media-upload 标签；前台弹窗类比 | admin-modal-width-css-cascade | 2 |
| 前台历史反馈类比 | admin-list-page-consistency | 3 |
| 动作族与执行环境边界 | sprint-003-retrospective S3-A004/S3-A005 | 2 |
| 原型一致性 | prototype-driven-ui-gate | 1（另 8 条 AC-PROTOTYPE） |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-14 00:02:14 | /opsx-archive | Change `add-chat-workbench-codex` 已归档，状态同步完成。 |
| 2026-09-10 10:27:01 | /opsx-modify | Change `add-chat-workbench-codex` 验收返修已同步，待复验或 archive。 |
| 2026-09-09 23:52:28 | /opsx-apply | Change `add-chat-workbench-codex` apply 完成，待 archive。 |
| 2026-09-08 14:18:06 | /opsx-apply | Change `add-chat-workbench-codex` apply 进行中，待补齐剩余验收。 |
| 2026-09-08 08:50:32 | req.capture | 记录 Chat 工作台功能需求，首版功能范围和验收标准待探索。 |
| 2026-09-08 08:59:39 | req.generate | 生成 Chat 工作台 PRD；承接 Ops 风格、服务端预配置仓库和个人私有会话三项确认，补齐执行状态、权限、Diff 与观测边界。 |
| 2026-09-08 11:27:56 | req.complete | 经 enriching 补齐文档与脱敏交互参考，完成拆解及契约种子；承接 Sprint-003 动作族/样式与挂载边界经验，状态 pending_review，视觉和接入待验。 |
| 2026-09-08 11:53:44 | req.review | 按用户确认采用平台统一认证/额度、主动删除＋容量上限，需求批准为 P1；工程验证保留 RC-001–004 条件，新增 AC-031–034。 |
| 2026-09-08 12:15:12 | req.opsx | 创建 add-chat-workbench-codex，承接两个新能力规格、DS策略、执行与视觉门禁。 |

- 阶段迁移：plan → review（/req-review）

## 首轮apply

/chat骨架证据见 openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/ui/。整体不可用，真实执行AC未完成；平台专用认证和RC-002待补齐，完整验收保持pending。


## 后端首批实施

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：会话API与恢复worker已部署，详细验证见Change evidence/backend/verification.json。Chat不再缺少全部后端路由，但模型执行、额度预留、业务对象关联、历史清理和前端API绑定仍未完成。需求保持已纳入迭代、当时验收尚未结束。


### 会话管理接入阶段证据

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：会话管理与事件读取已接API，内部额度预留/终态结算已通过SQLite与MySQL测试；当前仅任务3.2新增完成，整体4/25。真实模型执行仍未开放；关联快照、完整清理和文件级Diff待完成。详见openspec/archive/2026-09-13-add-chat-workbench-codex/trace.md「会话管理、事件与预留增量」及evidence/session-ui/。合成视觉数据不作为模型执行或真实CRUD证据，完整AC保持当时尚需验收。


执行增量已完成存储与可信事件/Diff任务，整体6/25。独立测试数据库两轮真实Codex、进程重建后的原线程恢复及本轮/累计Diff通过；平台认证隔离未通过，正式发送未开放。最新证据见Change trace和evidence/backend/real-runner.json。


## 当前实现边界（2026-09-08）

已实现会话/关联管理、不可变引用快照及撤权拦截、消息和本轮/累计Diff、停止确认/显式重试、内部预留结算、治理只读策略、请求/行为/运行观测与当前代码保护删除。执行副本和备份清理分别记录pending，不代表已经完成物理删除。

用户选择先开发与隔离验证，暂不配置正式限额和删除时限；平台专用认证与正式仓库绑定待提供。当前发送/重试保持关闭，有历史会话删除也不能绕过配置门禁。真实本机双轮与合成容器隔离是两类独立证据，不合并宣称平台端到端验收通过。完整映射见acceptance.md和Change trace。

## 共享侧边栏验收与部署（2026-09-08）

本批共享侧边栏已完成并部署：WorkbenchSidebar 统一品牌、版本、八项导航、折叠、用户/空间动作；useWorkbenchTheme 统一持久化与跨页主题。个人私有说明仅保留在会话区。需求中心原有账号和空间操作由共享模块承接，Chat 的空间选择限定于其授权目录，设置空间和进入后台分别遵循空间与账号权限。

验证：9个测试文件87项通过；实际18102构建页面52张截图、12组双页computed style完全一致（1440×900/1024×600/390×844，深浅×展开/折叠），16份账号/空间弹窗样式样本；跨页导航、主题持久化、只读空间、取消与Esc焦点返回通过，pageerror=0。另重新生成23张会话/关联/执行/停止截图，避免沿用旧CSS证据。所有浏览器业务响应均为合成API，不等同真实平台执行通过。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/sidebar-ui/{computed.json,verification.json,*.png} 与 evidence/session-ui。

源码证据确认根因：原Chat独立导航缺少分组、版本、折叠和账号菜单，通用按钮选择器覆盖rc样式。本轮浏览器又验证并修复390px空间浮层越界、空间设置遮罩留白/分列越界，以及CSS收敛造成的执行栏select颜色回归。最终导航展开224px/折叠72px，导航行高40px、padding=0 12px、gap=11px、font-size=13px，分组标题padding=16px 12px 7px；两页同状态值一致。

门禁：Cross-cutting tags=无admin-*（前台复用账号动作），AC-XCUT/knowledge_base_refs=pass，prototype与modal CSS经验已承接，PROCEED；本批Prototype Gate=pass，既有Skeleton承接，1440px/关键动作/computed=pass，Mock/API边界已声明；UI Reference Replication Gate=pass（共享壳、导航、账号动作、响应式）。REQ六件套及prototype context完成本批一致性回填，整体归档一致性仍待其他任务完成。

影响面：Web页面、共享组件、CSS、前端测试及验收脚本；复用已有鉴权API，不新增接口、DB迁移、客户端生成、部署变量或权限政策。product_data_collection_observability：本批not_applicable、affected_layers=[]，API/DB/请求日志/usage_events/Task Trace及请求封装字段未改变，详情见design补充合同。仅重建Web，后端与recovery镜像保持原值；健康接口ok、Chat页面200，镜像指纹见verification.json。


## 本地凭证与受控仓库真实执行验证（2026-09-08）

用户授权采用本地登录与可丢弃测试仓库，正式限额及删除时限继续暂缓。本批新增显式开启的 local_probe 认证工厂；仅复制登录文件到0700临时目录，文件0600，不加载个人配置、插件或历史。测试结束删除临时认证与执行历史；原登录文件不由测试写入。令牌刷新和异常宕机后的残留清理未在本次验证覆盖。

真实 codex-cli 0.153.4 通过后端 claim/run_claim 完成 counter.txt 的0→1→2修改、进程重建后同线程恢复、本轮及累计Diff和真实中止终态。原生命名权限配置隔离模型工具：凭证、相邻工作区与测试DB读取拒绝，仓库允许写入、.git禁止写入、工具外连拒绝；只读配置拒绝工作区写入。安装版本要求 initialize.experimentalApi，首次RPC拒绝经此修正后通过；增加读写降级回归。

真实测试1项通过（27.12秒）；后端回归41项通过、2项显式真实执行测试默认跳过。两轮完成用量分别22500和1455，均已结算；立即中止轮次未返回用量，标记usage_unavailable并保留reserved，不能按零消耗释放，实际用量对账仍未闭环。

证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/backend/local-credential-execution.json。使用合成API身份和独立SQLite，内部enqueue入队；本机原生执行不是已部署Docker worker或浏览器发送端到端证据。服务发送/重试仍503，未改真实环境、正式限额、删除期限或已有部署镜像。RC-001仅补齐本地正常路径及隔离子证据，进程异常/全链路部署等门禁不据此关闭。

影响：后端执行适配器、显式测试认证工厂、测试和部署说明。API契约、DB结构、UI、客户端生成均无变化。product_data_collection_observability=applicable；affected_layers=[api,db,task_traces]，沿用现有事件及额度持久化；validation=真实两轮、恢复、中止及保留未知用量预留通过，证据只保存状态和计量数值，不保存凭证或完整对话。

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，保持in_progress、13/26项，未标记整体实施完成态或归档。此前“缺少本地执行认证授权”的依赖已解除；正式共享平台认证与完整部署验收仍独立待完成。建议沿用本批显式开启、默认跳过的真实执行回归，不另建治理Issue。


## 五步隔离执行闭环（2026-09-08）

用户本批明确授权执行到测试清理。已完成：有界接收终态后用量、单调去重及可信记录幂等补结算；受配置与有效期保护的独立常驻worker；真实登录后的测试账号/空间/仓库入队门禁；回环地址18121上的构建Web与真实API验收；最终停止服务并删除测试数据。正常部署仍默认关闭发送/重试，正式认证、运营限额和删除时限继续暂缓。

实际四轮：完成0→1、worker重启后同线程完成1→2、网页停止、运行中SIGTERM重启worker后停止。恰好四轮，无自动重放；两轮修改与第三轮停止已按33873/2489/28778 tokens结算，第四轮停止没有权威用量，保持usage_unavailable与reserved，未按零消耗释放。整个临时测试DB随后按用户授权删除，不能把删除测试DB表述为该轮已对账。缺失用量的处理路径是保留预留、读取待对账清单，只有可信执行端结算凭据可用时才补结算；无自动推算或手填零值接口。

真实浏览器通过：创建会话、鉴权发送、刷新恢复、停止确认、历史读取、本轮/累计Diff、其他账号访问404及执行白名单拒绝；没有业务API Mock。初次刷新丢失选中会话与终态后输入区旧活动状态，分别通过URL保存不透明会话标识后重新鉴权读取、活动会话轮询修复。第一次停止观察90秒超时，退出浏览器没有停止后台运行；重新连接同一轮次后停止确认通过，未新建重复任务。截图及最终样式采样覆盖1440×900；本批没有布局/CSS改动，深浅/窄屏基线承接此前共享侧边栏验收。

实际原生权限探针通过：凭证、相邻种子仓库和测试DB读取拒绝，.git写入拒绝，模型工具网络拒绝，只读配置禁止写入。API仅回环监听且仍使用正常登录验证；私有配置需isolated-test、独立临时SQLite、指定身份/空间/仓库、有效期与新鲜worker心跳。配置不包含可由浏览器传入的路径或执行命令。异常worker租约与fencing由单元测试覆盖；本轮实际重启使用SIGTERM，不宣称已做SIGKILL全链路验收。

证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/live-web-execution/verification.json、computed.json及7张真实页面截图。四条Task Trace均关联真实请求ID，事件source_id无重复，行为与节点记录存在，页面pageerror=0。临时认证、仓库、SQLite和线程历史目录均已删除，服务停止、18121端口释放已核验；运行端原登录缓存未由测试写入。保留的证据没有凭证、原始执行会话文件或真实客户数据。

影响面：后端执行/结算/隔离配置及worker、网页会话恢复、测试启动器与验收脚本。API字段和OpenAPI schema比较不变，不需重新生成Orval；API能力和发送行为、DB持久化语义、安全/部署边界均已同步文档，无新表字段或迁移。product_data_collection_observability：status=applicable；affected_layers=[usage_events,request_logs,task_traces,task_trace_spans]；validation=真实请求与Task Trace关联、可信用量去重/恢复、所有者拒绝及脱敏摘要通过。UI Reference Replication Gate承接既有合同，本批真实交互及computed样式通过。

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004。RC-001受控接入Spike通过，对应任务1.4完成，整体14/26；本次用户指定的五步已处理，整个Change仍in_progress、当时验收尚未结束，不执行整体实施完成态或归档。正式共享平台认证、生产限额/删除期限和完整部署矩阵仍独立待完成。建议保留真实网页回归与故障场景的显式测试入口，无额外治理Issue/Change自动创建。


### 异常恢复与清理证据更新（2026-09-09）

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：承接本地凭证＋受控仓库方案。新增进程组故障回收、清理失败重试/当前权限复核、真实线程历史删除及独立镜像重启证据；未知运行保持互斥，未知用量保持预留。代码和凭证不随线程历史删除。实际备份与正式平台认证、限额、删除时限仍未闭环，不改变页面布局、动作语义或正式发送门禁。详细结果见本REQ acceptance.md及Change trace.md“异常恢复、清理与部署补验”；整体未进入实施完成态或归档。


### 推荐组合落地同步（2026-09-09）

用户选择的当前验证方案已实现：SQLite一致性备份与独立删除日志，恢复旧备份前重放删除；每会话独立Linux容器接入worker，真实双轮/恢复/停止及Diff、用量结算通过。空会话同样记录删除；代码和审计独立保留，旧备份正文须实际清理，恢复过滤不代表物理删除。正式方向保留为独立对象存储备份＋会话容器，S3/MySQL恢复、共享认证、正式额度和时限仍未开启。页面布局及动作合同不变；新证据见本REQ acceptance.md与Change trace.md，整体状态仍in_progress。


### 部署脚本接入补充（2026-09-09）

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：任务6.3完成，Change当前19/29项，整体仍in_progress、当时验收尚未结束。脱敏证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/deployment-scripts/。无API字段、业务表或UI变更，部署与安全边界同步docs/02-deployment.md，未执行整体实施完成态或归档。


### 终态并发释放补充（2026-09-09）

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：任务2.4内修复终态并发释放与Token结算耦合缺陷，新增内部迁移和回归；原实际测试DB并发恢复且Token保留，新测试实例停止→继续发送真实验证通过。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/concurrency-release/。整体19/29，未实施完成态或归档。


### 受控范围收口（2026-09-09）

当前24/29，任务2.3/2.4/3.1/4.3与验收映射5.5完成。新证据为Change evidence/usage-scope/（真实协议、双轮claim结算及双标签页/重启）。剩余正式配置/平台认证、正式清理部署与整体门禁仍阻塞，保持in_progress与pending。


### 单机常驻方案确认（2026-09-09）

用户已明确采用单机 Docker Compose、SQLite、本地独立备份、本机 Codex 认证单文件，取消用户/空间额度、并发和存储运营上限。显式 unlimited 与缺失配置区分，仍计量结算；同会话互斥、权限、未知态和单轮结果处理技术边界保留。历史及备份不自动过期；主动删除仍记录和跟踪主存储/执行线程/备份，副本无固定删除截止时间，旧备份物理移除前保持待清理。单机控制器顺序处理持久队列，容量不足不绕过隔离。正式仓库路径及空间映射尚待提供，当前不宣称正式服务已开放。方案细节以 docs/02-deployment.md 的单机常驻章节为准，替代此前“认证、限额和期限尚未决定”的当前态描述；历史证据保留。


## 单机常驻执行续接点（2026-09-09）

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004；用户已确认单机Compose、SQLite、独立本地备份、本机Codex认证单文件和unlimited运营策略。任务1.5/2.2/2.7完成，整体27/29。剩余5.4实际目标仓库/空间部署及5.6最终同步；已向用户询问仓库路径/空间名称，等待映射，其他正式运营决策已解除阻塞。未修改真实env或既有运行服务，未整体实施完成态/归档。

实现：显式unlimited语义、真实记账、常驻Worker/心跳与配置摘要门禁、--chat-platform Compose入口、独立初始Git基线；只保留API/容器/协议技术安全边界，不以大整数模拟无配额。控制器Docker权限不下放给执行容器。执行凭证使用单文件挂载和每轮私有副本更新；宿主文件inode改变需重建worker。备份每次启动及24小时周期创建，无自动过期；主动删除先记录删除日志，未物理expire的旧备份保持pending/retry。

根因与修复：新工作区仅git init、导入文件未跟踪会误阻止删除，补充初始提交和干净状态断言；首次真实Worker失败为main:49 FileNotFoundError，镜像内docker-cli缺失，替换包并加脱敏位置日志后通过。没有放宽隔离或删除断言。

验证：真实容器Worker双轮10569/10769 Tokens已结算，重启无重放；主动删除、离线恢复删除重放、执行线程清除与显式备份expire后状态闭环通过，代码保留；凭证副本/测试控制容器清理。MySQL43 passed/1 skipped、Web22 passed、部署脚本4 passed、真实Compose只读合并通过。证据：evidence/platform-local/verification.json。

product_data_collection_observability：status=applicable；affected_layers=[db,request_logs,task_traces,task_trace_spans]；reason=实际计量与常驻执行门禁、后台备份；validation=保持真实请求/轮次链路，后台不伪造用户行为，错误只记录类型和函数行号、不含路径和凭证。公开API字段及业务schema未变，无客户端重生；UI仅就绪提示文案更新，原型/共享侧边栏证据承接，Cross-cutting PROCEED，REQ子文档同步。

执行链路复盘：当前in_progress、acceptance=pending；暂停依赖仅为尚未指定的正式仓库与空间。建议保留镜像内命令存在性及新工作区干净基线回归，本批已落实；未自动创建Issue/Change。下一可执行动作是收到仓库映射后补齐私有env、执行--chat-platform预检与实际目标部署验收；无凭证内容需要用户发送。


### 实际单机部署检查点（2026-09-09）

用户指定当前MoonBox项目仓库及MoonBox空间。读取实际后端确认唯一空间编码moonbox对应显示名“AI原生软件工厂”，未新建或重命名空间。私有env保存仓库/空间映射、local-codex和unlimited策略，原env有私有备份；路径、ID与凭证不复制到治理证据。根up/down可根据已保存执行模式自动加载常驻Compose覆盖文件，脚本4项回归通过。

实际根up部署完成，API、Web、MinIO、Chat Worker均healthy；控制器非root，单认证文件只读挂载，API无认证文件及Docker socket，后台就绪摘要/空间权限/未配置仓库拒绝和独立备份日志核验通过。所选仓库已提交树1573文件、38876348字节成功初始化干净独立基线，源目录未改动，未提交代码不自动导入。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/。

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：任务5.4完成，整体28/29；5.6最终当前账号端到端验收和完成同步仍待登录。现有浏览器会话失效，使用已配置初始密码的一次登录返回401，不再重试、不重置账号、不伪造会话；已打开正常登录页并请求用户自行登录。独立环境的真实双轮/重启/删除恢复证据承接上一批，不冒充本次用户账号下的实际发送。常驻服务保留运行，不清理业务数据；下一动作是在当前有效登录下验证发送与刷新恢复，再执行最终完成同步。未执行实施完成态/归档及完成AI Usage钩子。

product_data_collection_observability：status=applicable；affected_layers=[request_logs,task_traces,task_trace_spans,db]；reason=实际部署接入和身份验收；validation=仅保存部署布尔结果和计数，初始密码及日志未外泄；后台只读检查不伪造用户行为，尚无本批真实用户轮次。不涉及公开API字段、业务schema或客户端重生；UI布局不变，既有原型证据继续适用。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，in_progress/acceptance=pending。仓库和空间依赖已解除，剩余是当前有效账号登录；建议以空间唯一编码辅助解析显示名称，本批已交叉核对，未自动创建Issue/Change。

## 2026-09-10 执行展示返修

连续相邻、同消息和同执行轮次的文字事件归并显示；工具/状态/消息身份变化及序号缺口保留边界。原始事件默认折叠，保留最近1000条窗口说明。所选轮次当前状态单独展示，时间线状态明确标为历史。安全Markdown新增表格（表头、对齐、转义管道、行内代码、空单元格），窄屏在表格内滚动，保持HTML/图片/危险链接不可执行。旧事件缺少消息身份时仅按连续区段归并，不伪造缺失边界。

本次只改变Web展示，事件持久化、SSE、API、DB、鉴权、停止/重试、Token计量不变，无需迁移或客户端生成。文件路径链接不在本次范围。
- 2026-09-14 00:02:14 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive REQ-0025-chat-workbench
