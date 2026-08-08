---
purpose: 下一步可执行命令 Issue 身份参数治理日志
content: 记录 REQ/BUG 链路在 req/bug/opsx 命令中的完整 Issue ID 输出规范
created_at: 2026-08-08 19:34:30
updated_at: 2026-08-08 19:34:30
owner: MoonBox 产品团队
---

# 下一步可执行命令 Issue 身份参数治理日志

## 迭代目标

优化命令完成后输出的“下一步”可执行命令参数规则：REQ 链路始终使用完整 `REQ-xxxx-slug`，BUG 链路始终使用完整 `BUG-xxxx-slug`，只有非 REQ/BUG 的纯治理 Change 才使用 `<change-id>`。

## 变更摘要

- 明确“原始 Issue ID”必须包含编号和 slug。
- 将 REQ/BUG 命令族的输入和下一步模板改为 `<REQ-full-id>` / `<BUG-full-id>`。
- 将 `/opsx-apply`、`/opsx-modify`、`/opsx-archive` 的用户可执行参数规则调整为 Issue 身份优先。
- 更新上下文预算校验脚本，检查关键 Skill 是否包含完整 Issue ID 约束，并阻止常见不完整模板。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：无影响。
- 测试：业务测试不适用；执行治理和 OpenSpec 校验。

## 更新文件

- `AGENTS.md`
- `docs/08-command-execution-order.md`
- `docs/README.md`
- `rules/agent-context-budget.md`
- `rules/requirement-management.md`
- `rules/bug-management.md`
- `.agents/skills/req-capture/SKILL.md`
- `.agents/skills/req-explore/SKILL.md`
- `.agents/skills/req-generate/SKILL.md`
- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/req-review/SKILL.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/bug-capture/SKILL.md`
- `.agents/skills/bug-explore/SKILL.md`
- `.agents/skills/bug-generate/SKILL.md`
- `.agents/skills/bug-complete/SKILL.md`
- `.agents/skills/bug-review/SKILL.md`
- `.agents/skills/bug-opsx/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-modify/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `.agents/skills/spec-opt/SKILL.md`
- `scripts/validate-agent-context-budget.py`
- `openspec/changes/optimize-next-step-issue-identity/`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate optimize-next-step-issue-identity`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item optimize-next-step-issue-identity`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-next-step-issue-identity --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-next-step-issue-identity --sprint sprint-001 --json`：通过，`usage_mode: actual`，`warning_count: 0`。

## 后续建议

- 后续新增命令时，若该命令会输出下一步，应优先使用完整 Issue ID 占位。
- 若命令由 Change 反查到 Issue，最终回复中的可执行命令仍应回到完整 Issue ID。
