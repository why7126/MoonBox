---
requirement_id: REQ-0041-remove-capture-draft-binding-check
title: 移除新建 Capture 草稿的项目绑定版本校验追溯记录
status: draft
created_at: '2026-10-05 23:30:19'
updated_at: 2026-10-08 23:03:55
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0029-capture-multimodal-candidate-review
related_requirements:
  - REQ-0029-capture-multimodal-candidate-review
iteration: null
openspec_changes: []
lifecycle:
  captured: '2026-10-05 23:30:19'
  generated: 2026-10-08 23:03:55
  completed: null
  reviewed: null
  approved: null
product_data_collection_observability:
  status: applicable
  affected_layers:
    - api
    - db
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 草稿恢复、确认及失败续作的绑定版本门禁变化涉及 API、持久化版本字段与多步骤任务；当前未计划改行为事件或 Web 请求封装，二者暂为 N/A。
  validation: 后续 PRD 与 Change 核对旧草稿跨绑定版本的恢复、授权、请求错误码、任务恢复与脱敏链路摘要；本次仅 capture，未执行实现验证。
priority: P1
---

# 移除新建 Capture 草稿的项目绑定版本校验追溯记录

## 来源与范围

用户在 `/explore` 后选择“完全删除校验”，并确认新增关联 REQ。目标是移除 Capture 草稿链路的绑定版本一致性门禁，同时保留当前用户和项目的授权、对象归属及写入一致性约束。已生成 PRD 草稿；尚未评审、纳入 Sprint 或创建 OpenSpec Change。

## 重复检查

| 候选 | 状态 | 相似原因 | 处理结论 |
|---|---|---|---|
| REQ-0029-capture-multimodal-candidate-review | done / archive | 已交付 Capture 草稿与项目绑定校验 | 用户选择另立关联需求，保留已归档事实，记录反向策略变更 |
| REQ-0038-capture-md | captured / plan | 同为 Capture 弹窗 | 只涉及编辑器材料输入，不覆盖绑定版本策略 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-08 23:03:55 | /req-generate | REQ-0041-remove-capture-draft-binding-check 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-05 23:30:19 | req.capture | captured | 用户确认新增关联 REQ，记录完全删除 Capture 草稿绑定版本一致性校验的需求。 |
