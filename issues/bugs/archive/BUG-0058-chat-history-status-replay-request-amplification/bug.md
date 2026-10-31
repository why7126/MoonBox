---
bug_id: BUG-0058-chat-history-status-replay-request-amplification
title: 聊天历史状态重建与重复读取导致加载迟缓
severity: high
status: done
owner: 产品团队
discovered_at: '2026-10-21 08:50:06'
created_at: '2026-10-21 09:02:03'
updated_at: 2026-10-31 10:22:33
environment: local
related_requirement: null
related_change: null
root_cause_status: confirmed
lifecycle_stage: archive
product_data_collection_observability:
  status: applicable
  affected_layers: [Web, API, request_logs, Task Trace]
  reason: 历史读取生命周期和请求归因涉及前端请求与服务端观测；本次只生成缺陷文档，不改变采集契约。
  not_applicable: 本次无数据库结构、索引、迁移、对象存储、部署、安全或客户端生成变更。
  validation: 复用同会话真实浏览器刷新与 Network Timing 证据，并重新核对相关读取代码；未执行修复回归或完整性能基准。
---

# 聊天历史状态重建与重复读取导致加载迟缓

## 现象

进入或重访已有历史消息的 Chat 会话时，正文与轮次状态不同步：正文已显示，但已结束轮次仍先显示“正在读取状态”，随后恢复“已完成”。多个组件独立读取同一轮次的事件与状态，执行详情收起后仍有读取活动。

本缺陷指历史读取与状态展示生命周期，不代表历史任务被重新执行。原 capture 的十轮观察为前次证据；本轮新增运行样本为一个已完成轮次，不将两者混为一次计量。

## 复现条件与步骤

环境为本地 Web，Chrome，页面 `/chat`；使用已有授权会话和已结束轮次，无需发送消息、重跑任务或写入业务数据。2026-10-21 同会话探索选用一个已完成归档操作的历史会话，执行详情保持收起。

1. 打开已完成会话，确认正文和“已完成”状态均可见。
2. 打开 Network，筛选 `/api/v1/chat/`，清空记录后刷新页面；保持浏览器缓存默认启用、无网络限速。
3. 观察正文先显示而轮次状态暂时为“正在读取状态”，等待其恢复“已完成”。
4. 按同一轮次归并 `events?after=0`，核对成功响应数量、传输大小及后续分页。
5. 查看事件分页的 Timing，分别记录 Queueing、Stalled、Waiting for server response 和总耗时。

刷新成功且请求返回 200，能够证明本次服务连通性，不仅是旧页面展示。清空到刷新之间保留了一条旧页面在途 turns 请求，显示 unknown；该条排除于成功请求证据，不使用总计数作为单次加载倍数。

## 期望与实际

| 维度 | 期望 | 实际 |
|---|---|---|
| 已结束轮次 | 尽快展示可信摘要，不以完整事件回放作为状态展示前提 | 挂载清空状态，先等事件再读取状态 |
| 请求复用 | 同一轮次的并发消费者共享事件与状态读取 | 状态摘要、消息页脚、执行详情分别请求 |
| 详情收起 | 详情按需读取，后台只保留必要的活跃状态刷新 | hidden 保留挂载，详情仍读取轮次、事件、Diff、context |
| 长历史 | 请求成本受摘要和按需分页控制 | 每页事件后再次读取状态，终态也进行初始回放 |
| 慢响应 | 同一恢复操作避免并发重复轮询 | 固定间隔缺少在途保护，实际影响规模尚未测量 |

## 证据链与确认边界

| 编号 | 类型 | 来源 | 事实与支持判断 |
|---|---|---|---|
| E1 | reproduction | 2026-10-21 同会话 bug-explore，Chrome 本地 `/chat` 刷新 | 单个完成态轮次从“已完成”变成“正在读取状态”，正文已可见，随后恢复完成；确认状态重建现象。 |
| E2 | network_request | 同次刷新后 Chrome 原生 DevTools Network | 同一轮次 `events?after=0` 有 3 条 200 响应，每条约 79.0 kB 传输、78.6 kB 资源大小；另见 after=200 分页。确认重复事件读取，不能据此声称整个页面请求量为三倍。 |
| E3 | network_request | 同次 after=200 请求的 Timing | 总耗时 2.04 s；Queueing 4.51 ms、Stalled 1.28 s、Waiting 738.71 ms、下载 19.19 ms。等待不全在服务端，但不能由 Stalled 单独断定连接池耗尽。 |
| E4 | code_path | `src/web/src/components/chat/TurnActivity.tsx`，useEffect/poll | 挂载时清空 events/turn，cursor=0；先 await 事件再 await 状态，满 200 条继续分页，终态不免除首次读取。 |
| E5 | code_path | `src/web/src/components/chat/ConversationMessages.tsx`，AssistantMeta | 页脚独立 Promise.all 读取同轮 events(after=0) 和 turn；与状态组件未共享结果，补足 capture 漏记的第三个读取方。 |
| E6 | code_path | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx` 与 `components/chat/ExecutionPanel.tsx` | hidden 不卸载详情组件；轮次列表定时刷新，选中轮次串行读取 events、diff、context。事件累计达到 1000 时该详情事件链暂停，不应描述成所有分支无限回放。 |
| E7 | code_path | `src/web/src/components/chat/RecoveryOperationPanel.tsx`，refresh/轮询 effect | 3 秒 setInterval，无在途保护；readSequence 丢弃过期响应。已有 document.hidden、completed 与 20 次预算限制，不能描述为无条件永久轮询。 |
| E8 | code_path | bug-generate 入口对 E4—E7 的聚焦复核 | 相关读取机制仍存在，复用同会话浏览器证据；本次生成未再次进行性能计时。 |

证据保存为本会话工具观察的脱敏摘要，未生成 HAR 或截图附件，不提供不存在的附件链接。省略用户、空间、会话、轮次真实标识及消息正文。当前工作区含已有改动，源码与浏览器构建版本未完成一一映射，不将 HEAD 作为部署版本证明。

## 根因摘要

`confirmed` 仅针对本缺陷的状态重建与重复读取机制：三个消费者各自发起事件读取，终态摘要缺少跨组件复用，状态展示又依赖事件先返回；收起的详情保持挂载并继续读取。直接网络重复响应、真实状态变化和代码路径形成闭环。

该结论不等于已确认所有首屏延迟来源，也不等于已量化重复请求的因果贡献。capture 中整体延迟归因的 probable 属于早期证据口径；本次确认范围明确限定在上述机制。恢复慢响应重叠的实际频率、Stalled 的具体原因、冷暖缓存差异与多轮扩展曲线仍未确认。缺少这些性能量化不应被替换为虚构改善百分比。

已排除将本次现象直接解释为“历史任务重新执行”；当前证据仅支持读取侧问题。也不能把服务端等待当作全部时延，或将收起执行详情视为可靠规避方案。

## 影响范围与严重等级

影响 Chat 历史首屏、会话重访、轮次状态和页脚统计展示，以及隐藏详情请求开销。多轮历史、事件分页较多或响应较慢时具有更大放大风险，具体幅度待基准验证。恢复面板仅影响有关联恢复操作的轮次；本轮单轮样本不证明恢复接口实际发生重叠。

维持 severity: high：核心研发入口存在等待和重复取数，影响连续工作；未见数据丢失、安全事故或全站不可用，不提升为 critical/blocker。建议常规 fix，不按 P0 热修推进。

相关方向为 BUG-0056、BUG-0057、BUG-0059，但不能认定共享同一根因。当前尚无正式关联 REQ、Sprint 或 Change。代码追溯显示状态串行读取见于提交 217d84c2，页脚独立读取见于 72f193ae；尚未开展历史版本对照，不认定为近期回归。

## 修复方向与后续验证

建议统一轮次摘要和共享请求生命周期，终态展示与完整事件详情解耦，详情按需加载，恢复读取合并在途请求。保持活跃/未知状态刷新、权限失效处理、成果核验及写入保护语义，不用过期缓存掩盖状态变化。正式实现仍需缺陷完善、评审、Sprint 与 OpenSpec 流程。

后续验收覆盖：多轮终态与活跃混合历史、长事件分页、首次进入与重访、面板展开/收起、权限变化、错误重试、会话快速切换与慢响应。分别统计正文可见和状态稳定时刻、按 endpoint/turn 分组请求数、传输量、并发与 Timing；用独立采样窗口排除其他导航。恢复慢响应使用明确测试环境验证，无需重跑真实历史任务。

生成阶段未修复代码、执行性能回归或新增测试。后续 bug-complete 已补齐 [根因分析](root-cause.md)、[临时操作建议](workaround.md) 和 [验收标准](acceptance.md)，验收仍待执行；未创建 OpenSpec Change，已通过 [修复评审](review.md)，尚未纳入 Sprint 或实施。
