# Acceptance

## AC-GOV-001 UI Contract

- 带 `prototype/` 的 UI Change 必须在 Change `design.md` 写入 UI Contract。
- UI Contract 必须覆盖事实源、页面入口、信息架构、视觉 token、交互状态、图标文案、Mock/API 边界、权限规则和一致性参照。

## AC-GOV-002 Skeleton 与视觉证据

- 带 prototype 的 UI Change 必须先完成 Skeleton 首轮确认。
- UI 任务完成前必须记录 1440px 默认首屏和关键交互截图或等价证据。
- UI 返修后相关旧证据必须视为 stale 并重新取证。

## AC-GOV-003 Computed Style

- 对原型敏感或已发生验收反馈的视觉点，必须记录 computed style 或等价断言。
- 验收记录必须能定位页面、选择器、视口和结论。

## AC-GOV-004 Mock/API 边界

- UI Change 必须声明 Mock 数据和真实 API 的边界。
- 未接入真实 API 的区域不得被表述为已完成真实数据集成。

## AC-GOV-005 前后台一致性

- 前后台相同功能必须使用一致文案和图标。
- 跨前后台对齐时必须检查品牌区、菜单分组、导航密度、active 态、折叠按钮、用户菜单、浮层层级、字体 token、图标尺寸和危险色。

