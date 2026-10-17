# sprint-close-history-aware-scan Specification

## Purpose
TBD - created by archiving change fix-sprint-close-stale-history-scan. Update Purpose after archive.
## Requirements
### Requirement: Sprint 关闭扫描区分当前状态与历史证据
系统 SHALL 仅将 Issue 子文档 Frontmatter 与 fenced YAML 中的结构化当前状态字段作为 Issue 中间态阻塞依据，并保留历史正文原样。

#### Scenario: 历史验收记录包含中间态词语
- **WHEN** 已归档 Issue 的正文包含带日期的旧 `pending`、`applied` 状态、测试样本或阶段性结论
- **THEN** 扫描器不因这些历史记录阻塞 Sprint 关闭

#### Scenario: 当前状态字段仍为中间态
- **WHEN** 已归档 Issue 的 Frontmatter 或 fenced YAML 状态字段仍为 `in_sprint`、`applied`、`pending` 等中间态
- **THEN** 扫描器报告具体文件与行号并阻塞 Sprint 关闭

#### Scenario: 证据链接仍指向活动目录
- **WHEN** 已归档 Issue 文档中的证据链接仍指向已归档 Change 的活动目录
- **THEN** 扫描器报告失效路径并阻塞 Sprint 关闭
