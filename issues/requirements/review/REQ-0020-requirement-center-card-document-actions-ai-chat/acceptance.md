---
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
title: 需求中心卡片文档查看、动作流转与 AI 聊天增强
acceptance_status: pending
owner: product
created_at: 2026-08-18 09:44:53
updated_at: 2026-08-18 13:24:21
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
- [ ] AC-005B 可用文档入口采用原型式金色文本链接并以空格分隔，不使用带图标的重型 chip；文档链接字体/字重与缺失提示保持轻量一致；缺失文档提示与上方分割线间距不得撑高卡片主体。
- [ ] AC-006 Markdown 抽屉支持只读预览；采集池阶段 `capture.md` 默认以预览态打开，点击“编辑”后进入受控编辑态，保存成功后回到预览态并回显最新内容；`trace.md` 和非采集池阶段 Markdown 保持只读。
- [ ] AC-006A Markdown 抽屉桌面端支持 420px-760px 拖拽宽度，移动端使用全屏宽；存在未保存修改时关闭抽屉必须二次确认。
- [ ] AC-007 `.html` 关联文档展示为可点击入口，并在新 Tab 打开 HTML 预览或详情。
- [ ] AC-008 文档缺失、类型不符、读取失败或权限不足时展示异常反馈，不触发卡片阶段流转。
- [ ] AC-009 全局 AI 悬浮按钮可打开右侧 AI 聊天抽屉，支持消息输入、Enter 发送和 Shift+Enter 换行。
- [ ] AC-010 卡片动作触发 AI 聊天时，聊天上下文包含对象 ID、标题、类型、当前阶段和建议命令。
- [ ] AC-011 Markdown、tasks 和 AI 聊天抽屉互斥，打开一个右侧抽屉时不会与另一个抽屉重叠遮挡；蒙层点击可关闭，抽屉内点击、编辑、保存和拖拽不得误关闭。
- [ ] AC-012 阶段动作按 Requirement / Bug 类型映射到正确 Slash Command，且命令参数保留完整 REQ/BUG ID。
- [ ] AC-012A 采集池卡片在 footer 右侧提供分析辅助动作：Requirement 展示“需求分析”并映射 `/req-explore ID`，Bug 展示“Bug 分析”并映射 `/bug-explore ID`；分析动作不得流转阶段；footer 文字按钮不得加粗，主动作保持金色，辅助分析动作使用蓝灰色。
- [ ] AC-013 执行阶段动作期间当前按钮禁用并显示 Loading，重复点击不会产生重复命令。
- [ ] AC-014 命令执行成功后卡片按状态机流转；执行失败时卡片保持原阶段并在 AI 聊天展示失败原因。
- [ ] AC-015 生成阶段支持 AI 生成或导入单个 `requirement.md` / `bug.md`，导入非法文件时不执行命令。
- [ ] AC-016 完善阶段支持 AI 完善、ZIP 导入或约定多文件导入，缺失或重复文件时不执行命令。
- [ ] AC-017 已评审对象加入迭代前必须选择合法未关闭 Sprint 或合法新 Sprint；成功后显示规范化 `sprint-xxx` 标签。
- [ ] AC-017A 采集池、规划中、待评审和已评审阶段均不得显示 Sprint 标签，且 Sprint 筛选项不得包含这些未入迭代阶段卡片的历史迭代字段。
- [ ] AC-018 研发中对象可从右侧抽屉只读查看 `tasks.md` 任务进度、完成数和阻塞提示。
- [ ] AC-018A 采集池、规划中、待评审和已评审阶段不得展示“研发 x/x”进度入口，即使对象历史字段存在 `tasks.md` 或 `task_progress`。
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
- [ ] AC-PROTOTYPE-006 实现阶段必须声明 Mock/API 边界，明确哪些对象、文档、命令反馈、Sprint 列表和 tasks 进度来自真实 API 或 Mock。
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
acceptance_status: pending
accepted_at: null
accepted_by: null
source_change: update-requirement-center-card-document-actions-ai-chat
source_sprint: sprint-003
evidence: []
failed_items: []
source_event: opsx.modify
notes: 待验收；由 opsx.apply 标记，后续 archive 时回填结论。
```

