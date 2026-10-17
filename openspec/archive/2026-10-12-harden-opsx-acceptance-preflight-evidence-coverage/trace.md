---
change_id: harden-opsx-acceptance-preflight-evidence-coverage
title: 自动验收预检与证据覆盖追溯记录
status: applied
created_at: 2026-10-12 23:05:00
updated_at: 2026-10-12 23:19:00
sprint: sprint-009
requirement: null
bug: null
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 仅改治理验收脚本的预检、脱敏证据元数据和报告，不改产品请求、事件采集或数据库。
  validation: 定向单测及治理校验通过；不读取或存储原始产品消息。
execution:
  schema_version: 1
  started_at: 2026-10-12 23:05:00
  completed_at: 2026-10-12 23:09:57
  last_event: opsx.apply
---

# 自动验收预检与证据覆盖追溯记录

## 来源与范围

源于已归档 BUG-0029 的两轮自动验收复盘。纯治理 Change，纳入 `sprint-009`；不修改业务代码、产品 API 或数据库结构。

## 验证记录

`tests/unit/test_opsx_acceptance.py` 18 项通过（1 条上游 Starlette 弃用提醒）。`openspec validate`、当前 Change 中文校验、中文标题、目录结构和 Agent 上下文预算校验通过。新增测试覆盖缺证据时不执行 AC、阻塞诊断不替换完整清单、视觉阶段视口缺项及逐 AC 证据路径报告。实际产品视觉语义仍由验收者目视签认，脚本只验证声明映射及文件哈希。Sprint 容量原已超出 30 人天，本项新增 1 人天，保留原容量和预警。

2026-10-12 `/opsx-accept`：根据纯治理范围建立 AC-001–003 计划，环境与样本预检通过；完整运行 `evidence/acceptance/20261012231443508040-67c17ae6/summary.md` 为 3/3 passed，`--readiness` 为 ready、无 stale。脱敏验证矩阵位于 `evidence/acceptance/validation-matrix.md`。本次 AC 是治理脚本合成回归、文件状态和标准一致性检查，不涉及产品页面或 Chat 发送轮次，也不据此宣称真实产品视觉效果。

归档前复核发现新增视觉覆盖要求误置于规格增量的 `MODIFIED` 章节；已归到 `ADDED`，并将规格文件加入 AC-003 输入。增量复验清单 `evidence/acceptance/20261012231856024778-60eef042/summary.md` 为 3/3 passed，AC-001、AC-002 复用有效结果，AC-003 重新执行；readiness 为 ready、无 stale。OpenSpec 与中文校验通过。
