---
bug_id: BUG-0066-chat-auto-verification-status-stale
title: 自动核验状态未刷新验收标准
created_at: '2026-10-26 18:19:35'
updated_at: 2026-10-26 19:55:10
acceptance_status: passed
---

# 自动核验状态未刷新验收标准

## 回归验收

- [x] AC-001：首次待核验、随后自动成功时，不点击不刷新页面也更新为已核验。
- [x] AC-002：自动处理中与失败需处理区分，失败显示原因及合法重试入口。
- [x] AC-003：有界刷新、并发去重、退避与终态停止，不放大历史轮次请求。
- [x] AC-004：组件卸载或切换轮次后取消请求并丢弃旧响应；401/403/404停止。
- [x] AC-005：手动核验保留版本围栏和幂等，不调用模型、不重放治理命令。
- [x] AC-006：真实浏览器记录执行终态、自动核验与界面更新的脱敏时间线。

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
accepted_at: 2026-10-26 19:55:10
accepted_by: workflow-sync
source_change: fix-chat-auto-verification-status-stale
source_sprint: sprint-014
evidence: [openspec/archive/2026-10-26-fix-chat-auto-verification-status-stale/evidence/acceptance/20261026191303432657-47e3dc27/summary.md]
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本次验收签认
2026-10-26 19:17:59：全部AC通过，见[逐项证据报告](../../../../openspec/changes/fix-chat-auto-verification-status-stale/evidence/acceptance/20261026191303432657-47e3dc27/summary.md)。合成回归、MySQL兼容和隔离真实浏览器分别记录；浏览器使用真实HTTP与后台控制器、合成业务证明，未重放原用户命令。历史原始事件身份缺口不扩张为全链路确认。
