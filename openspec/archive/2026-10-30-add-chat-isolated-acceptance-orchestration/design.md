---
title: Chat 隔离验收与原操作续接设计
created_at: 2026-10-29 17:11:36
updated_at: 2026-10-29 17:11:36
---

# Chat 隔离验收与原操作续接设计

## 背景与现状

来源为 `issues/requirements/review/REQ-0048-chat-isolated-acceptance-orchestration/` 六件套与局部原型；review 已批准，trace 为 in_sprint，sprint-016 预算30人天、剩余范围估算13人天。文档 Ready；模板实际摘要、运行资源和产品验收均待实施，不是运行 Ready。

`verification/candidate.py` 已提供固定 Git 候选的 SQLite/MySQL 供应、批准模板、租约及清理，`candidate_schema.py` 以 candidate_id 唯一记录环境。该契约面向固定候选，不能直接当作可多次尝试的 Chat 原操作。`chat/api.py` 已有预检、验证任务创建/查询/取消/证据接口。现有 OperationVerification 负责治理成果核验，不等于本需求的验收环境继续操作。

## 目标与非目标

在同一已授权 Chat 业务操作中完成当前输入的环境准备、逐项验收、结果回传与安全回收。支持未提交但归属明确的代码，保留来源轮次、尝试和历史证据。复用已归档底座，新增 Chat 编排适配及能力缺口。

不新增任意镜像托管、生产部署、真实数据恢复、独立环境门户、模型无限续接或自动归档。预配置验证和固定候选合入仍独立工作，不强制启动 MySQL。

## 设计决策

### D1 现有设计系统与原型冲突处理（Conflict Resolution）

用户已确认采用现有设计系统和 Chat 组件，承接 context.md 的策略。原型不是一对一外观复刻。结构事实源顺序：HTML → PNG（当前无）→ context → acceptance → UI规则 → 既有规格；业务权限、预算与完成语义以已评审 PRD/AC 为准。

| 冲突 | 处置 |
|---|---|
| HTML 独立 main/article 页面与原 Chat 局部入口 | 仅提取详情区域，不新增导航或门户 |
| HTML 14px 卡片圆角、system-ui 和24px标题 | 使用现有 Chat 字体、token及近直角组件，按钮采用已存在的2px token |
| HTML 演示状态下拉框与真实状态 | 仅原型保留，产品由服务端投影，不能人工伪造通过 |
| HTML 12/12 与完整20项 AC | 计数来自当前计划；不硬编码12，不忽略横切与原型AC |
| HTML 已释放同时显示验收通过 | 释放和结果分别展示；失败/停止也可能已释放 |
| 原PRD早期“本轮不生成prototype”措辞 | 以后续11.6节及现有原型为准；实现最终一致性时同步早期时态 |

选择复用组件以保持原会话密度和权限语义；直接复制原型 CSS 会引入第二套字体、圆角和页面壳，故不采用。素材驱动不适用，本需求无新增品牌素材。

### D2 单一编排事实与供应适配

在 `src/backend/app/verification/` 增加操作编排、持久状态、调度及身份服务；供应资源通过现有候选供应与 runner 的受控适配层执行，不复制一套浏览器或治理状态引擎。固定候选接口保持原语义，Chat 任务用 operation/attempt/environment 多级身份表达。抽取底座能力时回归固定候选四项既有规格。

受控快照从服务端授权工作区、对象绑定和允许文件清单生成，固定基准提交与内容 manifest；包含本操作未提交修改，排除真实env、凭据、数据库、日志和无关改动。捕获前后版本/清单一致，否则有界重捕获或 input_changed。不能证明文件归属则阻塞，不把共享工作区整体打包。项目脚本仅在受限容器执行，不能修改控制计划、接触 Docker socket 或控制器凭据。

准备阶段仅允许批准依赖源；执行阶段使用 internal 网络和只读制品。构建槽先释放再运行测试/浏览器槽。模板修订固定 schema、镜像摘要、实际补丁、架构、锁文件、迁移/种子/计划及健康/版本探针；历史任务保留旧修订。模板未发布或镜像不匹配返回 preparable/unavailable，不现场解除隔离。

### D3 持久对象、竞争与恢复

拟新增 `verification_operations`、`verification_attempts`、`verification_environment_steps`、`verification_ac_results`、`verification_identity_refs`；具体迁移按现有 metadata 入口实现，均兼容 SQLite/MySQL。操作关联 actor/space/repository/conversation/source_turn/change/plan；尝试关联 input_digest/template_digest/environment/verification_task。环境归属通过适配记录关联现有供应事实，不更改 candidate_id 唯一语义来强塞多尝试。

操作保存取消意图、原授权/绑定版本、原总预算和续接计数；尝试保存 epoch、state_version、worker占用、阶段与绝对期限；步骤保存开始意图、实际资源身份、结果摘要和副作用确定性。AC结果独立保存指纹、证据哈希、类别及失效原因；身份表只存引用、角色、有效期、撤销事实，不存明文秘密。

幂等唯一键按 actor+space+repository+operation+client_request_key_hash，输入摘要另行比较，同键异输入409；不能将输入摘要塞入唯一键后允许冲突绕过。operation+attempt序号、attempt+AC+输入摘要建立唯一约束；按状态/租约到期、空间/操作/创建时间建有界查询索引。使用短事务条件更新 epoch/state_version，外部 Docker/构建/文件操作不持有长事务。重启先读取实际资源及执行占用，不认领未知存活执行，不以心跳丢失单独证明模型终止。

状态独立保存：操作执行状态、attempt状态、environment阶段、AC状态、cleanup状态。环境 queued→preparing→ready→running→releasing→released；blocked/failed/cancelled/timeout/cleanup_failed 保存发生阶段与原因。验收全通过不覆盖 cleanup_failed；取消后成功回调可存历史事实但不能启动续接。

### D4 短期身份与停止优先

模板批准合成身份和角色，成员/只读默认可测，管理员仅用于显式批准AC。迁移、应用DB和浏览器身份分离；密码/登录态交付私有临时介质，仅对应测试进程可读，模型/API/日志只见不透明引用。每任务独立 browser context/Cookie。15分钟期限仅在活跃租约和当前权限有效时刷新，不能越过环境总寿命。

取消/撤权60秒内撤销受控访问；应用不可达时先切断所属网络，标记撤销待确认。停止事件以版本围栏阻止新模型及未提交业务写入；允许事实回读、撤销和清理。存活轮次通过持久结果投递记录去重；已结束轮次保持终态，只有确认已终止且原授权、预算、绑定、输入、占用与适配器恢复能力有效，才通过条件更新预占最多一次关联续接。消费端亦核验投递ID，响应丢失可回读。缺少该能力则阻塞，不能并发起模型冒充恢复。

### D5 资源预算与受限回收

数值唯一事实源为 REQ requirement.md §11.3，实施不得自行降配：全局2、每空间1、每原操作1；每环境4 CPU/8 GiB/20 GiB，另预留2 GiB证据。构建2 CPU/4 GiB/512进程；MySQL1/2/256，后端1/2/256，前端0.5/0.5/128，测试槽1/2/256（CPU/GiB/进程）。资源预留覆盖全套和平台余量，硬磁盘配额不可落实则阻塞。

排队30分钟、准备20分钟、健康120秒、迁移/种子5分钟、单AC10分钟、验收60分钟、首次供应寿命120分钟。租约5分钟、30秒心跳、60秒扫描，以服务端时钟及持久绝对期限计时；重启重试不重置。仅幂等瞬时错误最多重试2次（10/30秒）；清理每次5分钟，30/120秒后各重试一次。未知迁移/种子副作用先回读，无法证明则隔离并在剩余预算内重建私有库。

常驻 verification worker 执行租约扫描；worker停机不承诺自动回收，恢复后补扫。资源创建前记意图，标签记录精确环境和daemon；清理仅删除归属匹配且无有效执行者的容器、专属网络、临时卷和身份，保留其他任务与活跃资源。daemon不一致或删除无法确认保持cleanup_failed，禁止广泛prune。Agent实施时另遵守 temporary_docker 登记/标签/cleanup/check，不能用产品租约替代本地测试登记。

## 数据与 API

沿用 `/api/v1/chat/verification-environments/preflight` 和 `verification-tasks` 的预配置目标协议。新增编排 API 拟用 `/api/v1/chat/acceptance-operations`：POST 创建（原操作/轮次/Change引用、计划修订、幂等键），GET `/{operation_id}` 只读状态，POST 子资源 `/{operation_id}/resume`、`cancel`、`cleanup-retries`。写入带 expected_version 与幂等键；查询不创建环境、模型或重放步骤。重新核验调用只读查询/探针，不复用有业务应用副作用的接口。实施前在现有路由/schema上锁定最终命名并同步OpenAPI。

请求不接受镜像、宿主路径、命令、任意URL或数据库连接串；服务端解析可信绑定。每次创建、读取、续接、取消、清理及证据读取核对当前身份/权限，响应提供 allowed_actions、阶段、原因、环境版本、各AC及清理摘要。403拒绝越权；409表示输入/版本/占用冲突；能力缺失返回稳定原因与受影响AC，不假装业务测试失败。既有受控工具调用转接同一服务，不能绕过HTTP入口守卫。

API索引、后端OpenAPI、`src/web/openapi.json`、Orval生成类型和调用测试同步；DB设计、schema/migration、兼容矩阵和真实双库测试同步。持久业务恢复记录独立于90天观测保留；在存在活跃资源或证据引用时不清除恢复事实，证据在线访问沿用7日、长期脱敏副本归Change。

## UI Contract：原 Chat 详情与权限

入口沿用 ChatWorkbenchPage 当前对象会话和来源轮次；原消息、历史、输入与导航保持原行为。沿用 TurnStatusSkeleton 的 feedback/body/detail 插槽，新增 `src/web/src/components/chat/AcceptanceOperationPanel.tsx`（拟定）承载环境/AC/动作；共享 Button/ChatDialog，OperationVerification 保持原治理核验职责。

层级：轮次反馈→环境阶段与AC摘要→折叠详情（能力/数据库/版本/租约/清理）→动作及反馈。浅色背景#F4F6FA、文字#202636、边框#DDE3EE，深色#0A0D14/#ECEAE4/#242A3A，金色按项目token；Inter/Noto Sans SC，正文14px/约1.45，辅助12px，图标16px，动作gap8px、详情padding12px，边框1px，按钮圆角2px；在 Skeleton 采样确认后固定最终值，不从原型复制大标题。390px动作换行、长原因折行，页面无横向溢出；细节允许局部滚动。保留焦点、hover/disabled/busy和错误重试反馈。

权限来自服务端 allowed_actions；只读用户不显示继续/停止等写动作，隐藏不是安全边界。证据有无、到期与无权限分别展示。Mock仅用于骨架独立预览；正式页面、状态、计数与动作均接真实API。后端未知不补默认通过，不将合成原型截图作为产品证据。

一致性清单：复用原Chat品牌与导航/折叠/用户菜单；按钮字体与金色主动作一致；危险停止色及图标沿用共享组件；共享弹窗层级、焦点和Esc；后台本次无入口变更，仅复用共享token，不增加管理端CRUD标签。

## UI Skeleton：映射与分批门禁

第一批以合成数据实现原会话插槽、详情和确认弹窗容器；取得1440×900截图及首轮确认，再进入动作细节实现。等待确认只阻塞UI细节，后端独立任务继续。

| 原型 | 目标 data-testid | 组件/状态与数据 |
|---|---|---|
| #feedback | turn-status-feedback | 既有轮次反馈，当前操作原因 |
| #details | acceptance-details | AcceptanceOperationPanel，折叠/展开 |
| #stage | acceptance-stage | 环境阶段和独立清理状态 |
| #checks | acceptance-checks | 当前有效AC数量，失败/阻塞分别计数 |
| #actions | acceptance-actions | 服务端动作族，忙碌/权限/版本 |

### 动作按钮与浮层组件族

| 动作 | modal类型 | data-testid | 状态与证据 |
|---|---|---|---|
| 展开详情 | inline details | acceptance-details | 开/关与键盘，截图和交互 |
| 查看证据 | 既有授权证据入口 | acceptance-evidence | 可用/缺失/到期/403，不泄露内部路径 |
| 重新核验 | 无 | acceptance-verify | idle/busy/error；无新增任务/模型的请求计数 |
| 继续 | 无，恢复动作族 | acceptance-resume | allowed/disabled/busy/conflict；重复提交一次效果 |
| 重试清理 | 无，恢复动作族 | acceptance-cleanup-retry | 只清理所属资源，不重跑AC |
| 停止 | 共享 ChatDialog 确认族 | acceptance-stop、acceptance-stop-dialog、acceptance-stop-confirm | 返回/确认/Esc、焦点归还、停止后无模型调用 |

停止对话框关闭仅取消确认，明确点击“确认停止”才提交；遮罩外部关闭若沿用共享组件支持，覆盖内部stopPropagation与外部capture行为。动作按钮和弹窗同批实现，不逐按钮返修。

### 样式采样与视觉证据

对上述 selector 在浅/深主题、1440×900与390×844采集 font-family/font-size/line-height/width/height/padding/gap/border/color/background/overflow/position/z-index。期望按本Contract与共享token；尺寸容差1px、颜色精确、字体允许声明回退；当前值待产品实测，禁止预填。详情宽度不超过会话容器，小屏页面scrollWidth不超过视口。

第二批接API与动作族，验证准备/运行、权限、重复点击和停止对话框；第三批覆盖局部阻塞/恢复、停止/已释放、清理失败及最终REQ一致性。每批截图/样式/交互证据归 `evidence/acceptance/` 对应AC与阶段/视口，详见 acceptance.md。非目标页面只做共享组件受影响回归，不改全站布局。

## 验收、观测与风险

计划覆盖12项功能、4项横切、4项原型AC，详见 acceptance.md。首次成功、拒绝、原执行恢复、重启回读使用独立样本。Linux arm64 必测SQLite与真实MySQL8.4（utf8mb4/utf8mb4_0900_ai_ci/UTC，业务显式排序保留）；amd64启用前同矩阵，其他版本拒绝。合成测试、真实DB、真实浏览器、产品模型轮次及资源清理分别签认。依赖映射无法确定时扩大失效范围，不猜测缓存可复用。

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, database, chat, environment_orchestration, usage_events, request_logs, task_traces, task_trace_spans, evidence]
  reason: 原操作、尝试、环境、验证任务和AC跨持久化及异步执行，需要可信身份关联、阶段计时和脱敏诊断。
  validation: AC-004/006/007/008/009/012核对权限、指纹、epoch、状态、耗时、撤销回收及证据；用户动作透传行为ID，服务端生成request_id，后台恢复不伪造usage_events。
```

界面事件仅记录操作/尝试/环境不透明ID、动作类别和状态；Task Trace按预检、快照、资源预留、供应、迁移、身份、AC、投递、撤销、清理划节点。采集失败只降级诊断，不改变结果。禁止秘密、Prompt、正文、DSN与宿主路径。后台入口usage_events为N/A（无真实用户点击）；管理后台/移动端N/A（无入口）；对象存储基础结构N/A（复用既有受控证据服务）。在线7日证据、90日请求及Task Trace、180日行为明细策略不扩展。

风险：旧供应仅固定提交，需扩展快照适配但不能降低候选校验；硬磁盘限额/镜像实测缺失只阻塞相应运行；真实恢复依赖执行器能力，无法证明终止时保持阻塞；共享工作区已有其他改动，实施严格按任务归属。部分依赖已交付不免除完整20项AC。

## 迁移与回滚

先增量建表/索引及兼容旧请求，再部署批准模板与具备扫描能力的worker，最后开放新入口；开启前完成模板和双库探针。回滚先拒绝新编排，停止新AC/续接并撤销身份，精确清理所属环境，保留历史任务/证据/迁移表，再恢复前一批准模板和旧调用路径；不删除业务库、不执行down -v、不自动撤销已发生业务事实。本命令不执行部署。

实施同步 docs/02-deployment.md、docs/03-api-index.md、docs/04-database-design.md、compatibility/database、模块README、env示例及安全/观测标准；治理资产有语义变更时补治理日志和索引。模板摘要、实际补丁、硬限额能力、执行器恢复支持属于实施探针待测项，不是待用户重新评审事项。

## 本轮续接与长期转存实施（2026-10-29）

用户继续授权模型自动续接和长期证据转存，真实产品验收仍待接入。实现已接入固定 App Server 0.153.4 的 `item/tool/call`：新建受控实现线程注册 `moonbox_acceptance`，从当前授权范围捕获独立检查点；存活轮次由唯一执行器发送一次结果，收到对应完成通知才记录已消费。RPC 响应之前到达的工具请求保留到事件循环处理。发送后确认丢失时保留未知事实，不重发、不创建第二个消费者。

原轮次失败且执行器关闭、文件归集和环境释放均确认后，通过正常 Chat 准入事务创建最多一次关联轮次。事务重验权限、绑定、输入、原总期限、占用和额度，保留原轮次终态；有限 token 预算只允许使用原余额，未知用量或余额耗尽拒绝。关联轮次不能另建验收操作重置自动续接次数。主动停止及撤权在执行启动和事件循环重复核验；用户停止的原轮次与未知执行不自动续接。

长期转存保存白名单脱敏摘要到当前 Change 的 `evidence/runtime/`，以 attempt 身份和 SHA-256 保持不可变；使用项目写锁、原子替换、读回校验及持久 pending/published 记录恢复写后中断。查询每次重验当前权限和内容哈希。在线七日过期后仍可通过“长期摘要”读取已转存结果，不延长原截图或原始日志的访问期限。摘要包含逐 AC 结果、输入/部署/证据摘要，明确 `visual_artifacts_included=false`；真实产品视觉材料仍需按产品验收流程单独脱敏签认。

固定运行时的 thread/resume 协议不提供动态工具注册参数，因此既有未注册线程不被冒充具备该能力；新建受控线程可注册，既有线程保留现有 API 和已确认失败后的关联续接路径。未接入真实模型/产品轮次，不把合成 stdio、事务、截图或 MySQL 回归写成产品签认。

product_data_collection_observability: applicable；affected_layers: Chat API、请求/行为观测、持久编排、模型工具、Task Trace、Web。沿用现有分阶段追踪和请求封装，长期摘要读取仅记录既有脱敏请求元数据；不采集 prompt、命令原文、凭证或宿主路径。validation: 事务/协议/ACL/取消/预算/崩溃恢复回归、真实 MySQL 独立表、双视口组件取证；真实产品轮次待接入。
