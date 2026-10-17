---
bug_id: BUG-0036-bug
title: 需求中心 Bug 生成治理链路验收隔离夹具
status: captured
created_at: '2026-10-10 11:20:21'
updated_at: '2026-10-10 11:20:21'
severity: low
owner: user_b6aa2646805846d49532232d30dcff48
source: capture
lifecycle_stage: plan
captured_via: capture
capture_source:
  task_id: 471d3603-22c9-4ebe-8f0c-c88d55e0de4a
  candidate_id: a0d40197-c362-46d6-a262-d221bb2b5d7c
  revision: 6
  initial_type: bug
  final_type: bug
  adjusted_fields: []
  parents: []
classification_rationale: 材料用于既有需求中心治理链路的 Bug 验收夹具，不提出独立新能力，故按 bug 类型整理为测试候选；这不构成真实缺陷认定。severity
  暂取 low，仅用于满足候选分级结构，实际影响尚无证据。
---

# 需求中心 Bug 生成治理链路验收隔离夹具

## 现象

需求中心 Bug 生成治理链路验收隔离夹具

## 补充说明

材料明确将本对象定义为本地验收测试夹具，仅用于验证 MoonBox 需求中心 bug-generate、候选、自动应用、状态投影与后续治理命令的真实产品链路，不代表新发现的产品缺陷，不纳入正式交付或 Sprint。预期验收行为：从采集池发送生成命令后，留下候选和应用记录，生成 bug.md 与 trace.md，注册表与看板显示一致；异常时保留旧成果。材料关联标识为 BUG-0025-requirement-center-command-chain-write-gap，仅保留为来源事实，不作为本候选正式编号。材料未提供实际异常或验收结果。
