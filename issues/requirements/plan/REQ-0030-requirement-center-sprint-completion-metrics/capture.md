---
requirement_id: REQ-0030-requirement-center-sprint-completion-metrics
title: 需求中心指标卡新增 Sprint 已完成与累计数量
status: captured
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-14 09:07:44
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0012-frontend-requirement-center
captured_via: capture
classification_rationale: 用户要求在需求中心指标卡新增 Sprint 数量统计，属于尚未交付的看板指标增强。
priority: P1
---

# 一句话

需求中心指标卡新增 Sprint 数量统计，展示已完成 Sprint 数与累计 Sprint 数。

# 原始描述

用户反馈：“指标卡新增Sprint数量 已完成/累计数”。

# 初步范围

- 在需求中心顶部或既有指标卡区域新增 Sprint 数量指标。
- 指标至少包含已完成 Sprint 数量与累计 Sprint 数量。
- 统计口径需与 Sprint 生命周期事实源保持一致，避免只按前端临时卡片或局部筛选结果计算。

# 待澄清

- [ ] “已完成”是否仅统计 `archive` Sprint，还是包含状态为 completed 但尚未物理归档的 Sprint。
- [ ] 指标是否受当前筛选条件影响，或始终显示全局项目统计。
- [ ] 空状态、无 Sprint、加载失败时的展示文案。

# 建议验收要点

1. 有已归档与未归档 Sprint 时，指标卡分别展示已完成数量与累计数量。
2. 指标刷新后与 Sprint 事实源一致，不能因前端卡片过滤导致口径漂移。
3. 无 Sprint 或接口失败时展示稳定空态/错误态，不影响需求中心其他卡片加载。

# 探索结论

尚未执行 `/req-explore`；本记录仅完成轻量采集。
