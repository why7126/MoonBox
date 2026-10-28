---
title: 归档解释器修复交付追踪
created_at: 2026-10-26 12:55:09
updated_at: 2026-10-26 12:59:40
change_id: fix-archive-python-entry
status: applied
iteration: sprint-014
execution:
  schema_version: 1
  started_at: 2026-10-26 12:55:12
  completed_at: 2026-10-26 12:59:11
  last_event: opsx.apply
---

# 归档解释器修复交付追踪

## 来源
用户明确授权，承接 unify-governance-python-entry，纯治理 Change 纳入 sprint-014。
## 根因证据
archive-change.sh 原第161行直接执行 python，实际报 ModuleNotFoundError: sqlalchemy；指定项目虚拟环境后同一归档成功。代码证据显示整个脚本未引用 project-python.sh/PYTHON_BIN。既有校验仅遍历 Skill，未覆盖 shell。根因 confirmed：脚本未接入已交付入口。
## 验证记录
环境预检通过；后续隔离验证结果在本 Change 记录。业务测试不适用。


## 实施验证摘要
复用统一入口完成归档解释器接入，所有Python调用已使用PYTHON_BIN。32项测试通过（统一入口10、隔离归档7、既有身份与恢复15）。补齐旧恢复测试夹具所需delta及解释器入口，不改变门禁或降低断言。

证据：[隔离回归与恢复验证](evidence/validation.md)。上下文预算、中文、OpenSpec、标题、Sprint范围、目录及差异检查通过；目录保留既有legacy SQLite警告。API/DB/UI/部署/安全权限/客户端生成不适用，无业务代码改动。product_data_collection_observability: N/A；affected_layers: []。真实归档未重放，待本Change验收完成后按正常授权归档。

## 最终验收
4项AC通过，完整证据：[验收报告](evidence/acceptance/20261026125912610465-6e08d2b0/summary.md)。32项相关回归覆盖入口、隔离归档与原有恢复链路；归档预演通过，readiness为ready，opsx.apply与opsx.accept同步成功。未正式归档、未提交Git。
