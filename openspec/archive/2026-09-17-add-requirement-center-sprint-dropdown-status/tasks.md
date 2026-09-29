## 1. 前置核实与 UI Skeleton

- [x] 1.1 核实需求中心上下文 API、后端聚合服务、前端 `RequirementCenterPage` 和加入迭代弹窗当前 Sprint 字段与状态来源。
- [x] 1.2 根据 REQ prototype 和 design.md 完成 Sprint 筛选 UI Skeleton，覆盖工具栏、下拉打开态、全部 Sprint、具体 Sprint、未知状态和长名称。
- [x] 1.3 记录 1440px Skeleton 证据或等价 DOM/截图证据，确认筛选栏、下拉和卡片区不重叠。

## 2. 数据模型与 API 兼容

- [x] 2.1 若现有响应缺少结构化 Sprint 状态，扩展后端 schema/service，为 Sprint 选项提供状态、状态文案和异常原因的脱敏摘要。
- [x] 2.2 若 API 字段变化，更新 OpenAPI、Orval 客户端类型、API 文档和后端聚合测试。
- [x] 2.3 保持旧 `sprintOptions` 字符串或等价兼容路径，旧数据缺状态时稳定降级。

## 3. 前端实现

- [x] 3.1 实现 Sprint 状态映射与降级逻辑，覆盖 planning、in_progress、completed、archive 和 unknown。
- [x] 3.2 在需求中心工具栏 Sprint 筛选下拉展示状态，保持默认选择、手动选择、搜索叠加、刷新和项目切换行为。
- [x] 3.3 对齐加入迭代弹窗的状态口径，不回退现有状态/容量展示。
- [x] 3.4 覆盖 loading、error、empty、disabled、long-text、mobile、dark/light 和键盘可达状态。

## 4. 验证与文档同步

- [x] 4.1 运行后端聚合/响应字段相关测试；如 API 变化，验证 OpenAPI 与客户端类型生成。
- [x] 4.2 运行前端需求中心筛选相关测试，覆盖状态展示、选择、搜索叠加、权限和异常降级。
- [x] 4.3 采集 1440px 与窄屏、深浅主题、下拉打开态、长名称和 unknown 状态的视觉证据，并记录 computed style 或等价断言。
- [x] 4.4 验证 `usage_events` 与 `request_logs` 的适用场景或不新增原因，确保不记录完整响应体、本机路径、密钥或无权对象。
- [x] 4.5 同步 REQ acceptance/trace、Change trace/test-plan/acceptance、API 文档和最终一致性说明。

## 验收返修记录

| 时间 | 反馈 | 根因状态 | 调整 | 验证 |
|---|---|---|---|---|
| 2026-09-14 18:11:58 | 筛选下拉面板与触发框距离过远；筛选面板内删除“已完成 / 归档”开关。 | confirmed | 删除筛选面板内重复的“已完成 / 归档”checkbox；移除 `showArchived` 状态；修正后置 `.rc-multi-filter-popover` CSS 覆盖，恢复相对触发器的绝对浮层定位。 | `./node_modules/.bin/tsc --noEmit` 通过；相关 Vitest 2 passed；Playwright 2 个视觉样本通过，`popoverGapPx=6`。 |

REQ 子文档一致性扫尾检查：`requirement.md`、`user-stories.md`、`business-flow.md` 和 `prototype/web/context.md` 无需更新，原因是原需求聚焦 Sprint 下拉状态展示，并未把“已完成 / 归档”checkbox 作为产品能力；`acceptance.md` 与 Change 验收证据已补充返修结果。
