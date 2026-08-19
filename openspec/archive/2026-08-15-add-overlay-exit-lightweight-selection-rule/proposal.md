---
change_id: add-overlay-exit-lightweight-selection-rule
type: add
status: proposed
source_requirement: null
sprint: sprint-003
created_at: 2026-08-15 15:24:58
updated_at: 2026-08-15 15:24:58
---

# Proposal: 沉淀浮层退出路径与轻量选择确认规则

## 背景

近期 UI 验收中出现轻量时间选择浮层为了提供退出路径而引入“取消 / 确定”按钮，导致交互显得偏重。该问题暴露出治理规则缺口：浮层必须有明确退出路径，但轻量选择场景不应默认增加额外确认动作。

## 目标

- 在 UI 设计规则中明确浮层交互必须提供用户可理解的退出路径。
- 区分轻量选择与高成本编辑/提交场景，避免把“可退出”误解为必须增加确认按钮。
- 为后续 UI Contract、原型验收和返修复核提供统一判断口径。

## 非目标

- 不修改 Web、管理后台或后端业务实现。
- 不新增 UI 组件库能力或自动化校验脚本。
- 不改变现有已归档 Change 的验收结论。

## 影响范围

```yaml
impact:
  rules: true
  docs: true
  openspec: true
  scripts: false
  src: false
  api: false
  database: false
  deployment: false
  security: false
```
