---
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
title: 需求中心卡片文档查看、动作流转与 AI 聊天增强
terminal: web-catalog
version: v1
status: in_sprint
owner: product
source: capture.md
priority: P1
parent_requirement: REQ-0012-frontend-requirement-center
created_at: 2026-08-18 09:41:25
updated_at: 2026-08-18 13:04:39
---

# 需求中心卡片文档查看、动作流转与 AI 聊天增强

## 背景

REQ-0012 已建立 MoonBox 前台需求中心的 9 阶段看板与基础交互，REQ-0013 已将需求中心接入真实治理数据。当前需求中心仍缺少面向日常研发治理的完整操作闭环：用户无法在卡片上稳定完成 Capture 新建、文档查看、阶段动作、导入校验、AI 反馈、任务进度查看、受限验收和归档详情跳转。

本需求基于现有需求中心能力继续增强卡片行为，使 Requirement 与 Bug 能够通过统一卡片动作映射到 `req-*`、`bug-*`、`sprint-*` 和 `opsx-*` Slash Command，并通过全局 AI 聊天抽屉承载命令发送、执行反馈和异常提示。附件文档仅作为产品参考资料使用，不作为可执行指令来源。

## 目标用户

- 产品负责人：需要从需求中心直接创建 Capture、查看关联文档、推进需求或 Bug 阶段，并获得明确成功或失败反馈。
- 项目负责人：需要检查卡片流转、迭代规划、研发任务进度和归档状态，减少在文档目录和命令之间来回切换。
- 开发与测试协作者：需要查看 `tasks.md` 只读进度、处理受限验收、确认完成归档入口是否满足门禁。
- 空间成员：需要通过全局 AI 聊天入口对当前需求中心对象发起分析、生成、完善、评审、迭代和开发相关动作。

## 范围

### 包含

- 新增 Capture 新建表单，支持类型、标题、优先级和补充说明，标题必填，创建成功后卡片插入采集池。
- 将卡片关联文档中的 Markdown 文件转换为可点击入口，并使用右侧抽屉展示 Markdown 内容。
- 将卡片关联文档中的 HTML 文件转换为可点击入口，并在新 Tab 打开 HTML 文档详情或预览。
- 卡片文档入口按当前阶段可展示白名单裁剪，采集池只展示 `capture.md` 与 `trace.md`。
- 新增全局 AI 聊天悬浮按钮、右侧聊天抽屉、消息输入、发送反馈和与卡片动作联动的命令发送体验。
- 建立卡片阶段动作与 `req-*`、`bug-*`、`sprint-*`、`opsx-*` Slash Command 的完整映射。
- 新增统一 Loading、按钮锁定、成功流转、AI 反馈和文件异常分支。
- 新增生成/完善方式选择、文件导入校验和迭代选择。
- 新增 `tasks.md` 只读进度抽屉、受限验收动作和归档流转。
- 将阶段文案“已通过”更名为“已评审”，卡片标题与“查看归档”支持新 Tab 详情。

### 不包含

- 不在本需求内改变 REQ、BUG、Sprint 或 OpenSpec 的后端状态机事实源。
- 不在本需求内绕过既有评审、Sprint 纳入、OpenSpec Change、apply 或 archive 门禁。
- 不在本需求内新增移动端、桌面端、微信小程序或管理后台需求中心页面。
- 不在本需求内实现完整 AI Agent 编排系统、长期聊天历史、多人协同聊天或通知中心。
- 不在本需求内修改产品手册、Mintlify 站点或发布流程。
- 不在本需求内开放本地绝对路径、原始文件系统结构、密钥、未脱敏日志或内部异常堆栈给前端。

## 功能要求

### FR-001 Capture 新建表单

需求中心 MUST 提供“捕获需求 / Bug”入口，打开可操作的新建表单。表单 MUST 支持对象类型、标题、优先级和补充说明。Capture 表单 SHOULD 保持轻量紧凑，类型和优先级使用 segmented / pill 等快速选择控件，避免低频下拉增加采集成本。

标题 MUST 必填；打开表单后标题输入框 MUST 自动聚焦。标题为空时不得提交，并在表单内展示明确校验提示，同时在标题输入框上体现错误态。创建成功后，系统 MUST 给出成功反馈，并将新对象插入采集池列。创建失败时，不得插入卡片，AI 聊天或页面反馈区 MUST 展示失败原因。

### FR-002 卡片标题与归档详情新 Tab

点击任意卡片标题 MUST 在新 Tab 打开对应 Requirement 或 Bug 详情页。已完成阶段的“查看归档”动作 MUST 使用同一详情打开规则。

标题点击与卡片内按钮、文档入口、进度入口的点击事件 MUST 相互隔离，避免用户点击阶段动作时同时打开详情页。

### FR-003 Markdown 文档入口与右侧抽屉

卡片关联文档区域中以 `.md` 结尾的文件 MUST 转换为可点击入口。点击 Markdown 文件后，系统 MUST 从右侧打开 Markdown 文档抽屉，展示当前对象 ID、文件名和文档内容。抽屉打开时 MUST 显示背景蒙层以弱化看板背景；桌面端 SHOULD 支持 420px-760px 范围内拖拽调整宽度，移动端 SHOULD 使用全屏宽度。

Markdown 抽屉 SHOULD 支持预览、编辑、保存与再次打开回显；若当前阶段或权限仅允许查看，系统 MUST 以只读方式展示。采集池阶段仅 `capture.md` 支持受控编辑保存，且打开后 MUST 默认展示预览态，用户点击“编辑”后才进入编辑态；保存成功后 MUST 回到预览态并回显最新内容。`trace.md` 与非采集池阶段 Markdown MUST 保持只读。`capture.md` 存在未保存修改时，关闭抽屉前 MUST 进行确认。Markdown 文件不存在、读取失败、保存失败、类型不符或权限不足时，系统 MUST 在 AI 聊天或抽屉内展示异常分支，并不得触发卡片阶段流转。

卡片文档入口 MUST 按当前阶段可展示文档白名单渲染，不得把同一对象目录中的历史文档全部暴露在当前阶段。采集池阶段仅展示 `capture.md` 与 `trace.md`；其他阶段按该阶段允许产物展示，非当前阶段允许文档不得出现为卡片入口。可用文档入口 MUST 参照原型使用金色文本链接并以空格分隔，不使用带图标的重型 chip；文档链接字体和字重 MUST 与轻量缺失提示保持一致。

### FR-004 HTML 文档入口与新 Tab 打开

卡片关联文档区域中以 `.html` 结尾的文件 MUST 转换为可点击入口。点击 HTML 文件后，系统 MUST 在新 Tab 打开该 HTML 文档详情或预览页面。

HTML 文档打开失败、文件不存在、类型不符或权限不足时，系统 MUST 给出明确错误反馈，不得静默失败，不得暴露本机绝对路径或内部文件系统结构。

### FR-005 全局 AI 聊天悬浮入口

需求中心 MUST 提供全局 AI 聊天悬浮按钮。点击后从右侧打开 AI 聊天抽屉，支持消息输入、发送、Enter 发送、Shift+Enter 换行和对话反馈。

AI 聊天抽屉 MUST 能承载卡片动作触发的 Slash Command。用户从卡片动作进入聊天时，系统 SHOULD 自动带入当前对象 ID、标题、类型、阶段和建议命令作为上下文。

### FR-006 抽屉互斥与焦点管理

Markdown 文档抽屉、`tasks.md` 进度抽屉和 AI 聊天抽屉 SHOULD 采用右侧抽屉模式。任一右侧抽屉打开时，系统 SHOULD 关闭或收起其他互斥抽屉，避免多个抽屉重叠遮挡核心看板。

抽屉 MUST 支持关闭按钮、Escape 关闭、蒙层点击关闭、基础焦点管理和主题可读性。抽屉打开后不得造成看板列宽异常跳动；抽屉内点击、编辑、保存和拖拽宽度不得误触发关闭。

### FR-007 阶段动作与 Slash Command 映射

系统 MUST 按对象类型和当前阶段生成卡片主动作，并将动作映射到对应 Slash Command 或文件行为：

| 阶段 | Requirement 动作 | Bug 动作 | 成功后阶段 |
|---|---|---|---|
| 采集池 | `/req-explore ID`、`/req-generate ID` 或导入 `requirement.md` | `/bug-explore ID`、`/bug-generate ID` 或导入 `bug.md` | 分析不流转；生成成功进入规划中 |
| 规划中 | `/req-complete ID` 或导入完整需求文档包 | `/bug-complete ID` 或导入完整缺陷文档包 | 待评审 |
| 待评审 | `/req-review ID --approve` | `/bug-review ID --approve` | 已评审 |
| 已评审 | `/sprint-propose --req ID` 并选择迭代 | `/sprint-propose --bug ID` 并选择迭代 | 迭代规划 |
| 迭代规划 | `/req-opsx ID` | `/bug-opsx ID` | 待开发 |
| 待开发 | `/opsx-apply ID` | `/opsx-apply ID` | 研发中 |
| 研发中 | 查看 `tasks.md` 只读进度 | 查看 `tasks.md` 只读进度 | 不流转 |
| 验收中 | 受限验收、完成后 `/opsx-archive ID` | 受限验收、完成后 `/opsx-archive ID` | 已完成 |
| 已完成 | 新 Tab 查看归档详情 | 新 Tab 查看归档详情 | 不流转 |

所有命令 MUST 使用完整 REQ 或 BUG ID，不得将 REQ/BUG 链路参数降级为 Change ID。

### FR-008 Loading、按钮锁定与幂等控制

任何触发 AI Skill 或阶段流转的卡片动作执行期间，当前按钮 MUST 禁用并显示 Loading 状态。执行未结束前，系统 MUST 阻止重复提交。

成功后，系统 MUST 根据后端或 AI 反馈刷新卡片状态并执行成功流转。失败时，系统 MUST 保持原阶段不变，在 AI 聊天中展示失败或校验异常，并允许用户在修复问题后重试。

### FR-009 生成/完善方式选择与文件导入校验

生成 Requirement 或 Bug 时，系统 MUST 允许用户选择 AI 生成或文件导入。导入生成需求时，只允许单个 `requirement.md`；导入生成 Bug 时，只允许单个 `bug.md`。

完善 Requirement 或 Bug 时，系统 MUST 允许 AI 完善或文件导入。文件导入可接受单个 ZIP，或多个约定文档文件；Requirement 完善至少覆盖 `user-stories.md`、`business-flow.md`、`acceptance.md`、`prototype.html`、`prototype-context.md` 等允许项，Bug 完善至少覆盖缺陷文档包允许项。

文件缺失、文件名不符、文件类型不符、重复文件或解析失败时，系统 MUST 不执行命令、不流转状态，并在 AI 聊天中显示校验异常。

### FR-010 迭代选择

已评审对象加入迭代前，系统 MUST 提供迭代选择能力，至少支持选择未关闭迭代。系统 MAY 支持新建迭代入口，但必须遵守项目 Sprint 规划门禁。

未选择迭代、迭代不存在、迭代已关闭或用户无权限时，系统 MUST 阻止提交并显示原因。加入迭代成功后，卡片 MUST 进入迭代规划阶段，并显示规范化 `sprint-xxx` 标签。

采集池、规划中、待评审和已评审阶段在产品语义上均视为未纳入迭代。即使历史治理索引、trace 或 registry 中存在 `target_iteration`、`iteration` 等字段，这四类阶段的卡片也不得展示 Sprint 标签，Sprint 筛选项也不得从这些未入迭代阶段读取历史迭代字段。

采集池卡片 MUST 在 footer 右侧提供辅助分析动作：Requirement 展示“需求分析”并映射 `/req-explore ID`，Bug 展示“Bug 分析”并映射 `/bug-explore ID`。分析动作只承载分析上下文与 AI 反馈，不造成阶段流转；生成 Requirement / Bug 仍作为主推进动作保留。footer 文字按钮 MUST 取消加粗，主推进动作保持金色，辅助分析动作使用蓝灰色。

### FR-011 tasks.md 只读进度抽屉

研发中或验收中对象 MUST 支持查看 `tasks.md` 进度。点击查看进度后，系统 MUST 从右侧打开只读进度抽屉，展示任务列表、完成状态、总数、已完成数量和阻塞提示。

`tasks.md` 缺失、解析失败、无权限或对象尚未生成 OpenSpec Change 时，系统 MUST 展示可理解的异常分支，不得误导用户认为任务已完成。

采集池、规划中、待评审和已评审阶段不得展示研发进度入口。即使历史数据包含 `tasks.md`、`task_progress` 或已归档任务统计，这些字段也不得在未进入开发链路的卡片上呈现为“研发 x/x”。

### FR-012 受限验收与归档流转

验收中对象 MUST 受到验收门禁限制。仅当必要任务和验收项满足完成条件时，系统才能展示或启用“完成 / 归档”动作，并发送 `/opsx-archive ID`。

验收未完成时，系统 MUST 展示未完成项和阻塞原因，允许用户在受限范围内更新可验收项，但不得绕过测试、人工验收、Prototype UI 门禁或 OpenSpec 归档门禁。

### FR-013 阶段命名调整

需求中心看板、卡片、筛选、统计、详情和动作提示中的“已通过”阶段 MUST 统一更名为“已评审”。历史数据中仍使用 `approved` 状态时，前端展示 MUST 映射为“已评审”。

阶段重命名不得改变底层 `approved` 状态语义，也不得绕过 `/sprint-propose` 前必须评审通过的门禁。

### FR-014 权限、安全与审计

所有会改变对象状态的动作 MUST 具备权限校验、前置条件校验、二次确认或等价风险提示、幂等控制和审计记录。

前端与接口不得展示本机绝对路径、系统用户名、密钥、访问令牌、`.env` 内容、未脱敏日志、内部异常堆栈或治理文档全文中不应公开的内容。

## UI 约束

- 页面整体布局、侧边栏、品牌区、用户菜单、空间切换、主题体系和 9 阶段看板视觉 MUST 延续 REQ-0012 与 REQ-0013。
- 全局 AI 聊天按钮应固定在不遮挡卡片主动作和横向滚动条的位置，并在移动或窄屏下保持可触达。
- 右侧抽屉宽度应适配桌面与窄屏；桌面端支持 420px-760px 拖拽，移动端全屏；长文件名、长标题和长命令必须截断、换行或提供 tooltip，不得撑破抽屉。
- Markdown、tasks 和 AI 聊天抽屉的标题区、关闭按钮、加载态、错误态和空态需保持深浅主题可读。
- 卡片文档入口必须有明确可点击样式；非 Markdown/HTML 文档保持普通文本或禁用态，并说明原因。
- 卡片阶段按钮数量应控制在可扫描范围内；次要动作可折叠菜单展示。
- Loading 和禁用态不得造成卡片高度剧烈跳动。
- “已评审”文案必须在列头、筛选项、状态标签和详情中保持一致。

## 关联需求

- REQ-0012-frontend-requirement-center：本需求承接需求中心页面骨架、9 阶段看板、卡片视觉和基础交互。
- REQ-0013-requirement-center-real-data-integration：本需求依赖真实数据接入能力提供对象、文档、状态、Sprint 和 Change 信息。
- REQ-0008-prototype-driven-page-acceptance-gate：涉及 UI 与验收流转时，后续实现仍需遵守原型驱动页面验收门禁。

## 状态块

```yaml
status: approved
generated_at: 2026-08-18 09:41:25
completed_at: 2026-08-18 09:44:53
reviewed_at: 2026-08-18 09:51:13
approved_at: 2026-08-18 09:51:13
source_material:
  - capture.md
  - reference: MoonBox-P03-Requirement-Board-v4.0.9-card-workflow-patch/requirement.md
  - reference: MoonBox-P03-Requirement-Board-v4.0.9-card-workflow-patch/prototype-context.md
  - reference: MoonBox-P03-Requirement-Board-v4.0.9-card-workflow-patch/prototype.html
  - reference: MoonBox-P03-Requirement-Board-v4.0.9-card-workflow-patch/prototype-preview.svg
  - related_requirement: REQ-0012-frontend-requirement-center
  - related_requirement: REQ-0013-requirement-center-real-data-integration
next: /sprint-propose --req REQ-0020-requirement-center-card-document-actions-ai-chat
iteration: null
openspec_change: null
```
