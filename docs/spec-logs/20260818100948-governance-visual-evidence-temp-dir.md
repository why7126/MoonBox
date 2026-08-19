---
purpose: 视觉证据临时目录治理
content: 明确 tmp/visual-evidence 归属、ignore 策略、长期证据转存与目录结构校验行为
created_at: 2026-08-18 10:09:48
updated_at: 2026-08-18 10:09:48
owner: MoonBox 产品团队
---

# 视觉证据临时目录治理

## 迭代目标

明确 UI 视觉证据临时目录归属与 ignore 策略，消除根目录 `tmp/` 作为本地临时取证目录时对目录结构校验造成的误阻断，并规定长期验收证据的沉淀位置。

## 变更摘要

- 将根目录 `tmp/**` 加入 `.gitignore`。
- 在目录结构规则中声明 `tmp/visual-evidence/` 仅作为本地临时视觉证据采集目录。
- 在文档治理和原型 UI 验收标准中补充临时证据与长期验收证据边界。
- 更新目录结构校验脚本，使被 ignore 的根目录 `tmp/` 不再阻断校验。
- 创建 `add-visual-evidence-temp-dir-governance` OpenSpec Change，并纳入 `sprint-003`。

## 影响范围

- 影响治理规则、UI 验收标准、目录结构校验脚本、OpenSpec Change 和 Sprint scope。
- 不影响业务 `src/`、API、数据库、Web 运行时代码、管理端业务实现、客户端生成物或 Docker Compose。
- 临时截图、computed style JSON 和视觉对照中间产物仍不得提交；归档证据需转存到 Change `evidence/` 或脱敏摘要。

## 更新文件

- `.gitignore`
- `scripts/validate-directory-structure.py`
- `rules/directory-structure.md`
- `rules/document-governance.md`
- `docs/standards/prototype-ui-acceptance.md`
- `openspec/changes/add-visual-evidence-temp-dir-governance/`
- `iterations/change/sprint-003/`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

| 命令 | 结果 | 摘要 |
|---|---|---|
| `python scripts/validate-agent-context-budget.py` | pass | 43 个命令技能上下文预算、引导式反馈、force-proceed 和复盘 Hook 覆盖通过。 |
| `python scripts/validate-openspec-language.py` | pass | OpenSpec 文档语言校验通过。 |
| `python scripts/validate-directory-structure.py` | pass | 目录结构校验通过，根目录 `tmp/` 不再误阻断。 |
| `python scripts/validate-env-ignore-policy.py` | pass | 环境文件 ignore 策略校验通过。 |
| `openspec validate add-visual-evidence-temp-dir-governance` | pass | Change 结构校验通过。 |
| `python scripts/validate-sprint-scope.py sprint-003 --item add-visual-evidence-temp-dir-governance` | pass | Sprint scope 包含本 Change。 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change add-visual-evidence-temp-dir-governance --sprint auto` | pass | Workflow Sync Updated 2，Errors 0。 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-visual-evidence-temp-dir-governance --sprint sprint-003 --json` | pass | `usage_mode: actual`，`warning_count: 0`。 |

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：不适用。
- DB：不适用。
- Web：不修改运行时代码，仅影响 UI 验收证据归属。
- 客户端生成：不适用。
- 管理端：不修改运行时代码。
- Orval：不适用。
- Docker Compose：不适用。

## 后续建议

后续可评估将 `/opsx-archive` 的视觉证据转存检查接入自动校验脚本。
