---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
status: pending_review
created_at: 2026-08-19 11:36:10
updated_at: 2026-08-19 11:36:10
owner: product
source: requirement.md
---

# Prototype Context

## 页面清单

- 前台需求中心看板页面。
- Markdown 文档右侧抽屉。
- `capture.md` 可编辑态内的 Vditor 增强编辑器。

## 关键区域

- 抽屉标题区：对象 ID、文档名、编辑/预览状态、关闭按钮。
- 编辑器工具栏：图片、表格、代码块、数学公式、预览/源码切换。
- 编辑区：Markdown 编辑主体、预览区域或所见即所得主体。
- 上传反馈区：idle、uploading、done、failed。
- 底部/粘性动作区：未保存状态、保存按钮、保存 Loading。
- 降级提示区：Vditor 初始化失败时展示原始 Markdown 编辑说明。

## 组件层级

```text
RequirementCenterPage
  -> MarkdownDrawer
      -> DrawerHeader
      -> VditorEditorShell
          -> Toolbar
          -> EditorBody
          -> UploadFeedback
          -> SourceMode
          -> FallbackTextarea
      -> StickyActions
```

## 状态矩阵

| 状态 | 触发 | 期望表现 |
|---|---|---|
| preview | 打开 `capture.md` 默认态 | 展示当前 Markdown 内容，可进入编辑 |
| edit-idle | 点击编辑且 Vditor 初始化成功 | 展示工具栏和编辑区 |
| edit-dirty | 内容变更 | 展示未保存状态，关闭前确认 |
| saving | 点击保存 | 保存按钮禁用并 Loading |
| upload-idle | 未选择图片 | 上传入口可用 |
| uploading | 图片上传中 | 禁用重复上传，保留编辑内容 |
| upload-done | 上传成功 | Markdown 插入图片引用并回显 |
| upload-failed | 上传失败 | 展示错误，允许重试 |
| readonly | 非 `capture.md` 或无权限 | 不启用 Vditor 编辑器 |
| fallback | Vditor 初始化失败 | 展示原始 Markdown 文本编辑 |

## 交互触发

- 点击 `capture.md`：打开 Markdown 抽屉。
- 点击“编辑”：初始化 Vditor。
- 点击工具栏图片：进入上传状态机。
- 点击表格/代码/公式工具：插入对应 Markdown 结构。
- 点击保存：提交 Markdown 文本。
- 点击关闭、蒙层、Esc 或切换文档：如有未保存修改则确认。
- Vditor 初始化失败：进入 fallback textarea。

## 数据依赖

- 需求中心上下文中的对象 ID、阶段、文档清单和文档 `editable` 标记。
- Markdown 文档读取接口返回的 `content`。
- Markdown 文档保存接口接收的 Markdown 字符串。
- 图片上传接口返回的可访问 URL 或对象引用。
- 当前用户权限与鉴权 token。

## 响应式断点

- 桌面端：右侧抽屉宽度遵守 420px-760px，可拖拽。
- 1440px 验收：抽屉打开后看板背景、工具栏、编辑区和保存动作均可见。
- 窄屏/移动端：抽屉全屏，工具栏可换行或横向滚动，保存动作不被遮挡。

## 1440px 验收焦点

- Vditor 工具栏与 MoonBox 深浅主题一致。
- 表格、代码块、公式和图片预览不撑破抽屉。
- 上传中、上传失败、保存中和未保存状态有明确反馈。
- 抽屉关闭、蒙层点击、Esc、内部编辑点击和拖拽宽度不互相误触发。
- 降级 textarea 与增强编辑器保持一致的保存和脏状态保护。

## PNG 策略

当前阶段不要求产出 PNG。实现阶段必须补齐 1440px 视觉截图与 computed style 证据。
