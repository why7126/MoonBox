---
requirement_id: REQ-0009-git-check-pre-push-security-gate
title: git-check 推送前安全检测命令
terminal: multi
version: v1
status: done
owner: product
source: capture.md
priority: P1
parent_requirement:
created_at: 2026-08-09 07:18:58
updated_at: 2026-08-14 08:52:51
---

# git-check 推送前安全检测命令

## 背景

MoonBox 已在安全、环境变量、数据管理、发布和文档治理规则中明确禁止提交真实 `.env`、密钥、Token、真实客户数据、运行时数据库文件、对象存储运行时数据、本机绝对路径和不可公开运维信息。现有 `.gitignore` 已覆盖多数本地数据与构建产物，`scripts/validate-env-ignore-policy.py` 也能校验真实环境文件与示例环境文件的 ignore 策略。

但在实际推送前，仍缺少一个统一的 Git 安全门禁来检查 staged/tracked 文件是否已经包含不应进入仓库的内容。仅依赖 `.gitignore` 无法发现已被 tracked 的敏感文件、已 staged 的运行时数据、文档中误复制的密钥、连接串、Authorization header、本机绝对路径或大文件产物。

本需求新增 `git-check` 推送前安全检测命令，作为开发者和 Agent 在推送到 Git 仓库前的轻量安全检查入口。

## 目标用户

- 开发者：在提交或推送前快速发现不应进入 Git 仓库的本地数据、密钥、运行时文件和大文件。
- Agent 执行者：在生成、修改、归档或发布前获得一致的 Git 安全门禁，避免把敏感内容写入仓库。
- 项目维护者：通过统一脚本复用安全规则，减少分散校验和人工审查遗漏。
- 发布与治理负责人：确保公开文档、发布公告、Mintlify 投影和治理日志不携带真实密钥、客户数据或本机路径。

## 范围

### 包含

- 新增 `/git-check` Agent 命令，MVP 仅作为显式命令使用，不强制接入 Git `pre-push` hook。
- 新增或复用脚本作为检测实现入口，命令执行时默认扫描 staged 文件和 tracked 文件。
- 复用现有 `scripts/validate-env-ignore-policy.py`，确保真实环境文件被 ignore，示例环境文件仍可跟踪。
- 检测 staged/tracked 文件路径中不应提交的真实环境文件、运行时数据、数据库文件、对象存储数据、临时目录、构建产物、压缩包和大文件。
- 检测 staged/tracked 文本内容中疑似真实密钥、Token、Authorization header、Cookie、数据库连接串、对象存储凭据、私有生产地址、本机绝对路径和真实客户隐私数据。
- 支持可选全仓扫描增强模式，用于人工安全复核或发布前深度检查。
- 输出分级结果：高危项作为 error 阻断，低置信疑似项作为 warning，普通检查项作为 info 或 summary。
- 输出内容必须脱敏，不得在检测报告中完整打印密钥、Token、Cookie、连接串或真实 `.env` 内容。

### 不包含

- MVP 不强制安装或启用 Git `pre-push` hook。
- 不默认扫描完整 Git 历史。
- 不自动修复 `.gitignore`、不自动 unstage 文件、不自动删除本地文件。
- 不替代代码审查、发布校验、OpenSpec 校验、Mintlify 公开安全校验或镜像发布校验。
- 不把第三方 secret scanner 作为强依赖；如后续引入，应作为增强能力并保留项目本地规则。
- 不读取或输出被 Git ignore 且未 staged/tracked 的真实 `.env` 内容。本地真实环境文件只要被 ignore 覆盖且未进入 Git，不应阻断。

## 功能要求

### FR-001 命令入口

项目 MUST 提供 `/git-check` Agent 命令，用于在推送到 Git 仓库前执行安全检测。

MVP 阶段 `/git-check` MUST 作为显式命令运行，不强制接入 Git `pre-push` hook。未来可在误报策略稳定后扩展为 Git hook 或 CI 门禁。

### FR-002 默认扫描范围

`/git-check` 默认 MUST 扫描 staged 文件和 tracked 文件。

staged 文件用于识别即将提交的风险内容。tracked 文件用于识别已经进入仓库索引、但仍违反当前治理规则的敏感文件或本地数据。

命令 SHOULD 支持可选全仓扫描模式，用于发布前深度检查或人工安全复核。全仓扫描不得作为 MVP 默认行为。

### FR-003 env ignore 策略复用

`/git-check` MUST 复用 `scripts/validate-env-ignore-policy.py` 或等价逻辑，验证真实环境文件被 Git ignore 覆盖，示例环境文件没有被误 ignore。

当 env ignore 策略校验失败时，`/git-check` MUST 返回失败，并提示修复 `.gitignore`、环境示例文件或部署环境文件命名策略。

### FR-004 禁止提交路径检测

`/git-check` MUST 检测 staged/tracked 路径中的禁止提交文件和目录。

禁止提交路径至少包括真实环境文件、运行时数据库文件、运行时数据目录、对象存储运行时数据、上传文件、临时处理文件、MinIO/MySQL 本地卷数据、构建产物、压缩包和系统缓存文件。

当检测到禁止提交路径已 staged 或 tracked 时，命令 MUST 以 error 级别失败。

### FR-005 敏感内容检测

`/git-check` MUST 对 staged/tracked 文本文件执行敏感内容检测。

检测项至少包括真实密钥、API Key、AccessKey、SecretKey、Token、Authorization header、Cookie、数据库连接串、对象存储凭据、生产私有地址、本机绝对路径，以及疑似真实客户数据或个人隐私数据。

命令 MUST 区分示例占位符与疑似真实值。`<access_token>`、`change-me-in-local-env`、`example`、`localhost`、测试 fixture 中明确脱敏的公开样例等不应仅因关键词命中而直接作为 error。

### FR-006 输出脱敏

`/git-check` 输出 MUST 避免泄露检测到的敏感原文。

报告 MAY 输出文件路径、行号、规则名、风险级别和脱敏片段。报告 MUST NOT 完整输出密钥、Token、Cookie、Authorization header、数据库连接串、真实 `.env` 行或客户隐私数据。

### FR-007 大文件与二进制产物检测

`/git-check` MUST 检测 staged/tracked 文件中的大文件、压缩包、数据库文件、构建产物和常见二进制运行时产物。

大文件阈值 SHOULD 可配置；MVP 可提供项目默认值。超过阈值的非白名单文件 SHOULD 作为 error 或 warning 输出，具体级别由文件类型和目录决定。

### FR-008 允许名单与误报处理

`/git-check` SHOULD 支持项目级允许名单或规则豁免机制，用于处理公开样例、测试 fixture、文档占位符和必要二进制资产。

允许名单 MUST 保持可审计，不得用于绕过真实密钥、真实客户数据、真实环境文件或运行时数据库文件的阻断。

### FR-009 返回码与报告结构

`/git-check` MUST 在存在 error 级问题时返回非 0 退出码。

报告 SHOULD 包含检测摘要、error 列表、warning 列表、通过项摘要和修复建议。成功路径输出应保持紧凑，不展开完整扫描日志。

### FR-010 治理集成

后续实现 MUST 同步必要的规则、命令说明和测试。

如新增脚本或命令，必须遵守项目目录边界；不得恢复或新增 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/` 等历史 Agent 目录。

## UI 约束

本需求不涉及 Web、管理后台、小程序或移动端 UI。

命令行输出视为交互界面，必须满足以下约束：

- 输出中文优先，命令、路径、规则 ID 可保留英文。
- 成功输出保持简洁，重点展示扫描范围和通过摘要。
- 失败输出按 error、warning 分组，便于开发者快速修复。
- 敏感值必须脱敏，不能为了说明问题而泄露完整原文。
- 输出应给出下一步修复建议，例如移除 staged 文件、修正 `.gitignore`、改用 `.env.example` 或脱敏文档示例。

## 关联需求

- REQ-0008-prototype-driven-page-acceptance-gate：同属治理门禁类需求，可参考其“先门禁、再进入下一阶段”的流程约束思路。

## 状态块

```yaml
status: archived
generated_at: 2026-08-09 07:18:58
completed_at: 2026-08-09 07:21:45
reviewed_at: 2026-08-09 07:24:41
approved_at: 2026-08-09 07:24:41
source_material:
  - capture.md
  - req-explore: REQ-0009 是独立治理安全需求，适合新增统一推送前 Git 安全门禁
  - user-decision: MVP 只做 /git-check 命令，不强制接入 Git pre-push hook
  - user-decision: 默认扫描范围采用 staged + tracked，全仓扫描作为可选增强
next: /sprint-propose --req REQ-0009-git-check-pre-push-security-gate
iteration: null
```
