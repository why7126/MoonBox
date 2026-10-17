---
bug_id: BUG-0030-chat-assistant-output-missing-from-conversation
title: Chat 助手正文缺失回归验收记录
acceptance_status: passed
owner: 产品团队
created_at: 2026-10-07 13:40:37
updated_at: 2026-10-17 17:01:21
---

# Chat 助手正文缺失回归验收记录

## 验收前置条件

当前故障机制由隔离合成轮次确认，修复后回归和真实浏览器合成 API 验证已执行。原故障轮次 T1/T2 数据已删除，无法再做同一实例对照；本矩阵只确认当前机制的修复效果。

## 回归验收矩阵

| 编号 | 场景与操作 | 预期与证据 | 当前结果 |
|---|---|---|---|
| AC-001 | 有助手输出后停止轮次，查看对话并刷新重进 | 已保存文字可读，部分内容标识准确，状态保持已停止；记录消息数量/长度与页面观察 | 通过：隔离后端停止轮次回归及 Firefox/Chromium 合成 API 页面刷新；原 T1 不可复验 |
| AC-002 | 有输出但终态未知，查看对话和轨迹 | 部分文字可读，未知提示保留；不误报完成、不自动重发命令 | 通过：unknown 部分正文和未知警告在双浏览器、双视口可见；无自动重发 |
| AC-003 | 从 unknown 恢复为已停止、失败或完成 | 文字与同轮次正确关联，终态依权威证据确认；记录恢复 source_id、消息数量/长度 | 通过：隔离后端覆盖恢复为 stopped/failed/completed，权威终态及消息数量断言通过 |
| AC-004 | 重复恢复、重复事件、页面刷新 | 不重复助手正文，不跨轮次拼接；记录恢复次数与消息数量对照 | 通过：重复恢复、事件去重和刷新重进回归；页面正文只出现一次 |
| AC-005 | 正常完成且有最终答案的轮次 | 正常正文及状态无回退，过程文字和最终结果语义不混淆 | 通过：最终答案优先和过程增量区分，后端及前端状态回归通过 |
| AC-006 | 无助手输出的失败或停止轮次 | 不伪造正文或成功提示；保留真实错误与状态 | 通过：无输出轮次不伪造正文，保留失败/停止状态 |
| AC-007 | 旧轮次位于不同消息分页，重新进入历史会话 | 正确显示目标轮次文字，不因分页遗漏认定无消息；记录 page/page_size 和目标轮次别名 | 通过：隔离 API 分页、轮次稳定锚点及事件裁剪回归；原历史页数据已删除 |
| AC-008 | 核对历史证据可用性与替代证据 | 历史 Chat 数据已删除，明确记录原实例不可验证；用隔离环境合成轮次关联消息、事件、状态、API 与页面，不将其表述为 T1/T2 的历史根因 | 通过：历史 T1/T2 不可验证已明确；合成轮次后端/API/真浏览器及现存会话只读观察分别记录 |
| AC-009 | 检查观测摘要及权限边界 | 仅授权会话可读；摘要只含脱敏标识、状态、计数及长度，不含原始正文或凭证 | 通过：跨会话授权拒绝与脱敏字段回归；私有截图只存合成内容 |

## 产品数据采集与链路观测

product_data_collection_observability：applicable。affected_layers：chat_messages、execution_events、task_traces、消息 API、Web 对话展示。validation：已完成隔离合成轮次的事件、消息、状态、恢复事件与消息 API 关联；修复后回归、真实浏览器刷新及权限验证均通过。

最终实现新增兼容的消息响应可选字段，OpenAPI 与 Orval 客户端已同步。数据库迁移、部署服务及对象存储操作为 N/A：复用既有表和存储边界。

## 验收证据与通过条件

自动化回归使用合成输出，单独记录测试命令、场景和结果；真实页面观察记录环境版本、浏览器、时间、轮次别名、状态、消息数量和长度。只保存脱敏摘要，不保存原始 Prompt、回复或工具结果。所有可执行用例通过、替代证据链可复核、历史限制明确、状态与文档一致后再给出验收结论。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 17:01:21
accepted_by: workflow-sync
source_change: fix-chat-assistant-output-missing-from-conversation
source_sprint: sprint-009
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本轮修复回归进展

后端正文套件14项通过，覆盖断连、恢复三类终态、最终答案有无增量、写入失败、并发恢复、只读分页、事件窗口、权限与无输出。四种终态的合成 DOM 检查通过。Firefox 与 Chromium 各 16 个合成 API 真浏览器场景通过，覆盖刷新重进、视图切换、1440px/390px、部分正文与未知提示；现存已登录历史会话另经只读刷新和切换观察。历史 T1/T2 不可复验。详见 `openspec/archive/2026-10-09-fix-chat-assistant-output-missing-from-conversation/verification.md`。
