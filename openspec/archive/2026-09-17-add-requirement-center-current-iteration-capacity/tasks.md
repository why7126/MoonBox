## 1. UI Contract 与 Skeleton

- [x] 1.1 在 Change 设计落实 UI Contract，确认事实源优先级、页面入口、视觉 token、权限规则、Mock/API 边界和前台需求中心一致性检查。
- [x] 1.2 先实现或标记 UI Skeleton，覆盖 `CurrentIterationCapacityStrip`、`CapacityMetricItem`、状态容器、稳定选择器和占位数据边界。
- [x] 1.3 在细节实现前完成 1440px Skeleton 首轮视觉证据，确认容量区域位置、密度和层级不破坏现有统计区与看板。

## 2. 后端上下文聚合

- [x] 2.1 扩展需求中心上下文聚合，读取当前迭代 Sprint 列表、`scope_estimates[]` 与 `capacity_person_days`，生成容量摘要。
- [x] 2.2 实现单当前迭代、两个当前迭代、超过两个当前迭代、默认容量、超量和待核实状态派生。
- [x] 2.3 确保容量摘要执行项目、空间和 Sprint 权限过滤，并保持错误响应脱敏。
- [x] 2.4 补充后端聚合、权限、安全脱敏和容量状态测试。

## 3. API、客户端与观测

- [x] 3.1 同步 API 文档、OpenAPI 来源和 Orval/客户端类型，记录新增容量字段契约。
- [x] 3.2 验证容量聚合请求写入脱敏请求日志，Web 刷新/筛选/项目切换行为事件采集失败不阻断主流程。
- [x] 3.3 明确普通查询不新增 Task Trace；如实现引入异步或批量容量计算，补充 Task Trace 和流程节点设计及测试。

## 4. 前端展示

- [x] 4.1 在需求中心统计/筛选附近展示当前迭代容量，支持单项和双项并存。
- [x] 4.2 实现 normal、near_limit、over_limit、unknown、loading、refresh_failed 和权限隐藏状态。
- [x] 4.3 刷新失败时保留上一次成功容量信息并展示轻量失败提示，不清空看板。
- [x] 4.4 覆盖深浅主题、1440px、390px、长 Sprint ID、默认容量提示和待核实提示的前端测试或视觉证据。

## 5. 验证与文档同步

- [x] 5.1 运行后端聚合/权限/脱敏测试和前端组件测试。
- [x] 5.2 运行 TypeScript、OpenAPI/客户端生成校验或说明不适用原因。
- [x] 5.3 运行 OpenSpec 校验和 Sprint/REQ Workflow Sync。
- [x] 5.4 回填 Change trace、REQ acceptance 或验收记录，包含 1440px/窄屏视觉证据、computed style 摘要、Mock/API 边界和最终一致性检查。

## 验收返修记录

完整返修台账见 `acceptance-fixes.md`，本节仅保留可执行任务摘要。

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-09-14 18:24:52 | 用户要求当前迭代容量 UI 样式参考附件 HTML 的 `.capacity` 模块；移除可见文案“当前迭代容量”，保留 `aria-label`；其他模块不调整。 | 已将 `CurrentIterationCapacityStrip` 从“标题 + 卡片网格”收敛为紧凑横向容量条：左侧 Sprint ID/容量来源，中间容量数值和 5px 进度轨，右侧状态点；保留 `data-testid` 与无障碍 `aria-label`，未修改 API/DB/权限/部署。 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "current iteration capacity"` 1 passed；`./node_modules/.bin/tsc -b --pretty false` pass；新增 `capacity-modify-1440.png` 与 `capacity-modify-computed-style.json`。 |

- [x] F2 补齐需求中心可识别的交付验证来源入口：`trace.acceptance_refs` 指向 `acceptance-fixes.md`，并在 `trace.md` 增加非空 `## 验证记录`。

REQ 子文档一致性扫尾检查：已检查 `requirement.md`、`acceptance.md`、`trace.md`、`business-flow.md`、`user-stories.md`、`prototype/web/context.md`、`prototype/web/prototype.html`；本次只调整容量条视觉呈现与可见标题，不改变业务流程、用户故事、接口字段、Mock/API 边界或容量计算口径，除 `acceptance.md` 验收结果摘要外无需更新其他 REQ 子文档。
