---
purpose: OpenSpec Change 设计
content: 浮层外部点击 capture 阶段 stopPropagation 覆盖规则的治理设计
created_at: 2026-08-15 16:41:16
updated_at: 2026-08-15 16:41:16
owner: MoonBox 产品团队
---

# 治理设计

## 规则落点

- `rules/ui-design.md`：在“浮层交互”和 Prototype-driven UI Gate 中加入 capture 阶段外部点击覆盖要求。
- `docs/standards/prototype-ui-acceptance.md`：在 UI Contract、视觉截图门禁和弹窗/浮层场景中加入 `stopPropagation` 对照验收。
- `openspec/changes/.../specs/design-system/spec.md`：新增 Design System delta 场景，保证归档后能合并到正式规格。

## 验收语义

当 UI Contract 或验收标准声明浮层支持点击外部关闭时，验收必须覆盖：

- 关闭监听位于 capture 阶段或有等价机制，不依赖会被浮层内部冒泡阻断影响的单一路径。
- 浮层内部按钮、输入、滚动容器或嵌套菜单调用 `stopPropagation` 时，内部点击不误关闭浮层。
- 用户点击浮层外部、遮罩或页面其他可点击区域时，浮层仍能关闭，并且焦点、已选值或输入草稿处理符合 UI Contract。

## 文档同步

本次为纯治理 Change，不触碰 API、数据库、业务 UI 实现、部署或客户端生成。
