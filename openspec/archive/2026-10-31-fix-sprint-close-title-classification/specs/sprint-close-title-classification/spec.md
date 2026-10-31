# Sprint 关闭标题识别

## ADDED Requirements

### Requirement: 区分缺陷标题和当前状态
关闭扫描 MUST 排除已识别 Issue 标题中的状态描述，继续检查标题之外的当前状态。

#### Scenario: 已关闭缺陷标题包含待开发
- **WHEN** 已归档 Change 对应行含缺陷原始标题和 done 状态
- **THEN** 标题中的待开发不阻断关闭

#### Scenario: 标题之外仍有待实现
- **WHEN** 同行标题之外提示待实现
- **THEN** 扫描仍阻断关闭
