---
purpose: 命令执行复盘 Hook 治理日志
content: 记录 workflow 命令完成后输出链路状态、问题证据和规范优化建议的治理变更
created_at: 2026-08-15 09:29:46
updated_at: 2026-08-15 09:29:46
owner: MoonBox 产品团队
---

# 命令执行复盘 Hook 治理日志

## 背景

命令执行完成后，AI 已能输出下一步、待用户决策/处理、Workflow Sync 和 AI Usage 摘要，但缺少固定的执行链路复盘。用户希望每次 workflow 命令结束后都能回答三个问题：本次链路是否存在问题、问题是否有证据、是否暴露可沉淀的规范优化点。

## 本次变更

- 新增 Command Execution Review Hook：所有 workflow 命令完成后输出「执行链路复盘」。
- 复盘字段固定为「链路状态」「问题证据」「规范优化建议」和 follow-up 状态。
- 链路状态必须基于校验、脚本输出、日志、文件证据或用户补充证据，不得猜测。
- 无明确可复用沉淀时，规范优化建议写「无明显优化点」。
- 默认不自动创建 follow-up Issue/Change；只输出建议命令或 capture 文案，等待用户明确授权。
- 将中央契约接入 `scripts/validate-agent-context-budget.py`，避免规则、技能和命令顺序文档之间漂移。

## 触达资产

- `rules/agent-context-budget.md`
- `.agents/skills/workflow-sync/SKILL.md`
- `AGENTS.md`
- `docs/08-command-execution-order.md`
- `docs/README.md`
- `scripts/validate-agent-context-budget.py`
- `openspec/changes/establish-command-execution-review-hook/`
- `iterations/change/sprint-003/`

## 验证计划

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `python scripts/validate-sprint-scope.py sprint-003 --item establish-command-execution-review-hook`
- `openspec validate establish-command-execution-review-hook`
- `git diff --check`
- `python scripts/sync-workflow-status.py --event opsx.apply --change establish-command-execution-review-hook --sprint auto`
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change establish-command-execution-review-hook --sprint sprint-003 --json`

## 跨项目落地提示词

请建立命令执行复盘 Hook：所有 workflow 命令完成后输出链路状态、问题证据和规范优化建议；状态必须基于脚本、日志、文件、截图、验收或用户补证等证据；无明确优化点时写“无明显优化点”；默认不自动创建 follow-up Issue/Change，只输出建议命令或 capture 文案并等待用户明确授权；同步规则、workflow 技能、命令顺序文档和校验脚本。

## 后续建议

无。
