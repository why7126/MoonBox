# archive-finalization-consistency Specification

## Purpose
TBD - created by archiving change fix-archive-finalization-consistency. Update Purpose after archive.
## Requirements
### Requirement: 归档完成必须验证当前文档

系统 SHALL 在 CLI 完整归档与产品归档返回完成前验证关联普通引用及明确当前正文；目录移动和历史任务完成不能单独证明本次收尾成功。

#### Scenario: 旧路径或当前正文残留

- **WHEN** 目录已移动但相关文档存在失效导航或明确当前状态矛盾
- **THEN** 返回收尾阻断并保留现场，不返回完整归档成功

#### Scenario: 恢复和重放

- **WHEN** 从已移动、已同步或已完成操作恢复
- **THEN** 重新执行只读收尾验证，每次请求只验证一次，不重复合并

#### Scenario: 历史与部分交付

- **WHEN** 文档记录历史失败、示例路径或父需求部分交付
- **THEN** 保留原文，不据子 Change 归档自动将父需求判为 done；真实导航仍接受检查

#### Scenario: 非完整收尾

- **WHEN** CLI 未指定 finalize
- **THEN** 仅报告目录移动完成，不报告完整归档成功

