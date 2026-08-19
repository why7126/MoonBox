---
purpose: 治理迭代日志
content: 建立证据化根因分析治理、人工补证操作步骤和 root-cause evidence 校验脚本
created_at: 2026-08-14 22:33:06
updated_at: 2026-08-14 22:33:06
owner: MoonBox 产品团队
---

# 证据化根因分析治理

## 迭代目标

建立问题排查、BUG 完善、验收返修和效果不如预期场景的证据化根因分析治理：无证据不得确认根因；证据不足时必须输出人工补证操作步骤，等补证后再定根因。

## 变更摘要

- 新增 `rules/root-cause-evidence.md`，定义 `unknown`、`hypothesis`、`probable`、`confirmed` 根因状态、证据链、人工补证契约和脚本门禁。
- 更新 `/explore`、`/bug-explore`、`/bug-complete`、`/opsx-apply`、`/opsx-modify`，接入 root-cause evidence gate。
- 新增 `scripts/validate-root-cause-evidence.py`，支持 BUG、Change 和 active 扫描。
- 同步测试、日志、安全、UI 验收和文档索引规范，要求根因证据脱敏、可定位、可回扣。
- 创建 `establish-root-cause-evidence-governance` OpenSpec Change，并纳入 `sprint-003`。

## 影响范围

| 范围 | 影响 |
|---|---|
| API | 不涉及 |
| DB | 不涉及 |
| Web / 管理端 | 不涉及业务实现；UI 验收规范增加证据要求 |
| 客户端生成 / Orval | 不涉及 |
| Docker Compose / 部署 | 不涉及拓扑变更；部署异常补证纳入规则 |
| 安全 | 强化补证脱敏要求 |
| 测试 | BUG 修复与返修测试需回扣根因证据 |

## 更新文件

- `AGENTS.md`
- `rules/root-cause-evidence.md`
- `rules/bug-management.md`
- `rules/testing.md`
- `rules/security.md`
- `rules/ui-design.md`
- `rules/agent-context-budget.md`
- `docs/README.md`
- `docs/standards/testing-governance.md`
- `docs/standards/prototype-ui-acceptance.md`
- `.agents/skills/explore/SKILL.md`
- `.agents/skills/bug-explore/SKILL.md`
- `.agents/skills/bug-complete/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-modify/SKILL.md`
- `scripts/validate-root-cause-evidence.py`
- `openspec/changes/establish-root-cause-evidence-governance/`
- `iterations/change/sprint-003/`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

| 命令 | 结果 | 摘要 |
|---|---|---|
| `python scripts/validate-root-cause-evidence.py --change establish-root-cause-evidence-governance --json` | pass | 纯治理 Change 无 BUG 来源，root-cause evidence gate 为 `na`。 |
| `python scripts/validate-root-cause-evidence.py --all-active --json` | warning | 新门禁发现现存 `BUG-0011-admin-user-list-enum-time-display-unclear` 的 `root-cause.md` 缺少根因状态；本次未擅自补证。 |
| `python scripts/validate-agent-context-budget.py` | pass | 技能契约与上下文预算通过。 |
| `python scripts/validate-openspec-language.py` | pass | OpenSpec 中文优先校验通过。 |
| `python scripts/validate-directory-structure.py` | pass | 必需目录结构通过。 |
| `python scripts/validate-sprint-scope.py sprint-003 --item establish-root-cause-evidence-governance` | pass | Sprint scope 包含本 Change。 |
| `openspec validate establish-root-cause-evidence-governance` | pass | Change 结构校验通过。 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change establish-root-cause-evidence-governance --sprint auto` | pass | Workflow Sync 更新 2 项，无错误。 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change establish-root-cause-evidence-governance --sprint sprint-003 --json` | pass | `usage_mode: actual`，`warning_count: 0`，刷新 `data/ai-usage/sprints/sprint-003.json`。 |

## 后续建议

- 后续可将 `validate-root-cause-evidence.py` 接入 `/bug-review`、`/bug-opsx` 或归档 readiness 脚本。
- 后续可增加针对旧 BUG 文档的迁移脚本，把历史根因文档转换为证据链格式。
- 建议对 `BUG-0011-admin-user-list-enum-time-display-unclear` 执行 `/bug-complete` 或人工补证，补齐 `root-cause.md` 的根因状态与证据链。
