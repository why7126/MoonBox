---
requirement_id: REQ-0012-frontend-requirement-center
title: MoonBox 前台需求中心
owner: product
source: requirement.md
priority: P1
created_at: 2026-08-10 12:57:18
updated_at: 2026-08-10 12:57:18
---

# 用户故事

## US-001 统一查看需求与缺陷生命周期

作为产品负责人，我希望在一个看板中同时查看 Requirement 与 Bug 从采集到归档的完整阶段，以便快速判断当前研发治理对象的分布、阻塞与下一步动作。

验收要点：

- 看板 MUST 展示采集池、规划中、待评审、已通过、迭代规划、待开发、研发中、验收中、已完成 9 个阶段。
- Requirement 与 Bug MUST 共享阶段框架，但卡片视觉和主动作 MUST 能区分对象类型。
- 卡片 MUST 展示 ID、标题、优先级、负责人或来源、阶段产物、更新时间、阻塞状态、研发/测试进度和阶段主动作。

## US-002 按对象类型和研发维度筛选

作为项目负责人，我希望按全部、需求、Bug、负责人、优先级和 Sprint 过滤看板，以便在大量对象中聚焦当前决策范围。

验收要点：

- 工具栏 MUST 提供搜索、全部/需求/Bug 分段筛选、负责人筛选、优先级筛选和 Sprint 筛选。
- 搜索 MUST 支持 ID、标题、文档和负责人。
- 已进入迭代规划及后续阶段的对象 MUST 显示唯一 `sprint-xxx` 标签；未纳入迭代的对象不得显示空 Sprint 标签。

## US-003 按阶段触发治理命令

作为产品运营者，我希望每张卡片根据当前阶段提供正确的下一步主动作，以便减少误操作并保持 REQ/BUG、Sprint 和 OpenSpec 链路一致。

验收要点：

- 采集池对象主动作 SHOULD 指向 `req-generate` 或 `bug-generate`。
- 规划中对象主动作 SHOULD 指向 `req-complete` 或 `bug-complete`。
- 待评审对象主动作 SHOULD 指向 `req-review` 或 `bug-review`。
- 已通过对象主动作 SHOULD 指向 `sprint-propose`。
- 迭代规划对象主动作 SHOULD 指向 `req-opsx` 或 `bug-opsx`。
- 待开发和研发中对象主动作 SHOULD 指向实现进度或 `opsx-apply` / `sprint-apply`。
- 验收中对象只有在测试与人工验收完成后才允许显示完成/归档入口。

## US-004 使用 MoonBox 前台框架

作为 MoonBox 用户，我希望需求中心拥有统一的前台侧边栏、品牌、主题和空间上下文，以便在不同前台模块之间保持稳定导航体验。

验收要点：

- 页面 MUST 使用 MoonBox 前台侧边栏，包含研发总览、Chat 工作台、需求中心、Spec、任务中心、Skill Center、Agent Center、知识中心等入口。
- 需求中心 MUST 高亮当前导航项。
- 页面右侧内容区不得新增全局顶部导航栏，仅保留页面标题和局部动作栏。
- 侧边栏 MUST 支持展开/收起，并保留图标、悬停提示和当前菜单高亮。

## US-005 切换组织空间

作为多空间用户，我希望从用户菜单快速切换组织和空间，以便查看不同空间下的需求治理对象。

验收要点：

- 用户菜单入口文案 MUST 统一为“切换空间”。
- Hover“切换空间”时 MUST 在一级用户菜单右侧展示空间列表，无需点击。
- 从一级菜单移动到空间列表期间，一级用户菜单 MUST 持续显示。
- 空间列表 MUST 支持账号摘要、搜索、组织分组、空间单选、当前项勾选和创建/加入入口。
- 切换空间成功后 MUST 更新用户区空间名称、用户菜单摘要和本地最近选择。

## US-006 配置当前空间

作为空间管理员，我希望从用户菜单进入当前空间设置，以便维护空间名称、标识、描述、时区和后续成员/Agent/Skill/集成配置。

验收要点：

- 用户菜单 MUST 提供“空间设置”入口，作用于当前空间。
- 空间设置 MUST 使用居中分栏弹窗，左侧为常规、成员与权限、Agent、Skill、集成、高级设置，右侧为当前配置面板。
- 常规配置 MUST 支持空间名称、标识、描述和默认时区。
- 保存成功后 MUST 关闭弹窗并给出成功反馈；取消或关闭不得保存未确认变更。

## US-007 保持原型视觉和交互一致

作为设计验收者，我希望实现结果与目录中的 prototype.html、prototype.png 和 prototype-context.md 保持一致，以便避免实现阶段偏离已确认的产品原型。

验收要点：

- 实现 MUST 以 `prototype/prototype.html`、`prototype/prototype.png` 和 `prototype/prototype-context.md` 为视觉与交互事实源。
- 1440px 桌面视口 MUST 验收首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动、Hover 浮层和文本溢出。
- 若实现阶段调整原型意图，MUST 回填 REQ 文档和 active Change 文档后再进入归档。
