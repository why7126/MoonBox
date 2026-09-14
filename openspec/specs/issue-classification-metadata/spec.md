# issue-classification-metadata Specification

## Purpose
规范 REQ priority 与 BUG severity 的 Frontmatter 归属、事实源优先级、同步镜像、汇总展示和异常处理，保证需求与缺陷分级语义独立且可追溯。
## Requirements
### Requirement: Issue 分级元数据独立归属

系统 SHALL 在 REQ 使用 priority，在 BUG 使用 severity；trace Frontmatter 保存当前事实，已存在 capture 和主文档保持一致，注册表及汇总仅投影。

#### Scenario: 事实源与主文档冲突

- **WHEN** trace 的合法分级与主文档不同
- **THEN** 同步采用 trace 值并更新已有镜像文档，不改正文历史。

#### Scenario: 旧记录兼容

- **WHEN** trace 没有分级且主文档或 capture 有同类型合法正式字段或 hint
- **THEN** 聚焦同步补齐 trace 正式字段并清除镜像旧 hint 和异类分级字段。

#### Scenario: 缺失或非法分级

- **WHEN** 聚焦 Issue 无合法分级来源或最高优先来源显式值非法
- **THEN** 同步报告错误且不猜测或进行分级写入。

#### Scenario: 汇总类型区分

- **WHEN** 生成 Sprint 范围表
- **THEN** REQ 表使用优先级，BUG 表使用严重度。

#### Scenario: 只读与幂等

- **WHEN** 执行 dry-run 或对一致文档重复同步
- **THEN** dry-run 不写入，重复分级同步不改变时间戳。
