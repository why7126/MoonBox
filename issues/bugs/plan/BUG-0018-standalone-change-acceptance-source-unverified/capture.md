---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
status: captured
created_at: '2026-09-14 09:16:42'
updated_at: 2026-09-14 09:18:20
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
environment: web
related_requirement: REQ-0026-requirement-center-standalone-change-cards
related_bug: null
related_change: null
captured_via: capture
classification_rationale: 用户反馈的是已交付的需求中心独立 Change 卡片在验收中阶段展示“验收来源待核实：未找到交付验证记录”，而归档 Change 已存在验证记录与证据目录；属于既有能力与规格要求不一致，按缺陷采集。
severity: medium
---

# 现象

需求中心“验收中 / 测试与人工验收”分组内，独立 Change 卡片 `refresh-issue-index-after-archive-promotion` 展示红色提示：

- “验收来源待核实：未找到交付验证记录”

用户提供的截图显示该卡片包含 `trace.md`、`sprint.md`、`proposal.md`、`spec.md`、`design.md`、`tasks.md` 等文档入口，并归属 `sprint-005`。

# 复现步骤

1. 打开需求中心或相关当前迭代看板。
2. 查看“验收中 / 测试与人工验收”分组。
3. 定位独立 Change 卡片 `refresh-issue-index-after-archive-promotion`。
4. 观察卡片是否展示“验收来源待核实：未找到交付验证记录”。

# 期望 vs 实际

- 期望：独立 Change 卡片按自身交付验证记录、归档 Change 验证文件或证据目录定位验收来源；若存在可追溯交付验证记录，不应展示“未找到交付验证记录”。
- 实际：卡片展示“验收来源待核实：未找到交付验证记录”，容易误导为该 Change 缺少交付验证。

# 初步证据

- 用户截图：`screenshots/user-evidence-acceptance-source-unverified.png`
- 相关已归档能力：`add-requirement-center-change-visibility`
- 已归档相关能力：`openspec/archive/2026-09-14-add-requirement-center-change-visibility/verification.md`
- 已归档相关证据目录：`openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/`
- 已生效规格片段要求：独立 Change 应按自身交付证据定位验收来源，不套用 Issue 固定 `acceptance.md` 要求。

# 影响范围

- 影响需求中心独立 Change 卡片的验收来源展示。
- 可能影响用户对独立 Change 交付完整性、验收状态和归档质量的判断。
- 暂未确认是否只影响 `refresh-issue-index-after-archive-promotion`，或所有缺少 Issue 绑定的独立 Change。

# 待澄清与补证

- [ ] 当前前端/后端用于判断“交付验证记录”的数据字段与路径来源。
- [ ] `refresh-issue-index-after-archive-promotion` 对应 Change 的真实目录位置、验证文件和证据目录是否可被接口读取。
- [ ] 该提示是否由前端兜底误判、后端聚合遗漏，或 Workflow Sync/索引派生缺少独立 Change 验收来源字段导致。

# 建议验收要点

- 对存在 `verification.md` 或 `evidence/` 的独立 Change，不展示“未找到交付验证记录”。
- 独立 Change 的验收来源展示应引用自身验证记录，不强制要求 Issue `acceptance.md`。
- 对确实缺少验证记录的独立 Change，提示应说明缺失的具体证据类型和可补证路径。
