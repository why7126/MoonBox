---
purpose: 治理迭代日志
content: explore 输出 opsx 下一步链路身份规范优化记录
created_at: 2026-08-13 08:58:35
updated_at: 2026-08-13 08:58:35
owner: MoonBox 产品团队
---

# Explore 输出 Opsx 下一步链路身份规范优化

## 迭代目标

明确 `/explore` 与 `/opsx-explore` 在输出后续 `/opsx-*` 命令时的参数身份规则：可识别为 REQ/BUG 来源 Change 时必须使用完整 `REQ-xxxx-slug` 或 `BUG-xxxx-slug`，只有无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

## 变更摘要

- 新增 OpenSpec Change `optimize-explore-chain-identity`，描述探索命令链路身份输出契约。
- 更新 `/explore` Skill，增加 Change 来源识别顺序、REQ/BUG 参数保留规则和示例。
- 更新 `/opsx-explore` Skill，增加同等链路身份规则。
- 更新命令执行顺序文档，补充 explore 场景下正确与错误示例。
- 更新上下文预算校验脚本，增加 `/explore` 与 `/opsx-explore` 的链路身份契约检查。
- 将纯治理 Change 纳入 `sprint-002` scope。

## 影响范围

- Agent 命令输出契约：影响 `/explore`、`/opsx-explore` 输出「下一步」时的 `/opsx-*` 参数选择。
- 治理校验：影响 `scripts/validate-agent-context-budget.py` 对 explore 类 Skill 的检查。
- Sprint 治理：`sprint-002` 新增一个纯治理 Change 范围项。

## 更新文件

- `.agents/skills/explore/SKILL.md`
- `.agents/skills/opsx-explore/SKILL.md`
- `docs/08-command-execution-order.md`
- `scripts/validate-agent-context-budget.py`
- `openspec/changes/optimize-explore-chain-identity/proposal.md`
- `openspec/changes/optimize-explore-chain-identity/design.md`
- `openspec/changes/optimize-explore-chain-identity/tasks.md`
- `openspec/changes/optimize-explore-chain-identity/specs/agent-workflow-tooling/spec.md`
- `iterations/change/sprint-002/sprint.yaml`
- `docs/spec-logs/20260813085835-governance-explore-chain-identity.md`

## 验证结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 未通过：`python scripts/validate-openspec-language.py`，失败项来自既有历史 Change 中的英文脚手架标题和英文任务描述；本次新增 `optimize-explore-chain-identity` 文档未出现在失败列表中。
- 通过：`python scripts/validate-directory-structure.py`
- 通过：`python scripts/validate-sprint-scope.py sprint-002`
- 通过：`openspec validate optimize-explore-chain-identity`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change optimize-explore-chain-identity --sprint auto`
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-explore-chain-identity --sprint sprint-002 --dry-run --json`

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：无影响。
- DB：无影响。
- Web：无业务 UI 影响。
- 客户端：无影响。
- 管理端：无影响。
- Orval：无影响。
- Docker Compose：无影响。

## 后续建议

- 后续若新增其他探索类命令，应复用本次链路身份契约，并纳入上下文预算校验脚本。
