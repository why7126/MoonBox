---
change_id: add-local-project-governance-loop
requirement_id: REQ-0022-local-project-import-product-iteration
status: archived
iteration: sprint-005
updated_at: 2026-09-14 09:01:01
---

# Change 实施与验证记录

## 最新摘要

- Sprint持续展示：sprint.md跨阶段保留，主文档优先，既有解析/只读/必需文档校验不变。

- 主文档返修：requirement.md/bug.md生成后在所有阶段持续首位展示，始终Issue来源，保留原权限。

- 主动作/Tips返修：统一阻塞显示、禁用和执行守卫；Tips置于Agent上方，兼容窄屏与长文案。

- Sprint 文档返修：卡片 sprint.md 统一读取关联 Sprint，兼容归档且缺失不回退。BUG-0014 已消除缺 sprint.md 误报。

- 任务入口返修：三入口统一关联 tasks.md 完整文档阅读与定位，缺失提示；独立进度面板移除。当前 REQ-0022 没有明确人工验收任务，因此展示全文及未找到目标提示。

- 来源需求：REQ-0022-local-project-import-product-iteration；Change：add-local-project-governance-loop；Sprint：sprint-005。
- 当前阶段：archived，已完成 /opsx-archive；22项原始实现任务已完成，REQ 验收状态已回填为 passed。
- 首轮看板返修历史：注册对象38（REQ25/BUG13），34完成、4验收中，阻塞/漂移0；6条已核实失效路径已修正。需求中心独立连接栏已移除。
- 首屏返修：原位骨架替代独立加载面板，避免假零值与空态；1440深浅/390慢请求布局位移0px，后台刷新保留卡片与筛选。
- 文档返修：卡片只保留所属REQ/BUG的trace.md入口，缺失不回退Change；本文件顶部为当前摘要，下面为历史证据。
- 最新验证：归档后校验通过，包含 Change 身份、OpenSpec strict、中文、目录结构、env ignore、归档证据、Sprint scope、Workflow Sync 和 Issue promote。此前原型标签精简验证、后端/前端/浏览器证据保留在历史记录中。

## 归档验证摘要

- 归档路径：`openspec/archive/2026-09-14-add-local-project-governance-loop/`。
- 规格合并：新增 `local-project-governance-loop`，更新 `web-catalog-requirement-center-real-data`。
- Workflow Sync：`opsx.archive` 与 `req.archive` 均完成，Sprint 为 `sprint-005`，REQ 验收状态为 `passed`。
- Issue Promote：`REQ-0022-local-project-import-product-iteration` 已迁入 `issues/requirements/archive/`。
- AI Usage：hook 已执行，因未发现可归属 `token_count` 事件，`usage_mode=unavailable`；该项不阻断归档。

## 证据边界

本轮未切换当前业务部署。最新UI验证为本地源码、真实仓库文档与合成HTTP；历史apply真实闭环证据保留，不替代后续真实部署复验。

## 历史过程记录

以下保留2026-09-11初次apply及历次返修的原始阶段记录。诸如“6个失效路径保留提示”“增加ProjectBinding”“测试待追加”仅表示当时情况，现状以顶部摘要与对应后续返修结论为准。




本次 /opsx-apply 已完成，22/22 任务通过实施验证，Workflow Sync 已同步关联 Change 为 applied，REQ 验收状态为 pending。以下保留实施过程记录；当前结果以“完成门禁与真实交付证据”及末尾同步报告为准。

### 已完成的验证

- `python -m pytest src/backend/tests/test_governance_scope.py src/backend/tests/test_governance_candidates.py src/backend/tests/test_governance_writer.py -q`：11 passed。合成测试覆盖项目权限、冻结只读、无scope拒绝、文档版本、稳定快照、未提交治理覆盖、新会话不发送、固定写集、语义拒绝、幂等、整批冲突、替换后断电恢复、外部修改时恢复阻塞。
- 独立MySQL 8.2.0临时容器矩阵13 passed in 3.56s，覆盖作用域/候选/应用与恢复；结束后清理容器。新加文档保存测试待追加矩阵。凭据为临时随机值，未保存到证据。
- 当前仓库稳定读取990个允许治理文件、约4.44MB，单次约454ms；这是本地服务读取观测，不是浏览器5秒闭环验收。
- 原有registry中存在6个历史失效路径；聚合保留其漂移提示，不擅自迁移其他Issue。文件存在性属于快照事实，未因历史目录缺失拒绝全部看板。

### 原型与界面证据

UI Contract使用design.md既有局部一致方案，冻结selector、动作族与样式清单。生产页面增加ProjectBinding/GovernanceResult插槽；dev专用fixture位于src/web/tests/governance-preview.html，不进入生产入口，使用显式模拟数据，不写源仓库。

- 命令：`cd src/web && node tests/governance-skeleton.cjs`。
- 视口1440×1000、390×844；深浅主题；无浏览器pageerror。
- `evidence/ui/skeleton-requirements-light.png`：需求中心首屏、原九阶段横向看板和侧栏保留。
- `evidence/ui/skeleton-chat-dark.png`：Chat加载状态与成果摘要插槽。
- `evidence/ui/skeleton-preview-dark.png`、`skeleton-preview-light.png`、`skeleton-preview-mobile.png`：预览弹窗、文件列表、正文滚动和footer。
- `evidence/ui/skeleton-styles.json`：侧栏224px、弹窗880px、正文14px/20.3px、padding与主题采样。
- 首轮截图发现新增区域影响既有grid行以及窄屏关闭按钮换行，已修复并重取证。
- Skeleton人工确认卡片已提出，尚未收到确认；不关闭1.3及UI细节任务。

### 当前部署事实

只读检查本地容器：Web/后端/Chat worker运行。后端仍将issues挂载为可写，其他治理目录只读；现有Chat worker拥有源仓库只读副本入口，未部署独立治理写入控制器。新代码将旧文档保存/任务勾选改为入队，缺服务端登记的维护窗口时拒绝写入。

尚未修改真实env或部署新服务，尚未证明目标维护窗口独占条件成立。单机文件锁只协调登记控制器，不对任意外部编辑器提供跨文件事务保证。

### 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: web、api、database、request_logs、usage_events、task_traces、task_trace_spans、agent_workflow、deployment。API复用可信request_id路由；候选/应用/锁采用私有正文存储和opaque ID。后续补齐行为字典、Task Trace、保留/备份及实际降级测试。对象存储无新增依赖。

### 中断续接检查点

- 当前任务：后端独立工作与合成验证；并行等待Skeleton首轮人工确认。
- 下一可执行：继续权限/并发/恢复边界复核、控制文件基准、观测、API生成和部署计划；确认后接入前端scope/轮询/成果真实API。
- 尚未完成：真实MySQL、UI全动作族、真实账号/worker/原仓库应用、10次5秒观察、25条AC与RC001至004。
- 禁止把当前合成测试与Skeleton模拟当作真实闭环通过。未运行applied完成同步。


### 后端增量结果

- 新增真实登录态HTTP测试与原需求中心回归一起通过；新旧编辑能力保持，旧PUT调用显式迁移为202入队/查询/重读流程。当前聚焦组合33项通过。
- SQLite成套备份/离线恢复与既有Chat备份回归6项通过。恢复复用独立删除日志，拒绝摘要变化，不恢复维护窗口，不启动执行。
- OpenAPI/Orval治理客户端已生成；前端页面真实接入仍受Skeleton首轮确认局部阻塞。
- OpenSpec严格校验、中文优先校验通过。目录校验发现根目录.pnpm-store未登记，正在核对来源；不改治理规则放行缓存。


### 最近验证与剩余依赖

- 最后后端聚焦组合37 passed；此前Chat和备份相关组合70 passed、1 skipped（专用执行环境项）。新增写入序号和过期数据库会话用例已单独覆盖。
- 独立MySQL 8.2.0矩阵更新为18 passed，包含文档队列、读写竞争和旧事务重入；未连接业务数据库。
- TypeScript检查通过，OpenSpec严格/中文、Sprint范围、数据观测、上下文预算均通过。pnpm临时索引目录已移到系统临时目录，目录治理校验恢复通过。
- UI Skeleton人工确认：仍待回复。真实验证环境（独立本地副本或当前仓库维护窗口）：已提出卡片，仍待回复。不会因等待超时推定同意。
- 当前仅完成有独立证据的设计契约、作用域/快照/schema、治理准备和候选校验任务。写入控制器逻辑及合成恢复验证已实现，但目标维护窗口、部署权限与真实应用验收仍未关闭，因此4.x不冒充目标环境通过。
- 下一可执行顺序：收到Skeleton确认后完成5.1/5.2/5.3及卡片导航；收到验证环境选择后准备实际绑定/部署和维护窗口，执行6.3/6.5。6.4剩余前端与真实行为部分、6.6文档最终一致性直接依赖上述结果。
- 所有代码尚未部署，未修改真实env，未向真实Chat发送消息，未在原仓库应用候选。当前/opsx-apply保持in_progress，不执行applied完成同步。


### 目标环境预检与停止前决策

只读容器挂载比较确认：需求中心的issues/iterations/openspec/docs/rules均与Chat源仓库同源；现有Chat worker缺少docs/rules治理挂载，API仍有issues写权限。新覆盖文件已补齐这些挂载并将API改为只读；使用脱敏示例配置的Compose config校验通过，尚未部署。

目前不存在可越过人工门禁的前端细节或真实部署任务。独立后端实现、接口迁移、恢复/备份与兼容验证已完成本轮可执行部分；Skeleton确认后才能继续界面接入，验证项目选择与维护窗口成立后才能真实部署/应用。未终态成果及关联会话清理仍保持拒绝，恢复资料完整保留。

停止前决策：用户未要求停止，环境未强制结束；Change未完成。两项原生卡片均未回复，剩余交付直接或间接依赖首轮UI确认和真实验证环境/维护窗口。允许等待必要外部输入，恢复入口继续当前apply，不要求另发“继续”。Workflow Sync applied与AI Usage成功后置Hook不适用本次暂停，未运行；未自动创建跟进Issue或Change。

规范优化建议：后续可用/spec-opt为带prototype且涉及真实维护窗口的Change明确区分“独立后端合成验证完成”和“目标环境交付完成”，避免同一任务勾选混用两种证据。当前仅记录建议，不修改技能规范。

#### 确认后连续实施

用户回复“确认”，承接现有 Skeleton 与独立 MoonBox 本地验证副本两项推荐选择；此前用户确认阻塞解除。继续完成真实 API 接入、动作族、项目轮询及独立环境验证，不在当前源仓库执行验证对象写入。

#### 真实执行发现与当前 apply 修复

独立副本的实际浏览器已确认：卡片进入新建个人 Chat 后轮次数为 0，显式点击发送才启动平台容器 worker。首轮实际执行因 Chat 旧权限策略仅接受 in_sprint 对象而进入只读，同时触发测试预算限制（result_or_token_limit）；候选被拒绝，源文件未回写。已在当前 apply 内补齐 prepared→running 的专用副本写权限，并保持对象/成员授权及全工作区四文件成果校验。查看者仍无写权限，目录返回 readonly；增加真实体量的隔离测试预算后用新副本重跑。

合成回归：后端 38 项通过（scoped API、SQLite、候选、并发/恢复、备份、旧文档写入入口）。需求中心前端 59 项通过，旧同步保存测试迁移为 202 队列与读取终态；实路由不再模拟评审、导入或阶段推进。成果族新增 5 项验证完整预览不申请写入、固定版本与维护确认、恢复状态及任务 URL 范围。实际 Chat 外观与另一并行任务共享文件，独立项目栏出现并行移除，已请求项目状态展示位置的单项偏好；其余工作继续。

#### 实施验证增量

- 前端全套 18 文件、167 项测试通过；TypeScript 与 Vite 生产构建通过。旧登录目录断言同步为 projects；新增草稿测试确认轮询发现新版本后不覆盖本地输入，并保留旧 expected_version 拒绝冲突保存。
- MySQL 8.2 独立矩阵 19 项通过，覆盖候选专用写权限和持久应用恢复。新增查看者授权断言通过。
- `evidence/compose-permissions.json` 从实际治理 overlay 派生的可丢弃 Compose 验证：API 无源文件写权限、控制器可写同一宿主源、控制器无 Docker socket，未挂载模型凭证。真实执行环境为回环 API/控制器加生产平台容器执行器，使用独立 DB/私有目录，与当前运行的业务部署隔离。
- `evidence/ui/state-styles.json` 及 15 张 state 截图覆盖 pending/conflict/failed/recovery_blocked/applied 的 1440px 深浅色与 390px；窗口未越界、footer 可见。`skeleton-styles.json` 最新复验：侧边栏 224px，弹窗 880px，正文 14px/20.3px。Esc、焦点返回、遮罩退出和低视口检查通过。截图中的模拟结果标识保留，不作为模型执行证据。
- 项目状态默认并入 Chat 现有关联区域 `.pg-chat-project`，需求中心保留 `.pg-binding`；复用既有导航、主题、侧栏与 Composer，避免并行 Chat 外观调整反复覆盖顶部栏。
- 真实成功轮次曾因自建验证对象缺少标准 trace/registry 元数据被严格拒绝。已补齐标准 capture 格式（created_at、priority、lifecycle_stage、标准目录末尾分隔符），未放宽候选范围校验，继续以全新会话执行。源仓库尚未应用失败产物。

#### 完成门禁与真实交付证据

- 真实用户登录、真实卡片导航和真实平台容器 worker 完成 `REQ-9098-governance-live-validation` 的 req-generate。进入会话时确认轮次数为 0，随后浏览器手动发送。成功轮次产生固定四文件成果，应用前原项目 requirement.md 不存在。
- 浏览器展示完整 Diff、勾选有效维护窗口并显式确认；控制器返回 applied。`evidence/live-files.json` 逐一确认原项目 requirement.md、trace.md、_registry.yaml、CHANGELOG.md 的 SHA-256 与固定候选后镜像一致；浏览器规划中列显示该需求。来源分支为独立副本的 codex/req0022-local-validation。
- `evidence/ui/live-result.json` 与 live-board-before/live-chat-before-send/live-candidate-preview/live-applied/live-board-after 截图是实际观察，非 Mock。历史执行预算中断和元数据拒绝轮次保持失败/拒绝，没有改标或注入成功成果。
- 关闭已完成应用的维护窗口后，连续修改授权验证对象的 registry 标题 10 次，浏览器端实际呈现耗时为 2807、3826、3313、3813、3305、3812、3821、3808、3810、3311 ms，全部低于 5 秒；搜索筛选保持。原始落盘/呈现时间见 `evidence/ui/live-refresh.json`。
- 停止独立 API、Chat worker 和控制器后，执行实际成功记录与私有成果的离线备份/恢复；applied 操作及候选恢复，维护授权未恢复，见 `evidence/live-backup.json`。验收服务已停止，独立副本和私有备份仍保留在本机临时区；未切换或升级当前业务部署。
- REQ 的 PRD、流程、故事、验收、trace 与 prototype/context 已同步实际接口和 UI 映射。25 条 AC 与 RC-001 至 004 的实施证据闭合；本次 apply 完成不替代用户最终产品验收/归档。
- product_data_collection_observability: applicable；affected_layers: web、api、database、request_logs、usage_events、task_traces、task_trace_spans、agent_workflow、deployment；对象存储 N/A（私有成果使用受控本地目录，本次未新增对象存储或跨设备灾备）。validation: 固定事件字典、纯后台轮询无用户事件、脱敏关联、观测失败降级、SQLite/MySQL、Compose 权限和离线恢复均通过。

停止前决策：22/22 tasks 完成，相关测试和真实观察通过，剩余无可执行实施任务；允许串行执行 Workflow Sync 与 AI Usage Hook 后交付。优化建议：独立验证启动器应复用标准 capture 元数据和与项目规模匹配的测试预算，避免在模型执行结束后才发现验证数据格式差异；默认未创建后续 Issue/Change。

#### 工作流与用量收尾

Workflow Sync：opsx.apply → sprint-005，Updated 4、Skipped 2、Errors 0；REQ 子文档 checked 7、warnings 0、blockers 0，acceptance_status 为 pending。REQ trace 已含 openspec_changes[].status: applied 与 /opsx-apply 记录，当前态索引已覆盖。

AI Usage Hook 已使用本任务明确的会话文件运行：status warning、usage_mode unavailable、command_run_count 0、sprint_snapshot skipped、warning_count 1。会话没有可归属的 token_count 用量记录，未估算或伪造用量；需要实际统计时可在会话用量数据可用后重跑 Hook。该 best-effort 统计不影响实现交付。

最终边界：没有 Git 提交/推送、没有归档、没有切换当前业务部署；真实验证进程已停止，独立验证项目在计时结束后恢复到已核验的四文件 applied 内容，私有备份和恢复副本保留。

最终回归核对：新增查看者断言使用测试框架的精简成员表字段；修正测试插入后，后端完整相关集合再次 38 passed（5.96s）。产品代码无追加变动，工作流完成同步串行复核。


### 验收返修记录

- 反馈：用户4张附件显示38项全部阻塞、归档卡片回退、验收文件误报缺失，并要求移除需求中心项目连接栏。
- 根因 confirmed：活动Change缺失时默认proposed覆盖done；Sprint仅查活动目录；精简展示文档用于验收检查；6条registry路径与实际归档目录不符。修复前整库复现为33待开发/4验收/1完成、阻塞38。
- 调整：终态优先；Change/Sprint按完整身份解析活动与归档；归档Change只读；验收检查真实Issue文件；按精确完整ID修正6条已验证路径。未扩大查询scope和写入权限。
- UI：移除需求中心独立连接栏与专用grid行，保留工具栏刷新、同步title、轮询、筛选与草稿。Chat未调整。applied维持验收中语义。
- 整库结果：38对象=25REQ+13BUG；21REQ与13BUG完成、4REQ验收中；blocked=0、drift=0。三份REQ-0000未注册，不自动计入。
- 验证：最终后端5文件35 passed；首轮新增测试的2个调用参数顺序错误已修正并在最终运行通过。前端初次18文件167 passed，最后终态提示调整后聚焦2文件65 passed；TypeScript构建检查通过；视觉证据为evidence/ui/modify-board-*，1440深浅/390/筛选刷新，浏览器pageerror为0。
- 证据边界：浏览器采用仓库解析数据与合成HTTP，只证明当前源码UI；没有切换当前业务部署，不把历史真实闭环证据宣称为本轮真实部署复验。
- REQ 子文档一致性扫尾检查：已同步requirement.md、business-flow.md、user-stories.md、acceptance.md、prototype/web/context.md、prototype.html；trace当前结果由本记录和Workflow Sync承接。capture.md、review.md为历史采集/评审事实，无需重写；旧截图为历史证据，已提供替代截图。
- 文档同步：design、delta spec、API索引、Sprint验收/发布说明已更新。DB、部署、安全规则、客户端生成和成果应用文档无需更新，原因是schema、部署方式、授权边界和成果应用行为未变。
- product_data_collection_observability：affected_layers=[web, api]；本轮仅修正聚合派生值和布局，未新增行为事件、请求封装、日志、Task Trace、DB或存储字段；其余层N/A。validation：接口/权限/写入回归，轮询不新增用户行为埋点，OpenAPI/Orval schema不变。

返修视觉复核补充：首次新截图发现前端blockedTip仍给已完成项强制补验archive.md。已完成项没有待执行动作，现取消该终态重复校验，补充已完成卡片无rc-blocked提示的浏览器断言；重拍后证据覆盖此偏差。


### 返修完成门禁

- Workflow Sync：opsx.modify / sprint-005，Updated 1、Skipped 5、Errors 0；子文档checked 7、warnings 0、blockers 0，验收状态pending。
- AI Usage：status warning、usage_mode unavailable、command_run_count 0、sprint_snapshot skipped、warning_count 1；自动发现会话未获得可归属用量事件，需要统计时可指定具备token_count的会话重跑。未记录原始会话或凭据。
- OpenSpec strict、中文优先、Sprint scope、目录结构、上下文预算、TypeScript与变更空白检查通过。最终后端35/35，最终聚焦前端65/65；完整前端此前167/167。1440深浅、390、筛选刷新截图及computed style已更新，已完成列无缺项提示。
- 停止前决策：本次已授权源码、文档与合成验收均完成；业务部署未切换、产品最终签收待用户确认，不自动归档或创建follow-up Issue/Change。


#### 首屏骨架返修记录

用户附件34c55de6确认独立加载面板推低看板，并同时显示假零值/空态。已移除加载面板，新增指标/计数/卡片原位骨架及不占布局的读屏状态；首次慢请求与后台刷新分离。需求中心显式引入骨架样式，统计数字保持固定行高；首轮浏览器测得指标高度变化，修正样式引用后重验。

REQ子文档一致性扫尾：更新PRD、流程、故事、验收、原型context及HTML；trace状态由Workflow Sync维护。capture/review为历史材料无需修改。API、数据库、权限、部署及客户端生成无需更新，本轮仅UI加载展示。product_data_collection_observability：affected_layers=[web]；请求、日志、事件、Task Trace和存储N/A（未变更请求行为或采集字段），validation为慢请求与刷新合成浏览器回归。

首屏返修验证：延迟合成HTTP下1440深浅主题和390px，指标/工具栏/看板/列头/列体maxTopShift均为0px，pageerror=0；后台刷新卡片和筛选保留。证据evidence/ui/loading-styles.json及loading-*.png。TypeScript检查通过；聚焦前端测试结果见最终门禁回填。OpenSpec严格与中文校验、Sprint scope通过。

首屏返修最终测试：前端2文件65/65通过；旧空态源码断言已同步为仅非加载时出现。TypeScript通过。本轮未改后端，无需重复API/DB测试。


### trace 归属返修记录

来源为用户截图aa14241e：同名trace标题与实际Change正文归属混淆，旧实施记录位于最新结论之前。已分别提供Issue追踪和Change实施记录入口；后端复用现有label/url字段，前端按URL区分key并显示来源，沿用只读权限。REQ-0022 Change最新摘要置顶、历史完整保留；需求trace新增阅读摘要，机器状态经Workflow Sync维护。

REQ子文档一致性扫尾：PRD、流程、故事、acceptance、trace阅读摘要、原型HTML/context均已同步；capture/review历史事实无需更新。API索引补充同名条目按URL识别；DB、部署、安全规则和客户端生成无需更新，原因是schema、授权和运行边界未变。product_data_collection_observability：affected_layers=[web,api]；日志/事件/Task Trace/数据库N/A（未新增字段或请求封装），validation为来源路由、只读权限和抽屉浏览器回归。最新UI证据为仓库文档+合成HTTP，不代表业务部署复验。

同名trace返修验证：后端22通过、前端65通过、TypeScript通过；1440深浅与390共6个浏览器用例，来源URL/标题/正文一致，两种trace只读，来源行无溢出，错误0。首次浏览器脚本点击蒙层中心被正文拦截，改用可见关闭按钮后通过。证据evidence/ui/trace-source-styles.json及截图。OpenSpec严格/中文、目录结构、Sprint scope和空白检查通过。


### trace 单入口返修记录

用户明确收敛为所有REQ/BUG卡片仅展示所属Issue trace.md。本轮取消Change trace入口、拆分标签与额外来源行；所有阶段固定Issue路由，缺失时报不可用，不回退。Change文件、内部状态计算及其他文档保留。此前双入口记录仅作历史。

REQ子文档一致性扫尾：PRD/流程/故事/验收/trace阅读摘要/原型HTML与context已改为单入口；capture/review历史事实无需修改。API索引和delta spec同步；schema/DB/权限/部署/客户端生成无需修改。product_data_collection_observability：affected_layers=[web,api]；日志/事件/Task Trace/存储N/A，无新增采集和请求封装；验证覆盖Issue路由与缺失不回退。

单入口最终验证：后端44通过（含REQ/BUG所有阶段、Change存在但Issue trace缺失）、前端65通过、TypeScript通过；9个浏览器用例通过，正文为Issue文件，缺失只显示不可用，未请求Change trace。证据evidence/ui/issue-trace-styles.json及新截图。OpenSpec严格/中文/目录/Sprint scope/空白校验通过。当前业务部署未切换，产品签收待确认。


### 任务文档定位返修验证

本轮最终前端回归67项通过，TypeScript检查通过；浏览器24个生产组件场景通过，覆盖1440px深浅主题、390px、章节优先、任务回退、缺文件、缺章节、普通入口无定位；同步原型4个交互验证通过。视觉与 computed style 证据见 evidence/ui/tasks-navigation-*。OpenSpec strict、中文、目录、Sprint scope、diff检查通过。后端未改变，本轮未重跑后端测试。

回归中发现读取失败空白态处理影响保存失败草稿保留，已调整为仅在无正文的读取失败时隐藏预览；已有草稿/正文继续保留。对应保存失败、版本冲突、任务勾选回归均通过。Markdown块key使用源块起点，避免连续任务与标题key冲突影响定位。依赖版本检查阻止了pnpm包装命令，改用已安装本地测试与类型检查二进制，没有改项目依赖版本。


任务入口返修执行链路复盘：opsx.modify → Workflow Sync（0错误、7份子文档无阻塞、验收pending）→ AI Usage hook。Hook已执行，但未发现可归属token事件，usage_mode=unavailable，未填充虚构用量。建议后续 tasks.md 使用明确的研发、测试、人工验收章节名称以提升定位可预测性；本轮未自动创建治理Issue。仍为applied且未归档、未切换业务部署。


### Sprint文档返修记录

confirmed根因：聚合未读取关联Sprint且Issue读取接口固定Issue目录。展示、读取、缺失校验现共用关联Sprint解析，保留同项目作用域和只读能力。

Sprint文档返修验证：后端58项通过（聚合、REQ/BUG活动与归档来源、缺失不回退、路径校验、作用域和HTTP接口）；浏览器6个场景通过，覆盖1440深浅与390px正常/缺失态，原型Sprint入口验证通过。证据为evidence/ui/sprint-document-*及样式JSON。OpenSpec strict、中文、目录、Sprint scope与diff检查通过。浏览器为真实仓库聚合/正文与合成HTTP，未切换业务部署。


### 主动作与Tips返修验证

主动作与Tips返修最终验证：70项前端回归及TypeScript通过；12个浏览器状态通过（1440深浅、390、320；禁用/补齐恢复、短提示、长中文及无空格长词），提示矩形与Agent至少保留8px间距，无横向越界。原型禁用/恢复与长提示验证通过。证据为evidence/ui/action-toast-*和样式JSON；使用合成HTTP，只证明本地源码UI，未切换业务部署。OpenSpec strict、中文、目录、Sprint scope和diff检查通过。

根因confirmed：主动作disabled遗漏前端缺失与Issue阻塞；Tips和Agent固定右下且Tips层级较低。通过共享阻塞判断和固定上方安全区域解决。初次回归中旧助手动作断言仍预期“暂不支持”，现应优先提示缺失；新增断言忽略图标后的空白后最终通过。无需修改API/DB/部署/安全/客户端生成文档，因为仅涉及UI判断与布局。


### 主文档持续展示返修验证

主文档持续展示最终验证：后端80项、前端79项、TypeScript通过；15个浏览器场景通过（1440深浅/390，活动和归档REQ/BUG首位入口、Issue正文、只读与缺失不回退），原型主文档入口通过。证据为evidence/ui/main-document-*和样式JSON。OpenSpec strict、中文、目录、Sprint scope及diff校验通过。浏览器使用真实仓库聚合和正文配合合成HTTP，本轮未切换业务部署。

根因confirmed：后端Change文档列表未保留Issue主文档，前端阶段过滤排除后续阶段主文档。现按Issue类型保留真实主文档、置于首位，原文档路由与能力矩阵不变。旧隐藏断言与缺失消息断言已更新后通过。


### Sprint持续展示返修验证

Sprint持续展示验证：前端79项及TypeScript通过；15个浏览器场景通过（1440深浅/390，活动与归档REQ/BUG、主文档优先、关联Sprint正文、只读及缺失提示），原型入口通过。证据见evidence/ui/sprint-persistent-*及样式JSON。OpenSpec严格/中文、目录、Sprint scope与diff检查通过。本轮后端未变，未重跑后端测试；浏览器采用仓库文档与合成HTTP，未切换业务部署。

根因：阶段展示白名单在后续阶段过滤已有sprint.md。现仅扩展展示白名单，主文档排序、关联Sprint解析、只读权限、归档兼容和必需文档校验保持原样。REQ子文档、原型、Change与Sprint验收说明已同步；capture/review保留历史事实。


### 文档分组返修验证

文档分组返修：前端79项回归及TypeScript通过；15个浏览器场景通过，覆盖1440深浅/390、活动与归档REQ/BUG、文档只读和缺失提示。常驻顺序与阶段顺序由九阶段参数回归验证，单组无分隔、双组细线由相邻组CSS控制；computed style记录组间距、边框及宽度，无组内横向溢出。截图见evidence/ui/document-groups-*，原型同步。OpenSpec严格/中文、目录、Sprint scope与diff检查通过。后端无变更，未重跑；浏览器为真实仓库数据配合合成HTTP，未部署。

旧测试预期混排和空格分隔，已按分组DOM顺序更新。窄屏截图改为文档区域滚入可视区后的页面截图；页面既有顶部指标区较高、Agent浮层占位仍保留，本轮没有重构页面布局。


### 紧凑文档区返修验证

紧凑文档区返修：移除分隔线及额外padding，双组margin-top为4px，单组0px。15个浏览器场景通过，1440深浅与390的computed style确认border/padding为0、组间距4px，顺序与只读入口回归通过；原型同步。证据见evidence/ui/document-compact-*。本轮仅CSS与原型样式修改，未重跑TypeScript及单元测试；此前79项结果为历史记录。OpenSpec严格/中文检查通过；未部署，浏览器仍为真实仓库数据配合合成HTTP。


### 文档性能与刷新返修验证

文档性能与刷新返修验证：后端72项、前端80项及TypeScript通过；15个浏览器文档场景通过，1440深浅/390下4.2秒context延迟配合focus/visibility事件仅产生一次初始context请求，卸载取消由单元测试覆盖。权限隔离、写入恢复、草稿冲突回归通过。真实仓库1002文件快照817ms；同快照对照两次物化894/1534ms，一次569/720ms，详见evidence/read-performance.json；仅文件系统对照，不含DB授权/HTTP排队，不能宣称原20.81秒已解决。截图/样式见evidence/ui/refresh-performance-*，合成HTTP，未部署。OpenSpec严格/中文、Sprint scope与diff检查通过。

首次测试命令引用不存在的文件，未执行；修正为治理模块后完成。新增授权测试最初使用错误trace关联格式，被403正确拒绝，改为change_id对象后通过。没有放宽授权。部署后可按服务端request_id关联read_timing日志与Network等待时间，继续定位原现场剩余耗时。


### 卡片日期返修验证

卡片日期返修验证：后端65项、前端80项与TypeScript通过；15个浏览器场景覆盖1440深浅/390，完整日期与未知值、活动/归档REQ/BUG，以及时间与动作矩形无重叠。证据evidence/ui/updated-date-*。九阶段共享卡片日期断言通过。OpenSpec严格/中文、目录、Sprint scope及diff检查通过。原型与REQ子文档已同步；浏览器使用合成日期与HTTP，未部署。旧Capture测试“更新刚刚”已改为缺失真实日期时“更新时间未知”。


### 原型常驻验证

原型常驻返修：后端76项回归通过，补充嵌套预览HTTP授权用例单独通过；TypeScript通过；九阶段常驻前端9项及HTML新页交互聚焦验证通过，浏览器15场景通过（1440深浅/390、多端标识、活动/归档、紧凑布局），证据evidence/ui/prototype-persistent-*。后端覆盖符号链接、越界、缺失路径，预览沿用授权入口。浏览器是合成HTTP，不代表业务部署。

完整前端首轮5项超时；提高时限后81通过/1失败，并有1个异步Mock异常。失败是密码测试last-call被context轮询取代，异常为30秒revokeObjectURL回调在Mock恢复后运行，本次不修改无关业务。全仓中文检查被其他Change fix-requirement-center-apply-lifecycle-sync英文标题阻断，本Change单独中文校验与OpenSpec strict通过；目录、Sprint scope及diff检查通过。未新增Issue，未部署归档。


### 原型标签精简返修验证

原型标签精简验证：后端label/URL/新页模式聚焦检查通过，15个浏览器场景通过（1440深浅/390，活动/归档、多端相对路径、原有文档交互）；证据evidence/ui/prototype-label-*。本轮只改label与原型文案，未重跑全量测试或类型检查；前轮测试限制保留。OpenSpec strict通过；全仓中文校验仍被其他Change英文标题阻断，本Change无报错。未部署归档。
