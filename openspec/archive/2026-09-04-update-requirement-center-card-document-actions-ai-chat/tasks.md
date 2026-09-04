---
change_id: update-requirement-center-card-document-actions-ai-chat
source_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
status: in_progress
created_at: 2026-08-18 09:58:34
updated_at: 2026-08-18 09:58:34
---

# Tasks

## 1. UI Skeleton 与契约

- [x] 1.1 在需求中心页面建立 UI Skeleton：卡片文档入口、阶段动作容器、AI 悬浮按钮、三类右侧抽屉和三类弹窗容器。
- [x] 1.2 完成 1440px Skeleton 首轮视觉检查，记录截图或等价证据入口。
- [x] 1.3 在 Change trace 中记录 Mock/API 边界、Prototype 事实源优先级和 Skeleton 状态。

## 2. 文档入口与详情跳转

- [x] 2.1 将卡片 `.md` 关联文档映射为右侧 Markdown 抽屉入口。
- [x] 2.2 将卡片 `.html` 关联文档映射为新 Tab 预览入口。
- [x] 2.3 实现卡片标题与“查看归档”新 Tab 详情跳转。
- [x] 2.4 覆盖文档缺失、类型不符、读取失败和权限不足异常分支。

## 3. Capture、AI 聊天与阶段动作

- [x] 3.1 实现 Capture 新建表单、标题必填校验、成功反馈和采集池插入。
- [x] 3.2 实现全局 AI 聊天悬浮按钮、右侧抽屉、消息输入和发送交互。
- [x] 3.3 实现卡片阶段动作到 `req-*`、`bug-*`、`sprint-*`、`opsx-*` 的映射。
- [x] 3.4 实现按钮 Loading、锁定、成功刷新流转和失败不流转。

## 4. 生成/完善、Sprint 与 tasks

- [x] 4.1 实现生成/完善方式选择弹窗和文件导入校验。
- [x] 4.2 实现 Sprint 选择弹窗与合法未关闭迭代校验。
- [x] 4.3 实现 `tasks.md` 只读进度抽屉。
- [x] 4.4 实现验收中受限勾选和归档门禁展示。

## 5. API / 数据 / 安全

- [x] 5.1 扩展或确认需求中心上下文返回文档入口、动作映射、Sprint 选项和 tasks 进度字段。
- [x] 5.2 增加受控 Markdown 读取和 HTML 预览边界，确保不暴露本机路径和内部堆栈。
- [x] 5.3 增加命令执行/AI 聊天反馈的脱敏错误和权限失败分支。

## 6. 测试与验收

- [x] 6.1 补充前端单元/集成测试覆盖 Capture、文档入口、AI 聊天、阶段动作、导入校验、tasks 抽屉和“已评审”文案。
- [x] 6.2 补充后端/API 测试覆盖文档白名单、脱敏错误、动作字段和 tasks 进度字段。
- [x] 6.3 执行 1440px 视觉验收，覆盖首屏、三类抽屉、三类弹窗、toast、Loading 和文本溢出。
- [x] 6.4 记录 computed style 验收点。
- [x] 6.5 回填 REQ 最终一致性检查状态。

## 7. 文档同步

- [x] 7.1 如 API 字段变化，同步 `docs/03-api-index.md` 与 OpenAPI 来源。
- [x] 7.2 如安全边界变化，同步安全相关说明或测试。
- [x] 7.3 更新 Change `trace.md` 的实现、验收和证据入口。

## 验收返修记录

### 2026-08-18 opsx.modify：未入迭代阶段隐藏 Sprint 标签

- 反馈：采集池、规划中、待评审、已评审阶段尚未执行 Sprint 纳入动作，不应展示 `sprint-xxx` 标签，也不应进入 Sprint 筛选来源。
- 证据状态：confirmed。实现中后端从 `target_iteration` / `iteration` 派生 `sprint_id`，前端只要 `issue.sprintId` 存在就展示 `.rc-sprint-tag` 并加入 Sprint 筛选。
- 调整：后端仅在迭代规划及后续阶段输出 `sprint_id`；前端增加 `visibleSprintId` 守卫，卡片标签、Sprint 筛选项和筛选匹配均排除未入迭代四列的历史迭代字段。
- 测试：新增前端回归测试覆盖已评审卡片隐藏历史 Sprint 且不进入筛选；新增后端回归测试覆盖 `approved + target_iteration` 不输出 `sprint_id`。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 和 `prototype/**` 未更新，原因：本次修正为 Sprint 标签显示语义，不改变流程图、用户故事主体或原型资产。

### 2026-08-18 opsx.modify：Capture 弹窗轻量紧凑化

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `codex-clipboard-64990504-4bb3-4f41-b7c9-2266bd287e6c.png` |
| 页面/状态 | `/requirements`，深色主题，新建 Capture 弹窗，桌面视口截图 |
| 对照对象 | 用户验收截图与当前 Capture 弹窗实现 |
| 期望表现 | 采用轻量紧凑表单；减少字段分割线；标题必填与标签同行；类型和优先级使用快速选择控件；取消/创建按钮风格统一；标题自动聚焦并有校验态 |
| 实际表现 | 截图中字段间分割线较多，纵向留白偏大，类型/优先级为下拉，标题必填星号独立成行，取消按钮接近浏览器默认样式 |
| 偏差项 | 信息密度、分割线噪声、必填表达、按钮层级、控件选择效率、标题输入焦点与错误态 |
| 检查方式 | 截图视觉对照、DOM 结构与 Vitest 交互断言 |
| 处置结论 | 本次修复：Capture 弹窗增加紧凑变体、segmented 类型选择、pill 优先级选择、标题 autofocus、输入框 invalid 错误态、统一次级/主按钮 |
| 证据入口 | `src/web/src/requirement-center.test.tsx` 38 tests pass；Change trace 验证记录 |

- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 未更新，原因：本次仅优化 Capture 表单呈现和输入交互，不改变业务流程、状态流转和角色路径；`prototype/**` 未更新，原因：用户截图作为本次验收反馈事实源，原型资产仍作为初始结构参考。

### 2026-08-18 opsx.modify：采集池文档、探索动作与 Capture 二次返修

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `codex-clipboard-ffae2912-c80c-48bb-83da-f1306f622f5c.png` |
| 页面/状态 | `/requirements`，深色主题，采集池卡片 |
| 对照对象 | 用户验收截图、当前卡片文档入口和任务进度展示 |
| 期望表现 | 采集池只展示 `capture.md`、`trace.md`；不展示历史需求六件套；不展示“研发 18/18”；提供需求探索/BUG探索辅助动作 |
| 实际表现 | 截图中采集池 REQ 卡片展示 acceptance、business-flow、requirement、review、user-stories 等历史文档，并展示“研发 18/18” |
| 偏差项 | 阶段文档白名单缺失、未入开发阶段研发进度泄漏、采集池探索辅助动作缺失 |
| 检查方式 | 代码路径、Vitest 回归测试、Playwright 1440px 截图、computed style / DOM 摘要 |
| 处置结论 | 本次修复：卡片文档入口按阶段可展示白名单裁剪；采集池严格只显示 `capture.md` 和 `trace.md`；研发进度仅在待开发及后续阶段展示；采集池 Requirement/Bug 分别新增“需求探索”“BUG探索”辅助按钮 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-filter-actions/01-capture-card-filter-1440.png`；`computed-capture-filter-actions-1440.json`；`src/web/src/requirement-center.test.tsx` 39 tests pass |

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `codex-clipboard-d445e23f-1e32-47b6-aec9-87e8a07f27ed.png` |
| 页面/状态 | `/requirements`，深色主题，新建 Capture 弹窗 |
| 对照对象 | 用户验收截图与当前 Capture 弹窗 |
| 期望表现 | 标题必填与标签同行；弱化字段分割线；继续压缩纵向留白；取消/创建按钮使用一致设计语言；校验态清楚但不压过表单 |
| 实际表现 | 截图中标题必填星号仍独立成行，标题输入 focus ring 较强，顶部区隔和纵向空间仍偏重 |
| 偏差项 | 必填标记对齐、视觉噪声、表单高度、焦点/校验层级 |
| 检查方式 | Playwright 1440px 截图、computed style / DOM 摘要、Vitest 交互断言 |
| 处置结论 | 本次修复：标题/必填标记改为 `.rc-field-label` 行内结构；弱化标题区分割线；压缩弹窗 padding、字段间距、textarea 高度；降低 invalid/focus ring 强度；按钮保持统一主次样式 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-filter-actions/03-capture-dialog-compact-1440.png`；`04-capture-validation-1440.png`；`computed-capture-filter-actions-1440.json` |

- 测试：`pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` 39 tests pass，新增覆盖阶段文档白名单、采集池隐藏研发进度、需求探索/BUG探索辅助动作、HTML 入口保留与 Capture 校验态。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只修正卡片展示、辅助动作和弹窗交互，不改变业务状态流转、角色目标或用户故事主路径；`prototype/**` 未更新，原因：用户验收截图作为本次返修事实源，原型资产保留初始结构参考。

### 2026-08-18 opsx.modify：采集池卡片视觉按原型收口

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `codex-clipboard-4b1f6821-29c5-4d8e-9a5c-36bf68ce38e4.png`、`codex-clipboard-f6e1e512-391b-4a2e-9380-e6a084c252e6.png` |
| 页面/状态 | `/requirements`，深色主题，采集池卡片与规划中列 |
| 对照对象 | 原型截图与当前实现截图 |
| 期望表现 | 可用文档入口为原型式金色文本链接，以空格分隔；主动作和辅助分析动作同在 footer 右侧；Requirement 文案为“需求分析”，Bug 文案为“Bug 分析”；缺失文档提示轻量且不撑高卡片；卡片减少多余分割线和纵向留白 |
| 实际表现 | 当前实现中可用文档为带图标 chip；辅助动作为左侧描边按钮且文案为“需求探索 / BUG探索”；缺失文档提示和按钮占据卡片中部，卡片显得偏高偏散 |
| 偏差项 | 文档入口样式、辅助动作位置与文案、缺失态层级、卡片纵向留白、多余视觉分割 |
| 检查方式 | Playwright 1440px 截图、DOM/computed 摘要、Vitest 回归测试、TypeScript build |
| 处置结论 | 本次修复：文档入口去图标和 chip 化，改为金色文本链接；辅助分析动作移入 footer 右侧并改为“需求分析 / Bug 分析”；缺失提示轻量化；压缩卡片 padding、文档区和 footer 间距 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-prototype-card-visual/01-capture-cards-prototype-actions-1440.png`；`02-capture-analysis-ai-drawer-1440.png`；`computed-prototype-card-visual-1440.json` |

- 测试：`pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` 39 tests pass；`pnpm --dir src/web build` pass。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次仅调整卡片视觉层级、文案和动作位置，不改变业务流程、角色目标或状态流转；`prototype/**` 未更新，原因：原型截图作为本次对照事实源，修复结果已通过 Change evidence 回填。

### 2026-08-18 opsx.modify：采集池卡片分隔符、字体和 footer 层级细化

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `codex-clipboard-f9fae6bf-f4eb-44c1-8482-cbe53c9a912b.png` |
| 页面/状态 | `/requirements`，深色主题，采集池卡片 |
| 对照对象 | 用户验收截图与当前采集池卡片实现 |
| 期望表现 | `capture.md` 与 `trace.md` 使用空格分隔，不出现乱码；文档链接字体/字重对齐轻量缺失提示并保持可点击；缺失提示与上方分割线间距更紧凑；footer 文字按钮不加粗，主动作金色，需求分析/Bug 分析为蓝灰色辅助动作 |
| 实际表现 | 截图中文档入口中间出现 `Â·` 类乱码；文档链接和 footer 动作偏粗；需求分析显示为金色，层级接近主动作；缺失提示与分割线间距偏高 |
| 偏差项 | 分隔符渲染方式、字体字重、footer 主次层级、缺失提示间距 |
| 检查方式 | DOM/computed 摘要、Playwright 1440px 截图、Vitest 回归测试、TypeScript build |
| 处置结论 | 本次修复：文档分隔符改为显式空格节点；文档链接字重改为 400；缺失提示 `margin-top` 压缩为 4px；footer 按钮统一 400 字重，`.primary` 保持金色，`.secondary` 固定蓝灰色 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-card-typography-spacing/01-capture-card-typography-spacing-1440.png`；`02-capture-analysis-secondary-action-1440.png`；`computed-card-typography-spacing-1440.json` |

- 测试：`pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` 39 tests pass；`pnpm --dir src/web build` pass。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次仅调整采集池卡片视觉细节和点击入口呈现，不改变业务流程、角色目标或状态流转；`prototype/**` 未更新，原因：本次用户截图为验收反馈事实源，修复结果已通过 Change evidence 回填。

### 2026-08-18 opsx.modify：Markdown 抽屉蒙层、宽度和 capture.md 受控编辑

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements`，Markdown 右侧抽屉，采集池 `capture.md` / `trace.md` |
| 对照对象 | 当前实现与用户反馈 |
| 期望表现 | Markdown 抽屉打开后背景有蒙层；桌面端抽屉可在 420px-760px 调整宽度，移动端全屏；采集池 `capture.md` 支持编辑保存；`trace.md` 保持只读；未保存修改关闭前二次确认 |
| 实际表现 | 当前抽屉为裸 `aside`，无蒙层；宽度固定；Markdown 以 `<pre>` 只读展示；后端仅有文档读取和 HTML 预览接口 |
| 偏差项 | 阅读层级、抽屉宽度弹性、采集池文档编辑能力、保存权限边界、未保存保护 |
| 检查方式 | 代码路径、前端 Vitest、后端 pytest、Playwright 1440px 截图、computed style |
| 处置结论 | 本次修复：新增抽屉 layer/backdrop、拖拽宽度、移动端全屏 CSS、`capture.md` 编辑器、保存按钮、未保存关闭确认；后端新增受控 PUT 保存接口，仅允许采集池 `capture.md`，阻断 `trace.md` 与非采集池阶段 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-markdown-drawer-edit/01-markdown-drawer-backdrop-edit-1440.png`；`02-capture-save-success-1440.png`；`03-drawer-resized-1440.png`；`04-trace-readonly-1440.png`；`computed-markdown-drawer-edit-1440.json` |

- 测试：`pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` 40 tests pass；`uv run pytest tests/integration/api/test_requirement_center.py` 11 tests pass；`pnpm --dir src/web build` pass。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次增强文档抽屉阅读/编辑交互和受控保存边界，不改变业务流程、角色目标或状态流转；`prototype/**` 未更新，原因：当前验收反馈明确覆盖原型静态演示中的 Markdown 交互不足，最终行为已在 Change design/spec 和 evidence 中回填。

### 2026-08-18 opsx.modify：capture.md 默认预览与手动编辑态

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements`，采集池卡片 `capture.md` Markdown 右侧抽屉 |
| 对照对象 | 当前实现与用户确认的交互规则 |
| 期望表现 | 采集池 `capture.md` 抽屉打开默认是预览态；用户点击“编辑”后进入编辑态；保存成功后回到预览态并回显最新内容；未保存关闭确认保留；`trace.md` 继续只读 |
| 实际表现 | 上一轮实现中采集池 `capture.md` 打开后直接显示编辑器，阅读和编辑状态没有显式分离 |
| 偏差项 | 默认状态、编辑入口、保存后状态回落、预览回显 |
| 检查方式 | React 状态机检查、Vitest 回归测试、TypeScript build、Playwright 1440px 截图、DOM/computed 摘要 |
| 处置结论 | 本次修复：Markdown 抽屉新增 `preview/edit` 模式；`capture.md` 加载完成后默认预览；“编辑”按钮进入编辑态；保存成功使用服务端返回内容更新 `content/draft` 并回到预览态；脏关闭确认仅在编辑态且内容未保存时触发；`trace.md` 不出现编辑入口 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260818-capture-preview-edit/01-capture-md-preview-default-1440.png`；`02-capture-md-edit-mode-1440.png`；`03-capture-md-save-back-preview-1440.png`；`04-trace-md-readonly-1440.png`；`computed-capture-preview-edit-1440.json` |

- 测试：`pnpm --dir src/web exec vitest run src/requirement-center.test.tsx` 40 tests pass；`pnpm --dir src/web build` pass。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只细化 Markdown 抽屉阅读/编辑状态，不改变业务流转、角色目标或用户故事主路径；`prototype/**` 未更新，原因：本次用户文本反馈为验收事实源，最终行为已通过 Change design/spec、测试和 evidence 回填。

### 2026-08-30 opsx.modify：受控 demo 模式补齐 9 阶段卡片

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `codex-clipboard-e9dc9b12-bd93-4720-a32e-b55260ab0775.png` |
| 页面/状态 | `/requirements`，深色主题，9 阶段需求研发流转看板 |
| 对照对象 | 用户实际截图、当前真实 `/context` 数据和原型 9 阶段看板验收口径 |
| 期望表现 | Mock/demo 模式下每个阶段至少展示 1 张卡片，便于验收卡片密度、文档入口、阶段动作、Sprint 标签、研发进度、验收和归档状态 |
| 实际表现 | 当前真实数据分布为 `capture=1`、`planning=0`、`review-ready=0`、`approved=0`、`sprint-planning=0`、`ready-dev=31`、`development=1`、`acceptance=1`、`done=1`；多个阶段为空，无法完整验收视觉状态 |
| 偏差项 | 视觉验收夹具不足；真实治理数据不应为了演示而被污染 |
| 检查方式 | 只读阶段统计、前端 demo query 开关、Vitest、TypeScript build、Playwright 1440px 截图、DOM/computed 摘要 |
| 处置结论 | 本次修复：新增 `?mock=workflow` / `?demo=workflow` 受控前端 demo context，使用 `DEMO-` 前缀卡片覆盖 9 阶段每列至少 1 张；未显式启用时仍从真实 `/api/v1/requirement-center/context` 加载，不改后端 API、DB 或治理真实数据 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-mode/01-workflow-demo-9-stage-1440.png`；`02-workflow-demo-bug-filter-1440.png`；`computed-workflow-demo-mode-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 44 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- Mock/API 边界：默认路径继续读取真实 API；显式 demo query 才使用前端内置 demo context；demo 数据只服务视觉验收和产品演示，不写回真实治理文件、后端接口或数据库。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只补充视觉验收/demo 数据入口，不改变业务状态流转、角色目标或用户故事主路径；`prototype/**` 未更新，原因：原型仍作为 9 阶段结构事实源，demo 模式是实现侧验收夹具。

### 2026-08-30 opsx.modify：workflow demo 文档内容补齐

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements?mock=workflow`，受控 demo 模式，Markdown 抽屉与 HTML 新 Tab |
| 对照对象 | 当前 demo 卡片文档入口实现和真实 API 文档读取边界 |
| 期望表现 | demo 卡片关联文档不为空；Markdown 抽屉打开后展示与卡片阶段匹配的 mock 文档正文；HTML 入口可打开 demo 预览；默认真实 API 文档读取不受影响 |
| 实际表现 | demo 卡片仅提供文档入口字段，Markdown/HTML 入口仍指向真实文档 URL，`DEMO-*` 对象没有真实落盘文件时正文为空或读取失败 |
| 偏差项 | demo 文档正文缺失、HTML demo 预览缺失、demo 与真实文档 API 边界未覆盖到文档内容层 |
| 检查方式 | 代码路径、Vitest 回归测试、TypeScript build、Playwright 1440px 截图、DOM/computed 摘要 |
| 处置结论 | 本次修复：为 demo 文档入口补充 `content` / `htmlContent`；Markdown demo 入口直接展示内置正文且不请求真实文档 API；HTML demo 入口通过 Blob 新 Tab 打开；demo `capture.md` 保存只更新抽屉内 mock 内容并回到预览态 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260830-workflow-demo-documents/01-demo-markdown-document-1440.png`；`02-demo-html-preview-1440.png`；`03-default-real-document-api-1440.png`；`computed-workflow-demo-documents-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 45 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- Mock/API 边界：默认路径继续读取真实 `/api/v1/requirement-center/context` 与真实文档 API；显式 demo query 下卡片和文档内容使用前端内置脱敏样例，不读取或写入真实治理文件、后端接口或数据库。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只补齐 demo 文档内容与预览边界，不改变业务状态流转、角色目标或用户故事主路径；`prototype/**` 未更新，原因：原型仍作为结构事实源，demo 文档正文是实现侧验收夹具。

### 2026-09-01 opsx.modify：采集池 footer 动作顺序调整

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements?mock=workflow`，深色主题，采集池 Requirement 卡片 footer |
| 对照对象 | 当前实现中采集池卡片 footer 动作顺序 |
| 期望表现 | “需求分析”排在“生成需求”左侧，形成先分析、再生成的阅读顺序 |
| 实际表现 | 当前 JSX 先渲染主生成动作，再渲染辅助分析动作，视觉顺序为“生成需求 → 需求分析” |
| 偏差项 | footer 动作顺序与验收期望不一致 |
| 检查方式 | DOM 顺序断言、Vitest、TypeScript build、Playwright 1440px 截图和 computed/DOM 摘要 |
| 处置结论 | 本次修复：采集池辅助动作先渲染，主生成动作后渲染；Requirement footer 为“需求分析 / 生成需求”，Bug footer 为“Bug 分析 / 生成 Bug”；按钮颜色、字重、命令映射和流转语义不变 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260901-capture-action-order/01-capture-action-order-1440.png`；`computed-capture-action-order-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 51 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次仅调整卡片 footer 操作顺序，不改变业务流转、角色目标、文档内容、API/DB/权限或用户故事主路径；`prototype/**` 未更新，原因：用户文本反馈为本次验收事实源，原型结构未变。

### 2026-09-01 opsx.modify：采集池与规划中主动作文档非空门禁

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements` 与 `/requirements?mock=workflow`，采集池和规划中卡片 footer |
| 对照对象 | 当前 context action 门禁与前端右下角主动作禁用状态 |
| 期望表现 | 采集池“需求分析 / Bug 分析”随时可用且不锁定；采集池“生成需求 / 生成 Bug”必须在 `trace.md`、`capture.md` 均存在且内容非空时可用；规划中“完善需求”必须在 `trace.md`、`capture.md`、`requirement.md` 均存在且内容非空时可用；规划中“完善 Bug”必须在 `trace.md`、`capture.md`、`bug.md` 均存在且内容非空时可用 |
| 实际表现 | 当前后端只按部分文件名缺失和数据漂移生成 `disabled_reason`，未检查采集池 `capture.md` / `trace.md` 非空，也未要求规划中保留非空 `capture.md` |
| 偏差项 | 主动作启用门禁不完整；空文档也可能进入生成/完善选择 |
| 检查方式 | 后端 context 聚合测试、前端禁用状态测试、TypeScript build |
| 处置结论 | 本次修复：后端 `_blocked_reason` 按阶段和类型检查必需文档存在且内容非空，并通过 `action.disabled_reason` 禁用主动作；前端继续按该字段禁用主动作，同时辅助分析动作保持可用 |
| 证据入口 | `tests/integration/api/test_requirement_center.py`；`src/web/src/requirement-center.test.tsx` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 51 tests pass；`uv run pytest tests/integration/api/test_requirement_center.py` 13 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- product_data_collection_observability：N/A。本次只读取治理文档文件内容判断按钮启用，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只收紧主动作门禁，不改变业务阶段顺序、角色目标或用户故事主路径；`prototype/**` 未更新，原因：用户文本反馈是本次门禁事实源，原型结构未变。

### 2026-09-01 opsx.modify：未入迭代阶段必备文档门禁扩展

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements`，采集池、规划中、待评审、已评审卡片 footer 主动作 |
| 对照对象 | 当前 context action 门禁与 Requirement / Bug 阶段必备文档清单 |
| 期望表现 | 采集池需求/BUG主生成动作要求 `capture.md`、`trace.md` 均存在且内容非空；规划中需求要求 `capture.md`、`trace.md`、`requirement.md` 非空，规划中 BUG 要求 `capture.md`、`trace.md`、`bug.md` 非空；待评审需求要求 `capture.md`、`trace.md`、`requirement.md`、`acceptance.md`、`business-flow.md`、`user-stories.md` 非空，待评审 BUG 要求 `capture.md`、`trace.md`、`bug.md`、`root-cause.md`、`workaround.md`、`acceptance.md` 非空；已评审在对应待评审文档包基础上额外要求 `review.md` 非空 |
| 实际表现 | 当前后端门禁只覆盖采集池和规划中，待评审仍按旧逻辑只看 `acceptance.md` / `trace.md`，已评审未执行文档包非空门禁 |
| 偏差项 | 待评审和已评审卡片在关键文档缺失或为空时仍可能触发评审或加入迭代 |
| 检查方式 | 后端 context 聚合测试、OpenSpec strict、中文/模板语言校验、diff check |
| 处置结论 | 本次修复：将 `_required_action_documents` 扩展为四阶段 Requirement / Bug 文档包表，并继续通过 `action.disabled_reason` 禁用主动作；采集池分析辅助动作仍不受主动作门禁影响 |
| 证据入口 | `tests/integration/api/test_requirement_center.py` |

- 测试：`uv run pytest tests/integration/api/test_requirement_center.py` 13 tests pass；`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 51 tests pass；本轮未改前端渲染逻辑，前端继续消费既有 `disabled_reason`。
- product_data_collection_observability：N/A。本次只收紧既有 context 聚合字段语义，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只扩展主动作文档门禁，不改变业务阶段顺序、角色目标或用户故事主路径；`prototype/**` 未更新，原因：用户文本反馈是本次门禁事实源，原型结构未变。

### 2026-09-01 opsx.modify：缺失文档 Tips 同源门禁

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements`，卡片文档区下方缺失/异常 Tips |
| 对照对象 | 当前卡片 Tips 与主动作 `action.disabled_reason` 门禁 |
| 期望表现 | 缺失文档 Tips 基于阶段 + 类型必备文档表实现，优先展示后端 `action.disabled_reason`；前端 fallback 同步使用 `requiredDocsForIssue(stage, type)`，并区分缺少文档、文档内容为空和数据漂移 |
| 实际表现 | 当前 Tips 使用 `stage.requiredDocs` 计算，属于列级缺失判断，不区分 Requirement / Bug，也不会展示后端空文档或数据漂移原因 |
| 偏差项 | Tips 与按钮禁用原因可能不一致；待评审和已评审的 Requirement / Bug 文档包提示不完整 |
| 检查方式 | 前端渲染测试、后端 context 聚合测试、TypeScript build、OpenSpec strict、中文/模板语言校验、diff check |
| 处置结论 | 本次修复：新增前端 `requiredDocsForIssue(stage, type)`，Tips 优先展示 `action.disabled_reason`，无后端原因时按同一张必备文档表兜底生成“缺少 ...” |
| 证据入口 | `src/web/src/requirement-center.test.tsx`；`tests/integration/api/test_requirement_center.py` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 52 tests pass；`uv run pytest tests/integration/api/test_requirement_center.py` 13 tests pass。
- product_data_collection_observability：N/A。本次只调整前端 Tips 展示和既有 context 字段消费，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只统一异常 Tips 展示口径，不改变业务阶段顺序、角色目标或用户故事主路径；`prototype/**` 未更新，原因：用户文本反馈是本次门禁 Tips 事实源，原型结构未变。

### 2026-09-01 opsx.modify：workflow demo 验收矩阵重做

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements?mock=workflow`，受控 demo 模式，9 阶段看板 |
| 对照对象 | 当前 workflow demo mock 数据与已知验收场景集合 |
| 期望表现 | demo 数据重新设计为验收矩阵，覆盖各阶段 Requirement / Bug 正常、缺失文档、空文档、数据漂移、按钮禁用、采集池 `capture.md` 可编辑、`trace.md` 只读、HTML 新 Tab、Sprint 标签隐藏/显示、tasks 进度和归档入口 |
| 实际表现 | 当前 demo 主要覆盖 9 列有卡片，规划中、待评审、已评审等阶段文档包与最新门禁不一致，缺少足够的异常态和双类型对照 |
| 偏差项 | demo 数据像布局样例，不像验收夹具；无法一次性验收已知业务规则组合 |
| 检查方式 | 前端渲染测试、Playwright 1440px 截图、DOM/computed 摘要、TypeScript build、OpenSpec strict、diff check |
| 处置结论 | 本次修复：重做受控 demo context 为 24 张语义化 `DEMO-` 卡片；采集池、规划中、待评审、已评审各覆盖 Requirement / Bug 正常与异常组合，开发链路各阶段覆盖 Sprint、tasks、受限验收和归档入口；默认真实 API 数据不受影响 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260901-workflow-demo-matrix/01-workflow-demo-matrix-1440.png`；`computed-workflow-demo-matrix-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 53 tests pass；`node tmp-workflow-demo-evidence.mjs` 生成 1440px 视觉证据后已删除临时脚本。
- Mock/API 边界：默认路径继续读取真实 `/api/v1/requirement-center/context` 与真实文档 API；显式 demo query 下卡片、文档正文和 HTML 预览使用前端内置脱敏样例，不读取或写入真实治理文件、后端接口或数据库。
- product_data_collection_observability：N/A。本次只调整前端显式 demo 数据和验收证据，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只重做显式 demo 验收夹具，不改变业务阶段顺序、角色目标或用户故事主路径；`prototype/**` 未更新，原因：原型仍作为结构事实源，demo 矩阵是实现侧验收夹具。

### 2026-09-02 opsx.modify：待评审二次确认与已评审 action 重算

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements?mock=workflow`，待评审 Requirement / Bug 卡片动作与流转后的已评审卡片 |
| 对照对象 | 当前卡片 footer 主动作、二次确认弹窗和已评审阶段 Sprint 选择 |
| 期望表现 | 待评审阶段“发起评审 / 确认修复”点击后必须先二次确认；确认成功从待评审流转到已评审后，主动作必须变为“加入迭代 →”，再次点击要求选择 Sprint |
| 实际表现 | 返修前本地乐观流转只更新 `stage`，保留后端初始 `action`，导致已评审卡片仍显示“发起评审 / 确认修复”旧动作 |
| 偏差项 | 状态与 action 不一致；已评审阶段未进入 Sprint 选择门禁 |
| 检查方式 | 前端回归测试、TypeScript build、Playwright 1440px 截图和 DOM 摘要 |
| 处置结论 | 本次修复：为待评审动作增加 `review` 二次确认选择态；抽出阶段 action 重算器，流转后按目标阶段刷新 `action`，已评审阶段命令映射为 `/sprint-propose --req|--bug <ID>` 并要求 Sprint 选择 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260902-review-confirmation-action-refresh/01-review-confirmation-dialog-1440.png`；`02-review-action-recomputed-approved-1440.png`；`03-bug-sprint-choice-after-review-1440.png`；`computed-review-confirmation-action-refresh-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 54 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- Mock/API 边界：默认真实 API 路径不受影响；本次视觉证据使用显式 workflow demo 数据验证确认弹窗、action 重算和 Sprint 选择链路。
- product_data_collection_observability：N/A。本次只调整前端状态流转、二次确认和本地 action 重算，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次不改变阶段顺序和角色目标，只补齐待评审确认与已评审动作门禁；`prototype/**` 未更新，原因：用户文本反馈明确覆盖本次状态交互细节，原型结构未变。

### 2026-09-03 opsx.modify：验收中统一进度抽屉入口

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件截图 `codex-clipboard-4bcf6177-aa60-45eb-b8a9-1463da394c9e.png` |
| 页面/状态 | `/requirements?mock=workflow`，验收中 Requirement / Bug 卡片进度区 |
| 对照对象 | 当前卡片研发、测试、人工验收进度入口与右侧进度抽屉 |
| 期望表现 | 验收中卡片的测试进度和人工验收进度应与研发进度一样可点击；点击后打开右侧统一进度抽屉，并根据点击来源默认聚焦对应分区 |
| 实际表现 | 返修前只有“研发 x/x”为按钮并打开右侧抽屉，“测试 x/x”和“人工验收 x”为普通文本 |
| 偏差项 | 同一进度族交互不一致；测试和人工验收缺少可发现的详情入口 |
| 检查方式 | 前端回归测试、TypeScript build、Playwright 1440px 截图和 DOM 摘要 |
| 处置结论 | 本次修复：将研发、测试、人工验收统一渲染为 `rc-progress-action` 轻量文本按钮；右侧 tasks 抽屉改为统一进度抽屉，展示研发任务、自动化测试、人工验收三类分区，并按点击来源高亮 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260903-unified-progress-drawer/01-acceptance-test-progress-drawer-1440.png`；`02-acceptance-manual-progress-drawer-1440.png`；`computed-unified-progress-drawer-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 57 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- Mock/API 边界：默认真实 API 数据不受影响；本次视觉证据使用显式 workflow demo 数据验证验收中 Requirement / Bug 进度入口和右侧抽屉聚焦状态。
- product_data_collection_observability：N/A。本次只调整前端进度入口和抽屉展示，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次不改变阶段流转、角色目标或验收门禁，只补齐验收中进度入口族的交互一致性；`prototype/**` 未更新，原因：用户截图反馈是本次验收事实源，原型结构未变。

### 2026-09-03 opsx.modify：验收中进度区视觉与人工验收分数格式

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈，指向上一轮验收中卡片附件视觉 |
| 页面/状态 | `/requirements?mock=workflow`，验收中 Requirement / Bug 卡片进度区 |
| 对照对象 | 当前卡片 `.rc-progress` 视觉、人工验收文案和右侧统一进度抽屉 |
| 期望表现 | 上一轮误将附件预期理解为金色内联文本；该结论已被 2026-09-03 08:30:40 返修记录纠正，最终以 Image #2 的灰蓝色次级内联文本为准 |
| 实际表现 | 返修前 `.rc-card .rc-progress` 使用 `font-size: 10px`、`font-family: var(--rc-font-mono)`、`gap: 10px`；测试也锁定了 `人工验收 {manualAcceptanceCount}` 的单值格式 |
| 偏差项 | 字号、字体、字重、间距、默认按钮视觉、人工验收进度格式 |
| 检查方式 | 前端回归测试、TypeScript build、Playwright 1440px 截图和 computed style 摘要 |
| 处置结论 | 本轮仅保留 `manualAcceptanceProgress` 与人工验收 `已完成/总数` 格式；进度区视觉已由 2026-09-03 08:30:40 返修改为灰蓝色次级内联文本、点分隔和常规字重 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260903-progress-typography/01-acceptance-test-progress-typography-1440.png`；`02-acceptance-manual-progress-typography-1440.png`；`computed-progress-typography-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 57 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- Mock/API 边界：默认真实 API 数据不受影响；新增前端兼容字段只消费已有或未来的 `manual_acceptance_progress`，未改变后端接口、数据库或真实治理文档读取。
- product_data_collection_observability：N/A。本次只调整前端展示口径和显式 demo 视觉证据，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只调整进度入口视觉和人工验收展示格式，不改变业务阶段、角色目标、验收门禁或主路径；`prototype/**` 未更新，原因：用户验收反馈和上一轮附件视觉是本次事实源，原型结构未变。

### 2026-09-03 opsx.modify：按 Image #2 重新对齐验收中进度区次级视觉

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户附件 Image #2 为预期效果；Image #1 为上一轮当前实现效果 |
| 页面/状态 | `/requirements?mock=workflow`，验收中 Requirement / Bug 卡片进度区 |
| 对照对象 | Image #2 附件预期、Image #1 当前实现和 `.rc-progress` computed style |
| 期望表现 | 研发、测试、人工验收保持可点击并打开统一进度抽屉，但默认视觉应为灰蓝色次级内联文本；三项之间使用点分隔；不得使用金色主动作色或加粗；人工验收保持 `已完成/总数` 格式 |
| 实际表现 | 上一轮实现把进度区改为金色、600 字重和 16px 间距，导致进度信息与文档链接、右下主动作同层级，偏离 Image #2 的次级信息层级 |
| 偏差项 | 颜色、字重、视觉层级、分隔符、项间距 |
| 检查方式 | 前端回归测试、TypeScript build、Playwright 1440px 截图和 computed style 摘要 |
| 处置结论 | 本次修复：`.rc-progress` 改为 `var(--rc-muted)` 灰蓝次级色、`var(--rc-weight-regular)` 常规字重、8px gap；通过相邻按钮伪元素恢复点分隔；按钮默认仍无边框无底色且保持可点击 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260903-progress-muted-inline/01-acceptance-progress-muted-inline-1440.png`；`02-acceptance-test-drawer-muted-inline-1440.png`；`03-acceptance-manual-drawer-muted-inline-1440.png`；`computed-progress-muted-inline-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 57 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- Mock/API 边界：默认真实 API 数据不受影响；本次仅调整前端进度区视觉层级，不改后端接口、数据库或真实治理文档读取。
- product_data_collection_observability：N/A。本次只调整前端展示样式和显式 demo 视觉证据，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只纠正进度入口视觉层级，不改变业务阶段、角色目标、验收门禁或主路径；`prototype/**` 未更新，原因：用户明确 Image #2 为附件预期，本次以该截图反馈作为事实源。

### 2026-09-03 opsx.modify：开发链路必需文档表与 tasks.md 进度抽屉

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | 用户文本验收反馈 |
| 页面/状态 | `/requirements?mock=workflow`，研发中、验收中、已完成阶段卡片文档入口与验收中进度入口 |
| 对照对象 | 当前开发链路文档入口白名单、缺失文档 Tips、workflow demo mock 数据和进度抽屉 |
| 期望表现 | 研发中和验收中阶段必需文档统一为 `proposal.md`、`spec.md`、`design.md`、`trace.md`、`tasks.md`；已完成阶段必需文档为 `proposal.md`、`spec.md`、`design.md`、`trace.md`、`tasks.md`、`archive.md`；点击研发/测试/人工验收均打开右侧 `tasks.md` 抽屉并按来源聚焦分区 |
| 实际表现 | 返修前研发中、验收中和已完成仍沿用较早的阶段局部文档表，验收中展示 `acceptance.md` / `test-plan.md`，已完成只展示 `archive.md` / `trace.md`，与开发链路必需文档表不一致 |
| 偏差项 | 阶段可见文档白名单、缺失 Tips 兜底表、demo 文档夹具、进度点击语义 |
| 检查方式 | 前端回归测试、TypeScript build、OpenSpec strict、Playwright 1440px 截图和 DOM/computed 摘要 |
| 处置结论 | 本次修复：统一 `stages.requiredDocs` 与 `stageVisibleDocs` 的开发链路文档表；workflow demo 卡片与 mock 文档正文同步更新；测试覆盖研发中、验收中、已完成文档裁剪和验收中三类进度点击打开 `tasks.md` 抽屉 |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260903-dev-chain-docs-tasks-drawer/` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 57 tests pass；其余验证和 1440px 视觉证据见本轮最终输出。
- Mock/API 边界：默认真实 API 数据不受影响；显式 workflow demo 数据只用于验收矩阵和视觉证据，不写回真实治理文档、后端接口或数据库。
- product_data_collection_observability：N/A。本次只调整前端阶段文档白名单、demo 数据和抽屉入口语义，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次不改变用户旅程、业务流转或角色协作主路径，只收敛开发链路文档表与卡片展示规则；`prototype/**` 未更新，原因：用户文本反馈补充了开发链路必需文档表，属于当前实现验收口径。

### 2026-09-03 opsx.modify：进度区移除特殊分隔符

| 字段 | 内容 |
|---|---|
| 附件/截图编号 | `codex-clipboard-b554793f-ffdb-433c-b726-57275753ec16.png` |
| 页面/状态 | `/requirements?mock=workflow`，验收中 Requirement / Bug 卡片进度区 |
| 对照对象 | 用户截图、`.rc-progress` DOM 文本和 computed style |
| 期望表现 | 研发、测试、人工验收仍是可点击进度入口，但进度项之间只使用空格与 CSS `gap` 分隔，不出现 `Â·`、`·` 或其他特殊分隔符 |
| 实际表现 | 截图中 `研发 7/7`、`测试 3/3`、`人工验收 1/1` 之间出现 `Â·`，源码证据显示来自 `.rc-progress-action + .rc-progress-action::before { content: "·"; }` |
| 偏差项 | 特殊分隔符编码、进度区可读性、视觉验收稳定性 |
| 检查方式 | 源码搜索、前端样式契约测试、Playwright 1440px 截图、DOM/computed JSON |
| 处置结论 | 本次修复：删除进度区相邻按钮伪元素分隔符，仅保留 `.rc-progress { gap: 8px; }` 与按钮内部 `gap: 4px`；测试禁止 `.rc-progress-action + .rc-progress-action::before`、`content: "·"`、`content: "\\00B7"` 和 `Â·` |
| 证据入口 | `openspec/changes/update-requirement-center-card-document-actions-ai-chat/evidence/20260903-progress-gap-no-special-separator/01-acceptance-progress-gap-1440.png`；`02-test-progress-tasks-drawer-1440.png`；`03-manual-progress-tasks-drawer-1440.png`；`computed-progress-gap-no-special-separator-1440.json` |

- 测试：`corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 57 tests pass；`corepack pnpm@11.2.2 --dir src/web build` pass。
- Mock/API 边界：默认真实 API 数据不受影响；本次只修正前端 CSS 视觉分隔方式和显式 demo 视觉证据，不改后端接口、数据库或真实治理文档读取。
- product_data_collection_observability：N/A。本次只调整前端展示样式，不新增 API 字段、请求封装、行为埋点、日志审计、Task Trace、数据库或保留周期。
- REQ 子文档一致性扫尾检查：已同步 `requirement.md` 与 `acceptance.md`；`business-flow.md`、`user-stories.md` 无需更新，原因：本次只修正卡片进度区视觉分隔符，不改变业务流程、角色目标、状态流转、验收门禁或用户故事主路径；`prototype/**` 未更新，原因：用户截图为当前验收反馈事实源，原型结构未变。
