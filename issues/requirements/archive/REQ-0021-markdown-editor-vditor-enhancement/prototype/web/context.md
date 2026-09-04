---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
status: pending_review
created_at: 2026-08-19 11:36:10
updated_at: 2026-09-01 12:55:00
owner: product
source: requirement.md
---

# Prototype Context

## 页面清单

- 前台需求中心看板页面。
- Markdown 文档右侧抽屉。
- `capture.md` 可编辑态内的 Vditor 增强编辑器。
- 验收附件 `moonbox-drawer.html` 表达的 Markdown 右侧抽屉视觉结构。

## 关键区域

- 抽屉标题区：对象 ID、文档名、编辑/预览状态、放大全屏/恢复按钮、关闭按钮。
- 文档属性 Strip：默认收起，左侧仅显示“文档属性”，右侧展示展开/收起；展开后显示 frontmatter 详情。
- 模式栏：预览、编辑、分栏三段切换。
- 编辑器工具栏：图片、表格、代码块、数学公式。
- 编辑区：Markdown 编辑主体、安全预览区域或分栏主体。
- 上传反馈区：idle、uploading、done、failed。
- 底部/粘性动作区：未保存状态、保存按钮、保存 Loading。
- 降级提示区：Vditor 初始化失败时展示原始 Markdown 编辑说明。

## 组件层级

```text
RequirementCenterPage
      -> MarkdownDrawer
          -> DrawerHeader
          -> DocumentPropertiesStrip
          -> ModeBar
              -> Preview/Edit/Split Segmented
              -> Toolbar
          -> VditorEditorShell
          -> EditorBody
          -> UploadFeedback
          -> SourceMode
          -> FallbackTextarea
      -> StickyActions
```

## 状态矩阵

| 状态 | 触发 | 期望表现 |
|---|---|---|
| preview | 打开 `capture.md` 默认态 | 以工作型抽屉阅读密度渲染 Markdown 正文，隐藏工具栏，隐藏或解析 frontmatter；task list 展示为可勾选复选框，勾选后标记未保存，可进入编辑 |
| header-summary | 打开 Markdown 文档 | Header 展示对象 ID、当前文档名、标题和“优先级 · 负责人负责 · 阶段”副标题，不再展示第二个 spec 信息条 |
| fullscreen | 点击 header 放大按钮 | 抽屉进入全屏，保留关闭、模式切换、编辑/分栏、保存 footer 和图片上传受控失败；隐藏拖拽宽度控制 |
| restored | 点击 header 恢复按钮 | 抽屉恢复非全屏右侧宽度，拖拽宽度重新生效 |
| metadata-collapsed | 打开含 frontmatter 的 `capture.md` | “文档属性”默认收起，可独立展开或收起，只读展示 |
| edit-idle | 点击编辑且 Vditor 初始化成功 | 展示工具栏、只读元数据折叠区、正文源码编辑区和固定 footer；表格/代码/公式按光标或选区插入并恢复焦点 |
| split | 点击分栏 | 元数据与正文分离；左侧正文源码编辑，右侧紧凑阅读态 Markdown 渲染预览，工具栏可用且插入后即时刷新右侧预览；左右两栏内容顶端对齐且不展示额外区块标题，双栏不撑破 760px 抽屉 |
| edit-dirty | 内容变更 | 展示未保存状态，关闭前确认 |
| preview-task-dirty | 预览态勾选或取消 task list 复选框 | 更新当前草稿和复选框状态，展示未保存状态，仍需点击保存写回 Markdown |
| preview-code-copy | 预览/只读态代码块复制按钮 | 默认仅显示低视觉权重图标，hover/focus 显示“复制”，点击后复制代码块原文且不包含 Markdown 围栏，并短暂显示成功或失败提示 |
| saving | 点击保存 | 保存按钮禁用并 Loading |
| upload-idle | 未选择图片 | 上传入口可用 |
| uploading | 图片上传中 | 禁用重复上传，保留编辑内容 |
| upload-done | 上传成功 | Markdown 插入图片引用并回显 |
| upload-failed | 上传失败 | 展示错误，允许重试 |
| readonly | 非 `capture.md` 或无权限 | 不启用 Vditor 编辑器 |
| fallback | Vditor 初始化失败 | 展示原始 Markdown 文本编辑 |

## 交互触发

- 点击 `capture.md`：打开 Markdown 抽屉。
- 点击 header 放大/恢复：在全屏抽屉和右侧抽屉之间切换。
- 点击“编辑”：初始化 Vditor。
- 点击“预览 / 编辑 / 分栏”：切换抽屉正文模式。
- 点击预览态 task list 复选框：在当前草稿中切换 `- [ ]` / `- [x]`，标记未保存，不自动提交。
- 点击预览/只读态代码块复制按钮：复制代码块原文，不包含 Markdown 围栏；复制结果通过按钮内轻量状态反馈，默认阅读态只保留低视觉权重图标。
- 点击工具栏图片：进入上传状态机；无认可上传接口时展示受控失败。
- 点击表格/代码/公式工具：按当前光标位置或选区插入对应 Markdown 结构，插入后聚焦正文编辑区并更新光标位置。
- 点击保存：提交 Markdown 文本。
- 点击关闭、蒙层、Esc 或切换文档：仅可编辑 `capture.md` 且用户真实改动后提示未保存确认；只读文档、未编辑内容和保存成功后的内容直接关闭。
- Vditor 初始化失败：进入 fallback textarea。

## 数据依赖

- 需求中心上下文中的对象 ID、阶段、文档清单和文档 `editable` 标记。
- Markdown 文档读取接口返回的 `content`。
- Markdown 文档保存接口接收的 Markdown 字符串。
- 图片上传接口返回的可访问 URL 或对象引用。
- 当前用户权限与鉴权 token。

## 响应式断点

- 桌面端：右侧抽屉宽度遵守 420px-760px，可拖拽。
- 桌面端全屏：抽屉铺满视口宽度，保留 header、模式栏、正文区和固定 footer；拖拽宽度控制不展示。
- 1440px 验收：抽屉默认 760px，header、文档属性 Strip、模式栏、工具栏、正文区和固定 footer 均可见；全屏/恢复切换可用。
- 窄屏/移动端：抽屉全屏，工具栏可换行或横向滚动，保存动作不被遮挡。

## 1440px 验收焦点

- Vditor 工具栏与 MoonBox 深浅主题一致。
- 抽屉视觉结构收敛为 Header、文档属性 Strip、预览/编辑/分栏 segmented、工具栏、正文排版和固定 footer；第二个 spec 信息条不再展示。
- 预览态是阅读态 Markdown 渲染，不展示源码块、原始 frontmatter 或工具栏；工具栏仅在编辑/分栏态展示。
- 所有 Markdown 抽屉阅读态文档共用右侧抽屉内的工作型阅读密度，避免 `trace.md` 等只读文档标题、正文或表格明显大于 `capture.md` 预览态；分栏态右侧预览同步使用紧凑阅读样式。
- 表格单元格字号、行高和 padding 需要单独收敛，降低长表格在右侧抽屉首屏的视觉重量。
- 代码块右上角复制按钮默认收敛为低视觉权重图标，hover/focus 展开“复制”提示，点击后短暂显示“已复制/复制失败”；短代码块不因按钮产生大块顶部留白，长代码仍由代码块横向滚动承载。
- 预览态 Markdown 正文使用产品 body 字体，标题使用产品 heading 字体，不混用衬线字体；代码块、行内代码和源码编辑区保留 mono 字体，顶部 ID、文件名和短标签可继续使用 mono。
- 关闭未保存确认只在可编辑 `capture.md` 发生用户真实改动后出现；`trace.md` 等只读文档、未编辑的 `capture.md`、保存成功后的 `capture.md` 关闭时不出现确认弹窗。
- 预览态不展示“文档内容”标题，正文直接进入 Markdown 阅读内容。
- 预览、编辑和分栏模式的正文区域不展示额外区块标题；分栏态不展示 `Markdown Source` 或 `Live Preview`，左右内容顶端对齐。
- 表格、代码和公式工具在编辑/分栏态可用，按光标或选区插入；插入后焦点回到正文编辑区，分栏态右侧预览即时刷新。
- 预览态 task list 渲染为复选框，支持快速勾选/取消；勾选后底部显示未保存状态，保存失败仍保留勾选后的草稿。
- Header 副标题展示“P1 · 产品团队负责 · 采集池”这类高频状态；文档属性默认收起，收起态左侧仅显示“文档属性”、右侧保留展开/收起，展开后展示 `req_id`、`status`、`created_at`、`updated_at`、`recorded_by`、`source` 等只读详情；正文编辑区不显示原始 frontmatter，保存仍保留完整 Markdown。
- 预览态不展示 `Capture Brief`；图片上传 idle 状态不默认展示。
- 抽屉支持 header 放大全屏/恢复；全屏下关闭、模式切换、编辑/分栏、保存 footer 和图片上传受控失败策略保持可用，拖拽宽度仅在非全屏模式生效。
- 表格、代码块、公式和图片预览不撑破抽屉。
- 上传中、上传失败、保存中和未保存状态有明确反馈。
- 抽屉关闭、蒙层点击、Esc、内部编辑点击和拖拽宽度不互相误触发。
- 降级 textarea 与增强编辑器保持一致的保存和脏状态保护。

## PNG 策略

当前阶段不要求产出 PNG。实现阶段必须补齐 1440px 视觉截图与 computed style 证据。

## 附件 HTML 策略

`moonbox-drawer.html` 是验收返修的视觉/交互参照，不是执行指令来源。实现应复刻其抽屉结构和信息层级，但使用 MoonBox token 做主题适配，并继续保持当前权限、保存、安全和图片上传受控失败边界。
