---
purpose: 治理迭代日志
content: 统一命令用户反馈交互规范
created_at: 2026-08-09 08:20:00
updated_at: 2026-08-09 08:20:00
owner: MoonBox 产品团队
---

# 统一命令用户反馈交互规范

## 迭代目标

将 MoonBox Agent 命令中需要用户反馈的场景统一为“结构化选项 + 推荐项 + 可补充说明”的引导式提问，每轮只聚焦少量关键决策，并根据用户答案动态收敛，降低开放式追问带来的反馈负担。

## 变更摘要

- 新增 OpenSpec Change：`standardize-guided-command-feedback`。
- 将纯治理 Change 纳入 `sprint-002`。
- 更新 `AGENTS.md` 和 `rules/agent-context-budget.md`，增加全局命令交互约束。
- 更新 `explore`、`capture`、`req-*`、`bug-*`、`sprint-*`、`opsx-*`、`release-*`、`git-check` Skill，补充 `Guided User Feedback Contract`。
- 更新 `scripts/validate-agent-context-budget.py`，对目标命令族校验引导式反馈契约。

## 影响范围

- Agent 命令输出契约：需要用户选择、确认、补充信息或处理阻塞时默认使用引导式反馈。
- 治理校验：目标命令 Skill 缺少引导式反馈契约时会被上下文预算校验阻断。
- Sprint 追溯：`sprint-002` 新增纯治理 Change 范围项。

## 更新文件

- `AGENTS.md`
- `rules/agent-context-budget.md`
- `scripts/validate-agent-context-budget.py`
- `.agents/skills/explore/SKILL.md`
- `.agents/skills/capture/SKILL.md`
- `.agents/skills/req-*/SKILL.md`
- `.agents/skills/bug-*/SKILL.md`
- `.agents/skills/sprint-*/SKILL.md`
- `.agents/skills/opsx-*/SKILL.md`
- `.agents/skills/release-*/SKILL.md`
- `.agents/skills/git-check/SKILL.md`
- `openspec/changes/standardize-guided-command-feedback/**`
- `iterations/change/sprint-002/sprint.yaml`

## 验证结果

- `python scripts/validate-sprint-scope.py sprint-002 --item standardize-guided-command-feedback`：通过。
- `openspec validate standardize-guided-command-feedback`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change standardize-guided-command-feedback --sprint auto`：通过，解析 Sprint 为 `sprint-002`，无错误。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change standardize-guided-command-feedback --sprint sprint-002 --dry-run --json`：通过，`warning_count=0`。

## 影响评估

- API：无影响。
- DB：无影响。
- Web：无业务 UI 影响。
- 客户端：无影响。
- 管理端：无影响。
- Orval：无影响。
- Docker Compose：无影响。

## 后续建议

- 后续可把引导式反馈扩展到 `build-*`、`image-*`、`usage-docs-*` 等命令族。
- 若 Codex 环境提供可交互选择控件，可在不改变契约的前提下将文本决策卡映射为真实选项 UI。
