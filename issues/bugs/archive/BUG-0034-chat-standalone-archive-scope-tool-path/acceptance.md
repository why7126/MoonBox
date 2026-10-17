---
bug_id: BUG-0034-chat-standalone-archive-scope-tool-path
title: 产品内纯治理 Change 归档权限与工具路径修复验收方案
created_at: 2026-10-09 10:52:00
updated_at: 2026-10-17 17:01:21
acceptance_status: passed
---

# 产品内纯治理 Change 归档权限与工具路径修复验收方案

## 验收条件

以下复选框是进入验收阶段后的卡片计数来源；表格及后续“实施验证进度”保留隔离测试事实，不替代真实产品复验和验收签认。

- [x] AC-001：合法纯治理 Change 归档获得归档写权限。
- [x] AC-002：非归档命令或门禁不足时不获得额外归档写权限。
- [x] AC-003：真实执行沙箱内基础工具可用且无额外网络或宿主挂载。
- [x] AC-004：隔离临时仓库归档完成规格、目录、Workflow Sync 与终态闭环。
- [x] AC-005：真实产品中新的可归档纯治理 Change 完成对象 Chat 归档复验。

| 编号 | 操作与条件 | 期望结果 |
|---|---|---|
| AC-001 | 有写权限成员在纯治理 Change 已 applied、已纳入 Sprint、主对象匹配时发送完整 `/opsx-archive` 命令 | 授予 `archive_write / moonbox-archive`，不依赖 requirement/bug 字段 |
| AC-002 | 同对象发送其他命令、Change 未 applied、未纳入 Sprint、主对象不匹配或成员被撤权 | 不授予归档写权限；普通治理 profile 仍不可写规格和归档目录 |
| AC-003 | 在真实执行沙箱内运行 `cat`、Python、Node、OpenSpec 版本或状态命令 | 固定 PATH 可解析镜像内工具；无外部网络或额外宿主挂载 |
| AC-004 | 使用隔离临时仓库执行纯治理 Change 归档 | 规格合并、归档目录、Workflow Sync 与执行终态一致；原 Change 不重复合并 |
| AC-005 | 在真实产品新建一次可归档纯治理 Change 并执行 Chat 命令 | 记录真实轮次、权限 profile、工具执行和事实源结果；不把合成回归冒充真实观察 |

## 数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - chat_turns
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 权限决策和执行器工具失败影响现有 Chat 执行链路观察。
  validation: 对照同轮次脱敏权限决策、工具退出状态和 Change 归档结果；不记录 Prompt 全文、凭证或本机绝对路径。
```

本次未新增 API、DB 表、行为埋点或客户端请求封装；`usage_events` 新采集为 N/A，原因是操作入口和行为事件契约未变化。

## 实施验证进度

AC-001 至 AC-004 已由权限回归、真实沙箱及隔离仓库归档覆盖。AC-005 仍待真实产品中出现获授权且可安全归档的纯治理 Change 后复验；原目标已在修复前安全归档，不重复归档，也不将隔离探针冒充产品轮次证据。

2026-10-13 `/opsx-accept` 诊断：聚焦回归 22 passed；计划级 AC-001、AC-002、AC-003 命令检查通过，AC-004 仅复核既有隔离归档文字记录，原隔离样本未保留，以上均不替代最终验收签认。AC-005 缺新的获授权纯治理 Change 产品归档轮次及其授权只读 SQLite 数据源，预检诊断为 `product-db-unavailable`。完整清单为 `blocked / diagnostic`，归档就绪未取得。证据入口：`../../../../openspec/archive/2026-10-13-fix-chat-standalone-archive-scope-tool-path/evidence/acceptance/20261013164505227518-4d670577/summary.md`；分项命令诊断入口：`../../../../openspec/archive/2026-10-13-fix-chat-standalone-archive-scope-tool-path/evidence/acceptance/20261013164714406041-642de3a8/summary.md`。

## 最终复验

用户授权的隔离纯治理样本 `fix-isolated-chat-archive-acceptance-20261013` 在产品 `source` 工作区完成首次归档；轮次 `8436f1d1-4381-423a-89f2-2f29f789edc0` 为 `completed`、目标命令退出码 0，源仓库只保留唯一 canonical archive。修复归档续接门禁后，`--finalize` 轮次 `f908138b-7395-438b-add3-ece95e413b6b` 亦为 `completed`、退出码 0，Workflow Sync 0 errors。权限负向、工具链和离线完整归档分别验证，脱敏细节见 `../../../../openspec/archive/2026-10-13-fix-chat-standalone-archive-scope-tool-path/evidence/acceptance/samples/AC-005.md`。上文未完成记录是当时历史状态，本节与下方自动回填为当前结论。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 17:01:21
accepted_by: workflow-sync
source_change: fix-chat-standalone-archive-scope-tool-path
source_sprint: sprint-009
evidence: [openspec/archive/2026-10-13-fix-chat-standalone-archive-scope-tool-path/evidence/acceptance/20261013184622633595-b08ca3e4/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
