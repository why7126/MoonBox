---
signed_off: true
note: workflow-sync — 12/12 Change 已 archive；0 applied；人工 sign-off 已完成
title: 临时验证资源治理验收报告
created_at: 2026-10-26 12:12:25
updated_at: 2026-10-30 08:33:52
sprint_id: sprint-014
---

# 临时验证资源治理验收报告

## 验收范围
add-temporary-docker-lifecycle：登记、回收与拒绝路径、契约引用、真实Docker隔离验证。
## 验证事实
14项回归与2容器/1网络实测通过，最终逐项证据以Change验收包为准。到期时钟为模拟。
## 归档授权
用户已授权归档 sprint-014，并授权修复关闭检查发现的当前状态与失效引用；产品版本发布另行执行。
## 证据
[Change追踪](../../../openspec/archive/2026-10-26-add-temporary-docker-lifecycle/trace.md)

## BUG-0064 待执行验收

已纳入BUG-0064-chat-unknown-recovery-container-churn；根因8项证据通过，修复验收not_started。按[缺陷验收标准](../../../issues/bugs/archive/BUG-0064-chat-unknown-recovery-container-churn/acceptance.md)执行AC-01至AC-08，区分合成时钟与真实Docker观察，覆盖SQLite/MySQL、重启、并发、公平性、缓存失效、权限与资源收尾。不得将三项治理Change已归档视为本缺陷已完成。

## BUG-0067 待执行验收

BUG-0067-chat-stream-preview-premature-truncation：根因6项证据门禁通过，修复验收not_started。按[验收标准](../../../issues/bugs/archive/BUG-0067-chat-stream-preview-premature-truncation/acceptance.md)执行AC-001至AC-008，覆盖微片段边界、正文预算、历史缺口、最终答案、权限、查询成本与1440px及窄屏真实页面。单元/合成/真实视觉证据分别记录，当前纳入不表示通过验收。

product_data_collection_observability: applicable；affected_layers: Web、API、DB读取、Agent Workflow；validation: 修复后核对脱敏片段数、读取范围、截断原因及查询成本，当前仅证据就绪。部署、对象存储和物理表迁移暂N/A，若设计扩展边界再补对应验收。

## BUG-0068 待执行验收

BUG-0068-chat-database-lock-execution-interruption：11条根因结构化证据门禁通过，修复验收not_started。按[验收标准](../../../issues/bugs/archive/BUG-0068-chat-database-lock-execution-interruption/acceptance.md)执行AC-001至AC-009，覆盖零行UPDATE、重复核验、事务外文件扫描、SQLite/MySQL并发、失败恢复、幂等与权限。合成复现不能替代真实运行验收，原失败轮次不重放。

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、task_traces、task_trace_spans、Agent Workflow；validation: 根因和验收设计就绪，修复验证待执行；usage_events、对象存储及客户端生成当前N/A，设计改变契约时补对应门禁。

## BUG-0069 待执行验收

BUG-0069-chat-interrupted-successor-proof-missing根因6条证据门禁通过，验收not_started。按[验收标准](../../../issues/bugs/archive/BUG-0069-chat-interrupted-successor-proof-missing/acceptance.md)执行AC-001至AC-008，覆盖无旧同步证明正例、证据不足负例、原历史不变、并发与幂等、1440/390视觉、SQLite/MySQL及真实产品发送和现场独立验证。原BUG-0061历史passed不计入本次结果。

product_data_collection_observability: affected；affected_layers: governance workflow、completion proof、API admission、Web UI、recovery audit；validation: AC-002至AC-007尚待实施后执行。本次规划不解除保护或触发正式归档。

## BUG-0056 真实后台并发返修

2026-10-27 晚间用户反馈打开、刷新仍需二十多秒，本轮新增 AC-010，在 backend、chat-worker、governance-controller 同时运行时测量真实页面。首轮隔离通过记录保留，不能代替现场结论。重复状态核对、后台整库备份读锁、孤儿引用全表扫描已定位并修复；当前真实页面最终样本与资源收尾仍待完成。证据统一见 [返修台账](../../../openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/acceptance-fixes.md)。

product_data_collection_observability: applicable；affected_layers: API、DB 读写与索引、request_logs、自动快照 Task Trace、后台 Workflow；validation: SQLite 22项后台回归、MySQL 增量及需求中心173项前端回归通过，现场性能尚待通过。沿用既有日志及计时字段，无新增敏感内容采集。

### BUG-0056 真实后台性能返修复验

后台三服务同时运行时，30次暖导航首卡P95 1.776秒、HTTP1.359秒，30次刷新HTTP P95 1.111秒，零错误、后台健康无重启。隔离冷暖、配对改善及资源预算通过，证据见[返修台账](../../../openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/acceptance-fixes.md)。首次重启及源版本变化初始化8.620秒单列，不将其称为暖读。保留历史执行保护与授权核验；本轮不自动归档。

### BUG-0056 第二批跨负载返修进行中

上轮性能passed保留为历史，正式页面暖缓存再次出现20.148/23.75秒。本批减少重复维护、健康检查导入、审计主线程等待、逐卡状态查询与纯文件元数据重复处理；保留快照双遍一致性、权限新鲜复核及全部旧执行历史。当前SQLite聚焦回归与MySQL23项通过；最新正式路由跨负载样本尚待完成，锁屏时不以隔离样本代替。未归档，详见[返修台账](../../../openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/acceptance-fixes.md)。

2026-10-28检查点：BUG-0056最新满容量4并发30分钟1372请求零错误，内存末段增长18.84MiB、缓存45.46MiB均在预算内。固定副本context配对P95改善83.95%。正式页面跨负载最终样本与Firefox恢复仍被锁屏阻断，本批不标记完成、不归档；临时Docker零残留。

### BUG-0056 返修续接检查点（2026-10-28 10:52）

2026-10-28 10:52检查点：旧归档重复读取修复已部署，24模块摘要匹配，158项归档及128项快照/并发边界回归通过。正式高负载窗口保留29条诊断、全部200，其中26条超过3秒，最大59.087秒；已超过100样本P95允许的慢样本数，提前终止失败窗口，不计算完整窗口P95、不宣称通过。主机负载29.49→59.11（10核），交换区约13GB；该关联不是唯一根因证明。额外压力已停止，登记资源零残留，临时Web入口已移除，Firefox正式需求中心已同步29卡。等待用户选择释放其他应用负载或保持现状继续定位，未擅停其他项目。最新源码隔离长测及完整正式跨负载窗口仍未完成，不同步返修完成或ready，不归档。证据位于对应Change的tail-measurements/proof-read。

### BUG-0056 释放其他应用负载后的完整复验（2026-10-28）

2026-10-28 11:59:29 用户确认释放其他应用负载后复测：正式页面自然/额外2CPU两窗口各100次打开和100次刷新，完整保留400样本，全部200、唯一请求ID、同一快照、214授权卡/29可见卡。自然打开/刷新HTTP P95为10.811/6.757秒，额外2CPU为10.608/22.488秒；打开首卡P95为12.040/11.620秒。自然打开最慢20.704秒，压力刷新最慢39.700秒，四组均未达标。24个部署模块前后与工作区一致，复用原286项回归记录，本轮未重新执行该批单测。三后台始终健康、无重启；自然负载曾从4.38回升至33.45，压力中段/终点为23.01/24.87。负载与长尾相关，但不能认定主机是唯一根因；完整快照读取与解析仍占主要成本。额外压力已停止、临时资源零残留、采样入口已移除、Firefox已恢复正式需求中心。原用户环境选择已落实，不再等待该选择；仍为性能返修未完成，未发出opsx.modify完成或ready，不归档。

证据位于对应Change的 `evidence/acceptance/tail-measurements/released-host-20261028/`。

## 2026-10-29 摘要读取与分段验收返修

已按用户授权在原 Change 内补充方案评审，允许独立摘要读取、按需深层验收检查及活动卡片轻量状态接口。首页不再每 3 秒全量轮询，文档仍按需读取；摘要不是验收或发送准入证明。权限、快照一致性、安全上限和历史执行围栏保留。API 与生成客户端同步，无数据库迁移。

本轮 149 项前端回归和 TypeScript 通过；看板/摘要 84 项、冷读/并发/缓存边界 55 项增量回归通过。服务更新不等于性能通过：首次请求 504；自然刷新 30 次、同一版本，HTTP P95 2.226 秒；完整视口打开 30 次、同一版本，HTTP P95 5.657 秒、首卡 P95 8.472 秒，未达到 3/4 秒目标。历史失败及分段证据保留于 Change 的 evidence/acceptance/summary-repair-20261029/。

最新补丁将摘要冷读纳入现有 CPU 配额约束的双线程读取，并去除同一临时目录的重复创建，尚待更新后正式验证。整体仍为返修中，不同步 ready 或归档；原 applied 和首次完成时间不变。product_data_collection_observability: affected；affected_layers: REST API、Web 请求、请求分段证据；validation: request_id 与 Server-Timing 关联、权限与错误态回归；DB/新增日志表 N/A：本轮未新增表或持久日志字段。

## 2026-10-29 摘要返修当前验证

本轮原 Change 边界修订已明确获准；首页摘要、按对象完整检查、活动状态轻量更新和取消全量轮询已实现。正式后台持续运行，120 次同版本样本达到原 P95 门槛：自然打开/刷新 0.455/0.702 秒，额外 2 CPU 打开/刷新 2.139/2.992 秒；首卡 0.805/2.986 秒。压力刷新最大 3.292 秒，文档在八组资源压力下首次失败后重试成功，这些边界和历史失败均保留。

当前通过：冷暖 HTTP/首卡、配对改善、上限读取与超限拒绝、权限/状态保护、SQLite/MySQL、前端回归和真实筛选/文档恢复。仍待 30 分钟资源结果及自动验收收尾，不以本段替代 ready，不归档。证据：openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/evidence/acceptance/summary-repair-20261029/；详细记录见该 Change acceptance-fixes.md。


## 2026-10-30 当前修复验证

首页摘要、按需完整核验、取消全量轮询、快照生命周期与有界解析缓存，以及需求中心只读审计响应后执行均已实现。原权限、文件安全、历史围栏和安全上限保留。

|正式场景（各30次）|HTTP P95|首卡 P95|
|---|---:|---:|
|自然打开|1.214秒|2.255秒|
|自然刷新|1.295秒|不适用|
|额外2CPU打开|1.428秒|2.279秒|
|额外2CPU刷新|1.600秒|不适用|

正式120请求同版本、218授权对象、默认30卡，全部成功、分段独占对账通过；三个后台服务持续运行，健康且零重启。性能限于记录的自然/2CPU窗口，不保证任意宿主过载。

快照最终版本四组30分钟共3340请求、0错误，末段RSS增长最大25.063MiB，缓存、峰值RSS和CPU预算通过；审计补丁未改变读取算法，旧资源/配对结果按明确哈希边界复用，不冒称新审计版本重跑资源长测。context/MD配对改善87.54%/70.29%。主机和实际镜像各98项审计/权限/Chat增量回归通过，原Linux182项和前端149项证据保留。

交付范围为已验证冻结基线加BUG-0056补丁；ChatRoute补丁与当前语法树一致，其余17个并行文件的无关变化未纳入。API/观测文档、生成客户端及UI摘要状态已同步；审计补丁无正文模型、DB迁移或权限变化。强杀时尚未落库的只读日志可能丢失，用户已授权该时序；正常退出等待，容量满回退同步。

当前证据：openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/evidence/acceptance/summary-repair-20261029/audit-final/。此前20秒、59秒、400样本失败、资源增长失败和lifetime-final压力打开失败全部保留。

历史阶段约束：不覆盖首次applied及execution.completed_at，不归档。自动验收及最终准入另由共享门禁确认。

product_data_collection_observability: affected；affected_layers: REST请求、Web摘要读取、请求日志与分段；validation: 请求ID/独占计时、后台审计最终落库、权限、安全及跨负载样本。


## 2026-10-30 00:30 最新未通过结论

最终专用日志版本正式120请求全部成功、同版本、分段对账通过；120条审计记录及120条后台耗时日志均按request_id一一核对成功。自然打开/刷新HTTP P95 1.123/1.858秒；额外2CPU打开HTTP/首卡4.199/5.487秒仍失败，刷新2.619秒通过。三后台持续健康零重启，主机负载升至约14.5（10核），慢打开主要耗在快照读取，不能将全部波动单独归因于主机。

正式只读挂载2341文件、11153053字节，12组1/2/4线程交错对照全部字节等价；墙钟中位0.748/0.564/0.529秒，CPU中位0.746/0.762/0.817秒。4线程比2线程仅约6%更快且CPU增加，保留现有2线程，不实施无充分收益的并发修改。用户需选择再次稳定其他任务负载、评审进一步收窄读取范围，或暂停；未擅停其他应用。当前继续保留返修状态，不同步完成、不ready、不归档，前文通过窗口为历史阶段。证据见关联Change的evidence/acceptance/summary-repair-20261029/audit-final/。


BUG-0056 卡片展示局部返修：源码已移除状态详情、检查最新结果按钮与验收待检查提示，后台准入保留。本轮未更新正式服务；性能验收仍未通过，不构成归档就绪。


### 2026-10-30 最终跨负载复验与收尾

用户授权继续原范围验收返修，达标后归档。现有实现完成正式120样本同版本复验：自然打开HTTP/首卡P95为0.307/0.573秒、刷新0.389秒；额外2CPU打开0.384/0.715秒、刷新1.199秒。全部200、218授权对象、默认30卡、120唯一请求ID分段对账通过，120后台审计成功记录关联。后台三服务持续健康零重启；压力实测约202% CPU，主机负载记录于证据包，临时容器与页面已清理。

正文与清单分离属于评审候选优化，本轮依据现有实现达标结果不纳入交付，未实施也不声明读取量减少。原权限、安全、快照一致性和性能门槛不变；此前高负载失败保留，本轮结论限于实测窗口，不保证任意主机过载。前端173项、TypeScript和深浅1440px证据已通过；后端源指纹一致的资源/配对/边界证据按明确版本边界复用，旧前端指纹另存，详见 openspec/archive/2026-10-30-fix-requirement-center-context-load-latency/evidence/acceptance/final-20261030/reuse-boundary.md。

本记录替代前文“当前待复测/待更新服务”的当前态描述，历史失败与决策原文保留。自动验收与归档最终准入仍以本轮共享门禁结果为准，未提前宣称归档。


## 当前归档核对（2026-10-30 08:31:53）

12个Change均已归档，118/118任务完成，7个BUG均在archive目录。前文计划、失败窗口与返修记录保留为历史；当前交付与验收以归档Change trace及有效验收证据为准。此次仅更新证据定位与迭代收尾文档，不改写原始manifest或历史测试结果。

## 产品数据采集与链路观测关闭复核

product_data_collection_observability: applicable

- affected_layers: Web、API、DB、request_logs、task_traces、task_trace_spans、Agent Workflow、恢复审计。
- reason: 本迭代涉及恢复调度与结果持久化、自动核验读取、正文分页预览、数据库事务边界、需求中心读取性能和后继完成证明，沿用可信请求标识及脱敏链路。
- validation: 已核对七项BUG归档Change的trace/verification与签认证据；涵盖SQLite/MySQL、请求计数与权限、恢复退避、读取不改业务状态、事务诊断脱敏、后继证明及BUG-0056最终120请求与后台审计关联。归档就绪由Sprint readiness复核，不将历史失败窗口改写为通过。
- N/A: 未新增对象存储读写、未启用客户端或埋点保留周期；后台恢复和直接API没有对应用户动作，不伪造usage_events。纯治理Change仅改变本地流程与校验，不新增产品API、DB或遥测表。

## AI用量与环境检查边界

ai_usage_mode: estimated_fallback。已自动发现本地会话并刷新快照，但仍有用量覆盖警告；不作为精确Token成本，需完整可归因会话后再回填。临时Docker到期扫描因docker info连接失败未完成，本次未创建或删除容器；历史清理结果只依据各Change原有证据。目录校验通过，遗留SQLite运行目录警告保留，不在本次归档中迁移数据。


## 最终验收与关闭结论

验收结论：通过。归档签认依据：用户明确执行sprint-014归档并授权修复后重试；全部Change归档证据及严格关闭检查通过。关闭时间：2026-10-30 08:33:22。历史失败、合成验证与真实运行证据边界保持不变。
