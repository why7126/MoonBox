---
title: 历史归档验收样本状态兼容规格
created_at: 2026-10-17 17:00:00
updated_at: 2026-10-17 17:00:00
---
# 历史归档验收样本状态兼容规格

## MODIFIED Requirements

### Requirement: 增量复验与安全样本

系统 MUST 对输入或计划已变化的 AC 重新取证；仅在证据未过期且来源可复核时复用旧结果。单项复验缺少其他 AC 的有效结论时只生成诊断清单，不覆盖完整清单的归档就绪判定。已归档 Change 的历史计划可兼容已知旧样本状态，但 MUST 保留原始计划和 manifest，并核验证据后才投影通过。

#### Scenario: 已归档计划包含历史样本状态

- **WHEN** canonical 归档目录中的验收计划使用历史值 `completed-source-archive`
- **THEN** 计划读取 MUST 兼容该值且不改写归档文件
- **AND** 只有原完整通过 manifest 与附件校验通过时，Workflow Sync 才可保留已签认 AC 的通过投影。

#### Scenario: 活动计划使用历史样本状态

- **WHEN** 活动 Change 的验收计划使用 `completed-source-archive`
- **THEN** 计划校验 MUST 拒绝该值，不能将其作为新计划合法状态。
