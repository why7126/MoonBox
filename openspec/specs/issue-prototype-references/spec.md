# issue-prototype-references Specification

## Purpose
TBD - created by archiving change guard-issue-prototype-references. Update Purpose after archive.
## Requirements
### Requirement: 迁移原型引用预检
系统 MUST 在 Issue 阶段写入与移动前检查当前原型入口及其静态本地资源，并区分历史记录与有效引用。
#### Scenario: 迁移导致旧路径失效
- **WHEN** 当前有效原型引用在模拟迁移后无法解析
- **THEN** 阻断该 Issue，输出来源、行号、引用、目标与原因，保持文件不变
#### Scenario: 正常与历史引用
- **WHEN** 相对原型链接在迁移后有效且旧路径只存在于明确历史章节
- **THEN** 允许迁移并单独报告历史引用
#### Scenario: 只读预览
- **WHEN** 使用 dry-run 或 check
- **THEN** 执行相同预检且不写入文件或移动目录

### Requirement: 迁移结果复核
系统 MUST 在移动后重新检查实际引用，并让重复执行复核已迁移目标。
#### Scenario: 后检失败
- **WHEN** 实际迁移后资源缺失
- **THEN** 返回非零并保留诊断和迁移后的目录，不报告完整成功
#### Scenario: 批次隔离
- **WHEN** 一个 Issue 的引用阻断而其他 Issue 可迁移
- **THEN** 继续独立 Issue 并以失败退出码报告部分失败

