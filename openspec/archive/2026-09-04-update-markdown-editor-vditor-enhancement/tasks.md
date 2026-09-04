# Tasks

## 1. UI Skeleton 与依赖接入

- [x] 1.1 确认 Vditor 包接入方式、样式加载方式、bundle 影响和降级策略。
- [x] 1.2 在 Markdown 抽屉内建立 `VditorEditorShell` UI Skeleton，包含工具栏、编辑区、上传状态、源码/降级区和保存动作。
- [x] 1.3 完成 1440px UI Skeleton 首轮截图或等价视觉证据，确认抽屉宽度、工具栏密度和保存动作不冲突。

## 2. capture.md 编辑能力

- [x] 2.1 仅在采集阶段、文档名 `capture.md`、可编辑且有权限时启用 Vditor。
- [x] 2.2 保持 `trace.md`、非采集阶段 Markdown、不可编辑文档和无权限文档只读。
- [x] 2.3 保持保存内容为 Markdown 字符串，并提供源码查看或编辑能力。
- [x] 2.4 继承未保存关闭确认、保存 Loading、保存成功回显和保存失败提示。

## 3. 图片上传与安全

- [x] 3.1 接入项目认可的上传接口或明确禁用上传入口；禁止写入本机路径、临时私有地址和对象存储凭据。
- [x] 3.2 实现 `idle -> uploading -> done/failed` 上传状态机。
- [x] 3.3 覆盖上传失败保留内容和重复触发重试；当前无认可文档图片上传接口，成功同会话回显不适用。
- [x] 3.4 明确 Markdown HTML 清洗、白名单或禁用策略，防止脚本、事件属性和危险链接执行。

## 4. 表格、代码和公式

- [x] 4.1 支持表格插入、编辑和 Markdown 表格保存。
- [x] 4.2 支持代码块编辑与源码预览，并处理长行溢出。
- [x] 4.3 支持数学公式输入与源码预览，渲染失败时保留原始 Markdown/LaTeX。

## 5. 主题、响应式与视觉验收

- [x] 5.1 适配 MoonBox 深浅主题、金色强调、近直角和细线视觉规则。
- [x] 5.2 覆盖桌面 420px-760px 抽屉和移动端全屏抽屉。
- [x] 5.3 产出 1440px 视觉截图，覆盖编辑态、上传失败、表格、代码块、公式和 fallback textarea；上传中/成功因无认可接口不适用。
- [x] 5.4 产出 computed style 或等价证据，覆盖抽屉宽度、工具栏、编辑区、内容溢出和横向滚动。

## 6. 测试与同步

- [x] 6.1 补充前端组件测试，覆盖启用条件、只读保护、保存、脏状态、fallback、上传状态机和安全渲染。
- [x] 6.2 若接入真实上传接口，补充后端/API 或集成测试，覆盖上传、读取、回显和权限。
- [x] 6.3 补充 Docker 本地上传读取回显验收，使用实际 Web 端口和脚本化测试身份。
- [x] 6.4 同步必要 API、对象存储、部署或测试文档；不适用项在 trace 中说明。
- [x] 6.5 更新 Change trace 与 linked REQ 验收证据，确认 Mock/API 边界和 REQ 最终一致性。

## 验收返修记录

### 2026-08-27 08:40:00 · 附件 HTML 抽屉一比一复刻

验收反馈：Markdown 右侧抽屉需要参照附件 `moonbox-drawer.html` 一比一复刻。范围限定为 `capture.md` Markdown 抽屉 UI：header、spec 信息条、预览/编辑/分栏模式切换、toolbar、正文排版和固定 footer。保持现有权限边界和图片上传受控失败策略，不新增真实上传接口。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| `moonbox-drawer.html` | `/requirements`，1440px，深色主题，`capture.md` 抽屉预览态 | 附件 HTML 原型 vs 当前实现 | 抽屉默认 760px，header 含 REQ/文档面包屑、标题、副标题，主体有 spec 信息条 | 旧实现仅标题 + 模式说明，默认 520px，无 spec 信息条 | 宽度、header 层级、元信息区缺失 | 附件 HTML 结构/CSS 片段、Playwright 截图 | 本次修复 | `evidence/20260819-vditor-editor-visual/03-drawer-prototype-preview-1440.png` |
| `moonbox-drawer.html` | `/requirements`，1440px，编辑态 | 附件 HTML 原型 vs 当前实现 | 模式切换与 toolbar 独立位于正文上方，正文 textarea 使用原型式标签和密度 | 旧实现 toolbar 嵌在编辑器壳内，无模式切换 | segmented、toolbar 位置、编辑区密度 | Testing Library + Playwright 截图 | 本次修复 | `evidence/20260819-vditor-editor-visual/04-drawer-prototype-edit-1440.png` |
| `moonbox-drawer.html` | `/requirements`，1440px，分栏态 | 附件 HTML 原型 vs 当前实现 | 预览 / 编辑 / 分栏三段切换，分栏态左右两栏并列且不撑破抽屉 | 旧实现只有预览/编辑两态 | 缺少分栏、预览面板结构 | Testing Library + computed style | 本次修复 | `evidence/20260819-vditor-editor-visual/05-drawer-prototype-split-1440.png`、`computed-vditor-editor-1440.json` |
| `moonbox-drawer.html` | `/requirements`，1440px，上传失败态 | 附件 HTML 原型 vs 当前实现 | 保留受控失败反馈，底部 footer 不被遮挡 | 旧实现上传反馈存在但 footer 非附件式固定栏 | 状态反馈与 footer 层级 | Playwright 截图、computed style | 本次修复；真实上传接口仍为非目标 | `evidence/20260819-vditor-editor-visual/06-drawer-prototype-upload-failed-1440.png` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐附件 HTML 作为返修参照和预览/编辑/分栏模式。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：用户流程、角色目标和权限/上传边界未变化；本次只调整同一流程内的抽屉视觉结构和模式呈现。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：保持图片上传受控失败策略，不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-08-27 08:53:11 · 预览态阅读化返修

验收反馈：`capture.md` 预览态仍像编辑形态。预览必须改为阅读态 Markdown 渲染，隐藏或解析 frontmatter，不在预览态展示工具栏；toolbar 仅在编辑/分栏态显示，分栏态左源码右渲染预览；图片上传继续受控失败，不新增真实上传接口。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-9b1ed276-ff5e-4133-9aa0-cabd64236204.png` | `/requirements`，深色主题，`capture.md` 抽屉预览态 | 阅读态渲染 Markdown；frontmatter 隐藏或解析；不展示工具栏 | 预览 tab 已选中，但正文仍显示 `---` frontmatter 与 Markdown 源码，右侧仍有图片/表格/代码/公式工具栏 | 预览态视觉语义像编辑态 | 截图人工对照 + `MarkdownPreviewPane` 代码路径检查 | 本次修复：预览使用 `RenderedMarkdown`，frontmatter 解析为摘要，toolbar 仅 edit/split | `evidence/20260819-vditor-editor-visual/03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 用户截图 `codex-clipboard-9b1ed276-ff5e-4133-9aa0-cabd64236204.png` | `/requirements`，分栏态目标 | 左侧源码编辑，右侧阅读态渲染预览，工具栏可用 | 原实现预览 pane 复用源码 `<pre>`，分栏右侧仍偏源码 | 分栏右侧未体现渲染预览 | Testing Library + Playwright 截图 | 本次修复：分栏右侧复用阅读态 Markdown 渲染组件 | `evidence/20260819-vditor-editor-visual/05-drawer-prototype-split-1440.png` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐预览态阅读化、toolbar 展示边界和分栏左右语义。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐实现契约、验收证据和 OpenSpec 行为约束。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：用户流程和角色目标未变化；本次仅修正同一抽屉内不同模式的呈现语义。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：保持图片上传受控失败策略，不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-08-27 09:05:08 · frontmatter 元数据折叠与正文分离返修

验收反馈：元数据默认应收起，并允许展开/收起；编辑/分栏态应将 frontmatter 元数据与正文区分开。MVP 中元数据先只读展示，不开放任意 YAML 编辑；保存时仍保持 frontmatter + body 组合为 Markdown 字符串提交。范围仍限定 `capture.md`，不新增真实上传接口，图片上传受控失败策略不变。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文本反馈 + frontmatter 示例 | `/requirements`，`capture.md` 抽屉预览态 | 当前实现 | 元数据默认收起，可展开/收起查看 | 元数据摘要默认展开，占用正文上方空间 | 信息层级过重，阅读态仍被治理字段打断 | Testing Library + Playwright computed | 本次修复：元数据默认收起，展开后只读键值展示 | `evidence/20260819-vditor-editor-visual/03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 用户文本反馈 + frontmatter 示例 | `/requirements`，`capture.md` 编辑/分栏态 | 当前实现 | frontmatter 元数据与正文编辑区分离；正文编辑区只编辑 body | textarea 仍可能承载完整 Markdown，frontmatter 与正文混在一起 | 误编辑治理字段、误删 YAML 分隔符风险 | Testing Library 保存断言 + Playwright computed | 本次修复：编辑器只编辑 body，保存时重组完整 Markdown；元数据 MVP 只读 | `computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐元数据默认收起、只读展示、正文编辑区分离和保存重组规则。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 行为约束与验证证据。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：后端仍接收完整 Markdown 字符串；不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-08-27 09:27:51 · 抽屉文案、独立折叠与按需上传状态返修

验收反馈：顶部 spec 信息条右侧不再显示“元信息/元数据”，改为独立“展开/收起”控制且只控制 spec 详情；正文 frontmatter 标题改为“文档属性”，折叠区保持独立展开/收起，不与顶部联动；移除预览态 `Capture Brief` 提示模块；编辑/分栏态默认不展示“图片上传：待选择”，仅在用户点击图片按钮后展示上传状态或受控失败提示。范围仍限定 `capture.md`，不新增真实上传接口，图片上传受控失败策略不变。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-19915457-f690-4a48-93ae-d80d28a59023.png` | `/requirements`，深色主题，`capture.md` 预览态 | 当前实现 | 顶部 spec 右侧只显示“展开/收起”，只控制 spec 详情 | 顶部显示“元信息”，并与正文元数据折叠联动 | 文案难懂、层级混淆、状态联动错误 | Testing Library + Playwright computed | 本次修复：新增独立 spec 折叠状态，顶部仅显示“展开/收起” | `computed-vditor-editor-1440.json` |
| 用户截图 `codex-clipboard-19915457-f690-4a48-93ae-d80d28a59023.png` | `/requirements`，深色主题，`capture.md` 预览态 | 当前实现 | 正文 frontmatter 标题为“文档属性”，独立展开/收起 | 正文显示“元数据”，语义偏工程化 | 文案理解成本高 | Testing Library + Playwright computed | 本次修复：标题改为“文档属性” | `03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 用户截图 `codex-clipboard-19915457-f690-4a48-93ae-d80d28a59023.png` | `/requirements`，深色主题，预览正文顶部 | 当前实现 | 直接呈现文档属性和文档内容 | `Capture Brief` 占据首屏并解释安全策略 | 系统说明过多，干扰阅读 | Playwright 截图 + DOM 文案检查 | 本次修复：移除 `Capture Brief` 模块 | `03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 用户截图反馈 | `/requirements`，编辑/分栏态 | 当前实现 | 未触发图片入口前不显示上传状态；点击图片后才显示受控失败 | 默认展示“图片上传：待选择” | idle 状态噪音 | Testing Library + Playwright computed | 本次修复：idle 不渲染，点击图片后显示受控失败 | `06-drawer-prototype-upload-failed-1440.png`、`computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐“文档属性”、独立折叠、移除 `Capture Brief` 和上传状态按需展示规则。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 行为约束与验证证据。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：仅调整 `capture.md` 抽屉呈现与交互噪音；不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-08-27 09:43:44 · spec 默认收起、去标题与全屏返修

验收反馈：顶部 spec 信息条默认收起，仅显示展开/收起控制且只控制 spec 详情；预览态移除“文档内容”标题，正文直接进入 Markdown 阅读内容；右侧抽屉 header 增加放大全屏/恢复功能。全屏模式保留关闭、模式切换、编辑/分栏、保存 footer 和图片上传受控失败策略，拖拽宽度仅在非全屏模式生效。范围仍限定 `capture.md`，不新增真实上传接口。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文本验收反馈 | `/requirements`，深色主题，`capture.md` 预览态 | 当前实现 | 顶部 spec 默认收起，仅显示展开控制 | 顶部 spec 可展开/收起，但打开文档时仍默认展开 | 首屏信息密度偏高 | Testing Library + Playwright computed | 本次修复：打开 `capture.md` 时 spec 详情默认收起 | `computed-vditor-editor-1440.json` |
| 用户文本验收反馈 | `/requirements`，深色主题，`capture.md` 预览正文 | 当前实现 | 预览正文直接进入 Markdown 阅读内容 | 预览态在正文前显示“文档内容”标题 | 标题冗余，打断阅读 | Testing Library DOM 文案检查 + Playwright computed | 本次修复：移除“文档内容”标题 | `03-drawer-prototype-preview-1440.png`、`computed-vditor-editor-1440.json` |
| 用户文本验收反馈 | `/requirements`，桌面端右侧抽屉 | 当前实现 | header 支持放大全屏/恢复；全屏保留关闭、模式切换、编辑/分栏、保存 footer | 无全屏/恢复控制，只能拖拽到 760px | 大屏阅读/编辑空间不足 | Testing Library + Playwright computed | 本次修复：新增全屏/恢复按钮并保留核心操作 | `computed-vditor-editor-1440.json` |
| 用户文本验收反馈 | `/requirements`，全屏态 | 当前实现 | 拖拽宽度仅非全屏生效 | 全屏能力缺失，拖拽边界无法区分 | 全屏与抽屉宽度状态不清晰 | Testing Library class/style 断言 + Playwright computed | 本次修复：全屏态隐藏 resizer，恢复后回到 760px 非全屏宽度 | `computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐 spec 默认收起、预览态去“文档内容”标题、抽屉全屏/恢复和非全屏拖拽边界。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 行为约束与验证证据。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：仅调整 `capture.md` 抽屉 UI 与交互状态；不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-08-27 10:32:19 · 正文区块标题移除与分栏顶端对齐返修

验收反馈：分栏 Tab 下左右两边 `Markdown Source` 与 `Live Preview` 不一样高，且这两块文本信息可以不需要；如采用移除方案，其他 Tab 也一并调整。用户确认采用“全部移除正文区块标题”的方案。范围仍限定 `capture.md` 抽屉 UI，不新增真实上传接口。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-e0c29328-6b18-427c-870b-c73f36c21653.png` | `/requirements`，深色主题，`capture.md` 分栏态 | 当前实现 | 左侧正文源码与右侧阅读预览顶端对齐；不需要额外英文标题 | 左侧显示 `MARKDOWN SOURCE`，右侧显示 `LIVE PREVIEW`，两个标题与内容起点不一致 | 分栏左右内容顶端不齐；英文标题信息噪音 | 截图人工对照 + Testing Library DOM 文案检查 + Playwright computed | 本次修复：移除 `Markdown Source` 与 `Live Preview`，分栏左右 pane 顶端对齐 | `05-drawer-prototype-split-1440.png`、`computed-vditor-editor-1440.json` |
| 用户截图反馈 | `/requirements`，`capture.md` 预览/编辑/分栏态 | 当前实现 | 三个 Tab 正文区域均不展示额外区块标题，直接进入阅读内容或编辑内容 | 分栏态存在英文 pane 标题；编辑态也存在源码标题 | 正文区域层级不统一 | Testing Library 覆盖三种 Tab 文案不存在 | 本次修复：三个 Tab 正文区统一无额外标题 | `computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐正文区块标题移除、分栏左右顶端对齐和三种 Tab 正文区域一致性。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 行为约束与验证证据。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：仅调整 `capture.md` 抽屉正文区视觉层级；不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-08-28 09:15:42 · 编辑工具栏光标插入与分栏预览返修

验收反馈：Markdown 编辑状态下图片上传、表格、代码、公式功能还不能使用。用户确认返修范围：图片按钮继续保持受控失败且不新增真实上传接口；表格、代码、公式按钮改为按当前光标位置或选区插入 Markdown 片段，插入后聚焦编辑区、更新光标位置，并在分栏态即时刷新右侧预览；补充测试覆盖光标插入、选区包裹或插入反馈。范围仍限定 `capture.md` 抽屉 UI。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文本验收反馈 | `/requirements`，`capture.md` 编辑态 | 当前实现 | 表格、代码、公式按钮按光标或选区插入内容，插入后可继续编辑 | 按钮只将 Markdown snippet 追加到正文末尾，长文中用户难以感知插入结果 | 工具栏可用性弱，光标语义缺失 | 代码路径检查 + Testing Library 光标插入断言 | 本次修复：按 textarea selection 插入，并在下一帧恢复焦点和光标 | `src/web/src/requirement-center.test.tsx`、`computed-vditor-editor-1440.json` |
| 用户文本验收反馈 | `/requirements`，`capture.md` 分栏态 | 当前实现 | 工具插入后右侧阅读态预览即时刷新 | 旧逻辑追加到末尾，当前视口不一定体现预览变化 | 分栏预览反馈不明确 | Testing Library 预览 DOM 断言 + Playwright computed | 本次修复：分栏态插入后右侧预览随 draft 更新 | `05-drawer-prototype-split-1440.png`、`computed-vditor-editor-1440.json` |
| 用户文本验收反馈 | `/requirements`，`capture.md` 编辑/分栏态图片按钮 | 当前实现 | 图片按钮继续保持受控失败，不新增真实上传接口，不写入本机路径或私有对象地址 | 当前策略已是受控失败 | 无需扩展上传边界 | Testing Library 上传失败文案断言 + Playwright 截图 | 保持既有策略 | `06-drawer-prototype-upload-failed-1440.png`、`computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐编辑工具栏光标插入、选区包裹、焦点恢复、分栏预览即时刷新和图片上传受控失败边界。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 行为约束与验证证据。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：图片上传仍为受控失败，不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-08-28 09:40:00 · capture.md 保存失败与空面板返修

验收反馈：表格、代码、公式已按光标插入后，点击保存显示“文档保存失败”；即使真实保存失败，也不应进入空面板，应通过 toast、tooltip 或局部提示告知，并保留用户正在编辑的内容。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-bac87f13-fc42-4022-8c2b-c59f16a0ee31.png` | `/requirements`，深色主题，`capture.md` 编辑态，保存失败 | 当前实现 + Network | 保存失败时保留编辑/分栏态和 draft，并在保存按钮附近或 toast 显示可理解错误 | 面板正文只显示“文档保存失败”，Network 显示 `PUT capture.md` 返回 500 | 错误态替代了编辑内容，用户难以继续修改或重试 | 截图对照 + Network 状态 + 后端日志 | 本次修复：失败时不切预览、不清空 draft，显示“内容已保留”语义提示 | `src/web/src/requirement-center.test.tsx` |
| 后端日志证据 | Docker 本地后端，`PUT /api/v1/requirement-center/issues/.../documents/capture.md` | 当前 compose 挂载 | 本地开发环境应允许采集池 `capture.md` 受控保存 | `target.write_text` 抛出 `OSError: [Errno 30] Read-only file system` | `issues/` 被只读挂载，后端无法写入 | 容器日志 + `docker-compose.yml` 配置检查 | 本次修复：根目录本地开发 Compose 将 `issues/` 调整为可写；后端仍限制仅采集阶段 `capture.md` 可写 | `docker-compose.yml`、`tests/integration/api/test_requirement_center.py` |

#### 根因证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | network_request | 用户截图 | `PUT capture.md` 返回 `500 Internal Server Error` | 证明保存失败来自后端接口而非编辑器插入逻辑 |
| E2 | runtime_log | 后端容器日志 | `OSError: [Errno 30] Read-only file system`，触发点为 `target.write_text` | 证明 500 根因为本地开发治理目录只读挂载 |
| E3 | config_diff | `docker-compose.yml` | `./issues:/app/governance/issues:ro` | 证明后端容器内 `issues/` 无写入权限 |

#### REQ 子文档一致性扫尾检查

- 已更新：Change `trace.md`、`specs/web-catalog-requirement-center/spec.md`、`docs/02-deployment.md`，补齐保存失败、只读文件系统、受控写入和失败态保留草稿规则。
- 需由 Workflow Sync 同步：linked REQ `trace.md`、Sprint 验收状态。
- 无需更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，原因：既有验收已要求保存失败提示、异常时不丢失用户输入和 Docker 本地验收；本次是实现与环境返修，不改变用户故事或原型布局。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：用户流程、角色目标、权限路径和状态流转不变。
- 无需更新 API / DB / 对象存储文档，原因：未新增接口、数据库字段或真实上传链路；仅后端将写入异常安全化并调整本地开发 Compose 挂载。

### 2026-08-28 18:30:00 · 预览态 task list 复选框交互返修

验收反馈：`capture.md` 预览态中 Markdown 任务列表 `- [ ]` / `- [x]` 应展示为真实复选框，并允许用户快速勾选或取消；勾选后只更新当前 draft/content 并标记未保存，仍需点击保存才写回；编辑/分栏态继续展示标准 Markdown 源码；保存失败时保留勾选后的草稿状态并提示可重试；范围仅限采集池 `capture.md`，不扩大其他 Markdown 文档编辑权限。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-335cd0ab-169f-403e-bec4-3e5fb1e3bbc0.png` | `/requirements`，深色主题，`capture.md` 预览态 task list | 当前实现 | `- [ ]` / `- [x]` 渲染为真实 checkbox，可快速勾选/取消；勾选后进入未保存状态 | 预览态以普通 Markdown 文本或列表展示 `[ ]`，无法直接勾选 | task list 预览不可交互，用户需要切到编辑态手改源码 | 截图对照 + Testing Library checkbox/save 断言 | 本次修复：预览态 task list 支持复选框切换，保存失败保留草稿 | `src/web/src/requirement-center.test.tsx` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`、`trace.md`，补齐预览态 task list 真实复选框、勾选后未保存、保存按钮写回和失败保留草稿规则。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 行为约束与验证证据。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只增强同一 `capture.md` 预览态的局部 Markdown task list 交互。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：勾选只修改前端草稿，仍通过既有 `capture.md` Markdown 保存接口写回；不新增真实上传接口、数据库字段、部署变量或对象存储写入链路。

### 2026-09-01 00:00:00 · Markdown 阅读态字体密度返修

验收反馈：用户截图显示 `capture.md` Markdown 文档内容字体感觉偏大。返修范围限定为 `capture.md` 抽屉 UI：预览态正文、标题、表格和 task list 字号整体收敛一档，保持工作型抽屉阅读密度；编辑/分栏态源码编辑区维持可读密度，分栏右侧预览同步使用紧凑阅读样式。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-1b97f230-c0be-4779-ae9d-950ecdf61b1e.png` | `/requirements`，深色主题，`capture.md` 预览态，右侧抽屉 760px | 当前实现 | Markdown 正文和标题适合工作型抽屉阅读，首屏能容纳更多正文、表格和 task list 内容 | 预览态正文 `14px/1.85`、一级标题 `24px`、二级标题 `18px`，在 760px 抽屉内偏展示稿 | 字号层级、行距、列表/表格间距偏大 | 截图对照 + CSS 契约测试 + Playwright computed style | 本次修复：正文收敛到 `13px/1.72`，标题收敛为 `20px/16px/14px`，分栏右侧 compact 为 `12.5px/1.68` | `computed-vditor-editor-1440.json`、`src/web/src/requirement-center.test.tsx` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，补齐 Markdown 阅读态字体密度、分栏右侧紧凑阅读样式和验收焦点。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 字体密度约束、实现证据和验证记录。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只调整同一 `capture.md` 抽屉的阅读密度。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：仅调整 CSS 和视觉密度；不新增接口、数据库字段、部署变量、对象存储写入链路或真实图片上传能力。

### 2026-09-01 08:30:00 · 抽屉正文阅读区字体族一致性返修

验收反馈：用户反馈右侧抽屉各部分使用的 `font-family` 不一致。返修范围限定为 `capture.md` 抽屉 UI：Markdown 阅读态标题改用产品 heading 字体，正文显式使用 body 字体，代码块、行内代码和源码编辑区保留 mono；顶部 ID、文件名和短标签可继续使用 mono，正文阅读区不再混用衬线字体。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文字反馈 | `/requirements`，`capture.md` 右侧抽屉预览态与分栏态 | 当前实现 | 正文阅读区字体族统一到产品 UI 字体体系；代码和源码保留 mono；顶部治理 ID 与短标签可保留 mono | Markdown 标题使用 `"Noto Serif SC", serif`，正文未显式声明 body 字体，代码使用系统 mono | 阅读区标题与抽屉 UI 字体体系割裂 | CSS 检查 + 样式契约测试 + Playwright computed style | 本次修复：阅读区正文使用 `var(--rc-font-body)`，标题使用 `var(--rc-font-heading)`，代码使用 `var(--rc-font-mono)` | `computed-vditor-editor-1440.json`、`src/web/src/requirement-center.test.tsx` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，补齐阅读区字体族一致性和代码/source mono 保留规则。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 字体族约束、实现证据和验证记录。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只调整同一 `capture.md` 抽屉的视觉字体体系。
- 无需更新 API / DB / 部署 / 对象存储文档，原因：仅调整 CSS 字体族和视觉一致性；不新增接口、数据库字段、部署变量、对象存储写入链路或真实图片上传能力。

### 2026-09-01 10:23:00 · 抽屉关闭确认返修

验收反馈：用户截图显示当前打开的是 `trace.md`，但关闭时仍出现 `capture.md 有未保存修改` 弹窗；同时打开 `capture.md` 但未编辑时关闭也会误弹窗。返修范围限定为 `capture.md` 抽屉 UI：未保存确认仅限采集池可编辑 `capture.md` 且用户真实改动后触发。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-29585383-c9ee-40ba-a2be-379bb546d628.png` | `/requirements`，深色主题，右侧抽屉打开 `trace.md`，关闭触发浏览器确认弹窗 | 当前实现 | 只读 `trace.md` 关闭时不应出现 `capture.md` 未保存确认 | 弹窗文案为 `capture.md 有未保存修改，确认关闭？` | dirty 判断未限定可编辑 `capture.md`，且文案与当前文档不一致 | 截图对照 + 代码路径检查 + Testing Library 回归测试 | 本次修复：dirty 状态仅由可编辑 `capture.md` 用户真实改动触发；只读文档关闭不提示 | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/requirement-center.test.tsx` |
| 用户文字反馈 | `/requirements`，打开 `capture.md` 但未编辑后关闭 | 当前实现 | 未编辑的 `capture.md` 关闭时不提示未保存 | 关闭时误提示未保存 | 初始化/解析内容不应被视为用户修改 | Testing Library 回归测试 | 本次修复：新增显式 `dirty` 字段，初始化、读取、模式切换和保存成功均保持或恢复 clean | `src/web/src/requirement-center.test.tsx` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，补齐关闭确认触发边界。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound dirty 状态约束、实现证据和验证记录。
- 已更新：Sprint `acceptance-report.md`、`release-note.md`，补齐用户可见关闭确认行为。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只修正同一 `capture.md` 抽屉的关闭保护触发条件。
- 无需更新 API / DB / 部署 / 对象存储 / 安全文档，原因：仅调整前端抽屉 dirty 状态和关闭确认，不新增接口、数据库字段、权限、部署变量、对象存储写入链路或真实图片上传能力。

### 2026-09-01 10:48:00 · 抽屉顶部信息层级返修

验收反馈：用户确认抽屉顶部结构应收敛为 Header 与文档属性 Strip 两层：移除第二个 spec 信息条；Header 保留对象 ID、当前文档名、标题和“P1 · 产品团队负责 · 采集池”副标题；文档属性 Strip 左侧仅显示“文档属性”，右侧保留展开/收起，展开后展示 `REQ_ID`、`STATUS`、`created_at`、`updated_at`、`recorded_by`、`source` 等详情。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-c8058450-9dcd-417f-a6f0-03efc8b33fbe.png` | `/requirements`，深色主题，Markdown 抽屉顶部，`trace.md` 只读态 | 当前实现 | 顶部仅保留 Header 与文档属性 Strip；文档属性承担详情展开 | Header、第二个 spec 信息条、文档属性三层连续出现，信息重复 | 信息层级重复、首屏纵向空间浪费 | 截图对照 + DOM 测试 + Playwright computed | 本次修复：移除第二个 spec 信息条，Header 副标题改为优先级/负责人/阶段，文档属性 Strip 接管详情 | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/requirement-center.test.tsx`、`computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，补齐 Header + 文档属性 Strip 的两层信息架构。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 信息层级约束、实现证据和验证记录。
- 已更新：Sprint `acceptance-report.md`、`release-note.md`，补齐用户可见抽屉信息层级变化。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只调整同一 Markdown 抽屉顶部信息布局。
- 无需更新 API / DB / 部署 / 对象存储 / 安全文档，原因：仅调整前端展示层级和样式，不新增接口、数据库字段、权限、部署变量、对象存储写入链路或真实图片上传能力。

### 2026-09-01 11:12:00 · Markdown 抽屉阅读密度统一返修

验收反馈：用户截图显示不同 Markdown 文档在右侧抽屉中的阅读密度不一致，`trace.md` 等只读文档的标题和表格看起来仍偏大。返修范围限定右侧 Markdown 抽屉阅读态：所有 Markdown 文档预览/只读展示共用抽屉级阅读样式，正文、标题、列表、表格、代码块按工作型抽屉密度收敛；`capture.md` 编辑/分栏源码编辑区保持现状，不改变权限、保存、上传或数据接口。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-1c2f0af0-614c-4478-a858-c59cbb11f121.png` | `/requirements`，深色主题，`REQ-0022 trace.md` 右侧抽屉只读态 | 当前实现 | `trace.md` 与 `capture.md` 预览共用抽屉级 Markdown 阅读密度；表格不应像展示页正文一样厚重 | 标题、列表和表格在 760px 抽屉内视觉偏大，表格单元格 padding 和行高偏重 | 只读文档阅读态密度未充分收敛；表格视觉重量偏高 | 截图对照 + CSS 契约测试 + Playwright computed style | 本次修复：统一 `rc-rendered-markdown` 阅读密度，表格单元格单独收敛到 `12px/1.48` 与 `6px 8px` padding | `07-drawer-trace-readonly-density-1440.png`、`computed-vditor-editor-1440.json` |
| 用户截图 `codex-clipboard-51f842af-feef-4179-a250-063cf8971960.png` | `/requirements`，深色主题，`REQ-0001 trace.md` 右侧抽屉只读态 | 当前实现 | 长表格在抽屉中应更像工作台信息阅读，而不是大字号报告页 | 表格行高、单元格文字和标题层级偏大，首屏密度低 | 跨文档 Markdown 抽屉阅读样式不够一致 | 截图对照 + CSS 契约测试 + Playwright computed style | 本次修复：所有 Markdown 抽屉阅读态共享同一套正文、标题、列表、表格和代码块密度 | `07-drawer-trace-readonly-density-1440.png`、`computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，补齐所有 Markdown 抽屉阅读态统一密度和只读文档表格密度收敛规则。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 统一阅读密度约束、实现证据和验证记录。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只调整右侧 Markdown 抽屉阅读态视觉密度。
- 无需更新 API / DB / 部署 / 对象存储 / 安全文档，原因：仅调整 CSS 阅读密度和视觉证据；不新增接口、数据库字段、部署变量、对象存储写入链路或真实图片上传能力。

### 2026-09-01 12:05:00 · Markdown 阅读态代码块复制返修

验收反馈：用户确认预览状态下代码框支持复制是合理能力，并要求所有 Markdown 阅读态代码块右上角提供复制按钮；点击复制代码块原文且不包含 Markdown 围栏；成功/失败给出轻量提示；按钮不遮挡代码内容并适配抽屉宽度与横向滚动；不影响 `capture.md` 编辑/分栏源码编辑区，不改变权限、保存、上传或数据接口。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户文本验收反馈 | `/requirements`，Markdown 抽屉预览/只读态代码块 | 当前实现 | 代码块右上角提供复制按钮，复制代码原文且不含围栏，成功/失败轻量提示，不遮挡内容 | 代码块只渲染为 `<pre><code>`，用户需要手动选择复制 | 阅读态代码块复制效率不足 | Testing Library 剪贴板断言 + CSS 契约测试 + Playwright computed | 本次修复：`RenderedMarkdown` 为阅读态代码块增加复制按钮和按钮内状态反馈，代码块顶部 padding 预留按钮空间 | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/requirement-center.test.tsx`、`computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，补齐 Markdown 阅读态代码块复制能力、提示和布局约束。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 代码块复制行为、实现证据和验证记录。
- 已更新：Sprint `acceptance-report.md`、`release-note.md`，补齐用户可见 Markdown 阅读态代码块复制能力。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只增强右侧 Markdown 抽屉阅读态代码块复制交互。
- 无需更新 API / DB / 部署 / 对象存储 / 安全文档，原因：复制能力仅调用浏览器 Clipboard API，不新增接口、数据库字段、部署变量、对象存储写入链路、真实图片上传能力或后端权限变化。

### 2026-09-01 12:55:00 · 代码块复制按钮视觉权重返修

验收反馈：用户截图显示刚新增的复制按钮在短代码块上视觉权重偏高，且代码块为了按钮产生过大顶部留白。返修范围限定 Markdown 抽屉阅读态：复制按钮默认收敛为低视觉权重图标，hover/focus 时显示“复制”提示，点击后短暂显示“已复制/复制失败”；短代码块不得因复制按钮产生过大顶部留白，按钮不得遮挡代码内容，长代码横向滚动仍可正常复制。

#### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户截图 `codex-clipboard-1a675aff-a3ea-465a-9fa3-baddeab2f9ba.png` | `/requirements`，深色主题，`capture.md` 预览态短代码块 | 当前实现 | 复制能力可发现但低干扰；默认图标化，交互时展示文案或结果；短代码块保持紧凑 | 右上角常驻“复制”文字按钮，代码块顶部留白明显 | 按钮视觉权重偏高，短代码块阅读密度被破坏 | 截图对照 + CSS 契约测试 + Playwright computed style | 本次修复：默认只显示低透明度图标，hover/focus/结果态展开文案，代码块 padding 收敛为 `10px 44px 9px 10px` | `src/web/src/styles/globals.css`、`src/web/src/requirement-center.test.tsx`、`computed-vditor-editor-1440.json` |

#### REQ 子文档一致性扫尾检查

- 已更新：`requirement.md`、`acceptance.md`、`prototype/web/context.md`，补齐复制按钮默认图标化、hover/focus 展开、短代码块紧凑布局和结果反馈。
- 已更新：Change `design.md`、`specs/web-catalog-requirement-center/spec.md`、`trace.md`，补齐 archive-bound 视觉权重和布局约束。
- 已更新：Sprint `acceptance-report.md`、`release-note.md`，补齐用户可见代码块复制按钮视觉收敛。
- 无需更新：`business-flow.md`、`user-stories.md`，原因：需求治理流程、角色目标、权限路径和状态流转不变；本次只调整右侧 Markdown 抽屉阅读态代码块复制按钮视觉。
- 无需更新 API / DB / 部署 / 对象存储 / 安全文档，原因：仅调整前端按钮样式和交互状态，不新增接口、数据库字段、部署变量、对象存储写入链路、上传能力或后端权限变化。
