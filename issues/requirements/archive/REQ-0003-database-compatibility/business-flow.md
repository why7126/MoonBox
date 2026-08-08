---
requirement_id: REQ-0003-database-compatibility
status: archived
created_at: 2026-07-30 09:04:34
updated_at: 2026-08-07 18:03:54
owner: product
---

# 业务流程

## 主流程：按环境选择数据库

```text
开发者/部署系统
  |
  v
读取运行环境 APP_ENV / DATABASE_TYPE / DATABASE_URL
  |
  +-- APP_ENV=development
  |     |
  |     +-- DATABASE_TYPE=sqlite 或默认开发配置
  |           |
  |           v
  |     使用 SQLite 初始化连接与 schema
  |           |
  |           v
  |     运行本地开发、调试、SQLite 快速测试
  |
  +-- APP_ENV=production
        |
        +-- DATABASE_TYPE=mysql 且 DATABASE_URL 为 MySQL
        |     |
        |     v
        |   校验连接串、凭据来源、连接可用性
        |     |
        |     v
        |   执行 MySQL 迁移与生产服务启动
        |
        +-- 缺失、类型不匹配或连接失败
              |
              v
            阻止启动并输出可诊断错误
```

## 迁移与验证流程

```text
数据库相关变更
  |
  v
识别是否影响 schema / migration / ORM / Repository
  |
  +-- 不影响数据库
  |     |
  |     v
  |   按原流程验证
  |
  +-- 影响数据库
        |
        v
      审计 SQLite/MySQL 差异
        |
        v
      更新迁移、兼容性记录和数据库文档
        |
        v
      运行 SQLite 快速验证
        |
        v
      运行 MySQL 关键路径验证
        |
        v
      输出测试结果和已知限制
```

## 异常流程

### 生产误用 SQLite

```text
生产启动 -> 检测到 DATABASE_TYPE=sqlite 或 SQLite DATABASE_URL
  -> 启动失败
  -> 输出“生产环境禁止使用 SQLite”的错误
  -> 不创建本地数据库文件
  -> 不继续启动 API 服务
```

### MySQL 迁移失败

```text
执行迁移 -> MySQL 返回类型/约束/语法错误
  -> 标记迁移失败
  -> 输出数据库类型、迁移版本、失败语句摘要
  -> 阻止服务进入 ready 状态
  -> 要求修复迁移或兼容层后重试
```

## 与父 REQ 差异

本需求没有父需求。它不是某个单页功能的补充，而是跨后端、数据库、部署和测试治理的基础能力要求。

## 与后续 OpenSpec 的关系

后续 `/req-opsx` 应把本需求拆解为可实施的数据库兼容 Change，至少覆盖：

- 数据库配置与生产防回退。
- SQLite/MySQL schema 与迁移兼容。
- Repository/ORM 差异审计与兼容层。
- MySQL 测试环境与验证矩阵。
- 数据库设计、部署、规则和兼容性文档同步。
