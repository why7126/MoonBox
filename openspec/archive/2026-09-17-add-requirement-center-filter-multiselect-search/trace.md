---
change_id: add-requirement-center-filter-multiselect-search
source_requirement: REQ-0033-requirement-center-filter-multiselect-search
sprint: sprint-006
status: applied
created_at: 2026-09-14 15:05:58
updated_at: 2026-09-15 14:41:40
owner: product
execution:
  schema_version: 1
  started_at: 2026-09-14 15:20:37
  completed_at: 2026-09-14 15:29:40
  last_event: opsx.modify
---

# Trace

## Source

- Requirement: `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/requirement.md`
- Acceptance: `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/acceptance.md`
- Requirement trace: `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/trace.md`
- Sprint: `iterations/archive/sprint-006/`

## Prototype Source

- Decomposition: `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/prototype/web/context.md`
- HTML prototype: `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/prototype/web/prototype.html`

## Conflict Resolution

- Requirement authority: REQ-0033 PRD and acceptance define business goals, supported dimensions, combination semantics and non-goals.
- Spec authority: existing `web-catalog-requirement-center` and `web-catalog-requirement-center-real-data` specs define current lifecycle, data source, authorization and UI shell constraints.
- Implementation authority: current code decides exact component seams and whether object type stays segmented or becomes a dropdown, but it cannot weaken OR/AND semantics, permission boundaries or acceptance gates.
- If implementation requires new API fields, URL persistence, request wrapper changes or behavior events, update this Change before coding those changes.

## UI Contract / Skeleton Status

```yaml
prototype_gate:
  decomposition: done
  ui_contract: done
  ui_skeleton: done
  visual_acceptance_1440: pending_apply
  computed_style_evidence: pending_apply
  mock_api_boundary: declared_no_api_change_first
  req_final_consistency: pending_archive
```

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 首版 Change 仅增强前台需求中心筛选控件和客户端过滤组合，不新增或修改 API、数据库、请求日志、行为事件、Task Trace、请求封装、对象存储或 Agent Workflow。
validation: opsx-apply 需验证无 OpenAPI/Orval/API 文档差异、无新增请求日志字段、无新增行为事件和无 DB 迁移；若实现引入上述任一变化，必须改为 applicable 并补齐验证。
```

## Requirement Mapping

| REQ-0033 Acceptance | Change Artifact |
|---|---|
| AC-001, AC-002 | `specs/web-catalog-requirement-center/spec.md`, `tasks.md` 2.x |
| AC-003, AC-004 | `specs/web-catalog-requirement-center/spec.md`, `tasks.md` 3.x |
| AC-005, AC-006 | `design.md` UI Skeleton, `tasks.md` 3.x |
| AC-007 | `design.md` D3, `tasks.md` 3.4 |
| AC-008 | `tasks.md` 2.4 |
| AC-009, AC-010 | `specs/web-catalog-requirement-center-real-data/spec.md`, `tasks.md` 4.x |
| AC-UI-001 to AC-UI-006 | `design.md` UI Contract/Skeleton, `tasks.md` 5.x |
| AC-PROTOTYPE-001 to AC-PROTOTYPE-004 | `design.md`, `trace.md`, `tasks.md` 5.x/6.x |

## Validation Log

| Time | Command | Result |
|---|---|---|
| 2026-09-14 15:05 | `python scripts/validate-change-identity.py --new-id add-requirement-center-filter-multiselect-search` | pass |
| 2026-09-14 15:06 | `openspec new change add-requirement-center-filter-multiselect-search` | pass |
| 2026-09-14 15:09 | `openspec validate add-requirement-center-filter-multiselect-search --strict` | pass |
| 2026-09-14 15:09 | `python scripts/sync-workflow-status.py --event req.opsx --req REQ-0033-requirement-center-filter-multiselect-search --change add-requirement-center-filter-multiselect-search --sprint auto` | pass, warnings=0, blockers=0 |
| 2026-09-14 15:09 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event req.opsx --req REQ-0033-requirement-center-filter-multiselect-search --change add-requirement-center-filter-multiselect-search --sprint sprint-006 --json` | warning: usage_mode unavailable, sprint snapshot skipped because no command runs |
| 2026-09-14 15:12 | `python scripts/sync-workflow-status.py --event opsx.start --change add-requirement-center-filter-multiselect-search --sprint auto` | pass |
| 2026-09-14 15:24 | `pnpm --dir src/web test -- requirement-center.test.tsx` | blocked: Corepack pnpm cache missing local pnpm binary; used local Vitest binary instead |
| 2026-09-14 15:25 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` in `src/web` | pass, 84 tests |
| 2026-09-14 15:27 | Playwright 1440px visual and computed style capture on `/requirements?mock=workflow` | pass; evidence files under `openspec/archive/2026-09-17-add-requirement-center-filter-multiselect-search/evidence/` |
| 2026-09-14 23:20 | `python scripts/sync-workflow-status.py --event opsx.modify --change add-requirement-center-filter-multiselect-search --sprint auto --dry-run` | pass; sprint resolved to sprint-006; would update REQ acceptance_status pending |
| 2026-09-14 23:20 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` in `src/web` | pass, 93 tests |
| 2026-09-14 23:20 | `./node_modules/.bin/tsc -b` in `src/web` | pass |
| 2026-09-14 23:26 | Playwright 1440px visual and computed style capture on `/requirements?mock=workflow` | pass; `evidence/req-0033-modify-1440-level-popover.png` and `evidence/req-0033-modify-computed-style.json` show filter order, grouped grading, same-line labels and outside-click close |
| 2026-09-14 23:41 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` in `src/web` | pass, 94 tests |
| 2026-09-14 23:41 | `./node_modules/.bin/tsc -b` in `src/web` | pass |
| 2026-09-14 23:44 | Playwright 1440px visual and computed style capture on `/requirements?mock=workflow` | pass; `evidence/req-0033-modify-1440-sprint-unassigned.png` and `evidence/req-0033-modify-sprint-unassigned-style.json` show Sprint 全选包含“未纳入 Sprint” |
| 2026-09-15 08:54 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` in `src/web` | pass, 96 tests |
| 2026-09-15 08:54 | `./node_modules/.bin/tsc -b` in `src/web` | pass |
| 2026-09-15 09:05 | Playwright 1440px visual and computed style capture with intercepted authorized context | pass; `evidence/req-0033-modify-1440-sprint-default-summary.png` and `evidence/req-0033-modify-sprint-default-summary-style.json` show default Sprint trigger text `默认 Sprint 范围`, active filter count `0`, and manual Sprint change count `1` |
| 2026-09-15 09:08 | Change directory structure migration | pass; moved full acceptance fix ledger to root `acceptance-fixes.md`, kept `tasks.md` as checklist summary and `trace.md` as evidence entry |
| 2026-09-15 14:37 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` in `src/web` | pass, 96 tests |
| 2026-09-15 14:37 | `./node_modules/.bin/tsc -b` in `src/web` | pass |
| 2026-09-15 14:38 | Playwright 1440px visual and computed style capture on `/requirements?mock=workflow` | pass; `evidence/req-0033-modify-1440-filter-label-column-alignment.png` and `evidence/req-0033-modify-filter-label-column-alignment-style.json` show Sprint、分级、负责人、阶段摘要 `summaryLeft` 均为 `1103` |
| 2026-09-15 14:41 | `openspec validate add-requirement-center-filter-multiselect-search --strict` | pass |
| 2026-09-15 14:41 | `python scripts/validate-openspec-language.py --change add-requirement-center-filter-multiselect-search --residual-report` | pass; 当前 Change 中文校验通过，全仓残留分离报告无残留 |
| 2026-09-15 14:41 | `python scripts/sync-workflow-status.py --event opsx.modify --change add-requirement-center-filter-multiselect-search --sprint auto` | pass; Updated 3, Errors 0, acceptance pending |
| 2026-09-15 14:41 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change add-requirement-center-filter-multiselect-search --sprint sprint-006 --json` | warning; usage_mode unavailable, no command runs |

## Implementation Evidence

### Scope

- Frontend only: `src/web/src/pages/catalog/RequirementCenterPage.tsx`, `src/web/src/styles/globals.css`, `src/web/src/requirement-center.test.tsx`.
- API/DB/observability boundary: no OpenAPI, Orval generated client, backend schema/service, DB migration, request wrapper, request log, usage event, Task Trace or object storage change was introduced.
- Object type remains the existing segmented control; stage/status, owner, priority and Sprint use the new searchable multi-select dropdown.
- URL/local persistence remains non-goal; manual refresh, theme switch, drawer open/close and dropdown search preserve React filter state.

### Visual Evidence

| Evidence | Viewport | Summary |
|---|---:|---|
| `evidence/req-0033-1440-default.png` | 1440x900 | Default toolbar and 9-stage board render without overflow. |
| `evidence/req-0033-1440-sprint-popover.png` | 1440x900 | Sprint dropdown opens as toolbar popover with search, checkbox option, status meta and internal layer. |
| `evidence/req-0033-1440-sprint-empty.png` | 1440x900 | Dropdown search no-result state is visible and keeps current board/filter state. |
| `evidence/req-0033-1440-stage-summary.png` | 1440x900 | Stage multi-select summary switches to selected-count state and board counts/cards use one filtered result. |
| `evidence/req-0033-1440-light-theme.png` | 1440x900 | Light theme remains readable after theme toggle. |
| `evidence/req-0033-390-stage-summary.png` | 390x844 | Narrow viewport keeps filter controls usable with selected-count summary. |
| `evidence/req-0033-computed-style.json` | 1440x900 | Captures toolbar, trigger, popover, option row, checkbox and scroll container size/color/overflow. |
| `evidence/req-0033-modify-1440-level-popover.png` | 1440x900 | Modify evidence for Sprint、分级、负责人、阶段 order and grouped grading popover. |
| `evidence/req-0033-modify-computed-style.json` | 1440x900 | Captures modify filter order, grading groups, P/severity labels, popover/option/footer computed style and outside-click close result. |
| `evidence/req-0033-modify-1440-sprint-unassigned.png` | 1440x900 | Modify evidence for Sprint 全选后包含“未纳入 Sprint”合成候选项. |
| `evidence/req-0033-modify-sprint-unassigned-style.json` | 1440x900 | Captures Sprint options, selected count, unassigned checked state and popover/option/footer computed style. |
| `evidence/req-0033-modify-1440-sprint-default-summary.png` | 1440x900 | Modify evidence for Sprint 默认范围摘要 showing `默认 Sprint 范围` while active filter count remains 0. |
| `evidence/req-0033-modify-sprint-default-summary-style.json` | 1440x900 | Captures default Sprint summary, active filter count 0, manual changed Sprint summary and active filter count 1. |
| `evidence/req-0033-modify-1440-filter-label-column-alignment.png` | 1440x900 | Modify evidence for filter trigger label column alignment inside the filter popover. |
| `evidence/req-0033-modify-filter-label-column-alignment-style.json` | 1440x900 | Captures label width, summary left coordinate and grid columns for Sprint、分级、负责人、阶段 trigger rows. |

### Prototype Gate Report

```yaml
Prototype Gate: pass
UI Skeleton: done
1440px visual acceptance: pass
key interaction screenshots: pass
computed style acceptance: pass
Mock/API boundary: declared
REQ final consistency: pending archive check
```

### Acceptance Modify Evidence

| Field | Evidence |
|---|---|
| feedback | 筛选项顺序为 Sprint、分级、负责人、阶段；Sprint 只展示进行中/已归档；当前迭代标签与状态同行；需求优先级与 BUG 严重性在同一分级筛选内分组；所有筛选支持全选/清空；点击非筛选区域关闭筛选框。 |
| root_cause_status | confirmed |
| evidence_chain | 代码路径 `src/web/src/pages/catalog/RequirementCenterPage.tsx` 原实现顺序为阶段、负责人、优先级、Sprint；原优先级筛选仅匹配 `issue.priority`；外部点击监听以整条工具栏为 contains 范围，且未关闭原生 details 容器。 |
| adjustment | 改为 Sprint、分级、负责人、阶段；分级选项使用 `requirement:<P>` 和 `bug:<severity>` 内部值；下拉 footer 增加全选当前结果；点击非筛选区域同步关闭 active popover 与外层 details。 |
| attachment_comparison | 本次无附件、截图或标注图；依据用户文字验收反馈、REQ-0033 原型上下文和实现测试完成对照。 |
| req_subdocument_sweep | 已同步 `requirement.md`、`acceptance.md`、`user-stories.md`、`business-flow.md`；`prototype/web/context.md` 无需更新，原因是已覆盖 click-outside、单维清空、候选搜索和 Popover 结构。 |
| validation | Vitest 93 项通过；TypeScript build 通过；OpenSpec validate 通过；Playwright 1440px 视觉与 computed style 证据已刷新。 |

### Acceptance Modify Evidence / Sprint Unassigned Option

| Field | Evidence |
|---|---|
| feedback | Sprint 下拉全选时必须包含未纳入 Sprint 的对象；候选项增加“未纳入 Sprint”，支持搜索和全选，选中后匹配无明确 Sprint 归属的卡片；清空 Sprint 维度仍表示不按 Sprint 过滤。 |
| root_cause_status | confirmed |
| evidence_chain | 代码路径 `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 Sprint 候选原先只来自 `sprintOptions` 与卡片可见 Sprint ID，全选动作只合并当前可见真实候选值；无明确 Sprint 归属的卡片没有可被全选覆盖的候选值。 |
| adjustment | 新增 `未纳入 Sprint` 前端合成候选项和搜索别名；全选会包含该项；筛选时无明确 Sprint 归属卡片通过该项命中，清空 Sprint 维度仍保持不过滤。 |
| attachment_comparison | 本次无附件、截图或标注图；依据用户文字验收反馈、实现代码路径和回归测试完成对照。 |
| req_subdocument_sweep | 已同步 `requirement.md`、`acceptance.md`、`user-stories.md`、`business-flow.md`；`prototype/web/context.md` 无需更新，原因是原型已覆盖候选搜索、全选/清空和组合筛选模型。 |
| validation | Vitest 94 项通过；TypeScript build 通过；Playwright 1440px 视觉与 computed style 证据已刷新；OpenSpec validate 待最终文档校验阶段执行。 |

### Acceptance Fix Ledger

| Field | Evidence |
|---|---|
| ledger | `acceptance-fixes.md` |
| latest_feedback | 默认 Sprint 集合下外层筛选数量为 0 时，Sprint 触发器不得显示“已选 N 项”，应显示“默认 Sprint 范围”；手动改变 Sprint 选择后再显示已选数量。 |
| root_cause_status | confirmed |
| evidence_chain | 外层 active filter count 已按 `sprintFilterIsDefault` 排除默认 Sprint 集合，但触发器摘要仍按 `selected.length` 输出数量；用户截图出现 `筛选 0` 与 `已选 3 项` 同屏不一致。 |
| adjustment | Sprint 默认集合摘要改为“默认 Sprint 范围”；手动改选后恢复选项名或“已选 N 项”；组件测试覆盖默认态和手动改选态。 |
| validation | Vitest 96 项通过；TypeScript build 通过；Playwright 1440px 视觉与 computed style 证据已刷新。 |

### Acceptance Fix Ledger / Filter Label Column Alignment

| Field | Evidence |
|---|---|
| ledger | `acceptance-fixes.md` |
| latest_feedback | 筛选浮层内 Sprint、分级、负责人、阶段四行触发器摘要左侧未对齐，需要统一 label 列宽，使摘要从同一水平位置开始。 |
| root_cause_status | confirmed |
| evidence_chain | 用户附件截图显示摘要起点不齐；CSS 使用 `grid-template-columns: auto minmax(0, 1fr) auto`，第一列随 label 文案宽度变化。 |
| adjustment | `.rc-multi-filter-trigger` 第一列固定为 `64px`，摘要列保持弹性与截断。 |
| validation | Vitest 96 项通过；TypeScript build 通过；OpenSpec validate 通过；中文校验通过；Playwright style JSON 记录四行摘要 `summaryLeft` 均为 `1103`；Workflow Sync 通过。 |
