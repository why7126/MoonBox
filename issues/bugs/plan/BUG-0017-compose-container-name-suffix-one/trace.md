---
bug_id: BUG-0017-compose-container-name-suffix-one
title: 容器名不应自动追加 -1 后缀
status: captured
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-14 09:07:45
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
iteration: null
openspec_changes: []
lifecycle:
  captured: '2026-09-14 09:05:04'
  generated: null
  completed: null
  reviewed: null
  approved: null
related_requirement: null
related_bug: null
related_change: null
captured_via: capture
classification_rationale: 用户描述“容器名不要加 -1”，属于现有 Docker/Compose 命名表现与期望不一致，按缺陷采集。
severity: medium
---

# BUG-0017-compose-container-name-suffix-one Trace

## 来源与范围

来源为用户本次 `/capture` 输入。该条记录 Docker/Compose 容器命名偏差，根因未确认，未评审、未纳入 Sprint、未创建 OpenSpec Change。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 09:05:04 | /capture | 创建采集记录，初判 medium；用户反馈容器名后缀与期望不一致，按 BUG 采集。 |
