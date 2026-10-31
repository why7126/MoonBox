---
title: Chat 执行中问答与安全恢复设计
created_at: "2026-10-31 11:31:40"
updated_at: "2026-10-31 11:31:40"
---

# Chat 执行中问答与安全恢复设计

## 背景与现状

证据源：[根因E1–E8](../../../issues/bugs/review/BUG-0046-chat-midrun-question-response-unavailable/root-cause.md)。本次复核`app_server.py`仍有RPC交互拒绝分支。原始问题保存为正文，没有可提交对象；前端和后端普通新轮次互斥不是应解除的限制。事件接收阶段与实际协议版本须在实施首项验证，合成探针不能代表历史现场。

## 修复方案与取舍

### 结构化问题与能力

为支持的适配器声明问题交互能力，将模型工具请求转换为带稳定request/question/turn身份的事件。执行上下文说明需要用户决策时使用受支持的结构化工具；不解析任意Markdown为可执行请求，不把一般提问能力扩展为Shell审批。协议字段和版本由实施时本地适配器/schema证据确定并记录，未知方法明确拒绝。RPC等待及事件循环共用分发器，单一读者消费协议流，避免两个线程争抢响应。

### 数据与状态

新增问题持久化及答案投递记录，绑定空间、会话、轮次、执行实例、协议请求ID和问题ID；含选项schema、必要问题文本、版本、过期时间、答案幂等键及状态。唯一约束按执行实例和协议请求ID，防止ID跨进程复用。问题等待期间轮次仍活跃，等待不伪造执行成功。

状态区分pending、answer_received、delivered、cancelled、expired、unrecoverable；answer_received只表示服务端接收，delivered需适配器可验证的写入/确认依据，原轮次消费及结果另以事件验证。事务条件更新保护首个合法答案；重复同键同内容返回原结果，冲突答案拒绝。超时配置有默认值和上下界，在API契约中固化；取消/超时与提交竞争按提交时当前问题及轮次状态原子判定。

业务答案必要持久化按会话权限、保留及删除策略管理，不进入诊断日志；问题和答案继承会话删除策略，未知保留规则须在迁移前明确。SQLite/MySQL分别验证表、唯一约束与并发事务行为。

### 专用回答接口

在现有Chat API前缀下增加问题读取与答案提交接口，路由建议按conversation/turn/question分层；最终路径、输入限制与错误码在实施首项固化并生成OpenAPI。答案包含问题版本、稳定选项ID、补充文本和幂等键，服务端校验类型、长度、可选值及必答项，不接受任意协议method或执行指令。

每次读取、提交和投递重新校验用户对空间/会话/轮次的权限、撤权及归档只读状态；跨租户查询不泄漏问题存在性。普通消息enqueue互斥保持不变。客户端只显示收到、投递、结束等真实状态，不将HTTP成功解释为任务完成。

### Worker投递与恢复

答案通过持久记录由拥有原请求句柄的执行实例消费；限定单个owner/租约及版本条件，避免多worker重复写。进程内保留句柄映射，刷新仅重建界面；进程重启若无法证明原协议会话和句柄可恢复，标记unrecoverable，保留已做工作并说明核对原轮次后安全续接，不新开写轮次。

写入协议后、持久确认前崩溃属于不确定投递：没有协议级确认或可靠去重依据就禁止自动重发，不承诺跨进程严格一次。暂停交互不应占用DB事务，等待仍处理取消和心跳，现有运行超时与问题超时协调且有限。

### 页面交互合同

问题卡片归属原轮次，普通Composer仍可写草稿但不能新建并发轮次。包含问题、推荐选项、补充说明、提交和状态；原生协议没有推荐字段时不虚构推荐。提交中禁用重复点击，失败保留答案和可重试依据，已答/过期/取消只读；刷新从受权状态快照恢复并与实时事件去重。

| 动作 | 容器与selector约定 | 状态 | 验收 |
|---|---|---|---|
| 选择/补充 | 内联卡片；question-option、question-text | 待答、错误 | 键盘、焦点、文本长度 |
| 提交答案 | 内联按钮；question-submit | 待答、提交中、已接收、已投递 | 重复提交与真实回传 |
| 查看终止原因 | 内联状态；question-status | 过期、取消、不可恢复 | 不出现假操作按钮 |
| 停止原轮次 | 复用现有停止交互与确认容器 | 活跃、停止中、已终止 | 原轮次身份及竞争测试 |

上述selector为实施合同，不声称已有DOM。实现前补齐UI Contract和Skeleton，确认现有设计token与停止modal selector，不新增无必要弹窗。1440px/390px × 待答/提交中/错误/已回答/过期逐格采图；补充取消/恢复状态证据和关键computed style。原截图是故障证据，不是逐像素复刻目标。Mock只用于组件测试，最终真实产品证据必须标出API与执行器版本。

## 数据采集与链路观测

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、问答持久化、执行器、usage_events、request_logs、task_traces、task_trace_spans
- reason: 新增回答动作和原轮次异步回传，需可追溯且不得暴露答案。
- validation: 页面提交复用行为关联ID；直接API无行为ID仍可调用；后端可信request_id关联question/turn；记录等待/确认/拒绝/恢复耗时和错误码，日志不存自由文本、完整Prompt或凭证。核对保留与级联删除、OpenAPI/Orval及链路字段边界。观测写入失败不得阻断回答主链路。
- N/A: 对象存储不新增附件；管理端、小程序、移动和桌面端不新增界面。部署仅声明协议能力与配置兼容，不自动操作生产。

标准：[产品数据采集与链路观测](../../../docs/standards/product-data-collection-observability.md)。

## 测试策略与风险

AC-001/002覆盖卡片、专用回答与普通发送互斥；003双阶段协议；004非法答案/并发/幂等；005刷新重连；006取消超时；007进程故障；008授权；009不支持降级；010视口状态矩阵；011真实同轮消费；012观测脱敏。证据统一放`evidence/acceptance/`，逐AC记录命令、合成、视觉、真实轮次类型。所有12项未执行。

旧客户端和不支持适配器必须前置能力降级，不无限等待；历史事件仍可读。部署先兼容迁移及后端，再worker和Web，最后启用已核验能力。回滚按proposal保留数据并收口待答，未知投递不可重试。实现期间复核当前API、DB与UI路径，不依据历史行号机械改代码。


## 实施合同与已确认布局

2026-10-31用户已确认1440px Skeleton，证据`evidence/acceptance/browser/skeleton-1440.png`。最终卡片复用requirement-center主题和Chat token；内联表单不新增modal，停止仍复用既有轮次停止入口。

固定协议为镜像内codex-cli 0.153.4生成的ToolRequestUserInputParams/Response：支持`item/tool/requestUserInput`，答案为`answers[question_id].answers[]`；原生选项只有label/description，因此产品用请求内序号作稳定选项ID，不虚构推荐。确认该版本有`features.default_mode_request_user_input`，默认关闭，现显式启用；新线程同时注册moonbox_question动态工具，旧线程使用原生提问。仅支持非秘密问题；秘密输入请求明确拒绝。

新增`chat_questions`，复合唯一键turn_id/generation/request_key（协议ID的SHA256）。`chat_turns.question_capable`默认0，Web新请求显式声明true；旧客户端保持不支持交互的明确结束指引，不凭客户端声明授予权限。等待900秒，部署可配置30–3600秒；运行总超时仍有效。单一协议读者保存有界交错通知，保留RPC确认；原请求已解决或轮次已结束时关闭问题。答案接收、投递中、已写入原协议通道分别记录；delivered不表示任务完成。

接口：GET `/api/v1/chat/turns/{tid}/questions`；POST `/api/v1/chat/turns/{tid}/questions/{qid}/answers`。请求version、idempotency_key及每问题option_id/text；最多3题、8选项、4000字补充。2520表示答案不合法（422），2521表示状态/版本/答案冲突（409）；既有2501/2502表示授权/不可见。API返回问题及状态，不回传已持久化答案原文。

SQLite/MySQL均通过统一增量迁移；主业务答案随会话历史删除，不另设永久留存副本。独立备份继承现有Chat备份删除契约；旧版本回滚保留新增表及默认能力列，先终止/核对待答请求，不直接删表。请求审计只记录身份、状态和可信request_id；question阶段span使用同轮task_trace_id，页面行为事件chat.question_answer与直接API区分。
