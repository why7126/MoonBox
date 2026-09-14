---
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
title: 需求中心 Sprint 下拉列表新增状态展示
status: captured
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-14 09:07:45
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0012-frontend-requirement-center
captured_via: capture
classification_rationale: 用户要求 Sprint 下拉列表新增状态字段，属于已有筛选/选择控件的信息展示增强。
priority: P2
---

# 一句话

需求中心 Sprint 下拉列表在每个选项中展示 Sprint 状态，帮助用户区分当前、规划中、已完成或归档迭代。

# 原始描述

用户反馈：“Sprint下拉列表 新增状态”。

# 初步范围

- 在 Sprint 下拉选项中增加状态信息。
- 状态文案需与项目内 Sprint 生命周期一致，避免前端自造不可追溯状态。
- 排序、筛选与默认选中行为需与现有 Sprint 下拉交互兼容。

# 待澄清

- [ ] 状态展示为文本、标签、颜色，还是组合展示。
- [ ] 是否需要按状态分组或优先展示当前迭代。
- [ ] 状态枚举与后端字段的映射关系。

# 建议验收要点

1. Sprint 下拉中每个选项能看到可理解的状态。
2. 多状态混合时排序和当前选中项清晰，不影响原有选择操作。
3. 状态数据缺失或未知时有稳定兜底展示。

# 探索结论

尚未执行 `/req-explore`；本记录仅完成轻量采集。
