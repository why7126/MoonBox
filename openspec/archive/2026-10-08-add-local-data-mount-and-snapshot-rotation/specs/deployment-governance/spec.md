---
title: 本地数据目录治理增量规格
created_at: 2026-10-08 14:44:33
updated_at: 2026-10-08 14:44:33
---

# 本地数据目录治理增量规格

## MODIFIED Requirements

### Requirement: 本地数据目录治理

MoonBox 本地部署 MUST 明确区分本地持久数据目录与运行时控制状态目录。SQLite、对象存储、Chat Platform runtime、Governance runtime 和临时文件处理目录的宿主机归属 MUST 在部署文档中可追溯。所有本地 SQLite 启动组合 MUST 将 `/app/data/sqlite/moonbox.db` 解析到同一宿主机 `data/sqlite/moonbox.db`；迁移期间不得静默切换、覆盖或创建另一份业务库。

#### Scenario: SQLite 与对象存储拥有 canonical 宿主机目录

- **WHEN** 使用本地 SQLite 与自建 MinIO/S3 兼容对象存储
- **THEN** 本地 SQLite canonical 宿主机目录 MUST 为 `data/sqlite/`
- **AND** 自建 MinIO/S3 对象数据 canonical 宿主机目录 MUST 为 `data/s3/`
- **AND** 生产 MySQL 或外部对象存储模式 MUST NOT 依赖本地 SQLite 或本地 MinIO 数据目录作为生产事实源

#### Scenario: Chat 与治理 runtime 不承载业务持久数据库

- **WHEN** 启用 Chat Platform、Governance Controller 或 Codex 执行器
- **THEN** `data/runtime/chat-platform/` MAY 承载 Chat 状态、备份、工作区和 Codex 执行器 runtime
- **AND** `data/runtime/governance/` MAY 承载治理控制器私有状态
- **AND** `data/runtime/` MUST NOT 被描述为本地 SQLite 或对象存储数据的 canonical 目录

#### Scenario: 迁移 legacy runtime backend 存储前置检查

- **GIVEN** 旧部署曾将容器 `/app/data` 挂载到 `data/runtime/backend/`
- **WHEN** 准备将实际 SQLite 或媒体文件迁回 canonical 目录
- **THEN** 实施方 MUST 先停止相关服务
- **AND** MUST 备份源库和目标库
- **AND** MUST 执行 SQLite 完整性检查与关键表行数对比
- **AND** MUST 在验证 Chat 会话、媒体上传和治理控制器可用后再清理 legacy 目录

#### Scenario: 本地挂载路径分叉

- **WHEN** 根 Compose、本地 Compose、Chat/Governance overlay 或辅助脚本解析的本地 SQLite 实际宿主机路径与 canonical 路径不同
- **THEN** 启动检查 MUST 阻止静默创建或使用第二份业务库
- **AND** MUST 输出不含凭据与本机绝对路径的迁移提示

#### Scenario: 两处业务库内容有差异

- **GIVEN** legacy 与 canonical 业务库均存在
- **WHEN** 完整性、schema 版本或关键表内容比较发现差异或校验失败
- **THEN** 自动迁移 MUST 暂停并保全两份原文件
- **AND** MUST 提供差异报告、人工来源确认和回滚入口

#### Scenario: 切换后验证与历史快照清理

- **WHEN** 运维确认来源并切换本地挂载
- **THEN** 系统 MUST 验证 API、Chat Worker、关键业务数据和重启行为
- **AND** 历史快照 MUST 先盘点摘要、治理引用及删除状态，保全迁移前恢复点后逐份受控清理
