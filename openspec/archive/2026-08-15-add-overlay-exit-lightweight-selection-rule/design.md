---
change_id: add-overlay-exit-lightweight-selection-rule
status: proposed
created_at: 2026-08-15 15:24:58
updated_at: 2026-08-15 15:24:58
---

# Design: 浮层退出路径与轻量选择确认规则

## 规则口径

浮层交互拆成两个判断：

1. 是否有明确退出路径：用户必须知道如何离开浮层，且退出后状态结果可预测。
2. 是否需要额外确认：只有存在高成本副作用、自由输入、多步编辑、批量选择、异步提交或校验恢复时，才使用确认按钮。

轻量选择的默认模式为“选择即应用并关闭”或“点击外部关闭并保留当前值”。该模式适用于日期快捷项、展示筛选、空间/菜单切换、单选列表等可随时重选、低成本、无不可逆副作用的交互。

## 文档同步

- `rules/ui-design.md` 新增“浮层交互”章节。
- `docs/spec-logs/CHANGELOG.md` 追加治理索引。
- `docs/spec-logs/YYYYMMDDhhmmss-governance-overlay-exit-lightweight-selection.md` 记录本次规范迭代。

## 验收判断

- UI 验收时检查浮层是否至少存在一种明确退出路径。
- 对轻量选择浮层，若引入“取消 / 确定”等确认按钮，必须有高成本副作用或编辑提交原因。
- 若选择行为会提交、删除、授权或触发不可逆状态变化，则仍需要显式取消/确认或等价保护。
