---
purpose: 规范工程变更历史
content: 记录 docs/spec-logs 下规范、脚本、命令、目录边界和校验规则的更新日志索引
created_at: 2026-08-08 20:53:52
updated_at: 2026-08-08 21:05:10
owner: MoonBox 产品团队
---

# 规范工程变更历史

本文件用于记录每一次规范、脚本、命令、目录边界和校验规则更新的历史摘要，帮助快速追踪治理资产演进。

单次变更的完整事实源仍以对应的 `YYYYMMDDhhmmss-governance-xxx.md`、`YYYYMMDDhhmmss-study-xxx.md`、active OpenSpec Change、Sprint 四件套和正式规格为准；本文件只做目录级索引和摘要。

## 记录规则

新增或更新条目时 SHOULD 按时间倒序维护，并包含：

- 时间：使用 `YYYY-MM-DD HH:mm:ss`，时区为 `Asia/Shanghai`。
- 类型：`governance` 或 `study`。
- 主题：使用简短中文描述。
- 关联记录：指向单次治理日志、学习报告或 OpenSpec Change。
- 更新文件：列出本次触达的主要治理资产。
- 验证结果：记录关键校验命令摘要。
- 跨项目落地提示词：记录其他项目要落地同类规范时可复制给 Agent 的 Prompt。
- 后续建议：如无后续动作，写“无”。

## 安全边界

本文件不得写入用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、本机绝对路径、系统用户名或用户主目录。

如需说明隐私或安全风险，只能使用脱敏占位符或聚合描述。

## 变更历史

| 时间 | 类型 | 主题 | 关联记录 | 更新文件 | 验证结果 | 跨项目落地提示词 | 后续建议 |
|---|---|---|---|---|---|---|---|
| 2026-08-08 21:01:51 | governance | 为 spec-logs 变更历史新增跨项目落地提示词列 | `docs/spec-logs/20260808210151-governance-spec-logs-adoption-prompt-column.md`、`openspec/archive/2026-08-08-add-spec-logs-adoption-prompt-column/` | `docs/spec-logs/CHANGELOG.md`、`openspec/archive/2026-08-08-add-spec-logs-adoption-prompt-column/` | 上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope、Workflow Sync 和 AI Usage 通过 | `请在本项目的规范工程变更历史文档中新增“跨项目落地提示词”列，为每条治理变更记录一段其他项目可复用的 Prompt；请遵守本项目 OpenSpec、Sprint 和验证流程，并避免写入私有路径、密钥或隐私数据。` | 后续治理变更继续维护该列 |
| 2026-08-08 20:58:10 | governance | 修复 add-admin-crud-list-template OpenSpec 英文脚手架标题 | `docs/spec-logs/20260808205810-governance-crud-list-template-title-language.md`、`openspec/changes/add-admin-crud-list-template/` | `openspec/changes/add-admin-crud-list-template/proposal.md`、`openspec/changes/add-admin-crud-list-template/design.md` | 上下文预算、OpenSpec 语言、目录结构和目标 Change 校验通过 | `请检查当前项目 active OpenSpec Change 是否残留英文脚手架标题，如 Why、What Changes、Context、Goals、Impact 等；将标题中文优先化，但不要改变正文语义、任务范围或业务实现，并运行项目的 OpenSpec 语言校验。` | 可继续推进 `add-admin-crud-list-template` apply |
| 2026-08-08 20:53:52 | governance | 新增 spec-logs 变更历史文档 | `docs/spec-logs/20260808205352-governance-spec-logs-changelog.md`、`openspec/archive/2026-08-08-add-spec-logs-changelog/` | `docs/spec-logs/CHANGELOG.md`、`docs/spec-logs/README.md`、`openspec/archive/2026-08-08-add-spec-logs-changelog/` | OpenSpec、目录结构、上下文预算、Sprint scope、Workflow Sync、AI Usage 和归档证据校验通过 | `请在本项目的规范工程日志目录中新增 CHANGELOG.md，用于按时间倒序记录规范、脚本、命令、目录边界和校验规则更新历史；请同步目录 README、创建或复用治理 Change，纳入 Sprint，并运行项目要求的治理校验。` | 后续 `/spec-opt` 治理变更完成时同步追加条目 |
