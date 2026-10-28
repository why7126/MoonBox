---
bug_id: BUG-0065-chat-final-answer-duplicate-concatenation
title: 最终回答重复拼接验收标准
created_at: '2026-10-26 18:19:35'
updated_at: 2026-10-26 19:54:50
acceptance_status: passed
---

# 最终回答重复拼接验收标准

## 回归验收

- [x] AC-001：正常完成后恢复同一最终答案，持久化和展示只保留一个逻辑答案。
- [x] AC-002：同来源重复事件幂等，偏移分片正确，多字节正文不丢失。
- [x] AC-003：不同最终版本按明确版本规则选择，不盲目拼接；合法多段及重复措辞保留。
- [x] AC-004：已有重复历史在刷新、分页、复制时一致展示，不重放业务动作。
- [x] AC-005：有界与chunks_v2路径、终态恢复、并发围栏和权限隔离回归通过。

## 证据要求

分别记录合成回归与真实产品观察；现有缺陷复现通过不勾选修复验收。输出脱敏事件标识、状态、计数和摘要，不保存凭证或原始聊天。

## 数据采集与链路观测

product_data_collection_observability: applicable
affected_layers: [Web, API, DB, Agent Workflow]
validation: 修复后核对请求次数、输出摘要或核验时间线；本次仅合成缺陷复现，未改变采集契约。
N/A：本次无对象存储、部署、API schema 或DB迁移变更；实施时若扩展范围需重新评估。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-26 19:54:50
accepted_by: workflow-sync
source_change: fix-chat-final-answer-duplicate-concatenation
source_sprint: sprint-014
evidence: [openspec/archive/2026-10-26-fix-chat-final-answer-duplicate-concatenation/evidence/acceptance/20261026191542555621-1a457098/summary.md]
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本次验收签认
2026-10-26 19:17:59：全部AC通过，见[逐项证据报告](../../../../openspec/changes/fix-chat-final-answer-duplicate-concatenation/evidence/acceptance/20261026191542555621-1a457098/summary.md)。合成回归、MySQL兼容和隔离真实浏览器分别记录；浏览器使用真实HTTP与后台控制器、合成业务证明，未重放原用户命令。历史原始事件身份缺口不扩张为全链路确认。
