# reviewed-spec-evolution Specification

## Purpose
TBD - created by archiving change support-reviewed-spec-evolution. Update Purpose after archive.
## Requirements
### Requirement: 当前证据支持的同名规则演进
系统 SHALL 对已评审交付中的同名MODIFIED条文复用现行结构化验收、完整唯一历史及原有归档权限；不能只因原文发生业务语义变化拒绝，也不能以旧确认、Agent文字或精确白名单代替证据。受影响规格全文 SHALL 纳入验收输入。

#### Scenario: 同名修改验收有效
- **WHEN** 原新条文与已完成唯一前驱明确，当前完整验收有效且覆盖规格全文
- **THEN** 共享准入允许继续原有归档检查，不新增批准人、签署或独立证明，不自动归档

#### Scenario: 证据或覆盖不完整
- **WHEN** 验收缺失、失败、过期、被篡改或未绑定受影响规格全文
- **THEN** 共享准入拒绝，不复用旧确认或仅人工文档

#### Scenario: 历史或操作边界异常
- **WHEN** 前驱未完成、重复、缺损，或者请求越权、撤权、跨项目、写前内容变化
- **THEN** 原有门禁继续拒绝并保留历史；删除和重命名不因本能力取得新增准入

