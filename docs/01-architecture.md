---
purpose: 架构说明
content: MoonBox MVP 架构边界、模块分层和数据流
created_at: 2026-07-29 22:55:00
updated_at: 2026-07-29 22:55:00
owner: MoonBox 产品团队
---

# 架构说明

MoonBox MVP 采用 Web + API + SQLite + MinIO 的本地优先架构，围绕项目空间、Agent Workflow、产品知识图谱和 Harness Runtime 建立研发组织基础设施。

## 分层

| 层 | 目录 | 责任 |
|---|---|---|
| Web | `src/web` | 品牌入口、工作台、管理后台、Agent Workflow 可视化 |
| API | `src/backend` | REST API、认证、组织空间、Workflow 状态、知识索引 |
| Shared | `src/shared` | 跨端类型、契约、设计 token 和共享常量 |
| Infrastructure | `src/infrastructure` | Docker、存储、数据库、部署脚本 |
| Data | `data` | 本地运行数据和开发样例，不提交真实数据 |

## 核心模块

- Project Workspace：组织空间、项目空间、成员角色和权限边界。
- Harness Runtime：项目结构、规则、技能、上下文和治理流程。
- Agent Workflow：节点、状态、审批、执行记录和复盘。
- Product Knowledge Graph：需求、设计、代码、测试、决策与经验的追溯关系。

## 数据流

用户在 Web 工作台创建产品目标或研发事项，API 将其写入 SQLite，并通过 Workflow 状态机推进到需求、OpenSpec、Sprint、实现、验证和知识沉淀。文档与图片资产通过对象存储保存，元数据和引用关系保存在数据库中。
