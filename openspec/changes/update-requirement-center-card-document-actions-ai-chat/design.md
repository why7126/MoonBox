---
change_id: update-requirement-center-card-document-actions-ai-chat
source_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
status: proposed
created_at: 2026-08-18 09:58:34
updated_at: 2026-08-18 09:58:34
---

# Design: 需求中心卡片文档查看、动作流转与 AI 聊天增强

## 1. 设计决策

### D1. 策略：tailwind-ds + prototype-driven-ui-contract

本 Change 采用项目现有 React/Tailwind/设计系统风格实现，延续 REQ-0012 / REQ-0013 的前台需求中心结构、MoonBox token、近直角、细线和低阴影视觉语言。

不采用单纯 CSS Port。附件 `prototype.html` 作为结构和交互事实源，但生产实现必须融入现有组件、真实数据 hook、权限态、错误态和测试体系。

### D2. 全局 AI 聊天抽屉承载命令反馈

卡片阶段动作不直接静默执行。动作触发后，系统将对象 ID、标题、类型、阶段、建议命令和用户选择带入 AI 聊天抽屉，展示执行中、成功或失败反馈。实际状态仍以刷新后的治理事实源为准。

### D3. 文档预览和 capture.md 编辑走受控入口

Markdown 与 HTML 关联文档只通过白名单字段和受控预览/读取入口打开。前端不得基于本机绝对路径拼接 URL，也不得展示内部文件系统结构。采集池阶段的 `capture.md` 打开后默认进入预览态，用户点击“编辑”后才进入受控编辑态；保存成功后回到预览态并回显服务端返回内容。`trace.md` 和非采集池阶段 Markdown 保持只读，避免绕过需求/缺陷治理链路。

### D4. 阶段流转只由命令成功与刷新事实源确认

按钮成功态仅表示命令调用成功，不直接伪造最终阶段。执行成功后必须刷新需求中心上下文；刷新结果确认阶段后再移动卡片。失败或校验异常时保持原阶段。

## 2. Conflict Resolution

事实源优先级：

```text
prototype/web/prototype.html
> prototype/web/prototype.png
> prototype/web/context.md
> acceptance.md
> rules/ui-design.md
> openspec/specs/web-catalog-requirement-center/spec.md
> openspec/specs/web-catalog-requirement-center-real-data/spec.md
```

| 冲突点 | 处理 |
|---|---|
| 现行规格仍写“已通过” | 前端展示统一改为“已评审”，底层 `approved` 状态不变 |
| 原型使用静态模拟命令执行 | 生产实现必须接入真实命令发送/反馈边界或明确 Mock/API 边界；状态以刷新后的事实源为准 |
| 原型可直接展示文档内容 | 生产实现必须通过受控文档读取/预览接口，不暴露本机路径 |
| 原型中的 localStorage Markdown 演示 | 可作为交互演示，不作为生产保存事实源；生产保存仅限采集池 `capture.md` |
| UI 抽屉互斥与已有页面浮层 | 右侧抽屉统一使用互斥状态机，弹窗和抽屉必须有明确关闭路径 |

## 3. UI Contract

### 3.1 页面与入口

- 页面：前台需求中心 `/requirements`。
- 入口：
  - 工具栏或页面动作中的“捕获需求 / Bug”。
  - 卡片标题。
  - 卡片关联文档区域。
  - 卡片阶段动作按钮。
  - 页面右下角 AI 聊天悬浮按钮。
- 不新增右侧内容区全局顶部导航栏。

### 3.2 信息架构

```text
RequirementCenterPage
  ├─ Sidebar / UserMenu / SpaceSwitcher
  ├─ PageHeader
  ├─ StatsPanel
  ├─ Toolbar
  ├─ KanbanBoard
  │   └─ KanbanColumn × 9
  │       └─ RequirementCard / BugCard
  │           ├─ CardTitleLink
  │           ├─ SprintTag（仅迭代规划及后续阶段）
  │           ├─ DocumentLinks
  │           └─ StageActionButton
  ├─ CaptureDialog
  ├─ WorkflowChoiceDialog
  ├─ SprintChoiceDialog
  ├─ MarkdownDrawer
  ├─ TasksDrawer
  ├─ AiFloatingAction
  ├─ AiChatDrawer
  └─ Toast
```

### 3.3 视觉 Token

- 颜色、字体、边框、圆角、阴影延续 `rules/ui-design.md` 与现有前台需求中心。
- Requirement 卡片左边框使用蓝色语义；Bug 卡片左边框使用红色语义。
- 主强调使用单一金色，不新增蓝紫渐变、厚阴影或大圆角装饰。
- 抽屉和弹窗在深浅主题下均需保持标题、正文、输入框、按钮、错误态可读。

### 3.4 交互状态

- 卡片标题、文档入口、阶段动作必须阻止误冒泡。
- 卡片文档入口按阶段可展示白名单裁剪，不能把同一对象目录内的历史文档全部暴露到当前阶段。采集池阶段只展示 `capture.md` 与 `trace.md`；后续阶段可展示文档以该阶段允许产物为准，HTML 原型预览仅在允许阶段展示。可用文档入口采用原型式金色文本链接并以空格分隔，不使用带图标的重型 chip；文档链接字重与缺失提示保持轻量一致。
- 未进入开发链路的卡片不得展示 `tasks.md` 研发进度。`taskProgress` 仅在待开发、研发中、验收中和已完成阶段可作为入口展示，采集池、规划中、待评审和已评审阶段即使存在历史 `tasks.md` 或进度字段也必须隐藏。
- 采集池卡片除了主生成动作外，必须在 footer 右侧提供轻量文本辅助分析动作：Requirement 文案为“需求分析”并映射 `/req-explore <REQ-ID>`，Bug 文案为“Bug 分析”并映射 `/bug-explore <BUG-ID>`，点击后进入 AI 聊天反馈上下文，不直接流转阶段。footer 文本按钮不得加粗，主生成动作保持金色，辅助分析动作使用蓝灰色以弱化层级。
- 当前动作执行期间按钮禁用并显示 Loading。
- Markdown、tasks 与 AI 聊天右侧抽屉互斥。
- 弹窗/抽屉支持关闭按钮、Escape 和外部点击；内部点击不得误关闭。右侧抽屉打开后必须显示背景蒙层以弱化看板背景，桌面端支持 420px-760px 拖拽宽度，移动端使用全屏宽度。
- Markdown 抽屉中仅采集池阶段 `capture.md` 支持编辑和保存。打开 `capture.md` 时必须先展示预览内容和“编辑”入口，点击“编辑”后才显示编辑器；关闭存在未保存修改的编辑态 `capture.md` 前必须确认；保存成功后必须回到预览态并回显最新内容。`trace.md` 必须保持只读。
- Toast 使用 fixed 定位，不造成看板 layout shift。
- Capture 弹窗采用轻量紧凑表单：类型和优先级使用 segmented / pill 选择控件，标题必填与标签同行，打开后自动聚焦标题输入框，校验失败时在输入框和表单内同步呈现错误态。
- Capture 弹窗只保留标题区分割线，字段之间通过间距分组，不使用多条横向分割线；取消和创建按钮使用统一设计系统按钮风格。

### 3.5 图标与文案

- 用户可见按钮使用产品化文案，如“生成需求”“加入迭代”“开始开发”“查看进度”“完成 / 归档”。
- 可追溯 Slash Command 存在于数据映射、AI 聊天上下文或调试信息中，不作为唯一用户可见文案。
- “已通过”展示文案统一改为“已评审”。
- 采集池、规划中、待评审和已评审阶段均视为未纳入迭代；即使历史治理索引存在 `target_iteration` 或 `iteration`，卡片也不得展示 Sprint 标签，Sprint 筛选项也不得从这些阶段读取历史迭代字段。

### 3.6 权限规则

- 无权限创建 Capture、读取文档、执行命令、加入 Sprint 或归档时，按钮隐藏或禁用并说明原因。
- 服务端仍负责权限和前置条件校验，前端禁用不得替代服务端门禁。

### 3.7 Mock/API 边界

- 卡片列表、文档列表、Sprint 列表、命令执行结果和 `tasks.md` 进度应来自真实接口或真实命令桥接。
- 若实现阶段暂用 Mock，必须在 Change trace 和验收证据中标注 Mock 区域，不得冒充生产能力。
- 文档读取、HTML 预览和导入校验不得暴露本机绝对路径、内部目录结构、原始异常堆栈或敏感内容。

### 3.8 Computed Style 验收点

实现阶段至少记录或断言：

- `.ai-fab` 的 `position`、`right`、`bottom`、`z-index`、`width`、`height`。
- `.side-drawer` 的 `width`、`max-width`、`z-index`、`overflow`、`background-color`、`border-color`。
- 卡片阶段按钮 Loading 状态下的 `height`、`line-height`、`gap`。
- Toast 的 `position: fixed` 与不影响看板布局。
- 9 列看板、列头、卡片标题、长文件名的 `overflow` 与文本换行/截断。

## 4. UI Skeleton

### 4.1 Skeleton 任务边界

实现必须先完成 UI Skeleton，再做细节数据接入和命令执行。

Skeleton 包含：

- 页面壳保持现有 Sidebar、PageHeader、Stats、Toolbar、KanbanBoard。
- 卡片新增文档入口、标题新 Tab 入口、阶段动作 loading 容器。
- 新增 CaptureDialog、WorkflowChoiceDialog、SprintChoiceDialog。
- 新增 MarkdownDrawer、TasksDrawer、AiChatDrawer、AiFloatingAction。
- 状态容器包含 loading、error、empty、permission-denied、file-invalid、command-failed。

### 4.2 可测选择器建议

```text
requirement-center-board
issue-card-{id}
issue-card-title
issue-document-link
stage-action-button
capture-dialog
workflow-choice-dialog
sprint-choice-dialog
markdown-drawer
tasks-drawer
ai-chat-drawer
ai-floating-action
```

### 4.3 1440px 验收焦点

- 9 阶段列头与卡片列对齐，横向滚动和吸顶不回归。
- AI 悬浮按钮不遮挡卡片动作和横向滚动条。
- Markdown、tasks、AI 聊天三个右侧抽屉宽度、遮罩和层级清晰。
- Capture 表单标题必填错误不造成布局跳动。
- Capture 表单在 1440px 下应完整露出类型、优先级、标题、补充说明和底部按钮；按钮风格与深色主题一致，标题校验错误态清晰。
- Workflow/Sprint 选择弹窗具备明确关闭路径。
- Loading spinner 不撑高卡片。
- 长文件名、长命令和长卡片标题不溢出。

## 5. 数据与 API 设计

### 5.1 需求中心上下文字段扩展

治理对象建议增加或确认以下白名单字段：

```yaml
documents:
  - filename: string
    kind: markdown | html | other
    label: string
    open_mode: drawer | new_tab | disabled
    url: string | null
    disabled_reason: string | null
actions:
  primary:
    label: string
    command: string
    requires_choice: none | workflow | sprint | tasks | acceptance
    disabled: boolean
    disabled_reason: string | null
progress:
  tasks_total: integer | null
  tasks_done: integer | null
  acceptance_pending: integer | null
```

### 5.2 命令执行边界

命令执行 MAY 先通过 AI 聊天桥接或受控后端接口实现，但必须满足：

- 命令参数保留完整 REQ/BUG ID。
- 执行中可取消 UI 重复提交，但不要求取消后端任务。
- 成功后刷新需求中心上下文。
- 失败时返回脱敏错误。

### 5.3 文档读取边界

- Markdown 读取返回可渲染内容或安全失败原因。
- HTML 新 Tab 只打开受控预览 URL。
- 文件导入先前端基础校验，再服务端或命令侧校验。
- Markdown 保存仅允许采集池阶段的 `capture.md`，请求体限制内容长度并通过鉴权、文件名、扩展名、issue 目录和阶段校验。`trace.md`、非采集池对象、路径越界、缺失文件和权限不足必须返回脱敏错误且不写入。

## 6. 测试策略

- 前端 Vitest/Testing Library：
  - Capture 标题必填、创建反馈和采集池插入。
  - Markdown/HTML 文档入口打开模式。
  - 卡片标题与按钮点击互不冒泡。
  - AI 聊天抽屉发送、Enter/Shift+Enter。
  - 阶段动作 Loading、按钮锁定、失败不流转。
  - Workflow/Sprint 选择与文件导入校验。
  - tasks 抽屉只读/受限验收。
  - “已评审”文案一致。
- 后端/API 测试：
  - 文档白名单、预览 URL、文件不存在/权限不足/解析失败脱敏。
  - 命令映射字段、Sprint 选择字段、tasks 进度字段。
- 视觉验收：
  - 1440px 桌面首屏。
  - Markdown/AI/tasks 抽屉。
  - Capture/Workflow/Sprint 弹窗。
  - Loading/toast/错误态。

## 7. 追溯

- REQ：`REQ-0020-requirement-center-card-document-actions-ai-chat`
- Sprint：`sprint-003`
- Knowledge refs：
  - `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`
  - `docs/knowledge-base/retrospectives/sprint-002-retrospective.md`
  - `docs/standards/prototype-ui-acceptance.md`
