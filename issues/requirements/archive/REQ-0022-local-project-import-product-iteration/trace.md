---
requirement_id: REQ-0022-local-project-import-product-iteration
status: done
created_at: 2026-08-19 15:24:24
updated_at: 2026-09-14 09:01:01
lifecycle:
  captured: 2026-08-19 15:24:24
  generated: 2026-09-11 08:34:54
  completed: 2026-09-11 08:44:50
  reviewed: 2026-09-11 08:48:13
  approved: 2026-09-11 08:48:13
iteration: sprint-005
openspec_changes:
  - change_id: add-local-project-governance-loop
    type: add
    status: archived
related_requirements:
  - REQ-0025-chat-workbench
  - REQ-0024-markdown-editor-human-edit-permission-matrix
  - REQ-0023-product-workbench-modern-ops-visual-system
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
  - docs/knowledge-base/retrospectives/sprint-003-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/archive/REQ-0022-local-project-import-product-iteration/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/archive/REQ-0022-local-project-import-product-iteration/prototype/web/context.md
    role: decomposition-and-contract-seed
prototype_gate:
  decomposition: done
  ui_skeleton: passed
  visual_acceptance_1440: passed
  req_final_consistency: passed
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, request_logs, usage_events, task_traces, task_trace_spans, agent_workflow, deployment]
  reason: 项目查询与成果应用新增跨页面请求及可恢复文件写入链路；DB 是否新增结构在设计时确定。
  validation: 已定义 AC-016 及权限、幂等、冲突和恢复验收；本次未运行产品验收。
lifecycle_stage: archive
related_change: add-local-project-governance-loop
priority: P1
---

# REQ-0022-local-project-import-product-iteration Trace

## 阅读摘要

- 任务入口返修：研发、测试、人工验收统一打开关联 tasks.md 并定位章节或任务；缺失明确提示，移除独立进度面板。

本文件是需求生命周期追踪；关联Change的实施、测试与返修细节保留在归档Change的trace.md。REQ已完成并归档，关联Change已归档到 `openspec/archive/2026-09-14-add-local-project-governance-loop/`。需求中心所有卡片只展示所属REQ/BUG的trace.md；Change实施记录不作为卡片trace入口。

## 当前状态

- 状态：done
- 优先级：P1
- 阶段：archive
- 关联 Sprint：sprint-005
- 关联 Change：add-local-project-governance-loop（archived，已归档）

## Readiness Report

| 项 | 结果 | 说明 |
|---|---|---|
| Readiness | Archived | 实现、合成回归、真实闭环、刷新观察与归档同步均已有证据 |
| Knowledge-base gate | Pass | 前台工作台未命中后台四类标签；自愿复用弹窗与复盘经验，形成 3 条 AC-XCUT |
| Prototype Gate | Pass | Skeleton 已确认，主题/视口、完整动作族、computed style 与最终文档一致性已核验 |
| 下一步 | 无 | 已完成 /opsx-archive 并迁入 archive |

## Knowledge-base Cross-cutting Report

| 标签 | 引用 | AC 条数 |
|---|---|---:|
| 无后台标签；前台弹窗经验复用 | admin-modal-width-css-cascade.md | 2 |
| 前台保存失败与视觉复盘承接 | sprint-003-retrospective.md | 1 |

无上传、后台 CRUD 列表和独立表单，未引入其专属验收项。全部 AC 仍待产品实施验证。

## 文档一致性与风险

- 10 条故事映射全部 FR，16 条功能 AC、3 条横切 AC、6 条原型 AC；单项目与受控应用范围一致。
- capture 保留原始采集历史；当前范围与状态以 requirement 和本 trace 为准，不将原始问题误作全部未决。
- 尚未决定具体恢复实现和执行基准准备技术，作为 OpenSpec 设计输入；不构成本次需求文档缺项。
- UI 规则引用的 ui-design/ui-design.md 当前未找到；评审采用现行 rules/ui-design.md 与共享工作台样式。建议治理维护时核对引用，不自动创建跟进项。
- 无业务代码、OpenSpec、Sprint 或真实部署变更；无产品行为通过声明。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-14 08:59:54 | /opsx-archive | Change `add-local-project-governance-loop` 已归档，状态同步完成。 |
| 2026-09-11 14:50:03 | /opsx-modify | Change `add-local-project-governance-loop` 验收返修已同步，待复验或 archive。 |
| 2026-09-11 10:49:09 | /opsx-apply | Change `add-local-project-governance-loop` apply 完成，待 archive。 |
| 2026-09-11 08:48:13 | req.review | 评审通过；保留基准准备、写入恢复、UI 证据与真实闭环交付门禁，尚未纳入 Sprint。 |
| 2026-09-11 08:44:50 | req.complete | 补齐故事、流程、25 条验收项及交互原型拆解；承接 Sprint-003 保存失败保留草稿、弹窗和证据经验；状态为 评审中。 |
| 2026-09-11 08:34:54 | req.generate | 生成单项目绑定、自动刷新及 Chat 治理成果受控应用的 MVP PRD；状态更新为 draft，未纳入 Sprint。 |
| 2026-08-19 15:24:24 | req.capture | 记录需求：本地存量项目导入 MoonBox 并支持产品内迭代闭环。 |

- 阶段迁移：plan → review（/req-review）

## REQ-0022 实施验证记录

当前 Change 的 22 项实现任务与 25 条 AC 已获得实施证据，真实闭环及连续 10 次刷新观察通过（2.807–3.826 秒）。UI 使用需求中心连接栏、Chat 关联栏项目状态与完整成果弹窗；原型保留离线 Mock 声明。API/数据库/观测/部署与客户端生成已同步，未自动归档或切换业务部署。详细报告见关联 Change 的 trace.md 与 evidence/。


## 看板返修一致性证据

需求中心已移除独立项目连接栏，保留同一授权绑定与刷新；验收态映射验收中。完整注册快照38条，34完成/4验收，阻塞0。返修视觉及样式证据见关联Change evidence/ui/modify-board-*；为仓库数据驱动的合成浏览器验收，当前业务部署尚未复验。REQ子文档及原型已同步，历史capture/review保持。
- 2026-09-14 08:59:42 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-local-project-governance-loop
