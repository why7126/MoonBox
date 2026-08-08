---
req_id: REQ-0003-database-compatibility
status: archived
created_at: 2026-07-30 08:58:57
updated_at: 2026-08-07 18:03:54
recorded_by: product
source: 用户输入
priority_hint: P1
parent_requirement:
---

# 一句话

开发环境使用 SQLite，生产环境使用 MySQL，系统的数据访问、迁移、配置和测试需要兼容两种数据库。

# 原始描述

开发环境数据库使用sqlite，生产环境数据库使用mysql，需要兼容2者

# 待澄清

- [ ] 是否要求本地测试同时覆盖 SQLite 与 MySQL，还是仅 CI/发布前覆盖 MySQL？
- [ ] 是否允许为 MySQL 引入专用迁移/连接配置，还是必须保持同一套 ORM 模型与迁移脚本？
- [ ] 当前生产 MySQL 目标版本、字符集、排序规则和时区策略是什么？
- [ ] 是否存在 SQLite 与 MySQL 不兼容字段类型、默认值、索引、外键或事务行为需要优先审计？

# 探索结论

（/req-explore 后人工确认写入）
