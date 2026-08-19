---
req_id: REQ-0021-markdown-editor-vditor-enhancement
status: captured
created_at: 2026-08-19 11:30:07
updated_at: 2026-08-19 11:30:07
recorded_by: product
source: explore
priority_hint: P1
parent_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
---

# 一句话

在需求中心 Markdown 文档抽屉中，为采集阶段的 `capture.md` 引入 Vditor 增强编辑体验，MVP 仅覆盖 `capture.md` 可编辑态。

# 原始描述

用户希望评估并记录 `markdown-editor-vditor-enhancement`：

- MVP 先定位为“仅 `capture.md` 增强编辑器”。
- 需要支持图片上传、表格工具、代码高亮、数学公式这类 Vditor 增强能力。

# 待澄清

- [ ] 图片上传应复用现有对象存储/上传接口，还是先使用前端本地占位或禁用生产上传。
- [ ] Vditor 默认模式采用所见即所得、即时渲染还是分屏预览。
- [ ] 数学公式、代码高亮和表格工具的安全渲染策略、样式隔离和深浅主题适配边界。
- [ ] `capture.md` 之外的 Markdown 文档是否明确保持只读纯文本预览，不纳入本 MVP。

# 探索结论

当前倾向将 Vditor 作为需求中心 `capture.md` 的增强编辑器，而不是全量替换所有 Markdown 文档查看能力。该范围能改善需求采集体验，同时控制依赖体积、样式适配、安全渲染和验收影响面。
