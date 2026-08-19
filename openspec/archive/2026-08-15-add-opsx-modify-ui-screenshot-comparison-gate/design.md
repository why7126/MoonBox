---
change_id: add-opsx-modify-ui-screenshot-comparison-gate
created_at: 2026-08-15 13:17:18
updated_at: 2026-08-15 13:17:18
---

# Design: UI 返修附件截图逐项视觉对照门禁

## 设计决策

- 将门禁放在 `/opsx-modify` Workflow 的 Clarify Feedback 阶段，早于 Modify Implementation。
- 仅当返修反馈涉及 UI、visual、prototype、截图附件、标注图、视觉差异或交互状态时触发。
- 对照表可以写入 Change `tasks.md` 的 `## 验收返修记录`、Change `trace.md`、验收记录或用户可见执行摘要，但必须可追溯。
- 对照表不要求保存原始隐私截图；截图证据路径或说明必须脱敏，避免写入真实客户数据、Token、Cookie、系统用户名或用户主目录。

## 对照表字段

| 字段 | 说明 |
|---|---|
| 附件/截图编号 | 用户附件、原型截图、实际截图或标注截图的可追溯编号 |
| 页面/状态 | 路由、视口、主题、交互状态或弹窗/浮层状态 |
| 对照对象 | 原型、验收截图、标注区域、现实现象或历史视觉证据 |
| 期望表现 | 用户附件或原型表达的目标视觉/交互结果 |
| 实际表现 | 当前实现或复现截图中的表现 |
| 偏差项 | 间距、字号、颜色、对齐、层级、溢出、文案、图标、状态等 |
| 检查方式 | 视觉对照、Playwright 截图、computed style、DOM 选择器、人工补证 |
| 处置结论 | 本次修复、无需修改并说明理由、超出范围、证据不足 |
| 证据入口 | 截图、日志、trace、style JSON 或脱敏说明的路径/摘要 |

## 阻断规则

- 缺少期望截图、实际截图、页面路由、视口或关键交互状态，导致无法判断偏差时，必须输出人工补证步骤。
- 对照表发现偏差超出当前 Change 边界时，必须停止业务返修并建议 `/req-capture`、`/bug-capture` 或新 OpenSpec Change。
- UI 返修后旧截图立即 stale，必须重新取证并在对照表或 trace 中记录复验结果。
