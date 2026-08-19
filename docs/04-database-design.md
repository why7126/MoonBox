---
purpose: 数据库设计
content: MoonBox SQLite 初始数据域与迁移治理
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-12 21:50:00
owner: MoonBox 产品团队
---

# 数据库设计

MoonBox MVP 采用双数据库策略：开发和自动化快速测试使用 SQLite，生产环境使用 MySQL。迁移策略为 Alembic 或等价 schema 初始化机制；在当前基线中，`schema_metadata` 由后端数据库初始化流程维护。

本地 Docker 环境默认通过 `DATABASE_TYPE=sqlite` 与 `DATABASE_URL=sqlite:////app/data/sqlite/moonbox.db` 注入后端服务。运行时数据库文件属于本地数据，不得提交 Git。

生产环境必须显式设置 `DATABASE_TYPE=mysql`，并通过 `DATABASE_URL` 或 `MYSQL_DATABASE_URL` 注入 MySQL 连接串。MySQL 凭据不得写入仓库；生产环境配置缺失、连接串非 MySQL 或误用 SQLite 时，服务必须启动失败。

## 初始数据域

| 数据域 | 说明 |
|---|---|
| workspaces | 组织空间、项目空间、成员关系 |
| agents | Agent 角色、能力、工具权限和运行配置 |
| workflows | Workflow 定义、节点、状态流转和审批记录 |
| knowledge_nodes | 需求、设计、代码、测试、决策、经验等知识节点 |
| knowledge_edges | 知识节点之间的追溯关系 |
| assets | 文档与图片对象存储元数据 |
| admin_users | 管理后台用户账号、角色、状态、冻结前状态、空间数、超级管理员保护和会话失效时间 |
| admin_sessions | 管理后台 access token 对应的服务端会话记录，支持过期、撤销和最后使用时间追溯 |
| admin_audit_events | 用户管理写操作审计，记录操作者、对象、动作、前后值、原因、结果和请求 ID |
| admin_spaces | 管理后台空间主表，记录空间编码、负责人、状态、来源、配额、有效期、回收期和保护标记 |
| admin_space_products | 空间与产品绑定表，当前约束为一空间一产品绑定 |
| admin_space_members | 空间成员关系表，保留空间成员角色和去重约束 |
| admin_space_applications | 管理后台空间申请与审批兼容表，记录申请人、拟负责人、目标空间、资源诉求、决策原因和决策人 |
| admin_space_audit_events | 空间管理写操作审计，不记录 token、会话 ID 明文或敏感凭证 |
| schema_metadata | 初始化 schema 版本追踪 |

## 管理后台用户表

`admin_users` 由 `add-admin-user-management` 引入，当前使用应用层 Repository + SQL 初始化维护。

| 字段 | 说明 |
|---|---|
| `id` | 服务端生成用户 ID |
| `username` | 全局唯一，4-32 位，字母开头，仅字母数字 |
| `nickname` | 昵称 |
| `avatar_url` | 头像访问 URL 或对象引用 |
| `role` | 仅允许“后台管理员”或“前台用户” |
| `status` | 待激活、正常、已冻结、已删除 |
| `status_before_freeze` | 冻结前状态，仅允许待激活、正常或空；解冻时据此恢复目标状态 |
| `workspace_count` | 关联空间数聚合结果 |
| `password_hash` | 管理后台账号密码哈希；不得保存明文密码 |
| `is_system_superadmin` | 系统内置唯一超级管理员保护标记 |
| `session_invalidated_at` | 冻结后 10 秒内会话失效目标时间 |
| `deleted_at` | 逻辑删除时间 |

冻结待激活或正常用户时，应用层必须写入 `status_before_freeze`；重复冻结已冻结用户不得覆盖既有冻结前状态。解冻成功后必须清空该字段；历史数据缺少冻结前状态时不得静默恢复为正常，应返回受控错误或执行明确兼容策略。`admin_audit_events` 记录用户管理写操作审计，不存储临时密码明文，仅记录重置动作结果和状态变化摘要。

## 管理后台会话表

`admin_sessions` 由 `add-admin-auth-system` 引入，用于让 access token 具备服务端可撤销能力。

| 字段 | 说明 |
|---|---|
| `id` | 服务端会话 ID |
| `user_id` | 关联后台用户 ID |
| `token_hash` | access token 哈希；不得存储明文 token |
| `expires_at` | 会话过期时间 |
| `revoked_at` | 会话撤销时间 |
| `last_used_at` | 最近使用时间 |
| `created_at` / `updated_at` | 创建与更新时间 |

## 管理后台空间表

`admin_spaces`、`admin_space_products`、`admin_space_members`、`admin_space_applications` 与 `admin_space_audit_events` 由 `add-admin-space-management` 引入，当前使用应用层 Repository + SQL 初始化维护。

| 表 | 关键字段与约束 |
|---|---|
| `admin_spaces` | `code` 全局唯一；`status` 仅允许 `ACTIVE`、`FROZEN`、`RECYCLE`；`source` 仅允许“后台创建”或“申请审批”；`expiry_type` 仅允许 `fixed_date` 或 `long_term`；`protected` 控制冻结、回收和彻底删除限制；`deleted_at`、`deleted_by`、`delete_reason`、`purge_at` 支撑回收站和 30 天保留 |
| `admin_space_products` | `space_id` 唯一，保证一空间一产品绑定；`immutable_binding` 标记绑定不可随意替换 |
| `admin_space_members` | `(space_id, user_id)` 唯一，记录空间普通成员与角色；负责人由 `admin_spaces.owner_id` 表达，不在成员列表中重复维护 |
| `admin_space_applications` | 管理后台审批兼容表；`application_type` 仅允许 `create` 或 `join`；`target_space_id` 记录历史加入空间申请的目标空间；`status` 仅允许“待审批”“已通过”“已拒绝”“已撤回”；保存申请人、拟负责人、产品、用途、资源诉求和审批决策字段 |
| `admin_space_audit_events` | 记录空间 ID、操作者、动作、前后状态摘要、原因、结果、请求 ID 和创建时间；不得写入 token、会话 ID 明文、密码或临时凭证 |

空间删除为软删除：正常空间移入回收站后写入 `deleted_at`、`deleted_by`、`delete_reason` 和 `purge_at`，默认列表不展示回收站数据；恢复会清理删除字段；彻底删除仅允许系统超级管理员对回收站空间执行，并级联清理绑定和成员关系。配额字段当前直接保存在 `admin_spaces`：`member_count/member_quota`、`storage_used_gb/storage_quota_gb`、`ai_used_tokens/ai_quota_tokens`，其中 `member_count` 口径为负责人加普通成员，普通成员关系保存在 `admin_space_members`；后续接入真实用量聚合时必须保持字段含义兼容。前台创建空间入口写入 `admin_space_applications` 待审批申请；平台管理员审批通过后再写入 `admin_spaces` 与 `admin_space_products`，申请人成为 `owner_id`。

## 双数据库兼容策略

| 项 | SQLite | MySQL |
|---|---|---|
| 使用场景 | 本地开发、快速测试 | 生产环境、发布前兼容验证 |
| 默认连接 | `sqlite:////app/data/sqlite/moonbox.db` | `mysql+pymysql://<user>:<password>@<host>:3306/<db>` |
| 字符集/排序规则 | 不适用；应用层约束 | `utf8mb4` / `utf8mb4_0900_ai_ci`，生产前人工确认 |
| 时间策略 | `CURRENT_TIMESTAMP` 文本或 ORM 映射 | `TIMESTAMP`，默认 `+00:00` 策略 |
| JSON 策略 | 优先应用层校验或 SQLite JSON1 能力 | 使用 MySQL JSON 能力时需补兼容测试 |
| 迁移策略 | 支持本地空库初始化 | 发布前验证迁移、约束和事务行为 |

当前基线 SQL 位于 `src/backend/app/db/schema.sql`，运行时初始化由 `src/backend/app/db/session.py` 按数据库方言执行。数据库变更必须同步模型、Repository、迁移脚本或 schema SQL、数据库文档、兼容性记录和测试。
