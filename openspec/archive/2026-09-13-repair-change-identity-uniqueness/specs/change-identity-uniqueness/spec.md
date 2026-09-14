---
created_at: 2026-09-13 15:59:31
updated_at: 2026-09-13 23:43:10
---

## ADDED Requirements

### Requirement: Change 身份跨生命周期唯一
系统 MUST 在活动目录与日期归档目录之间校验 Change ID 唯一，不因归档日期不同允许复用身份。

#### Scenario: 同 ID 出现在多个物理目录
- **WHEN** 活动与归档或多个日期归档拥有同一 ID
- **THEN** 校验失败并报告冲突相对路径，归档在修改文件前停止

#### Scenario: 创建已归档的 ID
- **WHEN** 创建前检查发现 ID 已存在于归档
- **THEN** 拒绝复用并要求使用新的 ID

#### Scenario: 初建和强化分别拥有唯一身份
- **WHEN** 两份归档已分配不同 ID 且 trace 身份一致
- **THEN** 校验通过并保留两份历史记录

### Requirement: 本地取证日志目录边界
项目 MUST 允许被 Git 忽略且未被跟踪的根 logs/ 本地取证目录，不因其存在阻断归档；跟踪日志或缺少忽略规则时校验失败。

#### Scenario: 现有本地日志保持原位
- **WHEN** logs/ 被忽略且没有被 Git 跟踪的文件
- **THEN** 目录校验通过且不删除或移动已有日志

#### Scenario: 日志被强制提交
- **WHEN** logs/ 存在 Git 跟踪文件
- **THEN** 目录校验失败并要求处理跟踪边界
