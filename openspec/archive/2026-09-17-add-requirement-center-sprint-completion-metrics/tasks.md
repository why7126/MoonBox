# 任务

## 1. 前置检查与 UI 契约

- [x] 1.1 确认 REQ-0030 仍为 `in_sprint`，且 `sprint-006` scope 包含该 REQ。
- [x] 1.2 在实现前复核 `prototype/web/context.md` 与 `prototype/web/prototype.html`，确认 UI Contract 与 selector 清单。
- [x] 1.3 先交付需求中心 Sprint 指标 UI Skeleton，并完成 1440px 深浅主题首轮截图确认。

## 2. 后端与 API

- [x] 2.1 在需求中心上下文聚合中新增 `sprint_metrics.completed_count`、`sprint_metrics.total_count`、`source`、`warning`。
- [x] 2.2 从 `iterations/change/` 与 `iterations/archive/` 聚合有效 Sprint，并按 Sprint ID 去重。
- [x] 2.3 固定已归档 Sprint 与 `status: completed` 未归档 Sprint 的已完成口径，避免重复计数。
- [x] 2.4 为无 Sprint、仅规划中、仅归档、重复 ID、解析失败和权限不足补充后端测试。
- [x] 2.5 同步后端响应 schema、OpenAPI 来源、`docs/03-api-index.md` 和前端客户端类型或生成物。
- [x] 2.6 验证 request_logs 只记录接口、状态码、耗时和脱敏统计摘要。

## 3. Web UI

- [x] 3.1 在需求中心指标区渲染 Sprint 指标卡，展示“已完成 / 总体”语义。
- [x] 3.2 接入真实 `sprint_metrics` 数据，生产默认路径不得使用原型静态数字。
- [x] 3.3 覆盖 loading、empty、error、last-successful-value 和重试状态。
- [x] 3.4 确保搜索、对象类型、负责人、优先级和 Sprint 筛选不改变 Sprint 数量指标。
- [x] 3.5 确保首次加载、手动刷新和空间切换后指标跟随聚合接口刷新。
- [x] 3.6 验证 usage_events 只记录页面加载、刷新或空间切换等脱敏上下文。

## 4. 视觉与验收证据

- [x] 4.1 补充 1440px 深色主题截图，覆盖指标区、筛选区和看板列头。
- [x] 4.2 补充 1440px 浅色主题截图，覆盖指标区、筛选区和看板列头。
- [x] 4.3 补充 1024px 与 390px 响应式截图，确认文字不溢出、控件不遮挡。
- [x] 4.4 补充筛选前后 Sprint 指标不变的交互证据。
- [x] 4.5 补充错误态脱敏证据，确认不暴露本机绝对路径、内部堆栈或原始治理文档。

## 5. 治理校验

- [x] 5.1 运行 OpenSpec validate 和中文优先校验。
- [x] 5.2 运行需求中心相关后端、前端和类型检查测试。
- [x] 5.3 运行 Sprint scope 校验与 workflow sync。
- [x] 5.4 归档前回填 REQ acceptance、trace、prototype gate 和 Change trace。

## 验收返修记录

完整返修台账见 `acceptance-fixes.md`，本节仅保留可执行任务摘要。

| 时间 | 反馈 | 处置 | 验证 |
|---|---|---|---|
| 2026-09-14 18:26:44 | 指标卡高度偏高；指标名需说明图标和统一 tooltip；需求、Bug、独立 Change 改为已完成/总体；Sprint 文案改为 Sprint 并删除底部说明 | 按方案 A 保留对象指标跟随当前筛选；新增 `.rc-stat-info[data-tooltip]` 统一浮层；压缩 `.rc-stat` 高度；对象指标改为完成比例；Sprint 底部说明迁移到 tooltip | `node_modules/.bin/tsc -b`；`node_modules/.bin/vitest --run src/requirement-center.test.tsx`；Playwright 返修视觉证据 |

- [x] F2 补齐需求中心可识别的交付验证来源入口：`trace.acceptance_refs` 指向 `acceptance-fixes.md`，并在 `trace.md` 增加非空 `## 验证记录`。

REQ 子文档一致性扫尾检查：已更新 `requirement.md`、`acceptance.md`、`trace.md`、`prototype/web/context.md` 与 `prototype/web/prototype.html`；`business-flow.md`、`user-stories.md` 无需更新，原因是本次返修仅调整指标区视觉、展示文案与统计说明方式，不改变业务流程或用户故事目标。
