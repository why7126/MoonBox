---
bug_id: BUG-0058-chat-history-status-replay-request-amplification
title: 聊天历史状态重建与重复读取根因分析
root_cause_status: confirmed
created_at: '2026-10-21 09:05:51'
updated_at: '2026-10-21 09:05:51'
---

# 聊天历史状态重建与重复读取根因分析

## 根因状态

status: confirmed

确认范围为历史状态重建、相同轮次重复读取和隐藏详情仍取数的机制；不声称已经确认所有页面延迟来源或量化各机制贡献。恢复操作慢响应重叠的运行规模与 Stalled 的具体成因不在 confirmed 范围。

## 现象

本地 Chrome 已完成会话刷新后，正文可见而状态先显示“正在读取状态”，随后恢复完成。同一轮次事件首页出现三条成功响应，详情面板当时收起。复现条件与采样边界见 [缺陷说明](bug.md)。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | 2026-10-21 同会话 bug-explore，Chrome 本地 `/chat`；bug.md E1 | 已完成单轮会话刷新，正文已显示但状态重新读取，随后恢复完成 | 历史状态显示确实经历重建，不只是旧页面残留 |
| E2 | network_request | 同次 DevTools Network；bug.md E2 | 同一轮次 events?after=0 三条 200 响应，各约 79.0 kB；另见 after=200 | 相同事件数据被重复传输；不能据此推断整页请求三倍 |
| E3 | network_request | 同次 after=200 的 Timing；bug.md E3 | 总计 2.04 s，Queueing 4.51 ms、Stalled 1.28 s、Waiting 738.71 ms、下载 19.19 ms | 时延包含浏览器连接等待与响应等待，不能全部归入服务端处理 |
| E4 | code_path | `src/web/src/components/chat/TurnActivity.tsx:28`，useEffect/poll | 清空 events/turn，cursor=0，串行事件→状态；每满200条继续两次读取 | 终态也要重放，状态展示被首次事件读取阻塞 |
| E5 | code_path | `src/web/src/components/chat/ConversationMessages.tsx:160`，AssistantMeta | 独立并发读取事件首页与 turn，与 TurnActivity 无共享结果 | 页脚为第二个独立消费者 |
| E6 | code_path | `src/web/src/pages/catalog/ChatWorkbenchPage.tsx:88`；`src/web/src/components/chat/ExecutionPanel.tsx:26` | hidden 保留详情挂载；轮次列表定时刷新，选中项读取事件、Diff、context | 隐藏详情为第三个事件消费者，收起不等于停止 |
| E7 | code_path | `src/web/src/components/chat/chatEvents.ts:5`，readChatEvents | 每次 fetch 独立发起，cache 为 no-store | 浏览器普通缓存不能合并这些事件读取 |
| E8 | code_path | `src/web/src/components/chat/RecoveryOperationPanel.tsx:59`、78—84 | 固定3秒轮询、readSequence 丢弃过期响应，无在途保护；有页面隐藏、completed、20次预算限制 | 存在条件性重叠风险，但不是无条件永久轮询 |
| E9 | code_path | 2026-10-21 bug-complete 聚焦复核 E4—E8 路径 | 三处事件读取、隐藏挂载及恢复轮询条件仍存在 | 同会话证据可用于本次机制分析；并非本次重新计时 |

E1—E3 为本会话实际工具观察的脱敏摘要，没有 HAR 或截图附件；不得把摘要说成已保存的原始文件。刷新前遗留在途 turns 的 unknown 请求不计入成功证据。源码可能含其他工作区改动，浏览器使用构建包，未宣称 HEAD 与部署版本严格一致。代码行号为本次定位点，后续以函数定位复核。

## 已排除假设

| 假设 | 判断与依据 |
|---|---|
| 状态重新读取就表示历史任务重新执行 | 不支持此推断。E1/E2 是读取行为，E4—E7 为读取代码；未观察到任务重执行。此结论不替代全量执行审计。 |
| 页面正文必须等完整事件回放才显示 | E1 已观察到正文先显示，状态仍在读取；正文与状态依赖不同。 |
| 收起执行详情即可消除详情请求 | E6 的 hidden 不卸载组件，E2 在收起时仍观察到重复读取。 |
| 所有时延均为服务器计算耗时 | E3 存在 1.28 s Stalled；Waiting 也不能等同纯服务器计算。 |
| 恢复面板永久无条件轮询 | E8 存在可见性、终态与预算限制，排除该过度描述。 |

## 已确认根因

读取生命周期按展示组件分散管理。TurnActivity、AssistantMeta、ExecutionPanel 各自读取同一轮次事件，没有共享请求或缓存结果；事件接口 no-store 又使普通浏览器缓存无法消除重复传输。TurnActivity 挂载即丢弃状态，并先等事件再读终态，造成已结束历史也呈现状态加载过程。详情容器只隐藏、不卸载，且轮询未以面板可见性和终态按需控制，增加不必要取数。

长历史进一步受事件页数影响：每个满页会再次读取状态，最终页不足200条且为终态才停止；这说明放大机制，不是实测的全局时延公式。ExecutionPanel 事件累计达到1000时暂停该链，轮次列表另行继续刷新。

## 修复方向

以轮次身份统一摘要和事件读取，合并并发消费者；终态摘要先展示，轨迹详情按需分页。面板隐藏时停用详情专属取数，保留必要的活跃任务与权限状态更新。恢复查询使用单请求在途或完成后调度，避免陈旧结果覆盖和连续丢弃造成长期加载。缓存按会话、轮次和权限边界隔离，不能用缓存绕过成果核验或写入保护。

后续设计判断是否需要新增服务端摘要；本次不预设 API/数据库改造，更不直接修改接口或代码。

## 验证闭环

现象→独立请求→代码消费者的机制闭环已建立，满足进入缺陷评审的证据门禁，不代表修复验收通过。验收计划见 [验收标准](acceptance.md)，当前未执行修复回归。

仍待修复阶段量化：冷暖/首次与重访对照、多轮长分页请求曲线、同环境客户端与服务端计时、慢响应重叠。受控慢响应应在明确测试环境完成，不重跑真实历史任务。缺少原始附件及部署映射的限制随证据一并保留，性能基准重新采样，不拿本次单样本作为收益承诺。

product_data_collection_observability: applicable；affected_layers: Web、API、request_logs、Task Trace。validation: 同会话浏览器证据与当前代码复核；本轮不改变采集字段、数据库、部署、对象存储或安全边界。
