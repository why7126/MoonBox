---
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
title: 需求中心 Sprint 下拉列表新增状态展示
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:32:20
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
parent_requirement: REQ-0012-frontend-requirement-center
iteration: sprint-006
openspec_changes:
  - change_id: add-requirement-center-sprint-dropdown-status
    type: update
    status: archived
related_requirements:
  - REQ-0012-frontend-requirement-center
lifecycle:
  captured: '2026-09-14 09:05:04'
  generated: '2026-09-14 10:21:59'
  completed: '2026-09-14 14:50:40'
  reviewed: '2026-09-14 14:56:59'
  approved: '2026-09-14 14:56:59'
captured_via: capture
classification_rationale: 用户要求 Sprint 下拉列表新增状态字段，属于已有筛选/选择控件的信息展示增强。
knowledge_base_refs:
  - docs/knowledge-base/README.md
  - docs/knowledge-base/retrospectives/sprint-005-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/review/REQ-0032-requirement-center-sprint-dropdown-status/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0032-requirement-center-sprint-dropdown-status/prototype/web/context.md
    role: ui-decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  req_final_consistency: passed
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: 需求改变需求中心 Sprint 筛选下拉展示和选择体验，可能复用或扩展 Sprint 列表查询，需要保留选择、请求结果和异常降级的安全排障链路；不预期新增 DB、对象存储、Agent Workflow 或长耗时任务。
  validation: opsx-apply 已验证 Sprint 下拉打开、选择、状态缺失、OpenAPI/Orval 同步和安全摘要边界；未新增 DB、对象存储、后台任务或新的日志落库路径，不记录完整响应体、本机路径、密钥或无权对象。
related_change: add-requirement-center-sprint-dropdown-status
priority: P2
---

# REQ-0032-requirement-center-sprint-dropdown-status Trace

## 来源与范围

来源为用户本次 `/capture` 输入。该条记录 Sprint 下拉列表状态展示增强，当前已评审、已纳入 Sprint，并完成 OpenSpec Change 归档。

## Readiness

```yaml
readiness: Implemented
knowledge_base_gate: N/A
prototype_gate: Apply Evidence Ready
reason: 需求主文档、用户故事、业务流程、验收标准、trace 扩写和 web 原型均已补齐；opsx-apply 已完成 UI Skeleton、真实浏览器视觉证据、computed style 采样、API 文档和测试验证，最终验收已在归档链路回填。
status: done
lifecycle:
  completed: 2026-09-14 14:53:46
  reviewed: 2026-09-14 14:56:59
  approved: 2026-09-14 14:56:59
  status: done
  stage: archive
  iteration: sprint-006
  related_change: add-requirement-center-sprint-dropdown-status
openspec_changes:
  - change_id: add-requirement-center-sprint-dropdown-status
    type: update
    status: archived
```

## 评审摘要

```yaml
review_id: REV-REQ-0032-001
result: approved
reviewed_at: 2026-09-14 14:56:59
next: closed
```

## 知识库承接摘要

本需求为 web-catalog 需求中心筛选下拉增强，不命中 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 四类横切标签，因此不写 AC-XCUT。已读取 `docs/knowledge-base/README.md` 与最近一期 `docs/knowledge-base/retrospectives/sprint-005-retrospective.md`，承接“需求中心卡片和控件展示必须事实源优先，不能依赖前端临时推断”的经验，已写入状态事实源、异常降级、观测和验收项。

## 文档包

| 文件 | 状态 | 说明 |
|---|---|---|
| capture.md | captured | 用户原始反馈与初步范围。 |
| requirement.md | done | PRD 主文档。 |
| user-stories.md | done | 用户故事与验收要点。 |
| business-flow.md | done | 主流程、状态解析、异常与权限流程。 |
| acceptance.md | done | 功能、UI、原型、观测和知识库检查。 |
| prototype/web/context.md | done | 原型拆解。 |
| prototype/web/prototype.html | done | 静态 HTML 原型。 |

## 实现验证摘要

| 类型 | 结论 | 证据 |
|---|---|---|
| 后端事实源 | Sprint 选项状态由 `iterations/change` 与 `iterations/archive` 的 Sprint 事实源派生，非法或冲突状态降级为“状态待核实”。 | `tests/integration/api/test_requirement_center.py` |
| 前端展示 | Sprint 筛选下拉展示状态徽标，并保持多选筛选、搜索、刷新和项目切换兼容；加入迭代弹窗复用状态映射。 | `src/web/src/requirement-center.test.tsx` |
| API 合约 | `sprint_option_details` 已同步 OpenAPI、Orval 客户端和 API 文档，旧 `sprint_options` 保留。 | `src/web/openapi.json`、`src/web/src/api/generated/governance.ts`、`docs/03-api-index.md` |
| UI 证据 | 已采集 1440px 深色主题、390px 浅色窄屏和 computed style。 | `openspec/archive/2026-09-17-add-requirement-center-sprint-dropdown-status/evidence/ui/` |
| 观测安全 | 未新增 DB、对象存储、后台任务、Task Trace 或新的日志落库路径；warning 仅保留脱敏摘要。 | `openspec/archive/2026-09-17-add-requirement-center-sprint-dropdown-status/test-plan.md` |

## 归档前最终一致性检查

| 检查项 | 结论 | 证据 |
|---|---|---|
| requirement / acceptance / prototype | passed | REQ 文档、验收项和 `prototype/web/context.md` 均聚焦 Sprint 下拉状态展示，不要求重做筛选体系或新增归档能力。 |
| Change 设计与实现 | passed | `openspec/archive/2026-09-17-add-requirement-center-sprint-dropdown-status/design.md`、`trace.md`、`acceptance.md` 与实现证据一致。 |
| 视觉与返修证据 | passed | 1440px 视觉证据存在；验收返修删除重复“已完成 / 归档”筛选控件并修正下拉间距，未改变需求主目标。 |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:31:31 | /opsx-archive | Change `add-requirement-center-sprint-dropdown-status` 已归档，状态同步完成。 |
| 2026-09-17 08:30:53 | /opsx-archive | 归档前 REQ 最终一致性检查通过，prototype_gate.req_final_consistency 更新为 passed。 |
| 2026-09-14 18:17:46 | /opsx-modify | Change `add-requirement-center-sprint-dropdown-status` 验收返修已同步，已完成复验并归档。 |
| 2026-09-14 15:38:32 | /opsx-apply | Change `add-requirement-center-sprint-dropdown-status` apply 完成，已归档。 |
| 2026-09-14 15:36:27 | /opsx-apply | 完成 Sprint 下拉状态展示实现、API 合约同步、自动化测试、视觉证据和 Change 验收文档回填；工作流最终同步已完成。 |
| 2026-09-14 15:21:10 | /opsx-apply | Change `add-requirement-center-sprint-dropdown-status` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 15:08:00 | /req-opsx | 创建 OpenSpec Change add-requirement-center-sprint-dropdown-status，状态最终为 archived。 |
| 2026-09-14 15:01:06 | /sprint-propose | 正式纳入 sprint-006；后续已创建 OpenSpec Change 并完成归档。 |
| 2026-09-14 14:56:59 | /req-review | 需求评审通过，评审通过；后续已纳入 Sprint、创建 Change 并完成归档。 |
| 2026-09-14 14:53:46 | /req-complete | REQ-0032-requirement-center-sprint-dropdown-status 已完成文档补齐，状态曾同步为待评审，后续已完成归档。 |
| 2026-09-14 14:50:40 | /req-complete | 补齐用户故事、业务流程、验收标准、trace 扩写和 web 原型，状态曾推进为待评审，后续已完成归档；知识库横切标签无匹配，承接 sprint-005 事实源优先经验。 |
| 2026-09-14 10:21:59 | /req-generate | 生成 requirement.md，状态曾从 captured 同步为草稿，后续已完成归档。 |
| 2026-09-14 09:05:04 | /capture | 创建采集记录，初判 P2；按控件信息展示增强独立拆分。 |

- 阶段迁移：plan → review（/req-review）
- 2026-09-17 08:31:31 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-requirement-center-sprint-dropdown-status
