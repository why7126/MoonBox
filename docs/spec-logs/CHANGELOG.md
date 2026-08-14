---
purpose: 规范工程变更历史
content: 记录 docs/spec-logs 下规范、脚本、命令、目录边界和校验规则的更新日志索引
created_at: 2026-08-08 20:53:52
updated_at: 2026-08-12 13:04:04
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
| 2026-08-12 13:04:04 | governance | Docker media-upload 验收口径治理 | `docs/spec-logs/20260812130404-governance-docker-media-upload-acceptance.md`、`openspec/changes/fix-docker-media-upload-acceptance-gate/` | `docs/07-object-storage-strategy.md`、`docs/knowledge-base/best-practices/admin-media-upload-chain.md`、`.agents/skills/req-complete/SKILL.md`、`scripts/verify-docker-media-upload.py`、`tests/unit/test_verify_docker_media_upload.py`、`iterations/change/sprint-002/` | 单元测试、Docker media-upload 验收脚本、OpenSpec validate、Sprint scope 和 Workflow Sync 通过 | `请将 Docker media-upload 验收从固定宿主端口和默认管理员密码假设改为：解析 HOST_PORT_WEB，默认 18102；由脚本准备一次性测试用户或测试会话；验证 login、avatar upload、受保护读取和回显；输出必须脱敏。` | 后续可把该脚本接入媒体上传 Change 的自动验收清单 |
| 2026-08-10 22:36:56 | governance | 优化 Issues CHANGELOG 当前态看板 | `docs/spec-logs/20260810223656-governance-issues-changelog-current-state.md`、`openspec/changes/optimize-issues-changelog-current-state-index/` | `issues/requirements/CHANGELOG.md`、`issues/bugs/CHANGELOG.md`、`rules/{requirement-management,bug-management,issues-lifecycle,document-governance,directory-structure,agent-context-budget}.md`、`.agents/skills/{capture,req-*,bug-*,sprint-propose,opsx-apply,opsx-archive,workflow-sync}/SKILL.md`、`iterations/change/sprint-002/{sprint.md,sprint.yaml}` | 上下文预算、OpenSpec 语言、目录结构、Sprint scope、OpenSpec validate、Workflow Sync 和 AI Usage Hook 通过 | `请将项目的 issues/requirements/CHANGELOG.md 与 issues/bugs/CHANGELOG.md 从事件流水调整为每 Issue 一行的当前态看板；保留 trace.md 作为完整生命周期事实源，CHANGELOG 只展示当前状态、阶段、Sprint、Change、下一步和事实源路径，并同步规则、技能、OpenSpec 和治理日志。` | 后续可将看板行刷新自动化纳入 Workflow Sync |
| 2026-08-10 20:14:00 | governance | 强化原型驱动 UI 验收规范 | `docs/spec-logs/20260810201400-governance-prototype-ui-acceptance-contract.md`、`openspec/changes/strengthen-prototype-ui-acceptance/` | `rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、`AGENTS.md`、`.agents/skills/{req-opsx,opsx-apply,opsx-modify}/SKILL.md`、`iterations/change/sprint-002/sprint.md` | 上下文预算、OpenSpec 语言、目录结构、Sprint scope、OpenSpec validate、聚焦 diff whitespace、Workflow Sync 和 AI Usage Hook 通过 | `请强化带 prototype 的 UI Change 验收规范：新增 UI Contract、前后台一致性 checklist、Skeleton 首轮确认、1440px 与关键交互截图门禁、computed style 验收、Mock/API 边界声明和图标/文案一致性检查，并同步 OpenSpec、Skill、规则、文档索引和治理日志。` | 后续可将 UI Contract 与截图证据检查沉淀为 `/opsx-archive` 前自动校验 |
| 2026-08-10 09:05:11 | governance | 新增 REQ/BUG 全局事件索引 | `docs/spec-logs/20260810090511-governance-issues-changelog-index.md`、`openspec/changes/add-issues-changelog-index/` | `issues/requirements/CHANGELOG.md`、`issues/bugs/CHANGELOG.md`、`rules/requirement-management.md`、`rules/bug-management.md`、`rules/issues-lifecycle.md`、`rules/document-governance.md`、`rules/directory-structure.md`、`rules/agent-context-budget.md`、`.agents/skills/{capture,req-*,bug-*,sprint-propose,opsx-apply,opsx-archive,workflow-sync}/SKILL.md` | 上下文预算、OpenSpec 语言、目录结构、Sprint scope、OpenSpec validate、Workflow Sync 和 AI Usage Hook 通过 | `请为项目的 issues/requirements 与 issues/bugs 新增根目录 CHANGELOG.md，作为 REQ/BUG 关键生命周期事件的全局摘要索引；同步生命周期规则、目录结构、上下文预算和相关 Agent 技能，明确该索引不替代 registry、trace、Sprint 或 OpenSpec 事实源，并避免写入隐私、密钥、未脱敏日志和本机路径。` | 后续可将全局索引维护自动化纳入 Workflow Sync 脚本 |
| 2026-08-09 08:54:59 | study | 应用轻量 Mintlify 治理与 docs-site 部署边界 | `docs/spec-logs/20260809085459-study-mintlify-lightweight-governance.md`、`openspec/changes/apply-mintlify-lightweight-governance/` | `rules/document-governance.md`、`rules/release.md`、`rules/directory-structure.md`、`.agents/skills/usage-docs-*`、`scripts/validate-mintlify-docs.py`、`docs/02-deployment.md`、`deploy/**/README.md`、`mintlify/README.md` | Sprint scope、OpenSpec、Mintlify、上下文预算、语言、目录结构、Workflow Sync、AI Usage 和 docs-site Compose config 通过 | `请学习 ProjectTilesFST 的 Mintlify 治理，但采用轻量方案：保留当前 latest 优先的产品手册模型，新增 usage_docs generated/skipped/pending_confirmation 决策，增强 site-manifest、导航、链接、截图资产和公开安全校验，并把 docs-site 本地预览、生产承载和 Compose config 校验纳入 release/deploy 门禁。` | 后续可评估是否升级到完整版本化 usage docs 快照体系 |
| 2026-08-09 08:27:52 | governance | 优化 spec-study 日志优先学习顺序 | `docs/spec-logs/20260809082752-governance-spec-study-log-first-learning.md`、`openspec/changes/optimize-spec-study-log-first-learning/` | `.agents/skills/spec-study/SKILL.md`、`rules/agent-context-budget.md`、`docs/spec-logs/README.md`、`docs/spec-logs/CHANGELOG.md` | 上下文预算、OpenSpec 语言、目录结构、Sprint scope、目标 Change、Workflow Sync 和 AI Usage 通过 | `请优化 /spec-study 跨项目学习顺序：当学习对象存在 docs/spec-logs/CHANGELOG.md 时，先读日志索引，再读相关 study/governance 单次日志，再横向校验 AGENTS、rules、docs、Agent 目录、scripts 和部署示例，最后只按需读取代码或脚本补证；日志只作为入口地图，不替代当前资产事实源。` | 后续可在真实跨项目学习中观察日志优先是否降低上下文消耗 |
| 2026-08-09 08:18:35 | governance | 新增 git-check 推送前安全检测和 REQ/BUG 治理类 Change 的 spec-logs 强制关联规则 | `docs/spec-logs/20260809081835-governance-git-check-security-gate.md`、`openspec/changes/add-git-check-pre-push-security-gate/`、`REQ-0009-git-check-pre-push-security-gate` | `.agents/skills/git-check/SKILL.md`、`scripts/git-check.py`、`tests/unit/test_git_check.py`、`rules/security.md`、`rules/document-governance.md`、`docs/spec-logs/README.md` | `git-check`、env ignore、pytest、OpenSpec、中文语言、diff whitespace、Workflow Sync 和 AI Usage 通过 | `请新增 /git-check 推送前安全检测命令，默认扫描 staged + tracked，检测真实环境文件、运行时数据、数据库、大文件、密钥/Token/连接串、本机绝对路径和本地数据；并要求 REQ/BUG 驱动但触达治理资产的 Change 也必须写入 spec-logs 和 CHANGELOG。` | 后续可用脚本自动校验治理资产触达与 `spec_log_refs` 一致性 |
| 2026-08-08 21:01:51 | governance | 为 spec-logs 变更历史新增跨项目落地提示词列 | `docs/spec-logs/20260808210151-governance-spec-logs-adoption-prompt-column.md`、`openspec/archive/2026-08-08-add-spec-logs-adoption-prompt-column/` | `docs/spec-logs/CHANGELOG.md`、`openspec/archive/2026-08-08-add-spec-logs-adoption-prompt-column/` | 上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope、Workflow Sync 和 AI Usage 通过 | `请在本项目的规范工程变更历史文档中新增“跨项目落地提示词”列，为每条治理变更记录一段其他项目可复用的 Prompt；请遵守本项目 OpenSpec、Sprint 和验证流程，并避免写入私有路径、密钥或隐私数据。` | 后续治理变更继续维护该列 |
| 2026-08-08 20:58:10 | governance | 修复 add-admin-crud-list-template OpenSpec 英文脚手架标题 | `docs/spec-logs/20260808205810-governance-crud-list-template-title-language.md`、`openspec/changes/add-admin-crud-list-template/` | `openspec/changes/add-admin-crud-list-template/proposal.md`、`openspec/changes/add-admin-crud-list-template/design.md` | 上下文预算、OpenSpec 语言、目录结构和目标 Change 校验通过 | `请检查当前项目 active OpenSpec Change 是否残留英文脚手架标题，如 Why、What Changes、Context、Goals、Impact 等；将标题中文优先化，但不要改变正文语义、任务范围或业务实现，并运行项目的 OpenSpec 语言校验。` | 可继续推进 `add-admin-crud-list-template` apply |
| 2026-08-08 20:53:52 | governance | 新增 spec-logs 变更历史文档 | `docs/spec-logs/20260808205352-governance-spec-logs-changelog.md`、`openspec/archive/2026-08-08-add-spec-logs-changelog/` | `docs/spec-logs/CHANGELOG.md`、`docs/spec-logs/README.md`、`openspec/archive/2026-08-08-add-spec-logs-changelog/` | OpenSpec、目录结构、上下文预算、Sprint scope、Workflow Sync、AI Usage 和归档证据校验通过 | `请在本项目的规范工程日志目录中新增 CHANGELOG.md，用于按时间倒序记录规范、脚本、命令、目录边界和校验规则更新历史；请同步目录 README、创建或复用治理 Change，纳入 Sprint，并运行项目要求的治理校验。` | 后续 `/spec-opt` 治理变更完成时同步追加条目 |
