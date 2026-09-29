---
change_id: add-requirement-center-filter-multiselect-search
source_requirement: REQ-0033-requirement-center-filter-multiselect-search
sprint: sprint-006
created_at: 2026-09-15 08:54:10
updated_at: 2026-09-15 14:41:40
owner: product
---

# 验收返修台账

## F1 筛选顺序、分级表达与浮层关闭

| 项 | 记录 |
|---|---|
| 验收反馈 | 筛选项顺序调整为 Sprint、分级、负责人、阶段；Sprint 状态仅展示进行中/已归档，当前迭代为同行标签；需求 P 优先级与 BUG 严重性在同一分级筛选内分组表达；所有筛选下拉支持全选/清空；点击非筛选区域关闭筛选浮层。 |
| 偏差证据 | 用户文字验收反馈 + 原实现顺序为阶段、负责人、优先级、Sprint；优先级仅匹配 `issue.priority`；外部点击监听未完整关闭内层浮层和外层筛选容器。 |
| 附件截图逐项视觉对照表 | 本批次无附件、截图或标注图；对照对象为用户文字验收反馈、REQ-0033 原型契约和当前实现证据。无缺失附件阻断。 |
| 调整内容 | 前端筛选维度改为 Sprint、分级、负责人、阶段；分级内分组展示需求优先级和缺陷严重性；Sprint 筛选展示两态与当前迭代标签；下拉 footer 增加全选当前结果；外部点击同步关闭 active popover 与外层容器。 |
| REQ 子文档一致性扫尾检查 | 已同步 `requirement.md`、`acceptance.md`、`user-stories.md`、`business-flow.md`；`prototype/web/context.md` 已覆盖外部点击、单维清空、候选搜索和 Popover 结构，无需更新。 |
| API / DB / 部署 / 安全 / 观测 | 不涉及；仍为前端 UI 与客户端过滤语义返修，不新增 API、数据库、请求日志、行为事件、Task Trace、对象存储或权限边界。 |
| 验证 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 93 项；`./node_modules/.bin/tsc -b` 通过；Playwright 1440px 视觉与 computed style 证据已刷新。 |

## F2 Sprint 全选包含未纳入 Sprint

| 项 | 记录 |
|---|---|
| 验收反馈 | Sprint 下拉全选时必须包含未纳入 Sprint 的对象；Sprint 候选项增加“未纳入 Sprint”合成选项，支持搜索和全选，选中后匹配无明确 Sprint 归属的卡片；清空 Sprint 维度仍表示不按 Sprint 过滤。 |
| 偏差证据 | 用户追加验收反馈 + Sprint 候选集合只由真实 Sprint ID 构成，全选只能选中真实 Sprint，无法覆盖缺少明确 Sprint 归属的卡片。 |
| 附件截图逐项视觉对照表 | 本批次无附件、截图或标注图；对照对象为用户文字验收反馈、现有 Sprint 筛选实现和新增回归测试。无缺失附件阻断。 |
| 调整内容 | 新增“未纳入 Sprint”合成候选项和搜索别名；Sprint 全选会选中该候选项；筛选逻辑对无明确 Sprint 归属卡片支持该候选项命中，同时保留清空 Sprint 维度为不过滤。 |
| REQ 子文档一致性扫尾检查 | 已同步 `requirement.md`、`acceptance.md`、`user-stories.md`、`business-flow.md`；`prototype/web/context.md` 无需更新，原因是原型已覆盖 Sprint 候选、全选/清空和筛选组合模型。 |
| API / DB / 部署 / 安全 / 观测 | 不涉及；“未纳入 Sprint”为前端授权上下文内的合成候选项，不新增 API、数据库、权限或观测字段。 |
| 验证 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 94 项；`./node_modules/.bin/tsc -b` 通过；Playwright 1440px 视觉与 computed style 证据已刷新。 |

## F3 默认 Sprint 范围摘要与外层筛选数量一致

| 项 | 记录 |
|---|---|
| 验收反馈 | 筛选按钮后的数量与实际筛选显示不一致；当 Sprint 维度处于默认选择集合时，外层筛选数量为 0 是合理的，但 Sprint 触发器不应显示“已选 N 项”，应显示“默认 Sprint 范围”或等价默认态文案；用户手动改变 Sprint 选择后再显示已选数量。 |
| 偏差证据 | 用户截图显示外层筛选数量为 `0`，但 Sprint 触发器显示“已选 3 项”；代码中外层数量通过 `sprintFilterIsDefault` 排除默认 Sprint 集合，而触发器摘要仍按 `selected.length` 输出数量摘要。 |
| 附件截图逐项视觉对照表 | 用户附件截图：外层按钮 `筛选 0` 与 Sprint 触发器 `已选 3 项` 同屏出现；期望为外层数量保持 0，Sprint 触发器显示默认态文案；检查方式为代码断言、组件测试和 1440px 视觉证据。 |
| 调整内容 | `filterSummary` 支持默认摘要；Sprint 当前选中集合等于默认 Sprint 集合时显示“默认 Sprint 范围”；用户手动取消或改选 Sprint 后恢复选项名或“已选 N 项”；外层 activeFilterCount 口径保持不变。 |
| REQ 子文档一致性扫尾检查 | 已同步 `requirement.md`、`acceptance.md`、`user-stories.md`、`business-flow.md`；`prototype/web/context.md` 无需更新，原因是默认摘要属于实现态文案规则，原型已覆盖摘要与数量降级模型。 |
| API / DB / 部署 / 安全 / 观测 | 不涉及；仅修改前端摘要文案和测试，不新增 API、数据库、请求日志、行为事件、Task Trace、对象存储或权限边界。 |
| 验证 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 96 项；`./node_modules/.bin/tsc -b` 通过；Playwright 1440px 视觉与 computed style 证据已刷新：`evidence/req-0033-modify-1440-sprint-default-summary.png`、`evidence/req-0033-modify-sprint-default-summary-style.json`。 |

## F4 筛选触发器摘要左侧对齐

| 项 | 记录 |
|---|---|
| 验收反馈 | 筛选浮层内各筛选触发器摘要左侧未对齐；Sprint、分级、负责人、阶段四行应统一 label 列宽，使摘要文案从同一水平位置开始。 |
| 偏差证据 | 用户附件截图显示 `Sprint` 行摘要起点与 `分级`、`负责人`、`阶段` 行摘要起点不同；代码中 `.rc-multi-filter-trigger` 使用 `grid-template-columns: auto minmax(0, 1fr) auto`，第一列随 label 文案宽度变化。 |
| 附件截图逐项视觉对照表 | 用户附件截图：页面为需求中心筛选浮层打开态，深色主题，约 1440px 桌面宽度；期望四行摘要左侧统一对齐；实际为 label 第一列按文字宽度自适应导致摘要起点不齐；检查方式为视觉对照、CSS 路径和 Playwright computed style；处置结论为本次修复；证据入口为 `evidence/req-0033-modify-1440-filter-label-column-alignment.png`、`evidence/req-0033-modify-filter-label-column-alignment-style.json`。 |
| 调整内容 | 将筛选触发器 grid 第一列固定为 `64px`，保留摘要列 `minmax(0, 1fr)` 与箭头列；四个筛选维度 label 占用一致宽度，摘要从同一水平位置开始。 |
| REQ 子文档一致性扫尾检查 | 已同步 `acceptance.md`；`requirement.md`、`user-stories.md`、`business-flow.md`、`prototype/web/context.md` 无需更新，原因是本次仅细化同一筛选浮层的视觉对齐验收，不改变筛选行为、用户流程、数据边界或原型意图。 |
| API / DB / 部署 / 安全 / 观测 | 不涉及；仅修改前端 CSS 与 UI 验收测试，不新增 API、数据库、请求日志、行为事件、Task Trace、对象存储或权限边界。 |
| 验证 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过 96 项；`./node_modules/.bin/tsc -b` 通过；`openspec validate add-requirement-center-filter-multiselect-search --strict` 通过；当前 Change 中文校验通过；Playwright 1440px computed style 显示四行摘要 `summaryLeft` 均为 `1103`，`allSummaryLeftAligned: true`；Workflow Sync 通过。 |
