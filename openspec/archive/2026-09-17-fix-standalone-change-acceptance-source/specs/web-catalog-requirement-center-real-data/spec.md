## MODIFIED Requirements

### Requirement: 独立变更交付验收来源

系统 SHALL 按独立Change交付证据定位验收来源，不套用Issue的固定acceptance.md要求。系统 SHALL 在无显式验收来源引用时识别项目中实际使用的验证摘要和验证日志章节；证据存在 SHALL 仅表示发现可追溯验收来源，不得自动解释为验收通过。

#### Scenario: 历史验证记录

- **WHEN** 无显式acceptance_refs且没有acceptance.md或verification.md
- **THEN** 系统 SHALL 接受trace中非空验证记录、验收记录、验证结果、验收结果、验证摘要、Validation Log或实施与验证记录章节作为证据入口；无来源时提示待核实
- **AND** 证据存在 SHALL 不被解释为自动验收通过

#### Scenario: 显式来源

- **WHEN** trace声明acceptance_refs
- **THEN** 系统 SHALL 校验每个Change内相对Markdown引用，拒绝越界，缺失或空文件明确提示，不回退掩盖错误

#### Scenario: 验证摘要不误报缺失

- **WHEN** 独立Change处于验收中，trace存在非空验证摘要章节且未声明acceptance_refs
- **THEN** 需求中心卡片 SHALL 不显示“未找到交付验证记录”的验收来源待核实提示
- **AND** 系统 SHALL 保留后续验收通过、归档权限和任务完成门禁

#### Scenario: Validation Log不误报缺失

- **WHEN** 独立Change处于验收中，trace存在非空Validation Log章节且未声明acceptance_refs
- **THEN** 需求中心卡片 SHALL 不显示“未找到交付验证记录”的验收来源待核实提示
- **AND** 系统 SHALL 保留后续验收通过、归档权限和任务完成门禁
