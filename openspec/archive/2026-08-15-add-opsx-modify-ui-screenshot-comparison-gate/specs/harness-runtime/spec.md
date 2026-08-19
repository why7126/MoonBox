## ADDED Requirements

### Requirement: UI 返修附件截图逐项视觉对照

系统 MUST 在 UI 型 `/opsx-modify` 返修前，对验收反馈中的附件截图、标注截图、原型截图或实际截图建立逐项视觉对照表，并以该表作为进入实现返修的前置检查。

#### Scenario: UI 返修前建立逐项视觉对照表

- **WHEN** `/opsx-modify` 的验收反馈涉及 UI 视觉偏差、prototype、截图附件、标注图或关键交互状态
- **THEN** Agent MUST 先识别当前反馈中的附件截图、原型截图、实际截图和历史视觉证据
- **AND** Agent MUST 建立逐项视觉对照表，记录附件/截图编号、页面/状态、对照对象、期望表现、实际表现、偏差项、检查方式、处置结论和证据入口
- **AND** Agent MUST 在完成对照前不得开始修改业务实现

#### Scenario: 附件证据不足时阻断 UI 返修

- **WHEN** 附件截图缺少页面路由、视口、主题、关键交互状态、期望截图或实际截图，导致无法确认偏差
- **THEN** Agent MUST 输出人工补证步骤
- **AND** Agent MUST 标明需要返回的字段、脱敏要求和可接受证据格式
- **AND** Agent MUST NOT 将偏差根因标记为 confirmed

#### Scenario: UI 返修后复验对照结果

- **WHEN** Agent 完成 UI 返修
- **THEN** Agent MUST 将相关旧截图标记为 stale
- **AND** Agent MUST 重新执行 1440px 或受影响视口的视觉验收
- **AND** Agent MUST 在 Change `trace.md`、`tasks.md` 验收返修记录或等价验收证据中记录对照表复验结果
