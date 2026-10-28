---
title: Chat 最终回答去重与历史投影修复验收计划
created_at: '2026-10-26 18:50:07'
updated_at: '2026-10-26 19:17:59'
---

# Chat 最终回答去重与历史投影修复验收计划

## 验收状态
passed；来源[BUG验收](../../../issues/bugs/review/BUG-0065-chat-final-answer-duplicate-concatenation/acceptance.md)。

## 逐项验收
- [x] AC-001：正常完成后恢复同一最终答案，持久化和展示只保留一个逻辑答案。
- [x] AC-002：同来源重复事件幂等，偏移分片正确，多字节正文不丢失。
- [x] AC-003：不同最终版本按明确版本规则选择，不盲目拼接；合法多段及重复措辞保留。
- [x] AC-004：已有重复历史在刷新、分页、复制时一致展示，不重放业务动作。
- [x] AC-005：有界与chunks_v2路径、终态恢复、并发围栏和权限隔离回归通过。

## 证据与环境
每项分别登记测试命令、结果、输入版本与脱敏证据入口，归属evidence/acceptance/；真实观察与合成回归分列，不把当前缺陷复现通过当成修复通过。浏览器最新轮次、历史轮次、失败与切换样本分别记录，环境未就绪先诊断不伪造通过。

## 数据采集与链路观测
product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、DB、request_logs、task_traces、task_trace_spans
- reason: 结果持久化或自动核验读取行为变化，沿用可信request_id与现有请求封装。
- validation: 计划核对请求计数、脱敏状态/来源摘要、权限、直接API无伪造行为、观测失败降级；尚未执行修复验收。
自动GET不伪造用户点击，不把正文、令牌、本机路径写入日志；后台无HTTP不伪造request_id。沿用既有保留清理策略；未新增usage_events事件。对象存储、移动端/管理端、密钥和环境变量N/A。API字段变化同步OpenAPI/Orval；持久化变化同步DB文档及双库验证。

## 本次验收签认
2026-10-26 19:17:59：全部AC通过，见[逐项证据报告](evidence/acceptance/20261026191542555621-1a457098/summary.md)。合成回归、MySQL兼容和隔离真实浏览器分别记录；浏览器使用真实HTTP与后台控制器、合成业务证明，未重放原用户命令。历史原始事件身份缺口不扩张为全链路确认。
