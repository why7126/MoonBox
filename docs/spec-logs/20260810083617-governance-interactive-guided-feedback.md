---
purpose: 治理迭代日志
content: 记录命令引导式反馈从文本决策卡升级为原生交互卡片优先的规范返修
created_at: 2026-08-10 08:36:17
updated_at: 2026-08-10 08:36:17
owner: MoonBox 产品团队
---

# 命令引导式反馈交互形态返修

## 迭代目标

将命令输出规范从“文本结构化选项”升级为“优先原生交互卡片，无法支持时降级为文本结构化选项”，使 `/explore` 等命令在需要用户决策时更贴近可点击、可跳过、可补充说明的交互体验。

## 变更摘要

- 全局红线补充：用户反馈优先使用原生交互卡片。
- 上下文预算规则补充：客户端或工具层不支持原生交互卡片时，必须降级为文本结构化选项。
- 高频命令 Skill 补充：`explore`、`capture`、`req-*`、`bug-*`、`opsx-*`、`sprint-*`、`release-*`、`git-check` 等目标命令需遵守同一交互契约。
- 既有 OpenSpec Change 返修：`standardize-guided-command-feedback` 的 proposal、design 和 tasks 明确交互卡片优先策略。
- 校验脚本补充：`scripts/validate-agent-context-budget.py` 将“原生交互卡片”和“降级为文本结构化选项”纳入引导式反馈契约校验。

## 影响范围

- 命令输出规范：影响需要用户选择、确认、补充信息或处理阻塞的 Agent 命令。
- 客户端能力边界：支持交互组件时优先渲染原生卡片；不支持时保持文本降级，不阻塞命令执行。
- 业务实现：不修改 `src/` 业务代码，不改变 API、数据库、Web UI、部署拓扑或客户端生成物。

## 更新文件

- `AGENTS.md`
- `rules/agent-context-budget.md`
- `.agents/skills/*/SKILL.md` 中的目标命令 Skill
- `openspec/changes/standardize-guided-command-feedback/proposal.md`
- `openspec/changes/standardize-guided-command-feedback/design.md`
- `openspec/changes/standardize-guided-command-feedback/tasks.md`
- `scripts/validate-agent-context-budget.py`
- `docs/spec-logs/20260810083617-governance-interactive-guided-feedback.md`

## 验证结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py`
- 通过：`python scripts/validate-directory-structure.py`
- 通过：`openspec validate standardize-guided-command-feedback`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change standardize-guided-command-feedback --sprint auto`
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change standardize-guided-command-feedback --sprint sprint-002 --dry-run --json`

## API / DB / Web / 客户端 / 管理端 / Orval / Docker Compose 影响

- API：无影响。
- DB：无影响。
- Web：无业务 UI 实现影响；仅定义 Agent 命令输出交互形态。
- 客户端：无生成物更新；交互卡片能力由客户端或工具层按能力支持。
- 管理端：无影响。
- Orval：无影响。
- Docker Compose：无影响。

## 后续建议

- 若客户端支持原生选择卡片，应将命令层的“需要用户决策/处理”映射到可点击选项、推荐项高亮、跳过和补充说明入口。
- 若当前运行环境未暴露交互工具，命令必须继续输出文本结构化选项，避免因 UI 能力缺失阻塞治理流程。
