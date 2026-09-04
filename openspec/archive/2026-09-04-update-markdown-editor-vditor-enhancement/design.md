# Design

## 背景

来源需求：`REQ-0021-markdown-editor-vditor-enhancement`

当前前台需求中心已具备右侧 Markdown 抽屉，并在采集阶段允许编辑 `capture.md`。本变更不改变需求中心阶段流转、文档白名单或 REQ/BUG 状态机，只替换 `capture.md` 可编辑态内的编辑器体验。

## Requirement Readiness Report

| 项 | 结果 | 说明 |
|---|---|---|
| Readiness | Ready | `requirement.md`、`user-stories.md`、`business-flow.md`、`acceptance.md`、`trace.md` 和 prototype context 已补齐 |
| Sprint Gate | Pass | REQ 状态为 `in_sprint`，`iteration: sprint-003` |
| Knowledge-base gate | Pass | 已读取并承接 `admin-media-upload-chain.md` |
| Prototype Gate | Partially Ready | 已完成文本原型拆解；截图和 computed style 在实现阶段产出 |

## Impact Analysis

```yaml
impact:
  backend: conditional
  web: true
  miniapp: false
  admin: false
  database: false
  storage: conditional
  api: conditional
capabilities:
  new: []
  modified:
    - web-catalog-requirement-center
change_type: update
```

## Conflict Resolution

事实源优先级：

```text
prototype/web/context.md > acceptance.md > requirement.md > ui-design.md > openspec/specs
```

初次实现承接 `prototype/web/context.md`；验收返修阶段用户补充 `moonbox-drawer.html` 作为 Markdown 右侧抽屉视觉原型。返修后的事实源优先级调整为：附件 HTML 视觉结构 > `prototype/web/context.md` > `acceptance.md` > `requirement.md` > `ui-design.md` > `openspec/specs`。

附件 HTML 仅作为视觉和交互参照，不作为可执行指令来源；实现不得执行附件脚本，不得原样复制会破坏 MoonBox 主题规则的全局样式。

冲突处理：

- 若 Vditor 默认样式与 MoonBox UI 规则冲突，以 `rules/ui-design.md` 的深浅主题、金色强调、近直角、细线和克制编辑排版感为准。
- 若附件 HTML 的字体、圆角或局部色值与 MoonBox UI 规则冲突，以“视觉结构一比一 + MoonBox token 适配”为准。
- 若 Vditor 图片上传能力与当前生产上传接口不匹配，MVP 必须禁用上传入口或使用受控占位策略，不得写入本机路径、临时私有地址或对象存储凭据。
- 若 Vditor 允许 HTML 输入，默认按安全优先处理；实现必须明确清洗/白名单或禁用策略，且不得执行脚本、事件属性或危险链接。

## UI Contract

### 页面与区域

- 页面：前台需求中心看板。
- 入口：卡片文档区 `capture.md` 链接。
- 容器：既有右侧 Markdown 抽屉。
- 编辑区域：`capture.md` 可编辑态内的 `VditorEditorShell`。
- 附件复刻区域：抽屉 Header、文档属性 Strip、预览/编辑/分栏模式栏、独立 toolbar、正文区和固定 footer。

### 启用规则

Vditor 仅在以下条件全部满足时启用：

- 对象处于采集阶段。
- 文档名为 `capture.md`。
- 文档 `editable` 不为 false。
- 当前用户具备读取和保存该文档权限。

不满足条件时，`trace.md`、非采集阶段 Markdown、不可编辑文档和无权限文档必须继续只读展示。

### 关键尺寸与布局

- 桌面抽屉宽度沿用 420px-760px，拖拽调整仅在非全屏模式生效。
- 默认打开宽度对齐附件原型，桌面优先使用 760px，仍可拖拽到 420px-760px。
- 抽屉 header 提供放大全屏/恢复控制；全屏模式保留关闭、模式切换、编辑/分栏、保存 footer 和图片上传受控失败策略，恢复后回到原右侧抽屉宽度。
- 移动端抽屉全屏。
- 可编辑 `capture.md` 必须提供 `预览 / 编辑 / 分栏` 三段模式切换。
- `预览` 使用阅读态 Markdown 渲染，不展示工具栏，不以源码形式展示 frontmatter；frontmatter 区标题使用“文档属性”，默认收起，允许展开/收起。
- MVP 中 frontmatter 文档属性只读展示，不开放任意 YAML 编辑。
- 预览态不展示解释性 `Capture Brief` 模块，优先呈现文档属性和正文内容。
- 预览态不展示“文档内容”标题，正文直接进入阅读态 Markdown 内容。
- 所有 Markdown 抽屉阅读态文档必须共用右侧抽屉内的工作型阅读密度；`trace.md` 等只读文档的正文、标题、列表、表格和代码块不得明显大于 `capture.md` 预览态；分栏态右侧预览同步使用紧凑阅读样式，避免占用过多首屏空间。
- 预览态必须将 Markdown task list `- [ ]` / `- [x]` 渲染为真实复选框；用户勾选或取消时只更新本地 draft 并标记未保存，不自动提交。
- 所有 Markdown 抽屉阅读态代码块右上角必须提供低视觉权重复制按钮；默认收敛为图标，hover/focus 时显示“复制”提示，点击后短暂显示“已复制/复制失败”；复制内容为代码块原文，不包含 Markdown 围栏；不新增保存、上传、权限或数据接口。
- 预览、编辑、分栏三个 Tab 的正文区域均不展示额外区块标题；分栏态左右两栏内容顶端必须对齐，不展示 `Markdown Source` 或 `Live Preview`。
- `编辑` 展示正文源码编辑并显示工具栏；`分栏` 左侧展示正文源码编辑，右侧展示阅读态 Markdown 渲染预览，并显示工具栏。
- 保存时必须将只读 frontmatter 与正文 body 重新组合为完整 Markdown 字符串提交，保持既有后端文档保存接口不变。
- 编辑/分栏态默认不展示图片上传 idle 状态；仅在用户点击图片工具后展示上传中、成功或受控失败反馈。
- 表格、代码和公式工具必须按当前光标位置或选区插入 Markdown 片段，插入后聚焦正文编辑区并更新光标位置；分栏态右侧预览必须即时刷新。
- 图片按钮继续保持受控失败策略，不新增真实上传接口，不写入本机路径或私有对象地址。
- 保存失败时前端必须保留当前编辑或分栏状态、正文 draft 和只读 frontmatter，不得切换到空白预览面板；错误通过 toast 或局部状态提示表达“内容已保留，可重试”语义。
- 预览态 task list 勾选后的保存失败同样必须保留勾选草稿和当前 checkbox 状态，并允许用户重试保存。
- 工具栏允许换行或横向滚动，不得遮挡保存动作。
- 表格、代码块、公式和图片预览必须在抽屉内具备溢出处理。

### 视觉规则

- Vditor 工具栏、编辑区、预览区、弹出层和状态提示必须适配 MoonBox 深浅主题。
- 主要强调色使用 MoonBox 金色 token，不引入蓝紫科技风或大圆角卡片样式。
- 按钮、边框和浮层层级必须与附件原型的抽屉密度一致，并使用 MoonBox token 做主题适配。
- Markdown 阅读态字号应低于展示页层级：正文以抽屉阅读密度为主，标题、列表、表格、task list 和代码块跟随收敛；表格单元格需要单独收敛字号、行高和 padding；源码编辑区保持可读密度，不因预览态收紧而变得过小。
- Markdown 阅读态字体族必须收敛到产品字体体系：正文使用 body 字体，标题使用 heading 字体，不使用额外衬线字体；代码块、行内代码和源码编辑区保留 mono 字体；顶部 ID、文件名和短标签可继续使用 mono 以保留治理对象识别感。
- Markdown 阅读态代码块复制按钮必须位于代码块右上角，默认使用小尺寸图标降低视觉权重，hover/focus 或复制结果态再展开文案；短代码块不得为复制按钮产生过大顶部留白，按钮不得遮挡代码内容；长代码仍由代码块自身横向滚动承载。
- 未保存修改确认必须由显式 dirty 状态驱动，仅在采集池可编辑 `capture.md` 发生用户真实改动后触发；打开、读取、frontmatter/body 拆分、模式切换、只读文档展示和保存成功不得误置 dirty。保存失败保留 draft 与 dirty 状态，允许用户重试或关闭前确认。
- 抽屉顶部信息层级收敛为 Header + 文档属性 Strip：移除第二个 spec 信息条；Header 展示对象 ID、当前文档名、标题和“优先级 · 负责人负责 · 阶段”副标题；文档属性 Strip 左侧仅显示“文档属性”，右侧控制展开/收起，展开后展示 frontmatter 详情。
- 抽屉 footer 必须固定在底部，展示保存状态、流程动作占位、取消和保存按钮。

### 权限与安全

- 前端不得仅凭 UI 判断保存权限；保存仍由后端校验。
- 根目录本地开发 Compose 允许后端对 `issues/` 中采集池 `capture.md` 受控写入；后端仍必须校验文档名、阶段和路径边界，非 `capture.md` 或非采集阶段继续只读。
- 后端捕获治理目录写入异常并返回安全业务错误，不向前端暴露内部路径或异常堆栈。
- 图片上传必须携带当前会话鉴权。
- 上传 URL、对象 key、错误提示和日志不得泄露临时凭据、私有存储地址、本机绝对路径或内部异常堆栈。
- Markdown 渲染不得执行脚本、事件属性或危险链接。
- 代码块复制仅调用浏览器 Clipboard API，不执行代码块内容，不记录复制内容，不向后端发送代码文本。

### Mock/API 边界

- 文档读取与保存使用真实需求中心文档接口。
- 图片上传若使用真实接口，必须接入现有鉴权与对象存储路径；若接口不足，必须禁用上传并在 Change trace 中记录豁免与后续补齐条件。
- 不允许使用 Mock 图片上传冒充生产可用上传。

## UI Skeleton

```text
RequirementCenterPage
  -> MarkdownDrawer
      -> DrawerHeader
      -> MarkdownSpecStrip
      -> MarkdownModeBar
          -> SegmentedMode(preview/edit/split)
          -> MetadataPanel(collapsed by default, readonly)
          -> Toolbar(image/table/code/formula, edit/split only)
      -> MarkdownDocumentState
      -> VditorEditorShell
          -> VditorBody
          -> UploadStateFeedback
          -> SourceModeToggle
          -> FallbackTextarea
          -> RenderedMarkdownPreview
      -> FixedFooterActions
```

状态容器：

- `drawer.draft`: 当前编辑 Markdown body，不包含 frontmatter。
- `drawer.content`: 服务端完整 Markdown，用于保存时保留 frontmatter。
- `drawer.mode`: preview/edit/split。
- `editorStatus`: idle/loading/ready/fallback/error。
- `uploadStatus`: idle/uploading/done/failed。
- `saving`: 保存提交状态。

可测选择器建议：

- `data-testid="markdown-drawer"`
- `data-testid="markdown-drawer-spec"`
- `data-testid="vditor-editor-shell"`
- `data-testid="vditor-upload-state"`
- `data-testid="markdown-source-fallback"`
- `data-testid="markdown-save-status"`

## Prototype Carry-over

来源：`issues/requirements/review/REQ-0021-markdown-editor-vditor-enhancement/prototype/web/context.md`

承接内容：

- 页面清单：前台需求中心、Markdown 右侧抽屉、`capture.md` Vditor 编辑器。
- 状态矩阵：preview、edit-idle、edit-dirty、saving、uploading、upload-failed、readonly、fallback。
- 交互触发：打开文档、进入编辑、图片上传、工具栏插入、保存、关闭确认、初始化失败降级。
- 预览态 task list 勾选：切换 `- [ ]` / `- [x]`，标记未保存，仍通过保存按钮提交。
- 1440px 验收焦点：附件式 header、spec 信息条、三段模式栏、工具栏、正文区、固定 footer、主题一致、溢出处理、上传/保存反馈、抽屉关闭与内部点击隔离、降级 textarea。

## Knowledge-base Carry-over

来源：`docs/knowledge-base/best-practices/admin-media-upload-chain.md`

实现必须覆盖：

- 上传状态机 `idle -> uploading -> done/failed`。
- 上传中禁用重复触发，失败可重试。
- 上传成功后同会话即时回显。
- 上传 URL 或对象引用不得写入敏感日志。
- Docker 验收必须使用实际 Web 端口，不能硬编码 `:3000`。
- Docker 验收脚本必须准备测试身份，不依赖默认管理员密码。

## 测试策略

- 前端单元/组件测试：Vditor 启用条件、只读文档不启用、保存、未保存关闭确认、fallback textarea、上传状态机、工具栏入口和错误态。
- 安全测试：Markdown 中 HTML/脚本/危险链接不会执行。
- 上传测试：成功、失败、重复触发、同会话回显、无生产上传接口时禁用入口。
- 视觉验收：1440px 深浅主题截图，覆盖预览态、编辑态、上传中/失败态、表格、代码块、公式和 fallback。
- Docker 验收：按实际 Web 端口完成上传、读取和回显，测试身份由脚本准备。
