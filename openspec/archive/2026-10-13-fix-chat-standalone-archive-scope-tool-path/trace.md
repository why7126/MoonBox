---
change_id: fix-chat-standalone-archive-scope-tool-path
title: 修复 Chat 中纯治理 Change 归档授权与命令工具路径追溯记录
status: applied
created_at: 2026-10-09 10:54:00
updated_at: 2026-10-13 18:38:00
bug: BUG-0034-chat-standalone-archive-scope-tool-path
requirement: null
sprint: sprint-009
product_data_collection_observability:
  status: applicable
  affected_layers:
    - chat_turns
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 归档权限与命令执行状态需要沿用既有脱敏链路观测。
  validation: 同轮次对照服务端权限决策、工具退出状态与归档事实；无新增采集字段。
execution:
  schema_version: 1
  started_at: 2026-10-09 10:55:40
  completed_at: 2026-10-09 11:07:13
  last_event: opsx.apply
---

# 修复 Chat 中纯治理 Change 归档授权与命令工具路径追溯记录

## 来源与范围

来源：`BUG-0034-chat-standalone-archive-scope-tool-path`，关联 `BUG-0026-chat-platform-opsx-archive-source-permission`，纳入 `sprint-009`。已修复服务端归档权限判定、归档续接对象解析及执行器命令 PATH。

## 验证记录

| 验证层 | 结果 |
|---|---|
| 权限策略与工具链回归 | `test_chat.py`、`test_chat_toolchain.py`、`test_chat_platform.py`：72 passed、1 skipped；覆盖纯治理、撤销 Sprint 范围、来源字段冲突、归档续接及 REQ/BUG 既有路径。 |
| 真实执行容器 | `moonbox-archive` 沙箱中 `cat`、`node`、`openspec`、`python` 均可解析；仅归档授权目录可写，根目录写入被拒绝；固定 PATH 下工具链预检通过。 |
| 隔离仓库归档 | 使用仓库受控快照运行 `archive-change.sh ... --finalize`：退出码 0、唯一 canonical archive 存在、归档证据 PASS、Workflow Sync 0 errors；未接触产品业务数据。 |
| 本地产品部署 | 标准停启后 Web、Backend、Chat Worker、治理控制器与 MinIO 均健康；Backend `/health` 成功，Worker 心跳新鲜且配置指纹一致。MinIO 私有镜像拉取失败后使用本机已有兼容镜像恢复，未改持久配置。 |
| 真实产品归档 | 原目标 Change 已在修复前安全归档；后续使用用户授权的一次性隔离纯治理样本，在本地 `source` 工作区取得产品对象 Chat 完成态与唯一事实源归档，详见下文。 |

本次未新增 API、数据库结构、UI、客户端生成、部署拓扑或安全权限目录；部署说明已同步。归档权限范围变更属于服务端安全策略，已覆盖正反向测试。

## 自动验收诊断

2026-10-13 `/opsx-accept` 建立逐 AC 计划并运行诊断。AC-001～003 的聚焦命令检查通过；AC-004 仅复核既有隔离归档记录，原始隔离样本未保留；AC-005 缺新的获授权纯治理 Change 产品归档轮次和授权只读产品 SQLite 数据源。完整清单为 `blocked / diagnostic`，未取得归档就绪，不改变 `applied` 事实。完整诊断入口：`evidence/acceptance/20261013164505227518-4d670577/summary.md`；分项命令入口：`evidence/acceptance/20261013164714406041-642de3a8/summary.md`。

随后在用户授权的一次性隔离产品中创建纯治理样本并发起对象 Chat 归档。目标脚本同轮退出码为 0，会话工作区形成归档目录，但轮次因 `result_or_token_limit` 停止，治理来源未应用归档结果；归档续接又因活动 trace 已迁移而触发 `change_trace_missing`。完整自动验收为 `failed / complete`，AC-005 未通过，证据入口：`evidence/acceptance/20261013171644490479-c488e1fb/summary.md`、`evidence/acceptance/samples/AC-005.md`。Change 保持 `applied`，不宣称归档就绪。

验收返修批次一：再次获授权的隔离纯治理样本 `fix-isolated-chat-archive-acceptance-20261013` 先在离线副本完整归档预检通过。产品 `source` 工作区首次归档轮次 `8436f1d1-4381-423a-89f2-2f29f789edc0` 的权限为 `archive_write / archive_change_applied`，轮次 `completed`、目标命令退出码 0、源仓库唯一 canonical archive 存在且活动目录消失。首次 `--finalize` 续接因门禁只读活动 trace 而失败；修复 `scripts/validate-issue-acceptance-ready.py` 后，产品轮次 `f908138b-7395-438b-add3-ece95e413b6b` 完成、目标命令退出码 0、Workflow Sync 0 errors。聚焦门禁与归档恢复回归 16 passed。完整台账与脱敏证据：`acceptance-fixes.md`、`evidence/acceptance/samples/AC-005.md`。本次只修复既有归档续接门禁；无新增 API、DB、UI、部署拓扑、权限 profile 或客户端生成。

验收返修批次二：Workflow Sync 刷新 Issue 验收状态投影后，自动验收清单因全文指纹而立即过期。现保留 AC 条件指纹，排除生成的时间、状态与结果块；验收及归档相关单测 35 passed。规范说明见 `docs/standards/opsx-acceptance.md`，治理记录见 `docs/spec-logs/20261013184500-governance-opsx-acceptance-fingerprint.md`。两批返修均未改变 Change 首次 apply 的 `execution.completed_at`，当前状态仍为 `applied`，待最终 `/opsx-accept` 清单与同步结论。
