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
