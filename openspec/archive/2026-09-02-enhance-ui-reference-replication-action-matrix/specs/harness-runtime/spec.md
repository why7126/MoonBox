## ADDED Requirements

### Requirement: UI 参考稿复刻动作按钮矩阵

系统 MUST 在参考稿复刻类 UI Change 的实现前，为会触发弹窗、抽屉、Popover、确认框、Action Modal、AI 面板或内联展开区域的动作按钮建立矩阵，并以该矩阵驱动组件族实现和验收。

#### Scenario: 实现前建立动作按钮矩阵

- **WHEN** UI Change 引用附件 HTML、截图、标注图、既有页面或参考稿
- **AND** 复刻范围包含动作按钮、卡片 footer、FAB、工具栏动作或阶段动作
- **THEN** Agent MUST 在实现前建立“动作按钮 → modal 类型 → selector → 状态 → 验收证据”矩阵
- **AND** 矩阵 MUST 记录参考 selector、目标 selector、组件族、交互状态、验收证据和处置结论
- **AND** 缺少矩阵时不得将相关 UI 实现任务标记完成

#### Scenario: 同一动作族一次性实现组件族

- **WHEN** 多个动作按钮共享相同 modal 类型、视觉等级、状态模型、关闭路径或提交反馈
- **THEN** Agent MUST 将它们归入同一动作族
- **AND** Agent MUST 一次性设计、实现和验收按钮与 modal 组件族
- **AND** Agent MUST 覆盖 default、hover、focus、active、disabled、loading、open、submitted、error 和权限隐藏等适用状态
- **AND** Agent MUST NOT 将同一动作族拆成逐按钮问答返修，除非矩阵记录明确例外原因

#### Scenario: 返修反馈先回补动作族矩阵

- **WHEN** UI 返修反馈指出某个按钮、modal、Action Modal 或 AI 面板不符合参考稿
- **THEN** Agent MUST 先判断该反馈是否属于更大的动作族
- **AND** 若属于同一动作族，Agent MUST 更新矩阵中相关按钮、modal 类型、selector、状态和证据入口
- **AND** Agent MUST 基于更新后的组件族合同返修，而不是只对单个按钮做孤立修改

#### Scenario: 归档前复核动作按钮矩阵

- **WHEN** 参考稿复刻类 UI Change 准备归档
- **THEN** Agent MUST 复核动作按钮矩阵、selector 映射、computed style 采样、截图证据、非目标保留和最终实现记录一致
- **AND** 若矩阵缺少已实现动作或证据 stale，归档必须阻断
