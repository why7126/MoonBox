---
purpose: OpenSpec Change Proposal
content: 为 spec-logs 变更历史新增跨项目落地提示词列
created_at: 2026-08-08 21:01:51
updated_at: 2026-08-08 21:01:51
owner: MoonBox 产品团队
---

# 为 spec-logs 变更历史新增跨项目落地提示词列

## 背景

`docs/spec-logs/CHANGELOG.md` 已作为规范工程变更历史入口，但当前表格只能说明本项目发生了什么治理更新，尚未直接回答“其他项目要落地同一规范时应该给 Agent 什么提示词”。为了让治理经验更容易迁移，需要在变更历史中沉淀可复制的跨项目落地 Prompt。

## 变更内容

- 在 `docs/spec-logs/CHANGELOG.md` 的记录规则中新增“跨项目落地提示词”字段。
- 在变更历史表格中新增“跨项目落地提示词”列。
- 为已有历史条目补充可复制 Prompt。
- 写入本次 `/spec-opt` 治理迭代日志。

## 非目标

- 不修改业务代码。
- 不改变 `/spec-study`、`/spec-opt` 命令执行逻辑或校验脚本。
- 不替代其他项目自身的 OpenSpec、Sprint 或治理流程；提示词仅作为迁移入口。

## 影响范围

- 影响 `docs/spec-logs/CHANGELOG.md` 的表格结构。
- 影响 `docs/spec-logs/` 治理日志。
- API、DB、Web、客户端、管理端、Orval、Docker Compose 均无业务实现影响。
