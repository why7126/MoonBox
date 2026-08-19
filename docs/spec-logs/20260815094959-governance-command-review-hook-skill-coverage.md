---
purpose: 命令执行复盘 Hook Skill 覆盖率治理日志
content: 记录所有 .agents/skills 命令补充 Command Execution Review Hook 短引用和校验覆盖
created_at: 2026-08-15 09:49:59
updated_at: 2026-08-15 09:49:59
owner: MoonBox 产品团队
---

# 命令执行复盘 Hook Skill 覆盖率治理日志

## 迭代目标

让所有 `.agents/skills` 命令入口都就近提示命令结束前必须输出「执行链路复盘」，并用校验脚本防止新增或修改命令时遗漏 Hook 短引用。

## 变更摘要

- 为 43 个命令 Skill 补充 Command Execution Review Hook 短引用。
- 保留 `.agents/skills/workflow-sync/SKILL.md` 作为完整中央契约来源。
- 扩展 `scripts/validate-agent-context-budget.py`，校验命令 Skill 短引用覆盖率。
- 将 `openspec-*` 和 `usage-docs-*` 纳入命令技能识别口径。
- 更新 `rules/agent-context-budget.md`，明确每个命令 Skill 必须保留短引用。

## 影响范围

- `.agents/skills/*/SKILL.md`
- `rules/agent-context-budget.md`
- `scripts/validate-agent-context-budget.py`
- `openspec/changes/add-command-execution-review-hook-skill-coverage/`
- `iterations/change/sprint-003/`
- `docs/spec-logs/CHANGELOG.md`

## 更新文件

- `.agents/skills/*/SKILL.md`
- `rules/agent-context-budget.md`
- `scripts/validate-agent-context-budget.py`
- `openspec/changes/add-command-execution-review-hook-skill-coverage/{proposal,design,tasks,trace,acceptance}.md`
- `openspec/changes/add-command-execution-review-hook-skill-coverage/specs/agent-workflow-tooling/spec.md`
- `docs/spec-logs/20260815094959-governance-command-review-hook-skill-coverage.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过，43 个命令技能均已接入命令执行复盘 Hook 短引用。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate add-command-execution-review-hook-skill-coverage`：通过。
- `python scripts/validate-sprint-scope.py sprint-003 --item add-command-execution-review-hook-skill-coverage`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-command-execution-review-hook-skill-coverage --sprint auto`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-command-execution-review-hook-skill-coverage --sprint sprint-003 --json`：通过。
- `git diff --check`：通过。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

无。仅修改治理规则、Agent Skill、OpenSpec 文档、治理日志和校验脚本。

## 后续建议

无。
