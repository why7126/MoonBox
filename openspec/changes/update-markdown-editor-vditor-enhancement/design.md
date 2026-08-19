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

当前 REQ 只有 `prototype/web/context.md`，无 HTML/PNG 原型文件。实现阶段不需要还原静态原型图，而是必须承接 context 中的页面清单、区域、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。

冲突处理：

- 若 Vditor 默认样式与 MoonBox UI 规则冲突，以 `rules/ui-design.md` 的深浅主题、金色强调、近直角、细线和克制编辑排版感为准。
- 若 Vditor 图片上传能力与当前生产上传接口不匹配，MVP 必须禁用上传入口或使用受控占位策略，不得写入本机路径、临时私有地址或对象存储凭据。
- 若 Vditor 允许 HTML 输入，默认按安全优先处理；实现必须明确清洗/白名单或禁用策略，且不得执行脚本、事件属性或危险链接。

## UI Contract

### 页面与区域

- 页面：前台需求中心看板。
- 入口：卡片文档区 `capture.md` 链接。
- 容器：既有右侧 Markdown 抽屉。
- 编辑区域：`capture.md` 可编辑态内的 `VditorEditorShell`。

### 启用规则

Vditor 仅在以下条件全部满足时启用：

- 对象处于采集阶段。
- 文档名为 `capture.md`。
- 文档 `editable` 不为 false。
- 当前用户具备读取和保存该文档权限。

不满足条件时，`trace.md`、非采集阶段 Markdown、不可编辑文档和无权限文档必须继续只读展示。

### 关键尺寸与布局

- 桌面抽屉宽度沿用 420px-760px。
- 移动端抽屉全屏。
- 工具栏允许换行或横向滚动，不得遮挡保存动作。
- 表格、代码块、公式和图片预览必须在抽屉内具备溢出处理。

### 视觉规则

- Vditor 工具栏、编辑区、预览区、弹出层和状态提示必须适配 MoonBox 深浅主题。
- 主要强调色使用 MoonBox 金色 token，不引入蓝紫科技风或大圆角卡片样式。
- 按钮、边框和浮层层级必须与当前 Markdown 抽屉一致。

### 权限与安全

- 前端不得仅凭 UI 判断保存权限；保存仍由后端校验。
- 图片上传必须携带当前会话鉴权。
- 上传 URL、对象 key、错误提示和日志不得泄露临时凭据、私有存储地址、本机绝对路径或内部异常堆栈。
- Markdown 渲染不得执行脚本、事件属性或危险链接。

### Mock/API 边界

- 文档读取与保存使用真实需求中心文档接口。
- 图片上传若使用真实接口，必须接入现有鉴权与对象存储路径；若接口不足，必须禁用上传并在 Change trace 中记录豁免与后续补齐条件。
- 不允许使用 Mock 图片上传冒充生产可用上传。

## UI Skeleton

```text
RequirementCenterPage
  -> MarkdownDrawer
      -> DrawerHeader
      -> MarkdownDocumentState
      -> VditorEditorShell
          -> VditorToolbar
          -> VditorBody
          -> UploadStateFeedback
          -> SourceModeToggle
          -> FallbackTextarea
      -> StickySaveActions
```

状态容器：

- `drawer.content`: 服务端已保存 Markdown。
- `drawer.draft`: 当前编辑 Markdown。
- `drawer.mode`: preview/edit。
- `editorStatus`: idle/loading/ready/fallback/error。
- `uploadStatus`: idle/uploading/done/failed。
- `saving`: 保存提交状态。

可测选择器建议：

- `data-testid="markdown-drawer"`
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
- 1440px 验收焦点：主题一致、溢出处理、上传/保存反馈、抽屉关闭与内部点击隔离、降级 textarea。

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
