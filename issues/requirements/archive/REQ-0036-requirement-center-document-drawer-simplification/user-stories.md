---
requirement_id: REQ-0036-requirement-center-document-drawer-simplification
title: 需求中心文档抽屉简化与 Change 属性模块移除 - 用户故事
created_at: 2026-09-15 23:11:38
updated_at: 2026-09-15 23:11:38
owner: product
source: requirement.md
---

# 需求中心文档抽屉简化与 Change 属性模块移除 - 用户故事

## US-001 阅读当前文档

作为需求中心用户，我希望打开 REQ、BUG 或独立 Change 文档时，抽屉顶部只显示当前文档属性和正文，以便我快速进入阅读，不被 Change 追溯面板打断。

验收要点：

- 文档抽屉不再显示“Change 追溯属性”模块。
- 文档属性模块位于正文之前，展开、收起和滚动体验正常。
- 删除模块后没有空白占位、残留边框或贴边文本。

## US-002 追溯关联 Change 文档

作为验收人员，我希望即使抽屉不再展示 Change 属性模块，也仍能从需求中心找到关联 Change 的 proposal、design、tasks 和 trace，以便核对实现依据。

验收要点：

- 单 Change 关联仍有清晰文档入口。
- 多 Change 关联不默认选择第一个 Change。
- Change trace 与 Issue trace 不混淆。

## US-003 验证权限边界

作为空间管理员，我希望删除 UI 模块不会改变既有授权和只读策略，以便无权用户无法通过文档 URL、搜索或入口探测受限 Change 内容。

验收要点：

- 无权对象、只读成员、冻结空间和跨项目同 ID 场景均保持原有访问限制。
- 缺失文档、加载失败和草稿保护行为不回归。

## US-004 实现与验收人员回归 UI

作为研发和验收人员，我希望有明确的 UI 验收焦点，以便确认模块删除后的抽屉布局、间距、主题和响应式表现没有视觉退化。

验收要点：

- 覆盖 1440px 与窄视口。
- 覆盖深浅主题、长标题、长 ID 和长正文。
- 对关键样式保留截图或 computed style 证据。
