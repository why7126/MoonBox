---
requirement_id: REQ-0034-requirement-center-default-current-iteration-cards
title: 需求中心默认只显示当前迭代卡片
status: captured
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-14 09:07:45
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0012-frontend-requirement-center
captured_via: capture
classification_rationale: 用户要求需求中心默认列表范围调整为当前迭代，属于默认展示策略增强。
priority: P1
---

# 一句话

需求中心进入页面时默认只显示当前迭代相关卡片，减少历史或非当前范围卡片干扰。

# 原始描述

用户反馈：“默认只显示当前迭代卡片”。

# 初步范围

- 默认展示范围切换为当前迭代卡片。
- 用户仍应能通过筛选或显式操作查看非当前迭代卡片，具体入口留待后续确认。
- 存在多个当前迭代时需要与容量展示和筛选规则保持一致。

# 待澄清

- [ ] 当前迭代的判断来源：Sprint 状态、目录阶段、配置标记，还是组合规则。
- [ ] 多个当前迭代时默认展示全部当前迭代，还是要求用户选择一个。
- [ ] 非当前迭代卡片的查看入口和筛选重置行为。

# 建议验收要点

1. 首次进入需求中心时仅展示当前迭代相关卡片。
2. 存在 2 个当前迭代时，默认范围与产品确认的多迭代规则一致。
3. 用户能通过筛选查看历史/非当前卡片，且重置后回到默认当前迭代范围。

# 探索结论

尚未执行 `/req-explore`；本记录仅完成轻量采集。
