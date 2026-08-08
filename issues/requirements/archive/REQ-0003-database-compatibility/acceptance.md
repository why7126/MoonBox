---
requirement_id: REQ-0003-database-compatibility
acceptance_status: passed
created_at: 2026-07-30 09:04:34
updated_at: 2026-08-08 23:37:38
owner: product
---

# 验收清单

## 功能 AC

- [ ] AC-001 开发环境默认可使用 SQLite 启动后端服务，并能完成基础连接、初始化和 CRUD 验证。
- [ ] AC-002 生产环境必须显式配置 MySQL；缺少 MySQL 连接串、凭据或数据库类型配置时，服务启动失败。
- [ ] AC-003 生产环境配置为 SQLite 或 SQLite 连接串时，服务启动失败，并输出可定位的错误信息。
- [ ] AC-004 项目提供 SQLite 与 MySQL 的环境变量示例，示例中不包含真实密钥、真实账号或生产连接串。
- [ ] AC-005 ORM 模型、Repository 查询和迁移脚本完成 SQLite/MySQL 差异审计，审计结果记录到兼容性文档。
- [ ] AC-006 所有 Repository 自定义查询使用参数化查询、ORM 表达式或受控 SQL，不出现未参数化 SQL 拼接。
- [ ] AC-007 布尔值、时间字段、JSON 字段、文本长度、枚举值、自增主键、索引、唯一约束和外键约束均有跨数据库处理策略。
- [ ] AC-008 数据库迁移可以在 SQLite 与 MySQL 下执行；如存在数据库分支逻辑，分支条件和差异原因有文档说明。
- [ ] AC-009 MySQL 迁移失败时，错误信息能定位数据库类型、迁移版本和失败语句摘要。
- [ ] AC-010 本地快速测试覆盖 SQLite 数据库关键路径。
- [ ] AC-011 发布前或 CI 覆盖 MySQL 的连接、迁移、基础 CRUD、约束校验和事务行为。
- [ ] AC-012 MySQL 测试依赖具备可复现启动方式，例如 Docker Compose 服务或等价说明。
- [ ] AC-013 `docs/04-database-design.md` 更新为“开发 SQLite、生产 MySQL”的明确策略。
- [ ] AC-014 部署文档更新 MySQL 必需环境变量、连接方式和生产禁止回退 SQLite 的说明。
- [ ] AC-015 数据库规则更新双数据库兼容检查清单，并说明差异记录位置。
- [ ] AC-016 已识别的 SQLite/MySQL 差异沉淀到 `compatibility/database/` 或项目确认的等价路径。

## 非功能 AC

- [ ] AC-017 数据库兼容实现不得降低本地开发启动门槛，SQLite 仍可作为默认开发路径。
- [ ] AC-018 生产环境数据库配置不得写入 `.env`、仓库文档示例之外的真实密钥或真实客户数据。
- [ ] AC-019 数据库类型判断、启动错误和迁移失败日志不得输出数据库密码、Token 或完整敏感连接串。
- [ ] AC-020 后续涉及 DB、API、部署或测试边界的实现必须同步对应文档与验证结果。

## 横切 AC（knowledge-base）

无横切 AC。本需求为后端/数据库/部署治理类需求，未命中 `admin-list`、`admin-form`、`admin-modal`、`media-upload` UI 场景标签。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-08 23:37:38
accepted_by: workflow-sync
source_change: add-database-compatibility
source_sprint: sprint-001
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

