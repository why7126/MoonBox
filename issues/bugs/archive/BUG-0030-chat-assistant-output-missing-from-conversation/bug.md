---
bug_id: BUG-0030-chat-assistant-output-missing-from-conversation
title: Chat 工作台已有助手输出事件但对话正文为空
status: done
owner: 产品团队
created_at: 2026-10-07 13:35:17
updated_at: 2026-10-09 10:34:57
discovered_at: 2026-10-05 22:50:29
environment: local docker chat-platform
related_requirement: REQ-0025-chat-workbench
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
related_change: null
root_cause_status: confirmed
product_data_collection_observability:
  status: applicable
  affected_layers: [chat_messages, execution_events, task_traces]
  reason: 同一 Chat 轮次的消息、输出事件与执行终态需要关联核查。
  validation: 已用隔离 SQLite 合成轮次验证输出事件已保存而助手消息缺失、unknown 恢复仍缺失及正常终结对照；历史原轮次数据已删除，实际触发路径不可验证。
severity: high
---

# Chat 工作台已有助手输出事件但对话正文为空

## 现象

据 2026-10-05 的用户截图反馈和产品只读取证，BUG-0027 关联的 Chat 对象会话中，两轮归档命令已有助手文字轨迹，但对话区没有对应助手正文，用户只能查看工具调用和轮次状态。本轮复用 capture 中的历史观察，未重新访问原会话，不将其表述为当前运行态复现。

## 复现步骤

1. 在 local docker chat-platform 打开 BUG-0027 关联的 Chat 对象会话。
2. 定位 2026-10-05 15:47:48 发起的归档轮次：对话显示“已停止”，无助手正文；打开轨迹，历史观察读取到 221 条事件，其中包含多段助手文字。
3. 定位同日 21:16:05 发起的归档轮次：对话显示“状态未知”，无助手正文；轨迹历史观察读取到 16 条事件，其中包含助手文字增量。
4. 对照同一轮次的对话与轨迹；只读查看已有轮次，不重新发送归档命令。上述数量是已读取的全部类型事件数量，不是助手输出事件数。

## 期望与实际

| 项目 | 期望 | 实际历史观察 |
|---|---|---|
| 助手正文 | 已保存的助手文字可在对应轮次对话中阅读 | 轨迹有文字，对话无对应正文 |
| 非正常结束 | 已停止或终态未确认时明确标识部分内容与状态 | 两轮均无可读正文；未知轮次仍提示不要重复发送命令 |
| 完成语义 | 显示已有文字不等于宣告命令完成 | 尚无证据证明治理操作成功或失败，不推断业务完成 |

## 影响范围与严重等级

严重等级为 high：核心对话阅读能力受损，用户难以了解本轮输出及执行结果。已观察范围限于同一会话的已停止、状态未知两轮；其他会话、状态、环境及当前版本的发生频率未验证。未证明输出事件丢失、数据库损坏或归档失败，因此不扩大影响结论。

关联 BUG-0026 聚焦工作区权限与执行准备失败，本条聚焦已有输出但正文不可见，不能仅凭同属未知状态认定根因一致。

## 证据与根因

| 编号 | 来源 | 摘要与判断边界 |
|---|---|---|
| E1 | 本 BUG capture.md、trace.md 和用户授权引用快照 | 历史两轮轨迹与对话不一致；本轮文件核对与快照一致，未取得原始截图或轮次数据库样本 |
| E2 | src/backend/app/chat/execution.py，run_claim，约 239–247 行 | 增量文字累积到内存 reply，并独立记录 execution.output 事件 |
| E3 | 同文件 run_claim，约 289–318 行 | 正常收尾在快照、差异及容量检查后才写 assistant 消息；执行启动后的异常可转入 unknown，因此已有事件并不保证已写消息 |
| E4 | 同文件 reconcile_unknown，约 323–374 行 | 恢复路径同步终态并补工具事件，未见补写 assistant 消息；可解释一种消息持续缺失路径，但尚未证明原两轮走过此路径 |

当前故障机制状态为 confirmed：隔离合成测试证明输出事件已保存，而执行器断连后助手消息收尾写入未执行；unknown 恢复到 stopped 仍未补写正文。正常停止对照能写入并通过 API 返回消息。原历史两轮是否走过该路径不可验证；详见 root-cause.md。

## 本轮自主补证及限制

已聚焦读取当前 BUG capture、trace、执行和恢复代码，检查相关测试与日志文件入口；未定位到可直接关联原两轮的脱敏运行态证据。本轮没有浏览器工具，命令路径检查也未发现 Firefox；不能直接重新查看原会话。没有读取凭证、原始会话正文或运行时数据库，也未重放归档操作。代码证据支持候选断点，不能替代原轮次因果链，根因不标记 confirmed。

## 剩余补证步骤

1. 在原会话打开浏览器开发者工具 Network，再只读打开上述两轮对话和轨迹。分别用 T1、T2 作为稳定脱敏轮次标识，记录查询时间、部署版本、轮次状态、错误码、请求 method/path/status、request_id、assistant 消息数量和正文字符数、execution.output 数量及文字字符数。用于区分落库缺失和展示缺失。
2. 由已有读取权限的维护者按同一轮次及发生时间核对消息记录与执行事件，仅返回消息存在性、长度、终态事件 source_id、是否含 reconcile:terminal、是否发生 unknown、消息事务提交或回滚结果及异常类别。用于验证恢复路径与消息写入之间的因果关系。
3. 每轮返回一行脱敏字段表，无法取得的字段写“未取得”；不返回完整 Prompt、回复、工具输出、凭证、数据库连接串或原始日志。不要为补证重复执行归档命令。

## 后续验证边界

2026-10-08 补证结论：隔离合成轮次证实当前代码在输出后断连时，事件为 1、assistant 消息为 0，unknown 恢复为 stopped 后仍为 0；正常停止对照为事件 1、assistant 消息 1，消息 API 与落库结果一致。当前故障机制确认为 `confirmed`；历史 T1/T2 的具体断点仍不可验证。证据与命令见 root-cause.md 的 E10–E12。以下段落保留此前草稿阶段记录，不代表本次最终状态。

补证后再由 bug-complete 完善根因、临时方案和验收材料。后续验证覆盖有输出的停止、未知及恢复轮次，确认正文可读、部分输出标识清楚、不重复消息、不误报完成；正常完成轮次作为对照。本轮补齐缺陷治理草稿，不修改 API、数据库、UI、部署、安全或客户端生成物，未开展产品回归测试。

## 缺陷完善草稿进展

已保存 root-cause.md、workaround.md、acceptance.md；主状态现为 in_sprint。src/backend/app/chat/api.py 的 conversation_messages（约 338–350 行）按会话分页读取 messages，不从 execution.output 直接拼接正文。隔离合成轮次已验证当前 API 与数据库一致，原历史轮次的数据链仍不可取得。

2026-10-08 续补证：已用 Firefox 访问本地产品；历史状态为“全部”时搜索 BUG-0027，无匹配会话。当前本地库有 5 条 Chat 轮次，均始于 10 月 8 日；现存 3 份 Chat SQLite 快照和当前执行器历史索引均无 10 月 5 日目标时间窗口的轮次。以上只读检查未读取正文或凭证，不能反推历史根因。随后用隔离合成轮次确认了当前机制，详细证据见 root-cause.md。已运行 bug.complete 同步，现有 Sprint 状态保持不变。

## 本轮实现状态

当前修复 Change 为 `fix-chat-assistant-output-missing-from-conversation`，已进入研发中。后端68项通过、2项跳过，合成DOM与TypeScript检查通过；真实浏览器验收未完成，未声明修复交付。关联验证见 Change verification.md。
