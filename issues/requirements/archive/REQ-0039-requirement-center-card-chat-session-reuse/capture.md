---
requirement_id: REQ-0039-requirement-center-card-chat-session-reuse
title: 需求中心卡片动作复用对象会话
status: done
created_at: '2026-09-16 23:39:30'
updated_at: 2026-10-06 00:21:08
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0027-requirement-center-command-chain-realization
previous_requirement_id: REQ-0039-test
captured_via: req-capture
classification_rationale: 用户描述的是需求中心卡片按钮触发 Chat 时的目标会话复用策略和生成类治理动作候选创建策略，属于需求中心与 Chat 工作台协同体验增强；未提供现有线上故障证据，按需求记录。
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: 需求会影响需求中心卡片按钮触发 Chat 的对象会话查询、新建与治理动作候选生成链路，涉及 Web 行为入口、后端请求日志和治理动作执行链路；本 capture 阶段仅记录范围，不落地接口或数据结构。
  validation: 后续 PRD 与 OpenSpec 需声明会话复用查询、未归档未删除过滤、生成类 candidate 新建、turn 追加和观测字段的验证方式。
priority: P1
---

# 需求中心卡片动作复用对象会话

## 原始描述

需求中心卡片动作复用同一对象会话：同一个 REQ、BUG 或 Change 通过需求中心卡片按钮触发 Chat 时，应优先进入该对象最近的未归档、未删除会话；存在多个会话时使用最新会话；不存在时才新建。生成类治理动作进入同一会话但创建新的治理候选和 turn，不复用旧 candidate。

## 背景

需求中心卡片动作正在从只读分析和治理命令入口，演进为能承载 Chat 对话、候选生成、文件事实源写入和 Workflow Sync 的完整产品链路。若同一对象每次触发卡片动作都新建 Chat，会割裂上下文、降低复盘可追溯性；若生成类动作复用旧 candidate，又会混淆每次治理动作的候选结果。

## 目标

- 同一个 REQ、BUG 或 Change 从需求中心卡片按钮触发 Chat 时，优先进入该对象最近的未归档、未删除会话。
- 同一对象存在多个可用会话时，按最近更新时间或等价事实源选择最新会话。
- 同一对象不存在可用会话时，才创建新的 Chat 会话并建立对象关联。
- 生成、完善、评审、入迭代、生成 OpenSpec 等生成类治理动作可进入同一对象会话，但每次动作必须创建新的治理候选和新的 turn。
- 旧 candidate 不被静默复用；历史 candidate 仅作为历史上下文或可追溯记录。

## 非目标

- 本记录不绕过 REQ、BUG、Change 的评审、Sprint、OpenSpec 或归档门禁。
- 本记录不直接修改 `src/`、`openspec/`、Sprint 四件套或数据库结构。
- 本记录不定义完整 Chat 工作台能力；对象会话、消息、候选和观测字段的详细契约留待后续 PRD 与 OpenSpec。

## 重复/相似检查

- 与 `REQ-0027-requirement-center-command-chain-realization` 相似：同属需求中心卡片命令产品链路真实化。本条按用户指定沿用 `REQ-0039`，作为 `REQ-0027` 下的会话复用与 candidate 新建策略细化记录。
- 与 `REQ-0025-chat-workbench` 相关：复用 Chat 工作台会话能力，但本条聚焦需求中心对象卡片入口，不替代 Chat 工作台主需求。

## 待澄清

- [ ] “最近会话”的排序事实源使用最近消息时间、最近 turn 时间还是会话 `updated_at`。
- [ ] 未归档、未删除会话的过滤字段与对象关联关系由前端、后端还是 Workflow Sync 派生提供。
- [ ] 生成类治理动作的新 candidate 与新 turn 是否需要幂等键，避免重复点击产生重复候选。
- [ ] REQ、BUG、Change 三类对象的会话复用权限、归档态提示和异常降级文案。

## 探索结论

（/req-explore 后人工确认写入）
