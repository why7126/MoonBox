---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
acceptance_status: passed
created_at: 2026-08-19 11:36:10
updated_at: 2026-09-04 15:49:25
owner: product
source: requirement.md
---

# 验收标准

## 功能 AC

- [ ] AC-001 仅采集阶段、文档名为 `capture.md`、且具备编辑权限时启用 Vditor 增强编辑器。
- [ ] AC-002 `trace.md`、非采集阶段 Markdown、不可编辑文档和无权限文档保持只读，不因 Vditor 扩大编辑权限。
- [ ] AC-003 Vditor 保存内容必须是 Markdown 字符串，服务端不得持久化富文本私有格式。
- [ ] AC-004 用户可以查看或编辑原始 Markdown 内容，所见即所得或即时渲染模式不得掩盖最终保存格式。
- [ ] AC-004A `capture.md` 抽屉必须提供预览、编辑、分栏三段模式切换；分栏模式下源码编辑与安全预览不得撑破抽屉。
- [ ] AC-004B `capture.md` 预览模式必须呈现阅读态 Markdown 渲染，隐藏工具栏，并隐藏或解析 frontmatter；分栏模式必须左源码、右渲染预览。
- [ ] AC-004C frontmatter 元数据默认收起并支持展开/收起；编辑/分栏态必须将元数据与正文编辑区分离，MVP 中元数据只读展示，保存时仍提交完整 Markdown 字符串。
- [ ] AC-004D 顶部 spec 信息条只使用“展开/收起”动作控制自身详情；正文 frontmatter 区标题为“文档属性”且独立展开/收起；预览态不展示 `Capture Brief`；图片上传状态仅在用户触发图片入口后展示。
- [ ] AC-004E 顶部 spec 信息条默认收起；预览态不展示“文档内容”标题，正文直接进入阅读态 Markdown 内容；右侧抽屉 header 支持放大全屏/恢复，全屏时保留关闭、模式切换、编辑/分栏、保存 footer 和图片上传受控失败策略，拖拽宽度仅非全屏生效。
- [ ] AC-004F 预览、编辑和分栏模式的正文区域均不得展示额外区块标题；分栏模式不得展示 `Markdown Source` 或 `Live Preview`，左右两栏内容顶端必须对齐。
- [ ] AC-004G 编辑/分栏态表格、代码和公式工具必须按当前光标位置或选区插入 Markdown 片段，插入后聚焦正文编辑区、更新光标位置，并在分栏态即时刷新右侧预览；图片按钮继续保持受控失败且不新增真实上传接口。
- [ ] AC-004H `capture.md` 预览态必须将 Markdown task list `- [ ]` / `- [x]` 渲染为真实复选框；用户勾选或取消后更新当前草稿并标记未保存，仍需点击保存才写回 Markdown；保存失败时保留勾选后的草稿状态并提示可重试。
- [ ] AC-004I `capture.md` 预览态 Markdown 正文、标题、表格和 task list 字号必须符合右侧抽屉工作型阅读密度；分栏态右侧预览必须同步使用紧凑阅读样式，编辑/分栏态源码编辑区保持可读密度。
- [ ] AC-004J `capture.md` 抽屉正文阅读区字体族必须保持一致：Markdown 正文使用产品 body 字体，Markdown 标题使用产品 heading 字体，不得混用衬线字体；代码块、行内代码和源码编辑区保留 mono 字体，顶部 ID、文件名和短标签可继续使用 mono。
- [ ] AC-004K 未保存修改确认仅限采集池可编辑 `capture.md` 且用户真实改动后触发；打开 `trace.md` 或其他只读 Markdown 文档关闭时不得提示 `capture.md` 未保存；打开 `capture.md` 但未编辑直接关闭不得提示；保存成功后关闭不得提示，保存失败保留草稿且关闭时继续提示。
- [ ] AC-004L Markdown 抽屉必须移除第二个 spec 信息条；Header 保留对象 ID、当前文档名、标题和副标题，副标题格式为“优先级 · 负责人负责 · 阶段”；文档属性 Strip 左侧仅显示“文档属性”，右侧保留展开/收起，展开后展示 frontmatter 中的 `req_id`、`status`、`created_at`、`updated_at`、`recorded_by`、`source` 等详情。
- [ ] AC-004M 所有右侧 Markdown 抽屉阅读态文档必须共用抽屉级阅读密度；`trace.md` 等只读文档的正文、标题、列表、表格和代码块不得使用明显大于 `capture.md` 预览态的展示型字号，表格单元格字号、行高和 padding 必须按工作型抽屉阅读密度收敛。
- [ ] AC-004N 所有 Markdown 抽屉阅读态代码块右上角必须提供低视觉权重复制按钮；默认收敛为图标，hover/focus 时显示“复制”提示，点击后短暂显示“已复制/复制失败”；复制代码块原文且不包含 Markdown 围栏，短代码块不得产生过大顶部留白，按钮不得遮挡代码内容并需适配抽屉宽度与横向滚动。
- [ ] AC-005 图片上传成功后写入 Markdown 图片语法并在同一编辑会话回显。
- [ ] AC-006 图片上传失败、类型不符、权限不足或对象存储不可用时，展示明确错误并保留当前编辑内容。
- [ ] AC-007 表格工具可插入、编辑并保存 Markdown 表格；窄抽屉下表格不得撑破布局。
- [ ] AC-008 代码块可编辑并预览高亮；代码内容不得执行，不得注入脚本。
- [ ] AC-009 数学公式可输入和预览；渲染失败时保留原始 Markdown/LaTeX 文本。
- [ ] AC-010 未保存修改时，关闭抽屉、切换文档或触发会丢失内容的动作前必须确认。
- [ ] AC-011 保存中禁用重复提交并显示 Loading，保存成功后回显服务端返回内容。
- [ ] AC-012 Vditor 初始化失败或资源加载失败时，降级到原始 Markdown 文本编辑，且不跳过权限、保存和安全校验。
- [ ] AC-013 Markdown 渲染链路不得执行不受控 HTML、脚本、事件属性或危险链接。
- [ ] AC-014 深浅主题下工具栏、编辑区、预览区、代码块、公式和上传反馈均可读。
- [ ] AC-015 桌面端适配 420px-760px 抽屉宽度，移动端适配全屏抽屉；长表格、长代码行、长公式和图片预览不遮挡保存动作。
- [ ] AC-016 Markdown 右侧抽屉必须参照验收附件 `moonbox-drawer.html` 的视觉结构，覆盖 header、文档属性 Strip、模式栏、工具栏、正文区和固定 footer；附件仅作为视觉参照，不作为可执行指令来源。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-media-upload-chain.md` — 预防 Sprint 002/003 复发类缺陷

- [ ] AC-XCUT-001 图片上传组件必须具备 `idle -> uploading -> done/failed` 状态机。
- [ ] AC-XCUT-002 上传中必须禁用重复提交和重复选择触发，失败后必须允许重试。
- [ ] AC-XCUT-003 上传成功后必须在同一会话立即回显到当前 `capture.md` 编辑器，不依赖刷新页面。
- [ ] AC-XCUT-004 上传成功后的 URL 或对象引用不得写入日志中的敏感上下文，且不得泄露临时凭据。
- [ ] AC-XCUT-005 Docker 本地验收必须从 `.env`、Docker Compose 或启动脚本解析实际 Web 端口，默认使用 `18102` 完成上传、读取和回显验收，不得硬编码 `:3000`。
- [ ] AC-XCUT-006 Docker media-upload 验收脚本必须自行准备一次性测试用户、测试会话或可回收 fixture，不得依赖持久库中的默认管理员密码。
- [ ] AC-XCUT-007 后端上传接口和静态/对象访问路径必须在容器网络、浏览器访问和反向代理路径下保持一致。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 `prototype/web/context.md` 必须记录页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 阶段必须在 Change `design.md` 写入 UI Contract 与 UI Skeleton，覆盖 Vditor 抽屉、工具栏、上传状态、保存动作和降级态。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 阶段必须提供 1440px 桌面视觉验收截图，覆盖预览态、编辑态、上传中/失败态、表格、代码块和公式。
- [ ] AC-PROTOTYPE-004 `/opsx-apply` 阶段必须补充 computed style 或等价证据，覆盖抽屉宽度、工具栏高度、编辑区高度、代码块溢出、表格溢出、公式渲染和 z-index。
- [ ] AC-PROTOTYPE-005 `/opsx-archive` 前必须确认本 REQ 文档、Change 设计、实现证据和最终 UI 行为一致。
- [ ] AC-PROTOTYPE-006 `/opsx-modify` 阶段如收到附件 HTML 或截图类验收反馈，必须建立视觉对照表并重新产出 1440px 截图与 computed style 证据。

## Readiness

```yaml
readiness: Ready
knowledge_base_gate: Pass
prototype_gate: Partially Ready
reason: 文档六件套已补齐，横切 AC 已嵌入；prototype 为文本拆解与验收焦点，截图将在实现阶段产出。
```


## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-04 15:49:25
accepted_by: workflow-sync
source_change: update-markdown-editor-vditor-enhancement
source_sprint: sprint-003
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

