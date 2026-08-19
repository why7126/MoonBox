---
purpose: AI 行为入口
content: AI 开发流程入口、规则加载路由、OpenSpec 红线、目录与验证边界
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-15 13:17:18
owner: MoonBox 产品团队
---

# AI Agent 工作指南

## 项目定位

MoonBox 是 AI 原生软件工厂，面向 AI 创业者、小型软件团队和 AI 原生企业团队，帮助他们建立由 Agent 驱动的软件研发组织。

当前启用 Web 端、管理后台、REST API、SQLite、MySQL 生产兼容路径、MinIO/S3 兼容对象存储、Docker Compose 本地/生产部署矩阵、Mintlify 产品手册站点、OpenSpec、需求治理、缺陷治理、Sprint 治理、发布治理和 `.agents/skills/` 技能入口。本地模型、微信小程序、移动端、桌面端暂未启用。

## 执行前读取路由

所有任务先读：

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/language.md
rules/agent-context-budget.md
```

按任务追加读取：

| 任务类型 | 追加读取 |
|---|---|
| REQ / BUG | `rules/requirement-management.md`、`rules/bug-management.md`、`rules/issues-lifecycle.md`、对应 `issues/**` |
| Sprint | `rules/iterations-lifecycle.md`、相关 `iterations/change|archive/<sprint>/` |
| OpenSpec | `openspec/changes/<change-id>/`、`rules/document-governance.md` |
| 代码实现 | `rules/coding.md`、`rules/testing.md`、相关模块 README |
| API | `rules/api.md`、`docs/03-api-index.md`、OpenAPI 来源 |
| DB | `rules/database.md`、`docs/04-database-design.md` |
| UI | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、前端设计 token 和组件入口 |
| 部署 | `rules/environment.md`、`rules/port-management.md`、`rules/release.md`、`docs/02-deployment.md` |
| 产品手册 / Mintlify | `rules/document-governance.md`、`rules/release.md`、`docs/02-deployment.md`、`mintlify/README.md` |
| 对象存储 | `rules/data-management.md`、`rules/object-storage.md`、`docs/07-object-storage-strategy.md` |
| 安全 | `rules/security.md` |
| 问题排查 / 根因 / 返修 | `rules/root-cause-evidence.md`、相关 `logs/`、截图、测试失败、Change/Issue trace 片段 |
| 命令顺序 / 工作流编排 | `docs/08-command-execution-order.md`、`.agents/skills/workflow-sync/SKILL.md` |

## Agent 技能入口

本项目只保留 `.agents/skills/`。不得新增或恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/`。

常用命令族：

| 域 | 命令 |
|---|---|
| 通用探索 | `/explore` |
| 治理优化 | `/spec-opt`、`/spec-study` |
| Git 安全 | `/git-check` |
| 产品手册 | `/usage-docs-generate`、`/usage-docs-update`、`/usage-docs-validate` |
| 发布镜像 | `/release-propose`、`/release-prepare`、`/image-prepare`、`/image-build`、`/release-publish` |

## 流程红线

- 不允许绕过 OpenSpec Change 直接开发正式功能。
- 所有命令在需要用户选择、确认、补充信息或处理阻塞时，必须优先采用“原生交互卡片 + 结构化选项 + 推荐项 + 可补充说明”的引导式反馈；当客户端或工具层不支持原生交互卡片时，降级为文本结构化选项；每轮只聚焦 1-3 个关键决策，并根据用户答案动态收敛，不得用大段开放式追问替代。
- 未评审的 REQ/BUG 不得进入 Sprint 规划，不得转 OpenSpec，不得执行开发。
- REQ/BUG 评审通过后必须先执行 `/sprint-propose` 纳入 Sprint 并同步为 `in_sprint`，再执行 `/req-opsx` 或 `/bug-opsx`；不得从 review 直接跳到 opsx。
- `openspec/specs/` 只保存已生效规格，除归档合并动作外不得直接修改。
- 新建业务代码必须放在 `src/` 约定边界内。
- `.env`、真实密钥、真实客户数据、运行时数据库文件和临时大文件不得提交。
- 跨项目学习使用 `/spec-study`；学习对象必须全程只读，学习报告统一放入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`，本地学习对象持久化时必须脱敏为项目名或占位符。
- 规范优化使用 `/spec-opt`；规范、技能、脚本、目录边界或校验规则迭代日志统一放入 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md`，不得写入隐私、密钥、未脱敏日志、学习对象源码、本机绝对路径、系统用户名或用户主目录。
- Sprint ID 必须使用 `sprint-xxx` 三位数字递增格式；自动创建 Sprint 时扫描 `iterations/change/` 与 `iterations/archive/` 后取最大编号加一。
- 下一步可执行命令必须保留链路身份：REQ 链路的 `/req-*` 与后续 `/opsx-*` 使用完整 `REQ-xxxx-slug`，BUG 链路的 `/bug-*` 与后续 `/opsx-*` 使用完整 `BUG-xxxx-slug`，非 REQ/BUG Change 才使用 `<change-id>`。
- 所有 workflow 命令完成后必须输出「执行链路复盘」，包含链路状态、问题证据和规范优化建议；发现可优化点时默认只给建议命令或 capture 文案，不自动创建 follow-up Issue/Change，除非用户明确授权。
- API、DB、UI、部署或安全边界变化必须同步文档、规则和测试。
- 带 `prototype/` 的 UI 页面必须先完成原型拆解、UI Contract、UI Skeleton 首轮确认、1440px 与关键交互视觉验收、computed style 证据、Mock/API 边界声明和 REQ 文档最终一致性检查；不得缺少视觉证据、样式证据或文档回填即归档。
- UI 型 `/opsx-modify` 若验收反馈包含附件截图、标注图、原型截图或实际截图，必须先建立“附件截图逐项视觉对照表”，逐项确认期望、实际、偏差、检查方式、处置结论和证据入口；对照表证据不足时先补证，不得直接返修。
- REQ 来源 `/opsx-modify` 完成前必须执行 REQ 子文档一致性扫尾检查，按实际存在的 `requirement.md`、业务流程、用户故事、`acceptance.md`、`trace.md` 和 `prototype/**` 判断是否需同步，避免只更新 PRD 而遗漏子文档。
- 问题排查、BUG 完善、验收返修或效果不如预期时必须遵守证据化根因分析治理：无证据不得确认根因；证据不足时必须输出人工补证操作步骤，等补证后再定根因。
- OpenSpec 文档变更后运行中文优先校验；Mintlify 变更后运行产品手册校验。
- 完成前运行相关验证；无法运行时在回复中说明原因。

## 工作流同步

状态变化后运行：

```bash
python scripts/sync-workflow-status.py --event <event> [--req REQ-xxxx] [--bug BUG-xxxx] [--change change-id] [--sprint sprint-xxx|auto]
```

归档涉及 Issue 阶段迁移时继续运行：

```bash
python scripts/promote-issue-stage.py --to archive [--change change-id] [--sprint sprint-xxx] --reason "<event>"
```

## 回复要求

回复默认中文。涉及代码必须说明修改路径、影响面、验证结果，以及是否需要同步 API、数据库、UI、部署、安全或客户端生成。
