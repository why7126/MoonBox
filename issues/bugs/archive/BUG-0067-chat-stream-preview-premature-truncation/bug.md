---
bug_id: BUG-0067-chat-stream-preview-premature-truncation
title: Chat 流式正文预览过早截断并误导提示输出不完整
status: done
severity: medium
owner: 产品团队
created_at: '2026-10-26 20:15:28'
updated_at: 2026-10-27 09:10:24
discovered_at: '2026-10-26 19:57:39'
environment: local
related_requirement:
related_bug: BUG-0030-chat-assistant-output-missing-from-conversation
related_change:
root_cause_status: confirmed
---

# Chat 流式正文预览过早截断并误导提示输出不完整

## 现象

Chat 命令执行中，助手正文只展示开头半句话，却出现“输出内容不完整”提示。用户无法分辨正常生成、展示截短和真实输出丢失，可能误判本轮执行失败。

本地 BUG-0056 对象会话的 2026-10-26 19:56:46 bug-opsx 轮次中，截图显示执行中、12 次工具调用及该提示。后续最终答复出现后提示消失；这不证明执行状态已经完成。

## 复现步骤

1. 使用启用分片内容存储的本地 Chat，运行能持续产生小粒度流式文字的命令；原始观察样本为 BUG-0056 对象会话的 bug-opsx 轮次。
2. 在尚未形成最终答案时观察同轮对话正文；累计至少 21 个小片段，且正文总量远低于字符上限。
3. 检查页面是否只显示开头正文并出现“输出内容不完整”。
4. 只读统计对应 output 流的片段数、总字节数，按 sequence 拼接前 21 个片段并与页面核对；不得重放业务命令获取历史证据。
5. 最终答案形成后观察正文与提示的变化，独立检查执行状态，避免将正文变化当作完成证明。

## 期望与实际

| 项目 | 期望 | 实际 |
|---|---|---|
| 短正文预览 | 片段很多但总正文很短时完整展示 | 固定读取前 21 个片段，半句话即可触发截断 |
| 状态提示 | 正常生成、预览上限、真实缺口语义清楚 | truncated 一律显示“输出内容不完整” |
| 数据与展示 | 展示范围不掩盖已保存的短正文 | 样本 output 共 294 片段、1126 字节，预览仅取前 21 片段 |
| 最终答案 | 正确切换最终答复且不重复拼接 | 样本 final 为 1 片段、631 字节，出现后提示消失 |

## 影响范围与严重等级

严重度 medium：影响 Chat 过程输出阅读、复制及执行可信度；未发现本样本存储内容丢失或业务命令执行失败。

直接涉及分片内容存储的正文读取、API 投影字段 output_truncated 和 Web 提示。运行中的 output 流已有真实证据；最终答案多片段、停止、失败及历史读取的边界尚需回归，不将这些场景描述为已复现。

最终答复出现后仍显示执行中的收尾状态问题不纳入本条，原因未确认。BUG-0056 仅为观察样本；BUG-0030 的正文为空、BUG-0065 的最终答案重复均有独立触发机制。

## 根因判断与证据

根因状态：confirmed，范围限定为本样本的预览截断和提示产生机制。

| 证据 | 来源 | 事实及支持的判断 |
|---|---|---|
| E1 | 本会话用户截图，输出记录时间 2026-10-26 19:57:39 | 执行中与不完整提示同时出现，正文在句中结束 |
| E2 | 同会话业务库只读聚合，chat_result_segments / chat_content_objects | output 为 294 片段、1126 字节；前 21 片段拼接与截图一致，定位预览边界 |
| E3 | src/backend/app/chat/assistant_output.py::saved_output | V2 查询 limit(21)，len(preview)==21 就设置 truncated，未判断是否还有后续片段 |
| E4 | src/backend/app/chat/execution.py 的 item/agentMessage/delta 分支及 save_result | 小粒度增量逐次保存，片段数量不等价于正文长度 |
| E5 | src/web/src/components/chat/turnStatus.ts::projectRunStatus | truncated 为真时无条件输出该提示，不区分截断原因和执行状态 |
| E6 | 同会话 Chrome 本地 /chat 只读观察及 final 聚合 | 最终正文出现后提示消失，final 为 1 片段、631 字节，与切换读取流的逻辑吻合 |

本次生成前复核 E3–E5 代码路径仍存在。运行态 E1、E2、E6 复用本会话已取得证据，不宣称本次重新执行产品命令或完成修复回归。

因果链：每次小粒度增量保存为片段 → 预览只取前 21 片段 → 按数量设置 truncated → Web 显示泛化缺失提示。样本体量远小于 MAX_CHARS=200000，排除该样本由字符预算耗尽触发的解释。代码还显示恰好 21 片段也会被标记截断，该边界已在实施红测中独立复现，修复后回归通过。

## 修复方向与验证建议

保持读取有界，按合理正文预算与分页读取组织预览，不能用固定的小片段计数代替正文大小；真实上限或缺口应有准确原因和查看完整内容入口。最终实现方案在评审与 Change 设计阶段确定。

后续覆盖：20/21/22/294 个小片段、真实正文上限、历史序号缺口、运行中与各终态、最终答案切换、刷新与复制。验证输出完整性、提示语义、查询成本和不重复拼接；只读预览不得触发业务重放。本阶段未运行这些回归测试。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Web 对话展示、API 正文投影、DB 内容片段读取、Agent Workflow 输出链路。
- N/A：本次只生成治理文档，无 API 契约、数据库结构、UI 实现、部署、安全或客户端生成物变更，无新增埋点。
- validation：复用用户截图、浏览器页面和只读聚合，复核正文投影及提示代码；后续记录片段数、字节数、读取范围和截断原因，不保存完整 Prompt、回复正文、凭证或本机路径。

## 附件与追溯

用户截图保留在原会话；脱敏记录见 capture.md，状态见 trace.md。根因见 root-cause.md，临时处理见 workaround.md，回归标准见 acceptance.md；未创建 OpenSpec Change。
