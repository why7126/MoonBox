---
requirement_id: REQ-0042-agent-runtime-version-space-isolation
title: 统一主源码目录与交付链路工作区及模块化执行架构追溯记录
status: done
created_at: '2026-10-06 21:29:24'
updated_at: 2026-10-29 16:26:13
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
captured_via: req-capture
related_requirements:
- REQ-0040-space-agent-model-reasoning-config
- REQ-0054-workspace-recovery-points
- REQ-0055-sprint-authorized-worktree-merge
iteration: sprint-015
openspec_changes:
- change_id: update-unified-workspace-runtime
  type: update
  status: archived
lifecycle:
  captured: '2026-10-06 21:29:24'
  generated: '2026-10-28 23:51:25'
  completed: 2026-10-29 00:03:33
  reviewed: '2026-10-29 06:42:52'
  approved: '2026-10-29 06:42:52'
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - db
  - agent_workflow
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  reason: 统一工作区、调度、看板投影与环境诊断影响执行和可观测链路。
  validation: 已补充 AC-DATA-001 至 004，待 Change 实施验证；文档完整性不代表产品验收。
priority: P1
knowledge_base_refs:
- docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
- docs/knowledge-base/retrospectives/sprint-013-retrospective.md
cross_cutting_tags:
- admin-modal
prototype_refs:
- path: prototype/web/prototype.html
  role: html-structure
- path: prototype/web/context.md
  role: decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: done
  req_final_consistency: done
readiness: Partially Ready
related_change: update-unified-workspace-runtime
---
# 统一主源码目录与交付链路工作区及模块化执行架构追溯记录

## 来源与范围

来源为用户本次 `/req-capture` 输入。当前已生成 PRD，尚未评审、纳入 Sprint 或创建 OpenSpec Change。

## 重复检查

| 候选 | 当前状态 | 相似原因 | 处理结论 |
|---|---|---|---|
| REQ-0040-space-agent-model-reasoning-config | captured | 同为空间级 Agent 能力 | 其目标是 Agent、模型及思考程度配置；本需求的运行环境版本和多空间隔离可独立验收，记录为相关需求 |
| REQ-0025-chat-workbench | done | 已交付聊天与 Codex 执行入口 | 本需求扩展运行基础设施，不重复创建聊天入口 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-29 13:03:50 | /opsx-archive | Change `update-unified-workspace-runtime` 已归档，状态同步完成。 |
| 2026-10-29 12:52:58 | /opsx-accept | Change `update-unified-workspace-runtime` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-10-29 12:49:12 | /opsx-apply | Change `update-unified-workspace-runtime` apply 完成，待 archive。 |
| 2026-10-29 08:35:16 | /opsx-apply | Change `update-unified-workspace-runtime` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-29 08:18:40 | /opsx-apply | Change `update-unified-workspace-runtime` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-29 00:03:33 | /req-complete | pending_review | REQ-0042-agent-runtime-version-space-isolation 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-28 23:54:03 | /req-generate | draft | REQ-0042-agent-runtime-version-space-isolation 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-06 21:29:24 | capture | captured | 创建 Agent 运行环境版本治理与多空间隔离需求。 |
| 2026-10-28 23:41:40 | req.capture | captured | 用户确认更新原需求，纳入主源码目录、链路级 worktree 与模块拆分；恢复点和合入流程拆分关联，未评审。 |
| 2026-10-28 23:51:25 | req.generate | draft | 生成 PRD，承接已确认方案与 moonbox- 模块命名；未创建需求子文档或开发产物。 |
| 2026-10-29 00:02:50 | req.complete | enriching | 补齐 FR/US/AC 映射及原型拆解；承接 Sprint 013 的真实证据分层、旧内容不可伪造、双库与恢复边界。 |
| 2026-10-29 06:42:52 | req.review | approved | 文档评审通过，P1；实现验收门禁保留，下一步 Sprint 规划。 |

## 完善结果

功能 AC 12 条、横切 AC 3 条、原型 AC 4 条、数据与观测 AC 4 条。知识库门禁通过；PNG 暂不要求，视觉与 Skeleton 待实现，Readiness 为 Partially Ready。产品验收未执行，无 Sprint 或 Change。
- 阶段迁移：plan → review（/req-review）


## OpenSpec 设计承接

已生成 `update-unified-workspace-runtime`，关联sprint-015；下一步 `/opsx-apply REQ-0042-agent-runtime-version-space-isolation`。当前无实施或验收完成事实。

## 最终实现验收同步

本需求实现和验证已完成，当前有效证据见 `openspec/archive/2026-10-29-update-unified-workspace-runtime/implementation-verification.md` 与该Change的逐AC验收报告。主工作区正式事实、交付工作区进度、恢复保护和迭代权限确认合入保持一致；未经确认不自动合入，合入不代替正式归档。
- 2026-10-29 13:03:50 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive update-unified-workspace-runtime
