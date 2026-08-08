---
requirement_id: REQ-0003-database-compatibility
title: 数据库双环境兼容
terminal: multi
version: v1
status: done
owner: product
source: capture.md
priority: P1
parent_requirement:
created_at: 2026-08-07 18:03:49
updated_at: 2026-08-07 18:03:49
---

# 数据库双环境兼容

## 背景

MoonBox 当前开发环境以 SQLite 作为本地轻量数据库，生产环境需要使用 MySQL 承载真实业务数据。两类数据库在连接配置、字段类型、默认值、索引约束、事务行为、时间精度、布尔值表达、JSON 存储、大小写敏感性和 SQL 方言上存在差异。

本需求要求项目建立明确的双数据库兼容策略：开发环境保留 SQLite 的低门槛体验，生产环境使用 MySQL 且不得静默回退到 SQLite，同时保证 ORM 模型、迁移、Repository、测试和部署配置能够在两种数据库下稳定工作。

## 目标用户

- 本地开发 MoonBox 的工程师，需要无需额外数据库服务即可启动开发环境。
- 负责生产部署与运维的团队成员，需要明确 MySQL 连接、迁移和故障边界。
- 维护数据模型、Repository 和 API 的后端工程师，需要在实现时遵循跨数据库约束。
- 负责质量保障的测试人员，需要验证 SQLite 与 MySQL 差异不会导致生产缺陷。

## 范围

### 包含

- 开发环境使用 SQLite，生产环境使用 MySQL 的数据库环境策略。
- 数据库连接配置、环境变量、启动校验和生产环境防回退机制。
- ORM 模型、Repository、迁移脚本或 schema 初始化逻辑对 SQLite 与 MySQL 的兼容约束。
- SQLite 与 MySQL 在字段类型、默认值、时间、布尔值、JSON、文本长度、索引、唯一约束、外键和事务语义上的差异审计。
- 本地、测试、CI 或发布前验证中的数据库兼容测试要求。
- 数据库设计文档、环境文档和部署文档中对双数据库策略的同步说明。
- 数据库兼容性差异记录，按项目规则沉淀到 `compatibility/database/` 或等价位置。

### 不包含

- 从 SQLite 到 MySQL 的历史生产数据迁移工具，除非后续评审确认已有真实数据需要迁移。
- MySQL 高可用、读写分离、分库分表、备份恢复和容量规划。
- PostgreSQL、Oracle、SQL Server 或其他数据库适配。
- 业务表结构的新增、删改本身；具体 schema 变更应在后续 OpenSpec Change 中按能力独立说明。
- 数据访问层之外的 UI 调整、前端交互改版或客户端生成物变更，除非后续 API 契约受影响。

## 功能要求

### FR-001 数据库环境策略

- 系统应明确支持开发环境 SQLite 与生产环境 MySQL 两种数据库运行模式。
- 开发环境默认可通过 SQLite 启动，降低本地开发依赖。
- 生产环境必须通过 MySQL 连接串启动，不得在 MySQL 配置缺失或连接失败时静默回退到 SQLite。
- 数据库类型应由环境变量或配置项显式声明，避免仅通过连接串隐式推断导致误用。

### FR-002 连接配置与启动校验

- 后端服务应提供 SQLite 与 MySQL 的连接配置示例。
- 生产环境启动时应校验 MySQL 连接串、凭据来源和数据库类型配置。
- 数据库连接配置不得包含真实密钥、真实账号或生产连接串。
- 连接失败、数据库类型不匹配或生产环境误用 SQLite 时，应给出可诊断的启动错误。

### FR-003 ORM 与 Repository 兼容

- ORM 模型和 Repository 应避免依赖单一数据库私有语法。
- 如必须使用数据库特定能力，应在兼容层中封装，并记录 SQLite 与 MySQL 的差异。
- Repository 查询应使用参数化查询、ORM 表达式或受控 SQL，禁止拼接未参数化 SQL。
- 数据库访问层应保持同一业务语义在 SQLite 与 MySQL 下行为一致。

### FR-004 Schema 与迁移兼容

- 数据库结构变更必须通过 Alembic migration、schema SQL 或项目认可的等价机制维护。
- 迁移脚本应能在 SQLite 与 MySQL 下执行，或为差异提供显式分支与说明。
- 字段类型、默认值、索引名、唯一约束、外键约束和时间字段应通过兼容审计。
- 迁移失败时应可定位到具体版本、数据库类型和失败语句。

### FR-005 数据类型与方言差异约束

- 布尔值、时间字段、JSON 字段、文本长度、枚举值和自增主键应定义跨 SQLite/MySQL 的一致表达。
- 时间字段应明确时区、精度和默认值策略，避免 MySQL 与 SQLite 表现不一致。
- JSON 或半结构化字段如无法在 SQLite 与 MySQL 中保持完全一致，应明确降级表达、查询限制和测试覆盖。
- 字符集、排序规则和大小写敏感性应在 MySQL 生产配置中明确，避免唯一约束或查询结果在两类数据库下不一致。

### FR-006 测试与验证矩阵

- 本地快速测试应至少覆盖 SQLite。
- 发布前或 CI 应覆盖 MySQL 关键路径，包含连接、迁移、基础 CRUD、约束校验和事务行为。
- 涉及数据库结构、Repository 或迁移的变更应说明是否需要同时运行 SQLite 与 MySQL 测试。
- 如 MySQL 测试依赖 Docker 或外部服务，应提供可复现的启动方式和失败排查提示。

### FR-007 文档与兼容性沉淀

- 数据库设计文档应更新为开发环境 SQLite、生产环境 MySQL 的明确策略。
- 部署文档应说明生产 MySQL 的必需环境变量、连接方式和禁止回退行为。
- 数据库规范应补充双数据库兼容要求，特别是差异记录位置和变更检查清单。
- 已识别的 SQLite/MySQL 差异应沉淀到 `compatibility/database/`，供后续 OpenSpec 与实现任务引用。

## UI 约束

- 本需求不直接引入用户界面。
- 如后续实现增加管理后台中的数据库状态展示，应另行创建或扩展 UI 需求，并遵守项目设计系统。
- 错误信息可出现在日志、健康检查或部署诊断中，但不要求新增前端页面。

## 关联需求

- 暂无直接父需求。
- 可能影响后续涉及数据库结构、Repository、迁移、部署和测试治理的需求或 OpenSpec Change。

## 状态

- 当前状态：approved。
- 下一步：执行 `/req-opsx REQ-0003-database-compatibility` 创建 OpenSpec Change，或通过 `/sprint-propose` 纳入 Sprint。
