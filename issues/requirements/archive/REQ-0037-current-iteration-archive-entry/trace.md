---
requirement_id: REQ-0037-current-iteration-archive-entry
title: 当前迭代容量区域新增归档当前迭代入口
status: done
created_at: '2026-09-14 23:15:32'
updated_at: 2026-09-17 10:24:46
recorded_by: product
source: 用户反馈
parent_requirement: REQ-0031-requirement-center-current-iteration-capacity
lifecycle_stage: archive
iteration: sprint-007
openspec_changes:
  - change_id: add-current-iteration-archive-entry
    type: add
    status: archived
related_requirements:
  - REQ-0031-requirement-center-current-iteration-capacity
lifecycle:
  captured: '2026-09-14 23:15:32'
  generated: '2026-09-14 23:31:06'
  completed: '2026-09-14 23:35:53'
  reviewed: '2026-09-14 23:41:21'
  approved: '2026-09-14 23:41:21'
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-005-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/archive/REQ-0037-current-iteration-archive-entry/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/archive/REQ-0037-current-iteration-archive-entry/prototype/web/context.md
    role: ui-decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: done
  req_final_consistency: done
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: 当前需求新增 Web 端高风险归档入口和确认流程，涉及入口点击、权限拒绝、门禁检查、归档执行请求、Sprint archive 多步骤写操作和 Workflow Sync 结果刷新。
  validation: req-complete 已补齐行为事件、请求日志、Task Trace、权限、安全和 Workflow Sync 失败验收项；OpenSpec 阶段需继续声明复用或补齐的观测链路，验证不记录完整文档正文、本机路径、Authorization、Cookie、密钥、真实 .env 或未脱敏错误堆栈。
related_change: add-current-iteration-archive-entry
priority: P1
---

# REQ-0037-current-iteration-archive-entry Trace

## 来源与范围
用户通过 `/req-capture` 授权记录。当前已完成需求评审并通过，已纳入 `sprint-007`；OpenSpec Change `add-current-iteration-archive-entry` 已创建、实施并归档。

## 需求补齐摘要

- Readiness: Ready
- Knowledge-base gate: N/A（未命中管理端横切标签；已引用原型驱动 UI Gate 和 Sprint-005 需求中心动作族经验）
- Cross-cutting tags: []
- Prototype Gate: Pass（已提供 `prototype/web/context.md` 和 `prototype/web/prototype.html`；1440px 视觉证据已在实施阶段补齐）
- 关联父需求：REQ-0031-requirement-center-current-iteration-capacity

## 知识库承接

| 来源 | 承接方式 |
|---|---|
| docs/knowledge-base/best-practices/prototype-driven-ui-gate.md | 在 acceptance.md 写入 AC-PROTOTYPE-001~004，并在 trace 记录 prototype_refs 与 prototype_gate。 |
| docs/knowledge-base/retrospectives/sprint-005-retrospective.md | 承接“动作按钮与执行能力分离”“事实源优先”“视觉证据覆盖状态组合”，写入门禁、权限、观测和测试验收。 |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 10:24:46 | /opsx-archive | Change `add-current-iteration-archive-entry` 已归档，状态同步完成。 |
| 2026-09-15 08:35:49 | /opsx-modify | 验收返修：CapacityItem 改为桌面三列、390px 安全堆叠；状态 badge 左置并提供容量来源/说明 title；归档 icon button 去边框并保留 readiness title。 |
| 2026-09-15 08:24:01 | /opsx-modify | Change `add-current-iteration-archive-entry` 验收返修已同步，后续已完成归档。 |
| 2026-09-15 08:22:45 | /opsx-modify | 验收返修：当前迭代容量条归档入口改为 icon-only，状态 badge 保留在卡片右上角，readiness 长摘要改为 hover/title；补充 1440px/390px 视觉证据。 |
| 2026-09-15 00:43:06 | /opsx-apply | Change `add-current-iteration-archive-entry` apply 完成，后续已完成归档。 |
| 2026-09-15 00:39:03 | /opsx-apply | 实现当前迭代容量条归档入口、Sprint archive readiness 安全摘要、确认弹窗、OpenAPI/Orval 同步和 1440px/390px 视觉证据；真实归档执行继续复用 /sprint-archive 门禁。 |
| 2026-09-15 00:20:09 | /opsx-apply | Change `add-current-iteration-archive-entry` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-15 00:14:27 | /req-opsx | 创建 OpenSpec Change `add-current-iteration-archive-entry`；后续已执行 /opsx-apply。 |
| 2026-09-15 00:06:29 | /sprint-propose | 纳入 sprint-007，估算 M / 3 人天；后续已执行 /req-opsx。 |
| 2026-09-14 23:51:28 | /explore follow-up | 补充 UI 口径：归档入口启用状态必须基于 Sprint archive readiness 汇总；范围内任一 REQ、BUG 或独立 Change 未归档闭环时，入口隐藏或禁用并展示安全摘要。 |
| 2026-09-14 23:41:21 | /req-review | 评审通过，状态推进为 approved；下一步为 /sprint-propose --req REQ-0037-current-iteration-archive-entry。 |
| 2026-09-14 23:39:19 | /req-complete | REQ-0037-current-iteration-archive-entry 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-14 23:35:53 | /req-complete | 补齐 user-stories、business-flow、acceptance 与 Web prototype，状态推进为 pending_review；无管理端横切标签，原型驱动 UI Gate 已写入验收。 |
| 2026-09-14 23:32:22 | /req-generate | REQ-0037-current-iteration-archive-entry 已生成 requirement.md，状态同步为 draft。 |
| 2026-09-14 23:31:06 | /req-generate | 生成 requirement.md，状态推进为 draft；保留当前迭代容量区域归档入口、确认流程、Sprint archive 门禁复用、权限和观测要求。 |
| 2026-09-14 23:15:32 | /req-capture | 单条记录当前迭代容量区域归档入口需求，初判 P1，关联当前迭代容量展示父需求。 |

- 阶段迁移：plan → review（/req-review）
- 2026-09-17 10:24:34 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-current-iteration-archive-entry
