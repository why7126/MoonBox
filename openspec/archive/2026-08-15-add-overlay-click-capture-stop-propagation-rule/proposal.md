---
purpose: OpenSpec Change 提案
content: 沉淀浮层外部点击 capture 阶段覆盖弹窗内 stopPropagation 场景的 UI 交互验收规则
created_at: 2026-08-15 16:41:16
updated_at: 2026-08-15 16:41:16
owner: MoonBox 产品团队
---

# 沉淀浮层外部点击 capture 阶段 stopPropagation 覆盖规则

## 背景

既有 UI 浮层规则已要求浮层具备明确退出路径，并要求 click outside 等关键交互进入视觉与交互验收。但外部点击关闭常依赖全局捕获阶段监听；若只在冒泡阶段验证，弹窗内部 `stopPropagation` 可能遮蔽外部点击链路，导致用户点击浮层外部无法关闭弹窗或二级浮层。

## 目标

- 明确浮层外部点击关闭验收必须覆盖 capture 阶段监听。
- 要求验收覆盖“弹窗内部元素调用 `stopPropagation` 后，外部点击仍可关闭目标浮层”的场景。
- 将该规则同步到 UI 规则、原型驱动 UI 验收标准、OpenSpec delta、Sprint scope 和治理日志。

## 非目标

- 不修改业务 `src/` 实现。
- 不调整现有浮层组件 API 或事件实现。
- 不新增自动化测试脚本。

## 影响范围

- `rules/ui-design.md`
- `docs/standards/prototype-ui-acceptance.md`
- `openspec/changes/add-overlay-click-capture-stop-propagation-rule/`
- `iterations/change/sprint-003/`
- `docs/spec-logs/`
