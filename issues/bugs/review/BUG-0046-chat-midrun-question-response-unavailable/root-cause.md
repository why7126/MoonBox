---
bug_id: BUG-0046-chat-midrun-question-response-unavailable
title: Chat 执行中问答通道缺失根因分析
created_at: '2026-10-19 11:51:11'
updated_at: '2026-10-19 11:51:11'
owner: 产品团队
status: confirmed
---

# Chat 执行中问答通道缺失根因分析

## 根因状态

status: confirmed

确认范围为当前产品缺少完整的执行中提问、回答和原轮次续接通道。证据复用本会话2026-10-19只读探索与合成协议探针，不宣称原故障发生过已捕获的原生交互请求。

## 现象

助手在过程正文询问授权测试入口，选项无法操作；执行期间普通发送受互斥限制，用户没有向原问题提交回答的路径。原轮次后来正常结束，因此不能据此认定永久死锁。

## 证据链

| 编号 | 类型 | 来源 | 摘要与支持的判断 |
|---|---|---|---|
| E1 | screenshot | 用户提供的 BUG-0028 apply 执行中截图 | 问题和两项选择显示为部分输出正文，用户反馈无法回答；截图本身不证明协议请求已发出 |
| E2 | data_sample | 当前后端对原 apply 轮次及事件的只读查询 | 765条事件，类型为 execution.output/state/tool/usage；问题文本匹配，结构化提问和交互拒绝标识无匹配；status=completed、error_code为空，02:57:43 UTC结束，即10:57:43本地时间 |
| E3 | reproduction | 本轮 Chrome 当前活跃 Chat 页面观察，样本为 BUG-0044 sprint-propose | 显示执行中、原运行尚未终止、可先编写草稿，发送按钮禁用。该样本只验证共用输入行为，没有触发提问或发送业务消息 |
| E4 | code_path | src/web/src/components/chat/Composer.tsx disabled/send 分支；ConversationMessages.tsx 的 SafeMarkdown 展示 | active_turn_id 禁止普通发送；助手正文经 Markdown 展示，不自动变成带问题身份的回答控件 |
| E5 | code_path | src/backend/app/chat/admission.py enqueue；src/backend/app/chat/api.py 路由 | 普通新轮次要求 active_turn_id 为空；当前路由提供提交、中止、重试等，没有原问题回答端点 |
| E6 | code_path | src/backend/app/chat/app_server.py rpc，方法和请求ID同时存在的分支 | 返回 -32601、Interactive requests are not supported，并抛出 executor_interactive_request |
| E7 | test_failure | 无进程/无业务数据的 AppServer.rpc 合成内存探针 | 注入 item/tool/requestUserInput，实际得到 E6 的错误码与异常；可稳定验证适配器拒绝行为 |
| E8 | code_path | src/backend/tests/test_chat_app_server.py 的 test_uncertain_protocol_never_fabricates_terminal | 现有测试将 interactive 模式断言为 executor_interactive_request，说明拒绝是现有契约，而不是本轮偶发 UI 故障 |

## 已确认根因

1. 原样本问题以普通助手输出保存和展示，未形成产品可识别、可回答的结构化待答对象。Markdown 选项本身没有问题ID、回答状态或提交动作。
2. 普通消息通道面向新轮次，前端在 active_turn_id 存在时禁用发送，后端同样拒绝原轮次未结束时启动新轮次；该互斥合理，但没有独立的回答通道补位。
3. 适配器 rpc 等待期间收到带 id/method 的服务端交互请求会直接返回 -32601 并抛出 executor_interactive_request。无业务进程的合成内存探针稳定复现此行为。
4. 已检查的 API 与执行链路缺少问题持久化、答案回传及刷新/重连恢复契约；单独增加按钮或解除普通发送禁用不足以闭环。

## 已排除假设

| 假设 | 证据与结论 |
|---|---|
| 本例执行器永久死锁 | E2 有 completed 终态且无 error_code，不能认定死锁 |
| 浏览器完全无法输入 | E3可编辑草稿，阻断点为发送与原轮次回传 |
| 仅把 Markdown 选项做成按钮即可 | E5/E6 后端回答入口与协议处理仍缺失 |
| 当前归档只读导致原故障 | 原问题出现在归档前执行中，归档后只读是后续状态 |

## 证据边界与未确认事项

原轮次是否实际产生过未持久化的原生请求仍未知；事件查询没有匹配不能证明底层从未发出协议帧。RPC拒绝由合成探针验证，不能冒充原轮次的现场错误。AppServer.event直接返回事件，所有事件时序的交互行为尚未逐一动态复现；修复验收覆盖RPC等待和事件循环两个阶段。

这些边界不影响已确认的“普通正文提问无回答入口”因果链。BUG-0045负责环境能力，REQ-0046负责结果状态展示，BUG-0044负责阶段与对象互斥，分别交付。

## 修复方向

增加显式交互能力声明、结构化问题状态和专用回答API；授权并幂等地把答案交回原请求，维持普通命令互斥。等待中允许回答当前问题，不允许以答案替代新命令任意执行。覆盖轮次终止、问题过期、重复答案、撤权、刷新、断线与worker恢复；不能恢复时给出可信阻塞和安全续接方式，不静默新开写入轮次。

## 验证闭环

现有闭环：截图/用户反馈 → 原轮次输出与终态 → 当前活跃页面发送限制 → 前后端路径 → 合成协议拒绝。修复后还需真实产品同轮提问→回答→恢复及权限/幂等负向证据，详见 acceptance.md；当前未执行修复后验收。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: Web、API、问答状态持久化、执行器、请求日志、Task Trace。validation：用脱敏问题/轮次标识关联提问、回答确认和恢复；只保留状态、错误码、耗时与计数。当前文档无API/DB/部署/客户端/保留策略变更，以上变更N/A。
