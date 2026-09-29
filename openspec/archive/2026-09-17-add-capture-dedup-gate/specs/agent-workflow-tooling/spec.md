---
title: Capture 创建前去重门禁规格
created_at: 2026-09-16 22:42:16
updated_at: 2026-09-16 22:42:16
---

# Capture 创建前去重门禁规格

## ADDED Requirements

### Requirement: Capture 创建前重复相似 Issue 检查

`/capture`、`/req-capture` 和 `/bug-capture` MUST 在创建新 REQ/BUG 前执行重复/相似 Issue 检查。系统 MUST 先读取对应类型的 `CHANGELOG.md` 与 `_registry.yaml` 建立候选范围；候选不清晰时，MUST 只读取疑似候选目录中 `capture.md` 与 `trace.md` 的标题、Frontmatter、摘要、状态、关联 Sprint/Change 和下一步必要片段。系统 MUST NOT 为判重全量读取无关 Issue 正文、历史归档大目录或生成物。

#### Scenario: req-capture 识别已有需求补充

- **GIVEN** 用户输入的需求与现有 REQ 在业务域、目标用户、交付能力或验收闭环上高度相似
- **WHEN** 系统执行 `/req-capture`
- **THEN** 系统 MUST 在分配新 REQ ID 前输出候选 REQ、相似原因、当前状态、事实源路径和处理选项
- **AND** 系统 MUST 默认推荐关联或更新原 REQ，必要时使用 `parent_requirement`
- **AND** 系统 MUST 只有在用户确认非重复或候选仅弱相关后才创建新的 peer REQ

#### Scenario: bug-capture 识别已有缺陷补充

- **GIVEN** 用户输入的缺陷与现有 BUG 在页面、现象、触发条件、根因假设或修复面上高度相似
- **WHEN** 系统执行 `/bug-capture`
- **THEN** 系统 MUST 在分配新 BUG ID 前输出候选 BUG、相似原因、当前状态、事实源路径和处理选项
- **AND** 系统 MUST 默认推荐关联或更新原 BUG，必要时填写 `related_bug` 或 `related_requirement`
- **AND** 系统 MUST 只有在用户确认非重复或候选仅弱相关后才创建新的 peer BUG

#### Scenario: capture 混合输入分别检查

- **GIVEN** 用户通过 `/capture` 输入混合需求与缺陷
- **WHEN** 系统完成分类和拆分
- **THEN** 系统 MUST 对需求条目按 REQ 候选执行重复/相似检查
- **AND** 系统 MUST 对缺陷条目按 BUG 候选执行重复/相似检查
- **AND** 疑似重复条目 MUST 先完成用户决策，非重复条目 MAY 继续按正常 capture 流程创建
