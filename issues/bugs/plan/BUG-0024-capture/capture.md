---
bug_id: BUG-0024-capture
title: 列表刷新后滚动位置回到顶部
status: captured
created_at: '2026-09-16 20:00:07'
updated_at: '2026-09-16 20:00:07'
severity: medium
owner: user_f694abc671d548b48d9eb897f720ba4d
source: capture
lifecycle_stage: plan
captured_via: capture
capture_source:
  task_id: cb427af3-3122-4350-abca-3ad3abef8d28
  candidate_id: 3091f068-0367-45f3-80bb-70752fcba993
  revision: 33
  initial_type: bug
  final_type: bug
  adjusted_fields: []
  parents: []
classification_rationale: 反馈指向已有列表刷新行为的疑似偏差，倾向 BUG。所提供规格未明确要求刷新后保持滚动位置，因此仍需确认预期行为。暂按浏览连续性受影响评为
  medium，实际影响范围待确认。
---

# 列表刷新后滚动位置回到顶部

## 现象

列表刷新后滚动位置回到顶部

## 补充说明

用户反馈列表刷新后会回到顶部，并认为该行为可能存在问题，要求单独整理为候选。期望刷新后保留原浏览位置；具体列表、刷新方式及滚动位置保持规则待澄清，尚无复现验证。
