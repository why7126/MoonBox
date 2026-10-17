## ADDED Requirements

### Requirement: 产品运行态证据的浏览器选择

Agent 需要产品运行态证据时，MUST 优先检查并复用 Codex 侧边浏览器中与当前任务相关的目标产品标签页；若不可用或不能取得本次所需证据，MUST 尝试其他已提供的浏览器或等价自动化工具，Firefox 可作为后备。Agent MUST 区分旧页面展示与当前服务连通性，并记录实际浏览器、环境、视口、操作及脱敏结果。

#### Scenario: 侧边浏览器可满足取证

- **WHEN** Codex 侧边浏览器可访问目标产品并取得所需证据
- **THEN** Agent 使用该入口完成取证，不占用用户 Firefox 会话

#### Scenario: 侧边浏览器无法满足取证

- **WHEN** 侧边浏览器不可用或缺少所需证据能力
- **THEN** Agent 尝试其他可用入口，并记录失败与替代路径
