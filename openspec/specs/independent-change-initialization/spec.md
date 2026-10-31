# independent-change-initialization Specification

## Purpose
TBD - created by archiving change fix-independent-change-initialization. Update Purpose after archive.
## Requirements
### Requirement: 创建状态事实
系统 MUST 为新独立提案建立可识别且幂等的初始状态。
#### Scenario: 缺失状态记录
- **WHEN** 无执行进度的活动提案执行创建同步
- **THEN** 写入 proposed 与 schema v1，执行时间为空
#### Scenario: 重复创建同步
- **WHEN** 已有有效执行事实
- **THEN** 保留事实不回退状态
#### Scenario: 非法历史事实
- **WHEN** 状态非法或缺失状态但已有任务进度
- **THEN** 阻断并要求核实，不伪造历史

