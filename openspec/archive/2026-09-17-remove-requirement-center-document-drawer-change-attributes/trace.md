---
change_id: remove-requirement-center-document-drawer-change-attributes
title: 需求中心文档抽屉移除 Change 属性模块 - Trace
type: update
status: applied
created_at: 2026-09-15 23:32:00
updated_at: 2026-09-16 08:45:49
source_requirement: REQ-0036-requirement-center-document-drawer-simplification
source_sprint: sprint-007
affected_specs:
  - web-catalog-requirement-center
prototype_refs:
  - issues/requirements/review/REQ-0036-requirement-center-document-drawer-simplification/prototype/web/context.md
  - issues/requirements/review/REQ-0036-requirement-center-document-drawer-simplification/prototype/web/prototype.html
prototype_gate:
  decomposition: done
  ui_contract: done
  ui_skeleton: done
  visual_acceptance_1440: pass
  computed_style_evidence: pass
  mock_api_boundary: declared_no_api_change
  req_final_consistency: pass
product_data_collection_observability:
  status: not_applicable
  affected_layers:
    - web
  reason: 本 Change 只调整需求中心 Web 文档抽屉展示与入口组织，复用现有文档读取、权限、请求封装、日志审计、行为采集、Task Trace 和对象存储链路；不新增或修改 API、DB、请求日志字段、行为事件、Task Trace、对象存储或客户端请求封装。
  validation: 已通过 synthetic API + 真实 Web bundle 的 Playwright 视觉验收、computed style 检查、需求中心聚焦 Vitest 与 TypeScript 编译；本 Change 未新增 API、DB、OpenAPI、Orval、请求封装、埋点或对象存储变更。
validation:
  openspec_validate: pass
  workflow_sync: pass
  language_check: pass
  title_check: pass
  change_identity: pass
  sprint_scope: pass
  focused_frontend_test: pass
  typescript_check: pass
  visual_evidence: pass
execution:
  schema_version: 1
  started_at: 2026-09-15 23:37:28
  completed_at: 2026-09-15 23:46:17
  last_event: opsx.apply
---

# 需求中心文档抽屉移除 Change 属性模块 - Trace

## 来源

- REQ：`REQ-0036-requirement-center-document-drawer-simplification`
- Sprint：`sprint-007`
- Change 类型：`update`

## Conflict Resolution

`prototype/web/prototype.html` 和 `prototype/web/context.md` 是 UI Skeleton 输入；最终验收以 Change design、delta spec、REQ acceptance、1440px/关键交互视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-15 23:32:00 | /req-opsx | 创建 OpenSpec Change，生成 proposal、design、spec delta、tasks 和 trace 初稿。 |

| 2026-09-15 23:44:29 | /opsx-apply | 删除文档抽屉内 Change 属性模块，保留卡片侧抽屉外 Change 文档入口；完成前端测试、TypeScript 与 Playwright 视觉证据。 |
| 2026-09-16 08:15:51 | /opsx-modify | 验收返修：卡片关联 Change 文档入口改为直接紧凑文档入口，去除卡片完整 Change ID 展开；详见 `acceptance-fixes.md`。 |
| 2026-09-16 08:28:10 | /opsx-modify | 验收返修：移除额外 `Change 文档` / `更多` 弹层，关联 Change 的 tasks/spec/design/proposal/trace 直接作为紧凑文档入口展示；详见 `acceptance-fixes.md`。 |
| 2026-09-16 08:45:49 | /opsx-modify | 验收返修：卡片文档入口跨 Issue 与关联 Change 按文件名和语义去重，保留 Issue trace 与 Change trace 短文案区分；详见 `acceptance-fixes.md`。 |

## 验证记录

- 实现范围：`src/web/src/pages/catalog/RequirementCenterPage.tsx` 删除 Markdown 抽屉内 `Change 追溯属性` 条件渲染分支；返修后卡片只保留直接紧凑文档入口，用 `Change 1`、`Change 2` 短前缀打开关联 Change trace，并按文件名和语义对同名文档入口去重，保留 `current_change`、`related_changes`、`task_progress`、`warnings`、`drift_warnings`、`document_entries` 字段读取。
- 聚焦前端测试：`cd src/web && ./node_modules/.bin/vitest run src/requirement-center.test.tsx`，106 tests passed。
- TypeScript：`cd src/web && ./node_modules/.bin/tsc -b`，通过。
- 视觉证据：`openspec/archive/2026-09-17-remove-requirement-center-document-drawer-change-attributes/evidence/ui/`，synthetic API + 真实 Web bundle；覆盖深色 1440px、浅色 1440px、深色 390px，并复验同名文档入口去重。
- 截图：`drawer-requirement-*` 覆盖普通 REQ 文档和文档属性展开态；`drawer-related-change-*` 覆盖多 Change 关联文档入口；`drawer-standalone-change-*` 覆盖独立 Change 文档。
- computed style：`evidence/ui/computed-style.json`；记录 `changeModuleCount=0`、文档属性区 `padding`、`border`、`gap`、`font-size`、`line-height`、正文顶部间距和抽屉滚动容器 `overflow`。
- Mock/API 边界：使用合成 API 响应验证真实前端组件；本 Change 未新增 API 字段、OpenAPI、Orval、请求封装、DB、埋点、Task Trace 或对象存储变更。
- 权限与安全：未修改后端聚合、文档 URL 生成、鉴权、保存策略或直接文档读取路径；前端测试覆盖 `trace.md` 只读、非 `capture.md` 保存阻断、脏数据保护和读取失败保留。
- REQ 最终一致性：`requirement.md`、`acceptance.md`、`trace.md` 与 Change 的“删除抽屉内模块、保留抽屉外入口”范围一致。


## 验收返修记录

- R1 台账：`acceptance-fixes.md`。
- 用户反馈：卡片只保留紧凑文档入口，不在卡片上展开完整 Change ID；关联 Change 文档入口改为直接紧凑文档入口，并保留 Issue trace 与 Change trace 可区分。
- 调整结果：卡片不再显示 `.rc-change-id-row`；关联 Change 文档入口收敛为直接紧凑文档入口；Issue trace 仍显示 `trace.md`，Change trace 显示 `Change trace.md`。
- 验证：需求中心聚焦 Vitest、TypeScript、Playwright 视觉证据均通过；`evidence/ui/` 已刷新。

- R2：移除额外 `Change 文档` / `更多` 弹层，保留 `Change 1 Change trace.md` 等直接短文档入口；视觉证据已刷新。
- R3：Issue 自身文档与关联 Change 文档合并展示时按文件名和语义去重，`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 不重复出现；Issue trace 保持 `trace.md`，Change trace 保持 `Change 1 Change trace.md`、`Change 2 Change trace.md`。
