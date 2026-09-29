---
requirement_id: REQ-0028-chat-skill-codex
title: Chat 工作台支持多图片输入、仓库 Skill 快速引用与 Codex 截图基线体验增强
status: done
created_at: '2026-09-13 23:48:20'
updated_at: 2026-09-29 14:30:23
owner: 产品团队
source: internal
lifecycle_stage: archive
iteration: sprint-006
openspec_changes:
  - change_id: add-chat-workbench-image-skill-context
    type: add
    status: archived
lifecycle:
  captured: '2026-09-13 23:48:20'
  generated: 2026-09-14 11:04:42
  completed: 2026-09-14 23:17:57
  reviewed: 2026-09-14 23:31:15
  approved: 2026-09-14 23:31:15
parent_requirement: REQ-0025-chat-workbench
related_requirements:
  - REQ-0025-chat-workbench
  - REQ-0029-capture-multimodal-candidate-review
  - REQ-0035-chat-agent-model-reasoning-selector
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-005-retrospective.md
cross_cutting_tags:
  - media-upload
prototype_refs:
  - path: issues/requirements/review/REQ-0028-chat-skill-codex/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0028-chat-skill-codex/prototype/web/context.md
    role: decomposition
  - path: user-provided-image-1
    role: reference-screenshot
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
ui_reference_replication:
  mode: local_consistency
  source_priority:
    - user-provided-image-1
    - issues/requirements/review/REQ-0028-chat-skill-codex/prototype/web/context.md
    - issues/requirements/review/REQ-0028-chat-skill-codex/acceptance.md
    - rules/ui-design.md
    - existing-chat-workbench
  non_goals:
    - 不复刻截图中的历史命令文本、耗时、文件链接、账号信息或本机临时路径。
    - 不牺牲 MoonBox 共享导航、空间权限、会话历史、轨迹详情和 OpenSpec 治理边界。
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web_request_wrapper
    - api
    - db
    - object_storage
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 多图片上传、Skill 候选读取、Skill 上下文引用和本轮发送会影响 Web 请求封装、API 字段、可能的持久化结构、对象存储、行为事件、请求日志和 Codex 执行 Task Trace。
  validation: 后续 OpenSpec 和实现阶段需验证图片和 Skill 引用只记录脱敏标识、数量、大小、类型、来源摘要和处理结果；请求日志与 Task Trace 不保存完整图片、完整 Prompt、完整回复、完整 Diff、密钥、凭证、本机绝对路径或真实客户敏感数据；观测失败不阻断主流程但保留脱敏降级摘要。
readiness:
  status: ready
  knowledge_base_gate: pass
  prototype_gate: pass
related_change: add-chat-workbench-image-skill-context
priority: P1
---

# REQ-0028-chat-skill-codex Trace

## Readiness Report

| 项 | 结论 | 说明 |
|---|---|---|
| 文档包 | Ready | `requirement.md`、`user-stories.md`、`business-flow.md`、`acceptance.md`、`trace.md` 已齐。 |
| Knowledge-base gate | Pass | 命中 `media-upload`，已读取并转化上传横切 AC；已引用 prototype-driven UI gate。 |
| Prototype Gate | Pass | 已补齐 `prototype/web/context.md` 和 `prototype/web/prototype.html`，并记录 UI Reference Contract 种子。 |
| 观测声明 | Pass | 已声明 Web、API、DB、对象存储、行为事件、请求日志、Task Trace 和流程节点适用。 |

## Knowledge-base Cross-cutting Report

| 标签 | 引用文档 | 写入 acceptance 的 AC 条数 |
|---|---|---:|
| media-upload | docs/knowledge-base/best-practices/admin-media-upload-chain.md | 6 |
| prototype-ui | docs/knowledge-base/best-practices/prototype-driven-ui-gate.md | 4 |
| sprint-retro | docs/knowledge-base/retrospectives/sprint-005-retrospective.md | 2 |

## UI Reference Replication Contract Seed

| 项 | 内容 |
|---|---|
| 保真模式 | 局部一致 / 风格迁移。以用户提供的 Image #1 作为对话区结果呈现参考，不逐像素复刻整页。 |
| 事实源优先级 | 用户提供 Image #1、prototype context、acceptance、MoonBox UI 规则、既有 Chat 工作台实现。 |
| 组件清单 | 页面壳、对话滚动区、右侧用户气泡、助手正文块、分节标题、链接式文件引用、状态摘要、下一步区、待处理区、图片预览条、Skill 引用 token、输入区、发送/停止动作。 |
| 动作按钮矩阵种子 | 图片添加、图片移除、图片重试、Skill 打开选择、Skill 移除、发送、停止；后续 Change design 需映射到 selector、状态和验收证据。 |
| 验收证据 | 后续 `/req-opsx` 和 `/opsx-apply` 需补 selector 映射、computed style 采样、1440px/窄屏/深浅主题截图、上传状态和 Skill 菜单交互证据。 |
| 非目标 | 不复制截图中的历史命令文本和本机临时路径；不取消现有轨迹详情、权限、Diff、历史和治理边界。 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-09-29 14:30:23 | /opsx-archive | Change `add-chat-workbench-image-skill-context` 已归档，状态同步完成。 |
| 2026-09-17 08:48:08 | /opsx-modify | Change `add-chat-workbench-image-skill-context` 验收返修已同步，待复验或 archive。 |
| 2026-09-15 00:11:31 | /opsx-apply | Change `add-chat-workbench-image-skill-context` apply 完成，待 archive。 |
| 2026-09-14 23:51:33 | /opsx-apply | Change `add-chat-workbench-image-skill-context` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 23:31:15 | /req-review | approved | 评审通过；下一步先纳入 Sprint，不直接创建 OpenSpec Change |
| 2026-09-14 23:25:00 | /req-complete | pending_review | REQ-0028-chat-skill-codex 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-14 23:17:57 | /req-complete | pending_review | 补齐用户故事、业务流程、验收、prototype context、UI Reference Contract 种子、横切 AC 和观测声明 |
| 2026-09-14 11:04:42 | /req-generate | draft | REQ-0028-chat-skill-codex 已生成 requirement.md，状态同步为 draft。 |
| 2026-09-14 11:04:09 | /req-generate | draft | 生成 requirement.md，收敛多图片输入、Skill 上下文引用与 Codex 截图基线体验增强范围 |
| 2026-09-13 23:48:20 | capture | captured | 需求中心创建并持久化 |

- 阶段迁移：plan → review（/req-review）
- 2026-09-29 14:30:23 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive REQ-0028-chat-skill-codex
