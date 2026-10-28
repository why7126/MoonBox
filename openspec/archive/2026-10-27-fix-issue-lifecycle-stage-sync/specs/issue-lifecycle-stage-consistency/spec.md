---
title: Issue 生命周期阶段一致性
created_at: 2026-10-27 09:17:15
updated_at: 2026-10-27 09:17:15
---

# Issue 生命周期阶段一致性

## ADDED Requirements

### Requirement: 生命周期阶段投影
治理工具 MUST 按物理目录维护 trace、主文档、capture 中已有的生命周期阶段字段，并在迁移预览展示目标阶段；不得修改正文历史或其他语义状态。

#### Scenario: 评审及归档迁移
- **WHEN** Issue 从 plan 迁入 review 或从 review 迁入 archive
- **THEN** 已有阶段字段与目标目录一致，重复同步不产生修改

### Requirement: 阶段残留校验与定向修复
治理工具 MUST 检出阶段残留，合法值可定向同步，非法值须阻断；修复须可预览且不重跑归档。

#### Scenario: 已归档阶段残留
- **WHEN** 已归档 Issue 主文档阶段残留为 plan
- **THEN** 扫描报告字段差异，预览不写入，修复保持历史证据与其他语义字段不变
