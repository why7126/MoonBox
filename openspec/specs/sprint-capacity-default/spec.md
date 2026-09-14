# sprint-capacity-default Specification

## Purpose
定义 Sprint 默认容量、显式覆盖和容量投影一致性，确保缺省容量、人工纠正与超量门禁使用同一事实源。
## Requirements
### Requirement: 默认容量与显式覆盖
Sprint规划 MUST 在顶层容量缺失时使用30人天；有效显式容量优先且不得静默覆盖，非法容量应拒绝。

#### Scenario: 缺少容量
- **WHEN** Sprint未配置容量且无显式参数
- **THEN** 写入30人天并计算占用率

#### Scenario: 已有覆盖
- **WHEN** Sprint配置有效显式容量
- **THEN** 保留该值，只有明确容量修改请求才更新

### Requirement: 容量更新一致性
容量CLI MUST 同步总估算、占用、缓冲和门禁，超过120%时拒绝写入，并支持Workflow Sync刷新派生文档。

#### Scenario: 用户纠正容量
- **WHEN** 用户明确将sprint-005容量改为30
- **THEN** 使用30作为计算基准且刷新四件套，保留原日期和人员字段

#### Scenario: 非法或超量
- **WHEN** 容量非法或估算超过容量120%
- **THEN** 不写入Sprint事实源
