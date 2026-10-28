---
title: 需求中心首屏性能修复追溯记录
created_at: "2026-10-26 20:01:22"
updated_at: 2026-10-28 11:59:29
change_id: fix-requirement-center-context-load-latency
status: applied
bug: BUG-0056-requirement-center-context-load-latency
iteration: sprint-014
execution:
  schema_version: 1
  started_at: 2026-10-27 06:51:36
  completed_at: 2026-10-27 12:38:48
  last_event: opsx.apply
---

# 需求中心首屏性能修复追溯记录

## 来源与交付

来源BUG-0056-requirement-center-context-load-latency，已评审并纳入sprint-014，估算沿用5人天。13项实施任务完成，opsx.apply已同步；原BUG-0016只作复发关联，不改历史结论。请求内身份/归档索引、有界快照字节复用、纯读投影复用和请求分段计时已实现，既有授权、围栏、执行核验及安全上限保持有效。其他任务未提交改动已保留，未提交或部署。

## 验证与验收

根因门禁8条证据通过。Linux162测试和6子测试、MySQL83、前端165及增量验证通过；实际执行源码指纹与工作区一致。context/MD暖读配对P95改善64.95%/56.63%；浏览器暖100/冷30首卡P95为2.742/2.442秒，原慢样本完整保留。上限10000文件/32MiB及1458卡的冷暖与资源证据已完成；修复四组资源预算通过，历史基线内存超预算单列。

自动验收8/8通过，完整报告：[验收报告](evidence/acceptance/20261027124209183130-5049da30/summary.md)。方法、原始数据、空库首次初始化限制、接近预算项及真实浏览器/合成回归区分见[验证记录](verification.md)。API观测文档及知识库已同步，无响应正文、DB迁移或客户端生成。临时Docker/MySQL run均已check clean，测试前端服务已停止。

## 流程复盘

用户两次确认已落实：当前固定副本替代历史规模；保留安全上限并测超限拒绝。早期夹具完整性、长请求RSS采样和尾部样本数量问题均在当前apply内修正，失败记录未丢弃。经验已沉淀至docs/knowledge-base/incidents/requirement-context-read-cost.md，建议后续性能长测入口先验证扩容样本与独立RSS采样；未自动创建新Issue/Change。

AI Usage的opsx.apply Hook为actual、1个command run、0 warning；opsx.accept收尾另由统一Hook记录。治理运行ID run-15e09958896d4be980220ebf8db7de35。临时副本归档预演已通过，最终归档准入由本轮收尾共享门禁检查；本轮未获正式归档授权。

最终准入补证：受保护性能条文要求规格全文进入验收输入，已补齐AC-001/002覆盖。增量复验执行2项、复用6项，8/8通过；实现和量化阈值未变。

## 2026-10-27 真实后台并发返修

完成后台锁与重复读取修复；真实后台暖导航30次首卡P95 1.776秒、HTTP1.359秒，刷新30次P95 1.111秒，三个服务健康且无重启。首次服务重启及源版本更新初始化8.620秒单列限制，未冒充暖样本。完整偏差、调整、失败批次、验证与文档扫尾见[返修台账](acceptance-fixes.md)，证据evidence/acceptance/repair-measurements。保留首次apply事实及旧执行历史，待本轮自动验收同步，不自动归档。

## 第二批暖缓存长尾返修进展

本批已更新本地服务并验证17个相关模块源码一致。20.148秒打开与23.75秒刷新为本次复发证据，修复覆盖后台重复写入/扫描、健康检查导入、同步审计等待、请求内状态和权限批量读取、纯快照事实复用。历史执行保护、快照围栏与末尾权限核验保留。

固定副本配对和安全回归已通过；正式页面最终跨负载采样因锁屏待补、30分钟资源验证进行中。当前为返修中，旧apply事实和首次完成时间不变。本批尚未完成同步，不归档。完整台账见[返修台账](acceptance-fixes.md)，本批证据见[evidence/acceptance/tail-measurements/inputs.json](evidence/acceptance/tail-measurements/inputs.json)。

2026-10-28检查点：满容量4并发30分钟1372请求零错误，资源预算通过；正式页面最终跨负载与页面恢复仍因锁屏待补。临时Docker零残留、Web采样入口已移除。未同步本批完成事件，未覆盖首次apply时间，未归档；续接范围见返修台账。

2026-10-28 10:52检查点：旧归档重复读取修复已部署，24模块摘要匹配，158项归档及128项快照/并发边界回归通过。正式高负载窗口保留29条诊断、全部200，其中26条超过3秒，最大59.087秒；已超过100样本P95允许的慢样本数，提前终止失败窗口，不计算完整窗口P95、不宣称通过。主机负载29.49→59.11（10核），交换区约13GB；该关联不是唯一根因证明。额外压力已停止，登记资源零残留，临时Web入口已移除，Firefox正式需求中心已同步29卡。等待用户选择释放其他应用负载或保持现状继续定位，未擅停其他项目。最新源码隔离长测及完整正式跨负载窗口仍未完成，不同步返修完成或ready，不归档。证据：evidence/acceptance/tail-measurements/proof-read。

2026-10-28 11:59:29 用户确认释放其他应用负载后复测：正式页面自然/额外2CPU两窗口各100次打开和100次刷新，完整保留400样本，全部200、唯一请求ID、同一快照、214授权卡/29可见卡。自然打开/刷新HTTP P95为10.811/6.757秒，额外2CPU为10.608/22.488秒；打开首卡P95为12.040/11.620秒。自然打开最慢20.704秒，压力刷新最慢39.700秒，四组均未达标。24个部署模块前后与工作区一致，复用原286项回归记录，本轮未重新执行该批单测。三后台始终健康、无重启；自然负载曾从4.38回升至33.45，压力中段/终点为23.01/24.87。负载与长尾相关，但不能认定主机是唯一根因；完整快照读取与解析仍占主要成本。额外压力已停止、临时资源零残留、采样入口已移除、Firefox已恢复正式需求中心。原用户环境选择已落实，不再等待该选择；仍为性能返修未完成，未发出opsx.modify完成或ready，不归档。

证据：[完整400样本](evidence/acceptance/tail-measurements/released-host-20261028/live-browser.json)、[统计与版本](evidence/acceptance/tail-measurements/released-host-20261028/summary.json)、[性能门禁失败](evidence/acceptance/tail-measurements/released-host-20261028/performance-gate.json)。
