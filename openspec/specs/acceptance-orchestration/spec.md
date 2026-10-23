# acceptance-orchestration Specification

## Purpose
TBD - created by archiving change optimize-acceptance-archive-orchestration. Update Purpose after archive.
## Requirements
### Requirement: 验收逐项推进与局部阻塞
系统 SHALL 按依赖执行可运行的 AC，将待采集与硬阻塞区分，并保存可校验检查点。

#### Scenario: 单项证据缺失
- **WHEN** 一个 AC 缺少证据而另一个独立 AC 已具备条件
- **THEN** 独立 AC 执行，缺证项保持未通过，整体不得 ready

### Requirement: 精确复用与独立签认
系统 SHALL 仅复用输入、环境、证据与效果仍有效的结果，去重命令不替代逐项签认。

#### Scenario: 局部输入变化
- **WHEN** 一个 AC 的语义片段变化
- **THEN** 仅相关 AC 过期，真实失败不得被旧成功覆盖

### Requirement: 归档预演与恢复
系统 SHALL 在临时副本验证规格合并，保持正式归档授权边界及串行可恢复收尾。

#### Scenario: 未授权正式归档
- **WHEN** 预演成功但未授权正式归档
- **THEN** 正式规格、Change 目录和 Issue 状态不迁移

