# archive-recovery-metadata-consistency Specification

## Purpose
TBD - created by archiving change fix-archive-recovery-metadata-sync. Update Purpose after archive.
## Requirements
### Requirement: 归档状态恢复保持历史证据
系统 MUST 在关联 Issue 状态推导时读取全部关联 Change 的归档事实，且只通过绑定原文、恢复日志及有效验收证据的附加记录恢复受保护验收状态。

#### Scenario: 跨迭代全部完成
- **WHEN** 当前 Issue 的全部关联 Change 已归档且验收通过
- **THEN** Issue 可同步完成并迁移归档，历史证据和恢复日志保持不变

#### Scenario: 证明不完整
- **WHEN** 存在未归档关联、证据失败或恢复记录绑定漂移
- **THEN** 拒绝完成，不覆盖历史文件或放宽验收

### Requirement: 中文路径分隔保持链接语义
系统 MUST 将裸路径中的中文顿号作为文本分隔，保留显式 Markdown 链接原值。

#### Scenario: 并列文件说明
- **WHEN** 裸路径后以顿号列举另一文件
- **THEN** 分别识别完整路径边界，真实不存在的链接仍阻断

### Requirement: 历史原型引用按已证明的生命周期迁移解析
系统 MUST 保留受保护归档文档原字节，并只在唯一 Issue、完成状态、全部关联归档及原恢复证明有效时解析其旧阶段引用。

#### Scenario: 原型随需求归档
- **WHEN** 预检与迁移后均可证明同一 Issue 的同一原型文件存在
- **THEN** 原归档引用可按生命周期位置解析，不修改历史证据

#### Scenario: 引用存在歧义
- **WHEN** 出现重复 Issue、未完成状态、未归档兄弟、缺失文件或失效证明
- **THEN** 保留迁移阻塞，活动文档不使用历史引用豁免

