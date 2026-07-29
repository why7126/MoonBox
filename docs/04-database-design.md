---
purpose: 数据库设计
content: MoonBox SQLite 初始数据域与迁移治理
created_at: 2026-07-29 22:55:00
updated_at: 2026-07-29 22:55:00
owner: MoonBox 产品团队
---

# 数据库设计

MoonBox MVP 使用 SQLite 作为主关系型数据库，迁移策略为 Alembic。企业化部署可在后续 OpenSpec 中评估 PostgreSQL。

## 初始数据域

| 数据域 | 说明 |
|---|---|
| workspaces | 组织空间、项目空间、成员关系 |
| agents | Agent 角色、能力、工具权限和运行配置 |
| workflows | Workflow 定义、节点、状态流转和审批记录 |
| knowledge_nodes | 需求、设计、代码、测试、决策、经验等知识节点 |
| knowledge_edges | 知识节点之间的追溯关系 |
| assets | 文档与图片对象存储元数据 |

数据库变更必须同步模型、迁移脚本、数据库文档和测试。
