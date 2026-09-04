## ADDED Requirements

### Requirement: Markdown 文档人工编辑权限矩阵

系统 MUST 在需求中心按治理阶段、对象类型、文档名和文档路径类别计算 Markdown 文档的人工编辑能力，避免单一 `editable` 布尔值或前端硬编码决定编辑入口。

#### Scenario: 采集池只允许 capture

- **WHEN** Requirement 或 Bug 对象处于采集池阶段
- **THEN** 仅 `capture.md` 的 `human_editable` MUST 为 true
- **AND** `trace.md` 的 `human_editable` MUST 为 false

#### Scenario: 规划中只允许主文档

- **WHEN** Requirement 对象处于规划中阶段
- **THEN** 仅 `requirement.md` 的 `human_editable` MUST 为 true
- **AND** `bug.md` MUST NOT 因矩阵存在而对 Requirement 开放
- **WHEN** Bug 对象处于规划中阶段
- **THEN** 仅 `bug.md` 的 `human_editable` MUST 为 true
- **AND** `requirement.md` MUST NOT 因矩阵存在而对 Bug 开放

#### Scenario: 待评审允许完善类文档

- **WHEN** Requirement 对象处于待评审阶段
- **THEN** `user-stories.md`、`business-flow.md`、`acceptance.md` 和 `requirement.md` 的 `human_editable` MUST 为 true
- **AND** 其他文档 MUST 保持人工只读
- **WHEN** Bug 对象处于待评审阶段
- **THEN** `root-cause.md`、`workaround.md`、`acceptance.md` 和 `bug.md` 的 `human_editable` MUST 为 true
- **AND** 其他文档 MUST 保持人工只读

#### Scenario: 已评审允许评审材料编辑

- **WHEN** Requirement 或 Bug 对象处于已评审阶段
- **THEN** 待评审阶段可编辑文档和 `review.md` 的 `human_editable` MUST 为 true
- **AND** `trace.md` MUST 保持人工只读

#### Scenario: 受控阶段关闭全文编辑

- **WHEN** 对象处于迭代规划、研发中或已完成阶段
- **THEN** 所有 Markdown 文档的 `human_editable` MUST 为 false
- **AND** 前端 MUST 展示阅读态和受限原因

### Requirement: Markdown 抽屉能力驱动渲染

系统 MUST 根据后端返回的文档能力对象渲染 Markdown 抽屉，不得继续以 `capture.md` 或单一阶段判断硬编码编辑体验。

#### Scenario: 完整编辑态

- **WHEN** 文档能力中 `human_editable` 为 true
- **THEN** 前端 MUST 显示完整 Markdown 编辑、分栏、保存和脏状态保护
- **AND** 保存成功后关闭抽屉 MUST NOT 触发未保存确认

#### Scenario: 只读态

- **WHEN** 文档能力中 `readable` 为 true 且 `human_editable` 和 `task_toggle_only` 均为 false
- **THEN** 前端 MUST 以阅读态展示文档
- **AND** 前端 MUST 展示可理解的只读原因
- **AND** 关闭只读文档 MUST NOT 触发未保存确认

#### Scenario: checkbox-only 态

- **WHEN** 文档能力中 `task_toggle_only` 为 true
- **THEN** 前端 MUST 只渲染任务清单 checkbox 操作
- **AND** 前端 MUST NOT 显示 Vditor 工具栏、源码编辑区、全文保存入口或分栏编辑入口

#### Scenario: 待开发 Change 文档展示范围

- **WHEN** 用户查看待开发阶段的 OpenSpec Change 文档
- **THEN** 前端 MUST 清楚展示文档属于当前 Change 工作区
- **AND** 前端 MUST 避免让用户将 Change 草案 `spec.md` 与已生效 `openspec/specs/**/spec.md` 混淆

### Requirement: 验收中 tasks 勾选能力

系统 MUST 在验收中阶段仅允许用户对 `tasks.md` 执行 checkbox-only 操作，不允许全文 Markdown 编辑。

#### Scenario: 验收中 tasks 返回 checkbox-only

- **WHEN** 对象处于验收中阶段且用户打开 `tasks.md`
- **THEN** 文档能力 MUST 返回 `task_toggle_only=true`
- **AND** `human_editable` MUST 为 false

#### Scenario: 验收中其他文档只读

- **WHEN** 对象处于验收中阶段且用户打开非 `tasks.md` 文档
- **THEN** `human_editable` MUST 为 false
- **AND** `task_toggle_only` MUST 为 false

#### Scenario: tasks checkbox-only 操作不产生全文编辑脏状态

- **WHEN** 用户只切换 `tasks.md` 中的任务 checkbox
- **THEN** 前端 MUST 仅标记 task toggle 待保存状态
- **AND** 前端 MUST NOT 打开完整 Markdown 未保存确认流程
