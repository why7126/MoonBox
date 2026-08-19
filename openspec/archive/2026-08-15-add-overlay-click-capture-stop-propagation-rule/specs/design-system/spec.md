## ADDED Requirements

### Requirement: 浮层外部点击捕获阶段验收

MoonBox SHALL 在声明支持点击外部关闭的弹窗、Popover、Dropdown、Date/Time Picker 或其他可交互浮层中，将 capture 阶段外部点击关闭链路纳入 UI Contract、验收标准或交互证据。

#### Scenario: 弹窗内阻止冒泡时外部点击仍可关闭

- **GIVEN** 浮层声明支持点击外部区域关闭
- **AND** 浮层内部按钮、输入、滚动容器或嵌套菜单存在 `stopPropagation` 或等价阻止冒泡逻辑
- **WHEN** 用户点击浮层内部可交互区域
- **THEN** 浮层不得被误关闭
- **WHEN** 用户点击浮层外部、遮罩或页面其他可点击区域
- **THEN** 浮层必须按 UI Contract 关闭或回到预期状态
- **AND** 验收证据必须说明外部点击关闭监听位于 capture 阶段或具备不受内部 `stopPropagation` 影响的等价机制
