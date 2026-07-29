---
purpose: API 索引
content: MoonBox REST API 模块、契约治理和客户端生成规则
created_at: 2026-07-29 22:55:00
updated_at: 2026-07-29 22:55:00
owner: MoonBox 产品团队
---

# API 索引

MoonBox API 采用 REST 风格，由 FastAPI 暴露 OpenAPI 契约，前端通过 Orval 生成客户端。

| 模块 | 说明 | 状态 |
|---|---|---|
| Health | 健康检查 | planned |
| Auth | 登录、会话、成员身份 | planned |
| Workspace | 组织空间和项目空间 | planned |
| Agent Workflow | 流程节点、状态流转、审批和执行记录 | planned |
| Knowledge Graph | 需求、设计、代码、测试、决策和经验关联 | planned |
| Assets | 文档与图片上传、签名 URL、元数据 | planned |

API 变更必须同步 OpenAPI、Orval 客户端、测试、`docs/03-api-index.md` 和相关 OpenSpec Change。
