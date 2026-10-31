---
bug_id: BUG-0046-chat-midrun-question-response-unavailable
title: Chat 执行中问答与续接缺陷修复评审
created_at: '2026-10-21 09:28:08'
updated_at: '2026-10-21 09:28:08'
owner: 产品团队
review_result: approved
severity: high
reviewed_at: '2026-10-21 09:28:08'
review_basis: 用户明确 --approve；根因证据与验收门禁复核
---

# Chat 执行中问答与续接缺陷修复评审

## 评审结论

同意修复，严重度 high，文档 Readiness 为 Ready。采用常规 fix，无已证实的数据损坏或永久死锁，不走 hotfix。此结论只批准进入 Sprint 规划，不表示已开发、已验收或自动创建 Change。

## 评审清单

- [x] 可复现或根因充分：root-cause.md E1–E8 覆盖历史轮次、运行态输入限制、协议代码及合成探针；根因证据校验通过。
- [x] 严重等级合理：需要用户决策的核心命令不能在原轮次闭环，维持 high；不扩大为所有轮次死锁。
- [x] 回归验收明确：12项 AC 覆盖结构化提问、专用回答、双阶段协议、幂等、刷新恢复、终止竞争、worker恢复、权限隔离、降级、视觉、真实产品轮次及观测。
- [x] 修复路径明确：常规 fix；保持普通新命令互斥和安全边界，不以解除发送限制代替回答通道。

## 证据复核与适用边界

2026-10-21复核当前 app_server.py 的 rpc 交互拒绝分支及 Composer.tsx 的 active_turn_id 发送限制仍存在。历史运行态事实明确归属2026-10-19，未将历史截图冒称为今天重新运行的结果。

原轮次有普通正文提问且正常结束；其是否触发底层原生交互请求仍未知。-32601拒绝由独立合成探针验证，不作为原轮次现场异常。该边界不影响问答通道缺失的确认；修复后需要真实同轮提问、回答、恢复的独立证据。

## 批准范围与实施约束

批准结构化问题状态、专用回答API、前端问题卡片、协议回传、授权幂等及异常恢复。Sprint与Change阶段明确协议版本、问题过期、取消/回答竞争、worker恢复和无法恢复时的降级行为；不得静默新开写入轮次。

BUG-0045负责环境能力，REQ-0046负责整体输出状态，BUG-0044负责阶段与对象并发门禁，保持关联但不重复交付。现有12项验收均未执行修复后验证；视觉与真实产品证据不能由合成探针代替。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: Web、Chat API、问题状态持久化、执行器、请求日志、Task Trace。validation：按AC-002/004/006/007/008/011/012核对同轮身份、授权、幂等和恢复。日志不保存自由文本答案、完整Prompt或凭证；必要业务答案按授权与保留策略处理。本次仅评审，API/DB/UI/部署/安全策略/客户端生成物未变更，以上实施变更在本轮N/A。

## 后续门禁

先执行 /sprint-propose --bug BUG-0046-chat-midrun-question-response-unavailable；成功纳入并同步为 in_sprint 后才进入 bug-opsx。未纳入Sprint、未创建Change，不执行业务开发。
