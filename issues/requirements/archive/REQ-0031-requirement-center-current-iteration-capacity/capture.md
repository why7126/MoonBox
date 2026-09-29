---
requirement_id: REQ-0031-requirement-center-current-iteration-capacity
title: 需求中心显示当前迭代容量已使用与总容量
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:32:24
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0012-frontend-requirement-center
captured_via: capture
classification_rationale: 用户要求显示当前迭代容量和 2 个当前迭代的容量汇总，属于需求中心 Sprint 容量可视化新能力。
priority: P1
---

# 一句话

需求中心展示当前迭代容量，支持存在 2 个当前迭代时查看已使用容量与总容量。

# 原始描述

用户反馈：“显示当前迭代容量（2个当前迭代），已使用容量/总容量”。

# 初步范围

- 在需求中心显示当前迭代容量信息，格式包含已使用容量/总容量。
- 支持同时存在 2 个当前迭代的场景，避免只展示其中一个或覆盖另一个。
- 容量口径需承接 Sprint 容量规则，默认容量、已使用容量和显式容量覆盖策略留到后续需求完善阶段确认。

# 待澄清

- [ ] 2 个当前迭代是并列展示、汇总展示，还是一主一辅展示。
- [ ] 已使用容量按 REQ/BUG/Change 估算、已纳入 Scope 估算，还是实际消耗统计。
- [ ] 容量超过总容量时是否需要风险提示或视觉强调。

# 建议验收要点

1. 单个当前迭代时展示该迭代已使用容量/总容量。
2. 同时存在 2 个当前迭代时，两者容量信息均可识别，不被静默合并或覆盖。
3. 容量数据与 Sprint 事实源一致，空值、默认值、超量状态有稳定展示。

# 探索结论

尚未执行 `/req-explore`；本记录仅完成轻量采集。
