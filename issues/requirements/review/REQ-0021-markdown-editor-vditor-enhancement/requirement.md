---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
title: Markdown 文档 Vditor 增强编辑器
terminal: web-catalog
version: v1
status: in_sprint
owner: product
source: capture.md
priority: P1
parent_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
created_at: 2026-08-19 11:32:02
updated_at: 2026-08-19 12:04:14
---

# Markdown 文档 Vditor 增强编辑器

## 背景

REQ-0020 已为需求中心 Markdown 文档建立右侧抽屉、预览、编辑、保存和未保存关闭确认能力。当前实现以原始文本编辑为主，适合轻量治理文档维护，但对产品、运营或非工程背景用户并不友好：表格、图片、代码块、公式等 Markdown 内容需要手写语法，编辑时也缺少结构化工具与即时反馈。

本需求希望在不扩大文档编辑权限边界的前提下，引入开源工具 Vditor 作为 `capture.md` 的增强编辑器。MVP 仅覆盖采集阶段的 `capture.md` 可编辑态，避免一次性替换所有 Markdown 文档查看和编辑能力，降低包体积、样式隔离、安全渲染、上传链路和视觉验收风险。

## 目标用户

- 产品负责人：需要在需求采集阶段快速补充图文、表格、代码片段和公式，降低 Markdown 语法负担。
- 项目负责人：需要在需求中心内形成更可读的 capture 初稿，为后续生成 PRD、验收标准和 OpenSpec Change 提供更完整上下文。
- 研发协作者：需要查看含代码块、表格和技术说明的 capture 内容，并保持原始 Markdown 可追溯。

## 范围

### 包含

- 在需求中心 Markdown 抽屉中，仅对采集阶段可编辑的 `capture.md` 启用 Vditor 增强编辑器。
- 支持 Vditor 常用 Markdown 编辑能力，包括图片上传入口、表格工具、代码高亮和数学公式。
- 保持 `capture.md` 的受控保存流程、未保存关闭确认、保存成功回显和异常提示。
- 保持服务端持久化内容为 Markdown 文本，不引入富文本专有数据格式。
- 提供源码可追溯能力，确保用户能查看或编辑原始 Markdown 内容。
- 适配 MoonBox 深浅主题、右侧抽屉宽度、移动端全屏抽屉和既有视觉基调。
- 对图片上传、HTML 渲染、公式渲染和代码高亮建立安全边界与失败分支。

### 不包含

- 不在本需求内将 `trace.md`、`requirement.md`、`acceptance.md` 或非采集阶段 Markdown 文档改为可编辑。
- 不在本需求内全量替换只读 Markdown 文档预览能力。
- 不在本需求内改变 REQ、BUG、Sprint 或 OpenSpec 的状态机、权限门禁和 Workflow Sync 语义。
- 不在本需求内新增多人协同编辑、评论批注、版本 diff、自动保存或离线编辑。
- 不在本需求内开放本机文件路径、原始对象存储凭据、未脱敏日志、密钥、访问令牌或内部异常堆栈给前端。
- 不在本需求内绕过现有对象存储、安全扫描、上传大小限制和文件类型校验。

## 功能要求

### FR-001 `capture.md` 增强编辑器启用范围

需求中心 Markdown 抽屉 MUST 仅在对象处于采集阶段、文档名为 `capture.md` 且当前用户具备编辑权限时启用 Vditor 增强编辑器。

`trace.md`、非采集阶段文档、不可编辑文档和无权限文档 MUST 保持只读展示或既有受限编辑行为，不得因引入 Vditor 扩大编辑面。

### FR-002 编辑模式与源码追溯

系统 MUST 提供用户可理解的编辑模式，支持通过 Vditor 编辑 Markdown 内容，并保持保存内容为 Markdown 字符串。

系统 SHOULD 提供源码查看或源码编辑能力，确保用户可以确认最终写入 `capture.md` 的原始 Markdown 内容。若采用所见即所得或即时渲染模式，仍不得让用户误以为保存的是 HTML 或富文本私有格式。

### FR-003 图片上传

Vditor 编辑器 SHOULD 支持图片上传入口。上传链路 MUST 复用项目认可的对象存储或上传接口，并遵守文件大小、扩展名、MIME 类型、权限、鉴权和错误提示规则。

图片上传成功后，系统 MUST 将可访问的图片 URL 或约定 Markdown 图片语法写入 `capture.md` 内容。上传失败、文件类型不符、权限不足、网络异常或对象存储不可用时，系统 MUST 在编辑器或抽屉内展示可理解错误，不得静默丢失用户输入。

若后续实现阶段暂未具备生产可用上传接口，MVP MUST 明确禁用图片上传或使用受控占位策略，不得将本地绝对路径、临时文件路径或私有对象存储地址写入 Markdown。

### FR-004 表格工具

Vditor 编辑器 MUST 支持表格插入、编辑和 Markdown 表格语法保存。表格内容在抽屉宽度受限时 MUST 可横向滚动或自适应换行，不得撑破右侧抽屉或遮挡保存动作。

### FR-005 代码高亮

Vditor 编辑器 MUST 支持 Markdown 代码块编辑和预览高亮。代码块中的长行 MUST 可滚动或换行处理，不得造成抽屉布局溢出。

代码内容 MUST 按普通 Markdown 文本保存，不得执行代码，不得注入脚本，不得暴露内部异常堆栈或敏感运行时信息。

### FR-006 数学公式

Vditor 编辑器 MUST 支持数学公式输入与预览。公式渲染 SHOULD 在深浅主题中保持可读，并在移动端抽屉内不溢出。

公式渲染失败时，系统 SHOULD 保留原始 Markdown/LaTeX 文本，避免用户内容丢失。

### FR-007 保存、关闭与脏状态保护

Vditor 编辑器 MUST 继承当前 `capture.md` 的保存行为：用户修改内容后展示未保存状态，保存成功后回到预览或已同步状态，并回显服务端返回的最新内容。

当 `capture.md` 存在未保存修改时，关闭抽屉、切换文档或触发会丢失编辑内容的动作前 MUST 进行确认。保存中 MUST 禁用重复提交，并展示 Loading 状态。

### FR-008 安全渲染与内容边界

系统 MUST 对 Vditor 产生或渲染的 Markdown 内容建立安全边界，防止不受控 HTML、脚本、事件属性、危险链接或对象存储私有地址进入前端可执行上下文。

若允许 Markdown 中包含 HTML，后续设计 MUST 明确白名单、清洗策略和验收方式；若不允许，系统 MUST 在编辑、预览或保存链路中保持一致限制。

### FR-009 主题、布局与抽屉适配

Vditor 编辑器 MUST 适配 MoonBox 现有深浅主题、金色强调、近直角、细线和克制编辑排版感。工具栏、弹窗、输入区、预览区、代码块、公式和上传反馈在深色与浅色主题下均 MUST 可读。

桌面端 MUST 适配既有右侧抽屉宽度范围；移动端 SHOULD 使用全屏宽度。编辑器工具栏、保存动作、错误提示和长文内容不得互相遮挡。

### FR-010 加载失败与降级

Vditor 资源加载失败、初始化失败或浏览器能力不足时，系统 SHOULD 提供可用降级路径，至少允许用户通过原始 Markdown 文本方式继续编辑 `capture.md`，并展示明确提示。

降级路径不得跳过保存权限、脏状态确认和安全校验。

## UI 约束

- 编辑器必须嵌入既有右侧 Markdown 抽屉，不新增独立页面或覆盖整个需求中心看板。
- 工具栏应保持紧凑，优先展示图片、表格、代码、公式、预览/源码切换和保存相关能力，避免把低频功能挤满抽屉。
- Vditor 默认样式必须经过 MoonBox 主题覆写，不得出现突兀的蓝紫科技风、大圆角卡片、厚重阴影或与现有抽屉冲突的弹层层级。
- 保存按钮、关闭按钮、抽屉拖拽和编辑器内部点击不得互相误触发。
- 长文件名、长表格、长代码行、长公式和图片预览必须具备溢出处理。

## 关联需求

- REQ-0020-requirement-center-card-document-actions-ai-chat：本需求承接需求中心 Markdown 抽屉、`capture.md` 可编辑态和文档保存链路。
- REQ-0012-frontend-requirement-center：本需求延续前台需求中心页面骨架、9 阶段看板和视觉体系。
- REQ-0013-requirement-center-real-data-integration：本需求依赖真实数据接入能力读取和保存 `capture.md`。
- REQ-0008-prototype-driven-page-acceptance-gate：涉及 UI 变更时，后续实现需遵守原型驱动页面验收门禁。

## 状态块

```yaml
status: in_sprint
generated_at: 2026-08-19 11:32:02
completed_at: 2026-08-19 11:36:10
reviewed_at: 2026-08-19 11:41:07
approved_at: 2026-08-19 11:41:07
source_material:
  - capture.md
  - related_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
next: /opsx-apply REQ-0021-markdown-editor-vditor-enhancement
iteration: sprint-003
openspec_change: update-markdown-editor-vditor-enhancement
```
