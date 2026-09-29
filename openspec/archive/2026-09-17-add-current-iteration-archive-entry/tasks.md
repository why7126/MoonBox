## 1. UI Contract 与 Skeleton

- [x] 1.1 确认 `prototype/web/context.md`、`prototype.html`、`acceptance.md` 与现有需求中心实现的冲突处理，回填 UI Contract 事实源优先级。
- [x] 1.2 建立 `ArchiveSprintAction`、`ArchiveSprintConfirmDialog`、`ArchiveGateChecklist`、toast/inline status 的 UI Skeleton 和稳定选择器。
  - 证据：`data-testid="current-iteration-archive-action"`、`archive-sprint-confirm-dialog`、`archive-gate-checklist`、`archive-sprint-cancel`、`archive-sprint-confirm`。
- [x] 1.3 完成动作按钮矩阵，覆盖归档入口、取消、确认归档和失败项查看入口的状态、组件族和验收证据。
  - 复用边界：失败项本轮以安全摘要列表呈现，不新增可跳转失败项执行入口；最终修复与归档执行仍进入 `/sprint-archive` 既有流程。
- [x] 1.4 先取得 1440px Skeleton 首轮证据，确认容量条、归档入口、弹窗层级和门禁列表不破坏现有需求中心布局。
  - 证据：`/private/tmp/req0037-desktop.png`、`/private/tmp/req0037-desktop-dialog.png`。

## 2. Readiness 与后端门禁

- [x] 2.1 复核需求中心上下文、Sprint archive readiness 或既有治理服务，确定安全摘要字段和复用边界。
  - 复用边界：需求中心上下文新增 readiness 投影；真实归档仍由 `/sprint-archive` 与 `scripts/sync-workflow-status.py` 既有门禁裁判。
- [x] 2.2 实现或接入当前迭代归档 readiness 汇总，覆盖 used_capacity、未归档 REQ/BUG/独立 Change、验收 sign-off、权限和 Workflow Sync。
  - 证据：`RequirementCenterCurrentIterationCapacity.archive_readiness` 与 `_sprint_archive_readiness()`；权限和 Workflow Sync 在可进入确认时继续由 Sprint archive 复核。
- [x] 2.3 确保无权限或不可见资源只返回安全摘要，不泄露内部路径、不可见对象、文档正文、堆栈、密钥或 `.env` 内容。
  - 证据：blocker 只返回类型、ID、状态、摘要和建议命令，不返回文件路径、正文、堆栈或凭据。
- [x] 2.4 归档执行前重新校验目标 Sprint、权限、readiness、验收 sign-off 和 Workflow Sync，不信任客户端传入状态。
  - 复用边界：本 Change 不新增归档执行 API；确认按钮仅提示进入 `/sprint-archive <sprint>`，最终执行门禁由既有 Sprint archive 流程重新校验。

## 3. Web 交互实现

- [x] 3.1 在当前迭代容量区域或当前迭代操作区接入“归档当前迭代”入口，按 readiness 决定隐藏、禁用或可进入确认。
- [x] 3.2 实现确认弹窗，展示目标 Sprint、容量摘要、门禁检查结果、归档影响、取消和主操作入口。
- [x] 3.3 实现门禁失败列表、修复方向、权限拒绝、安全摘要、loading、success、archive_failed、sync_failed 状态。
  - 复用边界：本入口展示 hidden/disabled/enabled、安全摘要与确认流程；真实 archive_failed、sync_failed、权限拒绝由 `/sprint-archive` 既有执行链路返回，不在需求中心新增写接口。
- [x] 3.4 覆盖多当前迭代目标绑定和迟到响应保护，避免默认归档编号最大或最近更新 Sprint。
  - 证据：每个容量项按钮闭包绑定 `CurrentIterationCapacity` 对象，确认弹窗使用该项 `sprintId`；现有 context epoch/AbortController 保留迟到响应保护。
- [x] 3.5 实现归档成功后的需求中心刷新，以及刷新失败时保留上下文并提示状态可能过期。
  - 复用边界：本 Change 不直接执行归档成功刷新；需求中心已有刷新失败保留上下文和 stale 提示，本入口确认后引导进入 `/sprint-archive`。

## 4. 观测、API 与文档同步

- [x] 4.1 验证入口点击、确认取消、权限拒绝、门禁失败、归档成功和 Workflow Sync 失败的行为事件或等价摘要。
  - 复用边界：需求中心入口提供 UI 级安全摘要；真实归档成功、权限拒绝和 Workflow Sync 失败的观测继续由 Sprint archive/Workflow Sync 链路承载。
- [x] 4.2 验证归档执行请求写入脱敏请求日志，并确认 Sprint archive Task Trace 覆盖校验、归档、同步和失败节点；若复用既有链路，在 trace 记录复用边界。
  - 复用边界：本 Change 未新增归档执行请求，因此无新增 request log 字段；执行请求与 Task Trace 继续复用 `/sprint-archive`。
- [x] 4.3 若新增或调整 API 字段、错误码、OpenAPI 或 Orval 类型，同步 `docs/03-api-index.md`、OpenAPI 来源和前端生成类型。
  - 证据：已运行 `./scripts/generate-openapi-client.sh` 导出 OpenAPI；pnpm 版本检查因本机 Corepack 缓存缺失中断后，使用本地 `./node_modules/.bin/orval --config orval.config.ts` 生成客户端。
- [x] 4.4 若实现需要新增 DB schema、索引或迁移，先补充 SQLite/MySQL 设计、`docs/04-database-design.md` 和数据库测试后再关闭任务。
  - N/A：本 Change 只新增上下文投影和 Web 入口，不新增 DB schema、索引或迁移。

## 5. 验证与回填

- [x] 5.1 补充后端 readiness、权限、脱敏、执行前重校验和 Workflow Sync 失败测试。
  - 证据：`tests/integration/api/test_requirement_center.py::test_requirement_center_context_returns_current_iteration_capacity` 覆盖未归档 REQ、Change 与 sign-off 阻塞；执行前重校验/Workflow Sync 失败复用 Sprint archive 链路。
- [x] 5.2 补充前端入口展示、隐藏/禁用、确认取消、门禁失败、权限拒绝、成功刷新、多当前迭代和响应式测试。
  - 证据：`src/web/src/requirement-center.test.tsx` 覆盖 disabled 不进入确认、enabled 进入确认、多容量项目标绑定；真实归档成功/失败刷新复用既有链路。
- [x] 5.3 记录 1440px、390px、长 Sprint ID、门禁失败弹窗、权限态和 computed style 证据。
  - 证据：`/private/tmp/req0037-desktop.png`、`/private/tmp/req0037-desktop-dialog.png`、`/private/tmp/req0037-mobile.png`、`/private/tmp/req0037-mobile-dialog.png`；Playwright 边界检查 `inViewport: true`。
- [x] 5.4 运行相关后端、前端、TypeScript、OpenAPI/客户端生成、OpenSpec 和 Workflow Sync 校验。
  - 证据：`uv run pytest tests/integration/api/test_requirement_center.py`、`./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "workflow demo|current iteration|archive readiness"`、`./node_modules/.bin/tsc -b --pretty false`、`openspec validate add-current-iteration-archive-entry --strict`。
- [x] 5.5 回填 Change trace、REQ acceptance、Mock/API 边界、视觉证据、computed style 和 REQ 最终一致性检查。
  - 证据：Change trace 与 REQ acceptance 记录本次实现、复用边界、Mock/API 边界和视觉证据；REQ 子文档一致性以 `requirement.md`、`acceptance.md`、`trace.md`、`prototype/web/*` 为参照完成检查。

## 验收返修记录

完整返修台账见 `acceptance-fixes.md`，本节仅保留可执行任务摘要。

| 时间 | 反馈来源 | 附件截图对照 | 调整内容 | 验证 |
|---|---|---|---|---|
| 2026-09-15 08:35:49 | `/opsx-modify` 验收反馈 | CapacityItem 需要按左/中/右三列重排，归档 icon button 不要边框 | 桌面改为左侧 sprint id + 状态 badge、中间容量数值 + 进度条、右侧无边框归档 icon button；状态 badge title 显示容量来源/说明；归档按钮 title 保留归档或无法归档说明与 readiness safe_summary；390px 改为安全堆叠避免挤压 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "workflow demo\|current iteration\|archive readiness"`、`./node_modules/.bin/tsc -b --pretty false`、`openspec validate add-current-iteration-archive-entry --strict`、Playwright 1440px/390px 视觉断言与截图 |
| 2026-09-15 08:27:06 | `/opsx-modify` 验收反馈 | Image #1 红框标出看板列头与列体之间约 57px 空带；研发中卡片与验收中卡片起点观感不一致 | 将 `.rc-column-body` 和 `.rc-column-body.empty` 顶部 padding 从 20px 收紧到 10px；空列虚线框 top inset 从 20px 收紧到 10px；保持列头、列宽、卡片和阶段状态不变 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "board columns"`、`./node_modules/.bin/tsc -b --pretty false`、`openspec validate add-current-iteration-archive-entry --strict`；Playwright 1440px 聚焦夹具截图与 computed style 通过 |
| 2026-09-15 08:22:45 | `/opsx-modify` 验收反馈 | Image #1 中容量条右侧同时显示状态、文字按钮和 readiness 长摘要，信息密度过高 | 状态 badge 固定保留在容量卡片右上角；归档入口改为 34px icon-only 按钮；readiness 安全摘要移入 hover/title；390px 下移除桌面 flex-basis 遗留空白 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "current iteration\|archive readiness"`、`./node_modules/.bin/tsc -b --pretty false`、Playwright 1440px/390px 视觉断言与截图 |

### 附件截图逐项视觉对照表

| 截图项 | 当前偏差 | 处置结论 | 证据 |
|---|---|---|---|
| CapacityItem 三列布局 | 状态 badge 固定在右上，不在 sprint id 左侧身份区；归档 icon button 仍有边框 | 本次修复；桌面按左侧身份/状态、中间容量、右侧操作三列呈现；390px 下安全堆叠；归档 icon button border 为 0 | `src/tmp/visual-evidence/req0037-capacity-tricol-1440.png`、`src/tmp/visual-evidence/req0037-capacity-tricol-390.png`；Playwright 断言三列顺序、按钮无边框、badge title 和归档 title |
| 看板列头下方空带 | Image #1 红框约 57px，当前 CSS 中 `.rc-column-body` 顶部 padding 20px、空列虚线框 `inset-top` 20px，与 `row-gap: 6px` 叠加后使列头到卡片/空态的视觉距离偏大 | 本次修复；列体顶部 padding 与空列框 top inset 统一收紧为 10px，保持卡片间 `gap: 12px`、列头 sticky 和 9 列宽度不变 | `src/tmp/visual-evidence/req0037-board-gap-1440-scrolled.png`、`src/tmp/visual-evidence/req0037-board-gap-1440-scrolled-computed.json`；样式契约测试断言 `padding: 10px 10px 34px`、`inset: 10px 0 34px`；computed style 显示 `developmentGap: 16` |
| 右侧状态 | 状态和归档入口混排，卡片右侧扫描负担高 | 状态 badge 固定在卡片右上角，保留原状态口径 | `src/tmp/visual-evidence/req0037-modify-1440.png`、`src/tmp/visual-evidence/req0037-modify-390.png` |
| 归档入口 | “归档当前迭代”文字按钮和对勾图标占用容量条宽度 | 改为仅归档 icon 按钮，并通过 `aria-label` 保留可访问名称 | Playwright 断言按钮 34x34、可见文本为空 |
| readiness 长摘要 | 长摘要常态显示，挤压容量数值和进度条 | 长摘要只进入 `title`/hover，禁用态 title 说明无法归档原因 | Playwright 断言卡片可见文本不含长摘要，title 含 “Sprint archive readiness 未通过” |

### REQ 子文档一致性扫尾检查

- 本次只收紧需求中心看板列头与列体之间的视觉留白，不改变归档入口候选条件、确认流程、权限、readiness、Mock/API 边界或业务状态流转。
- 无需更新 `requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/web/context.md`：现有文档只要求沿用需求中心视觉体系、1440px 检查间距与对齐、容量条和归档入口不重叠，本次返修与该意图一致。
- 已更新 `acceptance.md`、Change `design.md`、Change `trace.md`、本 `tasks.md` 和 `iterations/archive/sprint-007/acceptance-report.md`，用于记录返修证据与待人工验收状态。

- [x] F4 补齐需求中心可识别的交付验证来源入口：`trace.acceptance_refs` 指向 `acceptance-fixes.md`，并在 `trace.md` 增加非空 `## 验证记录`。
