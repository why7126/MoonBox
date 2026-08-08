## ADDED Requirements

### Requirement: 数据库环境策略
MoonBox MUST 支持开发环境使用 SQLite、生产环境使用 MySQL 的双数据库运行策略。

#### Scenario: 开发环境默认使用 SQLite
- **WHEN** 后端服务在开发环境启动且未显式配置 MySQL
- **THEN** 系统 MUST 使用 SQLite 开发配置完成数据库连接和初始化
- **AND** SQLite 运行时数据库文件 MUST NOT 被要求提交到 Git

#### Scenario: 生产环境必须使用 MySQL
- **WHEN** 后端服务在生产环境启动
- **THEN** 系统 MUST 要求数据库类型显式配置为 MySQL
- **AND** 系统 MUST 使用 MySQL 连接串连接生产数据库

### Requirement: 生产数据库防回退
MoonBox MUST 在生产环境阻止 SQLite 或演示数据库作为生产数据源。

#### Scenario: 生产环境误配 SQLite
- **WHEN** 生产环境的数据库类型为 SQLite 或连接串指向 SQLite
- **THEN** 后端服务 MUST 启动失败
- **AND** 错误信息 MUST 明确指出生产环境禁止使用 SQLite

#### Scenario: 生产 MySQL 配置缺失
- **WHEN** 生产环境缺少 MySQL 连接串、数据库类型或必要凭据
- **THEN** 后端服务 MUST 启动失败
- **AND** 错误信息 MUST 标明缺失的配置类别
- **AND** 错误信息 MUST NOT 输出数据库密码、Token 或完整敏感连接串

### Requirement: 数据访问兼容
MoonBox 的 ORM 模型、Repository 查询和受控 SQL MUST 在 SQLite 与 MySQL 下保持一致业务语义。

#### Scenario: Repository 查询执行
- **WHEN** 数据访问层执行业务查询、写入、更新或删除
- **THEN** 查询 MUST 使用 ORM 表达式、参数化查询或受控 SQL
- **AND** 查询 MUST NOT 使用未参数化 SQL 拼接

#### Scenario: 数据库特定能力
- **WHEN** 实现必须使用 SQLite 或 MySQL 的特定能力
- **THEN** 差异 MUST 通过兼容层或显式分支封装
- **AND** 差异原因、行为边界和测试要求 MUST 记录到数据库兼容性文档

### Requirement: Schema 与迁移兼容
MoonBox 的数据库 schema 和迁移 MUST 支持 SQLite 与 MySQL，或为差异提供明确分支、文档和测试。

#### Scenario: 迁移在双数据库执行
- **WHEN** 数据库迁移或 schema 初始化被执行
- **THEN** 迁移 MUST 能在 SQLite 与 MySQL 下成功执行
- **OR** 迁移 MUST 包含可审计的数据库类型分支和差异说明

#### Scenario: 迁移失败诊断
- **WHEN** MySQL 迁移失败
- **THEN** 系统 MUST 输出数据库类型、迁移版本和失败语句摘要
- **AND** 系统 MUST NOT 进入 ready 状态

### Requirement: 数据类型与方言差异
MoonBox MUST 明确 SQLite 与 MySQL 在关键数据类型、约束和方言上的兼容策略。

#### Scenario: 关键字段类型审计
- **WHEN** schema、ORM 模型或迁移涉及布尔值、时间字段、JSON 字段、文本长度、枚举值、自增主键、索引、唯一约束或外键约束
- **THEN** 变更 MUST 明确 SQLite 与 MySQL 的表达方式和兼容策略

#### Scenario: MySQL 字符集与排序规则
- **WHEN** 生产 MySQL 配置被定义
- **THEN** 配置 MUST 明确字符集、排序规则和时区策略
- **AND** 唯一约束或查询行为不得因大小写敏感性差异产生未记录的不一致

### Requirement: 双数据库测试矩阵
MoonBox MUST 提供 SQLite 快速验证和 MySQL 关键路径验证。

#### Scenario: SQLite 本地验证
- **WHEN** 开发者运行本地快速测试
- **THEN** 测试 MUST 覆盖 SQLite 连接、初始化和基础 CRUD 关键路径

#### Scenario: MySQL 发布前验证
- **WHEN** 发布前或 CI 执行数据库相关验证
- **THEN** 测试 MUST 覆盖 MySQL 连接、迁移、基础 CRUD、约束校验和事务行为
- **AND** MySQL 测试环境 MUST 具备可复现启动方式

### Requirement: 文档与兼容性沉淀
MoonBox MUST 将双数据库策略同步到长期文档和兼容性记录。

#### Scenario: 数据库文档同步
- **WHEN** 数据库双环境兼容 Change 被实现
- **THEN** `docs/04-database-design.md` MUST 说明开发 SQLite 与生产 MySQL 策略
- **AND** 部署文档 MUST 说明 MySQL 必需环境变量、连接方式和生产禁止 SQLite 回退行为
- **AND** 数据库规则 MUST 补充双数据库兼容检查清单

#### Scenario: 兼容性记录沉淀
- **WHEN** 识别 SQLite/MySQL 差异
- **THEN** 差异 MUST 记录到 `compatibility/database/` 或项目确认的等价位置
- **AND** 记录 MUST 包含差异描述、处理策略和验证方式
