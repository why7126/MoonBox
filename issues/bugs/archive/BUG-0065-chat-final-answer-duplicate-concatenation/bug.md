---
bug_id: BUG-0065-chat-final-answer-duplicate-concatenation
title: Chat 最终回答相同内容重复保存并拼接展示
status: done
severity: medium
created_at: '2026-10-26 18:11:49'
updated_at: 2026-10-26 19:54:50
environment: local docker chat-platform
owner: 产品团队
source: 用户双条 bug-capture 授权及同会话只读探索
related_requirement: null
related_bug: BUG-0030-chat-assistant-output-missing-from-conversation
lifecycle_stage: plan
root_cause_status: confirmed
discovered_at: '2026-10-26'
related_change: null
---

# Chat 最终回答相同内容重复保存并拼接展示

## 现象与影响

Chat 单轮最终回答完整重复两次，影响阅读、复制及结果可信度。初判 medium：未发现业务命令重复执行或数据丢失，不以正文重复推断治理动作重复。

## 复现步骤

1. 在本地 Docker 产品 Chat 打开 BUG-0056-requirement-center-context-load-latency 对象会话。
2. 查看 2026-10-26 17:43:37 发起的 sprint-propose 轮次及 17:46:01 输出记录。
3. 对比正文两半，并只读统计该轮 assistant 消息和 final 流片段的长度、摘要及来源标识。

## 期望与实际

期望：一次最终回答展示一次；流式输出、完成事件与恢复重放不重复拼接同一最终答案，合法多片段与版本替换保持正确。
实际：assistant 消息 708 字，前后各 354 字且完全相同；final 流保存两个来源标识不同的片段，每片 676 字节、内容 SHA-256 相同，顺序号为 395、396。

## 证据与根因边界

复用本会话 2026-10-26 用户截图、Chrome 本地 /chat 页面、业务库只读统计及源码分析；不保存原始聊天、个人标识、凭证或数据库副本。

- E1：用户截图和浏览器正文均展示完整内容重复。
- E2：chat_messages 与 chat_result_segments/chat_content_objects 的脱敏统计如上；是存储正文重复，不仅是前端重复渲染。
- E3：src/backend/app/chat/execution.py 的 final_answer 分支按 item 标识保存最终片段；content_store.py::result 按来源标识与偏移去重。
- E4：assistant_output.py::saved_output 按顺序拼接所有 final 片段，未区分重复答案与不同最终版本。

重复片段经拼接形成重复正文的直接机制已确认；上游为何出现两个不同来源标识的相同答案仍待补证，完整根因状态保留 probable。后续捕获脱敏 item 生命周期、phase、来源关系与摘要，不能只按文本相同删除合法内容。

## 判重与关联

BUG-0030 已归档，处理输出事件存在但正文缺失；BUG-0058 处理历史状态读取放大。与本次最终片段语义及正文重复仅弱相关，独立记录。BUG-0056 仅为观察样本，不表示其性能问题造成本缺陷。

## 建议验收

覆盖不同来源标识的相同 final、相同来源重放、真实多片段、不同最终版本、流式加完成通知、恢复重放、刷新历史与复制正文；业务动作不得重放，合法重复措辞不得误删。

## 数据采集与链路观测

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、DB、Agent Workflow
- reason: 涉及输出持久化或核验读取链路；本次仅记录，不修改接口、表结构、日志或埋点；对象存储与部署变更暂无依据。
- validation: 同会话页面、只读统计及代码路径证据；未执行修复回归。

## 附件边界

截图沿用用户会话附件，仅记录脱敏结论；未复制附件或原始日志到仓库。

## 本次生成补证

2026-10-26 再次自主查看 Chrome 本地 /chat 原对象会话，重复正文仍存在，成果已核验。未重新发送业务命令。

| 证据 | 来源 | 脱敏结果 | 判断 |
|---|---|---|---|
| E5 | chat_result_segments 只读查询 | 两份 final 分别在 17:50:06、17:50:59 写入，偏移均为 0 | 不是同一文本被 DOM 渲染两次 |
| E6 | chat_events 聚焦查询 | reconcile:terminal 于 17:50:59 写入 | 第二片段与恢复完成同一时间 |
| E7 | execution.py 正常完成与 reconcile_unknown | 正常使用 final: 加 item ID；恢复使用 recovered-final: 加 item ID | 同一 item 经两条路径保存时来源键不相同，不能命中来源去重 |
| E8 | 运行 API 容器与本地源码摘要对照 | execution.py、assistant_output.py、content_store.py 三文件 SHA-256 一致 | 本地分析路径与部署 API 版本一致；未据此宣称所有服务代码都相同 |

根因状态：probable。已确认的机制是最终片段全量拼接与跨正常/恢复路径来源键不一致；本轮时间关联强烈支持恢复重复写入。未取得最初原始 item ID 与恢复 item ID 的可比证据，不把时间相关性单独当成同一 item 的直接证明。原始执行为何进入恢复不是本 BUG 必须重跑业务才能判断的前提，也不推断为模型主动重复生成。

## 修复范围建议

统一正常与恢复路径的逻辑答案身份，定义最终版本选择和重放幂等规则；读取投影不得盲目拼接多个完整最终答案。兼容历史重复数据的显示，但不直接批量删除业务记录。不得简单删除所有文本重复段落。

## 后续最小补证

已尝试浏览器、只读片段与恢复事件时间、部署代码摘要核对；现有存储仅保留来源哈希，无法从哈希反解 item ID。后续 bug-complete 优先运行隔离合成回归：相同 item 先经正常完成再经恢复，核对 final 片段数、消息摘要、长度及合法多片段行为。真实问题再次发生时维护者可提供正常/恢复事件的脱敏 item 映射、phase、时间、内容摘要；不要提供正文、认证头或原始会话文件。返回表格列为路径类型、匿名 item 标识、时间、phase、摘要、片段数。当前不要求重新执行原治理命令。

## 补齐结论

本次隔离复现已确认机制缺陷，前文 probable 为生成阶段历史判断，以 [根因分析](root-cause.md) 为当前结论；历史样本未证实部分仍保留，不扩张为全链路已确认。
