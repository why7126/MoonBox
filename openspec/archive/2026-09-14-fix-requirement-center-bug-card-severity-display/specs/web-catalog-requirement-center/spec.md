## MODIFIED Requirements

### Requirement: 前台需求中心生命周期看板

系统 MUST 在 MoonBox 前台提供需求中心看板，保留 9 个阶段展示 Requirement 与 Bug 生命周期，并展示独立 Change 的对应交付阶段。

#### Scenario: 卡片展示治理对象摘要

- **WHEN** 看板渲染 Requirement 或 Bug 卡片
- **THEN** 卡片必须展示 ID、标题、分级标签、负责人或来源、阶段产物、更新时间、阻塞状态、研发或测试进度以及阶段主动作
- **AND** Requirement 卡片分级标签必须展示 `priority`，合法值为 `P0`、`P1`、`P2`、`P3`
- **AND** Bug 卡片分级标签必须展示 `severity`，合法值为 `blocker`、`critical`、`high`、`medium`、`low`，或产品确认的中文映射
- **AND** Requirement 与 Bug 的分级标签必须在各自合法值范围内按等级呈现可区分颜色
- **AND** Bug 卡片不得因缺少 `priority` 被默认展示为 `P2` 或其他 P 值
- **AND** 卡片必须保持当前实现的标签、文档分组、进度、底部动作和更新时间结构，仅按当前 Change 身份展示契约新增 ID 行与替换标题
- **AND** 已进入迭代规划及后续阶段的卡片必须展示唯一 `sprint-xxx` 标签
- **AND** 未纳入迭代的卡片不得展示空 Sprint 标签
