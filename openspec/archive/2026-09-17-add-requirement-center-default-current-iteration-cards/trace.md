---
change_id: add-requirement-center-default-current-iteration-cards
title: 需求中心默认只显示当前迭代卡片
type: add
status: applied
created_at: 2026-09-14 15:20:35
updated_at: 2026-09-17 08:26:26
source_requirement: REQ-0034-requirement-center-default-current-iteration-cards
source_sprint: sprint-006
affected_specs:
  - web-catalog-requirement-center
  - web-catalog-requirement-center-real-data
prototype_refs:
  - issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/prototype/web/context.md
  - issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/prototype/web/prototype.html
prototype_gate:
  decomposition: done
  ui_contract: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  computed_style_evidence: passed
  mock_api_boundary: declared_no_api_change
  req_final_consistency: passed
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: 默认当前迭代范围影响需求中心页面加载、范围切换、筛选重置、手动刷新和空间/项目切换；若后端聚合接口参与当前迭代识别，需要请求日志记录安全摘要。
  validation: opsx-modify 已确认本次仅复用既有需求中心上下文字段 `sprint_option_details`、`sprint_options` 和卡片 `sprint_id`，无新增 API 字段、OpenAPI、Orval 或请求封装；行为仅为前端 Sprint 多选默认状态与筛选状态切换，不新增 usage_events 持久化点；后端请求日志保持既有安全摘要边界。
validation:
  openspec_validate: pass
  workflow_sync: pass
execution:
  schema_version: 1
  started_at: 2026-09-14 15:54:28
  completed_at: 2026-09-15 00:10:00
  last_event: opsx.modify
---

# Change Trace

## 来源

- REQ：`REQ-0034-requirement-center-default-current-iteration-cards`
- Sprint：`sprint-006`
- Change 类型：`add`

## Conflict Resolution

`prototype.html` 和 `prototype/web/context.md` 是 UI Skeleton 输入，最终验收以 Change design、delta spec、acceptance、1440px/关键交互视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 15:20:35 | /req-opsx | 创建 OpenSpec Change，生成 proposal、design、spec delta、tasks 和 trace 初稿。 |
| 2026-09-14 15:53:06 | /opsx-apply | 实现需求中心默认当前迭代范围、范围切换、空态、响应式样式、测试与视觉证据；未变更后端 API 契约。 |
| 2026-09-14 18:20:00 | /opsx-modify | 根据验收反馈移除独立范围筛选和筛选下方提示模块，改为在既有 Sprint 多选中默认选中当前 Sprint；同步测试与文档。 |
| 2026-09-14 23:55:00 | /opsx-modify | 根据验收反馈将默认 Sprint 多选扩展为当前 Sprint + 未纳入 Sprint，保留规划前待处理对象默认可见；同步测试与文档。 |
| 2026-09-17 08:26:26 | /opsx-archive | 归档前复核 REQ 文档、Change design、spec delta、1440px 视觉证据、computed style 与 Mock/API 边界一致；原型最终一致性标记为通过。 |

## Implementation Notes

- 实现入口：`src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/styles/globals.css`、`src/web/src/requirement-center.test.tsx`。
- Mock/API 边界：前端复用既有 `sprint_option_details` 中的 `lifecycle_stage/status` 识别 `planning` / `in_progress` 当前 Sprint；复用卡片 `sprint_id` 判定范围归属；不新增或修改后端 Schema、OpenAPI、Orval 生成物和请求封装。
- Sprint 多选语义：首次进入、重置筛选、空间/项目切换默认选中当前 Sprint 集合和 `未纳入 Sprint`；手动刷新保留用户显式 Sprint 选择；清空 Sprint 多选展示全量授权对象，选择历史/归档 Sprint 查看对应范围；workflow demo 保持全量展示以服务受控演示。
- 验收反馈处置：未新增 `当前迭代｜全部｜历史｜未纳入迭代｜归档` 范围筛选模块；未新增筛选模块下方提示模块；当前迭代只通过 Sprint 下拉多选中的选中状态表达。
- 安全与脱敏：错误态继续复用 `RequirementCenterError` 和后端脱敏读取错误；范围候选来自当前授权上下文，未新增本机路径、文档全文、密钥、Token、`.env` 或未授权对象身份输出。

## Acceptance Feedback Comparison

| 来源 | 期望 | apply 后偏差 | 返修处置 | 证据 |
|---|---|---|---|---|
| 用户验收反馈 | 不新增 `当前迭代｜全部｜历史｜未纳入迭代｜归档` 筛选 | apply 版本新增独立范围按钮组 | 已移除范围按钮组与 `requirement-range-*` UI | `rg requirement-range src/web/src/pages/catalog/RequirementCenterPage.tsx src/web/src/styles/globals.css` 无实现命中 |
| 用户验收反馈 | 不新增筛选模块下方提示模块 | apply 版本新增范围提示模块 | 已移除提示模块与对应样式 | `requirement-range-notice` 仅保留负向测试断言 |
| 用户验收反馈 | 当前迭代直接在 Sprint 下拉框中选中 | apply 版本以范围模式表达当前迭代 | 已改为 `selectedSprints` 默认当前 Sprint 集合 | `RequirementCenterPage.tsx` 默认选择 effect 与多选测试覆盖 |
| 用户补充 | Sprint 下拉支持多选 | apply 版本未以多选作为默认表达 | 单当前 Sprint + 未纳入 Sprint 默认显示 `已选 2 项`，多当前 Sprint + 未纳入 Sprint 默认显示 `已选 3 项`，可取消到单 Sprint | `requirement-center.test.tsx` 覆盖默认、多当前、清空和历史选择 |
| 用户验收反馈 | Sprint 默认选中当前 Sprint + 未纳入 Sprint | 上一版默认只选当前 Sprint，规划前无 Sprint 对象需清空后才可见 | 已将默认选择基线改为当前 Sprint 集合 + `未纳入 Sprint` 候选 | `requirement-center.test.tsx` 覆盖默认、重置、多当前与无当前 |

## UI Evidence

| Evidence | Viewport | Summary |
|---|---:|---|
| `evidence/sprint-default-current-1440.png` | 1440x960 | 默认当前 Sprint + 未纳入 Sprint 在既有 Sprint 多选中选中，首屏标题、指标、工具栏和九阶段看板稳定展示，无独立范围筛选/提示模块。 |
| `evidence/sprint-clear-all-1440.png` | 1440x960 | 清空 Sprint 多选后展示全量授权卡片，历史和未纳入迭代对象可见。 |
| `evidence/sprint-multi-current-1440.png` | 1440x960 | 多当前 Sprint + 未纳入 Sprint 默认多选，触发器显示 `已选 3 项`，长 Sprint ID 不遮挡看板。 |
| `evidence/sprint-no-current-1440.png` | 1440x960 | 无当前 Sprint 时默认选中未纳入 Sprint，页面不新增提示模块。 |
| `evidence/sprint-default-mobile-390.png` | 390x900 | 窄屏 Sprint 多选、工具栏和横向看板滚动可用。 |
| `evidence/computed-styles.json` | 390x900 | 采样 Sprint 多选触发器、筛选工具栏、看板滚动、sticky 表头和空态的 height/padding/gap/color/border/overflow/position。 |

## Validation Log

| Time | Command | Result |
|---|---|---|
| 2026-09-14 15:20 | `python scripts/validate-change-identity.py --new-id add-requirement-center-default-current-iteration-cards` | pass |
| 2026-09-14 15:20 | `openspec new change add-requirement-center-default-current-iteration-cards` | pass |
| 2026-09-14 15:21 | `openspec validate add-requirement-center-default-current-iteration-cards --strict` | pass |
| 2026-09-14 15:21 | `python scripts/add-sprint-scope-item.py --sprint sprint-006 --req REQ-0034-requirement-center-default-current-iteration-cards --change add-requirement-center-default-current-iteration-cards --size M --story-points 3 --person-days 3` | pass |
| 2026-09-14 15:24 | `python scripts/sync-workflow-status.py --event req.opsx --req REQ-0034-requirement-center-default-current-iteration-cards --change add-requirement-center-default-current-iteration-cards --sprint auto` | pass, updated=5, errors=0 |
| 2026-09-14 15:24 | `python scripts/validate-sprint-scope.py sprint-006 --item REQ-0034-requirement-center-default-current-iteration-cards` | pass |
| 2026-09-14 15:24 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event req.opsx --req REQ-0034-requirement-center-default-current-iteration-cards --change add-requirement-center-default-current-iteration-cards --sprint sprint-006 --json` | warning: usage_mode unavailable, sprint snapshot skipped because no command runs |
| 2026-09-14 15:48 | `npm --prefix src/web run test -- src/requirement-center.test.tsx` | pass, 88 tests |
| 2026-09-14 15:49 | `npm --prefix src/web run build` | pass |
| 2026-09-14 15:49 | `uv run pytest tests/integration/api/test_requirement_center.py src/backend/tests/test_governance_board.py` | pass, 91 tests |
| 2026-09-14 15:49 | `openspec validate add-requirement-center-default-current-iteration-cards --strict` | pass |
| 2026-09-14 15:53 | `Playwright visual evidence capture` | pass, screenshots and computed styles saved under `evidence/` |
| 2026-09-14 18:18 | `npm --prefix src/web run test -- src/requirement-center.test.tsx` | pass, 90 tests |
| 2026-09-14 18:19 | `openspec validate add-requirement-center-default-current-iteration-cards --strict` | pass |
| 2026-09-14 18:19 | `npm --prefix src/web run build` | pass |
| 2026-09-14 18:28 | `Playwright visual evidence capture` | pass, refreshed Sprint multi-select screenshots and computed styles saved under `evidence/` |
| 2026-09-14 18:29 | `openspec validate add-requirement-center-default-current-iteration-cards --strict` | pass |
| 2026-09-14 18:29 | `git diff --check -- ...REQ-0034...` | pass |
| 2026-09-14 18:29 | `python scripts/sync-workflow-status.py --event opsx.modify --change add-requirement-center-default-current-iteration-cards --sprint auto` | pass, sprint=sprint-006, updated=1, errors=0, subdocuments checked=7 |
| 2026-09-14 18:29 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change add-requirement-center-default-current-iteration-cards --sprint sprint-006 --json` | warning: usage_mode unavailable, sprint snapshot skipped because no command runs |
| 2026-09-15 00:03 | `npm --prefix src/web run test -- src/requirement-center.test.tsx` | pass, 94 tests |
| 2026-09-15 00:03 | `npm --prefix src/web run build` | pass |
| 2026-09-15 00:03 | `openspec validate add-requirement-center-default-current-iteration-cards --strict` | pass |
| 2026-09-15 00:04 | `Playwright visual evidence capture` | pass, refreshed current Sprint + 未纳入 Sprint screenshots and computed styles saved under `evidence/` |
| 2026-09-15 00:05 | `git diff --check -- ...REQ-0034...` | pass |
| 2026-09-15 00:05 | `python scripts/sync-workflow-status.py --event opsx.modify --change add-requirement-center-default-current-iteration-cards --sprint auto` | pass, sprint=sprint-006, updated=0, errors=0, subdocuments checked=7, updated=1 |
| 2026-09-15 00:05 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change add-requirement-center-default-current-iteration-cards --sprint sprint-006 --json` | warning: usage_mode unavailable, sprint snapshot skipped because no command runs |
