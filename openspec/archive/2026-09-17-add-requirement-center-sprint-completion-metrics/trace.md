---
change_id: add-requirement-center-sprint-completion-metrics
title: 需求中心 Sprint 已完成与累计数量指标
status: applied
change_type: add
requirement: REQ-0030-requirement-center-sprint-completion-metrics
sprint: sprint-006
created_at: 2026-09-14 15:07:31
updated_at: 2026-09-15 09:33:51
owner: 产品团队
acceptance_refs:
  - acceptance-fixes.md
execution:
  schema_version: 1
  started_at: 2026-09-14 15:19:01
  completed_at: 2026-09-14 15:33:36
  last_event: opsx.modify
---

# 追踪记录

## 来源链路

| 项 | 值 |
|---|---|
| Source REQ | REQ-0030-requirement-center-sprint-completion-metrics |
| Requirement status | in_sprint |
| Sprint | sprint-006 |
| Change | add-requirement-center-sprint-completion-metrics |
| Change status | applied |

## 需求就绪报告

| 检查项 | 结果 | 证据 |
|---|---|---|
| requirement.md | Pass | 已描述背景、范围、FR、UI、观测与状态块 |
| user-stories.md | Pass | 已补齐目标用户和故事 |
| business-flow.md | Pass | 已补齐业务流程 |
| acceptance.md | Pass | 已补齐功能 AC、原型 AC、横切 AC |
| prototype/web | Pass | 已存在 context.md 与 prototype.html |
| review.md | Pass | 已评审通过 |
| Sprint | Pass | 已纳入 sprint-006 |

## 原型与 UI 契约

- 原型来源：`issues/requirements/review/REQ-0030-requirement-center-sprint-completion-metrics/prototype/web/context.md`
- HTML 原型：`issues/requirements/review/REQ-0030-requirement-center-sprint-completion-metrics/prototype/web/prototype.html`
- UI Contract：已写入 `design.md`
- UI Skeleton：实现阶段先交付骨架并补 1440px 深浅主题证据
- PNG：当前 propose 阶段不要求；apply 阶段补截图证据

## 产品数据采集与链路观测

```yaml
status: applicable
affected_layers:
  - request_logs
  - usage_events
task_traces: N/A
task_trace_spans: N/A
validation:
  - 请求日志只记录接口、状态码、耗时和脱敏统计摘要
  - 行为事件只记录页面加载、手动刷新、空间切换等稳定上下文
  - 不记录原始治理文档、本机绝对路径、内部堆栈、密钥、token 或 .env 内容
```

## 实现记录

| 层 | 文件 | 说明 |
|---|---|---|
| Backend schema | `src/backend/app/schemas/requirement_center.py` | 新增 `RequirementCenterSprintMetrics`，并挂载到需求中心 context 响应 |
| Backend service | `src/backend/app/services/requirement_center.py` | 从 `iterations/change/` 与 `iterations/archive/` 聚合 Sprint 指标，按 Sprint ID 去重，解析失败返回脱敏 warning |
| Web UI | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 指标区新增 `[data-testid="sprint-completion-metric"]`，展示已完成/累计项目级总览 |
| Web style | `src/web/src/styles/globals.css` | 指标区扩展为 6 列并补充 Sprint 指标数字、提示和响应式防溢出样式 |
| API docs/client | `docs/03-api-index.md`、`src/web/openapi.json`、`src/web/src/api/generated/governance.ts` | 同步 `sprint_metrics` 契约、文档和生成客户端类型 |

## 验收返修记录

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户无新增附件；参考用户文字反馈与上一轮 Playwright 视觉证据 |
| 页面/状态 | 需求中心，指标区，1440 深浅主题、1024、390，tooltip hover 状态 |
| 对照对象 | 当前实现中的 `.rc-stat`、`[data-testid="sprint-completion-metric"]` 与用户验收反馈 |
| 期望表现 | 指标卡更矮；所有指标名后有说明图标和统一 tooltip；需求、Bug、独立 Change 展示已完成/总体；Sprint 标题为 Sprint 且无底部辅助文案 |
| 实际表现 | apply 后指标卡高度为 74px，Sprint 卡存在底部“已完成 / 累计 · 项目级总览”，对象指标仅显示数量 |
| 偏差项 | 高度、文案、说明承载方式、对象指标统计形式 |
| 检查方式 | 代码 selector、Vitest、Playwright 截图、computed style |
| 处置结论 | 本次修复；按方案 A 保留对象指标跟随当前筛选，Sprint 保持项目级总览 |
| 证据入口 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/modify-20260914-metrics-tooltip/req-0030-modify-visual-evidence.json` |

## 返修实现记录

| 层 | 文件 | 说明 |
|---|---|---|
| Web UI | `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 新增指标说明组件；需求、Bug、独立 Change 显示已完成/总体；Sprint 标题改为 `Sprint` 并删除底部说明 |
| Web style | `src/web/src/styles/globals.css` | 指标卡压缩为 `min-height: 60px`、`padding: 10px 14px`，新增统一 `data-tooltip` 浮层样式 |
| Frontend test | `src/web/src/requirement-center.test.tsx` | 覆盖完成比例、tooltip、Sprint 文案和紧凑样式 |

## Mock/API 边界

- 生产默认路径：需求中心 context 接口返回真实 `sprint_metrics`，前端从接口 context 读取，不使用原型静态数字。
- 自动化前端测试：使用 fixture 验证指标渲染、筛选不变、刷新失败保留上次成功数据和状态展示。
- 视觉验收：使用合成前台登录态与 `?mock=workflow` 演示上下文，只验证 UI 骨架、主题、响应式、文本溢出和交互不变性。

## 视觉证据

| 项 | 证据 | 结论 |
|---|---|---|
| 1440px 深色主题 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-dark-1440.png` | 指标卡 ready，无溢出 |
| 1440px 浅色主题 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-light-1440.png` | 指标卡 ready，无溢出 |
| 1024px | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-tablet-1024.png` | 指标卡 ready，无溢出 |
| 390px | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-mobile-390.png` | 指标卡 ready，无溢出 |
| computed style | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-visual-evidence.json` | `display=grid`、数字 `display=flex`、`white-space=nowrap`、`overflow=false` |
| 筛选不变性 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-filter-invariant.json` | 搜索筛选前后 Sprint 指标文本一致 |
| 返修视觉 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/modify-20260914-metrics-tooltip/req-0030-modify-visual-evidence.json` | 1440 深浅主题、1024、390 中 Sprint 卡 `min-height=60px`，label/数字无溢出，tooltip hover 可见 |

## 校验记录

| 时间 | 命令 | 结果 |
|---|---|---|
| 2026-09-15 09:33:51 | 需求中心交付验证来源入口 | pass；`acceptance_refs` 指向 `acceptance-fixes.md`，并新增非空 `## 验证记录`。 |
| 2026-09-14 15:07:31 | /req-opsx REQ-0030 | 创建 OpenSpec Change 草案 |
| 2026-09-14 15:19:01 | `python scripts/sync-workflow-status.py --event opsx.start --change add-requirement-center-sprint-completion-metrics --sprint auto` | Pass，Change 进入 in_progress |

## 验证记录

| 时间 | 验证项 | 结果 |
|---|---|---|
| 2026-09-15 09:33:51 | 需求中心交付验证来源入口 | pass；`acceptance_refs` 指向 `acceptance-fixes.md`，本节作为非空验证来源章节，避免卡片误报“未找到交付验证记录”。 |
| 2026-09-14 18:26:44 | Sprint 指标实现与返修验证 | pass；详见 `## 校验记录`、`## 视觉证据`、`## 验收返修记录` 和 `acceptance-fixes.md`。 |
| 2026-09-14 15:24:00 | `./scripts/generate-openapi-client.sh` | OpenAPI 导出成功；pnpm corepack 缓存缺失导致 Orval 步骤退出，随后用本地 Orval 补跑 |
| 2026-09-14 15:25:00 | `node_modules/.bin/orval --config orval.config.ts` | Pass，生成前端客户端类型 |
| 2026-09-14 15:28:00 | `node_modules/.bin/tsc -b` | Pass |
| 2026-09-14 15:28:30 | `node_modules/.bin/vitest --run src/requirement-center.test.tsx` | Pass，85 passed |
| 2026-09-14 15:29:00 | `uv run pytest ../../tests/integration/api/test_requirement_center.py -q` | Pass，20 passed |
| 2026-09-14 15:31:32 | Playwright 视觉采样 | Pass，1440 深浅主题、1024、390 均无溢出 |
| 2026-09-14 15:33:22 | Playwright 搜索筛选交互采样 | Pass，筛选前后 Sprint 指标文本一致 |
| 2026-09-14 18:25:39 | `node_modules/.bin/tsc -b` | Pass |
| 2026-09-14 18:25:39 | `node_modules/.bin/vitest --run src/requirement-center.test.tsx` | Pass，91 passed |
| 2026-09-14 18:26:44 | Playwright 返修视觉采样 | Pass，1440 深浅主题、1024、390 中 label/数字无溢出，tooltip hover 可见 |

## 产品数据采集与链路观测验证

```yaml
status: applicable
affected_layers:
  - request_logs
  - usage_events
validation:
  - context 接口新增字段仅返回 completed_count、total_count、source、warning、refreshed_at 等脱敏摘要
  - invalid sprint.yaml 测试确认 warning 为 sprint_metrics_partial，响应不包含临时路径或 /Users/
  - 前端只展示项目级短文案和脱敏 warning，不展示治理文件路径、堆栈、token、.env 或原始文档全文
```

## 下一步

- `/opsx-archive REQ-0030-requirement-center-sprint-completion-metrics`
