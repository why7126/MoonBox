---
requirement_id: REQ-0033-requirement-center-filter-multiselect-search
title: 需求中心筛选下拉框支持复选搜索多选与排序优化
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:30:56
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0012-frontend-requirement-center
captured_via: capture
classification_rationale: 用户要求筛选下拉框交互优化，包括复选框、搜索、多选和排序，属于需求中心筛选体验增强。
priority: P1
---

# 一句话

需求中心筛选下拉框升级为支持复选框、搜索、多选和更合理排序的筛选控件。

# 原始描述

用户反馈：“筛选下拉框交互优化（复选框、搜索+多选下拉框，排序优化）”。

# 初步范围

- 对需求中心筛选下拉控件提供多选能力。
- 下拉内支持搜索，便于在较多选项中快速定位。
- 使用复选框表达选中状态。
- 优化筛选项排序，让常用或当前相关选项更容易找到。

# 待澄清

- [ ] 涉及哪些筛选维度：Sprint、状态、类型、优先级、负责人、Change 或全部。
- [ ] 多选条件内部是 OR 还是 AND，不同筛选维度之间如何组合。
- [ ] 排序规则是按状态优先、最近更新时间、名称、编号，还是自定义优先级。

# 建议验收要点

1. 支持对目标筛选维度进行多选，选中状态清晰可见。
2. 搜索能过滤下拉项，清空搜索后恢复完整列表。
3. 排序规则稳定，当前迭代、常用状态或高相关项能优先出现。
4. 筛选结果、URL/状态保存、清空筛选和刷新后的表现符合后续设计约定。

# 探索结论

尚未执行 `/req-explore`；本记录仅完成轻量采集。
