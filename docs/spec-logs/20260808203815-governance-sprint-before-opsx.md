---
purpose: 评审后先 Sprint 再 opsx 治理日志
content: 记录 REQ/BUG review approved 后的下一步顺序修正
created_at: 2026-08-08 20:38:15
updated_at: 2026-08-08 20:38:15
owner: MoonBox 产品团队
---

# 评审后先 Sprint 再 opsx 治理日志

## 迭代目标

修正 REQ/BUG 评审完成后的下一步推荐顺序：先 `/sprint-propose` 纳入 Sprint，再 `/req-opsx` 或 `/bug-opsx` 创建 OpenSpec Change。

## 变更摘要

- `/req-review --approve` 的下一步改为 `/sprint-propose --req <REQ-full-id>`。
- `/bug-review --approve` 的下一步改为 `/sprint-propose --bug <BUG-full-id>`。
- `/req-opsx` / `/bug-opsx` 遇到 `approved` 状态时停止，要求先 Sprint。
- `sprint-propose` 输出接续 `/req-opsx` / `/bug-opsx`。
- 校验脚本增加旧顺序回退检查。

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
- `.agents/skills/req-review/SKILL.md`
- `.agents/skills/bug-review/SKILL.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/bug-opsx/SKILL.md`
- `.agents/skills/sprint-propose/SKILL.md`
- `scripts/validate-agent-context-budget.py`
- `openspec/changes/enforce-sprint-before-opsx/`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate enforce-sprint-before-opsx`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change enforce-sprint-before-opsx --sprint auto`：通过，错误 0。
- `python scripts/validate-sprint-scope.py sprint-001 --item enforce-sprint-before-opsx`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change enforce-sprint-before-opsx --sprint sprint-001 --json`：通过，`usage_mode: actual`，`warning_count: 0`。

## 后续建议

- 后续所有 review 类命令输出下一步时，先确认是否需要 Sprint 规划承载。
- 若 Issue 已经是 `in_sprint`，才允许输出对应 opsx 转换命令。
