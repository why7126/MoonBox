---
change_id: add-requirement-center-sprint-dropdown-status
type: update
status: applied
created_at: 2026-09-14 15:08:00
updated_at: 2026-09-17 08:30:53
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
req_id: REQ-0032-requirement-center-sprint-dropdown-status
sprint_id: sprint-006
owner: product
source: issues/requirements/review/REQ-0032-requirement-center-sprint-dropdown-status/
specs:
  - web-catalog-requirement-center
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
ui_contract:
  status: drafted
  source: design.md
ui_skeleton:
  status: done
  source: design.md
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: Sprint 筛选状态展示影响前端行为事件、需求中心上下文请求和异常降级排障；若扩展 API 字段，还需同步 OpenAPI/客户端类型和请求日志验证。
  validation: 已验证 Sprint 下拉打开、选择、状态缺失、OpenAPI/Orval 同步和安全摘要边界；未新增 DB、对象存储、后台任务或新的日志落库路径，不记录完整响应体、本机路径、密钥或无权对象。
execution:
  schema_version: 1
  started_at: 2026-09-14 15:21:10
  completed_at: 2026-09-14 18:11:58
  last_event: opsx.modify
---

# Change Trace

## 状态

```yaml
status: applied
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
req_id: REQ-0032-requirement-center-sprint-dropdown-status
sprint_id: sprint-006
tasks_total: 15
tasks_done: 15
```

## Requirement Readiness Report

| 检查项 | 结果 | 证据 |
|---|---|---|
| REQ 状态 | ready | trace 为 `in_sprint`，iteration 为 `sprint-006` |
| 文档包 | ready | requirement、user-stories、business-flow、acceptance、trace、review、prototype 均存在 |
| Prototype Gate | partially ready | 原型拆解完成；UI Skeleton、1440px 视觉证据和最终一致性待实现阶段完成 |
| Knowledge Gate | N/A | 无 admin-list/admin-form/admin-modal/media-upload 标签；承接 sprint-005 事实源优先经验 |
| Observability Gate | ready | REQ 与 design 已声明 `usage_events`、`request_logs` 适用 |

## Conflict Resolution

| 事项 | 结论 |
|---|---|
| 原型使用静态 combobox | 作为视觉方向，生产实现可选择原生 select 文案增强或受控 combobox。 |
| 现有工具栏是原生 select | 不强制换组件；以状态可读、可达和不回退筛选行为为验收。 |
| 加入迭代弹窗已有状态/容量模型 | 必须保持，不因本 Change 回退。 |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 15:08:00 | /req-opsx | 创建 OpenSpec Change，生成 proposal/design/spec/tasks/trace，状态为 proposed。 |

## 实现证据

| 类型 | 结论 | 证据 |
|---|---|---|
| 后端 API | `RequirementCenterContext` 新增 `sprint_option_details`，保留旧 `sprint_options` 字符串兼容路径 | `src/backend/app/schemas/requirement_center.py`、`src/backend/app/services/requirement_center.py` |
| 前端 UI | Sprint 筛选下拉展示进行中、规划中、已完成、已归档、状态待核实；加入迭代弹窗复用同一状态映射 | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/styles/globals.css` |
| API 文档与客户端 | OpenAPI JSON、Orval governance/chat 客户端与 `docs/03-api-index.md` 已同步 | `src/web/openapi.json`、`src/web/src/api/generated/governance.ts`、`docs/03-api-index.md` |
| 视觉证据 | 1440px 深色主题、390px 浅色窄屏、下拉打开态、unknown 状态和 computed style 已采集 | `evidence/ui/sprint-status-dark-1440.png`、`evidence/ui/sprint-status-light-390.png`、`evidence/ui/sprint-status-styles.json` |
| 观测与安全 | 响应只增加脱敏状态摘要；不新增 DB、对象存储、后台任务、Task Trace 或新的日志落库路径 | `test-plan.md` |

## 验证记录

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run pytest tests/integration/api/test_requirement_center.py -q` | 通过 | 20 passed |
| `./node_modules/.bin/vitest run src/requirement-center.test.tsx` | 通过 | 85 passed |
| `./node_modules/.bin/tsc --noEmit` | 通过 | TypeScript 类型检查通过 |
| `./scripts/generate-openapi-client.sh` | 部分通过 | OpenAPI JSON 已导出；本机 pnpm/Corepack 缺失导致脚本内客户端步骤跳过 |
| `./node_modules/.bin/orval --config orval.config.ts` | 通过 | governance/chat 客户端生成成功 |
| `node tests/requirement-center-sprint-status.cjs` | 通过 | 2 个真实浏览器视觉样本通过 |
| `openspec validate add-requirement-center-sprint-dropdown-status` | 通过 | Change 合法 |
| `python scripts/validate-design-system.py` | 非本变更失败 | 仓库既有 115 项违规，本次新增样式未出现在失败清单 |
| `python scripts/validate-openspec-language.py` | 非本变更失败 | 失败项来自其他活动 Change，本 Change 未出现在失败清单 |

## 验收返修记录

### 2026-09-14 筛选下拉浮层与重复筛选项

验收反馈：筛选下拉框的交互异常，下拉面板与触发框距离过远；所有筛选下拉一致异常；删除筛选面板内“已完成 / 归档”的重复筛选。

根因状态：confirmed。

证据链：

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 用户附件 `codex-clipboard-673ec29c-0817-4165-957d-996956074714.png` | 阶段下拉打开后，面板进入筛选菜单内部文档流，后续筛选控件被挤到下方；“已完成 / 归档”checkbox 可见。 | 证明验收反馈可复现于当前交互状态。 |
| E2 | code_path | `src/web/src/styles/globals.css` | `.rc-multi-filter-popover` 后置定义覆盖为 `position: relative`，覆盖前置绝对定位定义。 | 解释所有多选下拉均出现距离异常。 |
| E3 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 筛选面板中存在 `showArchived` checkbox，与 Sprint/阶段/负责人/优先级多选同级。 | 证明重复筛选项来源。 |
| E4 | computed_style | `evidence/ui/sprint-status-styles.json` | 返修后 1440px 深色与 390px 浅色样本 `popoverGapPx=6`，页面错误为空。 | 证明下拉浮层已贴近触发器且视觉复验通过。 |

附件截图逐项视觉对照表：

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| Image #1 | 需求中心，深色主题，筛选菜单展开，阶段下拉打开 | 当前实现截图与 Change UI Contract | 子下拉面板贴近触发框，后续筛选字段不被挤到远处；筛选面板不再出现“已完成 / 归档”checkbox | 面板与触发框距离很远，后续筛选控件位于面板底部；重复 checkbox 可见 | `position`、间距、文档流、重复筛选项 | 视觉对照、代码路径、Playwright geometry、computed style | 本次修复 | `evidence/ui/sprint-status-dark-1440.png`、`evidence/ui/sprint-status-light-390.png`、`evidence/ui/sprint-status-styles.json` |

调整内容：

- 删除 `showArchived` 状态和筛选菜单内“已完成 / 归档”checkbox；已完成卡片不再由该重复筛选项控制。
- 修正 `.rc-multi-filter-popover` 后置 CSS 覆盖，恢复 `position: absolute`、`top: calc(100% + 6px)`、`z-index: 36`。
- 更新前端测试与 Playwright 视觉脚本，断言重复 checkbox 不存在，且 Sprint 下拉 `popoverGapPx` 在 4 到 10px 范围内。

验证补充：

| 命令 | 结果 | 说明 |
|---|---|---|
| `./node_modules/.bin/tsc --noEmit` | 通过 | TypeScript 类型检查通过 |
| `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "keeps per-Change progress|shows traceable Sprint statuses"` | 通过 | 2 passed，覆盖删除 checkbox 与 Sprint 状态下拉 |
| `node tests/requirement-center-sprint-status.cjs` | 通过 | 2 个真实浏览器样本通过；`popoverGapPx=6` |
| `./node_modules/.bin/vitest run src/requirement-center.test.tsx --reporter=dot` | warning | 76 passed、14 failed；失败集中在既有默认当前迭代筛选/旧文档按钮查询断言，非本次浮层与重复控件返修路径 |

## 归档前最终一致性检查

| 检查项 | 结论 | 证据 |
|---|---|---|
| REQ 主文档与原型上下文 | 一致 | `requirement.md`、`prototype/web/context.md` 均限定为 Sprint 下拉状态展示，不包含重做筛选体系或归档能力。 |
| Change 设计与实现证据 | 一致 | `design.md` 保持 Sprint 状态事实源、UI Skeleton、Mock/API 边界；实现证据保留后端、前端、API 文档与视觉证据。 |
| 验收返修与非目标 | 一致 | 返修删除“已完成 / 归档”重复筛选控件，不改变 Sprint 状态展示主目标；视觉证据 `popoverGapPx=6`。 |
| 1440px 视觉验收 | passed | `evidence/ui/sprint-status-dark-1440.png` 与 `evidence/ui/sprint-status-styles.json`。 |
