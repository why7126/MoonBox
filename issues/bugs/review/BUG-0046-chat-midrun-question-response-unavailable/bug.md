---
bug_id: BUG-0046-chat-midrun-question-response-unavailable
title: Chat 命令执行中提出问题但缺少可回答和续接入口
severity: high
status: approved
owner: 产品团队
created_at: '2026-10-19 11:43:15'
updated_at: 2026-10-21 09:28:10
discovered_at: '2026-10-19 10:45:24'
environment: 本地 Docker Chat 平台，Web Chat 与 Codex app-server 适配链路
related_requirement: REQ-0025-chat-workbench
related_bug: BUG-0045-chat-acceptance-runtime-capability-gap
related_change: null
lifecycle_stage: plan
---

# Chat 命令执行中提出问题但缺少可回答和续接入口

## 现象

产品 Chat 执行 BUG-0028 的 opsx-apply 时，助手在过程正文中询问是否提供授权测试环境，并给出选项；用户反馈无法回答。问题作为普通输出展示，没有可提交到原问题的交互入口。执行期间普通消息发送又受同会话互斥限制，因此无法通过普通发送补足答案并续接原轮次。

原轮次最终于2026-10-19 10:57:43结束，报告 apply 仅完成4/10；没有已证实的永久等待或执行器死锁。后续桌面补验和 BUG-0028 归档不代表问答通道已修复。

## 复现步骤

1. 在产品 Chat 的授权对象会话执行需要用户补充信息的命令。历史来源是 /opsx-apply BUG-0028-requirement-center-card-owner-raw-user-id；该对象已归档，后续动态复现应另用隔离授权样本，不重放写入命令。
2. 观察执行中出现的普通正文问题和选项，检查是否有原问题专属回答控件。
3. 检查普通输入区：可先编写草稿，但原轮次活跃时发送按钮不可用；后端普通消息提交同样要求原轮次已结束。
4. 核对同轮事件是否保存结构化问题、答案和续接标识。原样本只查到普通输出中的提问，未查到 request_user_input/requestUserInput 或交互拒绝标识。
5. 独立合成探针向适配器 RPC 等待流程注入 item/tool/requestUserInput，验证其返回错误而非等待产品答案。该探针不等于原样本实际触发此分支。

## 期望与实际

| 环节 | 期望 | 实际 |
|---|---|---|
| 提问展示 | 问题有稳定身份、选项、补充说明及可操作入口 | 原样本以普通 Markdown 正文展示问题和选项 |
| 用户回答 | 允许回答当前待答问题，同时保持普通新命令互斥 | 活跃轮次期间普通发送被禁用，没有独立回答入口 |
| 协议交互 | 答案回到原请求/原轮次，恢复执行 | RPC 等待期间收到交互请求会返回不支持并抛出异常 |
| 状态恢复 | 刷新/重连仍可恢复待答问题，重复提交幂等 | 已检查链路未提供结构化问题持久化和回答接口 |
| 能力降级 | 不支持交互时明确限制和可执行续接路径 | 助手仍可在正文中提出用户无法在当前轮次完成的选择要求 |

## 影响范围与严重等级

high：阻断需要用户决策的命令闭环，并可能诱发用户重复发送命令或跨会话续接。影响面为共用 Chat 发送与执行适配链路，不限于测试环境问题；具体其他命令和部署版本仍需覆盖验证。没有已证实的答案丢失、业务数据损坏或执行器死锁。建议常规 fix，保留现有同会话执行互斥，不能通过直接解除发送禁用来修复。

## 证据链与根因状态

根因状态：confirmed，限于当前产品缺少执行中问答通道，以及已验证的交互请求拒绝分支。证据承接本会话2026-10-19 bug-explore，不冒称完整原生问答协议已在故障轮次重现。

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

## 已确认判断与边界

原故障有一条已证实的路径：助手普通正文提问 → 无结构化回答入口 → 活跃轮次禁止普通发送 → 用户无法把答案送入原轮次。另有独立验证路径：真正的服务端交互请求在 rpc 等待阶段也被显式拒绝。两者共同表明产品缺少完整问答接入，但不能声称原故障必然由 -32601 导致。

AppServer.event 会直接返回事件；本次没有对所有事件阶段的交互请求行为做动态验证，不把 rpc 分支结论推广为所有消息时序。事件未记录结构化请求也不证明底层从未发过任何未被持久化的协议帧。修复阶段须补齐这些时序测试。

已排除“永久死锁”为本例结论：原轮次有completed终态。当前 BUG-0028 归档后的完全只读是后续状态，不能用于解释原先执行中无法回答。未证明浏览器本身无法输入；观察反而支持可编辑草稿但不可发送。

## 修复方向与建议验收

1. 声明客户端交互能力，结构化保存问题ID、所属空间/会话/轮次、选项、补充说明、等待及终止状态。
2. 增加专用回答端点和原生交互卡片，校验本人授权、原请求仍有效、答案格式和幂等键；普通新命令互斥保持不变。
3. 将答案关联回原协议请求，覆盖请求在RPC等待和事件循环阶段到达、重复请求、超时、中止、断线和worker恢复，不能串轮次或重复推进副作用。
4. 不支持交互时向执行器明确能力，并向用户提供真实可执行的结束/续接路径；不承诺尚不存在的功能。
5. 分别记录协议回归、接口权限/幂等、UI卡片/刷新恢复以及真实产品同轮提问→回答→恢复证据。纯文字提问不能凭关键词自动执行用户答案。

## 关联边界

父需求为 REQ-0025-chat-workbench；BUG-0045负责验收环境能力，不负责问答桥接；REQ-0046负责执行结束与任务完成的状态展示；BUG-0044负责阶段迁移及对象并发门禁。本条来源是 BUG-0028 / fix-requirement-center-owner-display / sprint-010，不继承其 Sprint 或 Change。

当前仅生成主文档，未评审、未创建Change、未修复代码，也未提前生成 root-cause.md。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: Web 问答交互、Chat API、执行器协议、问题/答案状态持久化、请求日志和 Task Trace。

validation: 后续以脱敏问题ID/轮次关联验证请求、等待、答案确认与续接，记录状态、耗时、错误码和幂等结果；不要把自由文本答案、Prompt、凭证或真实用户标识复制到诊断日志。本轮仅文档，API/DB schema、客户端生成、部署、对象存储与保留策略变更 N/A，实施时按实际影响同步。
