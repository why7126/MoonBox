---
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
title: 需求中心 Sprint 下拉列表新增状态展示
acceptance_status: passed
owner: product
source: requirement.md
created_at: 2026-09-14 14:50:40
updated_at: 2026-09-29 14:41:41
---

# 验收标准

## 功能 AC

- [ ] AC-001 Sprint 筛选下拉中的每个具体 Sprint 选项都展示 Sprint ID/名称和状态信息；“全部 Sprint”作为聚合筛选项，不绑定单个状态。
- [ ] AC-002 状态事实源可追溯，planning、in_progress、completed 和归档目录事实分别映射为规划中、进行中、已完成、已归档。
- [ ] AC-003 状态缺失、非法、活动/归档冲突或无法唯一确认时，单个选项降级展示“状态待核实”或等价文案，且不阻断其他 Sprint 选择。
- [ ] AC-004 新增状态展示不改变既有 Sprint 筛选值、默认选择、刷新、项目切换、搜索/筛选联动、卡片列表和统计口径。
- [ ] AC-005 用户选择某个 Sprint 后，需求中心只展示匹配该 Sprint 的可见卡片；按关联 Change 搜索或其他筛选条件叠加时结果仍一致。
- [ ] AC-006 无 Sprint、项目加载失败、权限失败、只读成员、冻结空间和状态解析失败时沿用需求中心安全反馈，不暴露内部路径、原始日志、未授权项目或无权 Sprint。
- [ ] AC-007 工具栏 Sprint 筛选与加入迭代弹窗的现有 Sprint 状态口径一致；加入迭代弹窗已有状态/容量展示不得回退。
- [ ] AC-008 如实现确认现有 API 已提供足够状态字段，则 Change 文档需记录不新增 API/DB 的依据；如需扩展接口字段，则同步 API 文档、OpenAPI/客户端类型和请求日志验证。

## UI AC

- [ ] AC-UI-001 状态信息视觉层级低于 Sprint 主名称，使用 MoonBox Ops 近直角、细边框、低噪音标签或文本样式。
- [ ] AC-UI-002 深色和浅色主题下，规划中、进行中、已完成、已归档、状态待核实均具备可读对比度，状态色不作为唯一识别方式。
- [ ] AC-UI-003 1440px 桌面视口下，筛选栏、下拉宽度、选项行高、状态标签和周边控件不重叠、不跳动。
- [ ] AC-UI-004 窄屏视口下，长 Sprint ID/名称与状态组合受控换行或省略，不撑破容器、不遮挡选项。
- [ ] AC-UI-005 键盘 Tab、方向键、Enter/Space、Esc 或浏览器原生 select 等价操作可完成打开、浏览、选择和退出；focus 态清晰。
- [ ] AC-UI-006 hover、focus、selected、disabled、loading、error 和 empty 状态均有明确视觉反馈。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解已覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 后续 `/req-opsx` 需在 Change `design.md` 写入 UI Contract 和 UI Skeleton，明确筛选控件 selector、状态事实源、Mock/API 边界和权限显示规则。
- [ ] AC-PROTOTYPE-003 后续 `/opsx-apply` 需完成 1440px 桌面视口真实视觉验收，并覆盖深浅主题、下拉打开态、长 Sprint 名称和状态异常项。
- [ ] AC-PROTOTYPE-004 后续 `/opsx-apply` 或 `/opsx-modify` 需记录 computed style 或等价断言，覆盖字体、字号、行高、宽度、padding、gap、border、background、color、overflow 和 z-index。
- [ ] AC-PROTOTYPE-005 归档前需完成 REQ 最终一致性检查，确认 requirement、user stories、business flow、acceptance、prototype 与 Change 设计和实现证据一致。

## 产品数据采集与链路观测 AC

- [ ] AC-OBS-001 Sprint 下拉打开、选择、项目切换和异常降级如已有行为事件采集，应记录安全摘要，不记录完整响应体、用户输入原文、本机路径、密钥或未授权对象。
- [ ] AC-OBS-002 Sprint 列表或需求中心上下文请求应保留 request_id、结果状态、资源类型和脱敏错误摘要，授权失败与状态缺失可排障。
- [ ] AC-OBS-003 本需求不预期新增长耗时、多步骤或后台任务；若实现阶段新增批量同步、状态修复或异步解析，则需重新评估 task_traces/task_trace_spans。

## 知识库横切检查

| 标签 | 引用文档 | 写入 AC 条数 | 说明 |
|---|---|---:|---|
| 无匹配标签 | docs/knowledge-base/README.md；docs/knowledge-base/retrospectives/sprint-005-retrospective.md | 0 | 本需求属于 web-catalog 筛选下拉增强，不是管理端 CRUD 列表、表单、弹窗或媒体上传；不写 AC-XCUT，承接 sprint-005 的“事实源优先”经验到功能 AC。 |


## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: add-requirement-center-sprint-dropdown-status
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 实现验证摘要

| 类型 | 结论 | 证据 |
|---|---|---|
| 功能实现 | Sprint 筛选下拉展示 Sprint ID 与状态文案；缺失/非法/冲突状态降级为“状态待核实”；选择单个 Sprint 后筛选结果一致。 | `src/web/src/requirement-center.test.tsx`、`tests/integration/api/test_requirement_center.py` |
| API 合约 | 新增 `sprint_option_details`，保留 `sprint_options` 兼容；已同步 OpenAPI、Orval 和 API 文档。 | `src/web/openapi.json`、`src/web/src/api/generated/governance.ts`、`docs/03-api-index.md` |
| UI 证据 | 已完成 1440px 深色主题、390px 浅色窄屏、下拉打开态、unknown 状态与 computed style 采样。 | `openspec/archive/2026-09-17-add-requirement-center-sprint-dropdown-status/evidence/ui/` |
| 观测安全 | 未新增 DB、对象存储、后台任务、Task Trace 或新的日志落库路径；warning 仅保留脱敏摘要。 | `openspec/archive/2026-09-17-add-requirement-center-sprint-dropdown-status/test-plan.md` |

正式 `acceptance_status` 仍等待后续用户验收或 `/opsx-archive` 归档确认。

## 验收返修摘要

| 时间 | 用户反馈 | 处理结果 | 证据 |
|---|---|---|---|
| 2026-09-14 18:11:58 | 筛选下拉面板与触发框距离过远；所有下拉一致异常；删除筛选面板内“已完成 / 归档”。 | 已在原 Change 边界内返修：删除重复 checkbox，修正多选下拉浮层定位，保留 Sprint 状态展示。 | `openspec/archive/2026-09-17-add-requirement-center-sprint-dropdown-status/evidence/ui/sprint-status-styles.json`，`popoverGapPx=6`；相关 Vitest 2 passed。 |
