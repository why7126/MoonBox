---
title: Chat 流式正文预览过早截断并误导提示输出不完整
bug_id: BUG-0067-chat-stream-preview-premature-truncation
status: done
severity: medium
created_at: '2026-10-26 20:08:41'
updated_at: 2026-10-27 09:10:24
owner: 产品团队
source: 用户 bug-capture 授权及同会话只读探索
lifecycle_stage: plan
related_requirement: null
related_bug: BUG-0030-chat-assistant-output-missing-from-conversation
environment: local
---

# Chat 流式正文预览过早截断并误导提示输出不完整

## 现象与影响

Chat 执行中，正文仅显示开头半句话，同时提示“输出内容不完整”，易使用户误认为执行失败或内容丢失。初判 medium：影响过程阅读与状态理解，当前样本未证明执行失败或存储内容丢失。

## 复现步骤

1. 在本地 Chat 打开 BUG-0056-requirement-center-context-load-latency 对象会话。
2. 查看 2026-10-26 19:56:46 发起的 bug-opsx 轮次，在持续收到小粒度流式文字时观察对话正文。
3. 截图中执行中、12 次工具调用与“输出内容不完整”同时出现，正文在一句话中途结束。
4. 对该轮 output 流只读统计片段数与字节数，并按 sequence 拼接前 21 个片段，与截图可见正文核对。

## 期望与实际

- 期望：短正文不因流式片段多而被提前截断；持续生成与真实展示上限、历史缺口明确区分。
- 实际：output 共 294 个片段、1126 字节，前 21 个片段恰好对应截图半句话；后续 final 为 1 个片段、631 字节。最终正文出现后该提示消失。

## 已有证据与边界

复用本会话 2026-10-26 用户截图、Chrome 本地 /chat 页面与业务库只读统计，不持久化聊天原文、会话标识、数据库副本或本机路径。

- E1：用户截图证明“执行中”与缺失提示同时出现，正文仅有开头片段。
- E2：chat_result_segments 与 chat_content_objects 的聚合统计为上述数量；前 21 片段拼接与截图一致。
- E3：src/backend/app/chat/assistant_output.py::saved_output 在 V2 分支 limit(21)，读到第 21 个片段即设置 truncated，不以小片段总正文长度判定。
- E4：src/backend/app/chat/execution.py 对 item/agentMessage/delta 逐次调用 save_result，因此短正文可以生成大量存储片段。
- E5：src/web/src/components/chat/turnStatus.ts 在 truncated 为真时直接显示“输出内容不完整”，不区分预览上限与真实缺口。

本样本的预览截断机制已确认；其他状态、边界与修复方案仍需后续验证。最终答复出现后仍显示执行中的收尾状态问题不在本条范围，原因未确认。

## 判重与范围

已检查缺陷看板及注册表。BUG-0030 已归档，处理输出事件存在但正文为空；BUG-0065 已归档，处理最终答案重复拼接。两者与本次仅模块相关，触发条件及修复闭环独立，关联 BUG-0030 作为输出展示历史背景。BUG-0056 仅为观察样本，不代表其性能问题导致本缺陷。

正文截断及误导提示属同一因果链，保留单条记录。

## 建议验收

- 覆盖 20、21、22 及更多小片段组成的短正文，内容应完整且无误导提示。
- 覆盖真实字符上限、历史缺口、执行中、完成、停止、失败、刷新与复制；提示应准确区分原因。
- 读取有界，避免为补全预览无界加载；最终答案不得重复拼接，过程读取不得触发业务命令重放。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Web 对话展示、API 正文投影、DB 内容片段读取、Agent Workflow 输出链路。
- N/A：当前仅记录缺陷，不修改 API 契约、数据库结构、部署、安全或客户端生成物；无新增行为埋点和日志采集。
- validation：已有截图、同会话页面与只读聚合统计、源码路径交叉核对；后续回归记录片段数、字节数与截断原因，不记录原始 Prompt 或回复。

## 附件

用户截图保留于原会话；本记录仅保存脱敏证据摘要，未复制原图或运行日志。
