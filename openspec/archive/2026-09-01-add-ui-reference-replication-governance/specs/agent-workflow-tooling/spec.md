## ADDED Requirements

### Requirement: UI 参考稿复刻治理

MoonBox SHALL 对明确引用附件 HTML、截图、标注图、既有页面或参考稿并要求“一对一复刻”“全面贴近”“保持一致”的 UI Change 建立 UI Reference Replication Contract。该 Contract SHALL 在实现前完成参考稿反向工程、组件级视觉契约、selector 映射、computed style 采样清单、分批实现计划和验收门禁，避免 UI 复刻退化为逐元素问答返修。

#### Scenario: Explore 阶段反向工程参考稿

- **WHEN** 用户在 `/explore` 中要求分析当前实现与附件、HTML、截图或既有页面的一致性
- **THEN** 系统 SHALL 只读建立参考稿反向工程摘要
- **AND** 摘要 SHALL 区分一对一复刻、风格迁移或局部一致
- **AND** 摘要 SHALL 输出组件差异、selector 候选、computed style 采样候选、风险点和后续治理入口
- **AND** 系统 SHALL NOT 直接修改业务实现

#### Scenario: REQ 与 OpenSpec 承接复刻契约

- **WHEN** 一个 UI REQ 或 Change 明确要求对齐参考稿
- **THEN** `/req-complete` SHALL 在需求验收资料中记录参考事实源、保真模式、组件清单和关键验收点
- **AND** `/req-opsx` SHALL 在 Change `design.md` 写入 UI Reference Replication Contract
- **AND** Change `tasks.md` SHALL 将参考稿反向工程、selector 映射、computed style 采样和分批验收列为可跟踪任务

#### Scenario: Apply 和 Modify 执行分批验收

- **WHEN** `/opsx-apply` 或 `/opsx-modify` 实施参考稿复刻 UI Change
- **THEN** 系统 SHALL 按组件批次推进，不得仅用整体观感判断完成
- **AND** 每批 SHALL 记录目标 selector、关键视觉属性、截图或 computed style 证据、差异结论和非目标确认
- **AND** 若验收反馈暴露 Contract 缺口，系统 SHALL 先补齐 Contract，再继续返修

#### Scenario: Archive 阶段阻断证据缺失

- **WHEN** 参考稿复刻 UI Change 准备归档
- **THEN** 系统 SHALL 复核 UI Reference Replication Contract、最终截图、computed style 采样、selector 映射、REQ 验收资料和 Change 证据一致
- **AND** 若缺少关键组件证据、存在 stale 证据或非目标误改未解释，系统 SHALL 阻断归档
