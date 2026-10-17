---
requirement_id: REQ-0043-unify-data-mount-and-snapshot-rotation
title: 统一 data 目录边界与本地数据挂载及快照轮转追溯记录
status: done
created_at: '2026-10-08 14:09:07'
updated_at: 2026-10-08 17:44:19
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
captured_via: req-capture
related_requirements:
  - REQ-0025-chat-workbench
iteration: sprint-009
openspec_changes:
  - change_id: add-local-data-mount-and-snapshot-rotation
    type: add
    status: archived
lifecycle:
  captured: '2026-10-08 14:09:07'
  generated: '2026-10-08 14:10:35'
  completed: '2026-10-08 14:19:59'
  reviewed: '2026-10-08 14:25:36'
  approved: '2026-10-08 14:25:36'
product_data_collection_observability:
  status: applicable
  affected_layers:
    - db
    - task_traces
    - task_trace_spans
  reason: 本地业务库挂载、自动快照与删除恢复属于 DB 持久化和 Agent Workflow 维护链路；当前仅规划后台运维配置，没有新增 API、Web/管理端按钮或请求封装，因此 request_logs、usage_events 与客户端请求层为 N/A，后续若增加管理入口再评估。
  validation: 后续 PRD、Change 与验收需核对数据库连接与目录、轮转及异常的脱敏任务记录、删除恢复链路和 SQLite/MySQL 边界；本次 capture 未运行产品行为验证。
knowledge_base_refs:
  - docs/knowledge-base/retrospectives/sprint-007-retrospective.md
cross_cutting_tags: []
related_change: add-local-data-mount-and-snapshot-rotation
priority: P1
---

# 统一 data 目录边界与本地数据挂载及快照轮转追溯记录

## 来源与范围

来源为用户连续 `/explore` 后的明确选择和本次 `/req-capture` 指令。PRD、用户故事、业务流程和验收清单已齐，需求评审通过；已纳入 sprint-009，并创建 OpenSpec Change `add-local-data-mount-and-snapshot-rotation`。

## 知识库横切结论

本需求属于数据库、部署和本地备份治理，没有管理端列表、表单、弹窗或媒体上传，也无原型，因此 UI best-practices 标签与横切 AC 为 N/A。参照 sprint-007 复盘的证据分层和 legacy runtime 迁移经验，验收清单分别设置 SQLite/MySQL、挂载、迁移、恢复与文档门禁。

## 产品数据采集与链路观测

依据 `docs/standards/product-data-collection-observability.md`，适用层级为 DB、Task Trace、Task Trace span。迁移、轮转和恢复属后台任务；本需求不新增 HTTP 入口，不伪造行为事件或请求日志。后续 Change 需要核对真实实现的层级、脱敏字段及异常降级；若设计新增 API 或页面入口，再补齐 request_logs、usage_events 和客户端请求封装验证。

## 重复检查

| 候选 | 状态 | 相似原因 | 处理结论 |
|---|---|---|---|
| REQ-0025-chat-workbench | done / archive | 已交付 Chat 与 Codex 执行入口及本地备份基础能力 | 本需求新增统一挂载和快照轮转的独立验收闭环，作为相关需求 |
| REQ-0042-agent-runtime-version-space-isolation | captured / plan | 同涉及 Agent 运行目录 | 其目标是环境版本与多空间隔离，不覆盖业务库路径及备份轮转 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-08 17:44:19 | /opsx-archive | Change `add-local-data-mount-and-snapshot-rotation` 已归档，状态同步完成。 |
| 2026-10-08 15:48:57 | /opsx-apply | Change `add-local-data-mount-and-snapshot-rotation` apply 完成，待 archive。 |
| 2026-10-08 15:03:39 | /opsx-apply | Change `add-local-data-mount-and-snapshot-rotation` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-08 14:45:47 | /opsx-apply | Change `add-local-data-mount-and-snapshot-rotation` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-08 14:20:49 | /req-complete | REQ-0043-unify-data-mount-and-snapshot-rotation 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-08 14:11:19 | /req-generate | REQ-0043-unify-data-mount-and-snapshot-rotation 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-08 14:09:07 | req.capture | captured | 记录 data 目录、挂载、旧数据迁移与快照轮转需求。 |
| 2026-10-08 14:10:35 | req.generate | draft | 生成 PRD，明确配置、迁移、轮转及验收边界。 |
| 2026-10-08 14:19:59 | req.complete | pending_review | 补齐用户故事、业务流程和验收清单；知识库 UI 横切门禁为 N/A。 |
| 2026-10-08 14:25:36 | req.review | approved | 范围、验收、分级与观测门禁评审通过；后续先纳入 Sprint。 |

- 阶段迁移：plan → review（/req-review）
- 2026-10-08 17:44:19 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-local-data-mount-and-snapshot-rotation
