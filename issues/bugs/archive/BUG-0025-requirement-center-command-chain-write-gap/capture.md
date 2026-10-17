---
bug_id: BUG-0025-requirement-center-command-chain-write-gap
title: 需求中心看板展示完整治理命令链但多数命令未接入真实写入
status: done
created_at: '2026-09-16 23:49:40'
updated_at: 2026-10-14 17:43:05
owner: user_f694abc671d548b48d9eb897f720ba4d
source: capture
lifecycle_stage: plan
captured_via: capture
capture_source:
  task_id: 3c911e6f-dc95-42a0-9bb4-fb4b62d6dab2
  candidate_id: 271ec15d-dd4b-4f00-aa24-09c676adc9d9
  revision: 8
  initial_type: requirement
  final_type: bug
  adjusted_fields:
  - type
  - priority
  - severity
  parents: []
classification_rationale: 用户审阅将类型从 requirement 调整为 bug；初始建议依据：材料不足以判断是否涉及已有能力或规范偏差，暂按待澄清需求收录；类型及优先级均待确认，不据规格摘要推定缺陷或新增能力。
severity: medium
---

# 需求中心看板展示完整治理命令链但多数命令未接入真实写入

## 现象

需求中心看板展示完整治理命令链，但产品内仅 req-generate 具备真实治理写入链路，bug-generate、complete、review、sprint-propose、opsx 系列仍停留在文案或模拟流转。

## 补充说明

看板、弹窗或 action hint 会展示 `/bug-generate`、`/req-complete`、`/bug-complete`、`/req-review`、`/bug-review`、`/sprint-propose`、`/req-opsx`、`/bug-opsx`、`/opsx-apply`、`/opsx-archive` 等命令，但当前产品真实治理候选与应用链路仅支持采集池需求的 `/req-generate`。这会导致用户以为点击或进入 Chat 后可以像 Codex 命令一样生成文档、推进阶段并写入事实源，实际只得到普通回复或前端模拟流转。
