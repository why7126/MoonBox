---
requirement_id: REQ-0008-prototype-driven-page-acceptance-gate
prototype: web-governance
status: strategy
created_at: 2026-08-08 21:51:55
updated_at: 2026-08-08 21:51:55
---

# Prototype Strategy

本 REQ 是原型驱动页面开发验收门禁，不交付具体业务页面，因此不生成独立 `prototype.html` 或 `prototype.png`。

后续 Web 前台或管理后台页面若存在原型资产，应按本 REQ 的门禁顺序处理：

```text
prototype.html / prototype.png
  -> 原型拆解
  -> UI Skeleton
  -> 1440px 截图验收
  -> 关键 DOM/CSS 尺寸检查
  -> 业务逻辑联调
```

## 适用端

- Web 前台：适用。
- 管理后台：适用。
- 小程序、移动端、桌面端：首期不适用。

## 原型优先级

- `prototype.html`：优先表达页面结构、层级、组件关系、交互意图。
- `prototype.png`：优先表达视觉密度、关键样式和截图对照。
- 若两者冲突，后续页面 REQ 的 `prototype/context.md`、acceptance 或 OpenSpec design 必须明确优先级。

## 证据要求

- 原型拆解摘要。
- UI Skeleton 验收结论。
- 1440px 截图路径。
- 关键 DOM/CSS 检查清单。
- 是否允许进入业务逻辑联调。
