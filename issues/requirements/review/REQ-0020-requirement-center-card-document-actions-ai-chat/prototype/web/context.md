---
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
title: 需求中心卡片文档查看、动作流转与 AI 聊天增强原型拆解
source_files:
  - prototype.html
  - prototype-preview.svg
  - prototype.png
  - external_reference: MoonBox-P03-Requirement-Board-v4.0.9-card-workflow-patch/prototype-context.md
status: decomposed
created_at: 2026-08-18 09:44:53
updated_at: 2026-08-18 09:44:53
---

# 原型拆解

## 页面清单

| 页面/区域 | 说明 |
|---|---|
| 需求中心看板 | 9 阶段横向 Kanban，展示 Requirement 与 Bug 卡片 |
| Capture 新建表单 | 创建需求或 Bug Capture，支持标题必填校验 |
| 卡片详情新 Tab | 标题与查看归档进入对象详情 |
| Markdown 文档抽屉 | 右侧抽屉展示 `.md` 关联文档 |
| HTML 文档新 Tab | 新 Tab 打开 `.html` 文档 |
| AI 聊天抽屉 | 全局悬浮按钮打开，承载消息和 Slash Command 反馈 |
| 生成/完善方式选择弹窗 | AI 自动生成或文件导入选择 |
| Sprint 选择弹窗 | 选择未关闭迭代或创建新迭代 |
| tasks.md 进度抽屉 | 研发中只读，验收中受限勾选 |

## 关键区域

- 左侧 Sidebar：品牌、导航、用户入口、空间菜单和主题入口延续 REQ-0012/REQ-0013。
- 页面标题区：保留页面标题、局部动作与刷新/新建入口，不新增右侧内容区全局导航栏。
- 工具栏：搜索、对象类型、负责人、优先级和 Sprint 筛选。
- 统计区：展示总量、需求、Bug、阻塞等摘要。
- Kanban 区：9 列阶段、吸顶列头、横向滚动、卡片主动作。
- 浮层区：Capture 表单、生成/完善方式弹窗、Sprint 选择弹窗。
- 右侧抽屉区：Markdown、AI 聊天、tasks 互斥打开。
- Toast/反馈区：成功、失败、校验异常和命令执行反馈。

## 组件层级

```text
RequirementCenterPage
  ├─ Sidebar
  ├─ PageHeader
  ├─ StatsPanel
  ├─ Toolbar
  ├─ KanbanBoard
  │   ├─ KanbanColumn × 9
  │   │   └─ RequirementCard / BugCard
  │   │       ├─ CardTitleLink
  │   │       ├─ SprintTag
  │   │       ├─ DocumentLinks
  │   │       └─ StageActionButton
  ├─ CaptureDialog
  ├─ WorkflowChoiceDialog
  ├─ SprintChoiceDialog
  ├─ MarkdownDrawer
  ├─ TasksDrawer
  ├─ AiFloatingAction
  ├─ AiChatDrawer
  └─ Toast
```

## 状态矩阵

| 状态 | 主动作 | 文档行为 | 进度行为 | 流转规则 |
|---|---|---|---|---|
| 采集池 | 分析 / 生成 | `capture.md` 可点 | 无 | 分析不流转，生成成功进入规划中 |
| 规划中 | 完善 | `requirement.md` / `bug.md` 可点 | 无 | 完善成功进入待评审 |
| 待评审 | 发起评审 | 文档包可点 | 无 | approve 成功进入已评审 |
| 已评审 | 加入迭代 | `review.md` 可点 | 无 | 选择 Sprint 成功进入迭代规划 |
| 迭代规划 | 生成 Opsx | sprint 文档可点 | 无 | opsx 成功进入待开发 |
| 待开发 | 开始开发 | OpenSpec 文档可点 | `tasks.md` 可点 | apply 成功进入研发中 |
| 研发中 | 查看进度 | 文档可点 | 只读 tasks | 不流转 |
| 验收中 | 继续验收 / 完成归档 | 文档可点 | 受限 tasks | 门禁满足后归档 |
| 已完成 | 查看归档 | 归档文档可点 | 只读 | 不流转 |

## 交互触发

- 点击 Capture 入口：打开 Capture 表单。
- 点击卡片标题：新 Tab 打开详情。
- 点击 `.md` 文档：阻止卡片冒泡，打开 Markdown 抽屉。
- 点击 `.html` 文档：阻止卡片冒泡，新 Tab 打开预览。
- 点击分析/生成/完善/评审/迭代/开发/归档动作：打开 AI 聊天或选择弹窗，并按映射发送 Slash Command。
- 点击 AI 悬浮按钮：打开 AI 聊天抽屉，关闭其他右侧抽屉。
- 点击查看进度：打开 tasks 抽屉。
- 点击弹窗外部、遮罩、关闭按钮或 Escape：关闭对应浮层；内部点击不得误关闭。

## 数据依赖

- `IssueCard`: ID、类型、标题、优先级、阶段、关联文档、更新时间、Sprint、Change、任务进度。
- `DocumentLink`: 文件名、类型、可访问 URL、权限、读取状态。
- `StageAction`: 当前阶段、对象类型、允许命令、前置条件、权限态。
- `AiMessage`: 用户消息、命令消息、执行中、成功、失败、校验异常。
- `SprintOption`: sprint ID、状态、可选性、容量提示。
- `TaskItem`: 任务标题、完成状态、只读/可验收、阻塞原因。

## 响应式断点

| 断点 | 要求 |
|---|---|
| 1440px 桌面 | 重点验收视口；Sidebar、标题、统计、工具栏、9 列横向看板和右侧抽屉均需可读 |
| 1280px 桌面 | 看板横向滚动可用，AI 悬浮按钮不遮挡主动作 |
| 768px 平板 | 右侧抽屉宽度收敛，卡片文字不溢出，弹窗保持可滚动 |
| 375px 移动 | 可作为后续增强；当前需求不新增移动端页面，但不得出现关键按钮不可触达 |

## 1440px 验收焦点

- 9 阶段列头与卡片列水平对齐，列头吸顶不复制、不产生额外空白。
- “已评审”列头、筛选项和卡片标签文案一致。
- Requirement / Bug 左侧语义边框保留。
- 卡片标题、文档入口、阶段动作之间点击区域清晰，不互相冒泡。
- Markdown 抽屉、AI 聊天抽屉、tasks 抽屉宽度、层级、遮罩和关闭路径清晰。
- Capture 表单标题必填错误不改变布局。
- Loading spinner 与按钮文案不撑高卡片。
- Toast 为 fixed，不造成看板 layout shift。
- 长文件名、长命令、长卡片标题不溢出容器。

## Mock/API 边界

后续实现必须在 Change `design.md` 明确：

- 卡片列表、关联文档、Sprint 列表、命令执行结果和 tasks 进度是否来自真实接口。
- 若使用 Mock 数据，Mock 仅用于前端交互开发，不代表真实命令执行或状态流转已完成。
- 任何文件预览接口不得向浏览器暴露本机绝对路径或内部目录结构。

## 原型资产说明

- `prototype.html`：附件提供的交互原型 HTML，作为 UI 结构与行为参考。
- `prototype-preview.svg`：附件提供的静态预览。
- `prototype.png`：附件提供的位图预览，后续 1440px 视觉验收可作为参考之一。
