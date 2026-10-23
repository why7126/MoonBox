---
bug_id: BUG-0058-chat-history-status-replay-request-amplification
title: 聊天历史逐轮重放状态与重复轮询导致加载迟缓缺陷记录
status: captured
created_at: '2026-10-21 08:50:06'
updated_at: '2026-10-21 08:50:06'
severity: high
environment: local
owner: 产品团队
source: 用户授权与同会话 explore 证据
related_requirement: null
related_bug: null
root_cause_status: probable
lifecycle_stage: plan
---

# 聊天历史逐轮重放状态与重复轮询导致加载迟缓缺陷记录

用户第 3 项：Chat 历史对话显示慢，每轮状态重新更新。影响历史首屏、重访会话以及后台请求数量；不等同于历史任务重新执行。

## 已确认的证据

| 编号 | 类型 | 来源 | 事实及确认边界 |
|---|---|---|---|
| E1 | reproduction | 2026-10-21 同会话 Chrome，需求中心“查看执行”进入已完成会话后切回对话 | 十轮历史消息同时显示“正在读取状态”，随后部分变为“已完成”。确认状态重新读取现象；未观察到任务重新执行。 |
| E2 | code_path | src/web/src/components/chat/TurnActivity.tsx，useEffect/poll | 每轮挂载清空 events/turn，从 cursor=0 先读事件、后读轮次状态；每批 200 条时继续翻页，终态轮次也进行首次加载。 |
| E3 | code_path | src/web/src/components/chat/ExecutionPanel.tsx 与 pages/catalog/ChatWorkbenchPage.tsx | 详情用 hidden 隐藏但仍挂载；轮次列表常规轮询，事件、Diff、context 串行加载，无基于面板隐藏的停用开关。 |
| E4 | code_path | src/web/src/components/chat/RecoveryOperationPanel.tsx，refresh/轮询 effect | 固定 3 s setInterval 发起读取，无单请求在途保护；readSequence 丢弃较早返回结果。响应超过间隔时存在重叠与延迟更新风险，实际重叠规模待测。 |
| E5 | network_request | 同次 DevTools Network | 观察到多个不同轮次/恢复操作请求及 events?after=400；累计请求数从 68 到 87 再到 174。该计数混有之前导航与轮询，不能作为单次历史加载的独立请求数或倍数。 |

## 根因判断

逐轮状态清空及历史事件重放机制已确认；多处轮询在隐藏面板仍运行的代码路径已确认。整体延迟根因标 probable：需要冷暖缓存对照、请求归因及资源等待数据，才能量化重复请求对总时延的贡献。不存在“历史任务被重新执行”的证据。

## 判重与拆分

BUG-0030 为助手正文缺失，BUG-0048 为清理逻辑误删会话区域，BUG-0055 为同轮消息顺序错误；本条关注状态重建与请求放大，可独立修复验收。历史事件重放、隐藏面板轮询与逐轮恢复请求放入同一读取生命周期修复范围。

## 复现与期望

1. 打开包含多轮已结束对话的会话，记录正文与每轮状态可见时刻。
2. 切换会话再返回，并分别保持轨迹面板展开/收起。
3. 期望已结束轮次快速显示稳定状态，详情按需取数；实际逐轮重新读取状态。

## 待补证与验收建议

在每次操作前清空 Network，统计按 endpoint/turn 脱敏分组的请求数、字节数、并发峰值、排队与服务端耗时；记录轮次数、事件数与冷暖缓存。受控慢响应验证恢复请求是否重叠及旧结果丢弃，复验隐藏面板行为。验收覆盖长历史分页、终态/活跃/未知状态、权限变化、故障重试；列表使用摘要不应丢失完成核验与写入保护语义。

## 证据归属与边界

证据复用同会话 2026-10-21 浏览器工具结果与源码只读检查；本次 capture 未重新计时。运行态样本未保存 HAR/截图文件，以上为脱敏观察摘要，不伪称已有附件。代码行号可能变化，按文件与函数定位。浏览器 DOM 只读接口不支持 performance，已改用 Chrome 原生 DevTools 取证；未因单工具失败判定服务不可用。

后续补证优先自主浏览器与服务端可用观测；涉及创建会话或执行命令的采样使用明确测试对象或用户自然操作。返回格式：环境/版本、动作、脱敏路径、状态码、总耗时、Waiting、阶段计时、样本规模；禁止凭证、原始消息/文档、个人标识及本机路径。

## 严重等级与观测声明

初判 high：核心研发入口出现明显长等待，影响日常连续操作；无数据丢失、安全事故或全站不可用证据，不提升为 critical/blocker。

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、request_logs、Task Trace
- reason: 性能定位涉及请求等待及治理步骤计时；本次只记录 BUG，不改变埋点或日志契约。DB 索引/结构、对象存储和部署变更尚无证据支持，暂不提出修改。
- validation: 同会话浏览器观察与聚焦代码路径；未执行修复或性能回归，剩余计时见待补证。

