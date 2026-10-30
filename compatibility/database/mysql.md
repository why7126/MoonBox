---
purpose: MySQL 生产数据库适配说明
content: MoonBox 生产 MySQL 使用边界、连接配置、字符集、迁移和测试要求
created_at: 2026-07-30 09:15:29
updated_at: 2026-07-30 09:15:29
owner: MoonBox 产品团队
status: draft
---

# MySQL 适配说明

MoonBox 生产环境使用 MySQL，开发环境和快速测试保留 SQLite。MySQL 适配目标是保证生产数据库配置、迁移、Repository 行为和测试矩阵可追踪、可复现。

## 连接配置

| 配置 | 要求 |
|---|---|
| `APP_ENV` | 生产环境必须为 `production` |
| `DATABASE_TYPE` | 生产环境必须为 `mysql` |
| `DATABASE_URL` / `MYSQL_DATABASE_URL` | 必须使用 `mysql+pymysql://` 或项目认可的 MySQL scheme |
| `MYSQL_CHARSET` | 默认 `utf8mb4`，生产前人工确认 |
| `MYSQL_COLLATION` | 默认 `utf8mb4_0900_ai_ci`，生产前人工确认 |
| `DATABASE_TIMEZONE` | 默认 `+00:00`，生产前人工确认 |

真实用户名、密码、主机和数据库名必须通过环境变量或密钥系统注入，不得写入 Git。

## 生产防回退

- 生产环境缺少 `DATABASE_TYPE=mysql` 时必须启动失败。
- 生产环境连接串为 SQLite 时必须启动失败。
- 错误信息不得输出数据库密码、Token 或完整敏感连接串。

## SQLite/MySQL 差异

| 能力 | SQLite | MySQL | 处理策略 |
|---|---|---|---|
| 布尔 | 通常为 `0/1` | `BOOLEAN`/`TINYINT(1)` | ORM 层统一布尔语义 |
| 时间 | `TEXT` 或函数默认值 | `TIMESTAMP`/`DATETIME` | 统一 `+00:00` 存储策略 |
| JSON | JSON1 或应用层文本校验 | 原生 JSON | 查询能力差异需记录和测试 |
| 文本长度 | 动态类型 | `VARCHAR`/`TEXT` 长度约束 | 应用层和迁移同时约束 |
| 自增主键 | `INTEGER PRIMARY KEY` | `AUTO_INCREMENT` 或 ORM 映射 | 由 ORM/迁移层封装 |
| 排序规则 | 依赖 SQLite collation | 显式 charset/collation | 生产配置必须记录 |
| 事务 | 文件锁模型 | InnoDB 事务 | MySQL 发布前验证事务行为 |

## 验证要求

- SQLite 本地快速测试覆盖连接、初始化和基础 CRUD。
- MySQL 发布前或 CI 测试覆盖连接、迁移、基础 CRUD、约束校验和事务行为。
- MySQL 测试可通过 `docker compose --profile mysql up -d mysql` 启动。


## Chat 恢复预算兼容性

BUG-0064新增chat_turn_recoveries和chat_recovery_resumes，采用通用字符串时间、整数代次、唯一请求键及条件UPDATE；无需数据库专属锁语法。覆盖重复迁移、预算/暂停持久化、并发CAS、过期租约、终态围栏与续接幂等。数据库时钟使用SQLite CURRENT_TIMESTAMP、MySQL UTC_TIMESTAMP；运行验证见对应Change证据，不把SQLite结果视为MySQL证明。

## BUG-0068 核验锁竞争

核验读事务在文件计算前结束，避免REPEATABLE READ隐藏并发事实。提交阶段重新授权、检查项目代次/guard原值并条件写，拒绝旧计划；锁等待设置最小1秒后归池恢复。驱动1205/1213仅在已回滚且无外部副作用时允许有界重试，提交不明不重试。需真实MySQL回归，SQLite不能替代。

## 对象会话准备Trace兼容

BUG-0057的SQLite先写后读选项按方言隔离；MySQL继续原Trace查询、更新及span插入顺序，无新增SQL、字段、索引或事务策略。不能用SQLite并发采样代替MySQL运行态验收。
