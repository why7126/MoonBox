---
purpose: OpenSpec 项目说明
content: MoonBox OpenSpec 背景、范围、流程和 AI 执行约束
created_at: 2026-07-29 22:55:00
updated_at: 2026-07-29 22:55:00
owner: MoonBox 产品团队
---

# MoonBox OpenSpec

MoonBox 使用 OpenSpec 管理会改变业务能力、接口契约、数据结构、部署拓扑、权限边界、工作流语义或团队流程的变更。

## 产品范围

当前规格围绕 Project Workspace、Harness Runtime、Agent Workflow、Product Knowledge Graph 和 Agent Organization Model 展开。

## Change 流程

```text
idea / bug / change
-> issues/requirements 或 issues/bugs
-> review
-> openspec/changes
-> iterations/change
-> implementation
-> verification
-> archive
```

## 规格模块

| 模块 | 说明 |
|---|---|
| `product-workspace` | 组织空间、项目空间、成员和权限 |
| `harness-runtime` | 项目结构、规则、技能、上下文和治理流程 |
| `agent-workflow` | Agent 节点、调度、审批、执行和复盘 |
| `knowledge-graph` | 产品知识节点、边和追溯关系 |

归档前必须完成任务、测试记录、文档同步和规格更新。
