---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
acceptance_status: pending
created_at: 2026-08-19 11:36:10
updated_at: 2026-08-19 12:23:54
owner: product
source: requirement.md
---

# 验收标准

## 功能 AC

- [ ] AC-001 仅采集阶段、文档名为 `capture.md`、且具备编辑权限时启用 Vditor 增强编辑器。
- [ ] AC-002 `trace.md`、非采集阶段 Markdown、不可编辑文档和无权限文档保持只读，不因 Vditor 扩大编辑权限。
- [ ] AC-003 Vditor 保存内容必须是 Markdown 字符串，服务端不得持久化富文本私有格式。
- [ ] AC-004 用户可以查看或编辑原始 Markdown 内容，所见即所得或即时渲染模式不得掩盖最终保存格式。
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

## Readiness

```yaml
readiness: Ready
knowledge_base_gate: Pass
prototype_gate: Partially Ready
reason: 文档六件套已补齐，横切 AC 已嵌入；prototype 为文本拆解与验收焦点，截图将在实现阶段产出。
```


## 验收结果回填

```yaml
acceptance_status: pending
accepted_at: null
accepted_by: null
source_change: update-markdown-editor-vditor-enhancement
source_sprint: sprint-003
evidence: []
failed_items: []
source_event: opsx.apply
notes: 待验收；由 opsx.apply 标记，后续 archive 时回填结论。
```

