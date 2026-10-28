---
note: workflow-sync — 10/11 Change 已 archive；1 applied；待人工 sign-off
title: 临时验证资源治理验收报告
created_at: 2026-10-26 12:12:25
updated_at: 2026-10-28 00:06:28
sprint_id: sprint-014
---

# 临时验证资源治理验收报告

## 验收范围
add-temporary-docker-lifecycle：登记、回收与拒绝路径、契约引用、真实Docker隔离验证。
## 验证事实
14项回归与2容器/1网络实测通过，最终逐项证据以Change验收包为准。到期时钟为模拟。
## 待确认
本次仅实施与验收，未授权归档Sprint或发布。
## 证据
[Change追踪](../../../openspec/changes/add-temporary-docker-lifecycle/trace.md)

## BUG-0064 待执行验收

已纳入BUG-0064-chat-unknown-recovery-container-churn；根因8项证据通过，修复验收not_started。按[缺陷验收标准](../../../issues/bugs/review/BUG-0064-chat-unknown-recovery-container-churn/acceptance.md)执行AC-01至AC-08，区分合成时钟与真实Docker观察，覆盖SQLite/MySQL、重启、并发、公平性、缓存失效、权限与资源收尾。不得将三项治理Change已归档视为本缺陷已完成。

## BUG-0067 待执行验收

BUG-0067-chat-stream-preview-premature-truncation：根因6项证据门禁通过，修复验收not_started。按[验收标准](../../../issues/bugs/review/BUG-0067-chat-stream-preview-premature-truncation/acceptance.md)执行AC-001至AC-008，覆盖微片段边界、正文预算、历史缺口、最终答案、权限、查询成本与1440px及窄屏真实页面。单元/合成/真实视觉证据分别记录，当前纳入不表示通过验收。

product_data_collection_observability: applicable；affected_layers: Web、API、DB读取、Agent Workflow；validation: 修复后核对脱敏片段数、读取范围、截断原因及查询成本，当前仅证据就绪。部署、对象存储和物理表迁移暂N/A，若设计扩展边界再补对应验收。

## BUG-0068 待执行验收

BUG-0068-chat-database-lock-execution-interruption：11条根因结构化证据门禁通过，修复验收not_started。按[验收标准](../../../issues/bugs/review/BUG-0068-chat-database-lock-execution-interruption/acceptance.md)执行AC-001至AC-009，覆盖零行UPDATE、重复核验、事务外文件扫描、SQLite/MySQL并发、失败恢复、幂等与权限。合成复现不能替代真实运行验收，原失败轮次不重放。

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、task_traces、task_trace_spans、Agent Workflow；validation: 根因和验收设计就绪，修复验证待执行；usage_events、对象存储及客户端生成当前N/A，设计改变契约时补对应门禁。

## BUG-0069 待执行验收

BUG-0069-chat-interrupted-successor-proof-missing根因6条证据门禁通过，验收not_started。按[验收标准](../../../issues/bugs/review/BUG-0069-chat-interrupted-successor-proof-missing/acceptance.md)执行AC-001至AC-008，覆盖无旧同步证明正例、证据不足负例、原历史不变、并发与幂等、1440/390视觉、SQLite/MySQL及真实产品发送和现场独立验证。原BUG-0061历史passed不计入本次结果。

product_data_collection_observability: affected；affected_layers: governance workflow、completion proof、API admission、Web UI、recovery audit；validation: AC-002至AC-007尚待实施后执行。本次规划不解除保护或触发正式归档。

## BUG-0056 真实后台并发返修

2026-10-27 晚间用户反馈打开、刷新仍需二十多秒，本轮新增 AC-010，在 backend、chat-worker、governance-controller 同时运行时测量真实页面。首轮隔离通过记录保留，不能代替现场结论。重复状态核对、后台整库备份读锁、孤儿引用全表扫描已定位并修复；当前真实页面最终样本与资源收尾仍待完成。证据统一见 [返修台账](../../../openspec/changes/fix-requirement-center-context-load-latency/acceptance-fixes.md)。

product_data_collection_observability: applicable；affected_layers: API、DB 读写与索引、request_logs、自动快照 Task Trace、后台 Workflow；validation: SQLite 22项后台回归、MySQL 增量及需求中心173项前端回归通过，现场性能尚待通过。沿用既有日志及计时字段，无新增敏感内容采集。

### BUG-0056 真实后台性能返修复验

后台三服务同时运行时，30次暖导航首卡P95 1.776秒、HTTP1.359秒，30次刷新HTTP P95 1.111秒，零错误、后台健康无重启。隔离冷暖、配对改善及资源预算通过，证据见[返修台账](../../../openspec/changes/fix-requirement-center-context-load-latency/acceptance-fixes.md)。首次重启及源版本变化初始化8.620秒单列，不将其称为暖读。保留历史执行保护与授权核验；本轮不自动归档。

### BUG-0056 第二批跨负载返修进行中

上轮性能passed保留为历史，正式页面暖缓存再次出现20.148/23.75秒。本批减少重复维护、健康检查导入、审计主线程等待、逐卡状态查询与纯文件元数据重复处理；保留快照双遍一致性、权限新鲜复核及全部旧执行历史。当前SQLite聚焦回归与MySQL23项通过；最新正式路由跨负载样本尚待完成，锁屏时不以隔离样本代替。未归档，详见[返修台账](../../../openspec/changes/fix-requirement-center-context-load-latency/acceptance-fixes.md)。

2026-10-28检查点：BUG-0056最新满容量4并发30分钟1372请求零错误，内存末段增长18.84MiB、缓存45.46MiB均在预算内。固定副本context配对P95改善83.95%。正式页面跨负载最终样本与Firefox恢复仍被锁屏阻断，本批不标记完成、不归档；临时Docker零残留。

### BUG-0056 返修续接检查点（2026-10-28 10:52）

2026-10-28 10:52检查点：旧归档重复读取修复已部署，24模块摘要匹配，158项归档及128项快照/并发边界回归通过。正式高负载窗口保留29条诊断、全部200，其中26条超过3秒，最大59.087秒；已超过100样本P95允许的慢样本数，提前终止失败窗口，不计算完整窗口P95、不宣称通过。主机负载29.49→59.11（10核），交换区约13GB；该关联不是唯一根因证明。额外压力已停止，登记资源零残留，临时Web入口已移除，Firefox正式需求中心已同步29卡。等待用户选择释放其他应用负载或保持现状继续定位，未擅停其他项目。最新源码隔离长测及完整正式跨负载窗口仍未完成，不同步返修完成或ready，不归档。证据位于对应Change的tail-measurements/proof-read。

### BUG-0056 释放其他应用负载后的完整复验（2026-10-28）

2026-10-28 11:59:29 用户确认释放其他应用负载后复测：正式页面自然/额外2CPU两窗口各100次打开和100次刷新，完整保留400样本，全部200、唯一请求ID、同一快照、214授权卡/29可见卡。自然打开/刷新HTTP P95为10.811/6.757秒，额外2CPU为10.608/22.488秒；打开首卡P95为12.040/11.620秒。自然打开最慢20.704秒，压力刷新最慢39.700秒，四组均未达标。24个部署模块前后与工作区一致，复用原286项回归记录，本轮未重新执行该批单测。三后台始终健康、无重启；自然负载曾从4.38回升至33.45，压力中段/终点为23.01/24.87。负载与长尾相关，但不能认定主机是唯一根因；完整快照读取与解析仍占主要成本。额外压力已停止、临时资源零残留、采样入口已移除、Firefox已恢复正式需求中心。原用户环境选择已落实，不再等待该选择；仍为性能返修未完成，未发出opsx.modify完成或ready，不归档。

证据位于对应Change的 `evidence/acceptance/tail-measurements/released-host-20261028/`。
