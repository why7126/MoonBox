---
bug_id: BUG-0037-change-status-projection-unknown
title: 需求看板端口迁移 Change 状态异常临时处理
created_at: '2026-10-11 10:12:03'
updated_at: '2026-10-11 10:12:03'
---

# 需求看板端口迁移 Change 状态异常临时处理

## 临时处理

在产品修复前，将看板“数据异常”中的目标 Change 视为**待核实**，不要从当前统计推断它不存在或已完成。通过只读治理文档核对活动 Change 的 `trace.md`、`tasks.md` 和 `sprint-009/sprint.yaml`，并记录运行服务实际读取的治理根目录及版本。任务 4/4 和 Sprint 摘要中的 `applied` 只作线索。

若需要恢复生命周期状态，应通过现有正式治理命令和可复核执行事实完成；在事实不足时保留异常提示，不直接手改 trace 或绕过归档门禁。本临时处理不解决产品诊断入口和新记录防复发问题。
