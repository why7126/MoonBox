## 背景与原因

MoonBox 当前开发环境以 SQLite 保持低门槛启动，但生产环境需要使用 MySQL 承载真实业务数据。两类数据库存在连接配置、SQL 方言、字段类型、默认值、约束、时间精度、JSON、事务和排序规则差异，需要正式规格约束，避免开发可用但生产失败，或生产误回退到 SQLite。

## 变更内容

- 新增数据库双环境兼容能力：开发环境使用 SQLite，生产环境使用 MySQL。
- 约束数据库类型和连接串配置，生产环境禁止静默回退到 SQLite。
- 约束 ORM、Repository、迁移和 schema 初始化在 SQLite 与 MySQL 下保持业务语义一致。
- 要求沉淀 SQLite/MySQL 差异记录，并同步数据库设计、部署、规则和测试文档。
- 要求 SQLite 本地快速验证与 MySQL 发布前/CI 关键路径验证。

## 能力影响

### 新增能力

- `database-compatibility`: MoonBox 开发 SQLite 与生产 MySQL 的数据库配置、迁移、Repository 兼容、测试矩阵和文档同步能力。

### 修改能力

- 无。

## 影响范围

- `backend`: 需要调整数据库配置加载、启动校验、ORM/Repository 兼容层和迁移执行策略。
- `database`: 需要审计 SQLite/MySQL 字段类型、默认值、索引、唯一约束、外键、事务、时间和 JSON 差异。
- `api`: API 行为应保持一致；若数据库错误、健康检查或启动诊断暴露接口契约，需同步 OpenAPI 与集成测试。
- `storage`: 无对象存储结构变更。
- `web`: 无直接 UI 变更。
- `admin`: 无直接 UI 变更。
- `miniapp`: 无影响。
- `deploy`: 需要更新环境变量、Docker/生产配置示例和生产禁止 SQLite 回退说明。
- `tests`: 需要建立 SQLite 快速测试与 MySQL 关键路径测试矩阵。
