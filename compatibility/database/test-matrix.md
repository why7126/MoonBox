---
purpose: 数据库兼容测试矩阵
content: 数据库兼容范围、测试环境、Schema/迁移验证、CRUD、查询、事务、类型映射、性能、安全、CI 门禁和初始化生成规则
update_method: 项目初始化时由用户输入参数生成；数据库类型、兼容目标、迁移策略、测试框架、部署环境或质量门禁变化时更新；后续由 AI 辅助更新并经人工 Review
created_at: 2026-06-27 08:44:18
updated_at: 2026-06-27 08:44:18
owner: MoonBox
status: draft
note: 适用于 MoonBox 项目
---

# 数据库兼容测试矩阵


本文定义 `MoonBox` 的数据库兼容测试范围、测试矩阵、验收规则和质量门禁，用于验证数据库 Schema、migration、Repository/DAO、事务、查询、类型映射和多数据库适配是否符合项目要求。

本文重点回答：

- 当前项目需要验证哪些数据库、版本、驱动、ORM 和部署环境。
- 每类数据库变更必须跑哪些测试。
- SQLite、本地测试库、生产库、信创数据库之间如何验证语义一致。
- migration、回滚、数据修复、seed、fixtures 如何进入测试矩阵。
- 工程初始化时如何根据用户输入生成项目专属测试矩阵。

相关文档：

- 数据库规范：`rules/database.md`
- 测试规范：`rules/testing.md`
- 数据库设计：`docs/04-database-design.md`
- SQLite 适配：`compatibility/database/sqlite.md`
- 迁移规范：`compatibility/database/migration-rules.md`
- 发布规范：`rules/release.md`
- 数据治理：`rules/data-management.md`


工程初始化生成本文时，应优先使用用户输入和自动派生配置填充以下参数。缺失信息必须标记为 `见 docs/pending-decisions.md`，不得编造数据库版本、测试命令或测试结果。

| 参数 | 说明 | 示例 |
|---|---|---|
| `MoonBox` | 产品或项目名称 | 见 docs/pending-decisions.md |
| `MoonBox` | 项目代码，建议 kebab-case | 见 docs/pending-decisions.md |
| `MoonBox` | 数据库负责人或维护角色 | 见 docs/pending-decisions.md |
| `SQLite` | 主数据库、版本、驱动、ORM/DAO | SQLite + SQLAlchemy |
| `MoonBox` | 主关系型数据库 | SQLite |
| `MoonBox` | 信创或兼容数据库目标 | 无 / 达梦 / 海量 / PostgreSQL |
| `MoonBox` | ORM 或 DAO 技术栈 | SQLAlchemy / Prisma / Drizzle / 手写 SQL |
| `MoonBox` | 迁移工具 | Alembic / Prisma / 手写 SQL |
| `MoonBox` | 迁移目录 | `src/backend/migrations` |
| `MoonBox` | 测试数据库隔离策略 | 临时库 / 事务回滚 / 容器数据库 |
| `MoonBox` | 后端测试框架 | pytest / vitest / junit |
| `MoonBox` | 数据库测试命令 | `uv run pytest tests/integration` |
| `MoonBox` | 兼容性测试命令 | `uv run pytest tests/compatibility` |
| `MoonBox` | 迁移测试命令 | 见 docs/pending-decisions.md |
| `MoonBox` | CI 必跑命令 | 见 docs/pending-decisions.md |
| `MoonBox` | 环境清单 | local / test / staging / production |
| `MoonBox` | 数据规模 | small / medium / large / 见 docs/pending-decisions.md |
| `MoonBox` | 租户模型 | 单租户 / 多租户 / 见 docs/pending-decisions.md |


当前数据库兼容测试范围：

```text
SQLite 用于开发和快速测试；MySQL 用于生产和发布前兼容验证。
```

推荐范围：

| 数据库 | 版本 | 驱动/ORM | 使用场景 | 是否必测 | 说明 |
|---|---|---|---|---|---|
| SQLite | 系统 sqlite3 | SQLAlchemy | local/test | 是 | 本地快速路径必须覆盖 |
| MySQL | 8.x（生产前确认） | PyMySQL + SQLAlchemy | production/compatibility | 是 | 发布前或 CI 关键路径必须覆盖 |
| PostgreSQL | `MoonBox` | `MoonBox` | 生产/兼容 | 条件启用 | 声明支持时启用 |
| MySQL | `MoonBox` | `MoonBox` | 生产/兼容 | 条件启用 | 声明支持时启用 |
| 达梦 | `MoonBox` | `MoonBox` | 信创 | 条件启用 | 声明支持时启用 |
| 海量 | `MoonBox` | `MoonBox` | 信创 | 条件启用 | 声明支持时启用 |

规则：

- 声明支持的数据库必须进入测试矩阵。
- 未进入测试矩阵的数据库不得在 README、部署文档或销售材料中声明已支持。
- 只用于本地开发或单元测试的数据库必须标明“不代表生产兼容性”。
- 多数据库兼容测试应优先验证业务语义一致，而不只是 SQL 能执行。


| 层级 | 目标 | 推荐目录 | 触发场景 |
|---|---|---|---|
| 单元测试 | 验证 SQL 构造、Repository 参数、类型转换 | `tests/unit/` | Repository/DAO 逻辑变化 |
| 集成测试 | 验证真实数据库读写、事务、约束、分页 | `tests/integration/` | API、Service、Repository 变化 |
| 迁移测试 | 验证空库初始化、旧库升级、回滚或补偿 | `tests/compatibility/database/` | migration、schema、seed 变化 |
| 兼容性测试 | 验证多个数据库语义一致 | `tests/compatibility/database/` | 多数据库、信创、方言变化 |
| 性能测试 | 验证索引、大表、批量写入、迁移耗时 | `tests/performance/` | 大表、索引、导入导出变化 |
| 发布验收 | 验证 staging/production 执行结果 | 发布记录或运维记录 | 高风险迁移、生产升级 |


| 测试域 | 必测内容 | 主库 | SQLite | 兼容数据库 | 状态 |
|---|---|---|---|---|---|
| Schema 初始化 | 表、字段、索引、约束、默认值 | 必测 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| Migration 升级 | 从上一版本升级到当前版本 | 必测 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| Migration 回滚/补偿 | down migration、备份恢复或 forward fix | 条件启用 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| Seed 初始化 | 角色、权限、枚举、配置初始化 | 条件启用 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| CRUD | 新增、读取、更新、删除、软删除 | 必测 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| 查询 | 筛选、排序、分页、模糊搜索、空结果 | 必测 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| 事务 | 提交、回滚、异常、并发冲突 | 必测 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| 类型映射 | ID、时间、布尔、小数、JSON、枚举 | 必测 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| 约束 | NOT NULL、唯一、外键、状态流转 | 必测 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| 权限与租户 | 数据权限、租户隔离、越权访问 | 条件启用 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| 性能 | 索引命中、大表查询、批量导入、迁移耗时 | 条件启用 | 条件启用 | 条件启用 | 见 docs/pending-decisions.md |
| 安全 | SQL 注入、敏感字段、测试数据脱敏 | 必测 | 必测 | 必测 | 见 docs/pending-decisions.md |


每个 migration 必须验证：

| 验证项 | 要求 | 状态 |
|---|---|---|
| 空库初始化 | 从零执行所有 migration 成功 | 见 docs/pending-decisions.md |
| 旧库升级 | 从上一稳定版本升级成功 | 见 docs/pending-decisions.md |
| 重复执行保护 | 不会重复创建或破坏数据 | 见 docs/pending-decisions.md |
| 结构一致性 | 表、字段、索引、约束符合设计文档 | 见 docs/pending-decisions.md |
| 数据修复 | 行数、枚举、默认值、关联关系正确 | 条件启用 |
| 回滚或补偿 | 可执行 down、备份恢复或 forward fix | 条件启用 |
| 多数据库迁移 | 声明支持的数据库均可迁移 | 条件启用 |

推荐验证命令：

```bash
MoonBox
```

高风险 migration 还必须记录：

- 迁移文件。
- 影响表和数据范围。
- 测试数据规模。
- 执行耗时。
- 回滚或补偿结果。
- 审核人与验收人。


Repository/DAO 必须覆盖：

| 场景 | 要求 |
|---|---|
| 新增 | 必填字段、默认值、唯一约束、返回值 |
| 读取 | 按 ID、按业务键、资源不存在 |
| 更新 | 部分更新、并发版本、非法状态 |
| 删除 | 软删除、物理删除、级联或引用限制 |
| 列表 | 分页、排序、筛选、空结果 |
| 事务 | 成功提交、异常回滚、嵌套或边界事务 |
| 权限 | 租户过滤、用户过滤、角色过滤 |
| 异常 | 数据库错误、约束冲突、连接失败 |

规则：

- 测试必须使用真实数据库或可信 Fake，不能只 Mock 掉数据库行为。
- 业务关键查询必须断言返回顺序、总数、过滤条件和边界值。
- 数据库异常应映射为项目统一错误模型。


以下能力在多数据库场景中必须显式测试：

| 能力 | 测试点 | 风险 |
|---|---|---|
| 分页 | limit/offset、游标、最后一页、空页 | 方言或排序差异 |
| 排序 | 升序、降序、多字段、NULL 排序 | 数据库默认行为不同 |
| 模糊搜索 | 大小写、转义字符、中文、特殊符号 | collation 差异 |
| 时间筛选 | 时区、闭区间/开区间、日期边界 | 时间格式差异 |
| JSON 查询 | key 存在、数组、嵌套字段 | JSON 函数差异 |
| 聚合 | count、sum、group by、having | 类型和空值差异 |

多数据库兼容项目不得只在 SQLite 上验证查询正确性。


| 类型 | 必测边界 | 说明 |
|---|---|---|
| ID | 空、重复、非法格式、不可枚举性 | 与 API 暴露策略一致 |
| 时间 | 时区、毫秒、日期边界、排序 | 与 API 时间格式一致 |
| 布尔 | true/false、0/1、null | SQLite 需特别验证 |
| 小数 | 精度、舍入、最大值、最小值 | 金额类严禁误差失控 |
| 枚举 | 合法值、非法值、废弃值 | 与状态机一致 |
| JSON | 空对象、缺失 key、非法结构 | 与 Schema 一致 |
| 文本 | 空字符串、超长、中文、特殊字符 | 与校验规则一致 |
| 文件引用 | 不存在对象、过期 URL、删除引用 | 对象存储场景启用 |


测试数据策略：

```text
MoonBox
```

规则：

- 测试不得连接生产数据库。
- 每个测试必须独立，不能依赖执行顺序。
- 推荐使用事务回滚、临时数据库、容器数据库、独立 schema 或测试专用数据库文件。
- Fixtures 必须使用合成数据或脱敏数据。
- 测试运行后不得残留运行时数据库文件、临时备份或敏感导出。


推荐命令矩阵：

| 命令 | 用途 | 是否 CI 必跑 |
|---|---|---|
| `PYTHONPATH=src/backend pytest tests/compatibility/database` | SQLite 数据库兼容测试 | 是 |
| `docker compose --profile mysql up -d mysql` | 启动 MySQL 兼容验证服务 | 条件启用 |
| `DATABASE_TYPE=mysql DATABASE_URL=mysql+pymysql://moonbox:change-me@localhost:3306/moonbox PYTHONPATH=src/backend pytest tests/compatibility/database` | MySQL 关键路径验证 | 发布前必跑 |
| `PYTHONPATH=src/backend pytest` | 项目总测试命令 | 是 |

质量门禁：

- Schema、migration、Repository、DAO、数据库配置变化必须触发数据库测试。
- 多数据库项目必须至少在 CI 或定期流水线中验证声明支持的数据库。
- 高风险迁移不得只依赖本地测试结果。
- 测试失败不得通过删除断言、跳过测试或降低门禁解决。


数据库兼容测试结果应记录：

| 日期 | 变更/版本 | 数据库 | 测试命令 | 结果 | 问题 | 负责人 |
|---|---|---|---|---|---|---|
| `MoonBox` | `MoonBox` | `MoonBox` | `MoonBox` | `MoonBox` | `MoonBox` | `MoonBox` |

规则：

- 自动化测试结果以 CI 为准。
- 人工迁移演练或生产升级结果必须记录执行环境和数据规模。
- 不得在模板中伪造已通过的测试记录。


AI Agent 在处理数据库测试矩阵时必须：

- 先读取 `rules/database.md`、`rules/testing.md`、`docs/04-database-design.md`、本文和相关数据库适配文档。
- 识别当前 `MoonBox`、`MoonBox`、`MoonBox`、`MoonBox` 和测试命令。
- 涉及数据库结构、迁移、查询、事务、Repository、seed、fixtures 的变更，必须同步更新测试矩阵。
- 对无法确认的数据库版本、测试环境、测试结果标记 `见 docs/pending-decisions.md`。
- 不得编造测试通过记录、生产演练记录或 CI 结果。
- 不得删除声明支持数据库的测试项，除非同步调整兼容范围和相关文档。


作为工程初始化模块使用时：

- **默认保留**：文档定位、测试分层、核心测试矩阵、Schema/Migration 测试、Repository/DAO 测试、查询分页、类型边界、测试数据隔离、CI 门禁、AI 更新规则。
- **根据输入生成**：数据库栈、主数据库、兼容数据库、ORM、迁移工具、测试框架、测试命令、环境清单、数据规模。
- **条件启用**：SQLite 专项、多数据库兼容、信创数据库、性能测试、租户隔离、对象存储元数据、离线部署和生产迁移演练。
- **不得沿用来源项目内容**：业务表名、真实测试结果、真实数据库文件、生产数据规模、来源项目专属命令。

生成完成后，本文必须与以下文件保持一致：

- `rules/database.md`
- `rules/testing.md`
- `docs/04-database-design.md`
- `compatibility/database/sqlite.md`
- `compatibility/database/migration-rules.md`
- `MoonBox` 下的实际 migration 文件
- `tests/` 下的数据库相关测试
