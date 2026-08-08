## 1. 配置与启动校验

- [x] 1.1 增加显式数据库类型配置，支持开发 SQLite 与生产 MySQL。
- [x] 1.2 增加生产环境启动校验，阻止 MySQL 配置缺失、连接失败或误用 SQLite。
- [x] 1.3 更新 `.env.example` 或等价示例，提供 SQLite 与 MySQL 配置样例且不包含真实密钥。

## 2. 数据访问与迁移兼容

- [x] 2.1 审计 ORM 模型、Repository 查询、schema SQL 和 Alembic migration 的 SQLite/MySQL 差异。
- [x] 2.2 封装必要的数据库类型分支或兼容层，避免业务代码散落数据库私有语法。
- [x] 2.3 确认布尔值、时间字段、JSON、文本长度、枚举、自增主键、索引、唯一约束和外键约束的跨数据库策略。
- [x] 2.4 确认 MySQL 字符集、排序规则和时区策略，并记录生产推荐配置。

## 3. 兼容性文档与治理同步

- [x] 3.1 新增或更新 `compatibility/database/`，记录 SQLite/MySQL 差异、处理策略和验证方式。
- [x] 3.2 更新 `docs/04-database-design.md`，明确开发 SQLite、生产 MySQL。
- [x] 3.3 更新部署文档，说明 MySQL 必需环境变量、连接方式和生产禁止回退 SQLite。
- [x] 3.4 更新 `rules/database.md`，补充双数据库兼容检查清单。
- [x] 3.5 如 API 错误、健康检查或部署诊断契约变化，同步 API 文档、OpenAPI 和客户端生成边界。

## 4. 测试与验证

- [x] 4.1 补充 SQLite 本地快速测试，覆盖连接、初始化和基础 CRUD。
- [x] 4.2 建立 MySQL 可复现测试环境，覆盖连接、迁移、基础 CRUD、约束校验和事务行为。
- [x] 4.3 增加生产误用 SQLite、MySQL 配置缺失和敏感连接串不泄漏的测试。
- [x] 4.4 运行相关后端测试和 MySQL 兼容验证，记录命令与结果。

## 5. 追溯与收口

- [x] 5.1 更新 REQ trace、Change trace 和 Sprint 追溯状态。
- [x] 5.2 在实现完成前确认 `REQ-0003-database-compatibility` 的验收清单 AC-001 至 AC-020 均有对应验证或说明。
