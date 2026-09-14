---
change_id: repair-change-identity-uniqueness
status: applied
lifecycle_stage: change
iteration: sprint-004
created_at: 2026-09-13 15:59:31
updated_at: 2026-09-13 23:45:17
---

# 执行追溯

## 根因证据

confirmed：两个日期归档使用相同 change_id，用户确认初建和强化为不同工作。治理修复不改变历史实施结果。

## 执行结果（2026-09-13 16:06:17）

- 7 项 unittest 回归通过，包含跨日期重复归档、活动/归档冲突、已归档 ID 创建拒绝、身份不一致，以及归档修改前阻断。
- 实际仓库 ChangeIndex 只读验证：初建与强化分别解析为唯一 archive/done，无 conflict。
- 唯一性脚本、上下文预算、目标 Change strict validate、两项 Sprint scope、bash 语法检查通过。
- 全局中文校验仍被既有 fix-requirement-center-apply-lifecycle-sync 的 6 处英文标题阻断；本 Change 已修正并无剩余命中。
- 目录校验身份部分通过，整体仍被既有根目录 logs 未登记阻断；未改动该运行时目录。
- Workflow Sync：sprint-004，更新 2 项，跳过 7 项，错误 0。
- Sprint 显式容量仍为 30 人天；补登记强化和本次修复各 1 人天后为 32 人天（106.67%），处于容量风险区间而未超过 120% 硬门禁。估算不代表历史实耗。

身份纠正已完成，当前治理 Change 已实施、待归档；不改动 openspec/specs 正式规格。API/DB/Web/管理端/客户端/Orval/Docker Compose/安全边界均无变更。

收尾：再次 Workflow Sync 更新 0、跳过 9、错误 0；初建项 Sprint scope 同样通过。AI Usage Hook：warning / unavailable，command_run_count=0，Sprint snapshot skipped；当前未发现可归因的 token_count 事件，不补造用量。初建治理日志的当前归档入口也已纠正。

## 归档门禁恢复（2026-09-13 23:44:15）

目录、全局中文、上下文预算、环境忽略及目标 Change strict 校验全部通过；隔离验证3项通过（无忽略拒绝、忽略且未跟踪通过、强制跟踪拒绝）。日志文件数量与聚合SHA-256前后一致，未移动或修改日志。API/DB/Web/管理端/客户端/Orval/Docker Compose及业务安全边界无变更。
历史失败记录保留，当前结果以上述复验为准。

## 归档完成（2026-09-13 23:45:17）

归档目录 openspec/archive/2026-09-13-repair-change-identity-uniqueness；正式规格新增2条要求，脚手架Purpose已补齐中文说明。Workflow Sync更新2项、跳过7项、错误0，Sprint为sprint-004；无关联Issue需要迁移。日志32个文件完整性通过，目录、中文、环境忽略及归档证据门禁通过。

AI Usage归档Hook：warning、unavailable，command_run_count=0，sprint_snapshot=skipped，warning_count=1；无可归因用量事件，不影响归档结果。
