## 背景

来源 REQ：`issues/requirements/review/REQ-0003-database-compatibility/`。

当前项目文档仍以 SQLite 作为主关系型数据库，并在数据库设计中提到企业化部署后续评估 PostgreSQL。REQ-0003 已评审通过，明确要求开发环境继续使用 SQLite，生产环境使用 MySQL，并兼容两者。

本 Change 是跨后端、数据库、部署、测试和文档治理的基础能力变更。它不直接新增业务表，也不实现具体业务 API，但会改变数据库配置事实源、迁移要求和发布前验证门禁。

## Goals / Non-Goals

**Goals:**

- 明确开发 SQLite、生产 MySQL 的双数据库运行策略。
- 阻止生产环境在 MySQL 配置缺失、连接失败或数据库类型错误时静默回退到 SQLite。
- 建立数据库配置、ORM/Repository、迁移和 schema 初始化的兼容约束。
- 建立 SQLite/MySQL 差异记录与测试矩阵。
- 同步数据库设计、部署、规则和测试文档。

**Non-Goals:**

- 不提供历史生产数据从 SQLite 到 MySQL 的迁移工具。
- 不建设 MySQL 高可用、读写分离、备份恢复、容量规划或性能调优体系。
- 不适配 PostgreSQL、Oracle、SQL Server 或其他数据库。
- 不新增或修改具体业务表结构；业务 schema 变化由后续独立 Change 承接。
- 不引入 Web、管理后台、小程序或移动端 UI 变更。

## Decisions

### D1. 显式数据库类型优先于隐式连接串推断

运行环境应通过 `DATABASE_TYPE` 或等价配置显式声明数据库类型，并与 `DATABASE_URL` 交叉校验。

理由：

- 仅依赖连接串推断容易在生产环境误配 SQLite 文件路径。
- 显式类型便于启动校验、测试矩阵和部署文档表达。

备选方案：

- 仅通过 `DATABASE_URL` 推断数据库类型：配置更少，但生产防回退边界不够清晰。

### D2. 生产环境 fail-fast，禁止 SQLite 回退

当运行环境为生产时，如果数据库类型不是 MySQL、连接串不是 MySQL、凭据缺失或连接失败，后端服务必须启动失败。

理由：

- 生产数据写入本地 SQLite 是高风险错误。
- fail-fast 比运行中发现数据错写更容易诊断和回滚。

备选方案：

- MySQL 不可用时临时回退 SQLite：会破坏生产数据事实源，明确排除。

### D3. 兼容差异集中记录，代码中只保留必要分支

SQLite/MySQL 差异应沉淀到 `compatibility/database/` 或项目确认的等价路径。代码层只保留必要的受控分支或兼容层封装。

理由：

- 数据类型、默认值、JSON、时间和排序规则差异会持续出现，需要长期事实源。
- 分散在代码注释中会降低后续 OpenSpec 与测试复用价值。

备选方案：

- 每个 Repository 自行处理差异：短期快，但容易产生不可追踪的不一致。

### D4. MySQL 关键路径测试作为发布前门禁

本地快速测试至少覆盖 SQLite；发布前或 CI 必须覆盖 MySQL 连接、迁移、基础 CRUD、约束校验和事务行为。

理由：

- SQLite 无法完整暴露 MySQL 的类型、排序规则、默认值和外键行为。
- MySQL 测试若缺失，双数据库兼容只停留在文档层。

备选方案：

- 只在开发者本地手动验证 MySQL：成本低但不可复现，不能作为稳定发布门禁。

## Conflict Resolution

本 REQ 没有 `prototype/` 产物，不存在 HTML、PNG 或 UI 上下文冲突。后续实现如新增诊断页面、管理后台数据库状态展示或部署 UI，应创建独立 UI 需求并重新进入知识库横切 AC 判定。

## Risks / Trade-offs

- [Risk] SQLite 与 MySQL 方言差异导致同一迁移无法完全共用。→ Mitigation：允许迁移中使用显式数据库分支，但必须记录差异原因并覆盖测试。
- [Risk] MySQL 测试引入 Docker 或 CI 服务依赖，增加验证成本。→ Mitigation：将 SQLite 作为本地快速路径，MySQL 作为发布前关键路径门禁。
- [Risk] 生产启动 fail-fast 可能让配置错误更早暴露并阻断发布。→ Mitigation：提供清晰环境变量示例、错误摘要和排查文档。
- [Risk] JSON、时间、排序规则在两类数据库下难以完全一致。→ Mitigation：在兼容性文档中明确支持边界和查询限制。

## Migration Plan

1. 增加数据库类型配置和生产启动校验。
2. 更新 SQLite 与 MySQL 的连接示例，确保真实凭据不进入仓库。
3. 审计 ORM 模型、Repository 查询、schema SQL 和 Alembic migration 的 SQLite/MySQL 差异。
4. 建立或更新 `compatibility/database/` 差异记录。
5. 建立 MySQL 可复现测试环境，并补充发布前验证命令。
6. 更新 `docs/04-database-design.md`、部署文档、数据库规则和测试说明。
7. 回滚时保留开发 SQLite 路径，移除生产 MySQL 强制策略前必须重新评审风险。

## Open Questions

- 生产 MySQL 目标版本、字符集、排序规则和时区策略待实现前确认。
- MySQL 测试运行位置待确认：本地 Docker Compose、CI 服务容器，或发布前专用验证环境。
- 是否存在真实历史 SQLite 数据需要迁移到 MySQL？当前默认无，若有需另建迁移需求。
