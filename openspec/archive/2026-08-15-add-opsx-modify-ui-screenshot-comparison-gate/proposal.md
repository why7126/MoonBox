---
change_id: add-opsx-modify-ui-screenshot-comparison-gate
type: governance
status: applied
sprint: sprint-003
created_at: 2026-08-15 13:17:18
updated_at: 2026-08-15 13:22:00
---

# Proposal: 为 UI 型 opsx-modify 增加附件截图逐项视觉对照前置检查

## 背景

`/opsx-modify` 已要求 UI 返修遵守 prototype-driven UI Gate、1440px 视觉验收和 computed style 证据，但对用户在验收反馈中附带多张截图、标注图或前后对比图时，尚未强制先建立逐项视觉对照表。实际返修容易只处理文字反馈或单个显眼差异，遗漏附件截图中的间距、字体、状态、浮层、响应式和文案等细节。

## 目标

- UI 型 `/opsx-modify` 在返修前必须识别验收反馈中的附件截图、标注截图、原型截图和实际截图。
- 对每张附件截图建立逐项视觉对照表，覆盖期望、实际、偏差、影响元素、检查方式、处置结论和证据入口。
- 逐项对照未完成或附件缺失关键信息时，必须先要求人工补证，不得直接进入 UI 返修实现。
- 将该门禁同步到 `/opsx-modify` 技能、UI 设计规则、原型驱动 UI 验收标准和上下文预算规则。

## 非目标

- 不新增业务 UI 功能或修改 `src/` 运行时代码。
- 不引入自动视觉回归基线系统。
- 不改变 `/opsx-apply` 和 `/opsx-archive` 的现有门禁，只补强 `/opsx-modify` 的返修前置检查。

## 影响范围

```yaml
impact:
  skills: true
  rules: true
  docs: true
  scripts: false
  src: false
  api: false
  database: false
  deployment: false
```
