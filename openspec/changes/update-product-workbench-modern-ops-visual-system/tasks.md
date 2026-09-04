## 1. UI Contract 与 Skeleton

- [x] 1.1 复核 REQ-0023 六件套、附件视觉方向、prototype context、AC-PROTOTYPE 和横切 AC，确认实现范围与非目标。
- [x] 1.2 在实现前建立现代 Ops token 草案，覆盖深浅主题、字体、色彩、状态、间距、圆角、阴影、控件高度、图标尺寸和动效。
- [x] 1.3 完成工作台 Shell 与需求中心 UI Skeleton，覆盖 Sidebar、Header、Stats、Toolbar、Kanban、Card、Drawer、Modal 和 Toast 插槽。
- [x] 1.4 先完成 1440px Skeleton 首轮视觉证据，确认布局密度、层级、滚动边界和深浅主题方向后再进入细节实现。

## 2. 设计系统迁移

- [x] 2.1 更新设计系统 token 与 CSS 变量映射，区分品牌层、工作台层、组件层和语义状态层。
- [x] 2.2 更新设计系统预览页，展示现代 Ops 组件样式基线和深浅主题。
- [x] 2.3 更新或补充设计系统校验，覆盖硬编码颜色、绕过确认弹窗、toast、状态标签和主按钮样式的风险。
- [x] 2.4 更新 `rules/ui-design.md` 或长期设计系统文档，明确双品牌分层与现代 Ops 工作台规则。

## 3. 需求中心与工作台 Shell

- [x] 3.1 迁移登录后工作台 Shell 的 Sidebar、品牌区、导航分组、active 态、折叠态、用户菜单和主题切换视觉。
- [x] 3.2 迁移需求中心 Header、统计卡、Toolbar、搜索、segmented、筛选 Popover、active badge 和刷新按钮。
- [x] 3.3 迁移 9 阶段 Kanban、列头、空列、卡片状态边、meta pill、文档分隔区、进度/阻塞提示和 footer 动作分区。
- [x] 3.4 迁移右侧 Markdown/任务/AI 抽屉、确认弹窗和 fixed toast，确保浮层退出路径与 click outside capture 阶段验收可覆盖。

## 4. 管理后台一致性

- [x] 4.1 将后台 CRUD 列表模板、状态标签、筛选、分页、toast 和确认弹窗对齐现代 Ops token。
- [x] 4.2 验证后台列表分页 DOM、筛选结果、空态、fixed toast 和禁止 `window.confirm` 横切 AC。
- [x] 4.3 验证后台弹窗宽度、低视口滚动、遮罩滚动边界和 computed style，不让通用 `modal-card` 覆盖专属宽度。

## 5. 验证与文档同步

- [x] 5.1 运行设计系统校验、前端聚焦测试和相关 lint/build 校验。
- [x] 5.2 产出 1440px 与窄屏视觉证据，覆盖默认首屏、侧边栏、用户菜单、筛选 Popover、看板横向滚动、空列、错误态、卡片 hover、右侧抽屉、AI 入口和深浅主题。
- [x] 5.3 记录 computed style 证据，覆盖字体、字号、行高、间距、圆角、边框、背景、颜色、z-index、overflow 和 position。
- [x] 5.4 回填 Change trace、acceptance、linked REQ acceptance/trace 和必要长期文档，确认 Mock/API 边界、产品数据采集 N/A 和 REQ 最终一致性。

## 验收返修记录

### 2026-08-31 09:45 opsx.modify

- 反馈：继续贴近附件视觉，重点优化移动端挤压、Kanban 空列承载感、筛选 Popover 密度和右下 AI 入口位置。
- 附件截图逐项视觉对照：用户附件为 1440+ 深色需求中心看板；对照当前 Playwright 证据后确认偏差集中在移动端挤压、空列承载、筛选面板密度和 FAB 贴边位置。
- 调整：移动端隐藏版本 badge、压缩 Header/Toolbar；筛选 Popover 降低高度和间距；空列增加轻量虚线承载区；AI 入口调整为更贴近右下角的稳定 FAB。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx src/design-system.test.tsx src/admin-user-management.test.tsx`、`node_modules/.bin/tsc --noEmit`、`node_modules/.bin/vite build` 通过。
- 视觉证据：`openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次为同一 UI Contract 下的视觉密度与响应式返修；`acceptance.md`、`trace.md` 需回填新证据和返修摘要。

### 2026-08-31 14:42 opsx.modify

- 反馈：上一轮视觉返修整体效果不佳已撤回；本次仅调整需求中心右侧内容标题区，要求对齐后台用户/空间管理的 `admin-page-head` 内容页标题布局，去掉标题区底部分隔线、sticky 顶栏感、半透明背景和 blur。
- 范围边界：不调整指标卡、Kanban 列头、前台左上品牌区和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户验收反馈 / 后台用户空间管理参照 | `/requirements?mock=workflow`，1440px，深色主题，默认看板首屏 | `.rc-page-header` 对照后台 `.admin-page-head` | 右侧内容标题区采用后台内容页标题块布局，无底部分隔线、无 sticky 顶栏感、无半透明背景和 blur | 返修前 `.rc-page-header` 使用 sticky、底部分隔线、半透明背景和 `backdrop-filter`，视觉上更像固定顶栏 | `position`、`border-bottom`、`background`、`backdrop-filter`、垂直对齐和动作区间距 | CSS 选择器检查、Playwright 1440px 截图、computed style | 本次仅修复标题区；指标卡、Kanban 列头、左上品牌区保持不动 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：`.rc-page-header` 改为普通内容页标题块，使用 `align-items: flex-end`、`gap: 24px`、透明背景和 `18px 28px 0` 内边距；移除 sticky、`z-index`、底部分隔线、半透明背景和 blur。
- 测试：新增 `requirement-center.test.tsx` 标题区样式保护，锁定不再出现 topbar treatment。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；视觉证据已刷新。
- computed style 摘要：`.rc-page-header` 为 `position: static`、`border: 0px none`、`background: rgba(0, 0, 0, 0)`、`z-index: auto`、`gap: 24px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅收敛既有 UI Contract 下的标题区布局参照；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 14:58 opsx.modify

- 反馈：前台左上角 Logo、产品名、副标题与后台有差异；用户确认副标题保留前台业务语义，但统一视觉样式。
- 范围边界：仅调整前台左上品牌区；不调整需求中心右侧标题区、指标卡、Kanban 列头和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户验收反馈 / 后台 AdminSidebar 参照 | `/requirements?mock=workflow` 与 `/admin`，1440px，深色主题 | 前台 `.rc-brand-mark`、`.rc-brand-copy`、`.rc-version-badge` 对照后台 `.admin-mark`、`.admin-brand strong/small/em` | Logo、产品名、副标题和版本 badge 视觉规格与后台一致；副标题文案继续表达前台工作台业务语义 | 返修前前台产品名字号写死 17px，副标题使用 `em` 且样式与后台 `small` 不完全一致，版本 badge right 与圆角不同 | 字号、DOM 语义、字体族、行高、uppercase、版本 badge 位置和圆角 token | TSX/CSS 检查、Playwright 截图、computed style | 本次修复品牌区视觉；保留 `OPS WORKBENCH`，不改其它区域 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：前台品牌副标题从 `em` 改为 `small`；产品名使用 `--rc-text-lg`；副标题对齐后台字体、字号、行高、uppercase；版本 badge 对齐后台 right 与圆角 token。
- 测试：新增前台品牌区与后台品牌视觉规格对齐断言，并保留 `OPS WORKBENCH` 业务语义断言。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx src/admin-user-management.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；视觉证据已刷新。
- computed style 摘要：`.rc-brand-mark` 与 `.admin-mark` 均为 30px；`.rc-brand-copy strong` 与 `.admin-brand strong` 均为 18px 等宽字体；`.rc-brand-copy small` 与 `.admin-brand small` 均为 9px 等宽字体、`line-height: 11.7px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次不改变品牌分层策略或业务流程，仅修正既有 UI Contract 下的前台品牌区视觉一致性；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 15:10 opsx.modify

- 反馈：前台左上角版本号高度、展开与收起按钮与后台有差异。
- 范围边界：仅调整前台左上版本号高度和展开/收起按钮；不调整品牌文案、需求中心右侧标题区、指标卡、Kanban 列头和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户验收反馈 / 后台 AdminSidebar 参照 | `/requirements?mock=workflow` 与 `/admin`，1440px，深色主题 | 前台 `.rc-version-badge`、`.rc-collapse` 对照后台 `.admin-brand em`、`.admin-collapse` | 版本号高度与后台一致；展开/收起按钮基础态和折叠态视觉与后台一致 | 返修前前台版本号显式 `line-height` 导致高度更矮；前台 collapse 有额外 `z-index`，折叠态背景使用面板色 | 高度、line-height、z-index、折叠态背景 | CSS 检查、Playwright 截图、computed style | 本次修复版本号高度和 collapse 按钮；其它区域不变 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：移除 `.rc-version-badge` 显式 `line-height`；移除 `.rc-collapse` 与折叠态额外 `z-index`；为 `.rc-collapse` 补齐 `gap: 11px` 和 `line-height: var(--rc-leading-label)`；折叠态背景改为 `var(--rc-sidebar-bg)`。
- 测试：扩展前台品牌区一致性测试，覆盖版本号高度约束、collapse 基础态尺寸/背景/line-height 和折叠态背景。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx src/admin-user-management.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；视觉证据已刷新。
- computed style 摘要：`.rc-version-badge` 与 `.admin-brand em` 高度均为 `19.0469px`；`.rc-collapse` 与 `.admin-collapse` 均为 24px、`line-height: 16.9px`、`gap: 11px`、透明背景、`z-index: auto`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅为前台品牌区内版本号和按钮视觉一致性修正，不改变业务流程、原型意图或品牌文案；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 15:48 opsx.modify

- 反馈：九阶段看板的视觉设计与附件有差异。
- 范围边界：仅调整需求中心九阶段看板视觉；不调整左侧品牌区、右侧内容标题区、指标卡、筛选区和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户验收反馈 / 附件九阶段看板参照 | `/requirements?mock=workflow`，1440px，深色主题，默认看板首屏 | `.rc-board`、`.rc-column`、`.rc-column-head`、`.rc-column-head > span`、`.rc-column-body` | 九阶段列更接近附件的大盘比例：列更宽、列距更疏、列头更高，标题/副标题/count 层级更清晰，空列有承载感 | 返修前列宽 258px、列距 12px、列头 58px、count 28px、列体 padding 9px，整体更像紧凑任务看板 | 列宽、列间距、列头高度、标题/副标题字号、count 状态牌、列体 padding、空列承载高度 | CSS 检查、Playwright 截图、computed style | 本次修复九阶段看板视觉比例；其它区域保持不变 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：九阶段列宽从 258px 调整为 320px，列间距从 12px 调整为 16px；列头高度调整为 80px，标题 18px、副标题 12px；count 状态牌调整为 38px；列体 padding 调整为 14px，空列承载高度调整为 148px。
- 测试：更新九阶段看板比例测试，覆盖列宽、列距、列头高度、标题/副标题字号、count 状态牌、列体 padding 和空列承载高度。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；视觉证据已刷新。
- computed style 摘要：`.rc-board` 宽度 `3008px`、gap `16px`；`.rc-column` 宽度 `320px`、高度 `560px`；`.rc-column-head` 高度 `80px`；count 状态牌 `38px`；`.rc-card` 宽度 `290px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅为既有九阶段 UI Contract 下的视觉比例返修，不改变阶段定义、流转规则、业务流程或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 16:03 opsx.modify

- 反馈：用户补充两张截图，Image #1 与 Image #2 仍有较大差异；当前九阶段看板仍偏实线面板和后台表格列，未充分贴近附件暗场流转大盘。
- 范围边界：继续仅调整需求中心九阶段看板视觉；不调整左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| Image #1 参考截图 | 需求中心九阶段看板，深色主题，横向看板区域 | 当前实现 Image #2 与 `.rc-board`、`.rc-column`、`.rc-column-head`、`.rc-card` | 暗场浮动看板：列实线感弱，列头无强分隔，空列大面积虚线承载，count 为紧凑状态牌，卡片更接近附件的柔边框和金色状态线 | Image #2 中列边界过实、列头分隔线明显、空列虚线区偏局部、count 方框过硬、Requirement 卡片状态线偏蓝 | 列边框透明度、列头分隔线、列头背景、空列承载高度、count 尺寸/圆角/底色、卡片边框和状态线 | 用户截图对照、CSS 检查、Playwright 1440px 截图、横向滚动截图、computed style | 本次修复九阶段暗场看板质感；AI 入口等非本轮区域保持不变 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-board-scrolled-1440.png`、`computed-styles.json` |

- 调整：弱化 `.rc-column` 实线面板感并移除强 box-shadow；`.rc-column-head` 去掉底部分隔线并改为透明暗场标题区；count 从 38px 方形牌改为 26px 高紧凑胶囊状态牌；空列承载高度扩大到 320px；卡片增加高度和 padding，Requirement 卡片左侧状态线改为金色，卡片边框与背景更柔和。
- 测试：更新九阶段看板视觉测试，覆盖弱化列边框、列头无分隔、count 胶囊状态牌、列体 padding、空列承载高度和暗场背景。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；视觉证据已刷新。
- computed style 摘要：`.rc-column-head` border 为 `0px none`、background 为透明；`.rc-column-head > span` 高度 `26px`；`.rc-column-body` padding `18px`；`.rc-card` 高度 `150px`、宽度 `282px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仍为既有九阶段 UI Contract 下的视觉材质返修，不改变阶段定义、流转规则、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 16:40 opsx.modify

- 反馈：用户最新截图确认九阶段看板仍像深色表格列，原因集中在 `.rc-column` 与 `.rc-column-body` 仍承担完整面板边界，未达到附件“暗场标题 + 卡片/空列承载”的视觉表达。
- 范围边界：继续仅调整需求中心九阶段看板视觉；不调整左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新截图 | 需求中心九阶段看板，深色主题，1440px 左右桌面视口，默认看板区域 | `.rc-column`、`.rc-column-head`、`.rc-column-body`、`.rc-card` | 列容器退为暗场布局容器；列头浮在暗场；非空列靠卡片表达承载；空列由列体自身形成大面积虚线框；count 保持紧凑状态牌 | 返修前仍有完整列面板和竖向边界，空列虚线框被实心列容器包住，整体仍像后台表格列 | 列容器边框/背景、列头定位、列体边框/背景、空列承载框、卡片状态线和尺寸 | 用户截图对照、CSS 检查、Playwright 1440px/空列筛选截图、computed style | 本次修复：取消完整列面板，非空列仅保留卡片和透明列体，空列使用 body 自身虚线承载框 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-one-card-empty-columns-1440.png`、`requirements-board-scrolled-1440.png`、`computed-styles.json` |

- 调整：`.rc-column` 改为透明布局容器，移除边框、背景和 sticky 面板感；`.rc-column-head` 改为相对定位暗场标题区，去掉伪背景；`.rc-column-body` 非空态移除整列边框和背景，仅保留布局间距；`.rc-column-body:empty` 自身成为大面积虚线承载框；卡片高度、padding 和金色状态线进一步贴近附件。
- 测试：更新九阶段看板视觉测试，覆盖列容器透明化、列头非 sticky、空列 body 自承载、非空列无整列边框、卡片金色状态线和紧凑 count。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据已刷新，新增单卡片/空列截图。
- computed style 摘要：`.rc-column` border/background 为 `0px none`/透明；`.rc-column-head` 为 `position: relative`、`border: 0px none`、透明背景；`.rc-column-body` border/background 为 `0px none`/透明；`.rc-column-body:empty` 为 `300px × 430px` 大面积虚线承载框；`.rc-card` 为 `300px × 162px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仍为既有九阶段 UI Contract 下的视觉结构表达返修，不改变阶段定义、流转规则、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 16:57 opsx.modify

- 反馈：用户指出九阶段列头仍有差异，包括标题字体太大、列头上间距太大、空列缺少阶段差异化占位文案、空列展示结构与非空列不一致。
- 范围边界：继续仅调整需求中心九阶段看板视觉；不调整左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| Image #1 参考截图 | 需求中心九阶段看板，深色主题，列头与空列状态 | 当前实现 Image #2、`.rc-column-head`、`.rc-column-body`、空列 DOM | 列头字号更克制、顶部间距更紧；空列显示阶段差异化占位文案，且与非空列共用列体结构 | 返修前列头标题 18px、padding 上方 16px；空列依赖 `.rc-column-body:empty`，没有真实文案节点 | 字号、padding、空列文案、空列 DOM 结构、空列与非空列一致性 | 用户截图对照、CSS 检查、React DOM 检查、Playwright 空列截图、computed style | 本次修复：下调列头字号和间距；为空列渲染真实 stage-specific 占位内容；空列改为 `.rc-column-body.empty` 同结构列体 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`Stage` 定义增加 `emptyTitle`、`emptyHint`、`emptyDetail`；9 个阶段分别提供不同占位文案；空列渲染 `.rc-empty-stage` 真实节点；列头高度从 78px 收为 58px，标题从 18px 收为 16px，副标题从 12px 收为 11px，列头上 padding 从 16px 收为 6px。
- 测试：新增空列真实占位文案测试，更新九阶段看板样式测试，覆盖列头字号/间距、`.rc-column-body.empty` 和 `.rc-empty-stage`。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据已刷新，computed style 已记录 `.rc-column-head`、`.rc-column-head h2`、`.rc-column-head p`、`.rc-column-body.empty` 和 `.rc-empty-stage`。
- computed style 摘要：`.rc-column-head` 高度 `58px`、padding `6px 6px 10px`；标题 `16px`；副标题 `11px`；`.rc-column-body.empty` 为 `300px × 434px` 虚线承载框；`.rc-empty-stage` 为真实居中占位节点。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次为空列视觉空态与列头密度返修，不改变阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 17:07 opsx.modify

- 反馈：用户对比附件后确认九阶段看板只剩空列颜色偏差，当前空列底色仍偏蓝灰抬升，斜线纹理和金色虚线边框对比偏强。
- 范围边界：继续仅调整需求中心九阶段看板空列颜色；不调整列头字号、列头间距、空列文案、非空列卡片、左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| Image #1 / Image #2 对照 | 需求中心九阶段看板，深色主题，单卡片与空列并存 | `.rc-column-body.empty` 背景、斜线纹理、虚线边框 | 空列底色更贴近附件暗场，降低蓝灰抬升感；斜线纹理与金色虚线保持低对比 | 返修前空列使用 `var(--rc-raised) 48%` 背景、`var(--rc-border-soft) 42%` 斜线和 `var(--rc-border) 70% + accent` 虚线，视觉仍比附件更亮更蓝 | 空列背景混色、纹理透明度、虚线边框金色占比 | 用户截图对照、CSS 检查、Playwright 单卡片/空列截图、computed style | 本次仅下调空列底色抬升、斜线透明度和虚线边框金色对比；其它区域保持不变 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`.rc-column-body.empty` 背景从 `rc-raised 48%` 改为更贴近暗场的 `rc-panel 14%`；斜线纹理从 `rc-border-soft 42%` 降为 `24%`；虚线边框从 `rc-border 70% + accent` 改为 `rc-border-soft 86% + accent`，弱化金色边框对比。
- 测试：更新九阶段看板视觉测试，锁定空列低对比暗场背景、斜线纹理和弱金色虚线边框。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、Playwright 视觉证据、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、`python scripts/validate-openspec-language.py` 通过；diff check 待收尾运行。
- computed style 摘要：`.rc-column-body.empty` 为 `300px × 434px`，边框为 `1px dashed color(srgb 0.209647 0.205726 0.208549)`；空列背景层已从高抬升蓝灰改为低抬升暗场混色，斜线纹理透明度已降低。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅为空列颜色与低对比材质返修，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 17:35 opsx.modify

- 反馈：用户确认空列仍然是同样问题；上一轮小幅调色后，空列承载框仍像独立蓝灰面板，斜线纹理和完整矩形框仍保留较强视觉存在感。
- 范围边界：继续仅调整需求中心九阶段看板空列视觉；不调整空列文案、列头字号、列头间距、非空列卡片、左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新截图 | 需求中心九阶段看板，深色主题，单卡片与多空列并存 | `.rc-column-body.empty` 承载框、背景和边框 | 空列背景接近页面暗场；移除或极弱化斜线纹理；虚线边框为低对比冷灰且不混入金色，使空列不再像独立蓝灰面板 | 返修前仍绘制完整大面积斜线纹理和虚线矩形框，即使混色降低，整体视觉结构仍与上一版相似 | 空列承载框存在感、斜线纹理、边框金色混色、背景抬升感 | 用户截图对照、CSS 检查、Playwright 单卡片/空列截图、computed style | 本次修复：移除空列斜线纹理，空列背景贴近页面暗场，虚线边框改为低对比冷灰且不含金色 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`.rc-column-body.empty` 移除 `repeating-linear-gradient` 斜线纹理；背景改为 `color-mix(in srgb, var(--rc-bg) 94%, transparent)`；虚线边框改为 `color-mix(in srgb, var(--rc-border-soft) 46%, transparent)`，不再混入 `var(--rc-accent)`。
- 测试：更新九阶段看板视觉测试，锁定空列不再包含斜线纹理和金色边框混色。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、Playwright 视觉证据、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、`python scripts/validate-openspec-language.py` 和 diff check 通过。
- computed style 摘要：`.rc-column-body.empty` 背景为 `color(srgb 0.0392157 0.0509804 0.0784314 / 0.94)`，边框为 `1px dashed color(srgb 0.105882 0.129412 0.188235 / 0.46)`；空列 CSS 不再包含 `repeating-linear-gradient` 或 `var(--rc-accent)` 边框混色。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仍为空列视觉材质返修，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 17:44 opsx.modify

- 反馈：用户确认空列仍未符合预期，视觉上与未改类似；同时指出上一轮返修把九阶段列头冻结能力改没了。
- 范围边界：仅修正九阶段列头冻结与空列承载框形态；不调整列头字号、列头间距、空列文案、非空列卡片、左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新反馈 | 需求中心九阶段看板，深色主题，纵向滚动与空列状态 | `.rc-column-head`、`.rc-column-body.empty` | 列头保持冻结，但无强分隔线和实心面板背景；空列不再绘制完整大矩形面板，仅保留低存在感暗场占位与现有阶段文案 | 返修前 `.rc-column-head` 为 `position: relative`，测试还禁止 sticky；空列虽移除斜线但仍保留完整大矩形承载框 | 列头冻结能力、空列完整框线、空列面板感 | 用户反馈、CSS 检查、Vitest 样式契约、Playwright 截图、computed style | 本次修复：恢复列头 sticky；空列取消大虚线框和独立背景，仅保留文案占位结构 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`.rc-column-head` 恢复 `position: sticky; top: 0;`，保持 `border-bottom: 0` 和透明背景；`.rc-column-body.empty` 改为 `border: 0`、`background: transparent`，不再绘制完整大矩形承载框。
- 测试：更新九阶段看板视觉测试，恢复列头 sticky 断言，并锁定空列无边框、无背景、无斜线纹理、无金色边框混色。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、Playwright 视觉证据、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、`python scripts/validate-openspec-language.py` 和 diff check 通过。
- computed style 摘要：`.rc-column-head` 为 `position: sticky`、`z-index: 2`、透明背景、无边框；`.rc-column-body.empty` 为 `border: 0px none`、`background: rgba(0, 0, 0, 0)`，截图中空列仅保留低存在感阶段文案。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次为九阶段看板视觉与交互能力返修，恢复既有列头冻结能力并降低空列承载框存在感，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 17:52 opsx.modify

- 反馈：用户截图确认列头冻结后出现内容穿透，第一列任务卡内容滚到冻结列头下方并与“采集池 / Capture...”叠字。
- 范围边界：仅修正九阶段列头冻结遮挡层；不调整空列文案、空列无框状态、列头字号、列头间距、非空列卡片、左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新截图 | 需求中心九阶段看板，深色主题，纵向滚动后列头冻结 | `.rc-column-head` sticky 层与任务卡滚动内容 | 列头冻结时遮挡下方滚动内容，避免卡片文字与列头叠字；同时保持无强分隔线和无实心面板感 | 返修前 `.rc-column-head` 为 `position: sticky` 但 `background: transparent`，任务卡文本会透到列头区域下方 | sticky 遮挡背景、文字重叠、冻结层防穿透 | 用户截图、CSS 检查、Vitest 样式契约、Playwright 截图、computed style | 本次修复：列头保持 sticky，背景改为页面暗场 `var(--rc-bg)`，继续无分隔线 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`.rc-column-head` 保持 `position: sticky; top: 0; z-index: 2`，将背景从透明改为 `var(--rc-bg)`，用页面暗场遮挡滚动内容；继续保留 `border-bottom: 0`。
- 测试：更新九阶段看板视觉测试，锁定列头 sticky、无分隔线、暗场遮挡背景。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、Playwright 视觉证据、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、`python scripts/validate-openspec-language.py` 和 diff check 通过。
- computed style 摘要：`.rc-column-head` 为 `position: sticky`、`background: rgb(10, 13, 20)`、`border: 0px none`、`z-index: 2`；`.rc-column-body.empty` 仍为 `border: 0px none`、透明背景。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正 sticky 列头遮挡层防穿透，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 18:00 opsx.modify

- 反馈：用户截图确认仍存在 sticky 冻结边界穿透，任务卡顶部会从列头冻结边界上方/后方露出，形成卡片被列头切开的视觉问题。
- 范围边界：仅修正九阶段 sticky 列头冻结边界遮罩；不调整空列文案、空列无框状态、列头字号、列头间距、非空列卡片样式、左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新截图 | 需求中心九阶段看板，深色主题，纵向滚动后列头冻结边界 | `.rc-column-head` 与其遮罩层、滚动中的 `.rc-card` | sticky 列头上下边界应遮挡滚动卡片顶部和文字，避免卡片露在冻结边界上方或后方；仍保持无强分隔线和无实心面板感 | 返修前列头自身有暗场背景，但遮挡范围仅限自身盒子，卡片滚动经过边界时仍从上/下边缘露出 | sticky 边界缓冲区、遮罩范围、滚动穿透证据 | 用户截图、CSS 检查、Vitest 样式契约、Playwright 纵向滚动截图、computed style 伪元素 | 本次修复：增加 `.rc-column-head::before` 暗场遮罩，向上下边界扩展，覆盖卡片经过冻结边界时的露出区域 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png`、`computed-styles.json` |

- 调整：为 `.rc-column-head` 增加 `::before` 遮罩，`inset: -28px -10px -24px`，背景使用 `var(--rc-bg)`，`z-index: -1`，不增加边框、阴影或实心面板样式；仅将 `.rc-column-body` 顶部 padding 从 `14px` 微调为 `20px`，避免首张卡片撞到冻结层；证据脚本新增 1440×430 纵向滚动后的 `requirements-sticky-head-boundary-1440.png`，并采集 `.rc-column-head::before` computed style 与 sticky 边界滚动指标。
- 测试：更新九阶段看板视觉测试，锁定 sticky 列头遮罩的 inset、背景和 pointer-events。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据已刷新，`requirements-sticky-head-boundary-1440.png` 在 1440×430 视口、`.rc-board-wrap.scrollTop=120` 下生成。
- computed style 摘要：`.rc-column-head::before` 为 `340px × 110px`、`background: rgb(10, 13, 20)`、`z-index: -1`；`.rc-column-body` padding 为 `20px 10px 14px`；sticky 边界指标记录 `boardWrapScrollTop: 120`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅增强 sticky 列头冻结边界防穿透遮罩，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 18:27 opsx.modify

- 反馈：用户继续确认九阶段 sticky 列头冻结边界仍有穿透，上一轮单列列头遮罩未覆盖列间空隙和列头上方 padding 区域。
- 范围边界：继续仅修正九阶段 sticky 列头冻结边界穿透；不调整空列文案、空列无框状态、列头字号、列头间距、非空列卡片样式、左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新反馈与 1440×430 复验证据 | 需求中心九阶段看板，深色主题，`.rc-board-wrap.scrollTop=120` | `.rc-board-wrap`、`.rc-board-layer`、`.rc-board-head-mask`、`.rc-column-head`、滚动中的 `.rc-card` | sticky 冻结区应形成横向连续暗场遮罩带，覆盖列头上下边界、列间空隙和看板顶部 padding，卡片滚动经过时不露出 ID、标题或顶部文字 | 上一轮 `.rc-column-head::before` 为单列局部遮罩，且 board 级伪元素在当前绘制顺序中未稳定压住卡片 | 连续遮罩层、绘制层级、顶部 padding 穿透、列间空隙 | 用户截图、CSS 检查、Vitest 样式契约、Playwright 1440×430 纵向滚动截图、computed style 与滚动指标 | 本次修复：新增真实 `.rc-board-head-mask`，与 `.rc-board` 共享 `.rc-board-layer` 网格区域，遮罩层 `z-index: 2`，列头 `z-index: 3`，列体 `z-index: 0` | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png`、`computed-styles.json` |

- 调整：新增 `.rc-board-layer` 和真实 `.rc-board-head-mask`，移除 `.rc-column-head::before` 单列扩展遮罩；`.rc-board-head-mask` 宽度 `max(100%, var(--rc-board-width))`、高度 `110px`、`top: -18px`、背景 `var(--rc-bg)`，覆盖整条九阶段冻结边界；`.rc-column-head` 保持 sticky 与页面暗场背景，层级提升到 `z-index: 3`。
- 测试：更新九阶段看板视觉测试，锁定 board 级连续遮罩 DOM、遮罩尺寸、sticky top、层级关系和移除单列列头伪元素。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx` 通过；Playwright 视觉证据已刷新，`requirements-sticky-head-boundary-1440.png` 显示卡片 ID/标题不再从列头上方露出。
- computed style 摘要：`.rc-board-head-mask` 为 `3008px × 110px`、`position: sticky`、`top: -18px`、`background: rgb(10, 13, 20)`、`z-index: 2`；`.rc-column-head` 为 `z-index: 3`；sticky 边界指标记录 `maskTop: 277.375`、`maskBottom: 387.375`、`boardWrapScrollTop: 120`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅改变看板 sticky 遮罩实现策略，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 18:52 opsx.modify

- 反馈：用户截图确认连续遮罩方案产生副作用：任务卡信息被遮住，且滚动到一定位置后部分列头表现为随内容滚动。
- 范围边界：仅修正九阶段 sticky 列头冻结方案副作用；不调整空列文案、空列无框状态、列头字号、列头间距、非空列卡片样式、左侧品牌区、右侧内容标题区、指标卡、筛选区、AI 入口和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户 Image #1 / Image #2 | 需求中心九阶段看板，深色主题，纵向滚动后 | `.rc-board-head-mask`、`.rc-board`、`.rc-column-head`、`.rc-column-body`、`.rc-card` | 卡片信息完整展示；所有列头冻结位置一致；卡片从列头下方开始显示，不依赖大面积遮罩盖住内容 | 连续遮罩方案会遮住卡片中上部信息，并在滚动叠加时造成列头与内容节奏不一致 | 卡片可见性、列头冻结一致性、纵向滚动责任归属 | 用户截图、CSS 检查、Vitest 样式契约、Playwright 1440×430 列体滚动截图、computed style 与滚动指标 | 本次修复：移除 `.rc-board-head-mask` 与 `.rc-board-layer`，看板改为 header/body 分离，两行 grid；`.rc-board-wrap` 仅横向滚动，`.rc-column-body` 纵向滚动 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png`、`computed-styles.json` |

- 调整：`RequirementCenterPage.tsx` 将九阶段看板拆为 9 个 `.rc-column-head` 和 9 个 `.rc-column` 列体；移除独立 `.rc-board-head-mask` DOM；`.rc-board` 使用 `grid-template-rows: auto minmax(260px, 1fr)`；`.rc-board-wrap` 改为横向滚动、纵向隐藏；`.rc-column-body` 改为列体内部纵向滚动。
- 测试：更新九阶段看板视觉测试，锁定 header/body 分离结构、移除大面积遮罩、列体内部滚动和列头 sticky 一致性。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据已刷新，低高度视口下任务卡信息不再被 `.rc-board-head-mask` 遮住。
- computed style 摘要：`.rc-board` 为 `3008px × 596.625px`、gap `6px 16px`；`.rc-board-wrap` overflow 为 `auto hidden`；`.rc-column-head` 为 `position: sticky`、`z-index: 2`；前 4 个列头 top 均为 `295.375`；`.rc-column-body` 承担纵向滚动；卡片 top `379.375`，晚于列头 bottom `353.375`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整九阶段看板滚动结构和 sticky 实现策略，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 19:13:54 opsx.modify

- 反馈：用户确认空列目标应按最新附件样式展示，即保留大面积低对比虚线承载框、居中阶段文案和接近页面暗场的轻量底色；此前测试将“空列无框、透明背景”固化为通过条件，导致返修方向偏离目标。
- 范围边界：仅修正需求中心九阶段空列视觉契约与测试断言；不调整列头、卡片、sticky、筛选区、指标卡、品牌区和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新空列参考截图 | 需求中心九阶段看板，深色主题，空列状态 | `.rc-column-body.empty` 与 `.rc-empty-stage` | 空列保留大面积圆角虚线承载框；背景接近页面暗场但略有承载区域感；边框为低对比冷灰虚线且不混金色；文案居中展示 | 返修前 `.rc-column-body.empty` 被固定为 `border: 0`、`background: transparent`，测试也要求空列无框透明 | 空列承载框缺失、测试契约方向错误 | 用户附件对照、CSS 检查、Vitest 样式契约、Playwright 1440px 单卡片/空列截图、computed style | 本次修复：恢复空列大面积低对比冷灰虚线承载框，保留暗场轻量底色与现有文案；同步更新测试断言 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`.rc-column-body.empty` 从无框透明改为 `border: 1px dashed rgba(64, 77, 106, .5)`、`background: rgba(255, 255, 255, .012)`、`margin: 0`，形成与附件一致的大面积低对比承载框；继续不使用 `repeating-linear-gradient` 或 `var(--rc-accent)`。
- 测试：更新九阶段看板视觉测试，移除错误固化的“空列无框/透明”断言，改为锁定冷灰虚线边框、近暗场轻量背景和无金色混色。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx` 通过；Playwright 视觉证据已刷新。
- computed style 摘要：`.rc-column-body.empty` 为 `320px × 532.625px`，`border: 1px dashed rgba(64, 77, 106, 0.5)`，`background: rgba(255, 255, 255, 0.01)`；`.rc-empty-stage` 文案保持居中。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正空列视觉契约与测试断言，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 19:43:28 opsx.modify

- 反馈：用户继续指出空列占位文字字体仍有差异；当前空列框体已贴近附件，但占位标题和说明仍继承普通 UI body 字体，技术看板气质不足。
- 范围边界：仅修正需求中心九阶段空列占位文字字体；不调整现有字号、行高、颜色、居中布局、空列边框/背景、列头、卡片、sticky、筛选区、指标卡、品牌区和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户空列字体反馈 | 需求中心九阶段看板，深色主题，空列状态 | `.rc-empty-stage`、`.rc-empty-stage strong`、`.rc-empty-stage p` | 空列占位标题和说明使用现代 Ops 技术感字体 token，贴近附件里更窄、更克制的空态文字气质 | 返修前 `.rc-empty-stage` 继承 `Inter, "Noto Sans SC", system-ui, sans-serif`，测试和 computed style 未覆盖标题/说明文字字体 | 空列文字字体族、computed style 取证粒度、测试契约覆盖 | 用户反馈、CSS 检查、Vitest 样式契约、Playwright 1440px 单卡片/空列截图、computed style | 本次修复：`.rc-empty-stage` 使用 `var(--rc-font-accent)`，标题和说明继承 JetBrains Mono 链路；同步补充测试和 computed style 选择器 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`.rc-empty-stage` 增加 `font-family: var(--rc-font-accent)`，空列标题和说明继承现代 Ops 技术感字体；不改字号、行高、颜色、居中布局、空列框体或 sticky。
- 测试：更新九阶段看板视觉测试，锁定 `.rc-empty-stage` 使用 `var(--rc-font-accent)`；取证脚本新增 `.rc-empty-stage strong` 与 `.rc-empty-stage p` computed style。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx` 通过；Playwright 视觉证据已刷新。
- computed style 摘要：`.rc-empty-stage`、`.rc-empty-stage strong`、`.rc-empty-stage p` 的 `font-family` 均为 `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`；标题仍为 `12px`，说明仍为 `11px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正空列占位字体 token 和视觉验收证据，不改变阶段定义、空列文案、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 22:44:27 opsx.modify

- 反馈：用户要求将需求中心右侧标题区英文小标题从 `MoonBox Ops` 改为 `Requirement Operations`。
- 范围边界：仅修改需求中心标题区小标题文案；不调整标题区布局、字体样式、指标卡、Kanban、空列、卡片、sticky、筛选区、品牌区和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 / REQ 原型 | 需求中心，深色主题，默认首屏 | `.rc-page-header p` | 英文小标题显示 `Requirement Operations`，与 REQ 原型 `prototype/web/prototype.html` 中 eyebrow 文案一致 | 返修前实现显示 `MoonBox Ops` | 标题区用户可见文案 | TSX 文案检查、Vitest 断言、Playwright 1440px 截图 | 本次修复：将实现文案替换为 `Requirement Operations`，并增加回归断言防止退回旧文案 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` |

- 调整：`RequirementCenterPage.tsx` 中 `.rc-page-header p` 文案由 `MoonBox Ops` 改为 `Requirement Operations`。
- 测试：更新 `requirement-center.test.tsx` 标题区测试，断言页面源码包含 `Requirement Operations` 且不再包含旧 `<p>MoonBox Ops</p>`。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx` 通过；Playwright 需求中心 1440px 视觉证据已刷新。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 不需更新，原因：本次仅将实现文案对齐既有 REQ 原型 eyebrow；`prototype/web/prototype.html` 已为 `Requirement Operations`，无需更新；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 23:03:56 opsx.modify

- 反馈：用户确认新建 Capture 当前实现与附件不一致，要求仅调整需求中心右上新建 Capture 入口按钮，视觉对齐附件 `.btn-new` 的金色实心按钮、深色文字、尺寸、圆角、间距和 hover 上浮；保留现有点击打开 Capture 表单能力。
- 范围边界：仅调整需求中心右上新建 Capture 入口按钮；不调整弹窗、九阶段看板、指标卡、筛选区、品牌区和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 `moonbox-board.html` / `.btn-new` | 需求中心，深色主题，默认首屏 | `.rc-header-action` | 右上新建 Capture 为金色实心主按钮，深色文字，尺寸和圆角贴近附件，hover 轻微上浮 | 返修前为透明背景、金色描边和金色文字的 outline 操作按钮 | 按钮背景、文字颜色、尺寸、圆角、hover 动效 | 附件 HTML/CSS 对照、CSS 检查、Vitest 样式契约、Playwright 1440px 截图、computed style | 本次修复：`.rc-header-action` 改为 `var(--rc-accent)` 实心背景、深色文字、42px 高、18px 横向 padding、9px 圆角和 hover `translateY(-1px)`；保留 `onClick` 打开 Capture 表单 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：`globals.css` 中 `.rc-header-action` 从透明描边按钮改为附件风格主入口按钮；移动端保持实心主按钮方向并收紧横向 padding；不改 `RequirementCenterPage.tsx` 的点击逻辑和 Capture 表单。
- 测试：更新 `requirement-center.test.tsx` 标题区测试，锁定新建 Capture 按钮的实心背景、深色文字、圆角、padding、透明边框和 hover 上浮契约。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 需求中心 1440px 视觉证据已刷新。
- computed style 摘要：`.rc-header-action` 高度 `42px`、padding `0px 18px`、background `rgb(216, 172, 85)`、color `rgb(26, 20, 8)`、border `1px solid rgba(0, 0, 0, 0)`、font-size `13px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整新建 Capture 入口按钮视觉样式，不改变 Capture 表单能力、阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-08-31 23:20:36 opsx.modify

- 反馈：用户要求 9 个阶段列头样式保持与附件一致，聚焦 `.col-head`、`.col-name`、`.col-tags`、`.col-count` 的视觉契约。
- 范围边界：仅调整需求中心九阶段列头样式；保留 sticky 冻结能力和 header/body 分离结构；不调整空列框体、卡片、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 `moonbox-board.html` / `.col-head` | 需求中心九阶段看板，深色主题，列头区域 | `.rc-column-head`、`.rc-column-head h2/p/span` | 列头 baseline 对齐；标题约 14.5px 且使用附件标题字体气质；副标题和 count 使用 JetBrains Mono；count 为紧凑 pill；空列列头降权，非空列 count 使用柔和金色底且透明边框 | 返修前列头 `align-items: flex-start`、标题 16px、subtitle/count 继承普通 UI 字体，且列头缺少 filled/empty 状态类 | 对齐方式、标题字号/字体、subtitle/count 字体、count 尺寸、空/非空列头状态 | 附件 CSS 对照、CSS 检查、Vitest 样式契约、Playwright 1440px 截图、filled/empty computed style | 本次修复：列头增加 `filled/empty` 状态类；`.rc-column-head` 改 baseline 与附件 padding；标题改 14.5px + `Space Grotesk` 优先；subtitle/count 改 JetBrains Mono；count 改 `2px 9px` 紧凑 pill；空列标题/副标题/count 降权 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`RequirementCenterPage.tsx` 为每个 `.rc-column-head` 增加 `filled/empty` 状态类；`globals.css` 将列头对齐、padding、标题字号/字体、副标题/count 字体、count pill 和空/非空状态对齐附件视觉。
- 测试：更新 `requirement-center.test.tsx` 九阶段看板视觉测试，锁定列头 baseline、附件式 padding、14.5px 标题、Space Grotesk 标题字体、JetBrains Mono 副标题/count、紧凑 count pill 与 filled/empty 状态类。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 需求中心 1440px 和单卡片空列视觉证据已刷新。
- computed style 摘要：`.rc-column-head` padding `12px 10px 12px 4px`、gap `14px`、position `sticky`；filled/empty 标题均为 `14.5px` 且字体族 `"Space Grotesk", Inter, "Noto Sans SC", system-ui, sans-serif`；副标题与 count 均为 `"JetBrains Mono"`；filled count 为 `2px 9px`、`17.5px` 高、柔和金底透明边框；empty 标题/副标题/count 均降权为低对比冷灰。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整九阶段列头视觉样式，不改变阶段定义、空列文案/框体、任务卡、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 08:02:28 opsx.modify

- 反馈：用户提供最新空列占位符截图，要求仅调整需求中心九阶段空列占位符视觉，明确对齐附件 `.empty-state` 的虚线承载框、`◌` 图标、普通 UI 字体和紧凑说明块；不调整列头、卡片、sticky、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新空列占位符截图 / 附件 `moonbox-board.html` `.empty-state` | 需求中心九阶段看板，深色主题，空列状态 | `.rc-column-body.empty`、`.rc-empty-stage`、`.rc-empty-stage-icon`、`.rc-empty-stage strong/p` | 空列为大面积低对比冷灰虚线框，12px 圆角，近暗场轻量背景；图标为附件式 `◌`；标题/说明使用普通 UI 字体；两行说明作为同一块显示 | 返修前空列边框为 1px 且圆角偏小；图标为 CSS dashed 小圆；`.rc-empty-stage` 强制 `JetBrains Mono`；两行说明拆为两个 `p` 并被 `gap: 8px` 拉散 | 边框粗细、圆角、图标形态、字体族、说明块行距和 DOM 结构 | 附件截图/HTML 对照、CSS 检查、Vitest 样式契约、Playwright 1440px 单卡片/空列截图、computed style | 本次修复：空列承载框改为 `1.5px` 冷灰虚线和 `12px` 圆角；图标改为 `◌`；空态文案回到 `var(--rc-font-body)`；两行说明合并为单个说明块 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 调整：`RequirementCenterPage.tsx` 将空态 DOM 收敛为附件式 icon/title/sub 三块；`globals.css` 将 `.rc-column-body.empty` 调整为 1.5px 冷灰虚线、12px 圆角、2px 顶部节奏，并将 `.rc-empty-stage` 改回 body 字体、`gap: 0`、`20px 14px` padding；说明文案合并为一个 `p` + `<br />`。
- 测试：更新 `requirement-center.test.tsx` 九阶段看板视觉测试，锁定空列 1.5px 虚线、12px 圆角、body 字体、`◌` 图标、说明块 line-height 和 DOM 合并。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-column-body.empty` 为 `320px × 532.062px`，`border: 1px dashed rgba(64, 77, 106, 0.48)`，`background: rgba(255, 255, 255, 0.01)`；`.rc-empty-stage` 为 `Inter, "Noto Sans SC", system-ui, sans-serif`、`gap: 0px`、`padding: 20px 14px`；`.rc-empty-stage-icon` 为 `20px`；`.rc-empty-stage p` 为 `11px`、`line-height: 16.5px`、两行说明块。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正附件空列占位符视觉契约和取证，不改变阶段定义、空列文案语义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 08:22:44 opsx.modify

- 反馈：用户要求仅调整需求中心九阶段任务卡片视觉，对齐附件卡片的轻量票据风格，降低标题字号、左侧状态条宽度、圆角、padding、分隔线和状态信息视觉权重，同时保留 sprint、研发/测试进度、缺失文档、文档入口和动作能力。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；不调整列头、空列、sticky、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户卡片对照截图 / 附件 `moonbox-board.html` `.card` | 需求中心九阶段看板，深色主题，任务卡片状态 | `.rc-card`、`.rc-card-top strong`、`.rc-card-title`、`.rc-progress`、`.rc-docs`、`.rc-blocked`、`.rc-card-actions` | 卡片更接近附件轻量票据：3px 状态条、约 11px 圆角、约 13.5px 标题、较轻分隔线和低权重状态信息；现有治理信息和动作能力保留 | 返修前卡片状态条 5px、圆角 8px、标题约 15px，进度/缺失状态视觉权重偏高；同时单类 `.rc-card-title` 被 `.rc-card button` 高 specificity 覆盖，实际 computed title 仍为 13px | 状态条宽度、圆角、padding、标题字号/权重、分隔线、进度状态框、CSS specificity | 附件截图/CSS 对照、CSS 检查、Vitest 样式契约、Playwright 1440px 截图、computed style | 本次修复：卡片状态条改 3px、圆角 11px、padding 收紧、标题改 13.5px/600；状态信息框降低背景和边框存在感；用 `.rc-card .rc-card-title` 和 `.rc-card .rc-progress` 修正级联覆盖 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：`globals.css` 将 `.rc-card` 调整为 `min-height: 150px`、`padding: 15px 16px 13px`、`border-left: 3px`、`border-radius: 11px`；卡片 ID 改为 10.5px italic；`.rc-card .rc-card-title` 调整为 13.5px、600、1.5 行高；`.rc-card .rc-progress` 调整为 22px 低权重状态框；分隔线改用 `var(--rc-border-soft)`。
- 测试：更新 `requirement-center.test.tsx` 九阶段看板视觉测试，锁定轻量票据卡片的状态条、圆角、padding、标题字号、ID 样式和低权重进度框。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-card` 为 `300px × 150px`、`padding: 15px 16px 13px`；`.rc-card-top strong` 为 `10.5px`、JetBrains Mono、italic；`.rc-card-title` 为 `13.5px`、`line-height: 20.25px`；`.rc-progress` 为 `11.5px`、`22px` 高、低透明背景和低对比边框。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅收敛卡片视觉权重，不改变卡片信息模型、动作能力、阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 08:37:54 opsx.modify

- 反馈：用户指出任务卡片中 `P1 产品团队` 标签展示样式与附件不一致，要求仅调整九阶段任务卡片的优先级/负责人标签，拆为附件式两个独立 tag，并对齐 gap、padding、圆角、字体和视觉权重。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；不调整列头、空列、sticky、卡片其它区域、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户标签截图 / 附件 `moonbox-board.html` `.card-tags` | 需求中心九阶段看板，深色主题，任务卡片标签状态 | `.rc-card-meta`、`.rc-priority`、附件 `.card-tags .tag .tag.owner` | `P1` 与 `产品团队` 为两个独立 tag：优先级使用 warning-soft/strong 语义，负责人使用 raised 冷灰语义；两者用 6px gap 分隔 | 返修前实现为单个 `.rc-priority`，文本内容为 `P1 · 产品团队`，两类信息共享同一个背景、圆角和权重 | DOM 结构、标签数量、分隔方式、背景色、文字色、padding、圆角、字体 | 用户截图/附件 HTML 对照、React DOM 检查、CSS 检查、Vitest 样式契约、Playwright 1440px 截图、computed style | 本次修复：将卡片 meta 拆为 `.rc-priority-tag.rc-tag` 与 `.rc-owner-tag.rc-tag` 两个独立 tag；优先级使用 `--rc-warning` 派生色，负责人使用 `--rc-panel-2` 与 `--rc-muted`；保留 priority/owner 数据和所有动作能力 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：`RequirementCenterPage.tsx` 将 `.rc-card-meta` 中的单个 `{issue.priority} · {issue.owner}` 改为两个 span；`globals.css` 增加 `.rc-card-tags`、`.rc-tag`、`.rc-priority-tag`、`.rc-owner-tag`，对齐附件的 6px gap、`3px 8px` padding、20px 圆角、10px JetBrains Mono 和轻量 tag 视觉。
- 测试：更新 `requirement-center.test.tsx`，断言不再渲染 `P1 · 产品团队` 合并文本，卡片 meta 必须包含两个 span，并锁定两个 tag class 与附件式样式契约。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-card-tags` gap 为 `6px`；`.rc-priority-tag` 为 `28.0469px × 18px`、`padding: 3px 8px`、JetBrains Mono、warning 派生柔和底色；`.rc-owner-tag` 为 `56px × 18px`、`padding: 3px 8px`、JetBrains Mono、冷灰 raised 背景。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅拆分卡片标签视觉结构，不改变 priority/owner 信息模型、筛选逻辑、动作能力、阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 08:56:53 opsx.modify

- 反馈：用户提出九阶段任务卡片内部信息布局 4 个优化点：卡片高度应自适应避免内容超出；文档入口默认不显示下划线、hover 再显示；研发、测试、人工验收合并为同一行轻量进度信息；缺失文档提示移动到文档入口后、进度信息前。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；不调整列头、空列、sticky、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户卡片内部布局截图 | 需求中心九阶段看板，验收中任务卡片状态 | `.rc-card`、`.rc-docs button`、`.rc-blocked`、`.rc-progress`、`.rc-progress-action` | 卡片内容自适应展示；文档链接默认无下划线、hover/focus 再显示；缺失提示跟在文档入口后；研发/测试/人工验收同一行且字体权重接近文档入口；研发进度点击能力保留 | 返修前文档链接默认下划线；研发与测试/人工验收拆成两个 `.rc-progress` 状态框；缺失提示位于进度之后；状态框占用垂直空间，长卡片更容易靠近裁切边界 | 卡片高度、文档链接下划线、进度信息结构、缺失提示顺序、状态信息视觉权重 | 用户截图对照、React DOM 检查、CSS 检查、Vitest 样式契约、Playwright 1440px 截图、computed style | 本次修复：卡片显式保持 `height: auto` 与自然内容流；文档链接默认 `text-decoration: none` 并在 hover/focus 显示；缺失提示移到文档入口后；进度合并为一个 `.rc-progress` 行，研发项保留 `.rc-progress-action` 按钮能力 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：`RequirementCenterPage.tsx` 将缺失提示移动到文档入口后、进度行前，并把研发、测试、人工验收合并到同一个 `.rc-progress` 容器中；研发项仍是可点击按钮并打开任务抽屉。
- 样式：`globals.css` 为 `.rc-card` 增加 `height: auto` 和 `align-content: start`；`.rc-docs button` 默认无下划线，hover/focus-visible 才显示；`.rc-progress` 取消框体背景和边框，改为 10px JetBrains Mono 轻量单行信息；`.rc-progress-action` 提高选择器 specificity，避免被通用 `.rc-card button` 覆盖。
- 测试：更新 `requirement-center.test.tsx`，锁定文档链接默认无下划线、hover/focus 契约、卡片自适应高度、缺失提示位于文档和进度之间、进度行同一容器展示，以及研发进度按钮能力保留。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-docs button` 为 10px、无边框、透明背景、金色文本；`.rc-progress` 为 10px JetBrains Mono、`12.5px` 行高、`gap: 10px`、无边框、透明背景；`.rc-progress-action` 与进度行同色同字体，保留按钮能力；`.rc-blocked` 在 DOM 顺序上位于 `.rc-docs` 后、`.rc-progress` 前。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整卡片内部信息展示顺序和视觉权重，不改变卡片字段、任务抽屉、文档打开、动作执行、阶段流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 09:07:20 opsx.modify

- 反馈：用户提供待开发列截图，确认卡片高度自适应仍有实际问题：多卡片场景中 footer/action 贴近卡片底边，后续卡片在列体视口中有视觉裁切感。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；保持 9 阶段共用卡片组件；不改变卡片信息顺序、文档 hover 规则、进度行、缺失提示内容、列头、空列、sticky、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户待开发列截图 | 需求中心九阶段看板，待开发列，多任务卡片纵向滚动状态 | `.rc-card`、`.rc-card footer`、`.rc-column-body` | 所有阶段卡片共用同一组件并按内容自适应高度；footer/action 不贴底或被视觉裁切；列体底部有足够滚动缓冲，让长内容卡片完整展示 | 返修前 `.rc-card` 虽为 `height: auto`，但仍使用 grid 内容流且底部 padding 偏小；`.rc-column-body` 底部 padding 仅 14px，最后一张卡片或 footer 靠近滚动视口边界时仍有裁切感 | 卡片布局模式、footer 底部呼吸感、列体滚动底部缓冲 | 用户截图对照、CSS 检查、Vitest 样式契约、Playwright 1440px 截图、computed style | 本次修复：`.rc-card` 改为稳定垂直 flex 流，增加底部 padding 并保持 `overflow: visible`；`.rc-column-body` 增加底部 padding 与 `scroll-padding-bottom`，提升多卡片阶段的底部可见缓冲 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 调整：`globals.css` 将 `.rc-card` 从 grid 改为 `display: flex; flex-direction: column; align-items: stretch;`，保留 `height: auto`，底部 padding 从 13px 增至 18px，增加 `overflow: visible`；`.rc-card footer` 增加 `flex: 0 0 auto` 并将 `margin-top` 调整为 12px；`.rc-column-body` 底部 padding 和 `scroll-padding-bottom` 调整为 34px。
- 测试：更新 `requirement-center.test.tsx`，锁定卡片 flex column、自适应高度、可见 overflow、底部 padding 和列体滚动缓冲契约。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-column-body` 为 `display: grid`、`align-content: start`、`padding: 20px 10px 34px`、`overflow: hidden auto`；`.rc-card` 为 `display: flex`、`flex-direction: column`、`align-items: stretch`、`height: 150px`（首张短内容卡由 `min-height: 150px` 生效）、`padding: 15px 16px 18px`、`overflow: visible`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正卡片布局承载和列体滚动缓冲，不改变信息模型、交互能力、阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 09:21:51 opsx.modify

- 反馈：用户追问 9 个阶段卡片是否共用组件、卡片高度是否固定，并指出验收中卡片最后 3 行行间距不一致、待开发列卡片内容仍有超出和未自适应高度问题。
- 范围边界：继续仅修正九阶段任务卡片高度与内部节奏；保持 9 阶段共用同一卡片组件；不改变信息顺序、文档 hover 规则、进度行、缺失提示内容、列头、空列、sticky、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户 Image #1 | 需求中心九阶段看板，验收中列，两张验收卡片 | `.rc-card`、`.rc-docs`、`.rc-blocked`、`.rc-progress`、`.rc-card footer` | 文档、缺失提示、进度行、更新时间/action 保持统一垂直节奏，最后几行不出现忽紧忽松 | 返修前前置统一规则被后置 `.rc-docs` 与 `.rc-card .rc-progress` 覆盖，浏览器 computed style 中 docs 为 `0px`、progress 为 `6px`，blocked/footer 为 `8px` | 后置 CSS 覆盖导致信息栈节奏不一致 | 用户截图对照、CSS 级联检查、Vitest 样式契约、Playwright computed style | 本次修复：`.rc-docs` 和 `.rc-card .rc-progress` 后置规则也显式使用 `8px` margin，blocked/footer 同步保持 8px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| 用户 Image #2 | 需求中心九阶段看板，待开发列，多卡片纵向滚动状态 | `.rc-card`、`.rc-card footer`、`.rc-column-body` | 长标题、多缺失文档、多进度信息时卡片自然增高，footer/action 始终完整展示在卡片内部，9 阶段共用一个卡片组件 | 返修前 `.rc-card` 仍固化 `min-height: 150px`，短卡片表现为固定高度感；多内容组合时容易误判为未按内容自然撑开 | 卡片最小高度固定感、footer/action 贴边、长内容承载 | React 源码检查、CSS 检查、Vitest 样式契约、Playwright computed style | 本次修复：确认 9 阶段均使用 `renderIssueCard(stage, issue)`；`.rc-card` 改为 `min-height: 0`、`height: auto`、`overflow: visible`，由内容自然撑高 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 根因：上轮已将卡片改为 flex column，但保留了 `min-height: 150px`，短内容卡仍呈现固定高度感；同时 `.rc-docs` 与 `.rc-card .rc-progress` 的后置规则覆盖了前面的统一信息栈间距，导致最后几行实际 computed style 不一致。
- 调整：`.rc-card` 取消固定最小高度，改为 `min-height: 0`，继续保持 `display: flex`、`flex-direction: column`、`height: auto` 和 `overflow: visible`；`.rc-card .rc-card-title` 改为标题下方不额外占底部 margin；`.rc-card > .rc-card-meta` 保持 10px；`.rc-docs`、`.rc-blocked`、`.rc-card .rc-progress`、`.rc-card footer` 统一为 8px 顶部间距。
- 测试：更新 `requirement-center.test.tsx`，锁定卡片 `min-height: 0`、标题 margin、标签区 10px、文档/缺失/进度/footer 8px、后置 `.rc-docs` 与 `.rc-card .rc-progress` 不再覆盖统一节奏。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-card` 为 `display: flex`、`flex-direction: column`、`min-height: 0px`、`height: auto` 计算后当前样本高度 `151.031px`、`overflow: visible`；`.rc-card-title`、`.rc-docs`、`.rc-blocked`、`.rc-progress`、`.rc-card footer` 的 `margin-top` 均为 `8px`；`.rc-column-body` 仍为 `padding: 20px 10px 34px` 和 `scroll-padding-bottom: 34px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正卡片高度与内部节奏，不改变信息模型、交互能力、阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 09:41:54 opsx.modify

- 反馈：用户最新截图显示问题更多，待开发列多张卡片被压成横条，只露出 ID、sprint 或局部信息；用户明确要求按“研发中”的完整卡片样式展示。
- 范围边界：继续仅修正九阶段任务卡片列表布局；保持 9 阶段共用 `renderIssueCard`；不调整信息顺序、文档 hover 规则、进度行、缺失提示内容、列头、空列、sticky、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新截图 | 需求中心九阶段看板，深色主题，待开发/研发中/验收中三列对照 | `.rc-column-body`、`.rc-card`、`renderIssueCard(stage, issue)` | 待开发列也按研发中卡片基准完整展示：卡片不被压成条，ID、sprint、标题、标签、文档、缺失提示、进度和 footer/action 均留在卡片内部；多卡片列通过列体滚动承载 | 返修前待开发列多卡片被压缩，只露出局部信息；研发中列因卡片少而未触发压缩，表现为期望基准 | 多卡片列布局压缩、基础票据高度过度取消、卡片 flex shrink | 用户截图对照、React 源码检查、CSS 级联检查、Vitest 样式契约、Playwright 横向看板截图、computed style | 本次修复：确认 9 阶段共用 `renderIssueCard`；非空 `.rc-column-body` 改为纵向 flex 列表；`.rc-card` 恢复 150px 基础票据高度并设置 `flex: 0 0 auto` 防压缩，保留 `height: auto` 支持长内容自然增高 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-board-scrolled-1440.png`、`computed-styles.json` |

- 根因：上轮为消除固定高度感将 `.rc-card` 降为 `min-height: 0`，但 `.rc-column-body` 仍是 `display: grid` + `height: 100%` 的固定列体；待开发列多卡片进入该列体后，grid item 在固定高度内被压缩，导致卡片只露局部。研发中列卡片少，未触发该压缩，所以成为正确视觉基准。
- 调整：`.rc-column-body` 非空态从 grid 改为 `display: flex; flex-direction: column; align-items: stretch;`，保持内部纵向滚动；`.rc-card` 恢复 `min-height: 150px`、保持 `height: auto`，并增加 `flex: 0 0 auto`，确保多卡片列不压缩卡片主体。
- 测试：更新 `requirement-center.test.tsx`，锁定列体 flex column 列表、卡片 `flex: 0 0 auto`、基础票据高度和自然高度契约。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-column-body` 为 `display: flex`、`flex-direction: column`、`align-items: stretch`、`height: 532.062px`、`overflow: hidden auto`；`.rc-card` 为 `flex: 0 0 auto`、`flex-shrink: 0`、`min-height: 150px`、`height: auto` 计算后当前样本高度 `151.031px`、`overflow: visible`；`.rc-card footer` 为 `flex: 0 0 auto`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅纠正卡片列表布局承载方式和基础高度策略，不改变信息模型、交互能力、阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 09:57:06 opsx.modify

- 反馈：用户在 `/explore` 中确认指标卡第 3 行内容有点多余，随后要求仅调整需求中心指标卡，移除 `flow/scope/quality/risk` 装饰标签，保留标题与数值两层信息结构，并同步调整卡片高度、padding 和测试断言。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；不调整 Kanban、筛选区、新建 Capture、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户探索反馈 | 需求中心指标卡，深色主题，默认统计区域 | `.rc-stats`、`.rc-stat`、`.rc-stat-trend` | 指标卡保留标题与数值两层信息；第三行不再显示仅作分类装饰的 `flow/scope/quality/risk` | 返修前每张指标卡额外渲染固定英文小标签，和“全部对象/需求/Bug/当前阻塞”存在语义重复，且不承载动态业务信息 | 信息层级冗余、扫读负担、卡片高度和 padding 未按两层信息结构收敛 | React 源码检查、CSS 检查、Vitest 样式契约、Playwright 1440px 截图、computed style | 本次修复：删除 `statTrends` 与 `.rc-stat-trend` 渲染，移除对应 CSS，`.rc-stat` 调整为两层居中结构、`min-height: 74px`、`padding: 14px 16px` | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |

- 根因：`flow/scope/quality/risk` 是固定装饰性分类标签，不参与统计计算、筛选状态或趋势表达；与指标标题形成重复语义，增加了指标卡第三层视觉噪音。
- 调整：`RequirementCenterPage.tsx` 删除 `statTrends` 常量和 `<small className="rc-stat-trend">` 渲染；`globals.css` 删除 `.rc-stat-trend`，并将 `.rc-stat` 调整为 `align-content: center`、`gap: 11px`、`min-height: 74px`、`padding: 14px 16px`；`scripts/validate-design-system.py` 将 Ops 合约选择器从 `.rc-stat-trend` 更新为 `.rc-stat`，避免旧装饰标签被校验脚本固化。
- 测试：更新 `requirement-center.test.tsx`，锁定指标卡两层结构样式，并断言 `statTrends`、`rc-stat-trend`、`flow/scope/quality/risk` 装饰标签不再出现在页面源码；设计系统校验继续覆盖指标卡本体选择器。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：`.rc-stat` 为 `display: grid`、`align-content: center`、`min-height: 74px`、计算高度 `88.3906px`、`padding: 14px 16px`、`gap: 11px`、`overflow: visible`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅移除指标卡装饰标签和收紧两层信息结构，不改变统计口径、交互能力、阶段定义、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 10:14:21 opsx.modify

- 反馈：用户提供最新截图并要求每个阶段首张卡片需要顶部对齐，包括空列；随后确认仅调整九阶段列体首项顶部对齐，保持其它视觉系统不变。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；只调整列体首项顶部基准；不调整列头、空列文案、空列框视觉、卡片样式、sticky、筛选区、指标卡、新建 Capture、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户最新截图 | 需求中心九阶段看板，深色主题，采集池有卡片且规划中/待评审/已评审为空列 | `.rc-column-body`、`.rc-column-body.empty`、`.rc-column-body.empty::before`、`.rc-card` | 每个阶段的首个视觉对象顶部对齐：非空列首张卡片与空列虚线承载框从同一水平线开始 | 返修前非空列首卡由 `.rc-column-body` 的 20px padding 下移；空列框由 `.rc-column-body.empty` 自身绘制并额外带 `margin-top: 2px`，框体顶部与首卡不在同一基准 | 空列与非空列首项顶部基准不一致、空列额外 margin、空列框体绘制层级 | 用户截图、CSS 检查、Vitest 样式契约、Playwright 1440px 单卡片/空列截图、computed style | 本次修复：`.rc-column-body.empty` 移除额外 margin 并复用 `20px 10px 34px` padding；空列虚线框改由 `::before` 在 `top: 20px`、`bottom: 34px` 绘制，视觉样式保持原低对比虚线框 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |

- 根因：非空列首卡位置由 `.rc-column-body` 的顶部 padding 决定，而空列虚线框此前直接绘制在 `.rc-column-body.empty` 本体上，并额外带 `margin-top: 2px`；两者不是同一顶部基准，因此空列框与首张卡片出现纵向错位。
- 调整：`globals.css` 将 `.rc-column-body.empty` 的 `margin` 改为 `0`，border/background 交给 `.rc-column-body.empty::before`；空列本体 padding 改为与非空列一致的 `20px 10px 34px`，伪元素使用 `inset: 20px 0 34px` 绘制原低对比冷灰虚线框。
- 测试：更新 `requirement-center.test.tsx`，锁定空列本体 `margin: 0`、统一 padding，以及空列虚线框伪元素 `inset: 20px 0 34px`、1.5px 冷灰虚线、12px 圆角和轻量暗场背景。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b` 通过；Playwright 视觉证据和 computed style 已刷新。
- computed style 摘要：非空 `.rc-column-body` 为 `padding: 20px 10px 34px`、`.rc-card` 为 `margin-top: 0px`；空列 `.rc-column-body.empty` 为 `margin-top: 0px`、`padding: 20px 10px 34px`；`.rc-column-body.empty::before` 为 `position: absolute`、`top: 20px`、`bottom: 34px`、低对比冷灰虚线框。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅统一列体首项顶部对齐，不改变阶段定义、空列文案语义、卡片信息模型、交互能力、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 14:53:52 opsx.modify

- 反馈：用户在 `/explore` 中指出 9 个阶段的列间隙比较大，随后要求仅将 `.rc-board` 横向列间距从当前 16px 下调到 10px。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；只调整九阶段看板横向列间隙；保留 `grid-template-columns: repeat(9, 320px)`、`row-gap`、列头、空列、卡片、sticky、筛选区、指标卡、新建 Capture、品牌区和其它视觉系统不变；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户探索反馈 | 需求中心九阶段看板，深色主题，横向阶段列表 | `.rc-board` | 9 个阶段保持 320px 列宽，但横向列间距更紧凑，减少阶段之间的空隙 | 返修前 `.rc-board` 横向 `gap` 固化为 16px，横向扫读距离偏大 | 横向列间隙 | CSS 检查、Vitest 样式契约 | 本次仅将 `.rc-board` `gap` 从 16px 调整为 10px，并同步测试断言；`row-gap: 6px` 与 9 列宽度保持不变 | `src/web/src/styles/globals.css`、`src/web/src/requirement-center.test.tsx` |

- 调整：`globals.css` 将 `.rc-board` 的 `gap` 从 `16px` 下调为 `10px`，保留 `grid-template-columns: repeat(9, 320px)` 和 `row-gap: 6px`。
- 测试：更新 `requirement-center.test.tsx`，将九阶段看板列间距契约断言同步为 `gap: 10px`。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、`git diff --check` 通过；`pnpm --dir src/web exec vitest --run --environment jsdom src/requirement-center.test.tsx` 因本机 pnpm 版本守卫拦截，已改用项目本地 Vitest 执行同等测试。
- AI Usage：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change update-product-workbench-modern-ops-visual-system --sprint sprint-004 --json` 返回 warning，原因是当前会话无 token_count 事件，未生成 sprint snapshot。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅收紧 Kanban 横向列间隙，不改变阶段定义、空列文案语义、卡片信息模型、交互能力、状态流转、业务流程、AI 入口或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 17:25:06 opsx.modify

- 反馈：用户要求新增 Capture 弹窗按照附件 `moonbox-board (1).html` modal 完整实现，包括 eyebrow/title/sub、类型切换、标题、一句话描述与 200 字计数、负责人、来源、P0-P3 优先级、footer 快捷键提示、取消/创建按钮、Esc 关闭和 Cmd/Ctrl+Enter 创建。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅调整需求中心新增 Capture 弹窗；保留现有点击新建 Capture 打开弹窗、提交后插入采集池卡片能力；不调整九阶段看板、指标卡、筛选区、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 `moonbox-board (1).html` | 需求中心新增 Capture 弹窗，深色主题 | `.modal-overlay`、`.modal`、`.modal-head`、`.type-toggle`、`.priority-picker`、`.modal-foot` | 弹窗具备附件式深色遮罩、560px 模态框、三层标题、完整 Capture 表单、P0-P3 优先级、字符计数和快捷键提示；提交后仍插入采集池 | 返修前弹窗沿用旧 `rc-flow-dialog` 简化表单，仅包含类型、P0-P2、标题和描述，缺少 owner/source/P3/字符计数/快捷键提示，视觉密度和层级未对齐附件 | modal 尺寸、圆角、padding、标题层级、字段完整性、优先级数量、footer 信息和快捷键 | 附件 HTML selector 对照、React DOM 检查、CSS 检查、Vitest 行为/样式契约、computed style | 本次修复：为 Capture 增加独立 `.rc-capture-mask` 与 `.rc-capture-dialog` 附件式样式；补齐 owner/source/P3/字符计数；保留 Esc 关闭，新增 Cmd/Ctrl+Enter 走表单提交；标题为空时创建按钮禁用 | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/styles/globals.css`、`src/web/src/requirement-center.test.tsx` |

- 根因：此前只完成了“新建 Capture 入口按钮”的附件化，弹窗本体仍停留在旧的简化 capture 表单；同时旧测试把 P2 默认态和空标题提交报错固化为契约，未覆盖附件 modal 的完整字段和快捷键。
- 调整：`RequirementCenterPage.tsx` 扩展 `captureForm`，补充 owner/source 字段、P3 优先级、200 字描述计数、footer 快捷键提示和 Cmd/Ctrl+Enter 提交；创建后新卡片 owner/source 使用表单值，更新时间仍保持 `刚刚`；`globals.css` 为 Capture 弹窗增加独立遮罩、modal header/body/footer、segmented、priority chip、输入框、字符计数和按钮样式。
- 测试：更新 `requirement-center.test.tsx`，锁定附件式弹窗标题层级、需求/Bug 类型按钮、P1 默认优先级、P3 chip、标题 60 字限制、描述 200 字限制、字符计数、空标题禁用创建、负责人/来源选择和 Ctrl+Enter 创建卡片。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict` 通过；Playwright 生成 `requirements-capture-modal-1440.png` 并刷新 `computed-styles.json`；`git diff --check` 仍仅因两个无关既有文件 `iterations/change/sprint-003/sprint.md` 和 `openspec/specs/api-governance/spec.md` 的 EOF 空行失败，本轮未修改该两处。
- computed style 摘要：`.rc-capture-dialog` 为 `560px` 宽、`741.578px` 高、`padding: 0px`、深色侧栏背景、`1px` 边框；`.rc-capture-dialog .rc-dialog-head h2` 为 `18px`、Space Grotesk/Inter 字体；`.rc-capture-segmented` 为 `168.766px × 40px`、`padding: 3px`、`gap: 2px`；`.rc-capture-segmented.priority button` 为 JetBrains Mono `12px`；`.rc-capture-dialog .rc-primary-action` 为 `129.875px × 38px`、金色背景和深色文字。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅补齐 Capture 弹窗视觉和前端表单字段，不改变需求中心阶段定义、状态流转、后端接口、数据模型、业务流程或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-01 18:18:51 opsx.modify

- 反馈：用户要求调整新增 Capture 弹窗文案：删除 `Capture · req-capture / bug-capture`，删除 footer 快捷键提示 `Esc 取消 ⌘Enter 创建`；并要求类型、标题、来源、优先级作为必填项，用红色 `*` 标注。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅调整新增 Capture 弹窗文案和必填标识；保留 Esc 关闭、Cmd/Ctrl+Enter 创建、点击新建 Capture 打开弹窗、提交后插入采集池卡片能力；不调整九阶段看板、指标卡、筛选区、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文案反馈 | 需求中心新增 Capture 弹窗，深色主题，默认打开状态 | `.rc-capture-dialog .rc-dialog-head`、`.rc-capture-fieldset legend`、`.rc-field-label`、`.rc-dialog-actions` | 弹窗不展示顶部 eyebrow 和 footer 快捷键提示；类型、标题、来源、优先级显示红色必填 `*`；负责人和一句话描述不显示必填 `*` | 返修前仍展示 `Capture · req-capture / bug-capture` 与 `Esc/⌘Enter` 提示；来源和优先级缺少必填标识 | 文案冗余、必填标识缺失、footer 布局删除提示后需右对齐按钮 | 用户反馈、React DOM 检查、CSS 检查、Vitest 行为/样式契约、Playwright 截图与 computed style | 本次修复：删除 header eyebrow 与 footer 快捷键提示；类型/标题/来源/优先级补红色星号，title/source 添加 required，类型/优先级 group 添加 `aria-required`; footer 按钮右对齐 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-capture-modal-1440.png`、`computed-styles.json` |

- 调整：`RequirementCenterPage.tsx` 删除 Capture header eyebrow 与 footer 快捷键提示，补充类型/标题/来源/优先级必填标识；`globals.css` 复用红色星号样式并为无提示 footer 增加右对齐。
- 测试：更新 `requirement-center.test.tsx`，断言 eyebrow 和快捷键提示不再出现，类型与优先级 group 标记 `aria-required`，标题与来源控件为 required，弹窗内只有 4 个必填星号，且创建能力仍通过 Ctrl+Enter 保持可用。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict` 和 touched-file `git diff --check` 通过；Playwright 已刷新 `requirements-capture-modal-1440.png` 与 `computed-styles.json`。
- computed style 摘要：`.rc-capture-dialog .rc-dialog-head p` 为 `null`，确认 eyebrow 已删除；`.rc-capture-dialog .rc-dialog-actions kbd` 为 `null`，确认 footer 快捷键提示已删除；`.rc-capture-fieldset legend b` 与 `.rc-capture-dialog .rc-field-label b` 均为红色 `rgb(212, 116, 118)`，确认必填星号生效。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整 Capture 弹窗文案与必填标识，不改变需求中心阶段定义、状态流转、后端接口、数据模型、业务流程、快捷键行为或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-02 18:49:50 opsx.modify

- 反馈：用户要求参照附件 9 个阶段右下角按钮，一比一实现对应交互：右下为金色 pill `Agent 助手` FAB，点击后打开附件式居中 Action Modal/Agent 操作面板，而不是直接打开右侧 AI Chat 抽屉；面板承载 9 阶段当前可执行动作与上下文提示，并复用现有动作能力。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅调整需求中心九阶段右下 Agent 助手入口与对应交互；不调整九阶段看板列头、空列、卡片、指标卡、筛选区、新建 Capture、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 `moonbox-board (2).html` | 需求中心九阶段看板，深色主题，右下 Agent 入口 | `.fab`、`#actionModalOverlay`、`.modal`、`.modal-head`、`.modal-foot` | 右下固定金色 pill，显示工具图标与 `Agent 助手`；点击打开居中 Action Modal，展示阶段动作与上下文，Esc/遮罩可关闭，内部点击不误关闭 | 返修前右下入口仍是圆形 AI 入口，点击直接打开右侧 AI Chat 抽屉，未形成附件式 Agent 操作面板 | FAB 形态、入口文案、点击目标、操作承载容器、关闭方式、阶段动作聚合 | 附件 selector 对照、React DOM 检查、CSS 检查、Vitest 行为/样式契约、Playwright 1440px 截图、computed style | 本次修复：`.rc-ai-fab.rc-agent-fab` 改为附件式金色 pill；新增 `agentOpen` 居中面板，按 9 阶段映射可执行动作、对象计数、首个可操作对象或空态提示；动作继续走 `runIssueAction`、`choiceDialog`、toast、任务进度与 AI 消息能力 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-agent-modal-1440.png`、`computed-styles.json` |

- 根因：此前右下入口只承担 AI Chat 抽屉快捷入口，未按附件 `.fab` 的“Agent 操作入口”语义建模；交互目标也直接绑定聊天抽屉，导致 9 阶段动作没有统一的居中操作面板承载。
- 调整：`RequirementCenterPage.tsx` 新增 `agentOpen` 状态、Esc 关闭联动、`runAgentStageAction` 和 Agent 操作面板；右下按钮改为工具图标 + `Agent 助手` 文案，点击打开面板；面板内按 `stageColumns` 渲染阶段 title/subtitle/count、上下文提示和动作按钮，阶段动作继续复用既有 `runIssueAction` 与确认/Toast/AI 消息链路。
- 样式：`globals.css` 增加 `.rc-agent-fab`、`.rc-agent-mask`、`.rc-agent-dialog`、`.rc-agent-body`、`.rc-agent-stage` 等样式；FAB 对齐附件 48px 高、24px 圆角、32px/28px 右下定位、金色实心背景和 hover 上浮；弹层对齐 560px 居中 modal、深色遮罩、紧凑阶段动作列表和 footer Esc 提示。
- 测试：更新 `requirement-center.test.tsx`，锁定点击右下入口打开 Agent 面板、面板内点击不误关闭、Esc 关闭、从面板触发 `开始开发` 后关闭并流转到研发中；样式契约覆盖 FAB 尺寸/位置/圆角/padding/hover、面板宽度/圆角/遮罩和 selector。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict` 通过；Playwright 已生成 `requirements-agent-modal-1440.png` 并刷新 `computed-styles.json`。
- computed style 摘要：`.rc-agent-fab` 为 `48px` 高、`right: 32px`、`bottom: 28px`、`padding: 0 18px 0 15px`、`border-radius: 24px`、金色实心背景；`.rc-agent-dialog` 为 `560px` 宽、12px 圆角、深色浮层背景；`.rc-agent-body` 为 `max-height: min(58vh, 520px)` 的可滚动阶段动作列表。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整右下 Agent 助手入口与前端操作面板承载，不改变阶段定义、业务流程、API/DB、数据模型、状态流转、权限或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-02 19:18:20 opsx.modify

- 反馈：用户要求仅调整需求中心九阶段卡片动作按钮的弹窗交互，参照附件 `moonbox-board (2).html` 的 Action Modal 组件族，一比一复刻需求分析、生成需求/BUG、完善需求/BUG、发起评审/确认修复、加入迭代、生成 Opsx、开始开发/修复、查看进度、完成/归档的 modal 交互和 loading/checklist/dropzone/tabs/progress/confirm 状态。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅调整卡片动作按钮触发后的弹窗交互；不调整九阶段列头、空列、卡片静态样式、指标卡、筛选区、新建 Capture、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 `moonbox-board (2).html` | 需求中心九阶段看板，卡片 footer 动作点击后的 Action Modal 状态族 | `.modal-overlay`、`.modal`、`.modal-head`、`.modal-body`、`.modal-foot`、`.cmd-block`、`.doc-checklist`、`.action-tabs`、`.dropzone`、`.mini-bar` | 卡片动作点击后进入 560px 居中 Action Modal；分析有 loading 与采纳 checklist；生成/评审/归档有命令块和文档 checklist；完善有 AI/导入 tabs 与 dropzone；加入迭代有评估 loading、迭代 tabs 和 sprint checklist；生成 Opsx 有 Change 列表；开始开发/修复有执行步骤 checklist；查看进度有进度条；Esc/遮罩可关闭 | 返修前卡片动作仍混用直接执行、旧 `choiceDialog` 或打开 AI Chat 抽屉，缺少附件式统一 Action Modal 组件族，交互状态不完整且与右下 Agent 操作面板语义不一致 | 弹窗承载容器、状态覆盖、tabs/dropzone/checklist/progress、关闭方式、底层动作复用 | 附件 HTML selector 对照、React DOM 检查、CSS 检查、Vitest 行为/样式契约、Playwright 多状态截图、computed style | 本次修复：新增 `ActionDialog` 状态模型、`openIssueActionDialog`、`confirmActionDialog`、`renderActionDialog` 和 `.rc-action-*` 样式；卡片主/辅助动作与 Agent 面板阶段动作统一先打开 Action Modal，再复用 `runIssueAction`、toast、任务进度和 AI 消息能力 | `requirements-action-analysis-modal-1440.png`、`requirements-action-generate-modal-1440.png`、`requirements-action-complete-modal-1440.png`、`requirements-action-sprint-modal-1440.png`、`requirements-action-opsx-modal-1440.png`、`requirements-action-progress-modal-1440.png`、`computed-styles.json` |

- 根因：上一轮只将右下 Agent 助手入口改成附件式操作面板，卡片 footer 动作仍保留历史路径：部分动作直接调用 `runIssueAction`，部分动作触发旧 `choiceDialog`，分析动作打开 AI Chat 抽屉；因此按钮视觉已靠近附件，但具体动作交互没有统一进入附件 Action Modal 组件族，也没有覆盖 loading/checklist/dropzone/tabs/progress/confirm 状态。
- 调整：`RequirementCenterPage.tsx` 新增 `ActionDialog` 状态模型和动作类型映射，卡片主动作、分析辅助动作与 Agent 面板阶段动作统一调用 `openIssueActionDialog`；新增 `renderActionDialogBody` 分别渲染 analysis、command、complete、sprint、opsx、apply、progress 状态；`confirmActionDialog` 在确认后继续复用 `runIssueAction`，分析态仅保存分析结论，查看进度态仅关闭并写入 AI 消息。
- 样式：`globals.css` 增加 `.rc-action-mask`、`.rc-action-dialog`、`.rc-action-body`、`.rc-action-command`、`.rc-action-doc-list`、`.rc-action-tabs`、`.rc-action-dropzone`、`.rc-action-change`、`.rc-mini-bar` 和 footer action 样式；弹层对齐附件 560px 居中、16px 圆角、深色遮罩、紧凑 head/body/foot、金色主按钮与低对比状态区。
- 测试：更新 `requirement-center.test.tsx`，将旧 `choiceDialog` 和 AI Chat 抽屉断言改为 Action Modal 断言；新增行为测试覆盖生成需求、需求分析、完善需求导入、加入迭代、生成 Opsx、查看进度；新增样式契约测试覆盖 `.rc-action-*` selector、尺寸、padding、字体、背景、圆角和状态控件。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；Playwright 生成 6 张 Action Modal 1440px 截图并刷新 `computed-styles.json`。
- computed style 摘要：`.rc-action-mask` 为 fixed 全屏、`z-index: 96`、`padding: 24px`、`background: rgba(4, 5, 9, 0.62)`；`.rc-action-dialog` 为 `560px` 宽、`max-height: 88vh`、`border-radius: 16px`、深色侧栏背景；`.rc-action-dialog .rc-dialog-head` 为 `padding: 22px 24px 16px`；`.rc-action-command` 使用技术字体和 raised 背景；`.rc-action-tabs` 为 fit-content segmented；`.rc-mini-bar` 为 7px 进度条。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整卡片动作按钮的前端弹窗承载与交互状态，不改变阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-02 19:42:32 opsx.modify

- 反馈：用户截图指出需求分析 Action Modal 的“解决方案要点（可选择采纳）”当前不允许勾选；用户要求三条要点默认全选，点击可切换选中/未选中，底部主按钮文案实时更新，0 项选中时禁用主按钮，并补充测试。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅修正需求分析/Bug 分析 Action Modal 的要点勾选交互；不调整其它 Action Modal、九阶段看板、卡片静态样式、指标卡、筛选区、新建 Capture、品牌区和其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-93601d00-09ab-4c62-bdc1-73a21614607c.png` | 需求中心 Action Modal，需求分析结果态 | `.rc-action-adopt-list`、`.rc-action-adopt-list button`、`.rc-primary-action` | 解决方案要点应是真正可交互 checklist：默认 3 项全选，点击任一项可取消/恢复，底部按钮显示 `采纳 n/3 项并保留分析 →`，0 项时禁用 | 返修前要点渲染为普通 button，但 `className="checked"` 写死且无 `onClick` 与选中状态；主按钮文案 `3/3` 也写死 | 静态 checked、无状态、无点击切换、主按钮数量不联动、测试只断言元素存在 | 用户截图、源码检查、Vitest 行为测试、Playwright 截图、computed style | 本次修复：新增 `adoptedPointIndexes` 状态，默认 `[0,1,2]`；要点按钮使用 `aria-pressed` 与 `checked` 类表达状态，点击切换；主按钮实时显示选中数量且 0 项禁用；确认后 toast/AI 消息使用实际采纳数量 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-analysis-selection-1440.png`、`computed-styles.json` |

- 根因：Action Modal 初版只复刻了分析 checklist 的外观，没有建立 checklist 状态模型；`checked` 类和 `采纳 3/3` 文案被硬编码，测试也只覆盖“3 个按钮存在”，未覆盖点击切换和数量变化。
- 调整：`RequirementCenterPage.tsx` 为 `ActionDialog` 增加 `adoptedPointIndexes`，分析弹窗打开时默认全选；解决方案要点按钮增加 `aria-pressed`、状态 class 和点击切换逻辑；`renderActionDialog` 根据选中数量生成确认文案并在 0 项时禁用；`saveAnalysisResult` 使用实际采纳数量写入 toast 与 AI 消息。
- 样式：`globals.css` 增加 `.rc-action-adopt-list button.checked`、hover/focus、checked/unselected 圆点差异；未选中态为空心冷灰圆点，选中态为低对比金色圆点。
- 测试：更新 `requirement-center.test.tsx`，覆盖默认全选、取消单项、按钮文案从 `3/3` 到 `2/3`、取消到 `0/3` 后禁用、重新勾选到 `1/3`，并锁定 checked/unselected 样式契约。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build` 通过；Playwright 刷新 `requirements-action-analysis-selection-1440.png` 与 `computed-styles.json`。
- computed style 摘要：`.rc-action-adopt-list button:not(.checked) span` 为透明背景、冷灰边框；`.rc-action-adopt-list button.checked span` 为金色低对比背景；`.rc-action-dialog .rc-primary-action` 在取消一项后仍为可点击主按钮，截图状态对应 `采纳 2/3 项并保留分析 →`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正分析 Action Modal 内部 checklist 交互，不改变阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-02 22:38:41 opsx.modify

- 反馈：用户截图指出“已完成”阶段卡片不需要显示 `查看归档`，也不需要显示研发/测试/人工验收进度信息；仍需保留已完成卡片基础信息和归档文档入口。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅调整需求中心九阶段 `done` 阶段卡片展示；不调整其它阶段卡片、列头、空列、筛选区、指标卡、Action Modal 或其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-22f692f8-edaf-45f8-9340-9a9166e43aff.png` | 需求中心九阶段看板，已完成列 | `.rc-card`、`.rc-progress`、`.rc-card-actions` | 已完成卡片作为只读归档结果卡：保留 ID、sprint、标题、标签、`archive.md`、`trace.md` 和更新时间；不显示研发/测试/人工验收进度；不显示 `查看归档` 或其它 footer 动作按钮 | 返修前 `done` 阶段仍被 `visibleTaskProgress` 纳入进度展示，且 footer 同时渲染主动作和额外 `查看归档` 按钮 | done 阶段展示冗余、归档动作重复、进度信息与已完成结果态不匹配 | 用户截图、源码检查、Vitest 行为测试 | 本次修复：`visibleTaskProgress` 排除 `done`；`renderIssueCard` 为 `done` 阶段裁剪进度区和 footer 动作按钮；测试覆盖 done 阶段无进度、无归档动作且保留文档入口 | `src/web/src/requirement-center.test.tsx` |

- 根因：卡片共用组件后，阶段展示规则没有为 `done` 做结果态裁剪；`visibleTaskProgress` 把 `done` 纳入进度展示，`showArchive` 又默认允许非验收阶段显示主动作，同时下方还有 `stage.id === "done"` 的额外 `查看归档` 按钮，导致已完成卡片出现冗余进度和重复归档动作。
- 调整：`RequirementCenterPage.tsx` 将 `done` 从 `visibleTaskProgress` 中移除，并在 `renderIssueCard` 中用 `isDoneStage` 阻止进度区、主动作按钮和额外归档按钮渲染；保留基础信息、更新时间以及 `archive.md`、`trace.md` 文档入口。
- 测试：更新 `requirement-center.test.tsx`，覆盖 `DEMO-REQ-DONE` 与 `DEMO-BUG-DONE` 不展示 `研发 x/x`、`测试`、`人工验收` 和 `查看归档` 按钮，并确认 `archive.md`、`trace.md` 文档入口仍可见。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx` 与 `node_modules/.bin/tsc -b` 通过；后续完成 OpenSpec、设计系统、构建、Workflow Sync 和 AI Usage 复核。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅裁剪已完成阶段卡片的冗余展示，不改变需求中心阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-02 23:12:00 opsx.modify

- 反馈：用户指出加入迭代弹窗样式与附件仍有差异，要求仅调整需求中心加入迭代 Action Modal：按附件 `sprintModal` 一比一收敛结构与样式，补齐对象 label 与左侧金色边对象信息块、迭代模式文案、现有迭代状态 pill/radio/容量/容量条/容量不足 disabled badge，以及新建迭代编号和确认按钮禁用/文案联动。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅调整加入迭代 Action Modal；保留现有 `runIssueAction`、toast 和阶段流转能力；不调整其它 Action Modal、九阶段看板、卡片静态样式、筛选区、指标卡、新建 Capture、品牌区或其它视觉系统；不改变 API、DB、权限、部署、阶段定义、状态流转或 Mock/API 边界。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 `moonbox-board (2).html` | 需求中心加入迭代弹窗，深色主题，评估完成态 | `#sprintModalOverlay`、`.modal[style="width:520px"]`、`#sprintContextField`、`#sprintContextStrip`、`#sprintModeToggle`、`.sprint-option`、`.sprint-radio`、`.capacity-bar`、`.capacity-badge`、`#newSprintId`、`#confirmSprintBtn` | 弹窗宽度 520px；对象信息有 label 和左侧金色边；AI 工作量评估独立字段；模式为 `加入现有迭代 / 新建迭代`；现有迭代选项包含状态 pill、radio、容量 used/total、容量条和容量不足 disabled/badge；新建迭代编号驱动确认按钮文案与禁用状态 | 返修前加入迭代仍沿用简化 ActionDialog：对象信息缺少字段 label 和金色边上下文块，tab 文案是 `选择现有迭代`，选项只有 sprint 名称、状态和简单 `12/36 项` 文案，缺少 radio、容量条、disabled/badge 和新建编号联动 | sprintModal 结构缺失、容量决策不可视、禁用状态缺失、新建迭代交互不可编辑、确认按钮文案不随选择变化 | 附件 HTML selector 对照、React DOM 检查、CSS 检查、Vitest 行为/样式契约、Playwright 1440px 截图、computed style | 本次修复：为 sprint ActionDialog 增加 `sprintEstimate` 与 `newSprintId` 状态；对象块改为 `对象` 字段 + 左侧金色边信息条；现有迭代选项补 radio、状态 pill、容量 used/total、capacity bar 和 disabled/badge；新建迭代编号可编辑，确认按钮在空编号时禁用并随编号更新文案 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-sprint-modal-1440.png`、`computed-styles.json` |

- 根因：Action Modal 组件族初版只把加入迭代纳入通用弹窗容器，没有把附件 `sprintModal` 的“工作量评估 → 迭代容量决策 → 新建迭代兜底”状态机反向工程成组件级视觉与交互契约；因此实现停留在普通 tabs + button list，无法表达容量不足、选择态和新建编号联动。
- 调整：`RequirementCenterPage.tsx` 新增 sprint 估算、下一迭代编号、容量选项模型和默认可选 sprint 选择逻辑；加入迭代弹窗渲染 `对象` 信息块、`AI 工作量评估` 字段、`加入现有迭代 / 新建迭代` tabs、radio 选项、状态 pill、容量 used/total、capacity bar、容量不足 disabled/badge 与新建迭代编号输入；确认时继续调用 `runIssueAction(issue, { sprintId })`。
- 样式：`globals.css` 增加 `.rc-action-dialog.sprint` 520px 宽度、`.rc-sprint-context-strip` 左侧金色边对象块、`.rc-sprint-mode-toggle` 附件式 active 态、`.rc-sprint-options`、`.rc-sprint-option-name`、`.rc-sprint-status-pill`、`.rc-sprint-capacity-badge`、`.rc-sprint-radio` 和 `.rc-sprint-capacity-bar` 样式。
- 测试：更新 `requirement-center.test.tsx`，覆盖对象 label、`加入现有迭代` 文案、radio、容量 used/total、容量不足 badge、capacity bar、新建迭代编号清空后主按钮禁用、输入编号后主按钮文案与可用状态联动；样式契约锁定 sprintModal 520px、对象金色边、选项 1.5px 边框/11px 圆角、selected 背景、radio 圆形和 5px 容量条。
- 验证：`node_modules/.bin/vitest run src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict` 通过；Playwright 已刷新 `requirements-action-sprint-modal-1440.png` 与 `computed-styles.json`；`pnpm --dir src/web ...` 因本机 Corepack 当前 pnpm `11.7.0` 与项目 `11.2.2` 守卫不一致失败，已改用项目本地 `node_modules/.bin` 验证。
- computed style 摘要：`.rc-action-dialog.sprint` 宽 `520px`、深色弹层背景；`.rc-sprint-context-strip` 为 raised 背景和左侧金色边对象块；`.rc-sprint-mode-toggle button.active` 为金色实心、深色文字；`.rc-sprint-options` gap `10px`；`.rc-sprint-capacity-badge` 为 warning 派生背景与文字色；`.rc-sprint-capacity-bar` 高 `5px`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整加入迭代 Action Modal 的前端展示与选择交互，不改变需求中心阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-03 08:57:10 opsx.modify

- 反馈：用户指出卡片进度行 `研发 x/x`、`测试 x/x`、`人工验收 x/x` 与附件 `moonbox-board (2).html` 字号和颜色不一致，且标签文字与 `x/x` 数值需要区分视觉层级。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅调整九阶段任务卡片进度行字体与颜色；保留三项同一行、点击打开任务进度抽屉能力、已完成阶段隐藏进度规则；不调整卡片其它样式、列头、空列、sticky、筛选区、指标卡、新建 Capture、Action Modal、品牌区或其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 附件 `moonbox-board (2).html` | 需求中心九阶段任务卡片，深色主题，含研发/测试/人工验收进度行 | 附件 `.card-metrics`、`.card-metrics b`、`.metric-sep` 对照当前 `.rc-progress`、`.rc-progress-action` | 进度行整体使用 `JetBrains Mono`、`10.5px`；`研发/测试/人工验收` 为低对比 tertiary 层级；`x/x` 为 secondary 层级并加粗；分隔点为 quiet 层级 | 返修前 `.rc-progress` 使用继承字体和较大字号，`研发 19/19` 作为同一 button 文本渲染，标签与数值同色同层级 | 字体族、字号、标签/数值 DOM 层级、标签颜色、数值颜色、分隔点颜色、按钮可访问名称 | 附件 HTML selector 对照、React DOM 检查、CSS 检查、Vitest 行为/样式契约、Playwright computed style | 本次修复：进度按钮内部拆分 `.rc-progress-label` 与 `.rc-progress-value`，整体使用等宽 10.5px；标签低对比、数值 `--rc-muted` 且 600 字重、分隔点低对比；按钮增加 `aria-label` 保留任务抽屉入口名称 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` |

- 根因：此前卡片进度行虽然合并为一行，但 DOM 仍把 `研发 19/19`、`测试 3/3`、`人工验收 0/0` 当作整段 button 文本，CSS 只能统一设置颜色和字体，无法复刻附件 `.card-metrics b` 的标签/数值分层。
- 调整：`RequirementCenterPage.tsx` 将进度按钮内部拆为 `.rc-progress-label` 与 `.rc-progress-value`，并为每个按钮补充 `aria-label`；`globals.css` 将 `.rc-card .rc-progress` 对齐附件等宽字体与 10.5px 字号，标签、数值和分隔点分别设置不同视觉层级。
- 测试：更新 `requirement-center.test.tsx`，覆盖 `.rc-progress-label` / `.rc-progress-value` DOM 拆分、字体/字号/颜色样式契约、进度按钮可访问名称，以及点击后任务进度抽屉仍可打开。
- 验证：`python scripts/validate-design-system.py`、`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx` 通过；Playwright 已刷新 `requirements-1440.png` 与 `computed-styles.json`；`pnpm --dir src/web ...` 因本机 Corepack 当前 pnpm `11.7.0` 与项目 `11.2.2` 守卫不一致失败，已改用项目本地 `node_modules/.bin` 验证。
- computed style 摘要：`.rc-progress` 与 `.rc-progress-action` 为 `JetBrains Mono`、`10.5px`；`.rc-progress-label` 颜色为低对比 `color(srgb 0.305882 0.330196 0.398431)`；`.rc-progress-value` 颜色为 `rgb(152, 160, 179)`，对应附件 `text-secondary` 层级。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅调整任务卡片进度行视觉层级，不改变需求中心阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；`acceptance.md`、`trace.md` 回填本次复验证据。

### 2026-09-03 09:32:20 opsx.modify

- 反馈：用户指出九阶段任务卡片进度行中 `研发 x/x`、`测试 x/x`、`人工验收 x/x` 之间的分隔符可以保留，但当前页面显示为异常的 `Â·`，需要正常显示。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅修正进度行分隔符的 CSS 表达和测试断言；不调整 label/value 字体、字号、颜色分层、三项同一行、任务进度抽屉能力、已完成阶段隐藏进度规则、卡片其它样式、列头、空列、sticky、筛选区、指标卡、新建 Capture、Action Modal、品牌区或其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-b09e0ce3-9397-4db2-b87b-003e04dba463.png` | 需求中心九阶段任务卡片，验收中列，含研发/测试/人工验收进度行 | `.rc-progress-action + .rc-progress-action::before` | 分隔符如保留，必须稳定显示为正常 `·`，且维持低对比 quiet 层级 | 页面显示为异常 `Â·`；源码中 `content` 使用裸 `·` 字符 | CSS `content` 裸非 ASCII 字符在渲染链路中显示异常 | 用户截图、CSS 字节检查、Vitest 样式契约 | 本次修复：保留分隔点视觉，将 `content` 改为 CSS escape `\00B7`，避免裸字符被错误解码 | `src/web/src/styles/globals.css`、`src/web/src/requirement-center.test.tsx` |

- 根因：进度项之间的分隔点由 CSS 伪元素注入，当前 `content: "·"` 在源码中是裸 UTF-8 字符；用户截图显示该字符被页面链路渲染为 `Â·`，说明该写法存在编码/渲染稳定性风险。
- 调整：`globals.css` 将 `.rc-card .rc-progress-action + .rc-progress-action::before` 的 `content` 改为 `"\00B7"`，保留原有 `display`、`margin`、`color` 和 `text-decoration`，不改变进度行布局与交互。
- 测试：更新 `requirement-center.test.tsx` 中分隔符样式契约断言，锁定 `content: "\00B7";`，避免后续返修回到裸字符。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、`git diff --check -- <本轮相关文件>` 通过；Playwright 已刷新 `requirements-1440.png` 与 `computed-styles.json`；字节检查确认 CSS `content` 已由裸 UTF-8 `c2 b7` 改为 ASCII escape `5c 30 30 42 37`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正任务卡片进度行分隔符渲染稳定性，不改变需求中心阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；Change `design.md` 与 delta spec 已同步分隔符稳定显示要求。

### 2026-09-03 09:50:32 opsx.modify

- 反馈：用户复验截图指出进度行特殊符号仍然显示，明确要求 `研发 x/x`、`测试 x/x`、`人工验收 x/x` 之间改为纯空格/间距，不再出现 `·`、`Â·` 或其它特殊符号。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅修正进度行分隔方式和相关契约；不调整 label/value 字体、字号、颜色分层、三项同一行、任务进度抽屉能力、已完成阶段隐藏进度规则、卡片其它样式、列头、空列、sticky、筛选区、指标卡、新建 Capture、Action Modal、品牌区或其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-e4daa548-0f0c-4f2a-b593-3e1a8b9cb9b3.png` | 需求中心九阶段任务卡片，验收中列，含研发/测试/人工验收进度行 | `.rc-progress`、`.rc-progress-action + .rc-progress-action::before` | 三个进度项之间仅用空白间距分隔，不出现 `·`、`Â·` 或其它特殊符号 | 返修后仍通过 CSS `::before` 生成 `\00B7` 分隔点，视觉仍显示特殊符号 | 前一轮将“异常显示”误收敛为“保留正常点号”，未满足“无符号纯间距”期望 | 用户截图、源码检查、Vitest 样式契约、computed style | 本次修复：删除进度项 `::before` 分隔符规则，将 `.rc-progress` gap 改为 `10px`，用纯间距保持三项同一行 | `src/web/src/styles/globals.css`、`src/web/src/requirement-center.test.tsx`、`computed-styles.json` |

- 根因：此前返修只把裸字符 `·` 改成 CSS escape `\00B7`，解决的是编码稳定性，但仍保留了“显示分隔点”这个视觉契约；用户最新反馈确认目标应为无符号纯间距，因此需要移除伪元素而不是替换字符写法。
- 调整：`globals.css` 删除 `.rc-card .rc-progress-action + .rc-progress-action::before` 整段规则，并将 `.rc-card .rc-progress` 的 `gap` 从 `0` 改为 `10px`；进度按钮内部 `label/value` 的 `gap: 4px` 保持不变。
- 测试：更新 `requirement-center.test.tsx`，锁定 `.rc-progress` 使用 `gap: 10px`，并断言源码不再包含进度行 `::before` 分隔符、`\00B7` 或 `Â·`。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、`git diff --check -- <本轮相关文件>` 通过；Playwright 已刷新 `requirements-1440.png` 与 `computed-styles.json`，`.rc-progress` computed style 显示 `gap: 10px`，源码检查确认 `.rc-progress-action + .rc-progress-action::before` 已不存在。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅修正任务卡片进度行分隔视觉，不改变需求中心阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；Change `design.md` 与 delta spec 已同步无符号纯间距要求。

### 2026-09-03 21:47:10 opsx.modify

- 反馈：用户复验截图指出 `研发 x/x`、`测试 x/x`、`人工验收 x/x` 中的 `x/x` 数值颜色又被调回低对比灰色，未保持附件中 label/value 分层。
- 范围边界：仍属于 REQ-0023 现代 Ops 视觉系统验收返修；仅修正九阶段任务卡片进度行视觉回退；保持进度项之间不显示 `·`、`Â·` 或其它特殊符号，仅用 gap 分隔；不调整进度点击行为、卡片其它样式、缺失文档提示、已完成阶段隐藏进度规则、列头、空列、sticky、筛选区、指标卡、新建 Capture、Action Modal、品牌区或其它视觉系统。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-9206273d-6c55-46ca-a717-9a758fb0209b.png` 与附件 `moonbox-board (2).html` | 需求中心九阶段任务卡片，验收中列，含研发/测试/人工验收进度行 | 附件 `.card-metrics`、`.card-metrics b` 对照当前 `.rc-progress`、`.rc-progress-label`、`.rc-progress-value` | `.rc-progress` 使用 JetBrains Mono、10.5px；`研发/测试/人工验收` label 为低对比 tertiary；`x/x` value 为 secondary 并保持 600 字重；进度项之间仅用 gap，无特殊符号 | 返修后源码将 `.rc-progress` 改为 `var(--rc-font-body)`、`var(--rc-text-sm)`、`gap: 8px`，并将 `.rc-progress-value` 固化为 `color: inherit`、普通字重；测试也断言该错误状态 | 去除分隔符时误伤附件 `.card-metrics` 字体、字号、gap 和 label/value 颜色分层 | 用户截图、附件 CSS 对照、源码检查、Vitest 样式契约、Playwright computed style | 本次修复：恢复 `.rc-progress` 为 `var(--rc-font-accent)`、`10.5px`、`gap: 10px`；新增 `.rc-progress-label` 低对比色；恢复 `.rc-progress-value` 为 `var(--rc-muted)` 和 `var(--rc-weight-semibold)`；修正测试断言 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` |

- 根因：上一轮“取消进度行特殊符号”的返修同时把 `.rc-progress` 和 `.rc-progress-value` 改回了继承/普通 UI 口径，并将 `color: inherit` 与普通字重写入测试断言；这与 2026-09-03 08:57:10 已建立的附件 `.card-metrics` 视觉契约冲突。
- 调整：`globals.css` 恢复 `.rc-card .rc-progress` 的 JetBrains Mono 技术字体、10.5px 字号和 10px 纯 gap；新增 `.rc-card .rc-progress-label` 低对比色；`.rc-card .rc-progress-value` 恢复 secondary 层级 `var(--rc-muted)` 与 600 字重。
- 测试：`requirement-center.test.tsx` 删除错误的 `color: inherit` 与普通字重断言，改为锁定 label/value 分层、数值 `var(--rc-muted)`、`var(--rc-weight-semibold)`、等宽 10.5px 和无符号 gap。
- 验证：`node_modules/.bin/vitest --run --environment jsdom src/requirement-center.test.tsx`、`node_modules/.bin/tsc -b`、`node_modules/.bin/vite build`、`python scripts/validate-design-system.py`、`openspec validate update-product-workbench-modern-ops-visual-system --strict`、touched-file `git diff --check` 通过；Playwright 已刷新 `computed-styles.json`，`.rc-progress` computed style 为 JetBrains Mono、10.5px、`gap: 10px`，`.rc-progress-label` 为低对比色，`.rc-progress-value` 为 `rgb(152, 160, 179)`。
- REQ 子文档一致性扫尾检查：`requirement.md`、`business-flow.md`、`user-stories.md` 和 `prototype/**` 不需更新，原因：本次仅恢复任务卡片进度行视觉层级，不改变需求中心阶段定义、业务流程、API/DB、数据模型、权限、状态流转或 Mock/API 边界；`acceptance.md` 与 Change `trace.md` 回填本次复验证据。
