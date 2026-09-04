---
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
title: 需求中心卡片文档查看、动作流转与 AI 聊天增强
acceptance_status: passed
owner: product
created_at: 2026-08-18 09:44:53
updated_at: 2026-09-04 15:49:25
---

# 验收标准

## 功能 AC

- [ ] AC-001 Capture 新建表单支持 Requirement / Bug 类型、标题、优先级和补充说明；标题为空时阻止提交并展示校验提示。
- [ ] AC-001A Capture 弹窗采用轻量紧凑表单：类型和优先级为快速选择控件，标题输入框自动聚焦，标题必填与标签同行，校验失败时输入框和表单内均有明确错误态。
- [ ] AC-002 Capture 创建成功后展示成功反馈，并将新卡片插入采集池；失败时不插入卡片且保留用户输入。
- [ ] AC-003 卡片标题点击在新 Tab 打开对象详情，且不影响卡片内按钮、文档入口或进度入口点击。
- [ ] AC-004 已完成卡片“查看归档”在新 Tab 打开同一对象详情。
- [ ] AC-005 `.md` 关联文档展示为可点击入口，并从带背景蒙层的右侧 Markdown 抽屉打开。
- [ ] AC-005A 卡片文档入口按当前阶段可展示白名单裁剪；采集池阶段只展示 `capture.md` 与 `trace.md`，不得展示 `acceptance.md`、`business-flow.md`、`requirement.md`、`review.md` 或 `user-stories.md` 等历史文档。
- [ ] AC-005C 开发链路卡片文档入口按必需文档表裁剪：研发中和验收中统一展示 `proposal.md`、`spec.md`、`design.md`、`trace.md`、`tasks.md`；已完成展示 `proposal.md`、`spec.md`、`design.md`、`trace.md`、`tasks.md`、`archive.md`；缺失文档 Tips 必须基于同一表计算。
- [ ] AC-005B 可用文档入口采用原型式金色文本链接并以空格分隔，不使用带图标的重型 chip；文档链接字体/字重与缺失提示保持轻量一致；缺失文档提示与上方分割线间距不得撑高卡片主体。
- [ ] AC-006 Markdown 抽屉支持只读预览；采集池阶段 `capture.md` 默认以预览态打开，点击“编辑”后进入受控编辑态，保存成功后回到预览态并回显最新内容；`trace.md` 和非采集池阶段 Markdown 保持只读。
- [ ] AC-006A Markdown 抽屉桌面端支持 420px-760px 拖拽宽度，移动端使用全屏宽；存在未保存修改时关闭抽屉必须二次确认。
- [ ] AC-007 `.html` 关联文档展示为可点击入口，并在新 Tab 打开 HTML 预览或详情。
- [ ] AC-008 文档缺失、类型不符、读取失败或权限不足时展示异常反馈，不触发卡片阶段流转。
- [ ] AC-009 全局 AI 悬浮按钮可打开右侧 AI 聊天抽屉，支持消息输入、Enter 发送和 Shift+Enter 换行。
- [ ] AC-010 卡片动作触发 AI 聊天时，聊天上下文包含对象 ID、标题、类型、当前阶段和建议命令。
- [ ] AC-011 Markdown、tasks 和 AI 聊天抽屉互斥，打开一个右侧抽屉时不会与另一个抽屉重叠遮挡；蒙层点击可关闭，抽屉内点击、编辑、保存和拖拽不得误关闭。
- [ ] AC-012 阶段动作按 Requirement / Bug 类型映射到正确 Slash Command，且命令参数保留完整 REQ/BUG ID。
- [ ] AC-012A 采集池卡片在 footer 右侧提供分析辅助动作：Requirement 展示“需求分析”并映射 `/req-explore ID`，Bug 展示“Bug 分析”并映射 `/bug-explore ID`；分析动作不得流转阶段；辅助分析动作必须排在主生成动作左侧；footer 文字按钮不得加粗，主动作保持金色，辅助分析动作使用蓝灰色。
- [ ] AC-012B 采集池分析动作随时可用且不锁定；采集池 Requirement / Bug 生成动作必须在 `capture.md` 与 `trace.md` 均存在且内容非空时可用；规划中 Requirement / Bug 完善动作必须分别在 `capture.md`、`trace.md`、`requirement.md` 或 `capture.md`、`trace.md`、`bug.md` 均存在且内容非空时可用；待评审 Requirement / Bug 评审动作必须分别在 `capture.md`、`trace.md`、`requirement.md`、`acceptance.md`、`business-flow.md`、`user-stories.md` 或 `capture.md`、`trace.md`、`bug.md`、`root-cause.md`、`workaround.md`、`acceptance.md` 均存在且内容非空时可用；已评审 Requirement / Bug 加入迭代动作必须在对应待评审文档包基础上额外具备非空 `review.md`，否则禁用并说明原因。
- [ ] AC-012C 卡片缺失文档 Tips 必须基于 AC-012B 的阶段 + 类型必备文档表展示，优先复用后端 `action.disabled_reason`，并区分缺少文档、文档内容为空和数据漂移。
- [ ] AC-012D 待评审 Requirement 的“发起评审”和待评审 Bug 的“确认修复”执行前必须二次确认；确认成功流转到已评审后，卡片主动作必须重算为“加入迭代 →”并要求选择 Sprint，不得继续保留“发起评审”或“确认修复”旧 action。
- [ ] AC-013 执行阶段动作期间当前按钮禁用并显示 Loading，重复点击不会产生重复命令。
- [ ] AC-014 命令执行成功后卡片按状态机流转；执行失败时卡片保持原阶段并在 AI 聊天展示失败原因。
- [ ] AC-015 生成阶段支持 AI 生成或导入单个 `requirement.md` / `bug.md`，导入非法文件时不执行命令。
- [ ] AC-016 完善阶段支持 AI 完善、ZIP 导入或约定多文件导入，缺失或重复文件时不执行命令。
- [ ] AC-017 已评审对象加入迭代前必须选择合法未关闭 Sprint 或合法新 Sprint；成功后显示规范化 `sprint-xxx` 标签。
- [ ] AC-017A 采集池、规划中、待评审和已评审阶段均不得显示 Sprint 标签，且 Sprint 筛选项不得包含这些未入迭代阶段卡片的历史迭代字段。
- [ ] AC-018 研发中对象可从右侧抽屉只读查看 `tasks.md` 任务进度、完成数和阻塞提示。
- [ ] AC-018A 采集池、规划中、待评审和已评审阶段不得展示“研发 x/x”进度入口，即使对象历史字段存在 `tasks.md` 或 `task_progress`。
- [ ] AC-018B 验收中 Requirement / Bug 卡片的研发、测试和人工验收进度均必须可点击打开右侧 `tasks.md` 统一进度抽屉；卡片默认视觉必须为灰蓝色次级内联文本并仅使用空格与 `gap` 做视觉分隔，不得出现 `·`、`Â·`、金色主动作色、加粗、重型按钮、边框、底色或等宽小字；人工验收必须与研发、测试一样使用 `已完成/总数` 格式；抽屉内同时展示研发任务、自动化测试和人工验收三类进度，并根据点击来源默认高亮对应分区。
- [ ] AC-019 验收中对象仅允许受限更新验收项；门禁未满足时不展示或禁用“完成 / 归档”动作。
- [ ] AC-020 满足验收门禁后发送 `/opsx-archive ID`，成功后流转到已完成。
- [ ] AC-021 看板列头、筛选项、统计、详情和状态标签统一使用“已评审”，底层 `approved` 语义不变。
- [ ] AC-022 权限不足、前置条件不满足、二次确认取消或审计失败时，状态不流转且展示明确原因。
- [ ] AC-023 前端不得展示本机绝对路径、系统用户名、密钥、token、`.env` 内容、未脱敏日志或内部异常堆栈。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解完整记录页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 生成的 Change `design.md` 必须写入 UI Skeleton，覆盖页面壳、看板、卡片、右侧抽屉、弹窗、悬浮按钮、状态容器和可测选择器。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 先完成 UI Skeleton 首轮 1440px 视觉确认，再进入细节实现。
- [ ] AC-PROTOTYPE-004 1440px 视觉验收必须覆盖首屏结构、9 列看板、卡片密度、文档抽屉、AI 聊天抽屉、Capture 表单、选择弹窗、tasks 抽屉、toast、Loading 和文本溢出。
- [ ] AC-PROTOTYPE-005 支持点击外部关闭的抽屉或弹窗必须覆盖内部 `stopPropagation` 场景：内部点击不误关闭，外部点击仍按约定关闭。
- [ ] AC-PROTOTYPE-006 实现阶段必须声明 Mock/API 边界，明确哪些对象、文档、文档正文、HTML 预览、命令反馈、Sprint 列表和 tasks 进度来自真实 API 或 Mock；受控 demo 模式仅允许通过 `?mock=workflow` 或 `?demo=workflow` 显式启用，且每个阶段至少展示 1 张 `DEMO-` 前缀卡片；demo 卡片必须按验收矩阵覆盖 Requirement / Bug、正常推进、缺失文档、空文档、数据漂移、按钮禁用、采集池 `capture.md` 可编辑、`trace.md` 只读、HTML 新 Tab、Sprint 标签隐藏/显示、tasks 进度和归档入口；demo Markdown 抽屉必须展示阶段匹配 mock 文档正文，demo HTML 入口必须打开受控 demo 预览，默认视图继续使用真实 API 数据。
- [ ] AC-PROTOTYPE-007 归档前必须完成 REQ 文档最终一致性检查，确认 requirement、acceptance、trace 与最终 Change 设计、实现证据和视觉验收结果一致。

## 横切 AC（knowledge-base）

本 REQ 为前台需求中心 UI 交互增强，未命中 `req-complete` 当前定义的 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 横切标签。

- [ ] AC-XCUT-001 N/A — 非管理端 CRUD 列表页，不适用 `admin-list-page-consistency.md`。
- [ ] AC-XCUT-002 N/A — 非管理端全页表单/设置页，不适用 `admin-form-page-consistency.md`。
- [ ] AC-XCUT-003 N/A — 非管理端宽弹窗 CSS 级联场景，不适用 `admin-modal-width-css-cascade.md`。
- [ ] AC-XCUT-004 N/A — 本需求不包含图片/视频/头像/Logo 上传链路，不适用 `admin-media-upload-chain.md`。

## Readiness

```yaml
readiness: ready
knowledge_base_gate: N/A
prototype_gate: pass
review_ready: true
next: /req-review REQ-0020-requirement-center-card-document-actions-ai-chat --approve
```

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-04 15:49:25
accepted_by: workflow-sync
source_change: update-requirement-center-card-document-actions-ai-chat
source_sprint: sprint-003
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

