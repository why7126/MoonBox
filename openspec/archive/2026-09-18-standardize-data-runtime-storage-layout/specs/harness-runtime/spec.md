## MODIFIED Requirements

### Requirement: 目录与临时证据治理

系统 MUST 明确区分正式项目目录、Git 忽略的本地临时目录、本地工具缓存目录、本地持久数据目录、运行时控制状态目录和可归档的验收证据目录，避免临时视觉证据、本地工具缓存或运行时控制状态阻断目录结构校验或误入长期文档。

#### Scenario: data 持久存储与 runtime 控制状态分离

- **WHEN** 本地开发、Docker 本地部署、Chat Platform 或治理控制器需要在仓库 `data/` 下写入数据
- **THEN** 本地 SQLite 持久数据库 MUST 归属 `data/sqlite/`
- **AND** 本地 MinIO/S3 对象数据 MUST 归属 `data/s3/`
- **AND** Chat Platform、Governance、Codex 执行器的会话状态、控制状态、工作区、备份和执行器内部状态 MAY 归属 `data/runtime/`
- **AND** `data/runtime/` MUST NOT 作为业务 SQLite 数据库或对象存储数据的 canonical 根目录

#### Scenario: legacy runtime backend 存储目录迁移期可见

- **WHEN** 目录结构校验发现 `data/runtime/backend/sqlite/` 或 `data/runtime/backend/media/`
- **THEN** 校验 SHOULD 输出迁移期 warning
- **AND** warning MUST 指向 `data/sqlite/` 与 `data/s3/` 的 canonical 归属
- **AND** 在完成独立迁移 Change 前，校验 MAY 不阻断当前工作流
- **AND** 迁移动作 MUST NOT 在未停服、未备份、未校验数据库完整性的情况下执行
